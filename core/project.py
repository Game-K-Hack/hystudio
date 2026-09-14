"""Projet HyStudio : un modele, ses matieres, ses reglages de studio.

Enregistre en JSON (.hysp). Les anciens projets s'ouvrent toujours : .hyproj
(premiere extension de HyStudio) et .carproj (Car Studio, l'ancien nom). Les matieres s'appliquent a deux niveaux :
  materials  par materiau d'origine du modele (toutes les pieces qui le portent)
  parts      par piece, prioritaire (toit ouvrant, plaque, monogramme...)

Les chemins (modele, images) sont stockes relatifs au fichier projet quand
c'est possible, pour que le dossier reste deplacable.
"""
import copy, json, os

from . import paths, presets

FORMATS = ("hystudio", "carstudio")          # carstudio : ancien nom, toujours lu
EXTENSION = ".hysp"
OLD_EXTENSIONS = (".hyproj", ".carproj")

STUDIO_DEFAULTS = {
    "exposure": 0.0,        # IL
    "sharpen": 0,           # % de renforcement a l'encodage
    "views": 360,           # vues par tour
    "samples": 96,          # echantillons Cycles
    "cabin_light": 0.0,     # W, lumiere invisible dans l'habitacle
}


class Project:
    def __init__(self):
        self.path = None
        self.name = "Nouveau projet"
        self.model = ""
        self.materials = {}
        self.parts = {}
        self.labels = {}          # noms lisibles : pieces et materiaux
        self.studio = dict(STUDIO_DEFAULTS)

    # ----------------------------------------------------------- matieres
    def spec_for(self, part_name, material):
        """Matiere effective d'une piece : la sienne, sinon celle de son materiau."""
        if part_name in self.parts:
            return presets.complete(self.parts[part_name])
        if material in self.materials:
            return presets.complete(self.materials[material])
        return presets.default_spec("plastique")

    def label(self, key):
        return self.labels.get(key, key)

    # ----------------------------------------------------------- chemins
    def _rel(self, p):
        if not p or not self.path:
            return p
        try:
            return os.path.relpath(p, os.path.dirname(self.path))
        except ValueError:                     # autre lecteur
            return p

    def resolve(self, p):
        if not p:
            return p
        if os.path.isabs(p):
            return p
        base = os.path.dirname(self.path) if self.path else (paths.REPO or paths.PROJECTS)
        return os.path.normpath(os.path.join(base, p))

    # ----------------------------------------------------------- disque
    def to_dict(self, absolute=False):
        conv = (lambda p: self.resolve(p)) if absolute else self._rel

        def fix(spec):
            s = copy.deepcopy(spec)
            if s.get("kind") == "image" and s.get("image"):
                s["image"] = conv(self.resolve(s["image"]))
            if isinstance(s.get("decal"), dict) and s["decal"].get("image"):
                s["decal"]["image"] = conv(self.resolve(s["decal"]["image"]))
            return s

        return {
            "format": "hystudio", "version": 1,
            "name": self.name,
            "model": conv(self.resolve(self.model)),
            "materials": {k: fix(v) for k, v in self.materials.items()},
            "parts": {k: fix(v) for k, v in self.parts.items()},
            "labels": self.labels,
            "studio": self.studio,
        }

    def save(self, path=None):
        if path:
            self.path = os.path.abspath(path)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("format") not in FORMATS:
            from .i18n import tr
            raise ValueError(tr("{path} n'est pas un projet HyStudio", path=path))
        p = cls()
        p.path = os.path.abspath(path)
        p.name = d.get("name", p.name)
        p.model = d.get("model", "")
        p.materials = d.get("materials", {})
        p.parts = d.get("parts", {})
        p.labels = d.get("labels", {})
        p.studio = {**STUDIO_DEFAULTS, **d.get("studio", {})}
        return p


# ----------------------------------------------------------------- profils

