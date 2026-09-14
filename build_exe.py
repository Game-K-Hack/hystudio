"""Compile HyStudio en application Windows (PyInstaller, dossier dist\\HyStudio).

    python hystudio/build_exe.py

Mode dossier (onedir) plutot que fichier unique : demarrage immediat, sans
decompresser ~200 Mo de Qt a chaque lancement. Le dossier dist\\HyStudio se
copie tel quel ; Blender n'est pas inclus (trop lourd) : HyStudio le cherche
dans tools\\ du depot, dans un dossier blender* a cote de l'exe, ou dans
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


def main():
    import PyInstaller.__main__
    os.makedirs(BUILD, exist_ok=True)
    ico = os.path.join(BUILD, "hystudio.ico")
    icon(ico)
    sep = os.pathsep
    args = [
        os.path.join(HERE, "hystudio.py"),
        "--name", "HyStudio", "--onedir", "--windowed", "--noconfirm", "--clean",
        "--icon", ico,
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


if __name__ == "__main__":
    sys.exit(main())
