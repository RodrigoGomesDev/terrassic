package com.terrassic.entity;

/**
 * How a tamed dinosaur meets a fight (v0.16, docs/ORDENS.md), chosen on its dino screen and saved on the animal.
 * <ul>
 *   <li>{@link #PASSIVE}: never attacks, not even to defend itself or its owner (the rider still drives its attack).</li>
 *   <li>{@link #NEUTRAL}, the default: defends itself and its owner and joins the owner's fights, except the ones the
 *       owner starts against a player or someone's tamed animal.</li>
 *   <li>{@link #AGGRESSIVE}: joins every fight of its owner and also goes for monsters (not creepers) and wild
 *       dinosaurs that come within {@link DinosaurEntity#AGGRESSIVE_RANGE} blocks.</li>
 * </ul>
 */
public enum DinoStance {
    PASSIVE("passive"),
    NEUTRAL("neutral"),
    AGGRESSIVE("aggressive");

    /** Lang key part and save name. */
    public final String key;

    DinoStance(String key) {
        this.key = key;
    }

    /** The next one on the screen's button (passive, neutral, aggressive, passive...). */
    public DinoStance next() {
        return values()[(this.ordinal() + 1) % values().length];
    }

    public static DinoStance byKey(String key) {
        for (DinoStance stance : values()) {
            if (stance.key.equals(key)) {
                return stance;
            }
        }
        return NEUTRAL;
    }
}
