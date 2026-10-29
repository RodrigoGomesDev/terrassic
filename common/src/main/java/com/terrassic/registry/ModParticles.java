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

    private ModParticles() {
    }
}
