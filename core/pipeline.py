"""Pilotage de Blender : apercu realiste et generation complete pour l'autoradio.

Les deux fonctions sont bloquantes et prennent des rappels (progression,
annulation) : l'interface les execute dans un fil de travail.
"""
import json, os, shutil, subprocess, time

from . import encoder, paths
from .i18n import tr

RENDERER, WORK = paths.RENDERER, paths.WORK

# vues d'apercu : rotation en degres par rapport au 3/4 avant (noms traduits a l'affichage)
ANGLES = {"3/4 avant": 0, "Face": 325, "Profil gauche": 55, "3/4 arrière": 180,
          "Dos": 145, "Profil droit": 235, "3/4 avant droit": 290}


class Cancelled(Exception):
    pass


find_blender = paths.find_blender


def _export(project, model):
    os.makedirs(WORK, exist_ok=True)
    d = project.to_dict(absolute=True)
    d["unit_scale"] = model.unit_scale
    if model.is_gltf:                                    # Blender relit la geometrie lue par HyStudio
        d["geometry"] = model.cache
        d["source_materials"] = model.source_materials
    path = os.path.join(WORK, "projet_rendu.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    return path


_job = None


def _kill_with_us(proc):
    """Windows : range Blender dans un job ferme a la mort de HyStudio, meme brutale."""
    global _job
    if os.name != "nt":
        return
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.OpenProcess.restype = wintypes.HANDLE
    if _job is None:
        class LIMIT(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class IO(ctypes.Structure):
            _fields_ = [(n, ctypes.c_uint64) for n in ("r", "w", "o", "rt", "wt", "ot")]

        class EXT(ctypes.Structure):
            _fields_ = [("Basic", LIMIT), ("Io", IO), ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]
        job = k32.CreateJobObjectW(None, None)
        info = EXT()
        info.Basic.LimitFlags = 0x2000                 # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not job or not k32.SetInformationJobObject(wintypes.HANDLE(job), 9, ctypes.byref(info),
                                                      ctypes.sizeof(info)):
            return
        _job = job                                     # handle garde ouvert jusqu'a la fin du processus
    h = k32.OpenProcess(0x0101, False, proc.pid)       # PROCESS_TERMINATE | PROCESS_SET_QUOTA
    if h:
        k32.AssignProcessToJobObject(wintypes.HANDLE(_job), wintypes.HANDLE(h))
        k32.CloseHandle(wintypes.HANDLE(h))


def _popen(cmd, log_path):
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    log = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
    _kill_with_us(proc)
    return proc, log


def preview(project, model, turn=0, samples=48, cancel=lambda: False):
    """Rend une vue ; renvoie (rgb 800x424 tel que l'autoradio l'affichera, png plein format)."""
    blender = find_blender()
    if not blender:
        raise RuntimeError(tr("Blender introuvable (dossier tools/ du dépôt ou Program Files)"))
    proj = _export(project, model)
    out = os.path.join(WORK, f"apercu_{int(time.time()*1000)}.png")
    proc, log = _popen([blender, "-b", "-P", RENDERER, "--", "--project", proj, "--mode", "preview",
                        "--turn", str(turn), "--samples", str(samples), "--out", out],
                       os.path.join(WORK, "apercu.log"))
    try:
        while proc.poll() is None:
            if cancel():
                proc.kill(); raise Cancelled()
            time.sleep(0.1)
    finally:
        log.close()
    if not os.path.exists(out):
        raise RuntimeError(tr("Le rendu a échoué : voir {log}", log=os.path.join(WORK, "apercu.log")))
    rgb, _ = encoder.compose(out, project.studio.get("sharpen", 0))
    return rgb, out


def generate(project, model, frm_path, progress=lambda done, total, eta: None, cancel=lambda: False):
    """Rend toute l'orbite et encode chaque vue des qu'elle est ecrite.

    Le fichier .frm n'est ecrit que si TOUTES les vues sont presentes."""
    blender = find_blender()
    if not blender:
        raise RuntimeError(tr("Blender introuvable (dossier tools/ du dépôt ou Program Files)"))
    views = int(project.studio["views"])
    sharpen = int(project.studio.get("sharpen", 0))
    src = os.path.join(WORK, "vues")
    shutil.rmtree(src, ignore_errors=True)
    os.makedirs(src)
    proj = _export(project, model)
    done_flag = os.path.join(src, "RENDU_TERMINE")
    digits = max(3, len(str(views - 1)))
    frame = lambda i: os.path.join(src, f"v_{i:0{digits}d}.png")

    proc, log = _popen([blender, "-b", "-P", RENDERER, "--", "--project", proj, "--mode", "full",
                        "--views", str(views), "--out", src], os.path.join(WORK, "generation.log"))
    blobs, t0 = [], time.time()
    try:
        while len(blobs) < views:
            if cancel():
                proc.kill(); raise Cancelled()
            i = len(blobs)
            if os.path.exists(frame(i)) and (os.path.exists(frame(i + 1)) or os.path.exists(done_flag)):
                blobs.append(encoder.encode_file(frame(i), sharpen))
                os.remove(frame(i))                      # PNG non compresses : ~5 Mo chacun
                el = time.time() - t0
                progress(len(blobs), views, el / len(blobs) * (views - len(blobs)))
                continue
            if proc.poll() is not None and not os.path.exists(done_flag):
                raise RuntimeError(tr("Blender s'est arrêté à la vue {i} : voir {log}",
                                      i=i, log=os.path.join(WORK, "generation.log")))
            time.sleep(0.25)
        proc.wait()
    finally:
        if proc.poll() is None:
            proc.kill()
        log.close()

    data = encoder.assemble(blobs)
    tmp = frm_path + ".partiel"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, frm_path)
    shutil.rmtree(src, ignore_errors=True)
    return len(data), time.time() - t0
