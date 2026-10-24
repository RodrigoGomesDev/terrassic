package com.terrassic.client.ui;

import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;

import static com.terrassic.client.ui.TerrassicPalette.*;

/**
 * The Terrassic look drawn by code (docs/IDENTIDADE.md §3): every screen of the mod uses these pieces so the mod
 * reads as one thing, and none of them needs a texture.
 * <ul>
 *   <li>{@link #slab}: a basalt slab with a carved bevel (lit edge top and left, shadow bottom and right, like the
 *       vanilla blocks) and an amber inlay along the top, with an amber stud in each corner.</li>
 *   <li>{@link #well}: a recessed field (number boxes, slider grooves, lists).</li>
 *   <li>{@link #button} / {@link #tab}: carved stone buttons; amber means "this acts".</li>
 *   <li>{@link #slider}: a groove filled with amber up to an amber shard.</li>
 *   <li>{@link #paper}: a notebook page, for text read like a book.</li>
 * </ul>
 */
public final class TerrassicUi {
    private TerrassicUi() {
    }

    /** A basalt slab (a panel or window). */
    public static void slab(GuiGraphics g, int x0, int y0, int x1, int y1) {
        slab(g, x0, y0, x1, y1, BASALT_800);
    }

    public static void slab(GuiGraphics g, int x0, int y0, int x1, int y1, int fill) {
        g.fill(x0, y0, x1, y1, BASALT_950);                       // outline
        g.fill(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill);
        g.fill(x0 + 1, y0 + 1, x1 - 1, y0 + 2, BASALT_500);      // lit top edge
        g.fill(x0 + 1, y0 + 1, x0 + 2, y1 - 1, BASALT_600);      // lit left edge
        g.fill(x0 + 1, y1 - 2, x1 - 1, y1 - 1, BASALT_900);      // shadow bottom
        g.fill(x1 - 2, y0 + 1, x1 - 1, y1 - 1, BASALT_900);      // shadow right
        // amber inlay along the top, broken in the middle like a seam in the rock
        int mid = (x0 + x1) / 2;
        g.fill(x0 + 8, y0 + 4, mid - 6, y0 + 5, AMBER_700);
        g.fill(mid + 6, y0 + 4, x1 - 8, y0 + 5, AMBER_700);
        g.fill(mid - 2, y0 + 3, mid + 2, y0 + 6, AMBER_500);
        stud(g, x0 + 3, y0 + 3);
        stud(g, x1 - 6, y0 + 3);
        stud(g, x0 + 3, y1 - 6);
        stud(g, x1 - 6, y1 - 6);
    }

    /** A 3x3 amber stud with a lit pixel. */
    public static void stud(GuiGraphics g, int x, int y) {
        g.fill(x, y, x + 3, y + 3, AMBER_700);
        g.fill(x, y, x + 2, y + 2, AMBER_500);
        g.fill(x, y, x + 1, y + 1, AMBER_300);
    }

    /** A recessed field: shadow on top and left, light on bottom and right (the inverse of a slab). */
    public static void well(GuiGraphics g, int x0, int y0, int x1, int y1, boolean focused) {
        g.fill(x0, y0, x1, y1, focused ? AMBER_600 : BASALT_600);
        g.fill(x0 + 1, y0 + 1, x1 - 1, y1 - 1, BASALT_900);
        g.fill(x0 + 1, y0 + 1, x1 - 1, y0 + 2, BASALT_950);
        g.fill(x0 + 1, y0 + 1, x0 + 2, y1 - 1, BASALT_950);
    }

    /** A thin carved line with an amber dot in the middle. */
    public static void divider(GuiGraphics g, int x0, int x1, int y) {
        g.fill(x0, y, x1, y + 1, BASALT_950);
        g.fill(x0, y + 1, x1, y + 2, BASALT_600);
        int mid = (x0 + x1) / 2;
        g.fill(mid - 1, y, mid + 2, y + 2, AMBER_600);
    }

