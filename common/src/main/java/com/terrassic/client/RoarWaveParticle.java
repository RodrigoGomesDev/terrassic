package com.terrassic.client;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;

/**
 * The loud roar's burst in the air (entity/ApexTheropod): a ring of comic speed lines and little bolts racing out of
 * the mouth, 8 frames (textures/particle/roar_wave_0..7,
 * tools/modelgen/handmade/tyrannosaurus/roar_wave.py), facing the camera, at full
 * brightness. The sprite is drawn 1 texel = 1 Minecraft pixel, so the burst is 8 blocks across at strength 1. The
 * velocity's x carries the strength (the server sends it with count 0); each wave also shakes the camera
 * ({@link RoarShake}).
 */
public class RoarWaveParticle extends TextureSheetParticle {
    private final SpriteSet sprites;

    protected RoarWaveParticle(ClientLevel level, double x, double y, double z, float strength, SpriteSet sprites) {
        super(level, x, y, z);
        this.sprites = sprites;
        this.lifetime = 11;
        this.quadSize = 4.0F * strength;
        this.hasPhysics = false;
        this.gravity = 0.0F;
        this.xd = 0.0D;
        this.yd = 0.0D;
        this.zd = 0.0D;
        this.setSpriteFromAge(sprites);
    }

    @Override
    public void tick() {
        this.xo = this.x;
        this.yo = this.y;
        this.zo = this.z;
        if (this.age++ >= this.lifetime) {
            this.remove();
            return;
        }
        this.setSpriteFromAge(this.sprites);
        this.alpha = this.age > this.lifetime - 3 ? (this.lifetime - this.age) / 3.0F : 1.0F;
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
        private final SpriteSet sprites;

        public Provider(SpriteSet sprites) {
            this.sprites = sprites;
        }

        @Override
        public Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                       double xd, double yd, double zd) {
            float strength = (float) Math.max(0.2D, Math.min(2.0D, xd));
            RoarShake.pulse(x, y, z, strength);
            return new RoarWaveParticle(level, x, y, z, strength, this.sprites);
        }
    }
}
