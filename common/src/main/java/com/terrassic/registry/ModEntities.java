package com.terrassic.registry;

import com.terrassic.Terrassic;
import com.terrassic.entity.Ankylosaurus;
import com.terrassic.entity.Brachiosaurus;
import com.terrassic.entity.Compsognathus;
import com.terrassic.entity.Dilophosaurus;
import com.terrassic.entity.Gallimimus;
import com.terrassic.entity.Mosasaurus;
import com.terrassic.entity.Pachycephalosaurus;
import com.terrassic.entity.Parasaurolophus;
import com.terrassic.entity.Pteranodon;
import com.terrassic.entity.Spinosaurus;
import com.terrassic.entity.Stegosaurus;
import com.terrassic.entity.ThrownSpear;
import com.terrassic.entity.Triceratops;
import com.terrassic.entity.Tyrannosaurus;
import com.terrassic.entity.Velociraptor;
import dev.architectury.registry.level.entity.EntityAttributeRegistry;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/**
 * Entity types. Hitbox sizes come from the generated species classes (SIZES in tools/javagen/gen_species.py).
 * Hitboxes are smaller than the models on purpose: Minecraft hitboxes are square, and very wide boxes make
 * path finding hard for the big animals. The renderer handles culling of the long bodies.
 */
public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(Terrassic.MOD_ID, Registries.ENTITY_TYPE);

    // ---- predators
    public static final RegistrySupplier<EntityType<Tyrannosaurus>> TYRANNOSAURUS =
            mob("tyrannosaurus", Tyrannosaurus::new, Tyrannosaurus.WIDTH, Tyrannosaurus.HEIGHT, 10);
    public static final RegistrySupplier<EntityType<Spinosaurus>> SPINOSAURUS =
            mob("spinosaurus", Spinosaurus::new, Spinosaurus.WIDTH, Spinosaurus.HEIGHT, 10);
    public static final RegistrySupplier<EntityType<Dilophosaurus>> DILOPHOSAURUS =
            mob("dilophosaurus", Dilophosaurus::new, Dilophosaurus.WIDTH, Dilophosaurus.HEIGHT, 8);
    public static final RegistrySupplier<EntityType<Velociraptor>> VELOCIRAPTOR =
            mob("velociraptor", Velociraptor::new, Velociraptor.WIDTH, Velociraptor.HEIGHT, 8);
    public static final RegistrySupplier<EntityType<Compsognathus>> COMPSOGNATHUS =
            mob("compsognathus", Compsognathus::new, Compsognathus.WIDTH, Compsognathus.HEIGHT, 8);
    // ---- herbivores
    public static final RegistrySupplier<EntityType<Triceratops>> TRICERATOPS =
            mob("triceratops", Triceratops::new, Triceratops.WIDTH, Triceratops.HEIGHT, 10);
    public static final RegistrySupplier<EntityType<Stegosaurus>> STEGOSAURUS =
            mob("stegosaurus", Stegosaurus::new, Stegosaurus.WIDTH, Stegosaurus.HEIGHT, 10);
    public static final RegistrySupplier<EntityType<Ankylosaurus>> ANKYLOSAURUS =
            mob("ankylosaurus", Ankylosaurus::new, Ankylosaurus.WIDTH, Ankylosaurus.HEIGHT, 10);
    public static final RegistrySupplier<EntityType<Brachiosaurus>> BRACHIOSAURUS =
            mob("brachiosaurus", Brachiosaurus::new, Brachiosaurus.WIDTH, Brachiosaurus.HEIGHT, 14);
    public static final RegistrySupplier<EntityType<Parasaurolophus>> PARASAUROLOPHUS =
            mob("parasaurolophus", Parasaurolophus::new, Parasaurolophus.WIDTH, Parasaurolophus.HEIGHT, 10);
    public static final RegistrySupplier<EntityType<Pachycephalosaurus>> PACHYCEPHALOSAURUS =
            mob("pachycephalosaurus", Pachycephalosaurus::new, Pachycephalosaurus.WIDTH, Pachycephalosaurus.HEIGHT, 8);
    public static final RegistrySupplier<EntityType<Gallimimus>> GALLIMIMUS =
            mob("gallimimus", Gallimimus::new, Gallimimus.WIDTH, Gallimimus.HEIGHT, 10);
    // ---- flyers
    public static final RegistrySupplier<EntityType<Pteranodon>> PTERANODON =
            mob("pteranodon", Pteranodon::new, Pteranodon.WIDTH, Pteranodon.HEIGHT, 10);
    // ---- marine reptiles
    public static final RegistrySupplier<EntityType<Mosasaurus>> MOSASAURUS = ENTITY_TYPES.register("mosasaurus",
            () -> EntityType.Builder.of(Mosasaurus::new, MobCategory.WATER_CREATURE)
                    .sized(Mosasaurus.WIDTH, Mosasaurus.HEIGHT).clientTrackingRange(12).build("mosasaurus"));

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
        EntityAttributeRegistry.register(PTERANODON, Pteranodon::createAttributes);
        EntityAttributeRegistry.register(MOSASAURUS, Mosasaurus::createAttributes);
    }
}
