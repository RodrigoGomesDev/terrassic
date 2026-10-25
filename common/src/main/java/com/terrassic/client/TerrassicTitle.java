package com.terrassic.client;

import com.terrassic.Terrassic;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.client.ui.TerrassicFonts;
import com.terrassic.client.ui.TerrassicUi;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.CubeMap;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.RandomSource;

import java.util.List;

/**
 * The Terrassic look of the title and loading screens (v0.8, phase M2). Art made by tools/capagen/panorama.py and
 * title.py; texts in tools/javagen/menu_texts.py. Wired in by the client mixins TitleScreenMixin,
 * LevelLoadingScreenMixin and ReceivingLevelScreenMixin, and switched off in config/terrassic-client.json
 * ({@link ClientConfig}).
 */
public final class TerrassicTitle {
    /** Late Cretaceous dusk: the Rift in the sky, the lake, the herd, the T. rex on the rise. */
    public static final CubeMap CUBE_MAP = new CubeMap(Terrassic.id("textures/gui/title/background/panorama"));
    /** 256x64 stone wordmark, drawn 1:1 where the Minecraft logo goes. */
    public static final ResourceLocation LOGO = Terrassic.id("textures/gui/title/terrassic.png");

    private static final RandomSource RANDOM = RandomSource.create();
    private static final int LOGO_Y = 30;
    private static final int PAPER = 0xE8DCC0;

    private TerrassicTitle() {
    }

    /** Draws the logo and the chapter line, fading with {@code alpha} like the vanilla logo. */
    public static void renderLogo(GuiGraphics graphics, int screenWidth, float alpha) {
        graphics.setColor(1.0F, 1.0F, 1.0F, alpha);
        graphics.blit(LOGO, screenWidth / 2 - 128, LOGO_Y - 6, 0.0F, 0.0F, 256, 64, 256, 64);
        graphics.setColor(1.0F, 1.0F, 1.0F, 1.0F);
        int a = Math.max(4, (int) (alpha * 255.0F)) << 24;
        graphics.drawCenteredString(Minecraft.getInstance().font, TerrassicFonts.ui("menu.terrassic.subtitle"),
                screenWidth / 2, LOGO_Y + 46, PAPER | a);
    }

    /** A random line among splash.terrassic.0..n (counted from the language file, so the list can grow). */
    public static String randomSplash() {
        int n = count("splash.terrassic.");
        return n == 0 ? null : I18n.get("splash.terrassic." + RANDOM.nextInt(n));
    }

    /** A random loading tip among tip.terrassic.0..n, or null when there is none. */
    public static Component randomTip() {
        int n = count("tip.terrassic.");
        return n == 0 ? null : Component.translatable("tip.terrassic." + RANDOM.nextInt(n));
    }

    /**
     * Draws "Did you know?" and the tip, wrapped, on a basalt slab near the bottom of a loading screen
     * (docs/IDENTIDADE.md: TerrassicUi.slab, amber title, stone text).
     */
    public static void renderTip(GuiGraphics graphics, Component tip, int width, int height) {
        if (tip == null) {
            return;
        }
        var font = Minecraft.getInstance().font;
        int panel = Math.min(320, width - 20);
        List<FormattedCharSequence> lines = font.split(TerrassicFonts.ui(tip), panel - 20);
        int y1 = height - 8;
        int y0 = y1 - 26 - lines.size() * 10;
        TerrassicUi.slab(graphics, (width - panel) / 2, y0, (width + panel) / 2, y1);
        graphics.drawCenteredString(font, TerrassicFonts.ui("menu.terrassic.did_you_know"), width / 2, y0 + 9,
                TerrassicPalette.rgb(TerrassicPalette.AMBER_500));
        int y = y0 + 21;
        for (FormattedCharSequence line : lines) {
            graphics.drawCenteredString(font, line, width / 2, y, TerrassicPalette.rgb(TerrassicPalette.STONE_200));
            y += 10;
        }
    }

    private static int count(String prefix) {
        int n = 0;
        while (n < 1000 && I18n.exists(prefix + n)) {
            n++;
        }
        return n;
    }
}
