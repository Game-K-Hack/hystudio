"""Autoradio : carte SD branchee au PC.

Carte SD : on la reconnait a eu20_upgrade.lgu ou Aerith.exe a la racine.
Avant toute copie, le volume doit etre integre : une coupure de la tete en
pleine ecriture laisse la FAT marquee non integre (vu le 13/09/2026), et y
ecrire peut abimer d'autres fichiers. Chaque copie est verifiee par MD5.
"""
import ctypes, hashlib, os, string, subprocess

from .paths import viewer_exe
MARKERS = ("eu20_upgrade.lgu", "Aerith.exe")
NOWIN = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


# ----------------------------------------------------------------- carte SD

def find_sd_cards():
    """Lecteurs amovibles portant les fichiers de la tete."""
    if os.name != "nt":
        return []
    out = []
    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"
        if ctypes.windll.kernel32.GetDriveTypeW(root) != 2:       # DRIVE_REMOVABLE
            continue
        try:
            if any(os.path.exists(os.path.join(root, m)) for m in MARKERS):
                out.append(root)
        except OSError:
            continue
    return out


def is_clean(root):
    """True si le volume est integre (fsutil dirty query)."""
    r = subprocess.run(["fsutil", "dirty", "query", root.rstrip("\\")],
                       capture_output=True, text=True, creationflags=NOWIN)
    txt = (r.stdout + r.stderr).lower()
    # francais : "est integre" / "n'est pas integre" ; anglais : "is not dirty" / "is dirty"
    dirty = "n'est pas" in txt or ("is dirty" in txt and "not dirty" not in txt)
    return not dirty


def md5(path, chunk=4 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def copy_verified(src, dst, progress=lambda frac: None):
    """Copie par blocs avec progression, puis compare les MD5."""
    size = os.path.getsize(src)
    tmp = dst + ".copie"
    done = 0
    with open(src, "rb") as fi, open(tmp, "wb") as fo:
        for b in iter(lambda: fi.read(4 << 20), b""):
            fo.write(b); done += len(b); progress(done / max(size, 1))
        fo.flush(); os.fsync(fo.fileno())
    os.replace(tmp, dst)
    a, b = md5(src), md5(dst)
    if a != b:
        from .i18n import tr
        raise RuntimeError(tr("Copie corrompue sur {dst} (MD5 {got} au lieu de {want})", dst=dst, got=b, want=a))
    return a


def eject(root):
    ps = (f"$s=New-Object -ComObject Shell.Application;"
          f"$s.Namespace(17).ParseName('{root.rstrip(chr(92))}').InvokeVerb('Eject')")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, creationflags=NOWIN)
    return not os.path.exists(root)
