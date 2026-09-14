"""Vue 3D interactive : tourner, zoomer, cliquer une piece pour la selectionner.

OpenGL 3.3 (profil core) dans un QOpenGLWidget. L'eclairage est une
approximation de studio, pas le rendu final : il sert a reconnaitre et
selectionner les pieces, l'apercu realiste (Blender) juge l'aspect.

Selection : au clic, la scene est redessinee hors ecran avec une couleur par
piece (son numero), et on lit le pixel sous la souris.
"""
import math
import numpy as np
from OpenGL import GL
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from core import presets

VS = """#version 330 core
layout(location=0) in vec3 pos; layout(location=1) in vec3 nrm; layout(location=2) in vec2 uv;
uniform mat4 mvp; out vec3 P; out vec3 N; out vec2 UV;
void main(){ P = pos; N = nrm; UV = uv; gl_Position = mvp * vec4(pos, 1.0); }"""

FS = """#version 330 core
in vec3 P; in vec3 N; in vec2 UV; out vec4 o;
uniform int hasSrc; uniform sampler2D stex;
uniform vec3 base; uniform float metal, rough, alpha; uniform vec3 cam;
uniform int highlight; uniform int hasTex; uniform sampler2D tex;
uniform vec3 texRight, texUp; uniform vec4 texRange;
uniform int hasDecal; uniform sampler2D dtex;
uniform vec3 dRight, dUp, dDir; uniform vec2 dCenter, dSize, dRot;
vec3 env(vec3 d){
    float h = d.y;
    vec3 c = mix(vec3(0.05), vec3(0.34), smoothstep(-0.15, 0.35, h));
    c += vec3(2.2) * smoothstep(0.72, 0.86, h);
    c += vec3(1.1) * smoothstep(0.80, 0.92, abs(d.x)) * smoothstep(0.02, 0.12, h)
         * (1.0 - smoothstep(0.50, 0.62, h));
    return c;
}
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14), 0.0, 1.0); }
void main(){
    vec3 v = normalize(cam - P);
    vec3 n = normalize(N); if(!gl_FrontFacing) n = -n;
    vec3 b = base;
    if (hasTex == 1) {
        float u = (dot(P, texRight) - texRange.x) / (texRange.y - texRange.x);
        float w = (dot(P, texUp) - texRange.z) / (texRange.w - texRange.z);
        b = texture(tex, vec2(clamp(u, 0.0, 1.0), clamp(w, 0.0, 1.0))).rgb;
    }
    b = pow(b, vec3(2.2));
    if (hasSrc == 1) b *= pow(texture(stex, vec2(UV.x, 1.0 - UV.y)).rgb, vec3(2.2));   // glTF : v vers le bas
    float m = metal;
    if (hasDecal == 1) {                   // autocollant : meme calcul que render_project.add_decal
        float du = dot(P, dRight) - dCenter.x;
        float dv = dot(P, dUp) - dCenter.y;
        vec2 uv = vec2((du * dRot.x + dv * dRot.y) / dSize.x, (-du * dRot.y + dv * dRot.x) / dSize.y) + 0.5;
        if (all(greaterThanEqual(uv, vec2(0.0))) && all(lessThanEqual(uv, vec2(1.0)))) {
            vec4 t = texture(dtex, uv);
            float f = t.a * smoothstep(0.15, 0.35, dot(normalize(N), dDir));
            b = mix(b, pow(t.rgb, vec3(2.2)), f);
            m = mix(metal, 0.0, f);
        }
    }
    vec3 L = normalize(vec3(-0.35, 0.85, 0.40));
    float amb = mix(0.18, 0.85, n.y * 0.5 + 0.5);
    vec3 diff = b * (1.0 - m) * (0.55 * amb + 0.7 * max(dot(n, L), 0.0));
    vec3 F0 = mix(vec3(0.04), b, m);
    vec3 F = F0 + (1.0 - F0) * pow(1.0 - max(dot(n, v), 0.0), 5.0) * (1.0 - rough * 0.8);
    vec3 e = mix(env(reflect(-v, n)), vec3(0.3), clamp(rough * 1.3, 0.0, 1.0));
    vec3 col = pow(aces(diff + F * e), vec3(1.0 / 2.2));
    if (highlight == 1) col = mix(col, vec3(1.0, 0.55, 0.1), 0.45);
    o = vec4(col * alpha, alpha);
}"""

