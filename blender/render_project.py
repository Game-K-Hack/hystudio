"""Rendu Cycles d'un projet Car Studio. S'execute DANS Blender.

    blender.exe -b -P render_project.py -- --project p.json --mode preview --turn 0 --out a.png
    blender.exe -b -P render_project.py -- --project p.json --mode full --views 720 --out dossier

Generalise i20view/render_cycles.py, dont il reprend les choix valides :
  - studio de softboxes solidaire de la camera, sur un pivot : les reflets
    restent coherents d'une vue a l'autre ;
  - verre architectural dont le reflet ne s'applique qu'aux faces avant (les
    vitres en doubles coques devenaient sinon des miroirs opaques) ;
  - ombre au sol par shadow catcher, fond transparent, AgX ;
  - 'full' rend l'orbite en UNE animation et pose un temoin RENDU_TERMINE.

Le cadrage vient de studio.camera s'il est donne, sinon de la taille du
modele. Une matiere 'image' est projetee de face sur la piece, calee sur ses
bords, lisible depuis l'exterieur du vehicule. Un autocollant (spec["decal"])
se pose par-dessus une matiere : meme calcul que la vue 3D (ui/viewport.py).
"""
import argparse, json, math, os, sys, time
import bpy
from mathutils import Vector

RES = (1600, 848)            # 2x la vue de l'autoradio (800x424), reduit ensuite
LOOK = "AgX - Medium High Contrast"


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--mode", choices=("preview", "full"), default="preview")
    ap.add_argument("--turn", type=float, default=0.0, help="apercu : rotation en degres (0 = 3/4 avant)")
    ap.add_argument("--views", type=int, default=0)
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--out", required=True)
    return ap.parse_args(argv)


def linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


SOURCES = {}                 # materiaux du glTF, lus dans le projet exporte

FINISH = {"brillant": (0.30, 1.00, 0.03), "satine": (0.42, 0.45, 0.18), "mat": (0.58, 0.00, 0.30)}


# ------------------------------------------------------------------ matieres

def principled(name, base, rough, metal=0.0, coat=0.0, coat_rough=0.03):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    return m


