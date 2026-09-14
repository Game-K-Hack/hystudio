"""Emplacements de HyStudio, lance depuis les sources ou compile en .exe (PyInstaller).

  RESOURCES  fichiers livres avec le logiciel, en lecture seule (script Blender,
             visionneuse i20view.exe) : dossier des sources, ou _internal de l'exe
  APP_DIR    dossier du logiciel : sources, ou dossier contenant HyStudio.exe
  CACHE      donnees recalculables (geometrie, textures glTF, rendus en cours) :
             cache/ des sources, ou %LOCALAPPDATA%\\HyStudio\\cache pour l'exe
  USER_HOME  dossier de l'utilisateur, Documents\\HyStudio pour l'exe
  PROJECTS   projets de l'utilisateur : Documents\\HyStudio\\projets pour l'exe

Pour l'exe installe, rien de l'utilisateur ne vit dans le dossier du logiciel :
une mise a jour remplace ce dossier sans toucher aux projets, modeles et cache.

Version portable (fichier portable.txt a cote de HyStudio.exe) : tout reste dans
le dossier du logiciel, projets, cache et reglages (HyStudio.ini), rien dans
Documents, AppData ni le registre.
  REPO       depot hyundev s'il entoure le logiciel (Blender portable dans tools/,
             modele de la i20 dans interface/), sinon None
"""
import glob, os, sys

FROZEN = bool(getattr(sys, "frozen", False))
SOURCES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES = getattr(sys, "_MEIPASS", SOURCES)
APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if FROZEN else SOURCES
PORTABLE = FROZEN and os.path.isfile(os.path.join(APP_DIR, "portable.txt"))


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


REPO = _find_repo()

def _documents():
    """Dossier Documents reel (redirige vers OneDrive chez certains utilisateurs)."""
    if os.name == "nt":
        import ctypes, uuid
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [("d1", wintypes.DWORD), ("d2", wintypes.WORD), ("d3", wintypes.WORD), ("d4", ctypes.c_ubyte * 8)]
        u = uuid.UUID("FDD39AD0-238F-46AF-ADB4-6C85480369C7")                  # FOLDERID_Documents
        g = GUID(u.fields[0], u.fields[1], u.fields[2], (ctypes.c_ubyte * 8)(*u.bytes[8:]))
        out = ctypes.c_wchar_p()
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(g), 0, None, ctypes.byref(out)) == 0:
            path = out.value
            ctypes.windll.ole32.CoTaskMemFree(out)
            if path:
                return path
    return os.path.join(os.path.expanduser("~"), "Documents")


if PORTABLE:
    CACHE = os.path.join(APP_DIR, "cache")
    USER_HOME = APP_DIR
    PROJECTS = os.path.join(APP_DIR, "projets")
elif FROZEN:
    CACHE = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "HyStudio", "cache")
    USER_HOME = os.path.join(_documents(), "HyStudio")
    # projets/ d'une ancienne version en archive (a cote de l'exe), ceux des sources pour un exe
    # compile dans le depot, sinon Documents\HyStudio\projets
    candidates = [os.path.join(APP_DIR, "projets")]
    if REPO:
        candidates.append(os.path.join(REPO, "hystudio", "projets"))
    PROJECTS = next((c for c in candidates if os.path.isdir(c)), os.path.join(USER_HOME, "projets"))
else:
    CACHE = os.path.join(SOURCES, "cache")
    USER_HOME = REPO or SOURCES
    PROJECTS = os.path.join(SOURCES, "projets")

WORK = os.path.join(CACHE, "travail")
RENDERER = os.path.join(RESOURCES, "blender", "render_project.py")


def settings():
    """Reglages (langue, version ignoree) : registre, ou HyStudio.ini pour la version portable."""
    from PySide6.QtCore import QSettings
    if PORTABLE:
        return QSettings(os.path.join(APP_DIR, "HyStudio.ini"), QSettings.IniFormat)
    return QSettings("HyStudio", "HyStudio")


def summary():
    """Emplacements utilises, pour le diagnostic (--diagnostic)."""
    return {"frozen": FROZEN, "portable": PORTABLE, "app_dir": APP_DIR, "resources": RESOURCES,
            "projects": PROJECTS, "cache": CACHE, "user_home": USER_HOME, "repo": REPO,
            "blender": find_blender(), "viewer": viewer_exe()}


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
    for base in (APP_DIR, REPO, USER_HOME):
        if base:
            cands += sorted(glob.glob(os.path.join(base, "tools", "blender*", "blender.exe")), reverse=True)
            cands += sorted(glob.glob(os.path.join(base, "blender*", "blender.exe")), reverse=True)
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    cands += sorted(glob.glob(os.path.join(pf, "Blender Foundation", "*", "blender.exe")), reverse=True)
    return next((c for c in cands if os.path.isfile(c)), None)


def repo_file(*parts):
    """Chemin dans le depot (modele de la i20...), ou '' hors depot."""
    return os.path.join(REPO, *parts) if REPO else ""
