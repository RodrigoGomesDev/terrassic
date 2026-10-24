package com.terrassic.client;

import com.terrassic.client.title.TerrassicMenuScreen;

// BEGIN GENERATED imports
import com.terrassic.entity.Alamosaurus;
import com.terrassic.entity.Albertosaurus;
import com.terrassic.entity.Ankylosaurus;
import com.terrassic.entity.Archelon;
import com.terrassic.entity.Argentinosaurus;
import com.terrassic.entity.Baurusuchus;
import com.terrassic.entity.Brachiosaurus;
import com.terrassic.entity.Carcharodontosaurus;
import com.terrassic.entity.Carnotaurus;
import com.terrassic.entity.Citipati;
import com.terrassic.entity.Compsognathus;
import com.terrassic.entity.Corythosaurus;
import com.terrassic.entity.Dakotaraptor;
import com.terrassic.entity.Daspletosaurus;
import com.terrassic.entity.Deinocheirus;
import com.terrassic.entity.Deinosuchus;
import com.terrassic.entity.Didelphodon;
import com.terrassic.entity.Dilophosaurus;
import com.terrassic.entity.Dreadnoughtus;
import com.terrassic.entity.Edmontosaurus;
import com.terrassic.entity.Elasmosaurus;
import com.terrassic.entity.Euoplocephalus;
import com.terrassic.entity.Gallimimus;
import com.terrassic.entity.Giganotosaurus;
import com.terrassic.entity.Hatzegopteryx;
import com.terrassic.entity.Hesperornis;
import com.terrassic.entity.Ichthyornis;
import com.terrassic.entity.Leptoceratops;
import com.terrassic.entity.Maiasaura;
import com.terrassic.entity.Majungasaurus;
import com.terrassic.entity.Mononykus;
import com.terrassic.entity.Mosasaurus;
import com.terrassic.entity.Opisthocoelicaudia;
import com.terrassic.entity.Oviraptor;
import com.terrassic.entity.Pachycephalosaurus;
import com.terrassic.entity.Pachyrhinosaurus;
import com.terrassic.entity.Parasaurolophus;
import com.terrassic.entity.Protoceratops;
import com.terrassic.entity.Pteranodon;
import com.terrassic.entity.Quetzalcoatlus;
import com.terrassic.entity.Saltasaurus;
import com.terrassic.entity.Spinosaurus;
import com.terrassic.entity.Stegosaurus;
import com.terrassic.entity.Struthiomimus;
import com.terrassic.entity.Styracosaurus;
import com.terrassic.entity.Tarbosaurus;
import com.terrassic.entity.Therizinosaurus;
import com.terrassic.entity.Thescelosaurus;
import com.terrassic.entity.Triceratops;
import com.terrassic.entity.Troodon;
import com.terrassic.entity.Tylosaurus;
import com.terrassic.entity.Tyrannosaurus;
import com.terrassic.entity.Velociraptor;
import com.terrassic.entity.Xiphactinus;
// END GENERATED imports
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.registry.ModEntities;
import dev.architectury.registry.client.level.entity.EntityRendererRegistry;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.world.entity.EntityType;

import java.util.HashMap;
import java.util.Map;

/**
 * Client-only setup. Model scale and shadow come from the generated species classes (SIZES in
 * tools/javagen/gen_species.py), which combine the pixel size each model was authored at (tools/modelgen) with
 * the in-game size of the species.
 */
public final class TerrassicClient {
    /** species id -> renderer scale of its model (the carcass renderer draws any species). */
    public static final Map<String, Float> MODEL_SCALES = new HashMap<>();

    private TerrassicClient() {
    }

