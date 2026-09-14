"""HyStudio : personnaliser un modele 3D de voiture et produire ses vues pour l'autoradio.

    python hystudio/hystudio.py
    python hystudio/hystudio.py --capture ecran.png     # capture de controle, puis quitte

Point d'entree de l'exe (build_exe.py).
"""
import os, sys

if not getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QTimer                      # noqa: E402
from PySide6.QtGui import QIcon                        # noqa: E402
from PySide6.QtWidgets import QApplication             # noqa: E402

from ui.viewport import set_default_format            # noqa: E402


def main():
    if "--diagnostic" in sys.argv:                     # emplacements utilises, sans interface
        import json
        from core import paths
        out = sys.argv[sys.argv.index("--diagnostic") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump(paths.summary(), f, indent=2, ensure_ascii=False)
        return 0
    set_default_format()                               # OpenGL 3.3 avant toute fenetre
    if os.name == "nt":
        # identite propre dans la barre des taches : sinon Windows y montre l'icone de python.exe
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("HyStudio")
    app = QApplication(sys.argv)
    app.setApplicationName("HyStudio")
    from core import paths
    app.setWindowIcon(QIcon(os.path.join(paths.RESOURCES, "ui", "hystudio.png")))
    app.setStyle("Fusion")
    # Sous le theme sombre de Windows, Fusion dessine un point dans les boutons
    # radio NON coches : on ne distinguait plus le choix actif.
    app.setStyleSheet("""
        QRadioButton::indicator { width: 11px; height: 11px; border-radius: 7px;
                                  border: 2px solid #8A93A0; background: transparent; }
        QRadioButton::indicator:checked { background: #3D8FD6; border-color: #3D8FD6; }
    """)
    from core import i18n
    i18n.init()                                        # choix enregistre, sinon langue du systeme
    from ui.mainwindow import MainWindow, _WINDOWS
    win = MainWindow()
    _WINDOWS.append(win)
    win.show()

    if "--capture" in sys.argv:
        out = sys.argv[sys.argv.index("--capture") + 1]

        def snap():
            if win.model is None:                      # modele encore en chargement
                QTimer.singleShot(500, snap); return
            part = win.model.part("desirefx_me_207")
            if part:
                win.on_part_clicked(part.name, False)
            if "--apercu" in sys.argv:                 # controle de l'exe : Blender lance depuis l'application
                QTimer.singleShot(1500, preview)
            else:
                QTimer.singleShot(1500, lambda: (win.grab().save(out), app.quit()))

        def preview():
            win.grab().save(out)
            win.prev_samples.setCurrentIndex(0)
            win.run_preview()

            def wait():
                if win.preview_worker is not None:
                    QTimer.singleShot(500, wait); return
                pm = win.prev_label.pixmap()
                if pm is not None and not pm.isNull():
                    pm.save(os.path.splitext(out)[0] + "_apercu.png")
                win.dirty = False
                app.quit()
            QTimer.singleShot(500, wait)
        QTimer.singleShot(1000, snap)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
