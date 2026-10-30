package com.terrassic.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.research.GuideSpecies;
import com.terrassic.research.Knowledge;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientPlayerEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * The Terrassic HUD (ESCOPO.md "HUD próprio"; v0.8, phase M5), drawn with the mod's own models, live:
 * <ul>
 *   <li><b>Mount panel</b> (top left, while riding a dinosaur): portrait, name, health, hunger, cargo and sleep.</li>
 *   <li><b>Pack bar</b> (under it): up to 6 tamed dinosaurs of yours within 48 blocks, each with health and state
 *       (following, sitting, fighting, sleeping), like a Cobblemon party.</li>
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
    private static final int FOLLOW = 0;
    private static final int SIT = 1;
    private static final int FIGHT = 2;
    private static final int SLEEP = 3;
    private static final int CARGO = 4;
    private static final int PANEL = com.terrassic.client.ui.TerrassicPalette.alpha(com.terrassic.client.ui.TerrassicPalette.BASALT_800, 0xD0);
    private static final int EDGE = com.terrassic.client.ui.TerrassicPalette.AMBER_700;
    private static final int PAPER = com.terrassic.client.ui.TerrassicPalette.rgb(com.terrassic.client.ui.TerrassicPalette.BONE_100);

    private static Map<String, Integer> levels;
    private static Knowledge seenAtJoin;
    private static int baselineDelay;
    private static int titleDelay = -1;
    private static String titleEra;
    private static int tick;

    private TerrassicHud() {
    }

    public static void init() {
        ClientGuiEvent.RENDER_HUD.register(TerrassicHud::render);
        ClientTickEvent.CLIENT_POST.register(TerrassicHud::tick);
        ClientPlayerEvent.CLIENT_PLAYER_JOIN.register(player -> {
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
        int y = 4;
        Entity vehicle = player.getVehicle();
        if (ClientConfig.flag("hud_mount") && vehicle instanceof DinosaurEntity mount) {
            y += mountCard(g, mc.font, mount, 4, y);
        }
        if (ClientConfig.flag("hud_pack")) {
            List<DinosaurEntity> pack = mc.level.getEntitiesOfClass(DinosaurEntity.class, player.getBoundingBox().inflate(48.0D),
                    d -> d.isTame() && d != vehicle && player.getUUID().equals(d.getOwnerUUID()) && d.isAlive());
            pack.sort(Comparator.comparingDouble(player::distanceToSqr));
            for (int i = 0; i < Math.min(6, pack.size()); i++) {
                packCard(g, pack.get(i), 4, y + i * 30);
            }
        }
        float storm = RiftStormClient.intensity(partialTick);
        if (ClientConfig.flag("hud_rift_alert") && storm > 0.05F) {
            riftAlert(g, mc.font, storm, g.guiWidth());
        }
    }

    private static void frame(GuiGraphics g, int x0, int y0, int x1, int y1) {
        g.fill(x0, y0, x1, y1, PANEL);
        g.fill(x0, y0, x1, y0 + 1, EDGE);
        g.fill(x0, y1 - 1, x1, y1, EDGE);
        g.fill(x0, y0, x0 + 1, y1, EDGE);
        g.fill(x1 - 1, y0, x1, y1, EDGE);
    }

    private static void icon(GuiGraphics g, int index, int x, int y) {
        g.blit(ICONS, x, y, index * 8.0F, 0.0F, 8, 8, 64, 32);
    }

    private static void bar(GuiGraphics g, int x, int y, int width, float fraction, int colour) {
        g.fill(x, y, x + width, y + 4, com.terrassic.client.ui.TerrassicPalette.BASALT_950);
        g.fill(x, y, x + Math.round(width * Mth.clamp(fraction, 0.0F, 1.0F)), y + 4, colour);
        g.fill(x, y, x + Math.round(width * Mth.clamp(fraction, 0.0F, 1.0F)), y + 1, (colour & 0x00FFFFFF) | 0x60FFFFFF);
    }

    // ------------------------------------------------------------------ mount panel

    /** The mount panel: a 24 px portrait, the name, health with numbers, food, and the state icons beside it
     *  (the vanilla mount hearts are hidden for our dinosaurs: mixin/client/GuiMixin, forge/MountHudForge). */
    private static int mountCard(GuiGraphics g, Font font, DinosaurEntity d, int x, int y) {
        int w = 124;
        frame(g, x, y, x + w, y + 32);
        g.fill(x + 3, y + 3, x + 29, y + 29, com.terrassic.client.ui.TerrassicPalette.BASALT_950);
        portrait(g, d, x + 4, y + 4, 24);
        g.drawString(font, com.terrassic.client.ui.TerrassicFonts.ui(d.getDisplayName()), x + 33, y + 3, PAPER, false);
        int bx = x + 33;
        int bw = w - 37;
        bar(g, bx, y + 14, bw, d.getHealth() / d.getMaxHealth(), com.terrassic.client.ui.TerrassicPalette.BLOOD_500);
        String value = Mth.ceil(d.getHealth()) + "/" + Mth.ceil(d.getMaxHealth());
        g.pose().pushPose();
        g.pose().translate(bx + bw - font.width(value) * 0.75F, y + 19, 0.0F);
        g.pose().scale(0.75F, 0.75F, 1.0F);
        g.drawString(font, value, 0, 0, com.terrassic.client.ui.TerrassicPalette.rgb(com.terrassic.client.ui.TerrassicPalette.STONE_200), true);
        g.pose().popPose();
        bar(g, bx, y + 26, bw, d.getHunger() / (float) DinosaurEntity.MAX_HUNGER, com.terrassic.client.ui.TerrassicPalette.AMBER_600);
        status(g, d, x + w + 3, y + 3);
        return 36;
    }

    /** The little state icons beside the mount panel: cargo and sleep. */
    private static void status(GuiGraphics g, DinosaurEntity d, int x, int y) {
        if (d.hasCargo()) {
            icon(g, CARGO, x, y);
            y += 10;
        }
        if (d.isSleeping()) {
            icon(g, SLEEP, x, y);
        }
    }

    private static void packCard(GuiGraphics g, DinosaurEntity d, int x, int y) {
        frame(g, x, y, x + 28, y + 28);
        portrait(g, d, x + 2, y + 2, 24);
        bar(g, x + 2, y + 23, 24, d.getHealth() / d.getMaxHealth(), com.terrassic.client.ui.TerrassicPalette.BLOOD_500);
        int state = d.isSleeping() ? SLEEP : d.isAggressive() ? FIGHT : d.isInSittingPose() ? SIT : FOLLOW;
        icon(g, state, x + 19, y + 1);
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
        Vector3f b = m.transformPosition(new Vector3f(x + size, y + size, 0.0F));
        g.enableScissor(Math.round(a.x()), Math.round(a.y()), Math.round(b.x()), Math.round(b.y()));
        try {
            InventoryScreen.renderEntityInInventory(g, x + size / 2, y + size - 3, scale,
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

    private static void tick(Minecraft mc) {
        tick++;
        if (mc.player == null || mc.level == null) {
            return;
        }
        if (titleDelay > 0 && mc.screen == null) {
            if (--titleDelay == 0 && ClientConfig.flag("hud_era_title") && titleEra != null) {
                mc.gui.setTimes(10, 70, 20);
                mc.gui.setSubtitle(com.terrassic.client.ui.TerrassicFonts.ui(ClientResearch.story()
                        ? "menu.terrassic.subtitle" : "hud.terrassic.era." + titleEra + ".when"));
                mc.gui.setTitle(com.terrassic.client.ui.TerrassicFonts.title(Component.translatable("hud.terrassic.era." + titleEra)));
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
