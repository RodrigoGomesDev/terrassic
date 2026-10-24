package com.terrassic.client;

import com.terrassic.entity.Ankylosaurus;
import com.terrassic.entity.Brachiosaurus;
import com.terrassic.entity.Compsognathus;
import com.terrassic.entity.Dilophosaurus;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.Gallimimus;
import com.terrassic.entity.Pachycephalosaurus;
import com.terrassic.entity.Parasaurolophus;
import com.terrassic.entity.Pteranodon;
import com.terrassic.entity.Spinosaurus;
import com.terrassic.entity.Stegosaurus;
import com.terrassic.entity.Triceratops;
import com.terrassic.entity.Tyrannosaurus;
import com.terrassic.entity.Velociraptor;
import com.terrassic.registry.ModEntities;
import dev.architectury.registry.client.level.entity.EntityRendererRegistry;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.world.entity.EntityType;

/**
 * Client-only setup. Model scale and shadow come from the generated species classes (SIZES in
 * tools/javagen/gen_species.py), which combine the pixel size each model was authored at (tools/modelgen) with
 * the in-game size of the species.
 */
public final class TerrassicClient {
    private TerrassicClient() {
    }

    public static void init() {
        renderer(ModEntities.TYRANNOSAURUS, "tyrannosaurus", Tyrannosaurus.MODEL_SCALE, Tyrannosaurus.SHADOW);
        renderer(ModEntities.SPINOSAURUS, "spinosaurus", Spinosaurus.MODEL_SCALE, Spinosaurus.SHADOW);
        renderer(ModEntities.DILOPHOSAURUS, "dilophosaurus", Dilophosaurus.MODEL_SCALE, Dilophosaurus.SHADOW);
        renderer(ModEntities.VELOCIRAPTOR, "velociraptor", Velociraptor.MODEL_SCALE, Velociraptor.SHADOW);
        renderer(ModEntities.COMPSOGNATHUS, "compsognathus", Compsognathus.MODEL_SCALE, Compsognathus.SHADOW);
        renderer(ModEntities.TRICERATOPS, "triceratops", Triceratops.MODEL_SCALE, Triceratops.SHADOW);
        renderer(ModEntities.STEGOSAURUS, "stegosaurus", Stegosaurus.MODEL_SCALE, Stegosaurus.SHADOW);
        renderer(ModEntities.ANKYLOSAURUS, "ankylosaurus", Ankylosaurus.MODEL_SCALE, Ankylosaurus.SHADOW);
        renderer(ModEntities.BRACHIOSAURUS, "brachiosaurus", Brachiosaurus.MODEL_SCALE, Brachiosaurus.SHADOW);
        renderer(ModEntities.PARASAUROLOPHUS, "parasaurolophus", Parasaurolophus.MODEL_SCALE, Parasaurolophus.SHADOW);
        renderer(ModEntities.PACHYCEPHALOSAURUS, "pachycephalosaurus", Pachycephalosaurus.MODEL_SCALE, Pachycephalosaurus.SHADOW);
        renderer(ModEntities.GALLIMIMUS, "gallimimus", Gallimimus.MODEL_SCALE, Gallimimus.SHADOW);
        renderer(ModEntities.PTERANODON, "pteranodon", Pteranodon.MODEL_SCALE, Pteranodon.SHADOW);
        EntityRendererRegistry.register(ModEntities.SPEAR, ThrownSpearRenderer::new);
        ClientHooks.init();
    }

    private static <T extends DinosaurEntity> void renderer(RegistrySupplier<EntityType<T>> type, String id, float scale, float shadow) {
        EntityRendererRegistry.register(type, context -> new DinosaurRenderer<T>(context, id, scale, shadow));
    }
}
