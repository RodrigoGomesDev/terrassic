package com.primalera.client;

import com.primalera.entity.DinosaurEntity;
import com.primalera.registry.ModEntities;
import dev.architectury.registry.client.level.entity.EntityRendererRegistry;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.world.entity.EntityType;

/**
 * Client-only setup. The scale values match the pixel size each model was authored at (see tools/modelgen):
 * small animals are modelled bigger and scaled down so their textures keep detail.
 */
public final class PrimalEraClient {
    private PrimalEraClient() {
    }

    public static void init() {
        renderer(ModEntities.TYRANNOSAURUS, "tyrannosaurus", 1.0F, 1.4F);
        renderer(ModEntities.SPINOSAURUS, "spinosaurus", 1.0F, 1.4F);
        renderer(ModEntities.DILOPHOSAURUS, "dilophosaurus", 1.0F, 0.7F);
        renderer(ModEntities.VELOCIRAPTOR, "velociraptor", 0.5F, 0.4F);
        renderer(ModEntities.COMPSOGNATHUS, "compsognathus", 0.3F, 0.25F);
        renderer(ModEntities.TRICERATOPS, "triceratops", 1.0F, 1.3F);
        renderer(ModEntities.STEGOSAURUS, "stegosaurus", 1.0F, 1.2F);
        renderer(ModEntities.ANKYLOSAURUS, "ankylosaurus", 1.0F, 1.2F);
        renderer(ModEntities.BRACHIOSAURUS, "brachiosaurus", 1.0F, 2.2F);
        renderer(ModEntities.PARASAUROLOPHUS, "parasaurolophus", 1.0F, 1.0F);
        renderer(ModEntities.PACHYCEPHALOSAURUS, "pachycephalosaurus", 0.667F, 0.6F);
        renderer(ModEntities.GALLIMIMUS, "gallimimus", 1.0F, 0.6F);
        EntityRendererRegistry.register(ModEntities.SPEAR, ThrownSpearRenderer::new);
    }

    private static <T extends DinosaurEntity> void renderer(RegistrySupplier<EntityType<T>> type, String id, float scale, float shadow) {
        EntityRendererRegistry.register(type, context -> new DinosaurRenderer<T>(context, id, scale, shadow));
    }
}