PICK_FS = """#version 330 core
out vec4 o; uniform vec3 idcol; void main(){ o = vec4(idcol, 1.0); }"""


def set_default_format():
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    fmt.setDepthBufferSize(24)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)


def _perspective(fovy, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fovy) / 2)
    m = np.zeros((4, 4), np.float32)
    m[0, 0] = f / aspect; m[1, 1] = f
    m[2, 2] = (far + near) / (near - far); m[2, 3] = 2 * far * near / (near - far)
    m[3, 2] = -1.0
    return m


def _look_at(eye, target):
    f = target - eye; f /= np.linalg.norm(f)
    s = np.cross(f, np.array([0, 1, 0], np.float32)); s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.eye(4, dtype=np.float32)
    m[0, :3], m[1, :3], m[2, :3] = s, u, -f
    m[:3, 3] = -m[:3, :3] @ eye
    return m


def _program(vs, fs):
    def sh(src, kind):
        s = GL.glCreateShader(kind); GL.glShaderSource(s, src); GL.glCompileShader(s)
        if not GL.glGetShaderiv(s, GL.GL_COMPILE_STATUS):
            raise RuntimeError(GL.glGetShaderInfoLog(s).decode())
        return s
    p = GL.glCreateProgram()
    GL.glAttachShader(p, sh(vs, GL.GL_VERTEX_SHADER))
    GL.glAttachShader(p, sh(fs, GL.GL_FRAGMENT_SHADER))
    GL.glLinkProgram(p)
    if not GL.glGetProgramiv(p, GL.GL_LINK_STATUS):
        raise RuntimeError(GL.glGetProgramInfoLog(p).decode())
    return p


def decal_frame(part, model_center):
    """Meme projection que blender/render_project.py, en coordonnees OBJ (Y vertical)."""
    lo, hi = part.bounds
    dims = hi - lo
    center = (lo + hi) / 2
    axis = int(np.argmin(dims))
    n = np.zeros(3, np.float32); n[axis] = 1.0
    if (center - model_center)[axis] < 0:
        n = -n
    up = np.array([0, 1, 0], np.float32) if axis != 1 else np.array([0, 0, -1], np.float32)
    # memes produits que Blender : le passage Y vertical (OBJ) -> Z vertical
    # (Blender) est une rotation, l'orientation des produits vectoriels est gardee
    right = np.cross(up, n); right /= np.linalg.norm(right)
    vv = np.cross(n, right); vv /= np.linalg.norm(vv)
    us = part.positions @ right; ws = part.positions @ vv
    return right, vv, (float(us.min()), float(us.max()), float(ws.min()), float(ws.max()))


def decal_basis(direction):
    """Reperes de l'autocollant en coordonnees OBJ (Y vertical) : normale vers
    l'observateur, droite et haut de l'image tels qu'il les voit."""
    n = np.asarray(direction, np.float32)
    n = n / max(float(np.linalg.norm(n)), 1e-9)
    up = np.array([0, 1, 0], np.float32) if abs(float(n[1])) < 0.95 else np.array([0, 0, -1], np.float32)
    right = np.cross(up, n); right /= np.linalg.norm(right)
    return n, right, np.cross(n, right)


def decal_params(points, decal, aspect):
    """(n, droite, haut, centre (u, v), taille (l, h), (cos, sin)) pour des points (k, 3)."""
    n, right, vv = decal_basis(decal["dir"])
    us, ws = points @ right, points @ vv
    u0, u1, w0, w1 = float(us.min()), float(us.max()), float(ws.min()), float(ws.max())
    cu = (u0 + u1) / 2 + decal["x"] * (u1 - u0) / 2
    cv = (w0 + w1) / 2 + decal["y"] * (w1 - w0) / 2
    width = max(decal["size"] * (u1 - u0), 1e-6)
    r = math.radians(decal["rot"])
    return n, right, vv, (cu, cv), (width, width * aspect), (math.cos(r), math.sin(r))


