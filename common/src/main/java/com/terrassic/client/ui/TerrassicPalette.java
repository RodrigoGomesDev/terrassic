package com.terrassic.client.ui;

/**
 * The Terrassic palette, "Âmbar e Basalto" (docs/IDENTIDADE.md): one source for every colour the mod draws by code
 * (screens, HUD, toasts, title). ARGB ints, opaque unless the name says otherwise.
 * <p>
 * The identity: dark volcanic basalt for panels, warm limestone and bone for text, amber (the Rift's Temporal Amber)
 * as the one accent, the orange of the Rift for alerts, the dusk purple of the cover for brand moments, and the
 * paper and ink of Katarina's notebook for anything read like a book. Never cyan glass or hexagons (that is ARK), never
 * the red, yellow and black of a certain film logo.
 */
public final class TerrassicPalette {
    // basalt: backgrounds, from deepest to raised
    public static final int BASALT_950 = 0xFF0E0B0E;
    public static final int BASALT_900 = 0xFF141014;
    public static final int BASALT_800 = 0xFF1C181E;
    public static final int BASALT_700 = 0xFF2A2329;
    public static final int BASALT_600 = 0xFF3A3036;
    public static final int BASALT_500 = 0xFF524550;

    // stone and bone: text and lines
    public static final int STONE_400 = 0xFF8A7C6A;
    public static final int STONE_300 = 0xFFB3A48C;
    public static final int STONE_200 = 0xFFD8CCB2;
    public static final int BONE_100 = 0xFFEFE6D2;

    // amber: the accent (interaction, selection, progress)
    public static final int AMBER_700 = 0xFFB9771C;
    public static final int AMBER_600 = 0xFFD9952C;
    public static final int AMBER_500 = 0xFFF2B544;
    public static final int AMBER_300 = 0xFFFFD27A;

    // signals
    public static final int RIFT_500 = 0xFFF07A1A;   // the Rift: alerts, storms, bosses
    public static final int DUSK_700 = 0xFF3A2240;   // brand: title, intro, trailers
    public static final int DUSK_500 = 0xFF5E3866;
    public static final int FERN_400 = 0xFF7FAF55;   // done, science, safe
    public static final int BLOOD_500 = 0xFFC4473A;  // health, danger
    public static final int SKY_400 = 0xFF8FB4C8;    // stamina, water (muted, never neon)

    // Katarina's notebook
    public static final int PAPER = 0xFFE9DCBC;
    public static final int PAPER_DARK = 0xFFD8C79E;
    public static final int LEATHER = 0xFF5A3620;
    public static final int INK = 0xFF3B2A1A;
    public static final int INK_SOFT = 0xFF7A6448;

    // translucent variants for panels drawn over the world
    public static final int PANEL_OVER_WORLD = 0xE01C181E;
    public static final int SHADE = 0x80000000;

    private TerrassicPalette() {
    }

    /** The colour with a new alpha (0-255). */
    public static int alpha(int argb, int alpha) {
        return (alpha & 0xFF) << 24 | (argb & 0x00FFFFFF);
    }

    /** RGB only, for the font calls that take 0xRRGGBB. */
    public static int rgb(int argb) {
        return argb & 0x00FFFFFF;
    }
}
