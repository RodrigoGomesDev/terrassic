#version 150

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
