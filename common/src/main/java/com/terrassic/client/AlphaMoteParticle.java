package com.terrassic.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;

/**
 * One speck of the alpha's aura (v1.6, {@link AlphaAura}): the mod's own sprites (textures/particle/alpha_mote_0..3,
 * tools/spritegen/alfa_aura.py) tinted from one coat colour to the other over its life, at full brightness so the aura
 * glows at night without vanilla flames or end rods. Made straight by AlphaAura (colours never travel over the
 * network); the registered type only lends its sprites, and /particle terrassic:alpha_mote shows a pale mote.
 */
public class AlphaMoteParticle extends TextureSheetParticle {
    public static final int BLOCK = 0;
    public static final int CHIP = 1;
    public static final int GLINT = 2;
    public static final int FLAKE = 3;

    /** The four frames, kept by the provider when the particle sprites load. */
    private static SpriteSet sprites;

    private final float r0, g0, b0, r1, g1, b1;
    private final float peak;
    private final float size0;
    private final boolean twinkle;
    private final float phase;

    protected AlphaMoteParticle(ClientLevel level, double x, double y, double z, double xd, double yd, double zd,
                                int kind, int from, int to, float size, int life, float peak) {
        super(level, x, y, z);
        this.xd = xd;
        this.yd = yd;
        this.zd = zd;
        this.lifetime = life;
        this.hasPhysics = false;
        this.gravity = 0.0F;
        this.friction = 0.96F;
        this.r0 = (from >> 16 & 255) / 255.0F;
        this.g0 = (from >> 8 & 255) / 255.0F;
        this.b0 = (from & 255) / 255.0F;
        this.r1 = (to >> 16 & 255) / 255.0F;
        this.g1 = (to >> 8 & 255) / 255.0F;
        this.b1 = (to & 255) / 255.0F;
        this.peak = peak;
        this.size0 = size;
        this.quadSize = size;
        this.twinkle = kind == GLINT;
        this.phase = this.random.nextFloat() * Mth.TWO_PI;
        this.alpha = 0.2F;
        this.setColor(this.r0, this.g0, this.b0);
        if (sprites != null) {
            this.setSprite(sprites.get(kind, 3));
        }
    }

    /** Adds one speck; nothing before the sprites have loaded. */
    public static void spawn(ClientLevel level, double x, double y, double z, double xd, double yd, double zd,
                             int kind, int from, int to, float size, int life, float peak) {
        if (sprites == null) {
            return;
        }
        Minecraft.getInstance().particleEngine.add(
                new AlphaMoteParticle(level, x, y, z, xd, yd, zd, kind, from, to, size, life, peak));
    }

    @Override
    public void tick() {
        super.tick();
        float t = (float) this.age / (float) this.lifetime;
        // colour: from the bright coat colour to the dark one; size: swells a little, then shrinks away
        this.setColor(Mth.lerp(t, this.r0, this.r1), Mth.lerp(t, this.g0, this.g1), Mth.lerp(t, this.b0, this.b1));
        this.quadSize = this.size0 * (t < 0.2F ? 0.7F + 1.5F * t : 1.0F - 0.6F * (t - 0.2F));
        // fades in fast, holds, fades out over the last third; a glint flickers. Never under 0.2 while it lives: the
        // vanilla particle shader discards what is under 10% opacity (v1.6 fix, the first aura showed nothing)
        float a = t < 0.1F ? t / 0.1F : t > 0.67F ? (1.0F - t) / 0.33F : 1.0F;
        if (this.twinkle) {
            a *= 0.7F + 0.3F * Mth.sin(this.age * 1.3F + this.phase);
        }
        this.alpha = Math.max(0.2F, Mth.clamp(a, 0.0F, 1.0F) * this.peak);
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
    }

    @Override
    protected int getLightColor(float partialTick) {
        return 0xF000F0;
    }

    public static class Provider implements ParticleProvider<SimpleParticleType> {
        public Provider(SpriteSet set) {
            sprites = set;
        }

        @Override
        public Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                       double xd, double yd, double zd) {
            return new AlphaMoteParticle(level, x, y, z, xd, yd, zd, BLOCK, 0xF2EFE8, 0x8A857C, 0.25F, 40, 0.9F);
        }
    }
}
