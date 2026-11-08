package com.terrassic.registry;

import com.terrassic.Terrassic;
import com.terrassic.effect.BleedingEffect;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.effect.MobEffect;

/** The mod's own status effects (icons in assets/terrassic/textures/mob_effect/, drawn by tools/spritegen). */
public final class ModEffects {
    public static final DeferredRegister<MobEffect> EFFECTS = DeferredRegister.create(Terrassic.MOD_ID, Registries.MOB_EFFECT);

    /** 1.10.1: the Carcharodontosaurus' tearing bite (docs/estudos/13): a few seconds of damage over time. */
    public static final RegistrySupplier<MobEffect> BLEEDING = EFFECTS.register("bleeding", BleedingEffect::new);

    /** 1.21: effect instances and checks take the registry holder. */
    public static Holder<MobEffect> bleeding() {
        return BuiltInRegistries.MOB_EFFECT.wrapAsHolder(BLEEDING.get());
    }

    private ModEffects() {
    }
}
