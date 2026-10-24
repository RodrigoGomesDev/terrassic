package com.terrassic.client;

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
import net.minecraft.world.level.Level;
import org.joml.Quaternionf;

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
 *   <li><b>Era title</b>: "Late Cretaceous / Chapter 1 · Echoes of the End" when you arrive in the world.</li>
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
    private static final int HUNGER = 5;
    private static final int HEART = 6;
    private static final int PANEL = 0xC0201620;
    private static final int EDGE = 0xFF8A6A4A;
    private static final int PAPER = 0xE8DCC0;

    private static Map<String, Integer> levels;
    private static int baselineDelay;
    private static int titleDelay = -1;
    private static int tick;

    private TerrassicHud() {
    }

    public static void init() {
        ClientGuiEvent.RENDER_HUD.register(TerrassicHud::render);
        ClientTickEvent.CLIENT_POST.register(TerrassicHud::tick);
        ClientPlayerEvent.CLIENT_PLAYER_JOIN.register(player -> {
            levels = null;
            baselineDelay = 4;  // x10 ticks: wait for the server's Knowledge sync before comparing
            titleDelay = 60;
        });
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
            mountPanel(g, mc.font, mount, 4, y);
            y += 50;
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
        g.fill(x, y, x + width, y + 4, 0xFF2A1A1E);
        g.fill(x, y, x + Math.round(width * Mth.clamp(fraction, 0.0F, 1.0F)), y + 4, colour);
        g.fill(x, y, x + Math.round(width * Mth.clamp(fraction, 0.0F, 1.0F)), y + 1, (colour & 0x00FFFFFF) | 0x60FFFFFF);
    }

    private static void mountPanel(GuiGraphics g, Font font, DinosaurEntity d, int x, int y) {
        frame(g, x, y, x + 132, y + 46);
        g.fill(x + 3, y + 3, x + 43, y + 43, 0xFF140E16);
        portrait(g, d, x + 3, y + 3, 40);
        g.drawString(font, d.getDisplayName(), x + 47, y + 5, PAPER);
        icon(g, HEART, x + 47, y + 17);
        bar(g, x + 58, y + 19, 70, d.getHealth() / d.getMaxHealth(), 0xFFC42E2E);
        icon(g, HUNGER, x + 47, y + 27);
        bar(g, x + 58, y + 29, 70, d.getHunger() / (float) DinosaurEntity.MAX_HUNGER, 0xFFE0661C);
        int ix = x + 47;
        if (d.isChested()) {
            icon(g, CARGO, ix, y + 36);
            ix += 10;
        }
        if (d.isSleeping()) {
            icon(g, SLEEP, ix, y + 36);
        }
    }

    private static void packCard(GuiGraphics g, DinosaurEntity d, int x, int y) {
        frame(g, x, y, x + 28, y + 28);
        portrait(g, d, x + 2, y + 2, 24);
        bar(g, x + 2, y + 23, 24, d.getHealth() / d.getMaxHealth(), 0xFFC42E2E);
        int state = d.isSleeping() ? SLEEP : d.isAggressive() ? FIGHT : d.isInSittingPose() ? SIT : FOLLOW;
        icon(g, state, x + 19, y + 1);
    }

    private static void riftAlert(GuiGraphics g, Font font, float intensity, int width) {
        float pulse = 0.55F + 0.45F * Mth.sin(tick * 0.25F);
        g.setColor(1.0F, 1.0F, 1.0F, Mth.clamp(intensity * pulse + 0.2F, 0.0F, 1.0F));
        g.blit(ICONS, width / 2 - 8, 3, 0.0F, 16.0F, 16, 16, 64, 32);
        g.setColor(1.0F, 1.0F, 1.0F, 1.0F);
        g.drawCenteredString(font, Component.translatable("hud.terrassic.rift_storm"), width / 2, 21, 0xFFB63C);
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
        g.enableScissor(x, y, x + size, y + size);
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
            if (--titleDelay == 0 && ClientConfig.flag("hud_era_title") && mc.level.dimension() == Level.OVERWORLD) {
                mc.gui.setTimes(10, 70, 20);
                mc.gui.setSubtitle(Component.translatable("menu.terrassic.subtitle"));
                mc.gui.setTitle(Component.translatable("hud.terrassic.era.late_cretaceous"));
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
            // right after joining only take the baseline: no toasts for what you already knew
            if (--baselineDelay <= 0) {
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
