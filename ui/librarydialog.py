"""Fenetre de la bibliotheque de voitures : covers, recherche, creation d'un projet."""
import os

from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton,
                               QVBoxLayout)

from core import library, paths
from core.i18n import tr

THUMB = QSize(300, 160)


def thumbnail(path):
    """Cover recadree au format de la vignette ; fond neutre sans cover."""
    pm = QPixmap(THUMB)
    pm.fill(QColor(24, 28, 33))
    src = QPixmap(path) if path else QPixmap()
    if not src.isNull():
        scaled = src.scaled(THUMB, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x, y = (scaled.width() - THUMB.width()) // 2, (scaled.height() - THUMB.height()) // 2
        p = QPainter(pm)
        p.drawPixmap(0, 0, scaled, x, y, THUMB.width(), THUMB.height())
        p.end()
    return QIcon(pm)


class LibraryDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(tr("Bibliothèque de voitures"))
        self.resize(1040, 680)
        self.chosen = None
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("Rechercher une voiture…"))
        self.search.textChanged.connect(self._filter)
        top.addWidget(self.search, 1)
        refresh = QPushButton(tr("Actualiser"))
        refresh.clicked.connect(self.reload)
        folder = QPushButton(tr("Ouvrir le dossier de la bibliothèque"))
        folder.clicked.connect(self._open_folder)
        top.addWidget(refresh); top.addWidget(folder)
        lay.addLayout(top)

        self.grid = QListWidget()
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setIconSize(THUMB)
        self.grid.setGridSize(QSize(THUMB.width() + 24, THUMB.height() + 44))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setMovement(QListWidget.Static)
        self.grid.setUniformItemSizes(True)
        self.grid.setWordWrap(True)
        self.grid.itemDoubleClicked.connect(lambda _: self._create())
        self.grid.currentItemChanged.connect(lambda *_: self.create_btn.setEnabled(self.grid.currentItem() is not None))
        lay.addWidget(self.grid, 1)

        self.empty = QLabel(); self.empty.setWordWrap(True); self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setStyleSheet("color: #9AA3AE; font-size: 14px; padding: 40px;")
        lay.addWidget(self.empty, 1)

        bottom = QHBoxLayout()
        self.count = QLabel()
        bottom.addWidget(self.count, 1)
        self.create_btn = QPushButton(tr("Créer le projet"))
        self.create_btn.setDefault(True)
        self.create_btn.clicked.connect(self._create)
        close = QPushButton(tr("Fermer")); close.clicked.connect(self.reject)
        bottom.addWidget(self.create_btn); bottom.addWidget(close)
        lay.addLayout(bottom)
        self.reload()

    def reload(self):
        self.grid.clear()
        entries = library.scan()
        for e in entries:
            it = QListWidgetItem(thumbnail(e.cover), e.name)
            it.setData(Qt.UserRole, e)
            it.setToolTip(e.model)
            it.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            self.grid.addItem(it)
        self.grid.setVisible(bool(entries))
        self.empty.setVisible(not entries)
        self.empty.setText(tr("BIBLIOTHEQUE_VIDE", folder=paths.library_home()))
        self.count.setText(tr("{n} voiture(s)", n=len(entries)))
        if entries:
            self.grid.setCurrentRow(0)
        self.create_btn.setEnabled(bool(entries))
        self._filter(self.search.text())

    def _filter(self, text):
        t = text.lower().strip()
        for i in range(self.grid.count()):
            it = self.grid.item(i)
            it.setHidden(bool(t) and t not in it.text().lower())

    def _open_folder(self):
        home = paths.library_home()
        os.makedirs(home, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(home))

    def _create(self):
        it = self.grid.currentItem()
        if it is not None and not it.isHidden():
            self.chosen = it.data(Qt.UserRole)
            self.accept()
