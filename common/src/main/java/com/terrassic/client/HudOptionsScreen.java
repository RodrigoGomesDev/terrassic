package com.terrassic.client;

import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicButton;
import com.terrassic.client.ui.TerrassicFonts;
import com.terrassic.client.ui.TerrassicPalette;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;

/**
 * The HUD options (v0.14.2, docs/HUD.md; study: dirF.py scene_opcoes()), from the "HUD" button beside "Terrassic
 * Rules" on the pause menu: the style (Âmbar or compact) and one switch per piece. Every change
 * is written at once to config/terrassic-client.json.
 */
public class HudOptionsScreen extends Screen {
    private static final int W = 300;
    private static final int ROW = 17;
    /** The switches, in order; each label is gui.terrassic.hud.&lt;option&gt;. */
    private static final String[] OPTIONS = {"hud_mount", "hud_nameplate", "hud_taming", "hud_notices", "hud_new_species",
            "hud_era_title", "hud_numbers_always"};
    private final Screen parent;
    private int left;
    private int top;
    private int h;

    public HudOptionsScreen(Screen parent) {
        super(Component.translatable("gui.terrassic.hud.title"));
        this.parent = parent;
    }

    @Override
    protected void init() {
        this.h = 48 + OPTIONS.length * ROW + 28;
        this.left = (this.width - W) / 2;
        this.top = Math.max(2, (this.height - this.h) / 2);
        boolean compact = ClientConfig.compactHud();
        this.addRenderableWidget(new TerrassicButton(this.left + 120, this.top + 24, 80, 16, Component.translatable("gui.terrassic.hud.amber"),
                b -> this.style(false), compact ? TerrassicButton.Kind.STONE : TerrassicButton.Kind.PRIMARY, !compact));
        this.addRenderableWidget(new TerrassicButton(this.left + 204, this.top + 24, 84, 16, Component.translatable("gui.terrassic.hud.compact"),
                b -> this.style(true), compact ? TerrassicButton.Kind.PRIMARY : TerrassicButton.Kind.STONE, compact));
        this.addRenderableWidget(new TerrassicButton(this.left + W - 84, this.top + this.h - 22, 72, 16, CommonComponents.GUI_DONE,
                b -> this.onClose(), TerrassicButton.Kind.PRIMARY, false));
    }

    private void style(boolean compact) {
        ClientConfig.setHudStyle(compact);
        this.rebuildWidgets();
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(g);
        int x = this.left;
        int y = this.top;
        AmberHud.slab(g, "hud_options_" + this.h, x, y, 6, 0, W, 0, W, this.h - 5, W - 5, this.h, 0, this.h, 0, 6);
        Component title = TerrassicFonts.title(this.title.copy());
        g.drawString(this.font, title, x + (W - this.font.width(title)) / 2, y + 8, TerrassicPalette.rgb(TerrassicPalette.AMBER_500), false);
        AmberHud.text(g, this.font, Component.translatable("gui.terrassic.hud.style"), x + 12, y + 28, TerrassicPalette.STONE_200);
        for (int i = 0; i < OPTIONS.length; i++) {
            int yy = y + 48 + i * ROW;
            if (i > 0) {
                for (int xx = x + 12; xx < x + W - 12; xx += 2) {
                    g.fill(xx, yy - 4, xx + 1, yy - 3, TerrassicPalette.BASALT_700);
                }
            }
            boolean on = ClientConfig.flag(OPTIONS[i]);
            AmberHud.text(g, this.font, Component.translatable("gui.terrassic.hud." + OPTIONS[i]), x + 12, yy,
                    on ? TerrassicPalette.BONE_100 : TerrassicPalette.STONE_300);
            toggle(g, x + W - 34, yy - 1, on);
        }
        AmberHud.text(g, this.font, Component.literal("config/terrassic-client.json"), x + 12, y + this.h - 18, TerrassicPalette.STONE_400);
        super.render(g, mouseX, mouseY, partialTick);
    }

    /** A switch carved in the stone: amber with the knob on the right when on, dark with the knob on the left off. */
    private static void toggle(GuiGraphics g, int x, int y, boolean on) {
        g.fill(x, y, x + 22, y + 10, AmberHud.OUTLINE);
        g.fill(x + 1, y + 1, x + 21, y + 9, TerrassicPalette.BASALT_900);
        g.fill(x + 1, y + 8, x + 21, y + 9, TerrassicPalette.BASALT_600);
        if (on) {
            g.fill(x + 1, y + 1, x + 21, y + 8, TerrassicPalette.AMBER_700);
        }
        int gx = on ? x + 12 : x + 2;
        for (int yy = 0; yy < 8; yy++) {
            for (int xx = 0; xx < 8; xx++) {
                if (Math.abs(xx - 3.5F) + Math.abs(yy - 3.5F) <= 4.2F) {
                    boolean lit = xx + yy < 6;
                    int c = on ? (lit ? TerrassicPalette.AMBER_300 : TerrassicPalette.AMBER_500)
                            : (lit ? TerrassicPalette.STONE_300 : TerrassicPalette.STONE_400);
                    g.fill(gx + xx, y + 1 + yy, gx + xx + 1, y + 2 + yy, c);
                }
            }
        }
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button == 0 && mouseX >= this.left + 8 && mouseX < this.left + W - 8) {
            for (int i = 0; i < OPTIONS.length; i++) {
                int yy = this.top + 48 + i * ROW;
                if (mouseY >= yy - 3 && mouseY < yy + ROW - 3) {
                    ClientConfig.set(OPTIONS[i], !ClientConfig.flag(OPTIONS[i]));
                    this.minecraft.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(
                            net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK, 1.0F));
                    return true;
                }
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public void onClose() {
        this.minecraft.setScreen(this.parent);
    }
}
