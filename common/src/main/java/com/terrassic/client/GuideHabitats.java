package com.terrassic.client;

import com.terrassic.Terrassic;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;

import java.util.HashMap;
import java.util.Map;

/**
 * The habitat diorama behind the live model on a Field Guide page (docs/MENU.md, "Guia de Campo"): six 3D block
 * scenes without animals, rendered by tools/menugen/habitats.py and printed as a faint ink engraving on the notebook
 * paper, so the coloured model in front reads first. Species not listed here stand on the plains.
 */
public final class GuideHabitats {
    /** Texture size: 4x the picture box of the Guide page (186 x 72 GUI pixels). */
    private static final int TEX_W = 744;
    private static final int TEX_H = 288;
    private static final String DEFAULT = "planicie";
    private static final Map<String, String> HABITAT = new HashMap<>();

    static {
        put("floresta", "tyrannosaurus", "tarbosaurus", "daspletosaurus", "albertosaurus", "dakotaraptor", "troodon",
                "thescelosaurus", "didelphodon", "mesodma", "dilophosaurus", "compsognathus", "stegosaurus",
                "brachiosaurus");
        put("planicie", "triceratops", "styracosaurus", "pachyrhinosaurus", "leptoceratops", "ankylosaurus",
                "euoplocephalus", "pachycephalosaurus", "gallimimus", "struthiomimus", "maiasaura", "edmontosaurus",
                "corythosaurus", "parasaurolophus", "alamosaurus");
        put("rio", "spinosaurus", "carcharodontosaurus", "deinosuchus", "basilemys", "lepisosteus", "therizinosaurus",
                "deinocheirus");
        put("seco", "velociraptor", "protoceratops", "oviraptor", "citipati", "mononykus", "saltasaurus",
                "argentinosaurus", "dreadnoughtus", "opisthocoelicaudia", "giganotosaurus", "carnotaurus",
                "majungasaurus", "baurusuchus");
        put("litoral", "pteranodon", "quetzalcoatlus", "hatzegopteryx", "ichthyornis", "hesperornis", "vegavis");
        put("mar", "mosasaurus", "tylosaurus", "elasmosaurus", "xiphactinus", "enchodus", "archelon");
    }

    private GuideHabitats() {
    }

    private static void put(String habitat, String... species) {
        for (String id : species) {
            HABITAT.put(id, habitat);
        }
    }

    /** The diorama texture of a species. */
    public static ResourceLocation texture(String speciesId) {
        return Terrassic.id("textures/gui/notebook/habitat_" + HABITAT.getOrDefault(speciesId, DEFAULT) + ".png");
    }

    /** Draws the diorama of a species filling the box (x, y, w, h), cropped to keep its centre. */
    public static void render(GuiGraphics g, String speciesId, int x, int y, int w, int h) {
        float scale = Math.max(w / (float) TEX_W, h / (float) TEX_H);
        int cw = Math.round(w / scale);
        int ch = Math.round(h / scale);
        g.blit(texture(speciesId), x, y, w, h, (TEX_W - cw) / 2.0F, (TEX_H - ch) / 2.0F, cw, ch, TEX_W, TEX_H);
    }
}
