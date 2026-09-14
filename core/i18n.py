"""Langues de l'interface.

Le texte francais du code sert de cle : tr("Enregistrer") renvoie la traduction
de la langue active, ou le francais si la chaine n'est pas dans la table. Les
parametres s'ecrivent {nom} et se passent en arguments nommes.

Langue : choix enregistre dans les reglages (menu Langue), sinon langue du
systeme si elle est proposee, sinon anglais.
"""
from .translations import TABLE

LANGS = {"fr": "Français", "en": "English", "es": "Español",
         "de": "Deutsch", "it": "Italiano", "ru": "Русский",
         "zh": "中文", "ja": "日本語", "ko": "한국어"}
FALLBACK = "en"
AUTO = "auto"
SETTING = "langue"

_lang = "fr"
_qt_translator = None


def current():
    return _lang


def tr(src, **kw):
    entry = TABLE.get(src)
    text = entry.get(_lang, src) if entry else src
    return text.format(**kw) if kw else text


def tr_label(label):
    """Nom lisible venu d'un projet : traduit s'il s'agit d'un nom fourni par
    HyStudio (profil i20), laisse tel quel s'il a ete saisi par l'utilisateur."""
    entry = TABLE.get(label)
    return entry.get(_lang, label) if entry else label


def system_language():
    from PySide6.QtCore import QLocale
    for tag in QLocale.system().uiLanguages():
        code = tag.replace("_", "-").split("-")[0].lower()
        if code in LANGS:
            return code
    return FALLBACK


def _settings():
    from .paths import settings
    return settings()


def saved_choice():
    v = _settings().value(SETTING, AUTO)
    return v if v in LANGS or v == AUTO else AUTO


def save_choice(choice):
    _settings().setValue(SETTING, choice)


def resolve(choice):
    return system_language() if choice == AUTO else choice


LOCALES = {"fr": "fr_FR", "en": "en_US", "es": "es_ES", "de": "de_DE", "it": "it_IT",
           "ru": "ru_RU", "zh": "zh_CN", "ja": "ja_JP", "ko": "ko_KR"}


def number(value, decimals=0):
    """Nombre avec le separateur decimal de la langue active."""
    from PySide6.QtCore import QLocale
    return QLocale(LOCALES[_lang]).toString(float(value), "f", decimals)


def set_language(code):
    """Active une langue, y compris pour les boites de dialogue standard de Qt."""
    global _lang, _qt_translator
    _lang = code if code in LANGS else FALLBACK
    from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
    from PySide6.QtWidgets import QApplication
    QLocale.setDefault(QLocale(LOCALES[_lang]))       # separateur decimal des champs numeriques
    app = QApplication.instance()
    if app is None:
        return
    if _qt_translator is not None:
        app.removeTranslator(_qt_translator)
        _qt_translator = None
    t = QTranslator(app)
    name = {"zh": "qtbase_zh_CN"}.get(_lang, f"qtbase_{_lang}")
    if t.load(name, QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
        app.installTranslator(t)
        _qt_translator = t


def init():
    set_language(resolve(saved_choice()))
