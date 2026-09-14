"""Emplacements de HyStudio, lance depuis les sources ou compile en .exe (PyInstaller).

  RESOURCES  fichiers livres avec le logiciel, en lecture seule (script Blender,
             visionneuse i20view.exe) : dossier des sources, ou _internal de l'exe
  APP_DIR    dossier du logiciel : sources, ou dossier contenant HyStudio.exe
  CACHE      donnees recalculables (geometrie, textures glTF, rendus en cours) :
             cache/ des sources, ou %LOCALAPPDATA%\\HyStudio\\cache pour l'exe
  PROJECTS   projets de l'utilisateur : projets/ a cote du logiciel s'il est
             inscriptible, sinon Documents\\HyStudio
  REPO       depot hyundev s'il entoure le logiciel (Blender portable dans tools/,
             modele de la i20 dans interface/), sinon None
"""
import glob, os, sys

FROZEN = bool(getattr(sys, "frozen", False))
SOURCES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES = getattr(sys, "_MEIPASS", SOURCES)
APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if FROZEN else SOURCES


def _find_repo():
    d = APP_DIR
    for _ in range(5):                                 # dist\HyStudio\ est a 3 niveaux sous hyundev
        # le depot hyundev : dossier hystudio accompagne de interface/ ou tools/ (un simple
        # dossier « tools » chez un utilisateur ne doit pas etre pris pour le depot)
        if os.path.isdir(os.path.join(d, "hystudio")) and (
                os.path.isdir(os.path.join(d, "interface")) or os.path.isdir(os.path.join(d, "tools"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def _writable(d):
    try:
        os.makedirs(d, exist_ok=True)
        probe = os.path.join(d, ".ecriture")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
        return True
    except OSError:
        return False


REPO = _find_repo()

if FROZEN:
    CACHE = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "HyStudio", "cache")
    # projets/ a cote de l'exe s'il existe, sinon ceux des sources (exe compile dans hystudio\dist),
    # sinon a cote de l'exe s'il est inscriptible, sinon Documents\HyStudio (ex. Program Files)
    candidates = [os.path.join(APP_DIR, "projets")]
    if REPO:
        candidates.append(os.path.join(REPO, "hystudio", "projets"))
    PROJECTS = next((c for c in candidates if os.path.isdir(c)), None)
    if PROJECTS is None:
        PROJECTS = candidates[0] if _writable(candidates[0]) else \
            os.path.join(os.path.expanduser("~"), "Documents", "HyStudio")
else:
    CACHE = os.path.join(SOURCES, "cache")
    PROJECTS = os.path.join(SOURCES, "projets")

WORK = os.path.join(CACHE, "travail")
RENDERER = os.path.join(RESOURCES, "blender", "render_project.py")


def viewer_exe():
    """Visionneuse de l'autoradio : livree avec l'exe, sinon celle du depot."""
    for p in (os.path.join(RESOURCES, "i20view", "i20view.exe"),
              os.path.join(REPO or "", "i20view", "bin", "i20view.exe")):
        if os.path.isfile(p):
            return p
    return None


def find_blender():
    """Blender portable (a cote de l'exe ou dans tools/ du depot), sinon installation standard."""
    cands = []
    for base in (APP_DIR, REPO):
        if base:
            cands += sorted(glob.glob(os.path.join(base, "tools", "blender*", "blender.exe")), reverse=True)
            cands += sorted(glob.glob(os.path.join(base, "blender*", "blender.exe")), reverse=True)
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    cands += sorted(glob.glob(os.path.join(pf, "Blender Foundation", "*", "blender.exe")), reverse=True)
    return next((c for c in cands if os.path.isfile(c)), None)


def repo_file(*parts):
    """Chemin dans le depot (modele de la i20...), ou '' hors depot."""
    return os.path.join(REPO, *parts) if REPO else ""
