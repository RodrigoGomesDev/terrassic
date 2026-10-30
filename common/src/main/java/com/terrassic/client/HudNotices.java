package com.terrassic.client;

import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.network.ModNetwork;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * The notices on the right of the HUD (v0.14, docs/HUD.md), in place of the pack bar: one slab per event about one of
 * your animals, whichever of your twenty dinos it is (level up, tamed, a baby hatched, hungry, woke up, died with its
 * coordinates). Up to four at a time in the middle of the right edge; each slides in, stays six seconds and slides
 * out. The server sends them (ModNetwork.NOTICE); with "hud_notices": false they go to the action bar as before.
 */
public final class HudNotices {
    private static final int SHOWN = 4;
    private static final int STAY = 120;
    private static final int SLIDE = 6;
    private static final int STEP = 34;
    private static final int COMPACT_STEP = 26;
    private static final int[] TONES = {TerrassicPalette.AMBER_500, TerrassicPalette.FERN_400, TerrassicPalette.RIFT_500,
            TerrassicPalette.BLOOD_500};
    private static final Deque<Notice> WAITING = new ArrayDeque<>();
    private static final List<Notice> SHOWING = new ArrayList<>();
    private static final Map<ResourceLocation, LivingEntity> MODELS = new HashMap<>();
    private static int seeds;

    private HudNotices() {
    }

    private static final class Notice {
        final int tone;
        final Component title;
        final Component line;
        final ResourceLocation species;
        final int seed;
        int age;

        Notice(int tone, Component title, Component line, ResourceLocation species, int seed) {
            this.tone = tone;
            this.title = title;
            this.line = line;
            this.species = species;
            this.seed = seed;
        }
    }

    static void add(int tone, Component title, Component line, ResourceLocation species) {
        Minecraft mc = Minecraft.getInstance();
        if (!ClientConfig.flag("hud_notices")) {
            mc.gui.setOverlayMessage(Component.empty().append(title).append(": ").append(line), false);
            return;
        }
        WAITING.add(new Notice(Mth.clamp(tone, ModNetwork.NOTICE_AMBER, ModNetwork.NOTICE_BLOOD), title, line, species,
                9 + seeds++ % 7));
    }

    static void tick() {
        // v0.14.5: they wait (hidden, not aging) while the Lupa card holds the same spot (Mac test, 30/10)
        if (LensOverlay.showing()) {
            return;
        }
        SHOWING.removeIf(n -> ++n.age > STAY);
        while (SHOWING.size() < SHOWN && !WAITING.isEmpty()) {
            SHOWING.add(WAITING.poll());
        }
    }

    static void clear() {
        SHOWING.clear();
        WAITING.clear();
        MODELS.clear();
    }

    /** Draws the notices in a w x h space (the HUD scale, see ClientConfig.hudScale). */
    static void render(GuiGraphics g, Font font, float partialTick, boolean compact, int w, int h) {
        if (SHOWING.isEmpty() || LensOverlay.showing()) {
            return;
        }
        int step = compact ? COMPACT_STEP : STEP;
        int y = (h - (SHOWING.size() * step - 4)) / 2 - 6;
        for (Notice n : SHOWING) {
            float age = n.age + partialTick;
            // slides in from the right edge and back out at the end
            float in = Mth.clamp(Math.min(age, STAY - age) / SLIDE, 0.0F, 1.0F);
            float out = (1.0F - in) * (1.0F - in);
            if (compact) {
                compact(g, font, n, w, y, out);
            } else {
                slab(g, font, n, w, y, out);
            }
            y += step;
        }
    }

    private static void slab(GuiGraphics g, Font font, Notice n, int screenW, int y, float out) {
        int w = Math.max(150, 30 + Math.max(AmberHud.width(font, n.title), AmberHud.width(font, n.line)) + 8);
        int x = screenW - w - 4 + Math.round(out * (w + 8));
        AmberHud.slab(g, "notice_" + w, x, y, 0, 3, 6, 0, w, 0, w, 26, w - 6, 30, 40, 30, 34, 28, 0, 28);
        LivingEntity model = model(n.species);
        AmberHud.amberDrop(g, x + 14, y + 15, 12, 11, n.seed,
                model == null ? null : () -> TerrassicHud.portrait(g, model, x + 3, y + 7, 22, 18));
        AmberHud.text(g, font, n.title, x + 30, y + 6, TONES[n.tone]);
        AmberHud.text(g, font, n.line, x + 30, y + 16, TerrassicPalette.BONE_100);
    }

    /** The compact HUD: no slab, the animal itself beside two lines of text, right-aligned. */
    private static void compact(GuiGraphics g, Font font, Notice n, int screenW, int y, float out) {
        int w = Math.max(AmberHud.width(font, n.title), AmberHud.width(font, n.line));
        int x = screenW - 4 - w + Math.round(out * (w + 40));
        LivingEntity model = model(n.species);
        if (model != null) {
            TerrassicHud.portrait(g, model, x - 28, y - 1, 26, 16);
        }
        AmberHud.text(g, font, n.title, x, y, TONES[n.tone]);
        AmberHud.text(g, font, n.line, x, y + 10, TerrassicPalette.BONE_100);
    }

    /** One model per species for the portraits (the animal itself may be far away and not loaded here). */
    private static LivingEntity model(ResourceLocation species) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return null;
        }
        if (!MODELS.isEmpty() && MODELS.values().iterator().next().level() != mc.level) {
            MODELS.clear();
        }
        LivingEntity cached = MODELS.get(species);
        if (cached == null && BuiltInRegistries.ENTITY_TYPE.containsKey(species)) {
            Entity e = BuiltInRegistries.ENTITY_TYPE.get(species).create(mc.level);
            if (e instanceof LivingEntity living) {
                cached = living;
                MODELS.put(species, living);
            }
        }
        return cached;
    }
}