class Viewport(QOpenGLWidget):
    picked = Signal(str, str, bool)          # piece, materiau sous la souris, touche Ctrl

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.project = None
        self.selected = set()                 # pieces surlignees
        self.selected_mats = set()            # materiaux surlignes (toutes leurs faces)
        self._gpu = {}                        # nom -> (vao, nb sommets)
        self._textures = {}                   # chemin -> (texture, largeur, hauteur)
        self._decal_cache = {}
        self._pending_upload = False
        self.yaw, self.pitch, self.dist = 35.0, 12.0, 1.0
        self._drag = None
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(400, 300)

    # ------------------------------------------------------------ donnees
    def set_model(self, model, project):
        self.model, self.project = model, project
        lo, hi = model.bounds
        self.center = ((lo + hi) / 2).astype(np.float32)
        self.radius = float(np.linalg.norm(hi - lo)) / 2
        self.dist = self.radius * 2.6
        self._pending_upload = True
        self._decal_cache.clear()
        self.update()

    def view_direction(self):
        """Direction du centre vers la camera (reperes OBJ), calee sur un axe si proche."""
        _, eye = self._matrices()
        d = np.asarray(eye, np.float64) - self.center
        d /= np.linalg.norm(d)
        k = int(np.argmax(np.abs(d)))
        if abs(d[k]) >= math.cos(math.radians(12.0)):
            sign = 1.0 if d[k] > 0 else -1.0
            d = np.zeros(3); d[k] = sign
        return [round(float(c), 4) for c in d]

    def refresh(self):
        self.update()

    # ------------------------------------------------------------ OpenGL
    def initializeGL(self):
        self.prog = _program(VS, FS)
        self.pick = _program(VS, PICK_FS)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def _upload(self):
        for vao, _ in self._gpu.values():
            GL.glDeleteVertexArrays(1, [vao])
        self._gpu.clear()
        for part in self.model.parts:
            vao = GL.glGenVertexArrays(1); GL.glBindVertexArray(vao)
            attrs = [(0, part.positions, 3), (1, part.normals, 3)]
            if part.uvs is not None:
                attrs.append((2, part.uvs, 2))
            for loc, arr, width in attrs:
                buf = GL.glGenBuffers(1); GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buf)
                a = np.ascontiguousarray(arr, np.float32)
                GL.glBufferData(GL.GL_ARRAY_BUFFER, a.nbytes, a, GL.GL_STATIC_DRAW)
                GL.glEnableVertexAttribArray(loc)
                GL.glVertexAttribPointer(loc, width, GL.GL_FLOAT, False, 0, None)
            self._gpu[part.name] = (vao, len(part.positions))
        GL.glBindVertexArray(0)
        self._pending_upload = False

    def _texture(self, path):
        if path in self._textures:
            return self._textures[path]
        from PIL import Image
        try:
            im = Image.open(path).convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
        except OSError:
            return None
        data = np.asarray(im, np.uint8)
        t = GL.glGenTextures(1); GL.glBindTexture(GL.GL_TEXTURE_2D, t)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, im.width, im.height, 0, GL.GL_RGBA,
                        GL.GL_UNSIGNED_BYTE, data)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        for wrap in (GL.GL_TEXTURE_WRAP_S, GL.GL_TEXTURE_WRAP_T):
            GL.glTexParameteri(GL.GL_TEXTURE_2D, wrap, GL.GL_CLAMP_TO_EDGE)
        self._textures[path] = (t, im.width, im.height)
        return self._textures[path]

    def _matrices(self):
        yaw, pitch = math.radians(self.yaw), math.radians(self.pitch)
        eye = self.center + self.dist * np.array(
            [math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)], np.float32)
        w, h = max(self.width(), 1), max(self.height(), 1)
        proj = _perspective(30.0, w / h, self.radius * 0.05, self.radius * 20)
        return proj @ _look_at(eye.astype(np.float32), self.center), eye

    def paintGL(self):
        GL.glClearColor(24 / 255, 28 / 255, 33 / 255, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        if not self.model:
            return
        if self._pending_upload:
            self._upload()
        mvp, eye = self._matrices()
        p = self.prog
        GL.glUseProgram(p)
        loc = {k: GL.glGetUniformLocation(p, k) for k in
               ("mvp", "base", "metal", "rough", "alpha", "cam", "highlight", "hasTex", "tex",
                "texRight", "texUp", "texRange", "hasDecal", "dtex", "dRight", "dUp", "dDir",
                "dCenter", "dSize", "dRot", "hasSrc", "stex")}
        GL.glUniformMatrix4fv(loc["mvp"], 1, True, mvp)
        GL.glUniform3f(loc["cam"], *eye)
        glass = []
        # une plage = un materiau dans une piece : un modele non decoupe porte
        # tous ses materiaux dans une seule piece, chacun garde sa matiere
        for part in self.model.parts:
            for rng in part.ranges:
                spec = self.project.spec_for(part.name, rng[2])
                if spec["kind"] == "masque":
                    continue
                if spec["kind"] == "origine" and self._source_transparent(rng[2]):
                    glass.append((part, rng, spec)); continue
                if spec["kind"] == "verre":
                    glass.append((part, rng, spec)); continue
                self._draw(part, rng, spec, loc)
        GL.glEnable(GL.GL_BLEND); GL.glBlendFunc(GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glDepthMask(False)
        for part, rng, spec in glass:
            self._draw(part, rng, spec, loc)
        GL.glDepthMask(True); GL.glDisable(GL.GL_BLEND)

    def _source_transparent(self, material):
        info = self.model.source_materials.get(material)
        return bool(info) and (info["alpha_mode"] == "BLEND" or info["transmission"] > 0.1)

    def _draw(self, part, rng, spec, loc):
        k = spec["kind"]
        info = self.model.source_materials.get(rng[2]) if k == "origine" else None
        if info:                                   # materiau du glTF : facteurs, texture de couleur
            srgb = [c ** (1 / 2.2) for c in info["color"][:3]]
            GL.glUniform3f(loc["base"], *srgb)
            metal, rough = info["metal"], info["rough"]
            alpha = max(0.25, info["color"][3]) if self._source_transparent(rng[2]) else 1.0
            src = self._texture(info["color_tex"]) if info["color_tex"] else None
        else:
            GL.glUniform3f(loc["base"], *presets.display_color(spec))
            metal = 1.0 if k in ("chrome", "metal") else 0.0
            rough = spec.get("rough", 0.3 if k != "peinture" else presets.FINISH.get(spec.get("finish"), (0.3,))[0])
            alpha = 0.35 if k == "verre" else 1.0
            src = None
        GL.glUniform1i(loc["hasSrc"], 1 if (src and part.uvs is not None) else 0)
        GL.glUniform1i(loc["stex"], 2)
        if src:
            GL.glActiveTexture(GL.GL_TEXTURE2); GL.glBindTexture(GL.GL_TEXTURE_2D, src[0])
            GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glUniform1f(loc["metal"], metal)
        GL.glUniform1f(loc["rough"], float(rough))
        GL.glUniform1f(loc["alpha"], alpha)
        GL.glUniform1i(loc["highlight"], 1 if (part.name in self.selected or rng[2] in self.selected_mats) else 0)
        tex = None
        if k == "image" and spec.get("image"):
            tex = self._texture(self.project.resolve(spec["image"]))
        GL.glUniform1i(loc["hasTex"], 1 if tex else 0)
        GL.glUniform1i(loc["dtex"], 1)
        self._set_decal(part, rng, spec, loc)
        if tex:
            right, up, frame = decal_frame(part, self.center)   # pas 'rng' : c'est la plage dessinee
            GL.glActiveTexture(GL.GL_TEXTURE0); GL.glBindTexture(GL.GL_TEXTURE_2D, tex[0])
            GL.glUniform1i(loc["tex"], 0)
            GL.glUniform3f(loc["texRight"], *right); GL.glUniform3f(loc["texUp"], *up)
            GL.glUniform4f(loc["texRange"], *frame)
        vao, _ = self._gpu[part.name]
        GL.glBindVertexArray(vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, rng[0], rng[1])

    def _decal_zone(self, part, material):
        """Pieces de reference : la piece si elle porte sa propre matiere, sinon
        toutes les pieces du materiau qui n'ont pas de matiere propre."""
        if part.name in self.project.parts:
            return ("piece", part.name), [part]
        return ("materiau", material), [p for p in self.model.parts
                                        if material in p.materials and p.name not in self.project.parts]

    def _set_decal(self, part, rng, spec, loc):
        decal = presets.decal_of(spec)
        tex = self._texture(self.project.resolve(decal["image"])) if decal else None
        GL.glUniform1i(loc["hasDecal"], 1 if tex else 0)
        if not tex:
            return
        key, zone = self._decal_zone(part, rng[2])
        ck = (key, tuple(decal["dir"]), decal["size"], decal["x"], decal["y"], decal["rot"], tex[1], tex[2],
              tuple(p.name for p in zone))
        if ck not in self._decal_cache:
            pts = np.concatenate([p.positions for p in zone])
            self._decal_cache[ck] = decal_params(pts, decal, tex[2] / tex[1])
        n, right, vv, center, size, rot = self._decal_cache[ck]
        GL.glActiveTexture(GL.GL_TEXTURE1); GL.glBindTexture(GL.GL_TEXTURE_2D, tex[0])
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glUniform3f(loc["dRight"], *right); GL.glUniform3f(loc["dUp"], *vv); GL.glUniform3f(loc["dDir"], *n)
        GL.glUniform2f(loc["dCenter"], *center); GL.glUniform2f(loc["dSize"], *size)
        GL.glUniform2f(loc["dRot"], *rot)

    # ------------------------------------------------------------ selection
    def _pick(self, x, y):
        self.makeCurrent()
        ratio = self.devicePixelRatioF()
        w, h = int(self.width() * ratio), int(self.height() * ratio)
        fbo = GL.glGenFramebuffers(1); GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)
        col = GL.glGenRenderbuffers(1); GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, col)
        GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_RGBA8, w, h)
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_RENDERBUFFER, col)
        dep = GL.glGenRenderbuffers(1); GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, dep)
        GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH_COMPONENT24, w, h)
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER, dep)
        GL.glViewport(0, 0, w, h)
        GL.glClearColor(0, 0, 0, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        mvp, _ = self._matrices()
        GL.glUseProgram(self.pick)
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.pick, "mvp"), 1, True, mvp)
        cl = GL.glGetUniformLocation(self.pick, "idcol")
        slots = [(part, rng) for part in self.model.parts for rng in part.ranges]
        for i, (part, rng) in enumerate(slots, start=1):
            if self.project.spec_for(part.name, rng[2])["kind"] == "masque":
                continue
            GL.glUniform3f(cl, (i & 255) / 255, ((i >> 8) & 255) / 255, ((i >> 16) & 255) / 255)
            vao, _ = self._gpu[part.name]
            GL.glBindVertexArray(vao)
            GL.glDrawArrays(GL.GL_TRIANGLES, rng[0], rng[1])
        px = GL.glReadPixels(int(x * ratio), int(h - y * ratio - 1), 1, 1, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.defaultFramebufferObject())
        GL.glDeleteFramebuffers(1, [fbo]); GL.glDeleteRenderbuffers(2, [col, dep])
        self.doneCurrent()
        b = bytes(px)
        i = b[0] | (b[1] << 8) | (b[2] << 16)
        if 0 < i <= len(slots):
            part, rng = slots[i - 1]
            return part.name, rng[2]
        return None, None

    # ------------------------------------------------------------ souris
    def mousePressEvent(self, e):
        self._drag = (e.position().x(), e.position().y(), self.yaw, self.pitch, False)

    def mouseMoveEvent(self, e):
        if not self._drag:
            return
        x0, y0, yaw, pitch, _ = self._drag
        dx, dy = e.position().x() - x0, e.position().y() - y0
        if abs(dx) + abs(dy) > 3:
            self._drag = (x0, y0, yaw, pitch, True)
        self.yaw = yaw - dx * 0.4
        self.pitch = max(-5.0, min(85.0, pitch + dy * 0.3))
        self.update()

    def mouseReleaseEvent(self, e):
        moved = self._drag and self._drag[4]
        self._drag = None
        if not moved and self.model and e.button() == Qt.LeftButton:
            name, mat = self._pick(e.position().x(), e.position().y())
            self.picked.emit(name or "", mat or "", bool(e.modifiers() & Qt.ControlModifier))

    def wheelEvent(self, e):
        self.dist *= 0.9 ** (e.angleDelta().y() / 120)
        self.dist = max(self.radius * 0.6, min(self.radius * 8, self.dist))
        self.update()
