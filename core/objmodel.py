"""Lecture d'un modele OBJ piece par piece, avec le meme decoupage que Blender.

Blender (importeur OBJ, reglages par defaut) cree un objet par ligne 'o'. Le
logiciel doit utiliser exactement les memes pieces et les memes noms : ce que
l'on clique dans la vue 3D doit etre ce que Blender rendra. trimesh, lui,
regroupe par materiau, d'ou ce lecteur.

Chaque piece est une liste de triangles NON indexes (position et normale par
coin) : les normales du fichier sont gardees telles quelles, aretes vives
comprises, et l'affichage OpenGL n'a pas a reindexer.

Premier chargement : ~15 s pour 1,4 M de triangles. Le resultat est mis en
cache (cache/<nom>.npz), invalide si le fichier source change.

Les fichiers glTF (.gltf, .glb) passent par core/gltfmodel.py et donnent le
meme Model, avec en plus les coordonnees de texture et les materiaux du fichier.
Blender relit alors la geometrie depuis ce cache (Model.cache).
"""
import hashlib, json, os
from dataclasses import dataclass, field

import numpy as np

from .paths import CACHE as CACHE_DIR
CACHE_VERSION = 4
GLTF_EXTENSIONS = (".gltf", ".glb")


@dataclass
class Part:
    name: str                 # nom de l'objet OBJ, identique a Blender
    material: str             # materiau d'origine (premier 'usemtl' de la piece)
    positions: np.ndarray     # (n, 3) float32, un coin de triangle par ligne
    normals: np.ndarray       # (n, 3) float32
    materials: list = field(default_factory=list)   # tous les materiaux de la piece
    # (debut, nombre de coins, materiau) : une piece peut porter plusieurs
    # materiaux ; un modele non decoupe les porte meme tous
    ranges: list = field(default_factory=list)
    uvs: np.ndarray = None    # (n, 2) float32, glTF seulement (v vers le bas, convention glTF)

    @property
    def triangles(self):
        return len(self.positions) // 3

    @property
    def bounds(self):
        return self.positions.min(axis=0), self.positions.max(axis=0)


@dataclass
class Model:
    path: str
    parts: list               # [Part], dans l'ordre du fichier
    unit_scale: float         # multiplicateur vers le metre (0.01 si le fichier est en cm)
    source_materials: dict = field(default_factory=dict)   # glTF : {materiau: infos PBR et textures}
    cache: str = ""           # fichier .npz de la geometrie lue

    @property
    def is_gltf(self):
        return os.path.splitext(self.path)[1].lower() in GLTF_EXTENSIONS

    def part(self, name):
        for p in self.parts:
            if p.name == name:
                return p
        return None

    @property
    def triangles(self):
        return sum(p.triangles for p in self.parts)

    @property
    def bounds(self):
        lo = np.min([p.bounds[0] for p in self.parts], axis=0)
        hi = np.max([p.bounds[1] for p in self.parts], axis=0)
        return lo, hi

    @property
    def separated(self):
        """False si le fichier ne decoupe pas le vehicule en pieces ('o').

        Tout arrive alors en un seul objet : les matieres par materiau restent
        possibles, pas la selection piece par piece ni les images."""
        return len(self.parts) > 1

    def materials(self):
        seen = []
        for p in self.parts:
            for m in p.materials:
                if m not in seen:
                    seen.append(m)
        return seen


def _signature(path):
    st = os.stat(path)
    return hashlib.sha1(f"{os.path.abspath(path)}|{st.st_size}|{st.st_mtime_ns}|{CACHE_VERSION}"
                        .encode()).hexdigest()[:16]


def _parse(path, progress=None):
    """OBJ -> pieces. Les indices OBJ sont globaux et commencent a 1."""
    with open(path, "rb") as f:
        data = f.read()
    lines = data.split(b"\n")
    total = len(lines)

    v, vn = [], []
    parts, cur = [], None       # cur = [nom, materiaux, faces v, faces vn]
    mat = "defaut"

    def new_part(name):
        return [name, [], [], [], []]           # nom, materiaux, faces v, faces vn, plages

    for li, line in enumerate(lines):
        if not line:
            continue
        c = line[0]
        if c == 118:                                   # 'v'
            if line[1] == 32:                          # 'v '
                v.append(line[2:])
            elif line[1] == 110:                       # 'vn'
                vn.append(line[3:])
        elif c == 102:                                 # 'f'
            if cur is None:
                cur = new_part("piece_000"); parts.append(cur)
            toks = line.split()[1:]
            idx = [t.split(b"/") for t in toks]
            vi = [int(t[0]) for t in idx]
            ni = [int(t[2]) if len(t) > 2 and t[2] else 0 for t in idx]
            if not cur[4] or cur[4][-1][1] != mat:     # nouvelle plage de materiau
                cur[4].append([len(cur[2]), mat])
            for k in range(1, len(vi) - 1):            # eventail : quads et n-gones
                cur[2].extend((vi[0], vi[k], vi[k + 1]))
                cur[3].extend((ni[0], ni[k], ni[k + 1]))
            if mat not in cur[1]:
                cur[1].append(mat)
        elif c == 111 and line[1:2] == b" ":           # 'o '
            cur = new_part(line[2:].strip().decode("utf-8", "replace"))
            parts.append(cur)
        elif c == 117 and line.startswith(b"usemtl"):
            mat = line[6:].strip().decode("utf-8", "replace")
        if progress and li % 400000 == 0:
            progress(0.8 * li / total)

    if progress:
        progress(0.85)
    V = np.array(b" ".join(v).split(), dtype=np.float32).reshape(-1, 3)
    N = np.array(b" ".join(vn).split(), dtype=np.float32).reshape(-1, 3) if vn else None

    out = []
    for name, mats, fv, fn, rng in parts:
        if not fv:
            continue
        iv = np.asarray(fv, dtype=np.int64) - 1
        pos = V[iv]
        in_ = np.asarray(fn, dtype=np.int64)
        if N is not None and (in_ > 0).all():
            nor = N[in_ - 1]
        else:                                          # pas de normales : normale de face
            t = pos.reshape(-1, 3, 3)
            n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
            n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
            nor = np.repeat(n, 3, axis=0).astype(np.float32)
        bounds = [r[0] for r in rng] + [len(fv)]
        ranges = [(bounds[i], bounds[i + 1] - bounds[i], rng[i][1]) for i in range(len(rng))]
        out.append(Part(name, mats[0] if mats else "defaut", pos, nor.astype(np.float32), mats, ranges))
    if progress:
        progress(1.0)
    return out


