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
        if (ClientConfig.flag("hud_mount") && player.getVehicle() instanceof DinosaurEntity mount) {
            if (compact) {
                compactMount(g, mc, mount);
            } else {
                mountPlate(g, mc.font, mount, 4, 4);
            }
        }
        HudNotices.render(g, mc.font, partialTick, compact);
        if (titleAge >= 0 && titleEra != null) {
            eraTitle(g, mc.font, partialTick);
        }
        float storm = RiftStormClient.intensity(partialTick);
        if (ClientConfig.flag("hud_rift_alert") && storm > 0.05F) {
            riftAlert(g, mc.font, storm, g.guiWidth());
        }
    }

    /**
     * The era title, drawn here instead of the vanilla title: the "Entalhe" letters are wider than the vanilla font,
     * so the vanilla title (4x) ran off both sides of the screen. Same place and fade, scaled down to fit when needed.
     */
    private static void eraTitle(GuiGraphics g, Font font, float partialTick) {
        float age = titleAge + partialTick;
        float alpha = age < TITLE_IN ? age / TITLE_IN
                : age < TITLE_IN + TITLE_HOLD ? 1.0F : 1.0F - (age - TITLE_IN - TITLE_HOLD) / TITLE_OUT;
        int a = Mth.clamp((int) (alpha * 255.0F), 0, 255);
        if (a <= 8) {
            return;
        }
        Component title = com.terrassic.client.ui.TerrassicFonts.title(Component.translatable("hud.terrassic.era." + titleEra));
        Component subtitle = com.terrassic.client.ui.TerrassicFonts.ui(ClientResearch.story()
                ? "menu.terrassic.subtitle" : "hud.terrassic.era." + titleEra + ".when");
        int room = g.guiWidth() - 32;
        g.pose().pushPose();
        g.pose().translate(g.guiWidth() / 2.0F, g.guiHeight() / 2.0F, 0.0F);
        float big = Math.min(4.0F, room / (float) Math.max(1, font.width(title)));
        g.pose().pushPose();
        g.pose().scale(big, big, big);
        g.drawString(font, title, -font.width(title) / 2, -10, 0xFFFFFF | a << 24, true);
        g.pose().popPose();
        float small = Math.min(2.0F, room / (float) Math.max(1, font.width(subtitle)));
        g.pose().pushPose();
        g.pose().translate(0.0F, 2.0F, 0.0F);
        g.pose().scale(small, small, small);
        g.drawString(font, subtitle, -font.width(subtitle) / 2, 5, 0xFFFFFF | a << 24, true);
        g.pose().popPose();
        g.pose().popPose();
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
