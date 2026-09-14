"""Fichier de materiaux .mtl accompagnant un OBJ : lecture et conversion en matieres HyStudio.

Le .mtl est facultatif : a la creation d'un projet, l'utilisateur choisit de
reprendre ses valeurs ou non (et peut les importer plus tard, menu Fichier).

Beaucoup d'exportateurs (3ds Max notamment) ecrivent des valeurs bouche-trou,
identiques pour tous les materiaux : gris Kd 0.588, Ks 0, Ns 10. Elles ne
disent rien de la voiture et sont ignorees ; ces materiaux gardent la matiere
devinee d'apres leur nom. Les couleurs Kd sont lineaires, comme Blender les lit.

Conventions rencontrees : d = opacite, Tr = transparence (1 - d) ; Pm / Pr =
metal / rugosite (exportateurs PBR) ; Ks > 1 = forte reflexion (3ds Max).
Les textures (map_Kd) ne sont pas reprises.
"""
import os, re

from . import presets

# nom du materiau -> type de matiere, dans l'ordre de priorite
NAME_HINTS = [
    (("glass", "verre", "window", "vitre", "lens", "lamp_cover"), "verre"),
    (("tire", "tyre", "rubber", "pneu"), "caoutchouc"),
    (("chrome", "mirror", "miroir"), "chrome"),
    (("paint", "carpaint", "body", "carross"), "peinture"),
    (("rim", "wheel", "metal", "silver", "alu", "brake", "disk", "disc", "jante"), "metal"),
]


def guess_kind(name):
    n = name.lower()
    for keys, kind in NAME_HINTS:
        if any(k in n for k in keys):
            return kind
    return "plastique"


def find_for(obj_path):
    """Chemin du .mtl annonce par l'OBJ (mtllib), sinon du .mtl de meme nom ; None s'il n'existe pas."""
    base = os.path.dirname(obj_path)
    try:
        with open(obj_path, "rb") as f:
            head = f.read(1 << 16)
        m = re.search(rb"^mtllib[ \t]+(.+?)\s*$", head, re.M)
        if m:
            p = os.path.join(base, m.group(1).decode("utf-8", "replace"))
            if os.path.isfile(p):
                return p
    except OSError:
        pass
    p = os.path.splitext(obj_path)[0] + ".mtl"
    return p if os.path.isfile(p) else None


def parse(path):
    """{nom: {cle: valeur}} ; les valeurs numeriques sont des tuples de float."""
    mats, cur = {}, None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            t = line.strip().split(None, 1)
            if not t or t[0].startswith("#"):
                continue
            key, rest = t[0], (t[1] if len(t) > 1 else "")
            if key == "newmtl":
                cur = mats.setdefault(rest.strip(), {})
            elif cur is not None:
                try:
                    cur[key] = tuple(float(x) for x in rest.split())
                except ValueError:
                    cur[key] = rest.strip()
    return mats


def _num(m, key, default=None):
    v = m.get(key)
    return v[0] if isinstance(v, tuple) and v else default


def _rgb(m, key):
    v = m.get(key)
    return tuple(v[:3]) if isinstance(v, tuple) and len(v) >= 3 else None


def is_placeholder(m, name=""):
    """Valeurs par defaut d'exportateur : n'apprennent rien sur la matiere."""
    if re.fullmatch(r"wire_\d{9}", name):
        return True             # 3ds Max : couleur d'affichage de l'objet, pas une matiere
    kd = _rgb(m, "Kd")
    grey = kd is None or all(abs(c - 0.588) < 0.002 for c in kd)
    ks = _rgb(m, "Ks")
    no_spec = ks is None or max(ks) == 0
    opaque = _num(m, "d", 1.0) >= 0.999 and _num(m, "Tr", 0.0) <= 0.001
    return grey and no_spec and opaque and "Pm" not in m and "Pr" not in m


def _opacity(m, hint):
    """d fait foi. Tr seul n'est cru que pour un materiau nomme comme du verre :
    certains exportateurs y ecrivent autre chose (KITT : Tr 0.5 sur les jantes)."""
    if "d" in m:
        return _num(m, "d", 1.0)
    if "Tr" in m and hint == "verre":
        return 1.0 - _num(m, "Tr", 0.0)
    return 1.0


def _roughness(m):
    if "Pr" in m:
        return round(max(0.0, min(1.0, _num(m, "Pr"))), 3)
    ns = _num(m, "Ns")
    if ns is None:
        return 0.35
    return round(0.05 + 0.8 * max(0.0, 1.0 - min(ns, 100.0) / 100.0), 3)


def to_spec(name, m):
    """Matiere HyStudio deduite d'un materiau MTL informatif."""
    kd = _rgb(m, "Kd") or (0.5, 0.5, 0.5)
    kd = tuple(max(0.0, min(1.0, c)) for c in kd)
    hint = guess_kind(name)
    rough = _roughness(m)
    op = _opacity(m, hint)
    ks = _rgb(m, "Ks") or (0.0, 0.0, 0.0)
    # metal PBR : ignore s'il est totalement rugueux (KITT marque ainsi son habitacle)
    metal = _num(m, "Pm", 0.0) if rough < 0.9 else 0.0

    if op < 0.95 or hint == "verre":
        hi = max(kd)
        # vitre claire notee noire ou grise : pas de teinte ; feux colores : teinte saturee
        saturated = hi > 0.05 and (hi - min(kd)) / hi > 0.35
        tint = presets.linear_to_hex(tuple(c / hi for c in kd)) if saturated else "#FFFFFF"
        transmission = round(max(0.05, min(1.0, 1.0 - 0.9 * op)) if op < 0.95 else 0.9, 3)
        return {"kind": "verre", "color": tint, "transmission": transmission, "reflet": 1.0}
    color = presets.linear_to_hex(kd)
    if hint == "peinture":
        finish = "mat" if "mat" in name.lower() else ("satine" if rough > 0.6 and "Pr" not in m else "brillant")
        return {"kind": "peinture", "color": color, "finish": finish}
    if hint == "caoutchouc":
        return {"kind": "caoutchouc", "color": color, "rough": max(rough, 0.6)}
    if hint == "chrome" or (metal >= 0.5 and max(kd) > 0.45 and rough < 0.3) or (max(ks) > 1.5 and max(kd) < 0.05):
        return {"kind": "chrome", "reflect": round(max(0.3, min(1.0, max(max(kd), min(max(ks), 1.0)))), 3),
                "rough": round(min(rough, 0.2), 3)}
    if hint == "metal" or metal >= 0.5:
        return {"kind": "metal", "color": color, "rough": rough}
    return {"kind": "plastique", "color": color, "rough": rough}


def specs_for(path, material_names):
    """(matieres {nom: spec} pour les materiaux informatifs du modele, nombre de materiaux du .mtl)."""
    mats = parse(path)
    out = {}
    for name in material_names:
        m = mats.get(name)
        if m is not None and not is_placeholder(m, name):
            out[name] = presets.complete(to_spec(name, m))
    return out, len(mats)
