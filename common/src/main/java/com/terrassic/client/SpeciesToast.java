package com.terrassic.client;

import com.terrassic.Terrassic;
import com.terrassic.research.Knowledge;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.toasts.Toast;
import net.minecraft.client.gui.components.toasts.ToastComponent;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;

import java.util.HashMap;
import java.util.Map;

/**
 * "New species" toast of the Terrassic HUD: the species' model, its name and the Field Guide level it just reached.
 * At the silhouette level (only a fossil studied) the name and the model stay hidden: "???".
 */
public final class SpeciesToast implements Toast {
    private static final Map<String, LivingEntity> MODELS = new HashMap<>();
    private final String species;
    private final int level;

    public SpeciesToast(String species, int level) {
        this.species = species;
        this.level = level;
    }

    @Override
    public Visibility render(GuiGraphics g, ToastComponent toasts, long time) {
        // the Terrassic look (docs/IDENTIDADE.md): a basalt slab, the portrait in a recessed frame
        com.terrassic.client.ui.TerrassicUi.slab(g, 0, 0, this.width(), this.height());
        com.terrassic.client.ui.TerrassicUi.well(g, 3, 3, 29, 29, false);
        String key = switch (this.level) {
            case Knowledge.SILHOUETTE -> "hud.terrassic.species.silhouette";
            case Knowledge.SIGHTED -> "hud.terrassic.species.sighted";
            case Knowledge.STUDIED -> "hud.terrassic.species.studied";
            default -> "hud.terrassic.species.tamed";
        };
        var font = toasts.getMinecraft().font;
        g.drawString(font, com.terrassic.client.ui.TerrassicFonts.ui(key), 33, 8, com.terrassic.client.ui.TerrassicPalette.rgb(com.terrassic.client.ui.TerrassicPalette.AMBER_500), false);
        Component name = this.level <= Knowledge.SILHOUETTE ? Component.literal("???")
                : Component.translatable("entity.terrassic." + this.species);
        g.drawString(font, com.terrassic.client.ui.TerrassicFonts.ui(name), 33, 19, com.terrassic.client.ui.TerrassicPalette.rgb(com.terrassic.client.ui.TerrassicPalette.BONE_100), false);
        LivingEntity model = this.level <= Knowledge.SILHOUETTE ? null : model(this.species);
        if (model != null) {
            TerrassicHud.portrait(g, model, 4, 4, 24);
        } else {
            g.drawString(font, "?", 14, 12, com.terrassic.client.ui.TerrassicPalette.rgb(com.terrassic.client.ui.TerrassicPalette.STONE_200), false);
        }
        return time >= 5000L ? Visibility.HIDE : Visibility.SHOW;
    }

    private static LivingEntity model(String species) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return null;
        }
        if (!MODELS.isEmpty() && MODELS.values().iterator().next().level() != mc.level) {
            MODELS.clear();  // a new world or dimension: drop the old models (they hold the old level)
        }
        LivingEntity cached = MODELS.get(species);
        if (cached != null) {
            return cached;
        }
        Entity e = BuiltInRegistries.ENTITY_TYPE.get(Terrassic.id(species)).create(mc.level);
        LivingEntity living = e instanceof LivingEntity l ? l : null;
        if (living != null) {
            MODELS.put(species, living);
        }
        return living;
    }
}
