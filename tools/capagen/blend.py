"""
Path-traced backend for the cover scenes: the same meshes as gl.py (blocks, plants, water, the mod's dinosaurs), rendered
with Blender Cycles through the `bpy` module (pip install bpy). Real sun shadows, soft sky light, ambient occlusion,
light bouncing between blocks, volumetric fog with light shafts and true water reflection/refraction.

Coordinates: our scenes are y-up (Minecraft); Blender is z-up, so (x, y, z) -> (x, -z, y).
"""
import math
import os
import tempfile

import bpy
import numpy as np
from mathutils import Vector
from PIL import Image


def to_b(p):
    return Vector((p[0], -p[2], p[1]))


def _reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _image(img, name, tmp):
    path = os.path.join(tmp, name + ".png")
    img.convert("RGBA").save(path)
    im = bpy.data.images.load(path)
    im.alpha_mode = "STRAIGHT"
    return im


def _material(name, image, tint=(1, 1, 1), rough=0.85):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], mul.inputs["A"])
    mul.inputs["B"].default_value = (*tint, 1)
    nt.links.new(mul.outputs["Result"], bsdf.inputs["Base Color"])
    # cut-out alpha like Minecraft (leaves, plants): hard edge, no half-transparent fringes
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 0.5
    nt.links.new(tex.outputs["Alpha"], gt.inputs[0])
    nt.links.new(gt.outputs[0], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def _water_material(look):
    m = bpy.data.materials.new("water")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
    bsdf.inputs["Roughness"].default_value = 0.03
    bsdf.inputs["IOR"].default_value = 1.33
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    # small ripples so the reflection is not a perfect mirror
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.6
    noise.inputs["Detail"].default_value = 3
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    d = look["water_deep"]
    vol.inputs["Color"].default_value = (min(1, d[0] * 4), min(1, d[1] * 4), min(1, d[2] * 4), 1)
    vol.inputs["Density"].default_value = look.get("water_density", 0.35)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return m


def _mesh(name, verts, mat):
    """verts: (N, 9) float32 from gl.quad_verts (6 verts per quad: corners 0,1,2,0,2,3)."""
    v = np.asarray(verts, np.float32).reshape(-1, 6, 9)
    q = v[:, [0, 1, 2, 5], :]  # the 4 corners of each quad
    pos = q[..., :3].reshape(-1, 3)
    pos = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], 1)
    uv = q[..., 3:5].reshape(-1, 2).copy()
    uv[:, 1] = 1 - uv[:, 1]
    nq = q.shape[0]
    me = bpy.data.meshes.new(name)
    me.vertices.add(nq * 4)
    me.vertices.foreach_set("co", pos.ravel())
    me.loops.add(nq * 4)
    me.loops.foreach_set("vertex_index", np.arange(nq * 4, dtype=np.int32))
    me.polygons.add(nq)
    me.polygons.foreach_set("loop_start", np.arange(0, nq * 4, 4, dtype=np.int32))
    me.update()
    me.uv_layers.new(name="uv").data.foreach_set("uv", uv.ravel())
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _sky(look, sun_b):
    """The same art-directed sky as gl.py (horizon / mid / top gradient, sun glow, a few clouds), as world nodes."""
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    nt = w.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    L = nt.links.new
    out = N("ShaderNodeOutputWorld")
    co = N("ShaderNodeTexCoord")
    nrm = N("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    L(co.outputs["Generated"], nrm.inputs[0])
    sep = N("ShaderNodeSeparateXYZ")
    L(nrm.outputs["Vector"], sep.inputs[0])

    def ramp(stops):
        r = N("ShaderNodeValToRGB")
        el = r.color_ramp.elements
        el[0].position, el[0].color = stops[0][0], (*stops[0][1], 1)
        el[1].position, el[1].color = stops[-1][0], (*stops[-1][1], 1)
        for p, c in stops[1:-1]:
            e = el.new(p)
            e.color = (*c, 1)
        return r

    # elevation -> colour; map e in [-1, 1] to [0, 1]
    mr = N("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -1
    mr.inputs["From Max"].default_value = 1
    L(sep.outputs["Z"], mr.inputs["Value"])
    hor, mid, top = look["hor"], look["mid"], look["top"]
    below = tuple(c * 0.92 for c in hor)
    r = ramp([(0.0, below), (0.5, hor), (0.5 + 0.09, mid), (0.5 + 0.375, top), (1.0, top)])
    L(mr.outputs["Result"], r.inputs["Fac"])
    # sun glow
    dot = N("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    L(nrm.outputs["Vector"], dot.inputs[0])
    dot.inputs[1].default_value = tuple(sun_b)
    mx = N("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    mx.inputs[1].default_value = 0
    L(dot.outputs["Value"], mx.inputs[0])

    def powk(k, amt):
        p = N("ShaderNodeMath")
        p.operation = "POWER"
        L(mx.outputs[0], p.inputs[0])
        p.inputs[1].default_value = k
        m = N("ShaderNodeMath")
        m.operation = "MULTIPLY"
        L(p.outputs[0], m.inputs[0])
        m.inputs[1].default_value = amt
        return m

    gg = look.get("glow_gain", 1.0)
    g1, g2 = powk(8, 0.55 * gg), powk(64, 0.8 * gg)
    gs = N("ShaderNodeMath")
    gs.operation = "ADD"
    L(g1.outputs[0], gs.inputs[0])
    L(g2.outputs[0], gs.inputs[1])
    add = N("ShaderNodeMix")
    add.data_type = "RGBA"
    add.blend_type = "ADD"
    L(gs.outputs[0], add.inputs["Factor"])
    L(r.outputs["Color"], add.inputs["A"])
    add.inputs["B"].default_value = (*look["glow"], 1)
    color = add.outputs["Result"]
    if look.get("clouds", 0) > 0:
        # clouds: noise on the direction projected onto a dome, only above the horizon
        div = N("ShaderNodeVectorMath")
        div.operation = "DIVIDE"
        L(nrm.outputs["Vector"], div.inputs[0])
        ez = N("ShaderNodeMath")
        ez.operation = "ADD"
        L(sep.outputs["Z"], ez.inputs[0])
        ez.inputs[1].default_value = 0.08
        cz = N("ShaderNodeCombineXYZ")
        for k in "XYZ":
            L(ez.outputs[0], cz.inputs[k])
        L(cz.outputs["Vector"], div.inputs[1])
        noise = N("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 1.4
        noise.inputs["Detail"].default_value = 6
        noise.noise_dimensions = "4D"
        w_in = next((s for s in noise.inputs if s.name == "W"), None)
        if w_in is not None:
            w_in.default_value = look.get("cloud_shift", 0.0)
        L(div.outputs["Vector"], noise.inputs["Vector"])
        cr = N("ShaderNodeMapRange")
        cr.inputs["From Min"].default_value = 0.52
        cr.inputs["From Max"].default_value = 0.72
        L(noise.outputs["Fac"], cr.inputs["Value"])
        hz = N("ShaderNodeMapRange")
        hz.inputs["From Min"].default_value = 0.02
        hz.inputs["From Max"].default_value = 0.25
        L(sep.outputs["Z"], hz.inputs["Value"])
        m1 = N("ShaderNodeMath")
        m1.operation = "MULTIPLY"
        L(cr.outputs["Result"], m1.inputs[0])
        L(hz.outputs["Result"], m1.inputs[1])
        m2 = N("ShaderNodeMath")
        m2.operation = "MULTIPLY"
        L(m1.outputs[0], m2.inputs[0])
        m2.inputs[1].default_value = look["clouds"]
        cc = tuple(min(1.0, look["glow"][i] * 0.9 + look["hor"][i] * 0.35) for i in range(3))
        mixc = N("ShaderNodeMix")
        mixc.data_type = "RGBA"
        L(m2.outputs[0], mixc.inputs["Factor"])
        L(color, mixc.inputs["A"])
        mixc.inputs["B"].default_value = (*cc, 1)
        color = mixc.outputs["Result"]
    bg = N("ShaderNodeBackground")
    L(color, bg.inputs["Color"])
    bg.inputs["Strength"].default_value = look.get("sky_strength", 1.0)
    L(bg.outputs["Background"], out.inputs["Surface"])


def _fog(look, centre, size):
    """A box of fog around the scene: thicker near the ground, scatters sunlight forward (light shafts)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    box = bpy.context.active_object
    box.scale = size
    m = bpy.data.materials.new("fog")
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    L = nt.links.new
    out = N("ShaderNodeOutputMaterial")
    vol = N("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (*look["fog_col"], 1)
    vol.inputs["Anisotropy"].default_value = look.get("fog_aniso", 0.55)
    geo = N("ShaderNodeNewGeometry")
    sep = N("ShaderNodeSeparateXYZ")
    L(geo.outputs["Position"], sep.inputs[0])
    sub = N("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    L(sep.outputs["Z"], sub.inputs[0])
    sub.inputs[1].default_value = look.get("fog_height", 64)
    mx = N("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    L(sub.outputs[0], mx.inputs[0])
    mx.inputs[1].default_value = 0
    mul = N("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L(mx.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = -0.06
    ex = N("ShaderNodeMath")
    ex.operation = "EXPONENT"
    L(mul.outputs[0], ex.inputs[0])
    ma = N("ShaderNodeMath")
    ma.operation = "MULTIPLY_ADD"
    L(ex.outputs[0], ma.inputs[0])
    ma.inputs[1].default_value = 0.65 * look["fog_density"] * look.get("fog_scale", 1.0)
    ma.inputs[2].default_value = 0.35 * look["fog_density"] * look.get("fog_scale", 1.0)
    L(ma.outputs[0], vol.inputs["Density"])
    L(vol.outputs["Volume"], out.inputs["Volume"])
    box.data.materials.append(m)
    box.visible_shadow = False


COLOR_KEYS = ("top", "mid", "hor", "glow", "sun_col", "fog_col", "water_deep")


def linear(look):
    """The looks are written as display (sRGB) colours for the OpenGL preview; Cycles works in linear light."""
    out = dict(look)
    for k in COLOR_KEYS:
        if k in out:
            out[k] = tuple(float(c) ** 2.2 if c <= 1 else float(c) for c in out[k])
    return out


def render(meshes, cam, target, fov, sun_dir, look, W, H, samples=96, focus=None, fstop=4.0, fog_box=None,
           sun_strength=None, exposure=0.0, out=None, transparent=False):
    """Render with Cycles; returns a PIL RGB image (RGBA with the sky left out when transparent)."""
    _reset()
    look = linear(look)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.volume_bounces = 1
    sc.cycles.transmission_bounces = 4
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.volume_step_rate = float(os.environ.get("VSTEP", 2.0))
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = look.get("agx", "AgX - Punchy")
    except TypeError:
        pass
    sc.view_settings.exposure = exposure
    tmp = tempfile.mkdtemp(prefix="terrassic_blend_")
    sun_b = to_b(sun_dir).normalized()
    images = {}
    for i, m in enumerate(meshes):
        if m.water:
            _mesh(f"water{i}", m.verts, _water_material(look))
            continue
        key = id(m.texture)
        if key not in images:
            images[key] = _image(m.texture, f"tex{i}", tmp)
        _mesh(f"m{i}", m.verts, _material(f"mat{i}", images[key], m.tint))
    _sky(look, sun_b)
    # sun: soft shadow (the sun is ~0.5 degrees, a bit wider reads better at block scale)
    ld = bpy.data.lights.new("sun", "SUN")
    ld.energy = sun_strength if sun_strength is not None else look.get("sun_strength", 3.5)
    ld.color = tuple(min(1.0, c / max(look["sun_col"])) for c in look["sun_col"])
    ld.angle = math.radians(look.get("sun_angle", 1.5))
    lo = bpy.data.objects.new("sun", ld)
    sc.collection.objects.link(lo)
    lo.rotation_euler = (-sun_b).to_track_quat("-Z", "Y").to_euler()
    if look.get("fill"):
        # soft fill from the camera side (the sky behind the photographer), no shadows: keeps a backlit subject readable
        fd = bpy.data.lights.new("fill", "SUN")
        fd.energy = look["fill"]
        fd.color = tuple(min(1.0, c / max(look["mid"])) for c in look["mid"])
        fd.angle = math.radians(30)
        fd.use_shadow = False
        fo = bpy.data.objects.new("fill", fd)
        sc.collection.objects.link(fo)
        d = (to_b(cam) - to_b(target)).normalized() + Vector((0, 0, 0.6))
        fo.rotation_euler = (-d.normalized()).to_track_quat("-Z", "Y").to_euler()
    if fog_box:
        c, s = fog_box
        _fog(look, to_b(c), (s[0], s[2], s[1]))
    # camera
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = "VERTICAL"
    cd.angle = math.radians(fov)
    cd.clip_start, cd.clip_end = 0.1, 4000
    if focus:
        cd.dof.use_dof = True
        cd.dof.focus_distance = focus
        cd.dof.aperture_fstop = fstop
    co = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(co)
    co.location = to_b(cam)
    co.rotation_euler = (to_b(target) - to_b(cam)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    path = out or os.path.join(tmp, "render.png")
    sc.render.filepath = path
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    bpy.ops.render.render(write_still=True)
    return Image.open(path).convert("RGBA" if transparent else "RGB")
