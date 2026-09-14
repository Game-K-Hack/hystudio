"""Fenetre principale de HyStudio."""
import copy, datetime, os, time, traceback

import numpy as np
from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QButtonGroup, QColorDialog, QComboBox, QDockWidget, QDoubleSpinBox, QFileDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPlainTextEdit, QProgressBar, QPushButton, QRadioButton, QSpinBox, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from core import device, gltfmodel, i18n, mtl, objmodel, paths, pipeline, presets, project as projmod, updater
from core.i18n import tr, tr_label
from core.version import REPO_URL, VERSION
from ui.viewport import Viewport

PROJECTS = paths.PROJECTS
HOME = paths.USER_HOME                                   # dossier de depart des boites « Ouvrir »
# les anciens projets (.hyproj, .carproj de Car Studio) restent ouvrables
PROJECT_EXTS = "(*.hysp *.hyproj *.carproj)"
PRECISIONS = [(2, 180), (1, 360), (0.5, 720)]            # (degres par vue, nombre de vues)
_WINDOWS = []                  # garde la fenetre recreee au changement de langue
SEC_PER_VIEW_96 = 2.9          # mesure sur RTX 3080, 1600x848, 96 echantillons
KB_PER_VIEW = 102


# ===================================================================== fils

class Worker(QObject):
    progress = Signal(object)
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        self.cancelled = False

    def run(self):
        try:
            self.done.emit(self.fn(self))
        except pipeline.Cancelled:
            self.failed.emit(tr("Interrompu."))
        except Exception as e:                       # message lisible, trace au journal
            self.failed.emit(f"{e}\n\n{traceback.format_exc(limit=4)}")


class Relay(QObject):
    """Vit dans le fil de l'interface : une fonction Python simple connectee
    directement a un signal du travailleur s'executerait dans son fil a lui,
    et toucherait alors les widgets et le contexte OpenGL depuis le mauvais fil."""

    def __init__(self, parent, fn):
        super().__init__(parent)
        self.fn = fn

    @Slot(object)
    def call(self, value):
        self.fn(value)


def run_async(owner, fn, on_done, on_fail, on_progress=None):
    th = QThread(owner)
    w = Worker(fn)
    w.moveToThread(th)
    th.started.connect(w.run)
    relays = [Relay(owner, f) for f in (on_done, on_fail, on_progress or (lambda v: None))]
    w.done.connect(relays[0].call, Qt.QueuedConnection)
    w.failed.connect(relays[1].call, Qt.QueuedConnection)
    w.progress.connect(relays[2].call, Qt.QueuedConnection)
    for r in relays:
        th.finished.connect(r.deleteLater)
    for sig in (w.done, w.failed):
        sig.connect(th.quit)
    th.finished.connect(w.deleteLater)
    th.finished.connect(th.deleteLater)
    owner._threads.append((th, w))
    th.start()
    return w


def project_filter():
    return f"{tr('Projets HyStudio')} {PROJECT_EXTS}"


def rgb_to_pixmap(rgb):
    h, w, _ = rgb.shape
    img = QImage(np.ascontiguousarray(rgb).data, w, h, 3 * w, QImage.Format_RGB888)
    return QPixmap.fromImage(img.copy())


# ===================================================================== historique

class History:
    """Ctrl+Z / Ctrl+Y sur l'etat du projet (matieres, noms, studio).

    Un cliche est pris AVANT chaque modification. Des changements successifs
    du meme reglage (flèches d'un champ, glissement) a moins de 1,5 s
    d'intervalle ne forment qu'une seule etape d'annulation."""
    LIMIT = 300

    def __init__(self):
        self.clear()

    def clear(self):
        self.undo_stack, self.redo_stack = [], []
        self._last_tag, self._last_time = None, 0.0

    @staticmethod
    def snapshot(project):
        return copy.deepcopy({"materials": project.materials, "parts": project.parts,
                              "labels": project.labels, "studio": project.studio})

    @staticmethod
    def restore(project, snap):
        snap = copy.deepcopy(snap)
        project.materials, project.parts = snap["materials"], snap["parts"]
        project.labels, project.studio = snap["labels"], snap["studio"]

    def checkpoint(self, project, tag=None):
        now = time.monotonic()
        if tag is not None and tag == self._last_tag and now - self._last_time < 1.5:
            self._last_time = now
            return
        self.undo_stack.append(self.snapshot(project))
        del self.undo_stack[:-self.LIMIT]
        self.redo_stack.clear()
        self._last_tag, self._last_time = tag, now

    def undo(self, project):
        if not self.undo_stack:
            return False
        self.redo_stack.append(self.snapshot(project))
        self.restore(project, self.undo_stack.pop())
        self._last_tag = None
        return True

    def redo(self, project):
        if not self.redo_stack:
            return False
        self.undo_stack.append(self.snapshot(project))
        self.restore(project, self.redo_stack.pop())
        self._last_tag = None
        return True


# ===================================================================== matiere