def glass(name, tint, reflet, ior=1.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    fres = nt.nodes.new("ShaderNodeFresnel")
    fres.inputs["IOR"].default_value = ior
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    front = nt.nodes.new("ShaderNodeMath"); front.operation = "SUBTRACT"
    front.inputs[0].default_value = 1.0
    only_front = nt.nodes.new("ShaderNodeMath"); only_front.operation = "MULTIPLY"
    gain = nt.nodes.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.use_clamp = True
    gain.inputs[1].default_value = reflet
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (*tint, 1.0)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.0
    # reflet sur les faces avant seulement : sous un angle rasant, le Fresnel
    # d'une coque interieure vue de dos donne une reflexion totale opaque
    nt.links.new(geo.outputs["Backfacing"], front.inputs[1])
    nt.links.new(fres.outputs["Fac"], only_front.inputs[0])
    nt.links.new(front.outputs["Value"], only_front.inputs[1])
    nt.links.new(only_front.outputs["Value"], gain.inputs[0])
    nt.links.new(gain.outputs["Value"], mix.inputs["Fac"])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[1])
    nt.links.new(gl.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


def image_material(name, spec, obj, model_center):
    """Image projetee sur la face exterieure de la piece.

    Axe de projection : la plus fine dimension de la piece, oriente vers
    l'exterieur du vehicule. La droite de l'image est prise vue de l'exterieur
    (vue de dos, l'axe gauche-droite est donc inverse), le haut suit la
    verticale. L'image est calee sur les bords de la piece."""
    ws = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector((min(w.x for w in ws), min(w.y for w in ws), min(w.z for w in ws)))
    hi = Vector((max(w.x for w in ws), max(w.y for w in ws), max(w.z for w in ws)))
    dims = hi - lo
    center = (lo + hi) / 2
    axis = min(range(3), key=lambda i: dims[i])
    n = Vector((0, 0, 0)); n[axis] = 1.0
    if (center - model_center)[axis] < 0:
        n = -n
    up = Vector((0, 0, 1)) if axis != 2 else Vector((0, 1, 0))
    right = up.cross(n).normalized()
    vv = n.cross(right).normalized()
    us = [w.dot(right) for w in ws]; vs = [w.dot(vv) for w in ws]

    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = spec["rough"]
    b.inputs["Coat Weight"].default_value = spec["coat"]
    b.inputs["Coat Roughness"].default_value = 0.08
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    du = nt.nodes.new("ShaderNodeVectorMath"); du.operation = "DOT_PRODUCT"
    dv = nt.nodes.new("ShaderNodeVectorMath"); dv.operation = "DOT_PRODUCT"
    du.inputs[1].default_value = right
    dv.inputs[1].default_value = vv
    mu = nt.nodes.new("ShaderNodeMapRange"); mv = nt.nodes.new("ShaderNodeMapRange")
    mu.inputs["From Min"].default_value, mu.inputs["From Max"].default_value = min(us), max(us)
    mv.inputs["From Min"].default_value, mv.inputs["From Max"].default_value = min(vs), max(vs)
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(spec["image"], check_existing=True)
    img.image.colorspace_settings.name = "sRGB"
    img.interpolation = "Cubic"
    img.extension = "EXTEND"
    nt.links.new(geo.outputs["Position"], du.inputs[0])
    nt.links.new(geo.outputs["Position"], dv.inputs[0])
    nt.links.new(du.outputs["Value"], mu.inputs["Value"])
    nt.links.new(dv.outputs["Value"], mv.inputs["Value"])
    nt.links.new(mu.outputs["Result"], comb.inputs["X"])
    nt.links.new(mv.outputs["Result"], comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], img.inputs["Vector"])
    nt.links.new(img.outputs["Color"], b.inputs["Base Color"])
    return m


def _world_points(objs):
    """Sommets en coordonnees monde (numpy) : l etendue doit etre celle de la vue 3D, au sommet pres."""
    import numpy as np
    chunks = []
    for o in objs:
        me = o.data
        co = np.empty(len(me.vertices) * 3, np.float64)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        mw = np.array(o.matrix_world)
        chunks.append(co @ mw[:3, :3].T + mw[:3, 3])
    return np.concatenate(chunks)


