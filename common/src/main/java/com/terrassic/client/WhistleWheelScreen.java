package com.terrassic.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.entity.Whistle;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import org.lwjgl.glfw.GLFW;

/**
 * The whistle wheel (1.5, docs/ORDENS.md), drawn as in the HUD preview Rodrigo approved on 30/10/2026
 * (hud-estudo/scripts/dirF.py, "wheel"): six basalt slabs round the crosshair, the one pointed at edged in amber with
 * its name in the middle, and under it how many dinos hear the whistle. Hold the whistle key, point with the mouse,
 * let go to give the order (entity/Whistle); a click gives it too, Esc or letting go in the middle gives none.
 * It is a screen so the mouse is free to point; it does not pause the game nor darken the world.
 */
public class WhistleWheelScreen extends Screen {
    /** Inner and outer radius of the ring, in GUI pixels (the preview's). */
    private static final int R1 = 26;
    private static final int R2 = 50;
    /** Closer to the centre than this the mouse points at nothing. */
    private static final int DEAD_ZONE = 10;
    /** The orders' icons, drawn at twice their size (the preview's "ic"), in {@link Whistle#ORDERS} order. */
    private static final String[][] ICONS = {
            {"..+..", "...+.", "+++++", "...+.", "..+.."},   // follow: an arrow
            {"+.+", "+.+", "+.+", "+.+", "+.+"},             // wait here: a pause
            {".+...", "+.+.+", "...+."},                     // wander nearby: a wave
            {"..+.+", ".+.+.", "+.+..", "....."},            // attack my target: claw marks
            {"+...+", ".+.+.", "..+..", ".+.+.", "+...+"},   // gather: all to one point
            {".+++.", "+...+", "+...+", ".+++."}             // passive: an empty ring
    };
    private static final String[][] BIG = new String[ICONS.length][];

    static {
        for (int i = 0; i < ICONS.length; i++) {
            String[] rows = ICONS[i];
            String[] big = new String[rows.length * 2];
            for (int r = 0; r < rows.length; r++) {
                StringBuilder b = new StringBuilder();
                for (char c : rows[r].toCharArray()) {
                    b.append(c).append(c);
                }
                big[r * 2] = b.toString();
                big[r * 2 + 1] = b.toString();
            }
            BIG[i] = big;
        }
    }

    private final InputConstants.Key key;
    private int hovered = -1;
    private int hearing;
    private boolean done;

    public WhistleWheelScreen() {
        super(Component.translatable("gui.terrassic.whistle.title"));
        this.key = InputConstants.getKey(DinoControls.WHISTLE.saveString());
    }

