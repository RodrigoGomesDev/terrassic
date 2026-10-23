"""
Drives a real (headless) Blockbench to build, validate and export the models.

Requires a local Blockbench web build served over HTTP (see README in this
folder).  Using Blockbench itself guarantees the .bbmodel, the GeckoLib/Bedrock
geometry and the animation files are exactly what the editor would produce.
"""
import base64
import json
from playwright.async_api import async_playwright

BUILD_JS = r"""
(spec) => {
  newProject(Formats.bedrock);
  if (Modes.selected && Modes.selected.id !== 'edit') Modes.options.edit.select();
  Project.name = spec.id;
  Project.geometry_name = spec.id;
  Project.texture_width = spec.texture_width;
  Project.texture_height = spec.texture_height;
  const groups = {};
  for (const b of spec.bones) {
    const g = new Group({name: b.name, origin: b.origin, rotation: b.rotation});
    if (b.parent) g.addTo(groups[b.parent]);
    g.init();
    groups[b.name] = g;
  }
  for (const c of spec.cubes) {
    const cube = new Cube({name: c.name, from: c.from, to: c.to, origin: c.origin, rotation: c.rotation,
                           inflate: c.inflate, uv_offset: c.uv_offset, box_uv: true});
    cube.addTo(groups[c.bone]).init();
  }
  Canvas.updateAll();
  window.__groups = groups;
  const dump = [];
  for (const cube of Cube.all) {
    const mesh = cube.mesh; mesh.updateMatrixWorld(true);
    const pos = mesh.geometry.attributes.position, uv = mesh.geometry.attributes.uv;
    const verts = [];
    for (let i = 0; i < pos.count; i++) {
      const v = new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i));
      const w = v.clone().applyMatrix4(mesh.matrixWorld);
      verts.push({l: [v.x, v.y, v.z], w: [w.x, w.y, w.z],
                  uv: [uv.getX(i) * Project.texture_width, (1 - uv.getY(i)) * Project.texture_height]});
    }
    dump.push({name: cube.name, from: cube.from, to: cube.to, order: Canvas.face_order, verts});
  }
  return dump;
}
"""

FINISH_JS = r"""
(args) => {
  const [spec, dataurl, extra] = args;
  const tex = new Texture({name: spec.id + '_male.png'}).fromDataURL(dataurl).add(false);
  for (const c of Cube.all) { for (const f in c.faces) c.faces[f].texture = tex.uuid; }
  // extra textures (female variant) are stored in the project for editing but not applied
  for (const [name, url] of (extra || [])) { new Texture({name}).fromDataURL(url).add(false); }
  // bedrock is a single-texture format: the "default" texture is the one shown
  if (tex.setAsDefaultTexture) tex.setAsDefaultTexture();
  Canvas.updateAll();
  const groups = window.__groups;
  for (const a of spec.animations) {
    const anim = new Animation({name: a.name, loop: a.loop, length: a.length, snapping: 20}).add(false);
    for (const bone in a.bones) {
      const g = groups[bone];
      if (!g) throw new Error('animation ' + a.name + ' references unknown bone ' + bone);
      const ba = anim.getBoneAnimator(g);
      for (const channel of ['rotation', 'position', 'scale']) {
        const ks = a.bones[bone][channel];
        if (!ks) continue;
        for (const k of ks) {
          ba.addKeyframe({channel, time: k[0], data_points: [{x: k[1], y: k[2], z: k[3]}],
                          interpolation: a.interp || 'catmullrom'});
        }
      }
    }
  }
  return {
    bbmodel: Codecs.project.compile(),
    geo: Codecs.bedrock.compile(),
    anim: JSON.stringify(AnimationCodec.codecs.bedrock.compileFile(Animation.all)),
  };
}
"""

SHOT_JS = r"""
(args) => {
  const [cam, anim_name, time] = args;
  const p = Preview.selected;
  if (anim_name) {
    if (Modes.selected.id !== 'animate') Modes.options.animate.select();
    const a = Animation.all.find(a => a.name === anim_name);
    a.select();
    Timeline.setTime(time);
    Animator.preview();
  } else {
    if (Modes.selected.id !== 'edit') Modes.options.edit.select();
  }
  p.loadAnglePreset({position: cam.position, target: cam.target, projection: cam.ortho ? 'orthographic' : 'perspective', zoom: cam.zoom || 1});
  if (cam.fov) { p.camera.fov = cam.fov; p.camera.updateProjectionMatrix(); }
  p.controls.target.fromArray(cam.target); p.camera.lookAt(p.controls.target); if (p.controls.update) p.controls.update();
  let url;
  Canvas.withoutGizmos(() => { p.render(); url = p.canvas.toDataURL('image/png'); });
  return url;
}
"""


class Blockbench:
    def __init__(self, url="http://localhost:8123/index.html"):
        self.url = url
        self.errors = []

    async def __aenter__(self):
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        self.page = await self.browser.new_page(viewport={"width": 1500, "height": 1000})
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        await self.page.goto(self.url)
        await self.page.wait_for_function("typeof Codecs !== 'undefined' && typeof newProject === 'function'", timeout=60000)
        await self.page.wait_for_timeout(1500)
        await self.page.evaluate("() => { try { settings.default_keyframe_interpolation.value = 'catmullrom'; } catch(e) {} }")
        return self

    async def __aexit__(self, *a):
        await self.browser.close()
        await self._pw.stop()

    async def build(self, spec):
        return await self.page.evaluate(BUILD_JS, spec)

    async def finish(self, spec, png_bytes, extra=None):
        url = "data:image/png;base64," + base64.b64encode(png_bytes).decode()
        ex = [[n, "data:image/png;base64," + base64.b64encode(b).decode()] for n, b in (extra or [])]
        await self.page.evaluate(FINISH_JS, [spec, url, ex])
        await self.page.wait_for_timeout(400)
        return await self.page.evaluate("() => ({bbmodel: Codecs.project.compile(), geo: Codecs.bedrock.compile(), anim: JSON.stringify(AnimationCodec.codecs.bedrock.compileFile(Animation.all))})")

    async def set_texture(self, index):
        """Apply the n-th project texture to every cube (used to render the female variant)."""
        await self.page.evaluate("""(i) => { const t = Texture.all[i]; t.setAsDefaultTexture(); t.select(); Canvas.updateAllFaces(); Canvas.updateAll(); }""", index)
        await self.page.wait_for_timeout(150)

    async def set_visible(self, bone, visible):
        await self.page.evaluate("""([n, v]) => { const g = Group.all.find(g => g.name === n); if (g) { g.visibility = v; g.forEachChild(c => { c.visibility = v; }); Canvas.updateVisibility(); } }""", [bone, visible])

    async def shot(self, cam, anim=None, time=0.0):
        url = await self.page.evaluate(SHOT_JS, [cam, anim, time])
        return base64.b64decode(url.split(",", 1)[1])
