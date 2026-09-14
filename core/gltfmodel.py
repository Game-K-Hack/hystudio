"""Lecture d'un modele glTF 2.0 (.gltf avec ses .bin ou donnees integrees, .glb).

Le glTF porte ce que l'OBJ perd souvent : textures, coordonnees de texture et
materiaux PBR (couleur, metal, rugosite, normal map, emission, transparence).

HyStudio lit lui-meme le fichier, sans passer par l'importeur glTF de Blender :
celui-ci tronque les noms a 63 octets et renomme les doublons (KITT a des noms
de 86 caracteres, dont un en double), la vue 3D et le rendu ne designeraient
plus les memes pieces. Blender recoit donc exactement la geometrie lue ici
(blender/render_project.py, build_from_geometry).

Reperes : glTF est en Y vertical et en metres, comme les OBJ lus par HyStudio.
Une piece = un noeud portant un maillage, transformations de ses parents
appliquees ; une plage par primitive (un materiau).
"""
import base64, hashlib, json, os, struct, urllib.parse

import numpy as np

from . import mtl, presets
from .paths import CACHE as CACHE_DIR

COMPONENTS = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def _read(path):
    """(json, bloc binaire du .glb ou None)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] == b"glTF":
        pos, doc, blob = 12, None, None
        while pos < len(data):
            length, kind = struct.unpack_from("<I4s", data, pos)
            chunk = data[pos + 8:pos + 8 + length]
            if kind == b"JSON":
                doc = json.loads(chunk.decode("utf-8"))
            elif kind == b"BIN\x00":
                blob = chunk
            pos += 8 + length
        return doc, blob
    return json.loads(data.decode("utf-8")), None


def _uri_bytes(uri, base):
    if uri.startswith("data:"):
        return base64.b64decode(uri.split(",", 1)[1])
    with open(os.path.join(base, urllib.parse.unquote(uri)), "rb") as f:
        return f.read()


class _Reader:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.base = os.path.dirname(self.path)      # chemins de textures absolus : Blender tourne ailleurs
        self.g, glb = _read(path)
        self.buffers = [glb if ("uri" not in b and glb is not None) else _uri_bytes(b["uri"], self.base)
                        for b in self.g.get("buffers", [])]

    def accessor(self, i):
        a = self.g["accessors"][i]
        dtype, width = COMPONENTS[a["componentType"]], WIDTH[a["type"]]
        count = a["count"]
        if "bufferView" not in a:
            out = np.zeros((count, width), np.float32)
        else:
            bv = self.g["bufferViews"][a["bufferView"]]
            buf = self.buffers[bv["buffer"]]
            start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
            item = np.dtype(dtype).itemsize * width
            stride = bv.get("byteStride") or item
            if stride == item:
                out = np.frombuffer(buf, dtype, count * width, start).reshape(count, width)
            else:                                         # donnees entrelacees
                raw = np.frombuffer(buf, np.uint8, stride * (count - 1) + item, start)
                rows = np.lib.stride_tricks.as_strided(raw, (count, item), (stride, 1))
                out = np.frombuffer(np.ascontiguousarray(rows).tobytes(), dtype).reshape(count, width)
        if a.get("normalized") and dtype != np.float32:
            out = out.astype(np.float32) / np.iinfo(dtype).max
        return out

    def bufferview_bytes(self, i):
        bv = self.g["bufferViews"][i]
        start = bv.get("byteOffset", 0)
        return bytes(self.buffers[bv["buffer"]][start:start + bv["byteLength"]])


def _node_matrix(n):
    if "matrix" in n:
        return np.array(n["matrix"], np.float64).reshape(4, 4).T
    t = np.eye(4)
    t[:3, 3] = n.get("translation", [0, 0, 0])
    x, y, z, w = n.get("rotation", [0, 0, 0, 1])
    r = np.eye(4)
    r[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                 [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                 [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    s = np.diag([*n.get("scale", [1, 1, 1]), 1.0])
    return t @ r @ s


def _triangles(mode, idx):
    """Indices de triangles pour les modes 4 (liste), 5 (bande) et 6 (eventail)."""
    if mode == 4:
        return idx[: len(idx) // 3 * 3].reshape(-1, 3)
    if mode == 5:
        k = np.arange(len(idx) - 2)
        tri = np.stack([idx[k], idx[k + 1], idx[k + 2]], 1)
        odd = k % 2 == 1
        tri[odd, 0], tri[odd, 1] = idx[k[odd] + 1], idx[k[odd]]      # garde l'orientation
    elif mode == 6:
        k = np.arange(1, len(idx) - 1)
        tri = np.stack([np.full_like(k, idx[0]), idx[k], idx[k + 1]], 1)
    else:
        return np.zeros((0, 3), np.int64)
    keep = (tri[:, 0] != tri[:, 1]) & (tri[:, 1] != tri[:, 2]) & (tri[:, 0] != tri[:, 2])  # bandes degenerees
    return tri[keep]


def _texture_file(r, tex_ref, sig, cache):
    """Chemin d'image d'une reference de texture ; les images integrees sont extraites dans le cache."""
    if not tex_ref:
        return None
    tex = r.g.get("textures", [])[tex_ref["index"]]
    src = tex.get("source")
    if src is None:
        return None
    img = r.g["images"][src]
    uri = img.get("uri", "")
    if uri and not uri.startswith("data:"):
        p = os.path.join(r.base, urllib.parse.unquote(uri))
        return p if os.path.isfile(p) else None
    mime = img.get("mimeType") or (uri[5:uri.index(";")] if uri.startswith("data:") else "image/png")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(mime, ".png")
    out = os.path.join(cache, f"{sig}_{src}{ext}")
    if not os.path.exists(out):
        data = _uri_bytes(uri, r.base) if uri else r.bufferview_bytes(img["bufferView"])
        with open(out, "wb") as f:
            f.write(data)
    return out


def _material_info(r, m, sig, cache):
    pbr = m.get("pbrMetallicRoughness", {})
    ext = m.get("extensions", {})
    tex = lambda ref: _texture_file(r, ref, sig, cache)
    return {
        "color": [float(c) for c in pbr.get("baseColorFactor", [1, 1, 1, 1])],
        "color_tex": tex(pbr.get("baseColorTexture")),
        "metal": float(pbr.get("metallicFactor", 1.0)),
        "rough": float(pbr.get("roughnessFactor", 1.0)),
        "mr_tex": tex(pbr.get("metallicRoughnessTexture")),
        "normal_tex": tex(m.get("normalTexture")),
        "normal_scale": float(m.get("normalTexture", {}).get("scale", 1.0)),
        "emissive": [float(c) for c in m.get("emissiveFactor", [0, 0, 0])],
        "emissive_tex": tex(m.get("emissiveTexture")),
        "emissive_strength": float(ext.get("KHR_materials_emissive_strength", {}).get("emissiveStrength", 1.0)),
        "alpha_mode": m.get("alphaMode", "OPAQUE"),
        "alpha_cutoff": float(m.get("alphaCutoff", 0.5)),
        "transmission": float(ext.get("KHR_materials_transmission", {}).get("transmissionFactor", 0.0)),
        "ior": float(ext.get("KHR_materials_ior", {}).get("ior", 1.5)),
    }


def parse(path, progress=None):
    """-> (pieces [(nom, materiaux, positions, normales, uvs, plages)], materiaux {nom: info})."""
    r = _Reader(path)
    g = r.g
    sig = hashlib.sha1(os.path.abspath(path).encode()).hexdigest()[:10]
    tex_cache = os.path.join(CACHE_DIR, "textures_gltf")
    os.makedirs(tex_cache, exist_ok=True)

    # noms de materiaux uniques ; ils servent de cle dans les projets
    matnames, seen = [], set()
    for i, m in enumerate(g.get("materials", [])):
        name = m.get("name") or f"Material_{i}"
        if name in seen:
            name = f"{name}_{i}"
        seen.add(name); matnames.append(name)
    materials = {matnames[i]: _material_info(r, m, sig, tex_cache) for i, m in enumerate(g.get("materials", []))}

    nodes = g.get("nodes", [])
    scene = g.get("scenes", [{}])[g.get("scene", 0)] if g.get("scenes") else {"nodes": list(range(len(nodes)))}
    stack = [(i, np.eye(4)) for i in scene.get("nodes", [])]
    mesh_nodes = []
    while stack:
        i, parent = stack.pop(0)
        n = nodes[i]
        world = parent @ _node_matrix(n)
        if "mesh" in n:
            mesh_nodes.append((i, world))
        stack[0:0] = [(c, world) for c in n.get("children", [])]

    parts, names = [], set()
    for k, (ni, world) in enumerate(mesh_nodes):
        n = nodes[ni]
        mesh = g["meshes"][n["mesh"]]
        name = n.get("name") or mesh.get("name") or f"piece_{ni:03d}"
        base, j = name, 2
        while name in names:                              # doublon : suffixe lisible
            name = f"{base} ({j})"; j += 1
        names.add(name)
        normal_m = np.linalg.inv(world[:3, :3]).T
        pos_l, nor_l, uv_l, ranges, mats = [], [], [], [], []
        count = 0
        for prim in mesh.get("primitives", []):
            at = prim["attributes"]
            if "POSITION" not in at:
                continue
            p = r.accessor(at["POSITION"]).astype(np.float64)
            idx = (r.accessor(prim["indices"])[:, 0].astype(np.int64) if "indices" in prim
                   else np.arange(len(p), dtype=np.int64))
            tri = _triangles(prim.get("mode", 4), idx)
            if not len(tri):
                continue
            corners = tri.reshape(-1)
            pw = p @ world[:3, :3].T + world[:3, 3]
            pos = pw[corners].astype(np.float32)
            if "NORMAL" in at:
                nn = r.accessor(at["NORMAL"]).astype(np.float64) @ normal_m.T
                nn /= np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-12)
                nor = nn[corners].astype(np.float32)
            else:
                t = pos.reshape(-1, 3, 3)
                fn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
                fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
                nor = np.repeat(fn, 3, axis=0).astype(np.float32)
            if np.linalg.det(world[:3, :3]) < 0:            # symetrie : on retablit l'orientation
                pos = pos.reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3)
                nor = nor.reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3)
                corners = corners.reshape(-1, 3)[:, ::-1].reshape(-1)
            uv = (r.accessor(at["TEXCOORD_0"])[corners].astype(np.float32) if "TEXCOORD_0" in at
                  else np.zeros((len(corners), 2), np.float32))
            mat = matnames[prim["material"]] if "material" in prim else "defaut"
            ranges.append((count, len(pos), mat))
            if mat not in mats:
                mats.append(mat)
            pos_l.append(pos); nor_l.append(nor); uv_l.append(uv)
            count += len(pos)
        if pos_l:
            parts.append((name, mats, np.concatenate(pos_l), np.concatenate(nor_l), np.concatenate(uv_l), ranges))
        if progress:
            progress(0.95 * (k + 1) / max(len(mesh_nodes), 1))
    return parts, materials


def has_texture(info):
    return any(info.get(k) for k in ("color_tex", "mr_tex", "normal_tex", "emissive_tex"))


def default_spec(name, info):
    """Matiere de depart : les materiaux textures gardent le materiau du fichier ;
    les autres deviennent des matieres HyStudio modifiables (peinture, verre...)."""
    if has_texture(info):
        return {"kind": "origine"}
    r, g, b, a = info["color"]
    fake = {"Kd": (r, g, b), "Pm": (info["metal"],), "Pr": (info["rough"],)}
    if info["alpha_mode"] == "BLEND" and a < 0.95:
        fake["d"] = (a,)
    if info["transmission"] > 0.1:
        fake["d"] = (max(0.0, 1.0 - info["transmission"]),)
    return presets.complete(mtl.to_spec(name, fake))