    public static void init() {
        // BEGIN GENERATED renderers (tools/javagen/gen_species.py)
        renderer(ModEntities.TYRANNOSAURUS, "tyrannosaurus", Tyrannosaurus.MODEL_SCALE, Tyrannosaurus.SHADOW);
        renderer(ModEntities.SPINOSAURUS, "spinosaurus", Spinosaurus.MODEL_SCALE, Spinosaurus.SHADOW);
        renderer(ModEntities.DILOPHOSAURUS, "dilophosaurus", Dilophosaurus.MODEL_SCALE, Dilophosaurus.SHADOW);
        renderer(ModEntities.VELOCIRAPTOR, "velociraptor", Velociraptor.MODEL_SCALE, Velociraptor.SHADOW);
        renderer(ModEntities.COMPSOGNATHUS, "compsognathus", Compsognathus.MODEL_SCALE, Compsognathus.SHADOW);
        renderer(ModEntities.TRICERATOPS, "triceratops", Triceratops.MODEL_SCALE, Triceratops.SHADOW);
        renderer(ModEntities.STYRACOSAURUS, "styracosaurus", Styracosaurus.MODEL_SCALE, Styracosaurus.SHADOW);
        renderer(ModEntities.PACHYRHINOSAURUS, "pachyrhinosaurus", Pachyrhinosaurus.MODEL_SCALE, Pachyrhinosaurus.SHADOW);
        renderer(ModEntities.PROTOCERATOPS, "protoceratops", Protoceratops.MODEL_SCALE, Protoceratops.SHADOW);
        renderer(ModEntities.LEPTOCERATOPS, "leptoceratops", Leptoceratops.MODEL_SCALE, Leptoceratops.SHADOW);
        renderer(ModEntities.STEGOSAURUS, "stegosaurus", Stegosaurus.MODEL_SCALE, Stegosaurus.SHADOW);
        renderer(ModEntities.ANKYLOSAURUS, "ankylosaurus", Ankylosaurus.MODEL_SCALE, Ankylosaurus.SHADOW);
        renderer(ModEntities.EUOPLOCEPHALUS, "euoplocephalus", Euoplocephalus.MODEL_SCALE, Euoplocephalus.SHADOW);
        renderer(ModEntities.THERIZINOSAURUS, "therizinosaurus", Therizinosaurus.MODEL_SCALE, Therizinosaurus.SHADOW);
        renderer(ModEntities.DEINOCHEIRUS, "deinocheirus", Deinocheirus.MODEL_SCALE, Deinocheirus.SHADOW);
        renderer(ModEntities.BRACHIOSAURUS, "brachiosaurus", Brachiosaurus.MODEL_SCALE, Brachiosaurus.SHADOW);
        renderer(ModEntities.ALAMOSAURUS, "alamosaurus", Alamosaurus.MODEL_SCALE, Alamosaurus.SHADOW);
        renderer(ModEntities.SALTASAURUS, "saltasaurus", Saltasaurus.MODEL_SCALE, Saltasaurus.SHADOW);
        renderer(ModEntities.ARGENTINOSAURUS, "argentinosaurus", Argentinosaurus.MODEL_SCALE, Argentinosaurus.SHADOW);
        renderer(ModEntities.OPISTHOCOELICAUDIA, "opisthocoelicaudia", Opisthocoelicaudia.MODEL_SCALE, Opisthocoelicaudia.SHADOW);
        renderer(ModEntities.DREADNOUGHTUS, "dreadnoughtus", Dreadnoughtus.MODEL_SCALE, Dreadnoughtus.SHADOW);
        renderer(ModEntities.GIGANOTOSAURUS, "giganotosaurus", Giganotosaurus.MODEL_SCALE, Giganotosaurus.SHADOW);
        renderer(ModEntities.CARCHARODONTOSAURUS, "carcharodontosaurus", Carcharodontosaurus.MODEL_SCALE, Carcharodontosaurus.SHADOW);
        renderer(ModEntities.CARNOTAURUS, "carnotaurus", Carnotaurus.MODEL_SCALE, Carnotaurus.SHADOW);
        renderer(ModEntities.TARBOSAURUS, "tarbosaurus", Tarbosaurus.MODEL_SCALE, Tarbosaurus.SHADOW);
        renderer(ModEntities.DASPLETOSAURUS, "daspletosaurus", Daspletosaurus.MODEL_SCALE, Daspletosaurus.SHADOW);
        renderer(ModEntities.ALBERTOSAURUS, "albertosaurus", Albertosaurus.MODEL_SCALE, Albertosaurus.SHADOW);
        renderer(ModEntities.MAJUNGASAURUS, "majungasaurus", Majungasaurus.MODEL_SCALE, Majungasaurus.SHADOW);
        renderer(ModEntities.DAKOTARAPTOR, "dakotaraptor", Dakotaraptor.MODEL_SCALE, Dakotaraptor.SHADOW);
        renderer(ModEntities.TROODON, "troodon", Troodon.MODEL_SCALE, Troodon.SHADOW);
        renderer(ModEntities.OVIRAPTOR, "oviraptor", Oviraptor.MODEL_SCALE, Oviraptor.SHADOW);
        renderer(ModEntities.CITIPATI, "citipati", Citipati.MODEL_SCALE, Citipati.SHADOW);
        renderer(ModEntities.MONONYKUS, "mononykus", Mononykus.MODEL_SCALE, Mononykus.SHADOW);
        renderer(ModEntities.DIDELPHODON, "didelphodon", Didelphodon.MODEL_SCALE, Didelphodon.SHADOW);
        renderer(ModEntities.PARASAUROLOPHUS, "parasaurolophus", Parasaurolophus.MODEL_SCALE, Parasaurolophus.SHADOW);
        renderer(ModEntities.PACHYCEPHALOSAURUS, "pachycephalosaurus", Pachycephalosaurus.MODEL_SCALE, Pachycephalosaurus.SHADOW);
        renderer(ModEntities.THESCELOSAURUS, "thescelosaurus", Thescelosaurus.MODEL_SCALE, Thescelosaurus.SHADOW);
        renderer(ModEntities.GALLIMIMUS, "gallimimus", Gallimimus.MODEL_SCALE, Gallimimus.SHADOW);
        renderer(ModEntities.STRUTHIOMIMUS, "struthiomimus", Struthiomimus.MODEL_SCALE, Struthiomimus.SHADOW);
        renderer(ModEntities.MAIASAURA, "maiasaura", Maiasaura.MODEL_SCALE, Maiasaura.SHADOW);
        renderer(ModEntities.EDMONTOSAURUS, "edmontosaurus", Edmontosaurus.MODEL_SCALE, Edmontosaurus.SHADOW);
        renderer(ModEntities.CORYTHOSAURUS, "corythosaurus", Corythosaurus.MODEL_SCALE, Corythosaurus.SHADOW);
        renderer(ModEntities.PTERANODON, "pteranodon", Pteranodon.MODEL_SCALE, Pteranodon.SHADOW);
        renderer(ModEntities.QUETZALCOATLUS, "quetzalcoatlus", Quetzalcoatlus.MODEL_SCALE, Quetzalcoatlus.SHADOW);
        renderer(ModEntities.HATZEGOPTERYX, "hatzegopteryx", Hatzegopteryx.MODEL_SCALE, Hatzegopteryx.SHADOW);
        renderer(ModEntities.ICHTHYORNIS, "ichthyornis", Ichthyornis.MODEL_SCALE, Ichthyornis.SHADOW);
        renderer(ModEntities.MOSASAURUS, "mosasaurus", Mosasaurus.MODEL_SCALE, Mosasaurus.SHADOW);
        renderer(ModEntities.TYLOSAURUS, "tylosaurus", Tylosaurus.MODEL_SCALE, Tylosaurus.SHADOW);
        renderer(ModEntities.ELASMOSAURUS, "elasmosaurus", Elasmosaurus.MODEL_SCALE, Elasmosaurus.SHADOW);
        renderer(ModEntities.XIPHACTINUS, "xiphactinus", Xiphactinus.MODEL_SCALE, Xiphactinus.SHADOW);
        renderer(ModEntities.ARCHELON, "archelon", Archelon.MODEL_SCALE, Archelon.SHADOW);
        renderer(ModEntities.HESPERORNIS, "hesperornis", Hesperornis.MODEL_SCALE, Hesperornis.SHADOW);
        renderer(ModEntities.DEINOSUCHUS, "deinosuchus", Deinosuchus.MODEL_SCALE, Deinosuchus.SHADOW);
        renderer(ModEntities.BAURUSUCHUS, "baurusuchus", Baurusuchus.MODEL_SCALE, Baurusuchus.SHADOW);
        // END GENERATED renderers
        EntityRendererRegistry.register(ModEntities.SPEAR, ThrownSpearRenderer::new);
        EntityRendererRegistry.register(ModEntities.CARCASS, CarcassRenderer::new);
        ClientHooks.init();
        BuildingBlocksClient.init();
        TerrassicMenuScreen.register(); // the Terrassic main menu (docs/MENU.md)
    }

    private static <T extends DinosaurEntity> void renderer(RegistrySupplier<EntityType<T>> type, String id, float scale, float shadow) {
        MODEL_SCALES.put(id, scale);
        EntityRendererRegistry.register(type, context -> new DinosaurRenderer<T>(context, id, scale, shadow));
    }
}
