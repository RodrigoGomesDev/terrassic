package com.terrassic.client;

import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.PredatorDinosaur;
import com.terrassic.item.FieldLensItem;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.joml.Vector4f;

/**
 * The nameplate over the animal you look at (v0.14.1, docs/HUD.md; study: dirF.py nameplate() and taming()), drawn on
 * the HUD at the point over its head, the same size at any distance:
 * <ul>
 *   <li>a small slab with a drop in the colour of its temper (green: tame; red: a wild predator; amber: any other wild
 *       animal), "Tiranossauro · Nv 23" and its health cut into the stone;</li>
 *   <li>on a knocked-out animal, the taming bars beside it: "Desmaiado" with the time until it wakes, torpor and
 *       taming (the numbers come from the server, like the Field Lens card).</li>
 * </ul>
 * Not while holding the Field Lens (its card says all of it), nor on the animal you ride. "hud_nameplate" and
 * "hud_taming" in config/terrassic-client.json turn them off. The camera of the frame comes from
 * mixin/client/LevelRendererMixin; without it there are no nameplates.
 */
public final class DinoNameplate {
    /** How far the nameplate reaches (blocks). */
    private static final double RANGE = 24.0D;
    private static final int TAMING_W = 104;
    private static Matrix4f projection;
    private static Matrix4f view;
    private static Vec3 camera;
    private static int target = -1;
    private static int linger;
    private static int tick;

    private DinoNameplate() {
    }

    public static void init() {
        ClientTickEvent.CLIENT_POST.register(DinoNameplate::tick);
        ClientGuiEvent.RENDER_HUD.register(DinoNameplate::render);
    }

    /** The frame's projection and camera, kept for drawing the plate over the animal (LevelRendererMixin). */
    public static void capture(Matrix4f projectionMatrix, Matrix4f viewMatrix, Vec3 cameraPos) {
        projection = new Matrix4f(projectionMatrix);
        view = new Matrix4f(viewMatrix);
        camera = cameraPos;
    }

    private static void tick(Minecraft mc) {
        LocalPlayer player = mc.player;
        if (player == null || mc.level == null || FieldLensItem.holding(player)) {
            target = -1;
            return;
        }
        tick++;
        DinosaurEntity seen = LensOverlay.look(player, RANGE);
        if (seen != null && seen != player.getVehicle()) {
            target = seen.getId();
            linger = 10;
            if (seen.isKnockedOut() && tick % 5 == 0 && ClientConfig.flag("hud_taming")) {
                LensOverlay.ask(target);
            }
        } else if (--linger <= 0) {
            target = -1;
        }
    }

    private static void render(GuiGraphics g, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.options.hideGui || mc.level == null || target < 0 || projection == null || !ClientConfig.flag("hud_nameplate")) {
            return;
        }
        Entity e = mc.level.getEntity(target);
        if (!(e instanceof DinosaurEntity d) || !d.isAlive()) {
            return;
        }
        Vec3 at = d.getPosition(partialTick).add(0.0D, d.getBbHeight() + 0.35D, 0.0D);
        float[] screen = project(at, g.guiWidth(), g.guiHeight());
        if (screen == null) {
            return;
        }
        Font font = mc.font;
        Component name = d.hasCustomName() ? d.getCustomName() : d.getType().getDescription();
        Component dot = Component.literal(name.getString() + " · ");
        Component level = Component.translatable("hud.terrassic.level", Math.max(1, d.getLevel()));
        int w = AmberHud.width(font, dot) + AmberHud.width(font, level) + 22;
        int x = Math.round(screen[0]) - w / 2;
        int y = Math.round(screen[1]) - 19;
        boolean compact = ClientConfig.compactHud();
        if (!compact) {
            AmberHud.slab(g, "nameplate_" + w, x, y, 3, 0, w, 0, w, 16, w - 3, 19, 0, 19, 0, 3);
        }
        temper(g, x + 5, y + 5, d);
        int nx = AmberHud.text(g, font, dot, x + 13, y + 3, TerrassicPalette.BONE_100);
        AmberHud.text(g, font, level, nx, y + 3, TerrassicPalette.AMBER_500);
        AmberHud.groove(g, x + 4, y + 12, w - 8, d.getHealth() / d.getMaxHealth(), AmberHud.RED);
        CompoundTag info = d.isKnockedOut() && ClientConfig.flag("hud_taming") ? LensOverlay.infoFor(target) : null;
        if (info != null && info.getBoolean("KnockedOut")) {
            taming(g, font, x - TAMING_W + 11, y + 16, info, compact);
        }
    }

    /** The temper: a small drop in its colour, with a white glint. */
    private static void temper(GuiGraphics g, int x, int y, DinosaurEntity d) {
        int c = d.isTame() ? TerrassicPalette.FERN_400
                : d instanceof PredatorDinosaur ? TerrassicPalette.BLOOD_500 : TerrassicPalette.AMBER_500;
        for (int yy = 0; yy < 4; yy++) {
            for (int xx = 0; xx < 5; xx++) {
                if ((xx - 2) * (xx - 2) / 6.0F + (yy - 2) * (yy - 2) / 3.2F <= 1.0F) {
                    g.fill(x + xx, y + yy, x + xx + 1, y + yy + 1, c);
                }
            }
        }
        g.fill(x + 1, y, x + 2, y + 1, 0xFFFFFFFF);
    }

    /** "Desmaiado" and the time until it wakes, the torpor (lilac) and the taming (green). */
    private static void taming(GuiGraphics g, Font font, int x, int y, CompoundTag t, boolean compact) {
        int w = TAMING_W;
        if (!compact) {
            AmberHud.slab(g, "taming", x, y, 4, 0, w, 0, w, 27, w - 4, 30, 0, 30, 0, 4);
        }
        int secs = t.getInt("WakeSeconds");
        Component timer = Component.literal(secs / 60 + ":" + String.format("%02d", secs % 60));
        AmberHud.text(g, font, Component.translatable("hud.terrassic.knocked_out"), x + 5, y + 3, 0xFFC2B0EE);
        AmberHud.text(g, font, timer, x + w - 5 - AmberHud.width(font, timer), y + 3, TerrassicPalette.STONE_200);
        AmberHud.groove(g, x + 5, y + 13, w - 10, t.getFloat("Torpor") / Math.max(1.0F, t.getFloat("MaxTorpor")), AmberHud.TORPOR);
        AmberHud.groove(g, x + 5, y + 21, w - 10, Math.min(1.0F, t.getFloat("Progress") / Math.max(1.0E-3F, t.getFloat("Goal"))),
                AmberHud.FERN);
    }

    /** The GUI point of a world position in the last frame, or null behind the camera. */
    private static float[] project(Vec3 pos, int guiWidth, int guiHeight) {
        Vector4f v = new Vector4f((float) (pos.x - camera.x), (float) (pos.y - camera.y), (float) (pos.z - camera.z), 1.0F);
        view.transform(v);
        projection.transform(v);
        if (v.w() <= 0.05F) {
            return null;
        }
        float nx = v.x() / v.w();
        float ny = v.y() / v.w();
        if (Math.abs(nx) > 1.2F || Math.abs(ny) > 1.2F) {
            return null;
        }
        return new float[]{(nx * 0.5F + 0.5F) * guiWidth, (0.5F - ny * 0.5F) * guiHeight};
    }
}