class MaterialPanel(QWidget):
    """Edite la matiere de la selection : une piece, ou tout un materiau d'origine."""
    changed = Signal()

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.target = None                 # ("part", nom) ou ("material", nom)
        lay = QVBoxLayout(self)

        self.title = QLabel(tr("Cliquez une pièce dans la vue 3D ou dans la liste."))
        self.title.setWordWrap(True)
        self.title.setStyleSheet("font-weight: 600; font-size: 14px;")
        lay.addWidget(self.title)

        self.scope_box = QGroupBox(tr("Appliquer à"))
        sl = QVBoxLayout(self.scope_box)
        self.r_part = QRadioButton(tr("Cette pièce seulement"))
        self.r_mat = QRadioButton(tr("Toutes les pièces de ce matériau"))
        self.scope = QButtonGroup(self)
        for r in (self.r_part, self.r_mat):
            self.scope.addButton(r); sl.addWidget(r)
        self.r_part.setChecked(True)
        self.scope.buttonToggled.connect(lambda *_: self._load())
        lay.addWidget(self.scope_box)

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("nom affiché dans la liste"))
        self.name_edit.editingFinished.connect(self._rename)
        form.addRow(tr("Nom"), self.name_edit)
        self.kind = QComboBox()
        self.set_allowed_kinds(list(presets.KINDS))
        self.kind.activated.connect(self._kind_changed)
        form.addRow(tr("Matière"), self.kind)
        lay.addLayout(form)

        self.fields_box = QWidget()
        self.fields = QFormLayout(self.fields_box)
        lay.addWidget(self.fields_box)

        self.reset_btn = QPushButton(tr("Rétablir la matière du matériau d'origine"))
        self.reset_btn.clicked.connect(self._reset)
        lay.addWidget(self.reset_btn)
        lay.addStretch(1)
        self.set_target(None)

    # ------------------------------------------------------------
    def set_allowed_kinds(self, kinds):
        """Types proposes : sans 'image' pour un modele non decoupe, ou une image
        serait projetee sur la voiture entiere."""
        self.kind.blockSignals(True)
        self.kind.clear()
        for k in kinds:
            self.kind.addItem(tr(presets.KINDS[k]["label"]), k)
        self.kind.blockSignals(False)

    def reload(self):
        """Relit la selection courante (apres Ctrl+Z / Ctrl+Y)."""
        if self.part_name and self.win.model.part(self.part_name) is None:
            self.set_target(None)
        elif self.part_name or self.material:
            self._load()

    def set_target(self, part_name, material=None):
        """part_name : piece selectionnee (ou None) ; material : materiau choisi dans la liste."""
        self.part_name, self.material = part_name, material
        enabled = bool(part_name or material)
        for w in (self.scope_box, self.name_edit, self.kind, self.fields_box, self.reset_btn):
            w.setEnabled(enabled)
        self.scope_box.setVisible(bool(part_name))
        if not enabled:
            self.title.setText(tr("Cliquez une pièce dans la vue 3D ou dans la liste."))
            self._clear_fields()
            return
        if part_name:
            part = self.win.model.part(part_name)
            self.material = part.material
            self.r_part.blockSignals(True); self.r_mat.blockSignals(True)
            self.r_part.setChecked(True)                   # on modifie d'abord la piece cliquee
            self.r_part.blockSignals(False); self.r_mat.blockSignals(False)
        self._load()

    def _key(self):
        if self.part_name and self.r_part.isChecked():
            return "part", self.part_name
        return "material", self.material

    def _spec(self):
        kind, key = self._key()
        p = self.win.project
        if kind == "part":
            part = self.win.model.part(key)
            return p.spec_for(key, part.material)
        return presets.complete(p.materials.get(key, presets.default_spec("plastique")))

    def _store(self, spec):
        kind, key = self._key()
        p = self.win.project
        (p.parts if kind == "part" else p.materials)[key] = spec
        self.win.mark_dirty()
        self.changed.emit()

    def _load(self):
        if not (self.part_name or self.material):
            return
        kind, key = self._key()
        p = self.win.project
        mat_label = tr_label(p.label(self.material))
        n = sum(1 for x in self.win.model.parts if x.material == self.material)
        if kind == "part":
            name = tr_label(p.label(key))
            self.title.setText(tr("Pièce : {name} (matière propre)", name=name) if key in p.parts
                               else tr("Pièce : {name} (hérite de « {mat} »)", name=name, mat=mat_label))
            self.r_mat.setText(tr("Toutes les pièces « {mat} » ({n})", mat=mat_label, n=n))
        elif self.win.model.separated:
            self.title.setText(tr("Matériau : {mat} — {n} pièce(s)", mat=mat_label, n=n))
        else:
            self.title.setText(tr("Matériau : {mat}", mat=mat_label))
        self.name_edit.setText(tr_label(p.labels.get(key, "")))
        self.reset_btn.setVisible(kind == "part" and key in p.parts)
        spec = self._spec()
        i = self.kind.findData(spec["kind"])
        if i < 0:                                   # type non propose ici (image d'un ancien projet)
            self.kind.addItem(tr(presets.KINDS[spec["kind"]]["label"]), spec["kind"])
            i = self.kind.count() - 1
        self.kind.setCurrentIndex(i)
        self._build_fields(spec)

    def _clear_fields(self):
        while self.fields.rowCount():
            self.fields.removeRow(0)

    def _build_fields(self, spec):
        self._clear_fields()
        for key, label, typ, _ in presets.KINDS[spec["kind"]]["fields"]:
            val = spec.get(key)
            if typ == "color":
                w = QPushButton(val)
                w.setStyleSheet(f"background:{val}; color:{'#000' if QColor(val).lightness() > 128 else '#fff'};")
                w.clicked.connect(lambda _=False, k=key, b=w: self._pick_color(k, b))
            elif typ == "file":
                w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(0, 0, 0, 0)
                ed = QLineEdit(val); ed.setReadOnly(True)
                bt = QPushButton(tr("Choisir…"))
                bt.clicked.connect(lambda _=False, k=key, e=ed: self._pick_file(k, e))
                hl.addWidget(ed, 1); hl.addWidget(bt)
            elif isinstance(typ, tuple) and isinstance(typ[0], str):
                w = QComboBox()
                for opt in typ:
                    w.addItem(tr(opt.replace("satine", "satiné")), opt)
                w.setCurrentIndex(max(0, w.findData(val)))
                w.activated.connect(lambda _i, k=key, c=w: self._set(k, c.currentData()))
            else:
                lo, hi = typ
                w = QDoubleSpinBox(); w.setRange(lo, hi); w.setDecimals(2)
                w.setSingleStep((hi - lo) / 50); w.setValue(float(val))
                w.valueChanged.connect(lambda v, k=key: self._set(k, round(v, 3)))
            self.fields.addRow(tr(label), w)
        if spec["kind"] == "image":
            self.fields.addRow(self._hint(tr("IMAGE_AIDE")))
        if spec["kind"] == "origine":
            self.fields.addRow(self._hint(tr("ORIGINE_AIDE")))
        if spec["kind"] in presets.DECAL_KINDS:
            self._build_decal(spec)

    # ------------------------------------------------------------ autocollant
    @staticmethod
    def _hint(text):
        lb = QLabel(text); lb.setWordWrap(True)
        lb.setStyleSheet("color: #9AA3AE;")
        return lb

    def _build_decal(self, spec):
        """Image posee par-dessus la matiere : fichier, orientation, taille, position, rotation."""
        head = QLabel(tr("Autocollant"))
        head.setStyleSheet("font-weight: 600; margin-top: 10px;")
        self.fields.addRow(head)
        decal = spec.get("decal") or {}
        if not decal.get("image"):
            self.fields.addRow(self._hint(tr("AUTOCOLLANT_AIDE")))
            add = QPushButton(tr("Poser une image…"))
            add.clicked.connect(self._decal_pick)
            self.fields.addRow(add)
            return
        d = {**presets.default_decal(), **decal}
        w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(0, 0, 0, 0)
        ed = QLineEdit(d["image"]); ed.setReadOnly(True)
        pick = QPushButton(tr("Choisir…")); pick.clicked.connect(self._decal_pick)
        rem = QPushButton(tr("Retirer")); rem.clicked.connect(self._decal_remove)
        hl.addWidget(ed, 1); hl.addWidget(pick); hl.addWidget(rem)
        self.fields.addRow(tr("Fichier image"), w)
        orient = QPushButton(tr("Orienter depuis la vue actuelle"))
        orient.setToolTip(tr("AUTOCOLLANT_AIDE"))
        orient.clicked.connect(lambda: self._decal_set("dir", self.win.viewport.view_direction()))
        self.fields.addRow(orient)
        for key, label, lo, hi, scale, suffix in (("size", "Taille", 1, 300, 100, " %"),
                                                  ("x", "Horizontal", -150, 150, 100, " %"),
                                                  ("y", "Vertical", -150, 150, 100, " %"),
                                                  ("rot", "Rotation", -180, 180, 1, " °")):
            sb = QDoubleSpinBox(); sb.setRange(lo, hi); sb.setDecimals(0 if scale == 1 else 1)
            sb.setSingleStep(1 if scale == 1 else 2); sb.setSuffix(suffix)
            sb.setValue(d[key] * scale)
            sb.valueChanged.connect(lambda v, k=key, sc=scale: self._decal_set(k, round(v / sc, 4)))
            self.fields.addRow(tr(label), sb)

    def _decal_set(self, key, value, tag=True):
        spec = self._spec()
        decal = {**presets.default_decal(), **(spec.get("decal") or {})}
        if decal.get(key) == value:
            return
        self.win.checkpoint(("autocollant", self._key(), key) if tag else None)
        decal[key] = value
        spec["decal"] = decal
        self._store(spec)

    def _decal_pick(self):
        spec = self._spec()
        cur = (spec.get("decal") or {}).get("image", "")
        f, _ = QFileDialog.getOpenFileName(self, tr("Fichier image"), os.path.dirname(cur) if cur else HOME,
                                           tr("Images") + " (*.png *.jpg *.jpeg *.bmp)")
        if not f:
            return
        self.win.checkpoint()
        decal = spec.get("decal") or presets.default_decal(self.win.viewport.view_direction())
        decal["image"] = f
        spec["decal"] = decal
        self._store(spec)
        self._build_fields(spec)

    def _decal_remove(self):
        spec = self._spec()
        if "decal" in spec:
            self.win.checkpoint()
            del spec["decal"]
            self._store(spec)
            self._build_fields(spec)

    def _set(self, key, value):
        spec = self._spec()
        if spec.get(key) == value:
            return
        self.win.checkpoint(("champ", self._key(), key))
        spec[key] = value
        self._store(spec)

    def _pick_color(self, key, button):
        c = QColorDialog.getColor(QColor(button.text()), self, tr("Couleur"))
        if c.isValid():
            h = c.name().upper()
            button.setText(h)
            button.setStyleSheet(f"background:{h}; color:{'#000' if c.lightness() > 128 else '#fff'};")
            self._set(key, h)

    def _pick_file(self, key, edit):
        f, _ = QFileDialog.getOpenFileName(self, tr("Fichier image"), os.path.dirname(edit.text()) if edit.text() else HOME,
                                           tr("Images") + " (*.png *.jpg *.jpeg *.bmp)")
        if f:
            edit.setText(f)
            self._set(key, f)

    def _kind_changed(self):
        new = self.kind.currentData()
        old = self._spec()
        if old["kind"] == new:
            return
        self.win.checkpoint()
        spec = presets.default_spec(new)
        if "color" in spec and "color" in old:
            spec["color"] = old["color"]
        if new in presets.DECAL_KINDS and old.get("decal"):
            spec["decal"] = old["decal"]              # l'autocollant survit au changement de matiere
        self._store(spec)
        self._build_fields(spec)

    def _reset(self):
        if self.part_name in self.win.project.parts:
            self.win.checkpoint()
            del self.win.project.parts[self.part_name]
            self.win.mark_dirty()
            self.r_mat.setChecked(True)
            self.changed.emit()
            self._load()

    def _rename(self):
        kind, key = self._key()
        txt = self.name_edit.text().strip()
        labels = self.win.project.labels
        if txt == tr_label(labels.get(key, "")):     # nom affiche (traduit) inchange
            return
        if txt and labels.get(key) != txt:
            self.win.checkpoint()
            labels[key] = txt
        elif not txt and key in labels:
            self.win.checkpoint()
            del labels[key]
        else:
            return
        self.win.mark_dirty()
        self.win.fill_tree()


