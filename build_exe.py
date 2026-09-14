"""Compile HyStudio en application Windows puis en installateur.

    python hystudio/build_exe.py

  1. PyInstaller : dossier dist\\HyStudio (HyStudio.exe + _internal), mode dossier
     plutot que fichier unique : demarrage immediat, sans decompresser Qt a chaque
     lancement.
  2. Inno Setup 6 : dist\\HyStudio-<version>-Setup.exe, installe tous les dossiers ;
     c'est le fichier a joindre a la release GitHub (la mise a jour integree
     cherche un fichier « ...Setup.exe »).

Blender n'est pas inclus (trop lourd) : HyStudio le cherche dans tools\\ du depot,
dans un dossier blender* a cote de l'exe ou dans Documents\\HyStudio, ou dans
Program Files. Les fichiers .spec et build\\ sont des produits intermediaires.
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BUILD = os.path.join(HERE, "build")
DIST = os.path.join(HERE, "dist")

# modules Qt et Python jamais utilises : exe plus leger
EXCLUDES = [
    "tkinter", "unittest", "pydoc", "doctest", "pdb", "xmlrpc", "lib2to3",
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets",
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebChannel",
    "PySide6.QtMultimedia", "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtPdf",
    "PySide6.QtSql", "PySide6.QtTest", "PySide6.QtSvg", "PySide6.QtXml", "PySide6.Qt3DCore",
    "PySide6.QtBluetooth", "PySide6.QtPositioning", "PySide6.QtSerialPort", "PySide6.QtDBus",
    "PIL.ImageQt", "PIL.ImageTk", "numpy.f2py", "numpy.distutils",
]


LOGO = os.path.join(HERE, "ui", "hystudio.png")        # logo du logiciel : fenetre, barre des taches, exe


def draw_logo(path=LOGO):
    """Pastille bleue « Hy », 256 px (regenere le PNG livre avec le logiciel)."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, 248, 248), 56, fill=(27, 94, 170, 255))
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 128)
    except OSError:
        font = ImageFont.load_default()
    d.text((128, 132), "Hy", font=font, fill=(255, 255, 255, 255), anchor="mm")
    im.save(path)


def icon(path):
    """Icone de l'exe, tiree du logo."""
    from PIL import Image
    if not os.path.isfile(LOGO):
        draw_logo()
    Image.open(LOGO).save(path, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def version_file(path):
    """Ressource de version Windows (Proprietes > Details de HyStudio.exe)."""
    sys.path.insert(0, HERE)
    from core.version import VERSION
    nums = tuple(int(x) for x in VERSION.split(".")) + (0,) * (4 - len(VERSION.split(".")))
    text = f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}, mask=0x3f, flags=0x0, OS=0x40004,
                    fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040C04B0', [
      StringStruct('CompanyName', 'Game-K-Hack'),
      StringStruct('FileDescription', 'HyStudio'),
      StringStruct('FileVersion', '{VERSION}'),
      StringStruct('InternalName', 'HyStudio'),
      StringStruct('OriginalFilename', 'HyStudio.exe'),
      StringStruct('ProductName', 'HyStudio'),
      StringStruct('ProductVersion', '{VERSION}')])]),
    VarFileInfo([VarStruct('Translation', [1036, 1200])])
  ]
)
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return VERSION


def main():
    import PyInstaller.__main__
    os.makedirs(BUILD, exist_ok=True)
    ico = os.path.join(BUILD, "hystudio.ico")
    icon(ico)
    vfile = os.path.join(BUILD, "version.txt")
    version = version_file(vfile)
    sep = os.pathsep
    args = [
        os.path.join(HERE, "hystudio.py"),
        "--name", "HyStudio", "--onedir", "--windowed", "--noconfirm", "--clean",
        "--icon", ico, "--version-file", vfile,
        "--distpath", DIST, "--workpath", BUILD, "--specpath", BUILD,
        "--paths", HERE,
        "--add-data", f"{os.path.join(HERE, 'blender', 'render_project.py')}{sep}blender",
        "--add-data", f"{LOGO}{sep}ui",
        # PyOpenGL choisit sa plateforme et ses formats de tableaux a l'execution
        "--collect-submodules", "OpenGL.platform",
        "--collect-submodules", "OpenGL.arrays",
    ]
    viewer = os.path.join(REPO, "i20view", "bin", "i20view.exe")
    if os.path.isfile(viewer):                         # visionneuse copiee sur la carte SD
        args += ["--add-data", f"{viewer}{sep}i20view"]
    for m in EXCLUDES:
        args += ["--exclude-module", m]
    PyInstaller.__main__.run(args)
    exe = os.path.join(DIST, "HyStudio", "HyStudio.exe")
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(os.path.dirname(exe)) for f in fs)
    print(f"\nHyStudio.exe : {exe}\ntaille du dossier : {size / 1e6:.0f} Mo")
    setup = build_installer(version, ico)
    print(f"installateur : {setup} ({os.path.getsize(setup) / 1e6:.0f} Mo)")
    portable = build_portable(version)
    print(f"portable : {portable} ({os.path.getsize(portable) / 1e6:.0f} Mo)")


PORTABLE_NOTE = """HyStudio portable

Ce fichier active le mode portable : projets, cache et reglages restent dans ce
dossier (projets, cache, HyStudio.ini). Rien n'est ecrit dans Documents, AppData
ni le registre. Supprimez-le pour utiliser les emplacements de l'installateur.

Mise a jour : extrayez la nouvelle archive par-dessus ce dossier ; les dossiers
projets et cache sont conserves.

This file enables portable mode: projects, cache and settings stay in this folder.
To update, extract the new archive over this folder; projects and cache are kept.
"""


def build_portable(version):
    """Archive portable : dist\\HyStudio + portable.txt, sans modifier le dossier de l'installateur."""
    import zipfile
    src = os.path.join(DIST, "HyStudio")
    out = os.path.join(DIST, f"HyStudio-{version}-Portable.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for base, _, files in os.walk(src):
            for f in files:
                full = os.path.join(base, f)
                z.write(full, os.path.join("HyStudio", os.path.relpath(full, src)))
        z.writestr("HyStudio/portable.txt", PORTABLE_NOTE)
    return out


def find_iscc():
    import glob
    cands = [shutil.which("ISCC")] + [os.path.join(os.environ.get(v, ""), "Inno Setup 6", "ISCC.exe")
                                      for v in ("ProgramFiles(x86)", "ProgramFiles")]
    cands += glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"))
    return next((c for c in cands if c and os.path.isfile(c)), None)


def build_installer(version, ico):
    """Installateur Inno Setup a partir de dist\\HyStudio."""
    import subprocess
    iscc = find_iscc()
    if not iscc:
        raise SystemExit("Inno Setup 6 introuvable (ISCC.exe) : installez-le pour produire l'installateur.")
    subprocess.run([iscc, "/Q", f"/DAppVersion={version}", f"/DSourceDir={os.path.join(DIST, 'HyStudio')}",
                    f"/DOutputDir={DIST}", f"/DIconFile={ico}", os.path.join(HERE, "installer", "hystudio.iss")],
                   check=True)
    return os.path.join(DIST, f"HyStudio-{version}-Setup.exe")


if __name__ == "__main__":
    sys.exit(main())
