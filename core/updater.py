"""Mises a jour : derniere release GitHub, telechargement verifie, installateur.

Seul le dossier du logiciel est remplace : l'installateur (installer/hystudio.iss)
supprime puis reinstalle _internal et HyStudio.exe, jamais les projets
(Documents\\HyStudio), les modeles de l'utilisateur ni le cache (%LOCALAPPDATA%).

Sans connexion, check() renvoie None sans rien signaler : la verification au
demarrage doit rester invisible.
"""
import hashlib, json, os, re, subprocess, tempfile, urllib.request

from .version import REPO_URL, VERSION

API = os.environ.get("HYSTUDIO_UPDATE_URL") or \
    REPO_URL.replace("https://github.com/", "https://api.github.com/repos/") + "/releases/latest"
TIMEOUT = 6


class Release:
    def __init__(self, version, notes, url, size, sha256, page):
        self.version, self.notes, self.url, self.size, self.sha256, self.page = version, notes, url, size, sha256, page


def parse_version(text):
    nums = re.findall(r"\d+", text or "")
    return tuple(int(n) for n in nums[:3]) + (0,) * (3 - len(nums[:3]))


def is_newer(candidate, current=VERSION):
    return parse_version(candidate) > parse_version(current)


def _open(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"HyStudio/{VERSION}",
                                               "Accept": "application/vnd.github+json"})
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def check():
    """Release plus recente que la version en cours, avec son installateur ; sinon None."""
    try:
        with _open(API) as r:
            data = json.loads(r.read().decode("utf-8"))
    except (OSError, ValueError):
        return None
    tag = data.get("tag_name", "")
    if data.get("draft") or data.get("prerelease") or not is_newer(tag):
        return None
    asset = next((a for a in data.get("assets", []) if a.get("name", "").lower().endswith("setup.exe")), None)
    if not asset:
        return None
    digest = asset.get("digest") or ""                   # GitHub : "sha256:..."
    return Release(tag.lstrip("vV"), data.get("body") or "", asset["browser_download_url"],
                   int(asset.get("size") or 0), digest[7:] if digest.startswith("sha256:") else "",
                   data.get("html_url") or REPO_URL + "/releases/latest")


def download(release, progress=lambda frac: None, cancelled=lambda: False):
    """Installateur dans le dossier temporaire, taille et SHA-256 verifies. Renvoie son chemin."""
    from .i18n import tr
    dest = os.path.join(tempfile.gettempdir(), f"HyStudio-{release.version}-Setup.exe")
    part = dest + ".partiel"
    h, done = hashlib.sha256(), 0
    with _open(release.url) as r, open(part, "wb") as f:
        total = release.size or int(r.headers.get("Content-Length") or 0)
        while True:
            if cancelled():
                f.close(); os.remove(part)
                from .pipeline import Cancelled
                raise Cancelled()
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk); h.update(chunk); done += len(chunk)
            if total:
                progress(done / total)
    if (release.size and done != release.size) or (release.sha256 and h.hexdigest() != release.sha256.lower()):
        os.remove(part)
        raise RuntimeError(tr("Le téléchargement de la mise à jour est incomplet ou altéré. Réessayez plus tard."))
    os.replace(part, dest)
    return dest


def launch_installer(path):
    """Lance l'installateur puis laisse HyStudio se fermer : il remplace le logiciel et le relance.

    /SILENT : fenetre de progression sans questions ; /CLOSEAPPLICATIONS : attend la
    fermeture de HyStudio ; /LAUNCH : relance le logiciel une fois installe."""
    args = [path, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS", "/LAUNCH"]
    flags = subprocess.DETACHED_PROCESS if os.name == "nt" else 0
    subprocess.Popen(args, creationflags=flags, close_fds=True)


def can_install():
    """Installation automatique pour l'exe installe seulement ; version portable et sources :
    on ouvre la page de la release (l'installateur installerait ailleurs)."""
    from .paths import FROZEN, PORTABLE
    return FROZEN and not PORTABLE
