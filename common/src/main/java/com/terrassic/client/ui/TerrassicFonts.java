package com.terrassic.client.ui;

import com.terrassic.Terrassic;
import com.terrassic.client.ClientConfig;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;

/**
 * The three Terrassic typefaces (docs/IDENTIDADE.md §4), drawn pixel by pixel in tools/fontgen and shipped as
 * Minecraft bitmap fonts (assets/terrassic/font/*.json). Anything a face does not have falls back to the vanilla font.
 * <ul>
 *   <li>{@link #ui}: "Sedimento", the interface face: condensed letters cut in stone (8 px).</li>
 *   <li>{@link #title}: "Entalhe", the display face for titles: an inscription with thick stems and flared serifs
 *       (12 px, capitals only).</li>
 *   <li>{@link #hand}: "Caderno", Dr. Katarina Usha's handwriting, for her pages and notes.</li>
 * </ul>
 * Turned off with "terrassic_fonts": false in config/terrassic-client.json (then everything uses the vanilla font).
 */
public final class TerrassicFonts {
    public static final ResourceLocation SEDIMENTO = Terrassic.id("sedimento");
    public static final ResourceLocation ENTALHE = Terrassic.id("entalhe");
    public static final ResourceLocation CADERNO = Terrassic.id("caderno");

    private TerrassicFonts() {
    }

    public static boolean enabled() {
        return ClientConfig.flag("terrassic_fonts");
    }

    private static MutableComponent with(Component c, ResourceLocation font) {
        MutableComponent copy = c.copy();
        return enabled() ? copy.withStyle(s -> s.withFont(font)) : copy;
    }

    /** Interface text in "Sedimento". */
    public static MutableComponent ui(Component c) {
        return with(c, SEDIMENTO);
    }

    public static MutableComponent ui(String key, Object... args) {
        return ui(Component.translatable(key, args));
    }

    /** A title in "Entalhe". */
    public static MutableComponent title(Component c) {
        return with(c, ENTALHE);
    }

    /** Katarina's handwriting, "Caderno". */
    public static MutableComponent hand(Component c) {
        return with(c, CADERNO);
    }

    /** The interface style, for text boxes (EditBox#setFormatter). */
    public static Style uiStyle() {
        return enabled() ? Style.EMPTY.withFont(SEDIMENTO) : Style.EMPTY;
    }

    public static FormattedCharSequence uiText(String s) {
        return FormattedCharSequence.forward(s, uiStyle());
    }
}
