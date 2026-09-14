"""Compression des vues pour l'autoradio : format I20P v3, lu par i20view.exe.

    en-tete  '<4sHHHHHHI'  "I20P", 3, largeur, hauteur, nb_vues, 0, 0, 0
    table    (nb_vues+1) x uint32, offsets absolus des vues
    vue      uint16 nb_couleurs, palette RGB (indice 0 = fond), puis pour
             chaque ligne : uint16 nb_segments et par segment uint16 x,
             uint16 longueur, jetons de plages (c < 128 : c+1 litteraux ;
             c >= 128 : l'indice suivant repete c-126 fois)

Chaque rendu 1600x848 RGBA est compose sur le fond uni, reduit a 800x424,
eventuellement renforce en nettete, puis reduit a 255 couleurs propres a la
vue (ecart moyen ~1,6/255 avec la pleine couleur). Seuls la voiture et son
ombre sont stockes : ~100 Ko par vue au lieu de 1,36 Mo.
"""
import struct
import numpy as np

W, H = 800, 424
BG8 = np.array([24, 28, 33], np.uint8)        # #181C21, le bandeau de i20view


def compose(path, sharpen=0):
    from PIL import Image, ImageFilter                    # charge a la demande
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im, np.float32) / 255.0
    pm = a[..., :3] * a[..., 3:]
    pm_img = Image.fromarray((pm * 255 + 0.5).astype(np.uint8))
    al_img = Image.fromarray((a[..., 3] * 255 + 0.5).astype(np.uint8))
    pm = np.asarray(pm_img.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    al = np.asarray(al_img.resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255.0
    rgb = pm + (BG8.astype(np.float32) / 255.0) * (1.0 - al)
    rgb = np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8)
    mask = al[..., 0] > 1.5 / 255
    if sharpen > 0:
        sh = np.asarray(Image.fromarray(rgb).filter(
            ImageFilter.UnsharpMask(radius=1.0, percent=int(sharpen), threshold=2)))
        rgb = np.where(mask[..., None], sh, rgb).astype(np.uint8)
    return rgb, mask


def palette_view(rgb, mask):
    from PIL import Image, ImageFilter                    # charge a la demande
    px = rgb[mask]
    if len(px) == 0:
        return BG8[None, :], np.zeros((H, W), np.uint8)
    q = Image.fromarray(px.reshape(-1, 1, 3)).quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = np.vstack([BG8, np.array(q.getpalette()[:3 * 255], np.uint8).reshape(-1, 3)])
    pimg = Image.new("P", (1, 1))
    flat = np.zeros(768, np.uint8); flat[:3 * len(pal)] = pal.ravel()
    pimg.putpalette(flat.tolist())
    idx = np.asarray(Image.fromarray(rgb).quantize(palette=pimg, dither=Image.Dither.NONE)).copy()
    idx[~mask] = 0
    return pal, idx


def packbits(seq):
    out = bytearray(); i = 0; n = len(seq)
    while i < n:
        j = i + 1
        while j < n and j - i < 129 and seq[j] == seq[i]:
            j += 1
        if j - i >= 2:
            out += bytes((j - i + 126, seq[i])); i = j; continue
        j = i + 1
        while j < n and j - i < 128 and not (j + 1 < n and seq[j] == seq[j + 1]):
            j += 1
        out.append(j - i - 1); out += bytes(seq[i:j]); i = j
    return bytes(out)


def encode_view(pal, idx):
    out = bytearray(struct.pack("<H", len(pal)) + pal.tobytes())
    for row in idx:
        nz = np.flatnonzero(row)
        if len(nz) == 0:
            out += struct.pack("<H", 0); continue
        cuts = np.flatnonzero(np.diff(nz) > 6)
        starts = np.concatenate(([nz[0]], nz[cuts + 1]))
        ends = np.concatenate((nz[cuts], [nz[-1]])) + 1
        out += struct.pack("<H", len(starts))
        for a, b in zip(starts, ends):
            out += struct.pack("<HH", int(a), int(b - a)) + packbits(row[a:b].tobytes())
    return bytes(out)


def encode_file(png, sharpen=0):
    rgb, mask = compose(png, sharpen)
    pal, idx = palette_view(rgb, mask)
    return encode_view(pal, idx)


def decode_view(buf, off=0):
    """Decodeur de reference, miroir de drawFrame() dans i20view.c."""
    (nc,) = struct.unpack_from("<H", buf, off); p = off + 2
    pal = np.frombuffer(buf, np.uint8, 3 * nc, p).reshape(-1, 3); p += 3 * nc
    img = np.zeros((H, W), np.uint8)
    for y in range(H):
        (n,) = struct.unpack_from("<H", buf, p); p += 2
        for _ in range(n):
            x, ln = struct.unpack_from("<HH", buf, p); p += 4
            while ln > 0:
                c = buf[p]; p += 1
                if c < 128:
                    img[y, x:x + c + 1] = np.frombuffer(buf, np.uint8, c + 1, p)
                    p += c + 1; x += c + 1; ln -= c + 1
                else:
                    img[y, x:x + c - 126] = buf[p]; p += 1; x += c - 126; ln -= c - 126
    return pal[img]


def assemble(blobs):
    """Vues encodees -> contenu du fichier .frm, controle d'assemblage compris."""
    head = struct.pack("<4sHHHHHHI", b"I20P", 3, W, H, len(blobs), 0, 0, 0)
    offs, cur = [], len(head) + 4 * (len(blobs) + 1)
    for b in blobs:
        offs.append(cur); cur += len(b)
    offs.append(cur)
    data = head + struct.pack(f"<{len(offs)}I", *offs) + b"".join(blobs)
    for k in {0, len(blobs) // 2, len(blobs) - 1}:
        if not np.array_equal(decode_view(data, offs[k]), decode_view(blobs[k])):
            raise RuntimeError(f"assemblage incoherent sur la vue {k}")
    return data