    /** A carved stone button. {@code primary} = the main action (save, confirm): amber face. */
    public static void button(GuiGraphics g, Font font, int x, int y, int w, int h, Component label,
                              boolean active, boolean hot, boolean primary) {
        int face;
        int text;
        if (!active) {
            face = BASALT_700;
            text = STONE_400;
        } else if (primary) {
            face = hot ? AMBER_500 : AMBER_600;
            text = BASALT_900;
        } else {
            face = hot ? BASALT_600 : BASALT_700;
            text = hot ? AMBER_300 : STONE_200;
        }
        g.fill(x, y, x + w, y + h, BASALT_950);
        g.fill(x + 1, y + 1, x + w - 1, y + h - 1, face);
        int light = primary && active ? AMBER_300 : BASALT_500;
        int dark = primary && active ? AMBER_700 : BASALT_900;
        g.fill(x + 1, y + 1, x + w - 1, y + 2, light);
        g.fill(x + 1, y + h - 2, x + w - 1, y + h - 1, dark);
        if (hot && active && !primary) {
            g.fill(x + 1, y + h - 2, x + w - 1, y + h - 1, AMBER_600);
        }
        g.drawCenteredString(font, label, x + w / 2, y + (h - 8) / 2 + 1, rgb(text));
    }

    /** A tab: stone label; the selected one sits raised with an amber underline. */
    public static void tab(GuiGraphics g, Font font, int x, int y, int w, int h, Component label, boolean selected, boolean hot) {
        if (selected) {
            g.fill(x, y, x + w, y + h, BASALT_700);
            g.fill(x, y, x + w, y + 1, BASALT_500);
            g.fill(x + 2, y + h - 2, x + w - 2, y + h, AMBER_500);
        } else if (hot) {
            g.fill(x, y, x + w, y + h, BASALT_700);
        }
        int color = selected ? AMBER_500 : hot ? STONE_200 : STONE_400;
        g.drawCenteredString(font, label, x + w / 2, y + (h - 8) / 2, rgb(color));
    }

    /**
     * A slider: a groove filled with amber up to the knob, an amber shard as the knob and a small tick under the
     * groove at {@code defaultFraction}.
     */
    public static void slider(GuiGraphics g, int x, int y, int w, int h, double fraction, double defaultFraction,
                              boolean active, boolean hot) {
        int mid = y + h / 2;
        int x0 = x + 4;
        int x1 = x + w - 4;
        well(g, x0 - 1, mid - 2, x1 + 1, mid + 3, false);
        int kx = x0 + (int) Math.round(Math.max(0.0D, Math.min(1.0D, fraction)) * (x1 - x0));
        if (active && kx > x0) {
            g.fill(x0, mid - 1, kx, mid + 2, AMBER_700);
            g.fill(x0, mid - 1, kx, mid, AMBER_600);
        }
        int dx = x0 + (int) Math.round(Math.max(0.0D, Math.min(1.0D, defaultFraction)) * (x1 - x0));
        g.fill(dx, mid + 4, dx + 1, mid + 7, STONE_400);
        // the shard: a small diamond
        int c = !active ? STONE_400 : hot ? AMBER_300 : AMBER_500;
        g.fill(kx - 1, mid - 5, kx + 2, mid + 6, BASALT_950);
        g.fill(kx - 3, mid - 3, kx + 4, mid + 4, BASALT_950);
        g.fill(kx - 2, mid - 3, kx + 3, mid + 4, c);
        g.fill(kx - 1, mid - 4, kx + 2, mid + 5, c);
        g.fill(kx - 1, mid - 3, kx, mid, active ? 0xFFFFF1C8 : STONE_300);
    }

    /** A scroll bar: a groove and an amber thumb. */
    public static void scrollbar(GuiGraphics g, int x, int y0, int y1, int thumbY, int thumbH) {
        g.fill(x, y0, x + 3, y1, BASALT_900);
        g.fill(x, thumbY, x + 3, thumbY + thumbH, AMBER_700);
        g.fill(x, thumbY, x + 1, thumbY + thumbH, AMBER_500);
    }

    /** A notebook page: paper with a darker margin. */
    public static void paper(GuiGraphics g, int x0, int y0, int x1, int y1) {
        g.fill(x0, y0, x1, y1, PAPER_DARK);
        g.fill(x0 + 1, y0 + 1, x1 - 1, y1 - 1, PAPER);
    }

    /** A small amber mark (a changed value, a new entry). */
    public static void mark(GuiGraphics g, int x, int y) {
        g.fill(x, y, x + 3, y + 3, AMBER_500);
        g.fill(x, y, x + 1, y + 1, AMBER_300);
    }
}
