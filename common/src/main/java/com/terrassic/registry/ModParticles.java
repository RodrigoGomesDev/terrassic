package com.terrassic.registry;

import com.terrassic.Terrassic;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.Registries;

/** The mod's own particles (assets/terrassic/particles/; providers in client/). */
public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(Terrassic.MOD_ID, Registries.PARTICLE_TYPE);

    /** The loud roar's burst in the air (client/RoarWaveParticle); shown however low the particle setting is. */
    public static final RegistrySupplier<SimpleParticleType> ROAR_WAVE = PARTICLES.register("roar_wave", () -> new SimpleParticleType(true) {
    });

    /** v1.6: the alphas' aura (client/AlphaMoteParticle); AlphaAura makes them straight on the client. */
    public static final RegistrySupplier<SimpleParticleType> ALPHA_MOTE = PARTICLES.register("alpha_mote", () -> new SimpleParticleType(false) {
    });

    /** 06/11/2026: a blow, a throw, a body hitting the ground: no picture, only the camera shake near it (RoarShake), the
     *  strength in the x speed. Sent only to the players near (DinosaurEntity.impact). */
    public static final RegistrySupplier<SimpleParticleType> IMPACT = PARTICLES.register("impact", () -> new SimpleParticleType(true) {
    });

    private ModParticles() {
    }
}
