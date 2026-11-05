package com.terrassic.config;

import com.terrassic.research.GuideSpecies;

import java.util.HashSet;
import java.util.Set;

/**
 * The eras whose creatures live in the world. Since v0.10 only the Cretaceous is on; the Jurassic species already in
 * the mod (Stegosaurus, Brachiosaurus, Dilophosaurus, Compsognathus) stay registered, so saved worlds keep them, but
 * they do not spawn and are left out of the creative tabs, the Field Guide and the fossil drops. They come back with
 * their era.
 *
 * <p>v1.5: inside the active eras, only the species remade one by one ({@link #REMADE}) live in the world. The others
 * still have their old model; they are off the same way as the Jurassic ones (registered, saved worlds keep them) until
 * each one is remade and added here. WorldConfig "especies_antigas": true turns them back on.
 */
public final class Eras {
    public static final Set<String> ACTIVE = Set.of("late_cretaceous", "early_cretaceous");
    /** Species with their new model and own study (docs/CORES.md). Add each one here when it is remade. */
    public static final Set<String> REMADE = Set.of(
            "tyrannosaurus", "carnotaurus", "giganotosaurus", "protoceratops",
            "spinosaurus", "velociraptor", "pteranodon", "triceratops", "gallimimus", "pachycephalosaurus",
            "parasaurolophus", "ankylosaurus", "mosasaurus", "styracosaurus", "deinosuchus", "elasmosaurus");
    private static final Set<String> OFF_SPECIES = new HashSet<>();

    static {
        boolean old = WorldConfig.oldSpecies();
        for (GuideSpecies s : GuideSpecies.ALL) {
            if (!ACTIVE.contains(s.era()) || (!old && !REMADE.contains(s.id()))) {
                OFF_SPECIES.add(s.id());
            }
        }
    }

    private Eras() {
    }

    /** Whether the species lives in the world now (unknown ids count as active). */
    public static boolean active(String species) {
        return !OFF_SPECIES.contains(species);
    }

    public static boolean active(GuideSpecies species) {
        return !OFF_SPECIES.contains(species.id());
    }

    /**
     * Whether an item or block named after a species belongs to an active era: "stegosaurus_skull_trophy" or
     * "cave_painting_brachiosaurus" do not, "tyrannosaurus_saddle" or "thatch" do. Species ids have no underscore.
     */
    public static boolean activeName(String id) {
        for (String part : id.split("_")) {
            if (OFF_SPECIES.contains(part)) {
                return false;
            }
        }
        return true;
    }
}
