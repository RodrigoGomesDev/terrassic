package com.terrassic.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.terrassic.Terrassic;
import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.research.GuideSpecies;
import com.terrassic.research.Knowledge;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientPlayerEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.HashMap;
import java.util.Map;

/**
 * The Terrassic HUD (ESCOPO.md "HUD próprio"; v0.8, phase M5; "Âmbar" look since v0.14, docs/HUD.md), drawn with the
 * mod's own models, live. The player's own health, food, XP and jump bar stay vanilla:
 * <ul>
 *   <li><b>Mount plate</b> (top left, while riding a dinosaur): the animal in a drop of amber, its name and level,
 *       health and food cut into the stone, the health in numbers for three seconds when it changes, and the key
 *       socket of its special filling up while it recharges. The compact style ("hud_style": "compact") draws ten
 *       vanilla mount hearts above the food bar instead (10% each) and the special as a line of text.</li>
 *   <li><b>Notices</b> (middle of the right edge): what happens to any of your animals ({@link HudNotices}). They
 *       replace the old pack bar of six portraits: a player can have twenty dinosaurs.</li>
 *   <li><b>New species</b>: a toast with the portrait when a species reaches a new Field Guide level
 *       ({@link SpeciesToast}).</li>
 *   <li><b>Era title</b>: "Late Cretaceous" the first time you are in the era, once per player and world (the server
 *       keeps it and sends ModNetwork.ERA_TITLE); the line under it names the chapter only with the story mode on.</li>
 *   <li><b>Rift alert</b>: a pulsing cracked amber shard (top centre) while a Rift Storm is on.</li>
 * </ul>
 * Each part can be turned off in config/terrassic-client.json; F1 hides everything, like the vanilla HUD.
 */
public final class TerrassicHud {
    public static final ResourceLocation ICONS = Terrassic.id("textures/gui/hud.png");
    private static final ResourceLocation VANILLA_ICONS = new ResourceLocation("textures/gui/icons.png");
    /** Ticks the health number stays on the plate after the health changed. */
    private static final int NUMBER_TICKS = 60;

    private static Map<String, Integer> levels;
    private static Knowledge seenAtJoin;
    private static int baselineDelay;
    private static int titleDelay = -1;
    private static String titleEra;
    /** Ticks since the era title came up (-1 = none); fades like a vanilla title: 10 in, 70 held, 20 out. */
    private static int titleAge = -1;
    private static final int TITLE_IN = 10;
    private static final int TITLE_HOLD = 70;
    private static final int TITLE_OUT = 20;
    private static int tick;
    private static int numberMount = -1;
    private static float numberHealth;
    private static int numberLeft;

    private TerrassicHud() {
    }

    public static void init() {
        ClientGuiEvent.RENDER_HUD.register(TerrassicHud::render);
        ClientTickEvent.CLIENT_POST.register(TerrassicHud::tick);
        ClientPlayerEvent.CLIENT_PLAYER_JOIN.register(player -> {
            HudNotices.clear();
            levels = null;
            seenAtJoin = ClientResearch.get();
            baselineDelay = 20;  // x10 ticks: at most 10 s waiting for the server's Knowledge sync
        });
    }

    /** The server says this is the player's first time in the era: its title, 3 s after the world (and any screen) is up. */
    static void showEraTitle(String era) {
        titleEra = era;
        titleDelay = 60;
    }

    // ------------------------------------------------------------------ drawing

