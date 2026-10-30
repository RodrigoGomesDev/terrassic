package com.terrassic.client.ui;

import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import com.terrassic.Terrassic;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * The pieces of the "Âmbar" HUD (v0.14, docs/HUD.md), approved by Rodrigo on 30/10/2026 from the study in
 * /mnt/project-files/hud-estudo (generator scripts/dirF.py, whose shapes and colours this follows pixel for pixel):
 * <ul>
 *   <li>{@link #slab}: a chipped basalt slab, flat dark inside, lit on the top and left, dark on the bottom and right,
 *       with a one-pixel outline. The shape is a polygon, so every piece has its own broken edge.</li>
 *   <li>{@link #groove}: a bar cut into the stone, its fill in three tones with a bright meniscus.</li>
 *   <li>{@link #amberDrop}: a drop of amber with the animal's live model trapped inside, tinted like resin.</li>
 *   <li>{@link #icon}, {@link #chip} and {@link #text}: the small heart, meat and wind icons, the recharging key socket
 *       and the outlined Sedimento text.</li>
 * </ul>
 * Shapes are rasterised once into a texture (1 texel = 1 GUI pixel) and kept while their size does not change.
 */
public final class AmberHud {
    public static final int OUTLINE = TerrassicPalette.BASALT_950;
    public static final int[] RED = {0xFFF08A70, TerrassicPalette.BLOOD_500, 0xFF7E2620};
    public static final int[] AMBER = {TerrassicPalette.AMBER_300, TerrassicPalette.AMBER_600, TerrassicPalette.AMBER_700};
    public static final int[] FERN = {0xFFB8D890, TerrassicPalette.FERN_400, 0xFF4E7A30};
    public static final int[] SKY = {0xFFC4DCE8, TerrassicPalette.SKY_400, 0xFF5A8098};
    public static final int[] TORPOR = {0xFFC2B0EE, 0xFF8A6FC8, 0xFF5A4590};

    public static final String[] HEART = {"++.++", "+s+ss", "sssss", ".sss.", "..s.."};
    public static final String[] MEAT = {"...++", "..+s.", ".ss..", "sss..", ".s..."};
    public static final String[] WIND = {"++++.", "...s.", "sss..", "....s", "sss.."};
    /** A mouse with its right button lit: the key chip of a special on the use key (right click). */
    private static final String[] MOUSE = {".+s.", "++ss", "++++", "++++", ".++."};

    /** The amber ramp of the drop, from the dark rim to the light that bounces inside. */
    private static final int[] RAMP = {0xFF5A2E08, 0xFF7A420E, 0xFF9A5A12, TerrassicPalette.AMBER_700,
            TerrassicPalette.AMBER_600, TerrassicPalette.AMBER_500, TerrassicPalette.AMBER_300};

    private static final Map<String, Baked> BAKED = new HashMap<>();
    private static int bakedCount;

    private AmberHud() {
    }

    private record Baked(ResourceLocation id, DynamicTexture texture, int x0, int y0, int w, int h) {
    }

    // ------------------------------------------------------------------ slab

    /**
     * A basalt slab with the outline {@code poly} (x, y pairs, relative to x, y; vertices on whole pixels, the edge
     * pixels included like the study's polygons). {@code key} names the shape so its texture is kept between frames.
     */
    public static void slab(GuiGraphics g, String key, int x, int y, int... poly) {
        Baked b = BAKED.get(key);
        if (b == null || !b.id().getPath().endsWith(Integer.toHexString(Arrays.hashCode(poly)))) {
            if (b != null) {
                release(b);
            }
            b = bake(key, Integer.toHexString(Arrays.hashCode(poly)), slabImage(poly));
            BAKED.put(key, b);
        }
        draw(g, b, x, y);
    }

    private static Image slabImage(int[] poly) {
        int minX = Integer.MAX_VALUE;
        int minY = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE;
        int maxY = Integer.MIN_VALUE;
        for (int i = 0; i < poly.length; i += 2) {
            minX = Math.min(minX, poly[i]);
            maxX = Math.max(maxX, poly[i]);
            minY = Math.min(minY, poly[i + 1]);
            maxY = Math.max(maxY, poly[i + 1]);
        }
        int w = maxX - minX + 1;
        int h = maxY - minY + 1;
        boolean[][] in = new boolean[h + 4][w + 4];
        for (int py = 0; py < h; py++) {
            for (int px = 0; px < w; px++) {
                in[py + 2][px + 2] = inside(poly, px + minX, py + minY);
            }
        }
        int[] pixels = new int[w * h];
        for (int py = 0; py < h; py++) {
            for (int px = 0; px < w; px++) {
                int ix = px + 2;
                int iy = py + 2;
                if (!in[iy][ix]) {
                    continue;
                }
                int c;
                if (!(in[iy - 1][ix] && in[iy][ix - 1] && in[iy + 1][ix] && in[iy][ix + 1])) {
                    c = OUTLINE;
                } else if (!(in[iy - 2][ix] && in[iy][ix - 2])) {
                    c = !in[iy - 2][ix] ? TerrassicPalette.BASALT_500 : TerrassicPalette.BASALT_600;
                } else if (!(in[iy + 2][ix] && in[iy][ix + 2])) {
                    c = TerrassicPalette.BASALT_900;
                } else {
                    // flat dark inside (Rodrigo 30/10 18:06Z: "fundo escuro chapado", no random pixels)
                    c = TerrassicPalette.BASALT_800;
                }
                pixels[py * w + px] = c;
            }
        }
        return new Image(minX, minY, w, h, pixels);
    }

    /** Inside the polygon or within half a pixel of its edge (the edge pixels belong to the shape). */
    private static boolean inside(int[] poly, double x, double y) {
        boolean in = false;
        int n = poly.length / 2;
        for (int i = 0, j = n - 1; i < n; j = i++) {
            double xi = poly[i * 2];
            double yi = poly[i * 2 + 1];
            double xj = poly[j * 2];
            double yj = poly[j * 2 + 1];
            if (segmentDistance(x, y, xi, yi, xj, yj) <= 0.5D) {
                return true;
            }
            if ((yi > y) != (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) {
                in = !in;
            }
        }
        return in;
    }

    private static double segmentDistance(double px, double py, double ax, double ay, double bx, double by) {
        double dx = bx - ax;
        double dy = by - ay;
        double len = dx * dx + dy * dy;
        double t = len == 0.0D ? 0.0D : Mth.clamp(((px - ax) * dx + (py - ay) * dy) / len, 0.0D, 1.0D);
        double ex = ax + t * dx - px;
        double ey = ay + t * dy - py;
        return Math.sqrt(ex * ex + ey * ey);
    }

    /** A picture made by code once ({@code pixels}: w x h ARGB, row by row) and kept under {@code key}. */
    public static void picture(GuiGraphics g, String key, int x, int y, int w, int h, java.util.function.Supplier<int[]> pixels) {
        Baked b = BAKED.get(key);
        if (b == null) {
            b = bake(key, "0", new Image(0, 0, w, h, pixels.get()));
            BAKED.put(key, b);
        }
        draw(g, b, x, y);
    }

    // ------------------------------------------------------------------ amber drop

    /**
     * A drop of amber centred on cx, cy with radii rx, ry; the animal is drawn inside by {@code inside} (between the
     * resin and its glint), tinted dark amber like an insect in resin. {@code seed} gives each drop its own wobble.
     */
    public static void amberDrop(GuiGraphics g, int cx, int cy, int rx, int ry, int seed, Runnable inside) {
        String key = "drop_" + rx + "_" + ry + "_" + seed;
        Baked b = BAKED.get(key);
        if (b == null) {
            b = bake(key, "0", dropImage(rx, ry, seed));
            BAKED.put(key, b);
        }
        draw(g, b, cx, cy);
        if (inside != null) {
            g.setColor(0.62F, 0.33F, 0.09F, 1.0F);
            try {
                inside.run();
            } finally {
                g.setColor(1.0F, 1.0F, 1.0F, 1.0F);
            }
        }
        // bubbles and the glint on top of the animal
        int x0 = cx - rx;
        int y0 = cy - ry;
        int bubble = 0xC8FFECBE;
        g.fill(x0 + Math.round(0.72F * rx * 2), y0 + Math.round(0.26F * ry * 2), x0 + Math.round(0.72F * rx * 2) + 1, y0 + Math.round(0.26F * ry * 2) + 1, bubble);
        g.fill(x0 + Math.round(0.78F * rx * 2), y0 + Math.round(0.36F * ry * 2), x0 + Math.round(0.78F * rx * 2) + 1, y0 + Math.round(0.36F * ry * 2) + 1, bubble);
        g.fill(x0 + Math.round(0.22F * rx * 2), y0 + Math.round(0.70F * ry * 2), x0 + Math.round(0.22F * rx * 2) + 1, y0 + Math.round(0.70F * ry * 2) + 1, bubble);
        int gx = x0 + (int) (rx * 0.45F);
        int gy = y0 + (int) (ry * 0.32F);
        int glint = 0xEBFFFAE4;
        if (rx > 12) {
            g.fill(gx, gy + 1, gx + 1, gy + 3, glint);
            g.fill(gx + 1, gy, gx + 3, gy + 1, glint);
        } else {
            g.fill(gx, gy + 1, gx + 1, gy + 2, glint);
            g.fill(gx + 1, gy, gx + 2, gy + 1, glint);
        }
    }

    private static Image dropImage(int rx, int ry, int seed) {
        double ph = new java.util.Random(seed).nextDouble() * 6.0D;
        int x0 = -rx - 3;
        int y0 = -ry - 3;
        int w = rx * 2 + 6;
        int h = ry * 2 + 6;
        int[] pixels = new int[w * h];
        double rim = 1.0D + 1.4D / Math.min(rx, ry);
        for (int py = 0; py < h; py++) {
            for (int px = 0; px < w; px++) {
                double dx = (px + x0) / (double) rx;
                double dy = (py + y0) / (double) ry;
                double th = Math.atan2(dy, dx);
                double r = 1.0D + 0.06D * Math.sin(3 * th + ph) + 0.04D * Math.sin(5 * th + 2 * ph);
                double d = Math.hypot(dx, dy) / r;
                if (d <= 1.0D) {
                    double lit = -(dx * 0.55D + dy * 0.83D);
                    double v = 3.2D + lit * 2.2D - d * d * 1.2D;
                    if (d > 0.82D && dx + dy > 0.35D) {
                        v = 5.2D;
                    }
                    if (d > 0.86D && dx + dy < -0.2D) {
                        v = 2.0D;
                    }
                    pixels[py * w + px] = RAMP[Mth.clamp((int) Math.round(v), 0, 6)];
                } else if (d <= rim) {
                    pixels[py * w + px] = OUTLINE;
                }
            }
        }
        return new Image(x0, y0, w, h, pixels);
    }

    // ------------------------------------------------------------------ bars, icons, chips, text

    /** A bar cut into the stone, w x 5, filled to {@code fraction} with three tones (light, mid, dark). */
    public static void groove(GuiGraphics g, int x, int y, int w, float fraction, int[] tones) {
        g.fill(x, y, x + w, y + 5, OUTLINE);
        g.fill(x + 1, y + 4, x + w - 1, y + 5, TerrassicPalette.BASALT_600);  // lit lower lip: the groove is cut in
        int f = Math.round((w - 2) * Mth.clamp(fraction, 0.0F, 1.0F));
        if (f > 0) {
            g.fill(x + 1, y + 1, x + 1 + f, y + 4, tones[1]);
            g.fill(x + 1, y + 1, x + 1 + f, y + 2, tones[0]);
            g.fill(x + 1, y + 3, x + 1 + f, y + 4, tones[2]);
            g.fill(x + f, y + 1, x + f + 1, y + 4, tones[0]);  // meniscus
        }
    }

    /** A small pixel icon: '+' is the fill, 's' the shade; the outline grows around it. */
    public static void icon(GuiGraphics g, String[] rows, int x, int y, int fill, int shade) {
        icon(g, rows, x, y, fill, shade, OUTLINE);
    }

    /** The same with its own outline colour. */
    public static void icon(GuiGraphics g, String[] rows, int x, int y, int fill, int shade, int outline) {
        int h = rows.length;
        int w = 0;
        for (String r : rows) {
            w = Math.max(w, r.length());
        }
        for (int ry = -1; ry <= h; ry++) {
            for (int rx = -1; rx <= w; rx++) {
                char c = at(rows, rx, ry);
                if (c == '+' || c == 's') {
                    g.fill(x + 1 + rx, y + 1 + ry, x + 2 + rx, y + 2 + ry, c == 's' ? shade : fill);
                } else if (on(rows, rx - 1, ry) || on(rows, rx + 1, ry) || on(rows, rx, ry - 1) || on(rows, rx, ry + 1)) {
                    g.fill(x + 1 + rx, y + 1 + ry, x + 2 + rx, y + 2 + ry, outline);
                }
            }
        }
    }

    private static char at(String[] rows, int x, int y) {
        return y < 0 || y >= rows.length || x < 0 || x >= rows[y].length() ? '.' : rows[y].charAt(x);
    }

    private static boolean on(String[] rows, int x, int y) {
        char c = at(rows, x, y);
        return c == '+' || c == 's';
    }

    /**
     * A carved key socket (12 x 12): amber fills it from the bottom while the special recharges and lights up when it
     * is ready. {@code key} is the key's letter, or null for the right mouse button (a small mouse).
     */
    public static void chip(GuiGraphics g, Font font, int x, int y, String key, float fraction) {
        boolean ready = fraction >= 1.0F;
        g.fill(x, y, x + 12, y + 12, OUTLINE);
        g.fill(x + 1, y + 1, x + 11, y + 11, TerrassicPalette.BASALT_900);
        g.fill(x + 1, y + 10, x + 11, y + 11, TerrassicPalette.BASALT_600);
        int f = Math.round(9 * Mth.clamp(fraction, 0.0F, 1.0F));
        if (f > 0) {
            g.fill(x + 1, y + 10 - f, x + 11, y + 10, ready ? TerrassicPalette.AMBER_600 : TerrassicPalette.AMBER_700);
            g.fill(x + 1, y + 10 - f, x + 11, y + 11 - f, ready ? TerrassicPalette.AMBER_300 : TerrassicPalette.AMBER_600);
        }
        int ink = ready ? TerrassicPalette.BASALT_900 : TerrassicPalette.STONE_300;
        if (key == null) {
            for (int ry = 0; ry < MOUSE.length; ry++) {
                for (int rx = 0; rx < MOUSE[ry].length(); rx++) {
                    char c = MOUSE[ry].charAt(rx);
                    if (c != '.') {
                        g.fill(x + 4 + rx, y + 3 + ry, x + 5 + rx, y + 4 + ry,
                                c == 's' ? (ready ? TerrassicPalette.BONE_100 : TerrassicPalette.AMBER_500) : ink);
                    }
                }
            }
        } else {
            Component k = TerrassicFonts.ui(Component.literal(key));
            g.drawString(font, k, x + 6 - font.width(k) / 2, y + 2, TerrassicPalette.rgb(ink), false);
        }
    }

    /** Sedimento text with the study's hard shadow (the slab's outline colour, one pixel down and right). */
    public static int text(GuiGraphics g, Font font, Component text, int x, int y, int colour) {
        Component t = TerrassicFonts.ui(text);
        g.drawString(font, t, x + 1, y + 1, TerrassicPalette.rgb(OUTLINE), false);
        g.drawString(font, t, x, y, TerrassicPalette.rgb(colour), false);
        return x + font.width(t);
    }

    public static int width(Font font, Component text) {
        return font.width(TerrassicFonts.ui(text));
    }

    // ------------------------------------------------------------------ textures

    private record Image(int x0, int y0, int w, int h, int[] argb) {
    }

    private static Baked bake(String key, String version, Image img) {
        NativeImage ni = new NativeImage(img.w(), img.h(), true);
        for (int py = 0; py < img.h(); py++) {
            for (int px = 0; px < img.w(); px++) {
                int c = img.argb()[py * img.w() + px];
                // NativeImage is ABGR
                ni.setPixelRGBA(px, py, (c & 0xFF00FF00) | (c & 0xFF) << 16 | (c >> 16) & 0xFF);
            }
        }
        DynamicTexture tex = new DynamicTexture(ni);
        ResourceLocation id = Terrassic.id("hud_baked/" + key.toLowerCase(java.util.Locale.ROOT).replaceAll("[^a-z0-9_]", "_")
                + "_" + (bakedCount++) + "_" + version);
        Minecraft.getInstance().getTextureManager().register(id, tex);
        return new Baked(id, tex, img.x0(), img.y0(), img.w(), img.h());
    }

    private static void release(Baked b) {
        Minecraft.getInstance().getTextureManager().release(b.id());
    }

    private static void draw(GuiGraphics g, Baked b, int x, int y) {
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        g.blit(b.id(), x + b.x0(), y + b.y0(), 0.0F, 0.0F, b.w(), b.h(), b.w(), b.h());
    }
}
