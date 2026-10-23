package com.primalera.registry;

import com.primalera.PrimalEra;
import com.primalera.entity.Ankylosaurus;
import com.primalera.entity.Brachiosaurus;
import com.primalera.entity.Compsognathus;
import com.primalera.entity.Dilophosaurus;
import com.primalera.entity.Gallimimus;
import com.primalera.entity.Pachycephalosaurus;
import com.primalera.entity.Parasaurolophus;
import com.primalera.entity.Spinosaurus;
import com.primalera.entity.Stegosaurus;
import com.primalera.entity.ThrownSpear;
import com.primalera.entity.Triceratops;
import com.primalera.entity.Tyrannosaurus;
import com.primalera.entity.Velociraptor;
import dev.architectury.registry.level.entity.EntityAttributeRegistry;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/**
 * Entity types. Hitboxes are smaller than the models on purpose: Minecraft hitboxes are square, and very
 * wide boxes make path finding hard for the big animals. The renderer handles culling of the long bodies.
 */
public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(PrimalEra.MOD_ID, Registries.ENTITY_TYPE);

    // ---- predators
    public static final RegistrySupplier<EntityType<Tyrannosaurus>> TYRANNOSAURUS =
            mob("tyrannosaurus", Tyrannosaurus::new, 1.9F, 2.9F, 10);
    public static final RegistrySupplier<EntityType<Spinosaurus>> SPINOSAURUS =
            mob("spinosaurus", Spinosaurus::new, 1.9F, 2.8F, 10);
    public static final RegistrySupplier<EntityType<Dilophosaurus>> DILOPHOSAURUS =
            mob("dilophosaurus", Dilophosaurus::new, 0.9F, 1.6F, 8);
    public static final RegistrySupplier<EntityType<Velociraptor>> VELOCIRAPTOR =
            mob("velociraptor", Velociraptor::new, 0.7F, 0.9F, 8);
    public static final RegistrySupplier<EntityType<Compsognathus>> COMPSOGNATHUS =
            mob("compsognathus", Compsognathus::new, 0.4F, 0.5F, 8);
    // ---- herbivores
    public static final RegistrySupplier<EntityType<Triceratops>> TRICERATOPS =
            mob("triceratops", Triceratops::new, 1.9F, 2.0F, 10);
    public static final RegistrySupplier<EntityType<Stegosaurus>> STEGOSAURUS =
            mob("stegosaurus", Stegosaurus::new, 1.7F, 2.0F, 10);
    public static final RegistrySupplier<EntityType<Ankylosaurus>> ANKYLOSAURUS =
            mob("ankylosaurus", Ankylosaurus::new, 1.9F, 1.4F, 10);
    public static final RegistrySupplier<EntityType<Brachiosaurus>> BRACHIOSAURUS =
            mob("brachiosaurus", Brachiosaurus::new, 3.0F, 5.0F, 12);
    public static final RegistrySupplier<EntityType<Parasaurolophus>> PARASAUROLOPHUS =
            mob("parasaurolophus", Parasaurolophus::new, 1.4F, 2.0F, 10);
    public static final RegistrySupplier<EntityType<Pachycephalosaurus>> PACHYCEPHALOSAURUS =
            mob("pachycephalosaurus", Pachycephalosaurus::new, 0.9F, 1.4F, 8);
    public static final RegistrySupplier<EntityType<Gallimimus>> GALLIMIMUS =
            mob("gallimimus", Gallimimus::new, 0.9F, 1.8F, 10);

    // ---- projectiles
    public static final RegistrySupplier<EntityType<ThrownSpear>> SPEAR = ENTITY_TYPES.register("spear",
            () -> EntityType.Builder.<ThrownSpear>of(ThrownSpear::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(4).updateInterval(20).build("spear"));

    private ModEntities() {
    }

    private static <T extends Entity> RegistrySupplier<EntityType<T>> mob(String name, EntityType.EntityFactory<T> factory,
                                                                         float width, float height, int trackingRange) {
        return ENTITY_TYPES.register(name, () -> EntityType.Builder.of(factory, MobCategory.CREATURE)
                .sized(width, height).clientTrackingRange(trackingRange).build(name));
    }

    public static void registerAttributes() {
        EntityAttributeRegistry.register(TYRANNOSAURUS, Tyrannosaurus::createAttributes);
        EntityAttributeRegistry.register(SPINOSAURUS, Spinosaurus::createAttributes);
        EntityAttributeRegistry.register(DILOPHOSAURUS, Dilophosaurus::createAttributes);
        EntityAttributeRegistry.register(VELOCIRAPTOR, Velociraptor::createAttributes);
        EntityAttributeRegistry.register(COMPSOGNATHUS, Compsognathus::createAttributes);
        EntityAttributeRegistry.register(TRICERATOPS, Triceratops::createAttributes);
        EntityAttributeRegistry.register(STEGOSAURUS, Stegosaurus::createAttributes);
        EntityAttributeRegistry.register(ANKYLOSAURUS, Ankylosaurus::createAttributes);
        EntityAttributeRegistry.register(BRACHIOSAURUS, Brachiosaurus::createAttributes);
        EntityAttributeRegistry.register(PARASAUROLOPHUS, Parasaurolophus::createAttributes);
        EntityAttributeRegistry.register(PACHYCEPHALOSAURUS, Pachycephalosaurus::createAttributes);
        EntityAttributeRegistry.register(GALLIMIMUS, Gallimimus::createAttributes);
    }
}
