"""The era filter (docs/TEXTURAS_ERA.md, layer D): a light colour grade over the world, drawn by the mod's
EraFilter (common/.../client/EraFilter.java) with a vanilla post chain that ships inside each era pack.

One GLSL program serves every era; each era only sets its numbers in its own post chain
(assets/terrassic/shaders/post/era_<era>.json). The program lives in the minecraft namespace
(assets/minecraft/shaders/program/terrassic_era_grade.*) because vanilla looks programs up only there.
grade() applies the same maths with numpy, so the preview shows what the game will draw.
"""
import numpy as np
from PIL import Image

PROGRAM = "terrassic_era_grade"

# Strength: how much of the grade is mixed in (config "era_filter_strength" overrides it in game).
# Desaturation: share of grey mixed in. Warmth: multiplies r, g, b. Fade and Lift: c * Fade + Lift, which lifts
# the blacks a little and warms them (an old print). Vignette: corner darkening.
ERAS = {
    "cretaceo": {"Strength": 0.6, "Desaturation": 0.08, "Warmth": (1.035, 1.0, 0.95), "Fade": 0.95,
                 "Lift": (0.03, 0.022, 0.01), "Vignette": 0.4},
}

FRAGMENT = """#version 150

uniform sampler2D DiffuseSampler;

in vec2 texCoord;
in vec2 oneTexel;

uniform float Strength;
uniform float Desaturation;
uniform vec3 Warmth;
uniform float Fade;
uniform vec3 Lift;
uniform float Vignette;

out vec4 fragColor;

void main() {
    vec3 c = texture(DiffuseSampler, texCoord).rgb;
    float luma = dot(c, vec3(0.299, 0.587, 0.114));
    vec3 g = mix(c, vec3(luma), Desaturation) * Warmth;
    g = g * Fade + Lift;
    vec2 d = texCoord - vec2(0.5);
    g *= 1.0 - dot(d, d) * Vignette;
    fragColor = vec4(mix(c, clamp(g, 0.0, 1.0), Strength), 1.0);
}
"""

IDENTITY = [1.0 if i % 5 == 0 else 0.0 for i in range(16)]


def _uniform(name, value):
    values = list(value) if isinstance(value, tuple) else [value]
    return {"name": name, "type": "float", "count": len(values), "values": values}


def program():
    """assets/minecraft/shaders/program/terrassic_era_grade.json (the vertex shader is vanilla's "sobel")."""
    defaults = ERAS["cretaceo"]
    return {
        "blend": {"func": "add", "srcrgb": "one", "dstrgb": "zero"},
        "vertex": "sobel",
        "fragment": PROGRAM,
        "attributes": ["Position"],
        "samplers": [{"name": "DiffuseSampler"}],
        "uniforms": [{"name": "ProjMat", "type": "matrix4x4", "count": 16, "values": IDENTITY},
                     _uniform("InSize", (1.0, 1.0)), _uniform("OutSize", (1.0, 1.0))]
                    + [_uniform(k, v) for k, v in defaults.items()],
    }


def post_chain(era):
    """assets/terrassic/shaders/post/era_<era>.json: grade main into swap, copy swap back."""
    return {
        "targets": ["swap"],
        "passes": [
            {"name": PROGRAM, "intarget": "minecraft:main", "outtarget": "swap",
             "uniforms": [{"name": k, "values": list(v) if isinstance(v, tuple) else [v]} for k, v in ERAS[era].items()]},
            {"name": "blit", "intarget": "swap", "outtarget": "minecraft:main"},
        ],
    }


def grade(img, era, strength=None):
    """The fragment shader in numpy, for the previews."""
    p = ERAS[era]
    s = p["Strength"] if strength is None else strength
    a = np.asarray(img.convert("RGB"), np.float64) / 255.0
    h, w = a.shape[:2]
    luma = (a * (0.299, 0.587, 0.114)).sum(axis=2, keepdims=True)
    g = (a + (luma - a) * p["Desaturation"]) * p["Warmth"]
    g = g * p["Fade"] + p["Lift"]
    y, x = np.mgrid[0:h, 0:w]
    d2 = ((x + .5) / w - .5) ** 2 + ((y + .5) / h - .5) ** 2
    g *= (1.0 - d2 * p["Vignette"])[..., None]
    out = a + (np.clip(g, 0, 1) - a) * s
    return Image.fromarray(np.round(out * 255).astype(np.uint8), "RGB").convert("RGBA")