def add_decal(m, decal, zone_objs):
    """Autocollant par-dessus la matiere m (Principled BSDF).

    Reperes : ceux de ui/viewport.decal_params, passes de l'OBJ (Y vertical) a
    Blender (Z vertical) par (x, y, z) -> (x, -z, y), une rotation : les produits
    vectoriels, donc la droite et le haut de l'image, sont conserves."""
    import numpy as np
    dx, dy, dz = decal["dir"]
    n = np.array([dx, -dz, dy], np.float64); n /= np.linalg.norm(n)
    up = np.array([0, 0, 1.0]) if abs(n[2]) < 0.95 else np.array([0, 1.0, 0])
    right = np.cross(up, n); right /= np.linalg.norm(right)
    vv = np.cross(n, right)
    pts = _world_points(zone_objs)
    us, ws = pts @ right, pts @ vv
    u0, u1, w0, w1 = us.min(), us.max(), ws.min(), ws.max()
    cu = (u0 + u1) / 2 + decal["x"] * (u1 - u0) / 2
    cv = (w0 + w1) / 2 + decal["y"] * (w1 - w0) / 2

    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(decal["image"], check_existing=True)
    img.image.colorspace_settings.name = "sRGB"
    img.interpolation = "Cubic"
    img.extension = "CLIP"                           # hors de l'image : alpha nul
    iw, ih = img.image.size
    width = max(decal["size"] * (u1 - u0), 1e-6)
    height = width * (ih / iw if iw else 1.0)
    r = math.radians(decal["rot"])
    c, sn = math.cos(r), math.sin(r)

    geo = nt.nodes.new("ShaderNodeNewGeometry")

    def dot(vec_socket, v):
        d = nt.nodes.new("ShaderNodeVectorMath"); d.operation = "DOT_PRODUCT"
        nt.links.new(vec_socket, d.inputs[0]); d.inputs[1].default_value = tuple(float(x) for x in v)
        return d.outputs["Value"]

    def math_node(op, a, bval):
        k = nt.nodes.new("ShaderNodeMath"); k.operation = op
        for i, x in enumerate((a, bval)):
            if isinstance(x, (int, float)):
                k.inputs[i].default_value = float(x)
            else:
                nt.links.new(x, k.inputs[i])
        return k.outputs["Value"]

    du = math_node("SUBTRACT", dot(geo.outputs["Position"], right), cu)
    dv = math_node("SUBTRACT", dot(geo.outputs["Position"], vv), cv)
    a = math_node("ADD", math_node("ADD", math_node("MULTIPLY", du, c / width),
                                   math_node("MULTIPLY", dv, sn / width)), 0.5)
    bb = math_node("ADD", math_node("ADD", math_node("MULTIPLY", du, -sn / height),
                                    math_node("MULTIPLY", dv, c / height)), 0.5)
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(a, comb.inputs["X"]); nt.links.new(bb, comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], img.inputs["Vector"])

    facing = nt.nodes.new("ShaderNodeMapRange")      # seulement les faces tournees vers l'observateur
    facing.clamp = True
    facing.inputs["From Min"].default_value, facing.inputs["From Max"].default_value = 0.15, 0.35
    nt.links.new(dot(geo.outputs["Normal"], n), facing.inputs["Value"])
    fac = math_node("MULTIPLY", img.outputs["Alpha"], facing.outputs["Result"])

    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    sock = lambda coll, name, typ: next(x for x in coll if x.name == name and x.type == typ)
    nt.links.new(fac, sock(mix.inputs, "Factor", "VALUE"))
    sock(mix.inputs, "A", "RGBA").default_value = tuple(b.inputs["Base Color"].default_value)
    nt.links.new(img.outputs["Color"], sock(mix.inputs, "B", "RGBA"))
    nt.links.new(sock(mix.outputs, "Result", "RGBA"), b.inputs["Base Color"])
    metal = b.inputs["Metallic"].default_value
    if metal > 0:                                    # l'autocollant n'est pas metallique
        nt.links.new(math_node("MULTIPLY", math_node("SUBTRACT", 1.0, fac), metal), b.inputs["Metallic"])
    return m


def decal_spec(spec):
    d = spec.get("decal")
    if spec.get("kind") in ("peinture", "chrome", "metal", "plastique", "caoutchouc") and d and d.get("image"):
        return {"dir": [0.0, 0.0, 1.0], "size": 0.5, "x": 0.0, "y": 0.0, "rot": 0.0, **d}
    return None


def _tex_node(nt, path, non_color=False):
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path, check_existing=True)
    if non_color:
        t.image.colorspace_settings.name = "Non-Color"
    t.interpolation = "Cubic"
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"
    nt.links.new(uv.outputs["UV"], t.inputs["Vector"])
    return t


