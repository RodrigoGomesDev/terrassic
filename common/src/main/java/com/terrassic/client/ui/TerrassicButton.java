package com.terrassic.client.ui;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;

/**
 * A button in the Terrassic look (docs/IDENTIDADE.md §3), in place of the grey vanilla button on the mod's screens.
 * <ul>
 *   <li>{@link Kind#STONE}: carved basalt (windows such as the Rules); {@link Kind#PRIMARY}: the main action, amber face.</li>
 *   <li>{@link Kind#NOTEBOOK}: leather, for the Field Notebook (its tabs show the page colour when selected).</li>
 * </ul>
 */
public class TerrassicButton extends Button {
    public enum Kind { STONE, PRIMARY, NOTEBOOK }

    private final Kind kind;
    private final boolean selected;

    public TerrassicButton(int x, int y, int w, int h, Component label, OnPress onPress, Kind kind, boolean selected) {
        super(x, y, w, h, label, onPress, DEFAULT_NARRATION);
        this.kind = kind;
        this.selected = selected;
    }

    public static TerrassicButton stone(int x, int y, int w, int h, Component label, OnPress onPress) {
        return new TerrassicButton(x, y, w, h, label, onPress, Kind.STONE, false);
    }

    public static TerrassicButton notebook(int x, int y, int w, int h, Component label, OnPress onPress, boolean selected) {
        return new TerrassicButton(x, y, w, h, label, onPress, Kind.NOTEBOOK, selected);
    }

    @Override
    public void onPress() {
        if (!this.selected) {
            super.onPress();
        }
    }

    @Override
    protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        Font font = Minecraft.getInstance().font;
        boolean hot = this.active && this.isHoveredOrFocused();
        if (this.kind == Kind.NOTEBOOK) {
            TerrassicUi.leather(g, font, this.getX(), this.getY(), this.width, this.height, this.getMessage(), this.active, hot, this.selected);
        } else {
            TerrassicUi.button(g, font, this.getX(), this.getY(), this.width, this.height, this.getMessage(), this.active, hot,
                    this.kind == Kind.PRIMARY);
        }
    }
}
