package com.terrassic.research;

/**
 * Field Journal objectives of Chapter 1 (docs/HISTORIA.md, section 5): 4 themes with 3 objectives each, 2 of 3
 * complete a theme. Each one is also a vanilla advancement (data/terrassic/advancements/chapter1/&lt;id&gt;.json,
 * criterion "done") so it shows in the advancements screen. Objectives whose feature is not in the game yet are
 * listed with their hint but cannot be completed.
 */
public enum Objective {
    SHELTER(Theme.SURVIVAL, true),
    FIRST_SPEAR(Theme.SURVIVAL, true),
    RIFT_STORM(Theme.SURVIVAL, false),
    STUDY_FIVE(Theme.SCIENCE, true),
    FIRST_FOSSIL(Theme.SCIENCE, true),
    RESEARCH_TABLE(Theme.SCIENCE, true),
    TAME_HERBIVORE(Theme.TAMING, true),
    HATCH_EGG(Theme.TAMING, true),
    RIDE(Theme.TAMING, true),
    KATARINA_CAMPS(Theme.EXPLORATION, false),
    RIFT_RUIN(Theme.EXPLORATION, false),
    MIGRATION(Theme.EXPLORATION, false);

    public enum Theme {
        SURVIVAL, SCIENCE, TAMING, EXPLORATION;

        public String id() {
            return this.name().toLowerCase(java.util.Locale.ROOT);
        }
    }

    /** Thatch blocks to place for {@link #SHELTER}. */
    public static final int SHELTER_BLOCKS = 16;
    /** Studied species for {@link #STUDY_FIVE}. */
    public static final int STUDY_SPECIES = 5;
    /** Objectives of a theme needed to complete it. */
    public static final int PER_THEME = 2;

    private final Theme theme;
    private final boolean available;

    Objective(Theme theme, boolean available) {
        this.theme = theme;
        this.available = available;
    }

    public String id() {
        return this.name().toLowerCase(java.util.Locale.ROOT);
    }

    public Theme theme() {
        return this.theme;
    }

    /** false = the feature it needs is not in the game yet. */
    public boolean available() {
        return this.available;
    }

    public String advancement() {
        return "chapter1/" + this.id();
    }
}