def gltf_material(name, info):
    """Materiau PBR d'un glTF, reconstruit tel que le fichier le decrit."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    out = nt.nodes["Material Output"]
    r, g, bl, a = info["color"]
    b.inputs["Base Color"].default_value = (r, g, bl, 1.0)
    b.inputs["Metallic"].default_value = info["metal"]
    b.inputs["Roughness"].default_value = info["rough"]
    b.inputs["IOR"].default_value = info.get("ior", 1.5)
    alpha_socket = None
    if info.get("color_tex"):
        t = _tex_node(nt, info["color_tex"])
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
        sock = lambda coll, nm, typ: next(x for x in coll if x.name == nm and x.type == typ)
        sock(mix.inputs, "Factor", "VALUE").default_value = 1.0
        sock(mix.inputs, "A", "RGBA").default_value = (r, g, bl, 1.0)
        nt.links.new(t.outputs["Color"], sock(mix.inputs, "B", "RGBA"))
        nt.links.new(sock(mix.outputs, "Result", "RGBA"), b.inputs["Base Color"])
        alpha_socket = t.outputs["Alpha"]
    if info.get("mr_tex"):                       # glTF : G = rugosite, B = metal
        t = _tex_node(nt, info["mr_tex"], non_color=True)
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(t.outputs["Color"], sep.inputs["Color"])
        for channel, sock_name, factor in (("Green", "Roughness", info["rough"]), ("Blue", "Metallic", info["metal"])):
            k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = factor
            nt.links.new(sep.outputs[channel], k.inputs[0])
            nt.links.new(k.outputs["Value"], b.inputs[sock_name])
    if info.get("normal_tex"):
        t = _tex_node(nt, info["normal_tex"], non_color=True)
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.uv_map = "UVMap"
        nm.inputs["Strength"].default_value = info.get("normal_scale", 1.0)
        nt.links.new(t.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    emissive = info.get("emissive", [0, 0, 0])
    if info.get("emissive_tex") or max(emissive) > 0:
        strength = info.get("emissive_strength", 1.0)
        b.inputs["Emission Color"].default_value = (*emissive, 1.0)
        b.inputs["Emission Strength"].default_value = strength
        if info.get("emissive_tex"):
            t = _tex_node(nt, info["emissive_tex"])
            k = nt.nodes.new("ShaderNodeMix"); k.data_type = "RGBA"; k.blend_type = "MULTIPLY"
            sock = lambda coll, nm_, typ: next(x for x in coll if x.name == nm_ and x.type == typ)
            sock(k.inputs, "Factor", "VALUE").default_value = 1.0
            sock(k.inputs, "A", "RGBA").default_value = (*emissive, 1.0)
            nt.links.new(t.outputs["Color"], sock(k.inputs, "B", "RGBA"))
            nt.links.new(sock(k.outputs, "Result", "RGBA"), b.inputs["Emission Color"])
    mode = info.get("alpha_mode", "OPAQUE")
    if info.get("transmission", 0) > 0.1:
        b.inputs["Transmission Weight"].default_value = info["transmission"]
    elif mode in ("BLEND", "MASK"):
        if alpha_socket is not None:
            k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = a
            nt.links.new(alpha_socket, k.inputs[0])
            alpha = k.outputs["Value"]
        else:
            alpha = None
            b.inputs["Alpha"].default_value = a
        if alpha is not None and mode == "MASK":   # decoupe nette au seuil du fichier
            k = nt.nodes.new("ShaderNodeMath"); k.operation = "GREATER_THAN"
            k.inputs[1].default_value = info.get("alpha_cutoff", 0.5)
            nt.links.new(alpha, k.inputs[0])
            alpha = k.outputs["Value"]
        if alpha is not None:
            nt.links.new(alpha, b.inputs["Alpha"])
    return m


def build_from_geometry(path, unit_scale, sc):
    """Objets Blender a partir de la geometrie lue par HyStudio (glTF).

    Un objet par piece ; noms et materiaux gardes en proprietes (hs_part,
    hs_mat) car Blender tronque les noms longs. Axes : (x, y, z) OBJ/glTF ->
    (x, -z, y) Blender ; UV : v glTF vers le bas -> 1 - v."""
    import numpy as np
    z = np.load(path, allow_pickle=False)
    names = [str(x) for x in z["names"]]
    offs, P, N, UV = z["offsets"], z["positions"], z["normals"], z["uvs"]
    rng, matnames = z["ranges"], [str(x) for x in z["matnames"]]
    mats = {}

    def mat_slot(name):
        if name not in mats:
            m = bpy.data.materials.new(f"hs_{len(mats):03d}")
            m["hs_mat"] = name
            mats[name] = m
        return mats[name]

    objs = []
    for i, name in enumerate(names):
        a, e = int(offs[i]), int(offs[i + 1])
        n_corners = e - a
        pos = P[a:e].astype(np.float64) * unit_scale
        co = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], 1).astype(np.float32)
        nor = N[a:e]
        nb = np.stack([nor[:, 0], -nor[:, 2], nor[:, 1]], 1).astype(np.float32)
        me = bpy.data.meshes.new(f"hs_{i:04d}")
        me.vertices.add(n_corners)
        me.vertices.foreach_set("co", co.reshape(-1))
        n_tri = n_corners // 3
        me.loops.add(n_corners)
        me.loops.foreach_set("vertex_index", np.arange(n_corners, dtype=np.int32))
        me.polygons.add(n_tri)
        me.polygons.foreach_set("loop_start", np.arange(0, n_corners, 3, dtype=np.int32))
        me.polygons.foreach_set("loop_total", np.full(n_tri, 3, np.int32))
        part_rng = [r for r in rng if int(r[0]) == i]
        index = np.zeros(n_tri, np.int32)
        for slot, r in enumerate(part_rng):
            me.materials.append(mat_slot(matnames[int(r[3])]))
            index[int(r[1]) // 3:(int(r[1]) + int(r[2])) // 3] = slot
        me.polygons.foreach_set("material_index", index)
        uvl = me.uv_layers.new(name="UVMap")
        uv = UV[a:e].astype(np.float32).copy()
        uv[:, 1] = 1.0 - uv[:, 1]
        uvl.data.foreach_set("uv", uv.reshape(-1))
        me.update()
        me.validate(clean_customdata=False)
        me.shade_smooth()
        me.normals_split_custom_set_from_vertices(nb)
        o = bpy.data.objects.new(f"hs_{i:04d}", me)
        o["hs_part"] = name
        sc.collection.objects.link(o)
        objs.append(o)
    return objs


def part_name(o):
    return o.get("hs_part", o.name)


def material_name(mat):
    """Materiau d'origine d'un emplacement : propriete hs_mat (glTF), sinon nom Blender sans suffixe .001."""
    if "hs_mat" in mat:
        return mat["hs_mat"]
    return mat.name.split(".")[0]


def build(spec, name):
    k = spec["kind"]
    if k == "peinture":
        r, coat, cr = FINISH[spec.get("finish", "brillant")]
        return principled(name, linear(spec["color"]), r, coat=coat, coat_rough=cr)
    if k == "chrome":
        v = spec["reflect"]
        return principled(name, (v, v, v * 1.02 if v < 0.9 else v), spec["rough"], metal=1.0)
    if k == "metal":
        return principled(name, linear(spec["color"]), spec["rough"], metal=1.0)
    if k in ("plastique", "caoutchouc"):
        return principled(name, linear(spec["color"]), spec["rough"])
    if k == "verre":
        t = spec["transmission"]
        return glass(name, tuple(c * t for c in linear(spec["color"])), spec["reflet"])
    if k == "origine":
        return gltf_material(name, SOURCES[spec["src"]])
    if k == "masque":
        # transparence totale, ombre comprise : masque UN materiau sans cacher
        # le reste de l'objet (un modele non decoupe n'a qu'un seul objet)
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        tr.inputs["Color"].default_value = (1, 1, 1, 1)
        nt.links.new(tr.outputs["BSDF"], out.inputs["Surface"])
        return m
    raise ValueError(f"matiere inconnue : {k}")


# ------------------------------------------------------------------ scene

def area(name, size, loc, energy, parent, target):
    d = bpy.data.lights.new(name, "AREA")
    d.shape = "RECTANGLE"
    d.size, d.size_y = size
    d.energy = energy
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.parent = parent
    return o


def build_scene(proj, a):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    studio = proj["studio"]

    if proj.get("geometry"):                         # glTF : geometrie lue par HyStudio
        meshes = build_from_geometry(proj["geometry"], proj.get("unit_scale", 1.0), sc)
    else:
        bpy.ops.wm.obj_import(filepath=proj["model"], global_scale=proj.get("unit_scale", 1.0),
                              forward_axis="NEGATIVE_Z", up_axis="Y")
        meshes = [o for o in sc.objects if o.type == "MESH"]
    sources = proj.get("source_materials", {})
    SOURCES.update(sources)

    # recentrage : axe vertical au centre du vehicule, roues au sol
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    shift = Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))
    for o in meshes:
        o.location += shift
    bpy.context.view_layer.update()
    size = hi - lo
    center = Vector((0, 0, size.z / 2))

    # matieres : par materiau d'origine, puis par piece
    cache = {}

    def mat_for(spec, tag):
        key = json.dumps(spec, sort_keys=True)
        if key not in cache:
            cache[key] = build(spec, f"cs_{tag}")
        return cache[key]

    # materiaux d'origine releves AVANT de remplacer les matieres : sinon les objets
    # deja traites sortent de la zone et les suivants recoivent un autocollant reduit
    originals = {x.name: {material_name(sl.material) for sl in x.material_slots if sl.material}
                 for x in meshes}

    def zone_for(material):
        """Objets de reference d'un autocollant pose sur un materiau (comme la vue 3D)."""
        return [x for x in meshes if part_name(x) not in proj["parts"] and material in originals[x.name]]

    for o in meshes:
        pspec = proj["parts"].get(part_name(o))
        if pspec and pspec["kind"] == "masque":
            o.hide_render = True
            continue
        if pspec and pspec["kind"] == "image":
            m = image_material(f"cs_img_{o.name}", pspec, o, center)
            for slot in o.material_slots:
                slot.material = m
            continue
        for slot in o.material_slots:
            if not slot.material:
                continue
            orig = material_name(slot.material)
            spec = pspec or proj["materials"].get(orig)
            if spec is None:
                spec = {"kind": "origine"} if orig in sources else None
            if spec is None:
                continue
            if spec["kind"] == "origine":
                if orig in sources:
                    slot.material = mat_for({"kind": "origine", "src": orig}, orig)
                continue
            if spec["kind"] == "image":
                slot.material = image_material(f"cs_img_{o.name}", spec, o, center)
            elif decal_spec(spec):
                # materiau propre a l'objet : le reseau de l'autocollant depend de sa zone
                zone = [o] if pspec else zone_for(orig)
                slot.material = add_decal(build(spec, f"cs_dec_{o.name}_{orig}"), decal_spec(spec), zone)
            else:
                slot.material = mat_for(spec, orig)

    bpy.ops.mesh.primitive_plane_add(size=max(40.0, size.length * 8), location=(0, 0, 0))
    bpy.context.object.is_shadow_catcher = True

    cam_cfg = studio.get("camera") or {}
    length = max(size.x, size.y)
    dist = cam_cfg.get("dist", 1.5633 * length)
    target_z = cam_cfg.get("target_z", 0.3912 * size.z)
    elev = math.radians(cam_cfg.get("elev", 11.0))
    fov = cam_cfg.get("fov", 24.0)
    az0 = cam_cfg.get("az0", 35.0)

    rig = bpy.data.objects.new("rig", None)
    sc.collection.objects.link(rig)
    target = bpy.data.objects.new("cible", None)
    sc.collection.objects.link(target)
    target.location = (0, 0, target_z)
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = "VERTICAL"
    cd.angle_y = math.radians(fov)
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    cam.location = (0, -dist * math.cos(elev), target_z + dist * math.sin(elev))
    cam.parent = rig
    c = cam.constraints.new("TRACK_TO")
    c.target = target; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    sc.camera = cam

    # studio calibre sur une voiture de ~4 m, mis a l'echelle du modele
    k = length / 4.03
    tgt = (0, 0, 0.7 * k)
    area("plafond", (10.0 * k, 6.0 * k), (0, -0.5 * k, 5.2 * k), 420 * k * k, rig, tgt)
    area("bande_gauche", (5.5 * k, 0.9 * k), (-5.0 * k, -0.8 * k, 1.6 * k), 140 * k * k, rig, tgt)
    area("bande_droite", (5.5 * k, 0.9 * k), (5.0 * k, -0.8 * k, 1.6 * k), 140 * k * k, rig, tgt)
    area("face", (4.0 * k, 2.0 * k), (0.8 * k, -7.5 * k, 3.2 * k), 110 * k * k, rig, tgt)
    area("contre", (6.0 * k, 1.2 * k), (0, 6.5 * k, 2.4 * k), 120 * k * k, rig, tgt)

    if studio.get("cabin_light", 0) > 0:
        ld = bpy.data.lights.new("habitacle", "POINT")
        ld.shadow_soft_size = 0.35 * k
        # meme loi que les softboxes : la puissance suit la surface a eclairer,
        # sinon un vehicule plus grand (ou mal mis a l'echelle) reste sombre
        ld.energy = studio["cabin_light"] * k * k
        lo_ = bpy.data.objects.new("habitacle", ld)
        sc.collection.objects.link(lo_)
        lo_.location = (0, 0.1 * k, 0.64 * size.z)
        lo_.visible_camera = lo_.visible_glossy = lo_.visible_transmission = False

    w = bpy.data.worlds.new("studio")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.09, 0.095, 0.10, 1)
    sc.world = w

    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            if any(d.type == dev_type for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == dev_type
                sc.cycles.device = "GPU"
                break
        except TypeError:
            continue
    else:
        sc.cycles.device = "CPU"
    print("PERIPHERIQUE", sc.cycles.device, prefs.compute_device_type, flush=True)
    sc.cycles.samples = a.samples or studio.get("samples", 96)
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPTIX" if prefs.compute_device_type == "OPTIX" else "OPENIMAGEDENOISE"
    sc.cycles.transparent_max_bounces = 32
    sc.cycles.max_bounces = 8
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = LOOK
    sc.view_settings.exposure = studio.get("exposure", 0.0)
    return sc, rig, az0


def main():
    a = args()
    with open(a.project, encoding="utf-8") as f:
        proj = json.load(f)
    sc, rig, az0 = build_scene(proj, a)

    if a.mode == "preview":
        rig.rotation_euler = (0, 0, math.radians(az0 + a.turn))
        sc.render.filepath = a.out
        bpy.ops.render.render(write_still=True)
        print("APERCU", a.out, flush=True)
        return

    views = a.views or proj["studio"].get("views", 360)
    os.makedirs(a.out, exist_ok=True)
    sc.render.use_persistent_data = True
    sc.render.image_settings.compression = 0
    sc.frame_start, sc.frame_end = 0, views - 1
    rig.animation_data_create()
    act = bpy.data.actions.new("orbite")
    rig.animation_data.action = act
    fc = act.fcurves.new("rotation_euler", index=2)
    fc.keyframe_points.add(views)
    for i, kp in enumerate(fc.keyframe_points):
        kp.co = (i, math.radians(az0 + 360.0 * i / views))
        kp.interpolation = "CONSTANT"
    digits = max(3, len(str(views - 1)))
    sc.render.filepath = os.path.join(a.out, "v_" + "#" * digits)
    t0 = time.time()

    def written(scene, *_):
        done = scene.frame_current + 1
        el = time.time() - t0
        print(f"VUE {scene.frame_current} ({done}/{views}) {el:.0f}s", flush=True)

    bpy.app.handlers.render_write.append(written)
    bpy.ops.render.render(animation=True)
    open(os.path.join(a.out, "RENDU_TERMINE"), "w").write("ok")


main()