def load(path, progress=None):
    """Charge le modele (depuis le cache s'il est a jour)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"{os.path.splitext(os.path.basename(path))[0]}_{_signature(path)}.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=False)
        uvs_all = z["uvs"] if "uvs" in z.files else None
        srcmats = json.loads(str(z["srcmats"])) if "srcmats" in z.files else {}
        names = [str(x) for x in z["names"]]
        mats = [str(x) for x in z["mats"]]
        allm = [str(x).split("\t") for x in z["allmats"]]
        offs = z["offsets"]
        P, NN = z["positions"], z["normals"]
        rng = z["ranges"]                      # (piece, debut, nombre, indice de materiau)
        matnames = [str(x) for x in z["matnames"]]
        parts = [Part(names[i], mats[i], P[offs[i]:offs[i + 1]], NN[offs[i]:offs[i + 1]], allm[i],
                      [(int(r[1]), int(r[2]), matnames[int(r[3])]) for r in rng if r[0] == i],
                      uvs_all[offs[i]:offs[i + 1]] if uvs_all is not None else None)
                 for i in range(len(names))]
    else:
        srcmats = {}
        if os.path.splitext(path)[1].lower() in GLTF_EXTENSIONS:
            from . import gltfmodel
            raw, srcmats = gltfmodel.parse(path, progress)
            parts = [Part(name, mats[0] if mats else "defaut", pos, nor, mats, ranges, uv)
                     for name, mats, pos, nor, uv, ranges in raw]
        else:
            parts = _parse(path, progress)
        offs = np.cumsum([0] + [len(p.positions) for p in parts])
        matnames = sorted({r[2] for p in parts for r in p.ranges})
        ranges = np.array([(i, r[0], r[1], matnames.index(r[2])) for i, p in enumerate(parts)
                           for r in p.ranges], dtype=np.int64).reshape(-1, 4)
        extra = {}
        if srcmats:
            extra = {"uvs": np.concatenate([p.uvs for p in parts]), "srcmats": np.array(json.dumps(srcmats))}
        np.savez(cache, **extra, names=np.array([p.name for p in parts]),
                 ranges=ranges, matnames=np.array(matnames),
                 mats=np.array([p.material for p in parts]),
                 allmats=np.array(["\t".join(p.materials) for p in parts]),
                 offsets=offs,
                 positions=np.concatenate([p.positions for p in parts]),
                 normals=np.concatenate([p.normals for p in parts]))
    return Model(os.path.abspath(path), parts, guess_unit_scale(parts), srcmats, cache)


UNIT_CHOICES = (1.0, 0.1, 0.01, 0.001, 0.0001)      # m, dm, cm, mm, 1/10 mm
TYPICAL_LENGTH = 4.5                                  # m, longueur d'une voiture


def guess_unit_scale(parts):
    """Unite du fichier : celle qui donne au vehicule une longueur plausible.

    Les exports courants sont en m, cm ou mm (l'Elantra N Line en mm, le Supra
    d'origine en 1/10 mm). Supposer "cm des qu'on depasse 50 unites" rendait
    l'Elantra dix fois trop grande : la lumiere d'habitacle, en watts fixes,
    y devenait invisible. Longueur = plus grande dimension horizontale,
    mesuree sans les points isoles (0,1 % de chaque cote)."""
    P = np.concatenate([p.positions[::7] for p in parts])
    lo, hi = np.percentile(P, [0.1, 99.9], axis=0)
    length = float(max(hi[0] - lo[0], hi[2] - lo[2], 1e-9))
    return min(UNIT_CHOICES, key=lambda s: abs(np.log(length * s / TYPICAL_LENGTH)))

