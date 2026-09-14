"""Bibliotheque de voitures : un dossier par modele, nomme comme la voiture.

    models/
      Subaru BRZ 2022/
        Subaru BRZ 2022.glb     modele (.glb, .gltf ou .obj)
        cover.jpg               apercu affiche dans la bibliotheque (facultatif)

Les dossiers lus sont donnes par paths.library_dirs() ; un meme nom vu dans
plusieurs dossiers n'apparait qu'une fois (le premier l'emporte).
"""
import os
from dataclasses import dataclass

from . import paths

MODEL_EXTENSIONS = (".glb", ".gltf", ".obj")        # ordre de preference
COVER_NAMES = ("cover.jpg", "cover.jpeg", "cover.png")


@dataclass
class Entry:
    name: str
    folder: str
    model: str
    cover: str | None


def _model_in(folder):
    files = {f.lower(): f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))}
    for ext in MODEL_EXTENSIONS:
        hits = sorted(f for low, f in files.items() if low.endswith(ext))
        if hits:
            same = [f for f in hits if os.path.splitext(f)[0] == os.path.basename(folder)]
            return os.path.join(folder, (same or hits)[0])
    return None


def scan(dirs=None):
    entries, seen = [], set()
    for root in dirs if dirs is not None else paths.library_dirs():
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root), key=str.lower):
            folder = os.path.join(root, name)
            if not os.path.isdir(folder) or name.lower() in seen or name.startswith((".", "_")):
                continue
            model = _model_in(folder)
            if not model:
                continue
            cover = next((os.path.join(folder, c) for c in COVER_NAMES if os.path.isfile(os.path.join(folder, c))), None)
            entries.append(Entry(name, folder, model, cover))
            seen.add(name.lower())
    return entries