# ===================================================================== fenetre

class MainWindow(QMainWindow):
    def __init__(self, state=None, open_path=None):
        super().__init__()
        self.setAcceptDrops(True)                  # projet ou modele glisse sur la fenetre
        self._threads = []
        self.sd_busy = False
        self._swapping = False
        self.project = None
        self.model = None
        self.dirty = False
        self.preview_worker = None
        self.gen_worker = None
        self.history = History()
        self.resize(1500, 920)

        # ---- centre : vue 3D et apercu
        self.tabs = QTabWidget()
        self.viewport = Viewport()
        self.viewport.picked.connect(self.on_picked)
        self.tabs.addTab(self.viewport, tr("Vue 3D"))
        self.tabs.addTab(self._build_preview_tab(), tr("Aperçu réaliste"))
        self.setCentralWidget(self.tabs)

        # ---- gauche : pieces
        left = QWidget(); ll = QVBoxLayout(left)
        self.filter = QLineEdit(); self.filter.setPlaceholderText(tr("Filtrer les pièces…"))
        self.filter.textChanged.connect(self.apply_filter)
        self.tree = QTreeWidget(); self.tree.setHeaderLabels([tr("Pièce"), tr("Triangles")])
        self.tree.setColumnWidth(0, 225)
        self.tree.header().setStretchLastSection(True)
        self.tree.itemSelectionChanged.connect(self.on_tree_selection)
        ll.addWidget(self.filter); ll.addWidget(self.tree)
        self._dock("pieces", tr("Pièces"), left, Qt.LeftDockWidgetArea)

        # ---- droite : matiere et studio
        self.material_panel = MaterialPanel(self)
        self.material_panel.changed.connect(self.viewport.refresh)
        self._dock("matiere", tr("Matière"), self.material_panel, Qt.RightDockWidgetArea)
        self._dock("studio", tr("Studio"), self._build_studio(), Qt.RightDockWidgetArea)

        # ---- bas : production
        self._dock("production", tr("Production"), self._build_production(), Qt.BottomDockWidgetArea)

        self._build_menu()
        self.statusBar().showMessage(tr("Prêt"))
        QTimer.singleShot(0, self._size_docks)      # apres affichage, sinon ignore
        if state:
            QTimer.singleShot(0, lambda: self._restore(state))
        else:
            if open_path:                          # double-clic sur un .hysp, ou fichier glisse sur l'exe
                QTimer.singleShot(0, lambda: self.open_file(open_path))
            else:
                QTimer.singleShot(0, self.open_startup_project)
            # verification discrete des mises a jour : exe, ou essai via HYSTUDIO_UPDATE_URL
            if updater.can_install() or os.environ.get("HYSTUDIO_UPDATE_URL"):
                QTimer.singleShot(3000, self.check_updates)

    # ------------------------------------------------------------ construction
    def _size_docks(self):
        docks = {d.objectName(): d for d in self.findChildren(QDockWidget)}
        self.resizeDocks([docks["production"]], [200], Qt.Vertical)
        self.resizeDocks([docks["pieces"], docks["matiere"]], [370, 390], Qt.Horizontal)
        self.resizeDocks([docks["matiere"], docks["studio"]], [430, 240], Qt.Vertical)

    def _dock(self, ident, title, widget, area):
        d = QDockWidget(title, self)
        d.setObjectName(ident)
        d.setWidget(widget)
        d.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(area, d)
        return d

    def _build_menu(self):
        m = self.menuBar().addMenu(tr("&Fichier"))
        for text, slot, key in (
                (tr("Nouveau projet depuis un modèle 3D…"), self.new_project, QKeySequence.New),
                (tr("Bibliothèque de voitures…"), self.open_library, QKeySequence("Ctrl+B")),
                (tr("Ouvrir un projet…"), self.open_project, QKeySequence.Open),
                (tr("Enregistrer"), self.save_project, QKeySequence.Save),
                (tr("Enregistrer sous…"), self.save_project_as, QKeySequence.SaveAs),
                (None, None, None),
                (tr("Importer les matériaux d'un fichier MTL…"), self.import_mtl, None),
                (None, None, None),
                (tr("Quitter"), self.close, QKeySequence.Quit)):
            if text is None:
                m.addSeparator(); continue
            a = QAction(text, self)
            if key:
                a.setShortcut(key)
            a.triggered.connect(slot)
            m.addAction(a)

        e = self.menuBar().addMenu(tr("&Édition"))
        self.undo_action = QAction(tr("Annuler"), self)
        self.undo_action.setShortcuts([QKeySequence.Undo])
        self.undo_action.triggered.connect(self.undo)
        self.redo_action = QAction(tr("Rétablir"), self)
        self.redo_action.setShortcuts([QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")])
        self.redo_action.triggered.connect(self.redo)
        for a in (self.undo_action, self.redo_action):
            a.setShortcutContext(Qt.ApplicationShortcut)
            e.addAction(a)
        self.update_history_actions()
        QApplication.instance().installEventFilter(self)

        lang = self.menuBar().addMenu(tr("&Langue"))
        group = QActionGroup(self)
        choice = i18n.saved_choice()
        for code, label in [(i18n.AUTO, tr("Automatique (langue du système)"))] + list(i18n.LANGS.items()):
            a = QAction(label, self, checkable=True)
            a.setChecked(code == choice)
            a.triggered.connect(lambda _=False, c=code: self.change_language(c))
            group.addAction(a)
            lang.addAction(a)
            if code == i18n.AUTO:
                lang.addSeparator()

        help_menu = self.menuBar().addMenu("&?")
        check = QAction(tr("Rechercher des mises à jour…"), self)
        check.triggered.connect(lambda: self.check_updates(quiet=False))
        help_menu.addAction(check)
        about = QAction(tr("À propos de HyStudio"), self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    # ------------------------------------------------------------ mises a jour
    def check_updates(self, quiet=True):
        """Derniere release GitHub, en arriere-plan. quiet : au demarrage, rien si a jour ou hors ligne."""
        def done(release):
            from PySide6.QtCore import QSettings
            if release is None:
                if not quiet:
                    online = getattr(self, "_update_reachable", True)
                    QMessageBox.information(self, tr("Mises à jour"),
                                            tr("HyStudio est à jour (version {v}).", v=VERSION) if online
                                            else tr("Impossible de vérifier les mises à jour : pas de connexion à GitHub."))
                return
            if quiet and QSettings("HyStudio", "HyStudio").value("maj/ignoree", "") == release.version:
                return
            self._offer_update(release)

        def job(w):
            self._update_reachable = True
            release = updater.check()
            if release is None and not quiet:
                import urllib.request
                try:
                    urllib.request.urlopen(updater.API, timeout=updater.TIMEOUT).close()
                except OSError:
                    self._update_reachable = False
            return release

        run_async(self, job, done, lambda e: None)

    def _offer_update(self, release):
        from PySide6.QtCore import QSettings
        box = QMessageBox(self)
        box.setWindowTitle(tr("Mise à jour disponible"))
        box.setIconPixmap(self.windowIcon().pixmap(64, 64))
        box.setText(f"<h3>HyStudio {release.version}</h3>")
        box.setInformativeText(tr("MAJ_DISPO", new=release.version, cur=VERSION))
        if release.notes:
            box.setDetailedText(release.notes)
        if updater.can_install():
            go = box.addButton(tr("Mettre à jour"), QMessageBox.AcceptRole)
        else:                                      # depuis les sources : pas d'installateur a lancer
            go = box.addButton(tr("Ouvrir la page de téléchargement"), QMessageBox.AcceptRole)
        box.addButton(tr("Plus tard"), QMessageBox.RejectRole)
        skip = box.addButton(tr("Ignorer cette version"), QMessageBox.DestructiveRole)
        box.setDefaultButton(go)
        box.exec()
        if box.clickedButton() is skip:
            QSettings("HyStudio", "HyStudio").setValue("maj/ignoree", release.version)
        elif box.clickedButton() is go:
            if updater.can_install():
                self._install_update(release)
            else:
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                QDesktopServices.openUrl(QUrl(release.page))

    def _install_update(self, release):
        if self.gen_worker or self.preview_worker or self.sd_busy:
            QMessageBox.information(self, tr("Mise à jour disponible"),
                                    tr("Terminez d'abord le calcul ou la copie en cours."))
            return
        if not self.confirm_discard():             # projet enregistre (ou abandonne) avant de fermer
            return
        from PySide6.QtWidgets import QProgressDialog
        dlg = QProgressDialog(tr("Téléchargement de la mise à jour…"), tr("Interrompre"), 0, 100, self)
        dlg.setWindowTitle(tr("Mise à jour disponible"))
        dlg.setMinimumDuration(0)
        dlg.setValue(0)
        worker = {}

        def job(w):
            return updater.download(release, progress=lambda f: w.progress.emit(int(f * 100)),
                                    cancelled=lambda: w.cancelled)

        def done(path):
            dlg.close()
            updater.launch_installer(path)
            self.dirty = False                     # deja confirme ci-dessus
            self.close()

        def fail(msg):
            dlg.close()
            if not msg.startswith(tr("Interrompu.")):
                QMessageBox.warning(self, tr("Mise à jour disponible"), msg.split("\n\n")[0])

        worker["w"] = run_async(self, job, done, fail, lambda v: dlg.setValue(v))
        dlg.canceled.connect(lambda: setattr(worker["w"], "cancelled", True))

    def show_about(self):
        box = QMessageBox(self)
        box.setWindowTitle(tr("À propos de HyStudio"))
        box.setIconPixmap(self.windowIcon().pixmap(72, 72))
        box.setTextFormat(Qt.RichText)
        box.setText(f"<h3>HyStudio {VERSION}</h3>"
                    f"<p>{tr('Personnalisez un modèle 3D de voiture et produisez sa rotation 360° pour l\'autoradio.')}</p>"
                    f"<p><a href='{REPO_URL}'>{REPO_URL.replace('https://', '')}</a></p>")
        box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        box.exec()

    def _build_preview_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        bar = QHBoxLayout()
        self.angle = QComboBox()
        for name, deg in pipeline.ANGLES.items():
            self.angle.addItem(tr(name), deg)
        self.prev_samples = QComboBox()
        for s in (32, 64, 96):
            self.prev_samples.addItem(tr("{n} échantillons", n=s), s)
        self.prev_samples.setCurrentIndex(1)
        self.prev_btn = QPushButton(tr("Calculer l'aperçu"))
        self.prev_btn.clicked.connect(self.run_preview)
        self.prev_info = QLabel(tr("Rendu Blender d'une vue, tel qu'il apparaîtra sur l'autoradio (800 × 424)."))
        for x in (QLabel(tr("Vue")), self.angle, self.prev_samples, self.prev_btn):
            bar.addWidget(x)
        bar.addWidget(self.prev_info, 1)
        lay.addLayout(bar)
        self.prev_label = QLabel()
        self.prev_label.setAlignment(Qt.AlignCenter)
        self.prev_label.setMinimumSize(800, 424)
        self.prev_label.setStyleSheet("background:#181C21;")
        lay.addWidget(self.prev_label, 1)
        return w

    def _build_studio(self):
        w = QWidget(); f = QFormLayout(w)
        self.s_exposure = QDoubleSpinBox(); self.s_exposure.setRange(-3, 2); self.s_exposure.setSingleStep(0.1)
        self.s_exposure.setSuffix(tr(" IL"))
        self.s_sharpen = QSpinBox(); self.s_sharpen.setRange(0, 300); self.s_sharpen.setSingleStep(10)
        self.s_sharpen.setSuffix(" %")
        self.s_views = QComboBox()
        for deg, n in PRECISIONS:
            self.s_views.addItem(tr("{deg}° — {n} vues", deg=i18n.number(deg, 0 if deg >= 1 else 1), n=n), n)
        self.s_samples = QComboBox()
        for s in (48, 64, 96, 128):
            self.s_samples.addItem(str(s), s)
        self.s_cabin = QSpinBox(); self.s_cabin.setRange(0, 400); self.s_cabin.setSingleStep(10)
        self.s_cabin.setSuffix(" W")
        f.addRow(tr("Exposition"), self.s_exposure)
        f.addRow(tr("Netteté"), self.s_sharpen)
        f.addRow(tr("Précision"), self.s_views)
        f.addRow(tr("Échantillons"), self.s_samples)
        f.addRow(tr("Lumière habitacle"), self.s_cabin)
        self.s_estimate = QLabel(); self.s_estimate.setWordWrap(True)
        f.addRow(self.s_estimate)
        self.s_exposure.valueChanged.connect(lambda v: self._studio("exposure", round(v, 2)))
        self.s_sharpen.valueChanged.connect(lambda v: self._studio("sharpen", v))
        self.s_views.activated.connect(lambda _: self._studio("views", self.s_views.currentData()))
        self.s_samples.activated.connect(lambda _: self._studio("samples", self.s_samples.currentData()))
        self.s_cabin.valueChanged.connect(lambda v: self._studio("cabin_light", float(v)))
        return w

    def _build_production(self):
        w = QWidget(); lay = QHBoxLayout(w)
        col = QVBoxLayout()
        self.gen_btn = QPushButton(tr("Générer pour l'autoradio"))
        self.gen_btn.setStyleSheet("font-weight:600; padding:8px;")
        self.gen_btn.clicked.connect(self.run_generate)
        self.cancel_btn = QPushButton(tr("Interrompre")); self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_jobs)
        self.sd_btn = QPushButton(tr("Copier sur la carte SD"))
        self.sd_btn.clicked.connect(self.copy_to_sd)
        for b in (self.gen_btn, self.cancel_btn, self.sd_btn):
            col.addWidget(b)
        col.addStretch(1)
        lay.addLayout(col)
        right = QVBoxLayout()
        self.progress = QProgressBar(); self.progress.setFormat("%v / %m")
        self.progress_label = QLabel(tr("Aucune génération en cours."))
        self.log = QPlainTextEdit(); self.log.setReadOnly(True); self.log.setMaximumBlockCount(2000)
        right.addWidget(self.progress); right.addWidget(self.progress_label); right.addWidget(self.log, 1)
        lay.addLayout(right, 1)
        return w

    # ------------------------------------------------------------ journal
    def say(self, msg):
        self.log.appendPlainText(f"[{datetime.datetime.now():%H:%M:%S}] {msg}")
        self.statusBar().showMessage(msg.splitlines()[0], 8000)

    # ------------------------------------------------------------ projet
    def open_startup_project(self):
        os.makedirs(PROJECTS, exist_ok=True)
        path = os.path.join(PROJECTS, "i20" + projmod.EXTENSION)
        old = next((os.path.join(PROJECTS, "i20" + e) for e in projmod.OLD_EXTENSIONS
                    if os.path.exists(os.path.join(PROJECTS, "i20" + e))), None)
        if os.path.exists(path):
            self.set_project(projmod.Project.load(path))
        elif old:                                  # ancien projet : copie au nouveau format, l'original reste
            p = projmod.Project.load(old)
            p.save(path)
            self.set_project(p)
            self.say(tr("Projet converti au format .hysp : {path}", path=path))
        elif not projmod.i20_available():          # pas de modele i20 : on attend un projet
            self.say(tr("Ouvrez un projet ou créez-en un depuis un modèle 3D (menu Fichier)."))
            from core import library
            if library.scan():                     # une bibliotheque existe : on la propose d'emblee
                QTimer.singleShot(300, self.open_library)
        else:
            p = projmod.i20_profile()
            p.save(path)
            self.set_project(p)
            self.say(tr("Profil i20 validé créé : {path}", path=path))

    def set_project(self, p):
        self.project = p
        self.dirty = False
        self.history.clear()
        self.update_history_actions()
        self._sync_studio()
        self.update_title()
        model_path = p.resolve(p.model)
        if not model_path or not os.path.exists(model_path):
            QMessageBox.warning(self, tr("Modèle introuvable"), tr("Le modèle du projet est introuvable :\n{path}", path=model_path))
            return
        self.say(tr("Chargement du modèle {name}…", name=os.path.basename(model_path)))
        self.setEnabled(False)
        run_async(self, lambda w: objmodel.load(model_path), self._model_loaded,
                  lambda e: (self.setEnabled(True), QMessageBox.critical(self, tr("Chargement"), e)))

    def _model_loaded(self, model, quiet=False):
        self.setEnabled(True)
        self.model = model
        kinds = list(presets.KINDS)
        if not model.separated:
            kinds.remove("image")
        if not model.source_materials:                # materiau d'origine : glTF seulement
            kinds.remove("origine")
        self.material_panel.set_allowed_kinds(kinds)
        self.viewport.set_model(model, self.project)
        self.fill_tree()
        self.material_panel.set_target(None)
        self.say(tr("{parts} pièces, {tris} triangles", parts=len(model.parts),
                    tris=f"{model.triangles:,}".replace(",", " ")))
        self.update_estimate()
        if not model.separated and not quiet:
            QMessageBox.information(
                self, tr("Modèle non découpé en pièces"),
                tr("NON_DECOUPE", name=os.path.basename(model.path)))

    # ------------------------------------------------------------ ouverture de fichiers
    PROJECT_SUFFIXES = (projmod.EXTENSION,) + projmod.OLD_EXTENSIONS
    MODEL_SUFFIXES = (".glb", ".gltf", ".obj")

    def open_file(self, path):
        """Projet (.hysp...) : ouverture ; modele 3D : nouveau projet. Double-clic, glisser-deposer, ligne de commande."""
        ext = os.path.splitext(path)[1].lower()
        if ext in self.PROJECT_SUFFIXES:
            if self.confirm_discard():
                self.open_project_file(path)
        elif ext in self.MODEL_SUFFIXES:
            self.new_project(path)
        else:
            QMessageBox.warning(self, tr("Ouverture"), tr("Format de fichier non pris en charge : {file}",
                                                          file=os.path.basename(path)))

    def open_project_file(self, path):
        try:
            self.set_project(projmod.Project.load(path))
        except Exception as e:
            QMessageBox.critical(self, tr("Ouverture"), str(e))

    def _dropped_file(self, event):
        urls = event.mimeData().urls() if event.mimeData().hasUrls() else []
        for u in urls:
            p = u.toLocalFile()
            if os.path.isfile(p) and os.path.splitext(p)[1].lower() in self.PROJECT_SUFFIXES + self.MODEL_SUFFIXES:
                return p
        return None

    def dragEnterEvent(self, event):
        if self._dropped_file(event):
            event.acceptProposedAction()

    def dropEvent(self, event):
        path = self._dropped_file(event)
        if path:
            event.acceptProposedAction()
            QTimer.singleShot(0, lambda: self.open_file(path))

    def open_library(self):
        from ui.librarydialog import LibraryDialog
        dlg = LibraryDialog(self)
        if dlg.exec() and dlg.chosen:
            self.new_project(dlg.chosen.model, dlg.chosen.name)

    def new_project(self, model_path=None, name=None):
        if not self.confirm_discard():
            return
        f = model_path
        if not f:
            f, _ = QFileDialog.getOpenFileName(self, tr("Modèle 3D"), HOME,
                                               tr("Modèles 3D") + " (*.obj *.gltf *.glb);;glTF (*.gltf *.glb);;OBJ (*.obj)")
        if not f:
            return
        p = projmod.Project()
        p.name = name or os.path.splitext(os.path.basename(f))[0]
        p.model = f
        # matieres de depart deduites des noms de materiaux courants
        m = objmodel.load(f)
        if m.source_materials:                       # glTF : materiaux du fichier, textures comprises
            for mat in m.materials():
                info = m.source_materials.get(mat)
                p.materials[mat] = (gltfmodel.default_spec(mat, info) if info
                                    else presets.default_spec(mtl.guess_kind(mat)))
            n = sum(1 for mat in m.materials() if p.materials[mat]["kind"] == "origine")
            self.say(tr("{n} matériau(x) texturé(s) gardé(s) tels quels (« Matériau d'origine »).", n=n))
        else:
            for mat in m.materials():
                p.materials[mat] = presets.default_spec(mtl.guess_kind(mat))
            self._offer_mtl(f, m, p)
        out, _ = QFileDialog.getSaveFileName(self, tr("Enregistrer le projet"),
                                             os.path.join(PROJECTS, p.name + projmod.EXTENSION),
                                             project_filter())
        if not out:
            return
        p.save(out)
        self.set_project(p)

    def _offer_mtl(self, obj_path, model, p):
        """Propose de reprendre le .mtl du modele comme matieres de depart."""
        path = mtl.find_for(obj_path)
        if not path:
            return
        name = os.path.basename(path)
        try:
            specs, _ = mtl.specs_for(path, model.materials())
        except OSError as e:
            self.say(str(e)); return
        if not specs:
            self.say(tr("« {file} » ignoré : il ne contient que les valeurs par défaut de l'exportateur.", file=name))
            return
        box = QMessageBox(QMessageBox.Question, tr("Fichier de matériaux"),
                          tr("MTL_QUESTION", file=name, n=len(specs), total=len(model.materials())), parent=self)
        use = box.addButton(tr("Utiliser le MTL"), QMessageBox.AcceptRole)
        box.addButton(tr("Ignorer"), QMessageBox.RejectRole)
        box.setDefaultButton(use)
        box.exec()
        if box.clickedButton() is use:
            p.materials.update(specs)

    def import_mtl(self):
        """Fichier > Importer les materiaux d'un fichier MTL (annulable)."""
        if not self.model:
            return
        start = mtl.find_for(self.model.path) or os.path.dirname(self.model.path)
        f, _ = QFileDialog.getOpenFileName(self, tr("Fichier de matériaux"), start, tr("Matériaux MTL") + " (*.mtl)")
        if not f:
            return
        name = os.path.basename(f)
        try:
            specs, _ = mtl.specs_for(f, self.model.materials())
            known = set(mtl.parse(f)) & set(self.model.materials())
        except OSError as e:
            QMessageBox.critical(self, tr("Fichier de matériaux"), str(e)); return
        if not specs:
            QMessageBox.information(self, tr("Fichier de matériaux"),
                                    tr("MTL_DEFAUTS", file=name) if known else tr("MTL_AUCUN", file=name))
            return
        if QMessageBox.question(self, tr("Fichier de matériaux"),
                                tr("MTL_IMPORT", file=name, n=len(specs))) != QMessageBox.Yes:
            return
        self.checkpoint()
        self.project.materials.update(specs)
        self.mark_dirty()
        self.fill_tree()
        self.material_panel.reload()
        self.viewport.refresh()
        self.say(tr("Matières importées depuis « {file} » : {n} matériau(x).", file=name, n=len(specs)))

    def open_project(self):
        if not self.confirm_discard():
            return
        f, _ = QFileDialog.getOpenFileName(self, tr("Ouvrir un projet"), PROJECTS, project_filter())
        if f:
            self.open_project_file(f)

    def save_project(self):
        if not self.project.path:
            return self.save_project_as()
        self.project.save()
        self.dirty = False
        self.update_title()
        self.say(tr("Projet enregistré : {path}", path=self.project.path))
        return True

    def save_project_as(self):
        f, _ = QFileDialog.getSaveFileName(self, tr("Enregistrer sous"), self.project.path or PROJECTS,
                                           project_filter())
        if not f:
            return False
        self.project.save(f)
        self.dirty = False
        self.update_title()
        return True

    def mark_dirty(self):
        self.dirty = True
        self.update_title()

    def update_title(self):
        name = self.project.name if self.project else ""
        self.setWindowTitle(f"HyStudio {VERSION} — {name}{' *' if self.dirty else ''}")

    def confirm_discard(self):
        if not self.dirty:
            return True
        r = QMessageBox.question(self, tr("Modifications non enregistrées"),
                                 tr("Enregistrer les modifications du projet ?"),
                                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if r == QMessageBox.Save:
            return bool(self.save_project())
        return r == QMessageBox.Discard

    def closeEvent(self, e):
        if self._swapping:                         # remplacee par la fenetre dans la nouvelle langue
            e.accept(); return
        if self.gen_worker and QMessageBox.question(
                self, tr("Génération en cours"), tr("Une génération est en cours. L'arrêter et quitter ?")) != QMessageBox.Yes:
            e.ignore(); return
        if not self.confirm_discard():
            e.ignore(); return
        self.cancel_jobs()
        for th, _ in self._threads:
            try:
                th.quit(); th.wait(3000)
            except RuntimeError:
                pass
        e.accept()

    # ------------------------------------------------------------ pieces
    def fill_tree(self):
        current = self.tree.currentItem().data(0, Qt.UserRole) if self.tree.currentItem() else None
        self.tree.blockSignals(True)
        self.tree.clear()
        self._items, self._mat_items = {}, {}
        if not self.model.separated:
            # un seul objet : on ne propose que ses materiaux
            tri = {}
            for part in self.model.parts:
                for start, count, mat in part.ranges:
                    tri[mat] = tri.get(mat, 0) + count // 3
            for mat, n in tri.items():
                it = QTreeWidgetItem([tr_label(self.project.label(mat)), f"{n:,}".replace(",", " ")])
                it.setData(0, Qt.UserRole, ("material", mat))
                self.tree.addTopLevelItem(it)
                self._mat_items[mat] = it
            self._finish_tree(current)
            return
        groups = {}
        for part in self.model.parts:
            groups.setdefault(part.material, []).append(part)
        for mat, parts in groups.items():
            top = QTreeWidgetItem([f"{tr_label(self.project.label(mat))}  ({len(parts)})",
                                   f"{sum(p.triangles for p in parts):,}".replace(",", " ")])
            top.setData(0, Qt.UserRole, ("material", mat))
            self._mat_items[mat] = top
            f = top.font(0); f.setBold(True); top.setFont(0, f)
            for part in parts:
                label = tr_label(self.project.label(part.name))
                mark = " •" if part.name in self.project.parts else ""
                it = QTreeWidgetItem([label + mark, f"{part.triangles:,}".replace(",", " ")])
                it.setData(0, Qt.UserRole, ("part", part.name))
                if label != part.name:
                    it.setToolTip(0, part.name)
                top.addChild(it)
                self._items[part.name] = it
            self.tree.addTopLevelItem(top)
        self._finish_tree(current)

    def _finish_tree(self, current):
        if current:
            it = (self._items if current[0] == "part" else self._mat_items).get(current[1])
            if it:
                self.tree.setCurrentItem(it)
        self.tree.blockSignals(False)
        self.apply_filter(self.filter.text())

    def apply_filter(self, text):
        t = text.lower().strip()
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            if top.childCount() == 0:
                top.setHidden(bool(t) and t not in top.text(0).lower())
                continue
            any_visible = False
            for j in range(top.childCount()):
                ch = top.child(j)
                vis = not t or t in ch.text(0).lower() or t in ch.data(0, Qt.UserRole)[1].lower() \
                    or t in top.text(0).lower()
                ch.setHidden(not vis)
                any_visible |= vis
            top.setHidden(not any_visible)

    def on_tree_selection(self):
        items = self.tree.selectedItems()
        if not items:
            return
        kind, key = items[0].data(0, Qt.UserRole)
        if kind == "part":
            self.viewport.selected, self.viewport.selected_mats = {key}, set()
            self.material_panel.set_target(key)
        else:
            self.viewport.selected, self.viewport.selected_mats = set(), {key}
            self.material_panel.set_target(None, key)
        self.viewport.refresh()

    def on_part_clicked(self, name, ctrl=False):
        self.on_picked(name, "", ctrl)

    def on_picked(self, name, material, ctrl):
        if not name:
            self.tree.clearSelection()
            self.viewport.selected, self.viewport.selected_mats = set(), set()
            self.material_panel.set_target(None)
            self.viewport.refresh()
            return
        if not self.model.separated:                # un seul objet : on selectionne le materiau
            it = self._mat_items.get(material)
        else:
            it = self._items.get(name)
        if it:
            self.tree.setCurrentItem(it)
            self.tree.scrollToItem(it)

    # ------------------------------------------------------------ studio
    def _sync_studio(self):
        s = self.project.studio
        for w in (self.s_exposure, self.s_sharpen, self.s_views, self.s_samples, self.s_cabin):
            w.blockSignals(True)
        self.s_exposure.setValue(s["exposure"])
        self.s_sharpen.setValue(int(s["sharpen"]))
        self.s_views.setCurrentIndex(max(0, self.s_views.findData(int(s["views"]))))
        self.s_samples.setCurrentIndex(max(0, self.s_samples.findData(int(s["samples"]))))
        self.s_cabin.setValue(int(s["cabin_light"]))
        for w in (self.s_exposure, self.s_sharpen, self.s_views, self.s_samples, self.s_cabin):
            w.blockSignals(False)

    def _studio(self, key, value):
        if self.project.studio.get(key) == value:
            return
        self.checkpoint(("studio", key))
        self.project.studio[key] = value
        self.mark_dirty()
        self.update_estimate()

    def update_estimate(self):
        s = self.project.studio
        n = int(s["views"])
        secs = n * SEC_PER_VIEW_96 * (0.35 + 0.65 * int(s["samples"]) / 96)
        mb = n * KB_PER_VIEW / 1000
        warn = ""
        if mb > 180:
            warn = "  " + tr("⚠ plus de la moitié de la mémoire libre de l'autoradio (280 Mo)")
        self.s_estimate.setText(tr("Génération ≈ {min} min · fichier ≈ {mb} Mo", min=f"{secs/60:.0f}", mb=f"{mb:.0f}") + warn)

    # ------------------------------------------------------------ apercu
    def run_preview(self):
        if not self.model or self.preview_worker:
            return
        turn, samples = self.angle.currentData(), self.prev_samples.currentData()
        proj = copy.deepcopy(self.project)
        self.prev_btn.setEnabled(False)
        self.prev_info.setText(tr("Calcul en cours…"))
        t0 = time.time()

        def job(w):
            return pipeline.preview(proj, self.model, turn, samples, cancel=lambda: w.cancelled)

        def done(res):
            self.preview_worker = None
            rgb, _ = res
            self.prev_label.setPixmap(rgb_to_pixmap(rgb))
            self.prev_btn.setEnabled(True)
            self.prev_info.setText(tr("{view} — calculé en {s} s", view=self.angle.currentText(),
                                       s=i18n.number(time.time() - t0, 1)))
            self.tabs.setCurrentIndex(1)

        def fail(msg):
            self.preview_worker = None
            self.prev_btn.setEnabled(True)
            self.prev_info.setText(tr("Échec de l'aperçu."))
            self.say(msg)

        self.preview_worker = run_async(self, job, done, fail)

    # ------------------------------------------------------------ generation
    def run_generate(self):
        if not self.model or self.gen_worker:
            return
        default = os.path.join(os.path.dirname(self.project.path or PROJECTS), "i20.frm")
        out, _ = QFileDialog.getSaveFileName(self, tr("Fichier pour l'autoradio"), default, tr("Vues i20view") + " (*.frm)")
        if not out:
            return
        proj = copy.deepcopy(self.project)
        n = int(proj.studio["views"])
        self.progress.setRange(0, n); self.progress.setValue(0)
        self.gen_btn.setEnabled(False); self.cancel_btn.setEnabled(True)
        self.say(tr("Génération de {n} vues vers {path}", n=n, path=out))
        self.last_frm = out

        def job(w):
            return pipeline.generate(proj, self.model, out,
                                     progress=lambda d, t, eta: w.progress.emit((d, t, eta)),
                                     cancel=lambda: w.cancelled)

        def prog(v):
            d, t, eta = v
            end = datetime.datetime.now() + datetime.timedelta(seconds=eta)
            self.progress.setValue(d)
            self.progress_label.setText(tr("{d} / {t} vues — reste {min} min — fin vers {end}",
                                           d=d, t=t, min=f"{eta/60:.0f}", end=f"{end:%H:%M}"))

        def done(res):
            self.gen_worker = None
            size, dt = res
            self.gen_btn.setEnabled(True); self.cancel_btn.setEnabled(False)
            self.progress_label.setText(tr("Terminé : {mb} Mo en {min} min.", mb=i18n.number(size / 1e6, 1),
                                           min=i18n.number(dt / 60, 1)))
            self.say(tr("Fichier prêt : {path} ({mb} Mo)", path=out, mb=i18n.number(size / 1e6, 1)))
            QApplication.alert(self)

        def fail(msg):
            self.gen_worker = None
            self.gen_btn.setEnabled(True); self.cancel_btn.setEnabled(False)
            self.progress_label.setText(tr("Génération interrompue — aucun fichier écrit."))
            self.say(msg)

        self.gen_worker = run_async(self, job, done, fail, prog)

    def cancel_jobs(self):
        for w in (self.gen_worker, self.preview_worker):
            if w:
                w.cancelled = True

    # ------------------------------------------------------------ autoradio
    def copy_to_sd(self):
        frm = getattr(self, "last_frm", None)
        if not frm or not os.path.exists(frm):
            frm, _ = QFileDialog.getOpenFileName(self, tr("Fichier de vues à copier"), PROJECTS,
                                                 tr("Vues i20view") + " (*.frm)")
            if not frm:
                return
        cards = device.find_sd_cards()
        if not cards:
            QMessageBox.information(self, tr("Carte SD"), tr("Aucune carte SD de l'autoradio détectée.\n"
                                                          "Branchez-la (elle contient eu20_upgrade.lgu) puis réessayez."))
            return
        root = cards[0]
        if not device.is_clean(root):
            QMessageBox.warning(self, tr("Carte SD non intègre"),
                                tr("SD_SALE", root=root, drive=root.rstrip(chr(92))))
            return
        self.sd_btn.setEnabled(False)
        self.sd_busy = True
        self.progress.setRange(0, 100); self.progress.setValue(0)
        self.say(tr("Copie sur {root}…", root=root))

        def job(w):
            sums = {}
            files = [(frm, os.path.join(root, "i20.frm"))]
            if device.viewer_exe():
                files.append((device.viewer_exe(), os.path.join(root, "i20view.exe")))
            for k, (src, dst) in enumerate(files):
                sums[os.path.basename(dst)] = device.copy_verified(
                    src, dst, lambda f, k=k: w.progress.emit(int((k + f) / len(files) * 100)))
            ejected = device.eject(root)
            return sums, ejected

        def done(res):
            sums, ejected = res
            self.sd_busy = False
            self.sd_btn.setEnabled(True)
            self.progress.setValue(100)
            self.say(tr("Copie vérifiée (MD5) : {files}", files=", ".join(f"{k} {v[:8]}…" for k, v in sums.items())))
            msg = tr("Carte éjectée, vous pouvez la retirer.") if ejected else tr("Copie faite. Éjectez la carte avant de la retirer.")
            self.progress_label.setText(msg)
            QMessageBox.information(self, tr("Carte SD"), msg)

        def fail(msg):
            self.sd_busy = False
            self.sd_btn.setEnabled(True)
            self.say(msg)
            QMessageBox.critical(self, tr("Copie"), msg.split("\n\n")[0])

        run_async(self, job, done, fail, lambda v: self.progress.setValue(v))

    # ------------------------------------------------------------ annuler / retablir
    def checkpoint(self, tag=None):
        self.history.checkpoint(self.project, tag)
        self.update_history_actions()

    def update_history_actions(self):
        if hasattr(self, "undo_action"):
            self.undo_action.setEnabled(bool(self.history.undo_stack))
            self.redo_action.setEnabled(bool(self.history.redo_stack))

    def _after_history(self, done, verb):
        if not done:
            self.statusBar().showMessage(tr("Rien à annuler.") if verb == "annuler" else tr("Rien à rétablir."), 3000)
            return
        self.mark_dirty()
        self._sync_studio()
        self.update_estimate()
        if self.model:
            self.fill_tree()
            self.material_panel.reload()
            self.viewport.refresh()
        self.update_history_actions()
        self.statusBar().showMessage(tr("Annulé.") if verb == "annuler" else tr("Rétabli."), 3000)

    def undo(self):
        self._after_history(self.history.undo(self.project), "annuler")

    def redo(self):
        self._after_history(self.history.redo(self.project), "rétablir")

    # ------------------------------------------------------------ langue
    def change_language(self, choice):
        """Enregistre le choix et reconstruit la fenetre dans la nouvelle langue,
        sans recharger le modele ni perdre le projet, l'historique ou le journal."""
        i18n.save_choice(choice)
        code = i18n.resolve(choice)
        if code == i18n.current():
            return
        if self.gen_worker or self.preview_worker or self.sd_busy:
            QMessageBox.information(self, tr("Changement de langue"),
                                    tr("Un calcul ou une copie est en cours : la langue choisie s'appliquera au prochain démarrage."))
            return
        i18n.set_language(code)
        cur = self.tree.currentItem()
        state = {"project": self.project, "model": self.model, "dirty": self.dirty, "history": self.history,
                 "last_frm": getattr(self, "last_frm", None), "log": self.log.toPlainText(),
                 "camera": (self.viewport.yaw, self.viewport.pitch, self.viewport.dist),
                 "selection": cur.data(0, Qt.UserRole) if cur else None,
                 "tab": self.tabs.currentIndex(), "preview": self.prev_label.pixmap(),
                 "geometry": self.saveGeometry(), "docks": self.saveState()}
        new = MainWindow(state)
        new.restoreGeometry(state["geometry"])
        new.show()
        _WINDOWS[:] = [new]
        self._swapping = True
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.close()

    def _restore(self, st):
        self.restoreState(st["docks"])
        self.project, self.history = st["project"], st["history"]
        self.last_frm = st["last_frm"]
        self.log.setPlainText(st["log"])
        self._sync_studio()
        if st["model"] is not None:
            self._model_loaded(st["model"], quiet=True)
            self.viewport.yaw, self.viewport.pitch, self.viewport.dist = st["camera"]
            sel = st["selection"]
            if sel:
                it = (self._items if sel[0] == "part" else self._mat_items).get(sel[1])
                if it:
                    self.tree.setCurrentItem(it)
        if st["preview"] is not None and not st["preview"].isNull():
            self.prev_label.setPixmap(st["preview"])
        self.tabs.setCurrentIndex(st["tab"])
        self.dirty = st["dirty"]
        self.update_title()
        self.update_history_actions()

    def eventFilter(self, obj, ev):
        """Ctrl+Z dans un champ numerique annule le projet, pas la saisie du champ.

        Un QSpinBox garde le focus apres un changement et intercepte Ctrl+Z pour
        sa propre saisie : l'annulation du projet n'arrivait jamais. Les champs
        texte (nom d'une piece) gardent, eux, leur annulation de saisie."""
        from PySide6.QtCore import QEvent
        if ev.type() == QEvent.ShortcutOverride:
            w = QApplication.focusWidget()
            spin = w is not None and (isinstance(w, QAbstractSpinBox)
                                      or isinstance(w.parent(), QAbstractSpinBox))
            if spin and (ev.matches(QKeySequence.Undo) or ev.matches(QKeySequence.Redo)
                         or ev.keyCombination().toCombined() == QKeySequence("Ctrl+Y")[0].toCombined()):
                return True                        # non accepte : le raccourci du menu s'applique
        return super().eventFilter(obj, ev)
