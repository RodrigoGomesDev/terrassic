"""
Small OpenGL scene renderer for the cover art (moderngl, headless: run under `xvfb-run -a`).

Draws textured block meshes (the voxel scenery from voxels.py and the mod's dinosaur models) with a sun that casts
real shadows, sky/ground ambient light, distance + height fog, a gradient sky with sun glow, a water surface, and
returns colour and depth so the caller can add depth of field. Same look for scenery and dinosaurs, so they belong
together.
"""
import math

import moderngl
import numpy as np
from PIL import Image

VS = """
#version 330
uniform mat4 vp; uniform mat4 lvp;
in vec3 in_pos; in vec2 in_uv; in vec3 in_nrm; in float in_shade;
out vec2 uv; out vec3 nrm; out vec3 wpos; out vec4 lpos; out float shade;
void main(){ uv=in_uv; nrm=in_nrm; wpos=in_pos; shade=in_shade; lpos=lvp*vec4(in_pos,1.0); gl_Position=vp*vec4(in_pos,1.0); }
"""
FS = """
#version 330
uniform sampler2D tex; uniform sampler2D shadow;
uniform vec3 sun_dir; uniform vec3 sun_col; uniform vec3 sky_amb; uniform vec3 gnd_amb;
uniform vec3 cam; uniform vec3 fog_col; uniform float fog_density; uniform float fog_height; uniform vec3 tint;
uniform float shadow_px; uniform float clip_y; uniform float rim;
in vec2 uv; in vec3 nrm; in vec3 wpos; in vec4 lpos; in float shade;
out vec4 f;
float sh(){
  vec3 p=lpos.xyz/lpos.w*0.5+0.5; if(p.x<0.||p.x>1.||p.y<0.||p.y>1.) return 1.0;
  float s=0.; float b=0.0015;
  for(int x=-1;x<=1;x++) for(int y=-1;y<=1;y++){ float d=texture(shadow,p.xy+vec2(x,y)*shadow_px).r; s+= (p.z-b>d)?0.:1.; }
  return s/9.;
}
void main(){
  if(wpos.y<clip_y) discard;
  vec4 t=texture(tex,uv); if(t.a<0.5) discard;
  vec3 n=normalize(nrm);
  float ndl=max(dot(n,sun_dir),0.);
  float hemi=n.y*0.5+0.5;
  vec3 amb=mix(gnd_amb,sky_amb,hemi);
  vec3 c=t.rgb*tint*(amb*shade + sun_col*ndl*sh());
  vec3 v=normalize(cam-wpos);
  c+=t.rgb*sun_col*rim*pow(1.-abs(dot(n,v)),3.)*pow(max(dot(-v,sun_dir),0.),2.)*(0.5+0.5*max(dot(n,sun_dir)+0.3,0.));
  float d=length(wpos-cam);
  float fh=exp(-max(wpos.y-fog_height,0.)*0.06);
  float fog=1.-exp(-d*fog_density*(0.35+0.65*fh));
  f=vec4(mix(c,fog_col,clamp(fog,0.,1.)),1.);
}
"""
SVS = """
#version 330
uniform mat4 lvp; in vec3 in_pos; in vec2 in_uv; out vec2 uv;
void main(){ uv=in_uv; gl_Position=lvp*vec4(in_pos,1.0); }
"""
SFS = """
#version 330
uniform sampler2D tex; in vec2 uv; out vec4 f;
void main(){ if(texture(tex,uv).a<0.5) discard; f=vec4(1); }
"""
SKY_VS = """
#version 330
in vec2 in_xy; out vec2 xy; void main(){ xy=in_xy; gl_Position=vec4(in_xy,0.9999,1.); }
"""
SKY_FS = """
#version 330
uniform mat4 inv_vp; uniform vec3 sun_dir; uniform vec3 top; uniform vec3 mid; uniform vec3 hor; uniform vec3 glow;
uniform float sun_size; uniform float clouds; uniform float time;
in vec2 xy; out vec4 f;
float h(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float n2(vec2 p){ vec2 i=floor(p), u=fract(p); u=u*u*(3.-2.*u);
  return mix(mix(h(i),h(i+vec2(1,0)),u.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),u.x),u.y); }
float fbm(vec2 p){ float s=0., a=.5; for(int i=0;i<5;i++){ s+=a*n2(p); p*=2.03; a*=.5; } return s; }
void main(){
  vec4 a=inv_vp*vec4(xy,1.,1.); vec4 b=inv_vp*vec4(xy,-1.,1.);
  vec3 d=normalize(a.xyz/a.w-b.xyz/b.w);
  float e=d.y;
  vec3 c= e>0. ? mix(mix(hor,mid,smoothstep(0.,.18,e)),top,smoothstep(.18,.75,e)) : hor*0.92;
  float s=max(dot(d,sun_dir),0.);
  c+=glow*pow(s,8.)*0.55 + glow*pow(s,64.)*0.6;
  c=mix(c,vec3(1.,.97,.88),smoothstep(1.-sun_size,1.-sun_size*0.7,s));
  if(e>0.02 && clouds>0.){
    vec2 p=d.xz/(e+0.08)*1.6;
    float k=fbm(p*0.9+vec2(time,0.));
    float m=smoothstep(.55,.75,k)*clouds*smoothstep(0.02,.2,e);
    vec3 cc=mix(mid*1.05, glow*1.1+hor*0.4, pow(s,3.)*0.8+0.2);
    c=mix(c,cc,m);
  }
  f=vec4(c,1.);
}
"""
WATER_FS = """
#version 330
uniform vec3 cam; uniform vec3 sun_dir; uniform vec3 deep; uniform vec3 fog_col;
uniform float fog_density; uniform vec3 glow; uniform sampler2D refl; uniform vec2 res;
in vec2 uv; in vec3 nrm; in vec3 wpos; in vec4 lpos; in float shade; out vec4 f;
void main(){
  vec3 v=normalize(cam-wpos);
  vec2 p=wpos.xz;
  vec3 n=normalize(vec3(sin(p.x*1.7+p.y*0.6)*0.025+sin(p.x*0.43-p.y*1.1)*0.02, 1.,
                        sin(p.y*1.9-p.x*0.5)*0.025+sin(p.y*0.37+p.x*0.9)*0.02));
  float ndv=max(dot(n,v),0.);
  float fr=0.22+0.74*pow(1.-ndv,3.);
  vec2 s=gl_FragCoord.xy/res+n.xz*0.08;
  vec3 r=texture(refl,s).rgb;
  vec3 rv=reflect(-v,n);
  float sp=pow(max(dot(rv,sun_dir),0.),220.);
  vec3 c=mix(deep,r,fr)+glow*sp*1.4;
  float d=length(wpos-cam);
  float fog=1.-exp(-d*fog_density*0.35);
  f=vec4(mix(c,fog_col,clamp(fog,0.,1.)),mix(mix(0.78,1.,fr),1.,smoothstep(40.,120.,d)));
}
"""


