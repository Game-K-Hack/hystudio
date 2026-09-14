"""Matieres proposees dans HyStudio, partagees par l'interface et le rendu.

Une matiere est un dictionnaire JSON : {"kind": ..., <champs du type>}. Les
couleurs sont en sRGB hexadecimal (#RRGGBB), converties en lineaire au rendu.
KINDS decrit chaque type et ses champs : l'interface en deduit ses controles,
le rendu (blender/render_project.py) en deduit le shader. Libelles en francais,
traduits a l'affichage (core/i18n.py).
"""

KINDS = {
    "peinture": {
        "label": "Peinture carrosserie",
        "fields": [
            ("color", "Couleur", "color", "#E7E8E9"),
            ("finish", "Finition", ("brillant", "satine", "mat"), "brillant"),
        ],
    },
    "chrome": {
        "label": "Chrome",
        "fields": [
            ("reflect", "Réflectance", (0.10, 1.00), 0.90),
            ("rough", "Poli (0 = miroir)", (0.0, 0.5), 0.06),
        ],
    },
    "metal": {
        "label": "Métal",
        "fields": [
            ("color", "Couleur", "color", "#C4C6CA"),
            ("rough", "Rugosité", (0.0, 1.0), 0.25),
        ],
    },
    "plastique": {
        "label": "Plastique",
        "fields": [
            ("color", "Couleur", "color", "#1C1C1D"),
            ("rough", "Rugosité", (0.0, 1.0), 0.35),
        ],
    },
    "caoutchouc": {
        "label": "Caoutchouc",
        "fields": [
            ("color", "Couleur", "color", "#1C1C1C"),
            ("rough", "Rugosité", (0.0, 1.0), 0.85),
        ],
    },
    "verre": {
        "label": "Verre",
        "fields": [
            ("color", "Teinte", "color", "#FFFFFF"),
            ("transmission", "Transmission par face", (0.05, 1.00), 0.90),
            ("reflet", "Force du reflet", (0.0, 5.0), 1.0),
        ],
    },
    "image": {
        "label": "Image (plaque, logo)",
        "fields": [
            ("image", "Fichier image", "file", ""),
            ("rough", "Rugosité", (0.0, 1.0), 0.38),
            ("coat", "Vernis", (0.0, 1.0), 0.35),
        ],
    },
    "masque": {
        "label": "Masque (invisible)",
        "fields": [],
    },
    # glTF : le materiau du fichier tel quel (textures, normal map, emission) ;
    # propose seulement si le modele en fournit un (Model.source_materials)
    "origine": {
        "label": "Matériau d'origine (textures)",
        "fields": [],
    },
}

FINISH = {   # (rugosite peinture, epaisseur vernis, rugosite vernis)
    "brillant": (0.30, 1.00, 0.03),
    "satine":   (0.42, 0.45, 0.18),
    "mat":      (0.58, 0.00, 0.30),
}


# ----------------------------------------------------------------- autocollant
# Une image posee PAR-DESSUS la matiere (logo sur une portiere, bande sur le
# capot), a l'inverse du type 'image' qui remplace toute la matiere de la
# piece et ne convient qu'a une piece plate (plaque). Stocke dans spec["decal"].
#   dir   direction de projection, reperes OBJ (Y vertical), vers l'observateur
#   size  largeur, en fraction de l'etendue de la zone vue dans cette direction
#   x, y  decalage du centre, en fraction de la demi-etendue (-1 .. 1)
#   rot   rotation en degres
# La zone de reference est la piece, ou toutes les pieces du materiau quand la
# matiere est posee sur le materiau : un seul autocollant pour tout le groupe.
DECAL_KINDS = ("peinture", "chrome", "metal", "plastique", "caoutchouc")


def default_decal(direction=(0.0, 0.0, 1.0)):
    return {"image": "", "dir": [float(c) for c in direction], "size": 0.5, "x": 0.0, "y": 0.0, "rot": 0.0}


def decal_of(spec):
    """Autocollant actif de la matiere, ou None."""
    d = spec.get("decal")
    if spec.get("kind") in DECAL_KINDS and d and d.get("image"):
        return {**default_decal(), **d}
    return None


def default_spec(kind):
    return {"kind": kind, **{k: d for k, _, _, d in KINDS[kind]["fields"]}}


def complete(spec):
    """Complete une matiere avec les valeurs par defaut de son type."""
    out = default_spec(spec.get("kind", "plastique"))
    out.update(spec)
    return out


def hex_to_srgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def linear_to_hex(rgb):
    def enc(x):
        x = max(0.0, min(1.0, x))
        s = 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
        return round(s * 255)
    return "#%02X%02X%02X" % tuple(enc(x) for x in rgb)


def display_color(spec):
    """Couleur approchee pour la vue 3D (sRGB 0-1), sans rendu physique."""
    s = complete(spec)
    k = s["kind"]
    if k in ("peinture", "metal", "plastique", "caoutchouc", "verre"):
        return hex_to_srgb(s["color"])
    if k == "chrome":
        v = 0.35 + 0.6 * s["reflect"]
        return (v, v, v * 1.02)
    if k == "image":
        return (0.92, 0.92, 0.92)
    return (0.5, 0.5, 0.5)
