package com.terrassic.client;

import com.terrassic.research.Lore;
import net.minecraft.Util;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;

import java.util.List;

/**
 * Intro shown the first time a player enters the world (docs/HISTORIA.md, section 2): dark screen with an amber
 * glow, the lines appear one at a time and the era name comes last. About 25 seconds; Esc skips it. The full story
 * stays in the Report tab of the Field Notebook.
 */
public class IntroScreen extends Screen {
    private static final long LINE_MS = 3800L;
    private static final long FADE_MS = 1200L;
    private static final long END_HOLD_MS = 4500L;

    private long start = -1L;

    public IntroScreen() {
        super(Component.translatable("intro.terrassic.era"));
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        long now = Util.getMillis();
        if (this.start < 0L) {
            this.start = now;
        }
        long t = now - this.start;
        g.fill(0, 0, this.width, this.height, 0xFF0B0805);
        // amber glow in the middle, stronger as the story goes on
        int glow = (int) (Mth.clamp(t / (float) (LINE_MS * Lore.INTRO_LINES), 0.0F, 1.0F) * 70.0F);
        g.fillGradient(0, this.height / 3, this.width, this.height / 2, 0x00000000, (glow << 24) | 0x5A3208);
        g.fillGradient(0, this.height / 2, this.width, this.height * 2 / 3, (glow << 24) | 0x5A3208, 0x00000000);

        int y = this.height / 2 - Lore.INTRO_LINES * 12;
        for (int i = 0; i < Lore.INTRO_LINES; i++) {
            int alpha = alpha(t - i * LINE_MS);
            List<FormattedCharSequence> lines = this.font.split(com.terrassic.client.ui.TerrassicFonts.ui("intro.terrassic.line." + i), this.width - 60);
            for (FormattedCharSequence line : lines) {
                if (alpha > 8) {
                    g.drawString(this.font, line, (this.width - this.font.width(line)) / 2, y, (alpha << 24) | 0xE8C890, false);
                }
                y += 11;
            }
            y += 6;
        }
        long eraAt = Lore.INTRO_LINES * LINE_MS;
        int eraAlpha = alpha(t - eraAt);
        if (eraAlpha > 8) {
            Component era = com.terrassic.client.ui.TerrassicFonts.title(Component.translatable("intro.terrassic.era"));
            g.pose().pushPose();
            g.pose().translate(this.width / 2.0F, y + 14, 0.0F);
            g.pose().scale(1.25F, 1.25F, 1.0F);
            g.drawString(this.font, era, -this.font.width(era) / 2, 0, (eraAlpha << 24) | 0xF0A030, false);
            g.pose().popPose();
        }
        Component skip = com.terrassic.client.ui.TerrassicFonts.ui("intro.terrassic.skip");
        g.drawString(this.font, skip, this.width - this.font.width(skip) - 8, this.height - 14, 0x80A08870, false);
        if (t > eraAt + END_HOLD_MS) {
            this.onClose();
        }
    }

    /** 0..255 fade-in over FADE_MS once a line's time has come. */
    private static int alpha(long sinceShown) {
        if (sinceShown <= 0L) {
            return 0;
        }
        return (int) (Mth.clamp(sinceShown / (float) FADE_MS, 0.0F, 1.0F) * 255.0F);
    }
}