def i20_profile():
    """Hyundai Elite i20 2017 (Hum3D) avec les reglages valides le 13/09/2026.

    Reprend exactement i20view/render_cycles.py : couleurs lineaires converties
    en sRGB, exposition -1,2 IL, vitres 81 %, habitacle 6 %, toit plein,
    monogrammes chrome profond, plaques personnelles, nettete +150 %, 720 vues.
    """
    L = presets.linear_to_hex
    p = Project()
    p.name = "Hyundai i20"
    p.model = paths.repo_file("interface", "Hyundai Elite i20 2017", "Hyundai Elite i20 2017.obj")
    black = {"kind": "plastique", "color": L((0.012, 0.012, 0.013)), "rough": 0.35}
    p.materials = {
        "carpaint":    {"kind": "peinture", "color": L((0.80, 0.81, 0.82)), "finish": "brillant"},
        "chrome":      {"kind": "chrome", "reflect": 0.90, "rough": 0.06},
        "black":       black,
        "interior":    {"kind": "plastique", "color": L((0.06, 0.06, 0.0612)), "rough": 0.75},
        "tire":        {"kind": "caoutchouc", "color": L((0.012, 0.012, 0.012)), "rough": 0.85},
        "rim":         {"kind": "metal", "color": L((0.55, 0.56, 0.58)), "rough": 0.22},
        "rim_second":  {"kind": "metal", "color": L((0.22, 0.23, 0.24)), "rough": 0.32},
        "brakedisk":   {"kind": "metal", "color": L((0.32, 0.32, 0.33)), "rough": 0.45},
        "mirror":      {"kind": "chrome", "reflect": 0.95, "rough": 0.01},
        "Material__2": {"kind": "plastique", "color": L((0.85, 0.85, 0.83)), "rough": 0.45},
        # teinte x transmission = transmission par coque du rendu valide :
        # vitres (0.90, 0.927, 0.945), optiques (0.96, 0.97, 0.98)
        "windowglass": {"kind": "verre", "color": L((0.9524, 0.9810, 1.0)), "transmission": 0.945, "reflet": 1.0},
        "clearglass":  {"kind": "verre", "color": L((0.9796, 0.9898, 1.0)), "transmission": 0.98, "reflet": 1.0},
        "redglass":    {"kind": "verre", "color": L((0.85, 0.06, 0.05)), "transmission": 1.0, "reflet": 1.0},
        "orangeglass": {"kind": "verre", "color": L((0.95, 0.42, 0.06)), "transmission": 1.0, "reflet": 1.0},
    }
    plate = paths.repo_file("interface", "immatriculation.png")
    badge = {"kind": "chrome", "reflect": 0.38, "rough": 0.02}
    p.parts = {
        "desirefx_me_178": dict(black),                      # toit ouvrant -> toit plein
        "desirefx_me_053": dict(badge), "desirefx_me_109": dict(badge),
        "desirefx_me_108": dict(badge), "desirefx_me_050": dict(badge),
        "desirefx_me_207": {"kind": "image", "image": plate, "rough": 0.38, "coat": 0.35},
        "desirefx_me_208": {"kind": "image", "image": plate, "rough": 0.38, "coat": 0.35},
    }
    p.labels = {
        "carpaint": "Peinture carrosserie", "black": "Plastiques noirs et toit",
        "chrome": "Chromes et optiques", "windowglass": "Vitres",
        "clearglass": "Optiques transparentes", "redglass": "Feux rouges",
        "orangeglass": "Clignotants", "interior": "Habitacle", "tire": "Pneus",
        "rim": "Jantes (clair)", "rim_second": "Jantes (foncé)",
        "brakedisk": "Disques de frein", "mirror": "Miroirs des rétroviseurs",
        "Material__2": "Plaques d'immatriculation",
        "desirefx_me_178": "Toit ouvrant", "desirefx_me_053": "Logo H arrière",
        "desirefx_me_109": "Inscription HYUNDAI", "desirefx_me_108": "Inscription HYUNDAI (point)",
        "desirefx_me_050": "Monogramme i20", "desirefx_me_207": "Plaque avant",
        "desirefx_me_208": "Plaque arrière",
    }                         # en francais : traduits a l'affichage (core/i18n.tr_label)
    p.studio = {"exposure": -1.2, "sharpen": 150, "views": 720, "samples": 96, "cabin_light": 0.0,
                # cadrage exact du rendu valide (sinon deduit de la taille du modele)
                "camera": {"dist": 6.30, "target_z": 0.64, "elev": 11.0, "fov": 24.0, "az0": 35.0}}
    return p
