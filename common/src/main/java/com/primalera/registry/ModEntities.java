package com.primalera.registry;

import com.primalera.PrimalEra;
import com.primalera.entity.Compsognathus;
import com.primalera.entity.Stegosaurus;
import com.primalera.entity.Triceratops;
import com.primalera.entity.Tyrannosaurus;
import com.primalera.entity.Velociraptor;
import dev.architectury.registry.level.entity.EntityAttributeRegistry;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/**
 * Entity types. Hitboxes are smaller than the models on purpose: Minecraft
 * hitboxes are square, and a 2-block wide box already makes path finding hard
 * for the big animals. The renderer handles culling of the long bodies.
 */
public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(PrimalEra.MOD_ID, Registries.ENTITY_TYPE);

    public static final RegistrySupplier<EntityType<Tyrannosaurus>> TYRANNOSAURUS = ENTITY_TYPES.register("tyrannosaurus",
            () -> EntityType.Builder.of(Tyrannosaurus::new, MobCategory.CREATURE)
                    .sized(1.9F, 2.9F).clientTrackingRange(10).build("tyrannosaurus"));

    public static final RegistrySupplier<EntityType<Triceratops>> TRICERATOPS = ENTITY_TYPES.register("triceratops",
            () -> EntityType.Builder.of(Triceratops::new, MobCategory.CREATURE)
                    .sized(1.9F, 2.0F).clientTrackingRange(10).build("triceratops"));

    public static final RegistrySupplier<EntityType<Stegosaurus>> STEGOSAURUS = ENTITY_TYPES.register("stegosaurus",
            () -> EntityType.Builder.of(Stegosaurus::new, MobCategory.CREATURE)
                    .sized(1.7F, 2.0F).clientTrackingRange(10).build("stegosaurus"));

    public static final RegistrySupplier<EntityType<Velociraptor>> VELOCIRAPTOR = ENTITY_TYPES.register("velociraptor",
            () -> EntityType.Builder.of(Velociraptor::new, MobCategory.CREATURE)
                    .sized(0.7F, 0.9F).clientTrackingRange(8).build("velociraptor"));

    public static final RegistrySupplier<EntityType<Compsognathus>> COMPSOGNATHUS = ENTITY_TYPES.register("compsognathus",
            () -> EntityType.Builder.of(Compsognathus::new, MobCategory.CREATURE)
                    .sized(0.4F, 0.5F).clientTrackingRange(8).build("compsognathus"));

    private ModEntities() {
    }

    public static void registerAttributes() {
        EntityAttributeRegistry.register(TYRANNOSAURUS, Tyrannosaurus::createAttributes);
        EntityAttributeRegistry.register(TRICERATOPS, Triceratops::createAttributes);
        EntityAttributeRegistry.register(STEGOSAURUS, Stegosaurus::createAttributes);
        EntityAttributeRegistry.register(VELOCIRAPTOR, Velociraptor::createAttributes);
        EntityAttributeRegistry.register(COMPSOGNATHUS, Compsognathus::createAttributes);
    }
}