def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = (np.array(v, float) for v in (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4)
    m[0, :3], m[1, :3], m[2, :3] = s, u, -f
    m[:3, 3] = -m[:3, :3] @ eye
    return m


def perspective(fov, aspect, near, far, shift=(0.0, 0.0)):
    t = 1 / math.tan(math.radians(fov) / 2)
    m = np.zeros((4, 4))
    m[0, 0], m[1, 1] = t / aspect, t
    m[0, 2], m[1, 2] = -shift[0], -shift[1]
    m[2, 2], m[2, 3] = (far + near) / (near - far), 2 * far * near / (near - far)
    m[3, 2] = -1
    return m


def ortho(l, r, b, t, n, f):
    m = np.identity(4)
    m[0, 0], m[1, 1], m[2, 2] = 2 / (r - l), 2 / (t - b), -2 / (f - n)
    m[0, 3], m[1, 3], m[2, 3] = -(r + l) / (r - l), -(t + b) / (t - b), -(f + n) / (f - n)
    return m


class Mesh:
    """Quads with a texture. verts: (N,9) float32 = pos3, uv2, nrm3, shade1 (6 verts per quad)."""

    def __init__(self, verts, texture, tint=(1, 1, 1), water=False, rim=0.0):
        self.rim = rim
        self.verts = np.asarray(verts, np.float32)
        self.texture = texture.convert("RGBA")
        self.tint = tint
        self.water = water


def quad_verts(corners, uvs, normal, shade=1.0):
    """corners: 4 points (counter-clockwise), uvs: 4 (u,v) in 0..1 texture space."""
    out = []
    for i in (0, 1, 2, 0, 2, 3):
        out.append(list(corners[i]) + list(uvs[i]) + list(normal) + [shade])
    return out


class Scene:
    def __init__(self, W=1920, H=1080, samples=4):
        self.W, self.H = W, H
        self.ctx = moderngl.create_standalone_context()
        self.prog = self.ctx.program(vertex_shader=VS, fragment_shader=FS)
        self.sprog = self.ctx.program(vertex_shader=SVS, fragment_shader=SFS)
        self.sky = self.ctx.program(vertex_shader=SKY_VS, fragment_shader=SKY_FS)
        self.water = self.ctx.program(vertex_shader=VS, fragment_shader=WATER_FS)
        self.samples = samples
        self.meshes = []

    def add(self, mesh):
        self.meshes.append(mesh)

    def _tex(self, img):
        t = self.ctx.texture(img.size, 4, img.tobytes())
        t.filter = (moderngl.NEAREST, moderngl.NEAREST)
        t.repeat_x = t.repeat_y = False
        return t

    def render(self, cam, target, fov, sun_dir, look, shadow_box, near=0.5, far=900.0, shift=(0, 0), shadow_res=4096):
        ctx, W, H = self.ctx, self.W, self.H
        sun_dir = np.array(sun_dir, float)
        sun_dir /= np.linalg.norm(sun_dir)
        proj = perspective(fov, W / H, near, far, shift)
        view = look_at(cam, target)
        vp = proj @ view
        # light camera fitted to the shadow box (centre, half-size)
        c, r = np.array(shadow_box[0], float), shadow_box[1]
        lview = look_at(c + sun_dir * r * 2, c, (0, 1, 0) if abs(sun_dir[1]) < 0.99 else (0, 0, 1))
        lvp = ortho(-r, r, -r, r, 0.1, r * 4) @ lview
        vaos = []
        for m in self.meshes:
            vbo = ctx.buffer(m.verts.tobytes())
            tex = self._tex(m.texture)
            prog = self.water if m.water else self.prog
            vao = ctx.vertex_array(prog, [(vbo, "3f 2f 3f 1f", "in_pos", "in_uv", "in_nrm", "in_shade")])
            svao = ctx.vertex_array(self.sprog, [(vbo, "3f 2f 12x 4x", "in_pos", "in_uv")])
            vaos.append((m, vao, svao, tex))
        # shadow pass
        sdepth = ctx.depth_texture((shadow_res, shadow_res))
        sdepth.compare_func = ""
        sdepth.filter = (moderngl.NEAREST, moderngl.NEAREST)
        sfbo = ctx.framebuffer(depth_attachment=sdepth)
        sfbo.use()
        sfbo.clear(depth=1.0)
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        self.sprog["lvp"].write(lvp.T.astype("f4").tobytes())
        for m, vao, svao, tex in vaos:
            if m.water:
                continue
            tex.use(0)
            self.sprog["tex"] = 0
            svao.render()
        def draw(vp, clip_y):
            sk = self.sky
            sk["inv_vp"].write(np.linalg.inv(vp).T.astype("f4").tobytes())
            sk["sun_dir"] = tuple(sun_dir)
            for k in ("top", "mid", "hor", "glow"):
                sk[k] = look[k]
            sk["sun_size"] = look.get("sun_size", 0.0006)
            sk["clouds"] = look.get("clouds", 0.0)
            sk["time"] = look.get("cloud_shift", 0.0)
            quad = ctx.buffer(np.array([-1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1], "f4").tobytes())
            ctx.disable(moderngl.DEPTH_TEST)
            ctx.vertex_array(sk, [(quad, "2f", "in_xy")]).render()
            ctx.enable(moderngl.DEPTH_TEST)
            p = self.prog
            p["vp"].write(vp.T.astype("f4").tobytes())
            p["lvp"].write(lvp.T.astype("f4").tobytes())
            p["sun_dir"] = tuple(sun_dir)
            for k in ("sun_col", "sky_amb", "gnd_amb", "fog_col"):
                p[k] = look[k]
            p["cam"] = tuple(cam)
            p["fog_density"] = look["fog_density"]
            p["fog_height"] = look.get("fog_height", 0.0)
            p["shadow_px"] = 1.0 / shadow_res
            p["clip_y"] = clip_y
            sdepth.use(1)
            p["shadow"] = 1
            for m, vao, svao, tex in vaos:
                if m.water:
                    continue
                tex.use(0)
                p["tex"] = 0
                p["tint"] = tuple(m.tint)
                p["rim"] = m.rim
                vao.render()

        # reflection pass: the scene mirrored in the water plane, sampled by the water in screen space
        waters = [m for m in self.meshes if m.water]
        rtex = ctx.texture((W, H), 4)
        rtex.repeat_x = rtex.repeat_y = False
        if waters:
            wy = float(waters[0].verts[0, 1])
            mirror = np.identity(4)
            mirror[1, 1], mirror[1, 3] = -1, 2 * wy
            rfbo = ctx.framebuffer([rtex], ctx.depth_renderbuffer((W, H)))
            rfbo.use()
            rfbo.clear(0, 0, 0, 1, depth=1.0)
            draw(vp @ mirror, wy - 0.05)
        # main pass (multisampled)
        col = ctx.renderbuffer((W, H), 4, samples=self.samples)
        dep = ctx.depth_renderbuffer((W, H), samples=self.samples)
        fbo = ctx.framebuffer([col], dep)
        fbo.use()
        fbo.clear(0, 0, 0, 1, depth=1.0)
        draw(vp, -1e9)
        p = self.prog
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        wp = self.water
        for m, vao, svao, tex in vaos:
            if not m.water:
                continue
            wp["vp"].write(vp.T.astype("f4").tobytes())
            wp["cam"] = tuple(cam)
            wp["sun_dir"] = tuple(sun_dir)
            wp["deep"] = look["water_deep"]
            rtex.use(2)
            wp["refl"] = 2
            wp["res"] = (float(W), float(H))
            wp["fog_col"] = look["fog_col"]
            wp["fog_density"] = look["fog_density"]
            wp["glow"] = look["glow"]
            vao.render()
        ctx.disable(moderngl.BLEND)
        # resolve
        rcol = ctx.texture((W, H), 4)
        rdep = ctx.depth_texture((W, H))
        out = ctx.framebuffer([rcol], rdep)
        ctx.copy_framebuffer(out, fbo)
        rgb = np.frombuffer(rcol.read(), np.uint8).reshape(H, W, 4)[::-1, :, :3]
        # depth: single-sample pass for the DOF mask
        dfbo = ctx.framebuffer(depth_attachment=ctx.depth_texture((W, H)))
        dfbo.use()
        dfbo.clear(depth=1.0)
        for m, vao, svao, tex in vaos:
            if m.water:
                continue
            tex.use(0)
            p["tex"] = 0
            vao.render()
        zb = np.frombuffer(dfbo.depth_attachment.read(), np.float32).reshape(H, W)[::-1]
        z = zb * 2 - 1
        lin = 2 * near * far / (far + near - z * (far - near))
        lin[zb >= 1.0] = far
        return Image.fromarray(rgb.copy(), "RGB"), lin