    @Override
    protected void init() {
        this.countHearing();
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void tick() {
        if (!this.done && !this.held()) {
            this.give(this.hovered);
            return;
        }
        if (this.minecraft != null && this.minecraft.player != null && this.minecraft.player.tickCount % 10 == 0) {
            this.countHearing();
        }
    }

    private void countHearing() {
        Minecraft mc = Minecraft.getInstance();
        this.hearing = mc.player == null ? 0 : Whistle.hearing(mc.player).size();
    }

    /** Whether the whistle key is still down (read from the window: key mappings are not updated under a screen). */
    private boolean held() {
        if (this.minecraft == null) {
            return false;
        }
        long window = this.minecraft.getWindow().getWindow();
        if (this.key.getType() == InputConstants.Type.MOUSE) {
            return GLFW.glfwGetMouseButton(window, this.key.getValue()) == GLFW.GLFW_PRESS;
        }
        if (this.key.getType() == InputConstants.Type.KEYSYM && this.key.getValue() != InputConstants.UNKNOWN.getValue()) {
            return InputConstants.isKeyDown(window, this.key.getValue());
        }
        return true;   // a scan code: stay open until a click or Esc
    }

    /** Gives the order (or none for -1) and closes. */
    private void give(int order) {
        if (this.done) {
            return;
        }
        this.done = true;
        if (order >= 0 && order < Whistle.ORDERS.length) {
            DinoControls.whistle(Whistle.ORDERS[order]);
        }
        this.onClose();
    }

    @Override
    public boolean keyReleased(int keyCode, int scanCode, int modifiers) {
        if (DinoControls.WHISTLE.matches(keyCode, scanCode)) {
            this.give(this.hovered);
            return true;
        }
        return super.keyReleased(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button == GLFW.GLFW_MOUSE_BUTTON_LEFT && this.hovered >= 0) {
            this.give(this.hovered);
            return true;
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean mouseReleased(double mouseX, double mouseY, int button) {
        if (DinoControls.WHISTLE.matchesMouse(button)) {
            this.give(this.hovered);
            return true;
        }
        return super.mouseReleased(mouseX, mouseY, button);
    }

    // ------------------------------------------------------------------ drawing

    /** The slice the mouse points at: by direction from the centre, clockwise from the top; -1 in the dead zone. */
    private int sliceAt(double mouseX, double mouseY, int cx, int cy) {
        double dx = mouseX - cx;
        double dy = mouseY - cy;
        if (dx * dx + dy * dy < DEAD_ZONE * DEAD_ZONE) {
            return -1;
        }
        int n = Whistle.ORDERS.length;
        double angle = Math.atan2(dy, dx) + Math.PI / 2.0D;   // 0 at the top, growing clockwise (y points down)
        double step = Math.PI * 2.0D / n;
        int slice = (int) Math.floor((angle + step / 2.0D) / step);
        return Math.floorMod(slice, n);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        // no darkening and no blur: the world stays in sight, as in the preview
        int cx = this.width / 2;
        int cy = this.height / 2;
        int n = Whistle.ORDERS.length;
        this.hovered = this.sliceAt(mouseX, mouseY, cx, cy);
        for (int k = 0; k < n; k++) {
            double a0 = -Math.PI / 2.0D + (k - 0.5D) * 2.0D * Math.PI / n + 0.06D;
            double a1 = -Math.PI / 2.0D + (k + 0.5D) * 2.0D * Math.PI / n - 0.06D;
            AmberHud.slab(g, "whistle_" + k, cx, cy, slice(a0, a1));
            boolean on = k == this.hovered;
            if (on) {
                for (int i = 0; i < 40; i++) {
                    double t = a0 + 0.02D + (a1 - a0 - 0.04D) * i / 39.0D;
                    dot(g, cx + (R2 - 2) * Math.cos(t), cy + (R2 - 2) * Math.sin(t), TerrassicPalette.AMBER_500);
                    dot(g, cx + (R1 + 2) * Math.cos(t), cy + (R1 + 2) * Math.sin(t), TerrassicPalette.AMBER_700);
                }
            }
            double mid = -Math.PI / 2.0D + k * 2.0D * Math.PI / n;
            int ix = (int) Math.round(cx + (R1 + R2) / 2.0D * Math.cos(mid));
            int iy = (int) Math.round(cy + (R1 + R2) / 2.0D * Math.sin(mid));
            String[] icon = BIG[k];
            int w = icon[0].length();
            int h = icon.length;
            AmberHud.icon(g, icon, ix - w / 2 - 1, iy - h / 2 - 1,
                    on ? TerrassicPalette.AMBER_300 : TerrassicPalette.STONE_200,
                    on ? TerrassicPalette.AMBER_600 : TerrassicPalette.STONE_400);
        }
        if (this.hovered >= 0) {
            Component name = Component.translatable("gui.terrassic.whistle." + Whistle.ORDERS[this.hovered]);
            AmberHud.text(g, this.font, name, cx - AmberHud.width(this.font, name) / 2, cy - 4, TerrassicPalette.AMBER_300);
        }
        Component count = this.hearing == 0 ? Component.translatable("gui.terrassic.whistle.hearing.none")
                : this.hearing == 1 ? Component.translatable("gui.terrassic.whistle.hearing.one")
                : Component.translatable("gui.terrassic.whistle.hearing", this.hearing);
        int y = cy + R2 + 6;
        AmberHud.text(g, this.font, count, cx - AmberHud.width(this.font, count) / 2, y,
                this.hearing == 0 ? TerrassicPalette.STONE_300 : TerrassicPalette.AMBER_500);
        if (this.hovered >= 0) {
            Component tip = Component.translatable("gui.terrassic.whistle." + Whistle.ORDERS[this.hovered] + ".tip");
            AmberHud.text(g, this.font, tip, cx - AmberHud.width(this.font, tip) / 2, y + 10, TerrassicPalette.BONE_100);
        }
        Component release = Component.translatable("gui.terrassic.whistle.release", DinoControls.WHISTLE.getTranslatedKeyMessage());
        AmberHud.text(g, this.font, release, cx - AmberHud.width(this.font, release) / 2, y + (this.hovered >= 0 ? 20 : 10),
                TerrassicPalette.STONE_200);
        super.render(g, mouseX, mouseY, partialTick);
    }

    /** One slice of the ring: the outer arc then the inner arc back, eight points each (the preview's polygon). */
    private static int[] slice(double a0, double a1) {
        int[] poly = new int[32];
        for (int i = 0; i < 8; i++) {
            double t = a0 + (a1 - a0) * i / 7.0D;
            poly[i * 2] = (int) Math.round(R2 * Math.cos(t));
            poly[i * 2 + 1] = (int) Math.round(R2 * Math.sin(t));
        }
        for (int i = 0; i < 8; i++) {
            double t = a1 + (a0 - a1) * i / 7.0D;
            poly[16 + i * 2] = (int) Math.round(R1 * Math.cos(t));
            poly[16 + i * 2 + 1] = (int) Math.round(R1 * Math.sin(t));
        }
        return poly;
    }

    private static void dot(GuiGraphics g, double x, double y, int colour) {
        int px = Mth.floor(x + 0.5D);
        int py = Mth.floor(y + 0.5D);
        g.fill(px, py, px + 1, py + 1, colour);
    }
}