    private static void render(GuiGraphics g, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || mc.level == null || mc.options.hideGui) {
            return;
        }
        boolean compact = ClientConfig.compactHud();
        // the plate and the notices are drawn one HUD step smaller than the GUI (Rodrigo 30/10: GUI 3 -> HUD 2)
        float k = ClientConfig.hudScale(mc) / (float) mc.getWindow().getGuiScale();
        int hw = Math.round(g.guiWidth() / k);
        int hh = Math.round(g.guiHeight() / k);
        g.pose().pushPose();
        g.pose().scale(k, k, 1.0F);
        if (ClientConfig.flag("hud_mount") && player.getVehicle() instanceof DinosaurEntity mount && !compact) {
            mountPlate(g, mc.font, mount, 4, 4);
        }
        HudNotices.render(g, mc.font, partialTick, compact, hw, hh);
        g.pose().popPose();
        if (ClientConfig.flag("hud_mount") && player.getVehicle() instanceof DinosaurEntity mount && compact) {
            compactMount(g, mc, mount);  // beside the vanilla food bar, at the GUI's own scale
        }
        if (titleAge >= 0 && titleEra != null) {
            eraTitle(g, mc.font, partialTick);
        }
        float storm = RiftStormClient.intensity(partialTick);
        if (ClientConfig.flag("hud_rift_alert") && storm > 0.05F) {
            riftAlert(g, mc.font, storm, g.guiWidth());
        }
    }

    /**
     * The era title (v0.14.2, docs/HUD.md; study: dirB.py scene_title()): a cut through the rock layers across the
     * screen, soil, clay and ash over a thick band of amber with the era's name carved in it, chalk and basalt under
     * it, the ends crumbling away; a little ammonite in the chalk and a bone in the clay, and the date under it.
     * Drawn here instead of the vanilla title, with its fade: 10 ticks in, 70 held, 20 out.
     */
    private static void eraTitle(GuiGraphics g, Font font, float partialTick) {
        float age = titleAge + partialTick;
        float alpha = age < TITLE_IN ? age / TITLE_IN
                : age < TITLE_IN + TITLE_HOLD ? 1.0F : 1.0F - (age - TITLE_IN - TITLE_HOLD) / TITLE_OUT;
        int a = Mth.clamp((int) (alpha * 255.0F), 0, 255);
        if (a <= 8) {
            return;
        }
        int w = g.guiWidth();
        int top = g.guiHeight() / 2 - 36;
        int half = w / 2 + 2;
        RenderSystem.enableBlend();
        g.setColor(1.0F, 1.0F, 1.0F, a / 255.0F);
        AmberHud.picture(g, "era_strata_" + w, w / 2 - half, top - STRATA_PAD, half * 2, STRATA_H + STRATA_PAD * 2,
                () -> strata(half, 2));
        AmberHud.icon(g, AMMONITE, w / 2 + 150, top + 36, 0xFFF7F2E6, 0xFFB5AE9A, 0xFF5A5040);
        AmberHud.icon(g, BONE, w / 2 - 170, top + 3, TerrassicPalette.BONE_100, TerrassicPalette.STONE_300, TerrassicPalette.BASALT_600);
        g.setColor(1.0F, 1.0F, 1.0F, 1.0F);
        // the name carved in the amber: dark letters with a lit lower lip
        Component title = com.terrassic.client.ui.TerrassicFonts.title(Component.translatable("hud.terrassic.era." + titleEra));
        float big = Math.min(2.0F, (w - 48) / (float) Math.max(1, font.width(title)));
        float tx = (w - font.width(title) * big) / 2.0F;
        float ty = top + 15 + (2.0F - big) * 4.0F;
        for (int pass = 0; pass < 2; pass++) {
            g.pose().pushPose();
            g.pose().translate(tx, ty + (pass == 0 ? 1.0F : 0.0F), 0.0F);
            g.pose().scale(big, big, 1.0F);
            g.drawString(font, title, 0, 0, (pass == 0 ? 0xFFD27A : 0x4A2A08) | a << 24, false);
            g.pose().popPose();
        }
        Component subtitle = com.terrassic.client.ui.TerrassicFonts.ui(ClientResearch.story()
                ? "menu.terrassic.subtitle" : "hud.terrassic.era." + titleEra + ".when");
        int sx = (w - font.width(subtitle)) / 2;
        g.drawString(font, subtitle, sx + 1, top + 53, TerrassicPalette.rgb(TerrassicPalette.BASALT_950) | a << 24, false);
        g.drawString(font, subtitle, sx, top + 52, TerrassicPalette.rgb(TerrassicPalette.BONE_100) | a << 24, false);
    }

    private static final String[] AMMONITE = {".sss.", "s+++s", "s+s+s", "s++ss", ".sss."};
    private static final String[] BONE = {"+...+", "s+++s", "+...+"};
    /** The rock layers of the title, top to bottom: thickness, then light, mid and dark tones. */
    private static final int[][] LAYERS = {
            {3, 0xFF7A6650, 0xFF5B4636, 0xFF46362A},          // soil
            {4, 0xFFC2A672, 0xFFA08458, 0xFF86683F},          // clay
            {2, 0xFF6E6A62, 0xFF57534C, 0xFF45413B},          // ash
            {28, TerrassicPalette.AMBER_300, TerrassicPalette.AMBER_600, TerrassicPalette.AMBER_700},
            {3, 0xFFF2EEE2, 0xFFDCD6C4, 0xFFBDB6A2},          // chalk
            {4, TerrassicPalette.BASALT_500, TerrassicPalette.BASALT_700, TerrassicPalette.BASALT_800},
            {3, TerrassicPalette.BASALT_600, TerrassicPalette.BASALT_800, TerrassicPalette.BASALT_900}};
    private static final int STRATA_H = 47;
    private static final int STRATA_PAD = 3;

    /** The cut through the layers (study: common.py strata(), fade 0.8, wave 0.6, specks 0.08), 2 x half wide. */
    private static int[] strata(int half, int seed) {
        int w = half * 2;
        int h = STRATA_H + STRATA_PAD * 2;
        int[] px = new int[w * h];
        java.util.Random rnd = new java.util.Random(seed);
        double fade = 0.8D;
        double wave = 0.6D;
        int edge = 0xC80E0B0E;
        for (int i = 0; i < w; i++) {
            double d = Math.abs(i - half) / (double) half;
            double crumble = d > fade ? (d - fade) / (1.0D - fade) * 1.15D : 0.0D;
            int y0 = STRATA_PAD + (int) Math.round(wave * Math.sin(i * 0.07D + seed));
            int y = y0;
            for (int l = 0; l < LAYERS.length; l++) {
                int t = LAYERS[l][0];
                int off = (int) Math.round(wave * 0.8D * Math.sin(i * (0.05D + 0.02D * l) + l * 1.7D));
                int tt = l < LAYERS.length - 1 ? Math.max(1, t + off) : t;
                for (int k = 0; k < tt; k++) {
                    if (crumble > 0.0D && rnd.nextDouble() < crumble) {
                        continue;
                    }
                    int c = k == 0 ? LAYERS[l][1] : rnd.nextDouble() < 0.08D ? LAYERS[l][3] : LAYERS[l][2];
                    if (y + k >= 0 && y + k < h) {
                        px[(y + k) * w + i] = c;
                    }
                }
                y += tt;
            }
            if (!(crumble > 0.0D && rnd.nextDouble() < crumble)) {
                if (y0 - 1 >= 0) {
                    px[(y0 - 1) * w + i] = edge;
                }
                if (y < h) {
                    px[y * w + i] = edge;
                }
            }
        }
        // a softer, lighter core in the amber, where the letters sit
        int amberTop = STRATA_PAD + 3 + 4 + 2;
        for (int y = amberTop + 7; y < amberTop + 16; y++) {
            for (int i = 40; i < w - 40; i++) {
                if (px[y * w + i] == TerrassicPalette.AMBER_600 && rnd.nextBoolean()) {
                    px[y * w + i] = TerrassicPalette.AMBER_500;
                }
            }
        }
        return px;
    }

    // ------------------------------------------------------------------ mount plate

    /**
     * The mount plate (study: dirF.py plate()): a slab 145 wide, wider for a long name, with the animal in a drop of
     * amber hanging over its left edge. Two rows for now, health and food; the third, stamina, comes with the mount
     * stamina. The key socket on the right is the special (the loud roar), if the animal has one.
     */
    private static void mountPlate(GuiGraphics g, Font font, DinosaurEntity d, int x, int y) {
        Component name = d.hasCustomName() ? d.getCustomName() : d.getType().getDescription();
        Component dot = Component.literal(name.getString() + " · ");
        Component level = Component.translatable("hud.terrassic.level", Math.max(1, d.getLevel()));
        int extra = Math.max(0, 34 + AmberHud.width(font, dot) + AmberHud.width(font, level) + 6 - 145);
        AmberHud.slab(g, "mount_plate_" + extra, x, y, 14, 0, 112 + extra, 0, 116 + extra, 3, 141 + extra, 3, 144 + extra, 7,
                144 + extra, 32, 139 + extra, 37, 70, 37, 66, 35, 14, 35);
        for (int i = 0; i < 9; i++) {  // an amber seam where the slab broke
            int c = i % 4 != 0 ? TerrassicPalette.AMBER_700 : TerrassicPalette.AMBER_500;
            g.fill(x + 126 + extra + i, y + 34 - i / 3, x + 127 + extra + i, y + 35 - i / 3, c);
        }
        AmberHud.amberDrop(g, x + 15, y + 19, 15, 15, 5, () -> portrait(g, d, x + 1, y + 7, 28, 26));
        int nx = AmberHud.text(g, font, dot, x + 34, y + 5, TerrassicPalette.BONE_100);
        AmberHud.text(g, font, level, nx, y + 5, TerrassicPalette.AMBER_500);
        AmberHud.icon(g, AmberHud.HEART, x + 33, y + 16, 0xFFF08A70, TerrassicPalette.BLOOD_500);
        AmberHud.groove(g, x + 41, y + 17, 62, d.getHealth() / d.getMaxHealth(), AmberHud.RED);
        AmberHud.icon(g, AmberHud.MEAT, x + 33, y + 24, TerrassicPalette.BONE_100, 0xFFB5453A);
        AmberHud.groove(g, x + 41, y + 25, 62, d.getHunger() / (float) DinosaurEntity.MAX_HUNGER, AmberHud.AMBER);
        if (numberLeft > 0 || ClientConfig.flag("hud_numbers_always")) {
            AmberHud.text(g, font, Component.literal(Mth.ceil(d.getHealth()) + "/" + Mth.ceil(d.getMaxHealth())),
                    x + 106, y + 14, TerrassicPalette.BONE_100);
        }
        float charge = d.specialCharge();
        if (charge >= 0.0F) {
            AmberHud.chip(g, font, x + 108, y + 23, useKey(), charge);
        }
    }

    /** The compact style: ten vanilla mount hearts over the food bar (10% of the health each) and the special in a
     *  line of text over the hotbar. */
    private static void compactMount(GuiGraphics g, Minecraft mc, DinosaurEntity d) {
        int w = g.guiWidth();
        int h = g.guiHeight();
        int halves = Mth.ceil(Mth.clamp(d.getHealth() / d.getMaxHealth(), 0.0F, 1.0F) * 20.0F);
        // on Forge the hearts did not show without these two lines (Mac test of v0.14; most likely the depth test)
        RenderSystem.disableDepthTest();
        RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
        RenderSystem.enableBlend();
        for (int i = 0; i < 10; i++) {
            int hx = w / 2 + 91 - i * 8 - 9;
            int hy = h - 49;
            g.blit(VANILLA_ICONS, hx, hy, 52, 9, 9, 9);
            if (i * 2 + 1 < halves) {
                g.blit(VANILLA_ICONS, hx, hy, 88, 9, 9, 9);
            } else if (i * 2 + 1 == halves) {
                g.blit(VANILLA_ICONS, hx, hy, 97, 9, 9, 9);
            }
        }
        RenderSystem.enableDepthTest();
        float charge = d.specialCharge();
        if (charge >= 0.0F && d.specialName() != null) {
            Component special = Component.translatable("hud.terrassic.special." + d.specialName());
            Component line = charge >= 1.0F ? Component.translatable("hud.terrassic.special.ready", special)
                    : Component.translatable("hud.terrassic.special.wait", special, Mth.ceil(d.specialTicksLeft() / 20.0F));
            AmberHud.text(g, mc.font, line, (w - AmberHud.width(mc.font, line)) / 2, h - 60, TerrassicPalette.STONE_200);
        }
    }

    /** The use key's letter for the key socket, or null when it is a mouse button (the socket then shows a mouse). */
    private static String useKey() {
        KeyMapping use = Minecraft.getInstance().options.keyUse;
        if (use.saveString().startsWith("key.mouse")) {
            return null;
        }
        String k = use.getTranslatedKeyMessage().getString();
        return k.isEmpty() ? null : k.substring(0, 1).toUpperCase(java.util.Locale.ROOT);
    }

    private static void riftAlert(GuiGraphics g, Font font, float intensity, int width) {
        float pulse = 0.55F + 0.45F * Mth.sin(tick * 0.25F);
        RenderSystem.enableBlend();
        g.setColor(1.0F, 1.0F, 1.0F, Mth.clamp(intensity * pulse + 0.2F, 0.0F, 1.0F));
        g.blit(ICONS, width / 2 - 8, 3, 0.0F, 16.0F, 16, 16, 64, 32);
        g.setColor(1.0F, 1.0F, 1.0F, 1.0F);
        RenderSystem.disableBlend();
        g.drawCenteredString(font, com.terrassic.client.ui.TerrassicFonts.ui("hud.terrassic.rift_storm"), width / 2, 21, com.terrassic.client.ui.TerrassicPalette.rgb(com.terrassic.client.ui.TerrassicPalette.RIFT_500));
    }

    /** The live entity, scaled to fit a size x size box (by the species' real length), seen three-quarters. */
    static void portrait(GuiGraphics g, net.minecraft.world.entity.LivingEntity e, int x, int y, int size) {
        portrait(g, e, x, y, size, size);
    }

    /** The same in a w x h box (the drops of amber are taller than wide). */
    static void portrait(GuiGraphics g, net.minecraft.world.entity.LivingEntity e, int x, int y, int w, int h) {
        int size = Math.min(w, h);
        float length = e.getBbWidth();
        if (e instanceof DinosaurEntity d) {
            GuideSpecies s = GuideSpecies.byId(d.speciesId());
            if (s != null) {
                length = Math.max(length, s.length() * e.getScale());
            }
        }
        float extent = Math.max(length * 0.8F, e.getBbHeight());
        int scale = Math.max(1, (int) (size * 0.9F / Math.max(0.3F, extent)));
        float bodyRot = e.yBodyRot;
        float yRot = e.getYRot();
        float xRot = e.getXRot();
        float headO = e.yHeadRotO;
        float head = e.yHeadRot;
        e.yBodyRot = 210.0F;
        e.setYRot(210.0F);
        e.setXRot(0.0F);
        e.yHeadRot = 210.0F;
        e.yHeadRotO = 210.0F;
        // the scissor box is in screen coordinates and ignores the pose: move it with the pose (toasts are translated)
        Matrix4f m = g.pose().last().pose();
        Vector3f a = m.transformPosition(new Vector3f(x, y, 0.0F));
        Vector3f b = m.transformPosition(new Vector3f(x + w, y + h, 0.0F));
        g.enableScissor(Math.round(a.x()), Math.round(a.y()), Math.round(b.x()), Math.round(b.y()));
        try {
            InventoryScreen.renderEntityInInventory(g, x + w / 2, y + h - 3, scale,
                    new Quaternionf().rotateZ((float) Math.PI), null, e);
        } finally {
            g.disableScissor();
            e.yBodyRot = bodyRot;
            e.setYRot(yRot);
            e.setXRot(xRot);
            e.yHeadRotO = headO;
            e.yHeadRot = head;
        }
    }

    // ------------------------------------------------------------------ events

    /** The health number on the plate: three seconds after the ridden animal's health changed. */
    private static void numberTick(Minecraft mc) {
        if (numberLeft > 0) {
            numberLeft--;
        }
        if (!(mc.player.getVehicle() instanceof DinosaurEntity d)) {
            numberMount = -1;
            return;
        }
        if (d.getId() != numberMount) {
            numberMount = d.getId();
            numberHealth = d.getHealth();
            numberLeft = 0;
        } else if (Math.abs(d.getHealth() - numberHealth) >= 0.5F) {
            numberHealth = d.getHealth();
            numberLeft = NUMBER_TICKS;
        }
    }

    private static void tick(Minecraft mc) {
        tick++;
        if (mc.player == null || mc.level == null) {
            return;
        }
        if (!mc.isPaused()) {
            HudNotices.tick();
            numberTick(mc);
        }
        if (titleAge >= 0 && !mc.isPaused() && ++titleAge > TITLE_IN + TITLE_HOLD + TITLE_OUT) {
            titleAge = -1;
        }
        if (titleDelay > 0 && mc.screen == null) {
            if (--titleDelay == 0 && ClientConfig.flag("hud_era_title") && titleEra != null) {
                titleAge = 0;
            }
        }
        if (tick % 10 != 0) {
            return;
        }
        Knowledge k = ClientResearch.get();
        Map<String, Integer> now = new HashMap<>();
        for (GuideSpecies s : GuideSpecies.ALL) {
            now.put(s.id(), k.level(s.id()));
        }
        if (levels == null) {
            // right after joining only take the baseline, once the server's sync arrived (a new Knowledge object):
            // no toasts for what you already knew
            if (k != seenAtJoin || --baselineDelay <= 0) {
                levels = now;
            }
            return;
        }
        if (ClientConfig.flag("hud_new_species")) {
            for (Map.Entry<String, Integer> e : now.entrySet()) {
                if (e.getValue() > levels.getOrDefault(e.getKey(), 0)) {
                    mc.getToasts().addToast(new SpeciesToast(e.getKey(), e.getValue()));
                }
            }
        }
        levels = now;
    }
}
