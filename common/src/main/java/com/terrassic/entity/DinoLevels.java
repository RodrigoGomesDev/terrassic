package com.terrassic.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;

/**
 * ARK-style levels (v0.13, docs/NIVEIS.md): the level and stat points of one animal. DinosaurEntity owns one, saves
 * it and turns {@link #multiplier} into attribute modifiers, torpor and hunger.
 * <p>
 * A wild animal is born at a level from 1 to the "Max wild level" rule, drawn from a curve where half stay at 40 or
 * below and about one in twenty passes 120; every level above 1 is one point in a stat, drawn with the species'
 * weights (giants lean to health, quick hunters to attack). The points are scaled so that a level 40 animal has the
 * species' table values, which is the game as it was before levels: a level 1 has about 70% of the health, a level
 * 150 nearly twice the health and half again the damage.
 * <p>
 * Taming adds bonus levels (half the wild level times the taming effectiveness, drawn like the wild ones). A tame
 * animal then earns experience fighting, carrying a rider and collecting, up to {@link #MAX_TAMED_LEVELS} levels
 * more, and each of those is a point its owner spends on the dino screen.
 * <p>
 * Stamina and weight, in the plan, come with the systems they act on (mount stamina, cargo weight).
 */
public final class DinoLevels {

    public enum Stat {
        HEALTH("health", 0.03D, 0.04D),
        ATTACK("attack", 0.025D, 0.02D),
        /** Not drawn for wild animals (as in ARK): only the owner's points make a mount faster; half a percent each
         *  since v0.15.3 (75 points at 1% made a mount 75% faster). */
        SPEED("speed", 0.0D, 0.005D),
        FOOD("food", 0.02D, 0.05D),
        /** Only wild animals have a use for it (resisting the knockout), so the owner does not spend points on it. */
        TORPOR("torpor", 0.03D, 0.0D);

        public final String key;
        /** Effect of one wild point, before the level-40 scaling. */
        public final double wildPer;
        /** Effect of one point the owner spends: a fraction of the wild value. */
        public final double tamedPer;

        Stat(String key, double wildPer, double tamedPer) {
            this.key = key;
            this.wildPer = wildPer;
            this.tamedPer = tamedPer;
        }

        public boolean drawn() {
            return this.wildPer > 0.0D;
        }

        public boolean spendable() {
            return this.tamedPer > 0.0D;
        }

        public static Stat byKey(String key) {
            for (Stat s : values()) {
                if (s.key.equals(key)) {
                    return s;
                }
            }
            return null;
        }
    }

    public static final int MAX_TAMED_LEVELS = 75;
    /** The wild level whose stats are the species' table values. */
    public static final int REFERENCE_LEVEL = 40;
    /** Shape of the birth curve (a Kumaraswamy distribution): median 40 and 95th percentile 120 on 1-150. */
    private static final double CURVE_A = 0.8D;
    private static final double CURVE_B = 1.65D;

    private static final Stat[] STATS = Stat.values();
    private final double[] weights;
    private final double totalWeight;
    private final int[] wild = new int[STATS.length];
    private final int[] tamed = new int[STATS.length];
    private int tamedLevels;
    private float xp;
    private boolean rolled;

    public DinoLevels(double[] weights) {
        this.weights = weights;
        double total = 0.0D;
        for (Stat s : STATS) {
            if (s.drawn()) {
                total += weights[s.ordinal()];
            }
        }
        this.totalWeight = total;
    }

    /** The species' weights in the draw, from its table health and damage: giants (low damage for their bulk)
     *  lean to health and food, quick hunters (high damage for their bulk) to attack, the rest in between. */
    public static double[] weightsFor(double health, double damage) {
        double ratio = health > 0.0D ? damage / health : 0.1D;
        double[] w = new double[STATS.length];
        if (health >= 200.0D || ratio < 0.07D) {
            w[Stat.HEALTH.ordinal()] = 4.0D;
            w[Stat.ATTACK.ordinal()] = 1.0D;
            w[Stat.FOOD.ordinal()] = 2.0D;
            w[Stat.TORPOR.ordinal()] = 1.0D;
        } else if (ratio >= 0.14D) {
            w[Stat.HEALTH.ordinal()] = 2.5D;
            w[Stat.ATTACK.ordinal()] = 3.0D;
            w[Stat.FOOD.ordinal()] = 1.0D;
            w[Stat.TORPOR.ordinal()] = 1.5D;
        } else {
            w[Stat.HEALTH.ordinal()] = 3.0D;
            w[Stat.ATTACK.ordinal()] = 2.0D;
            w[Stat.FOOD.ordinal()] = 1.5D;
            w[Stat.TORPOR.ordinal()] = 1.5D;
        }
        return w;
    }

    public boolean isRolled() {
        return this.rolled;
    }

    /** Draws a wild animal's level (1 to {@code maxLevel}) and spreads its points. */
    public void roll(RandomSource random, int maxLevel) {
        java.util.Arrays.fill(this.wild, 0);
        double u = random.nextDouble();
        double x = Math.pow(1.0D - Math.pow(1.0D - u, 1.0D / CURVE_B), 1.0D / CURVE_A);
        this.addWildPoints(random, (int) Math.round((Math.max(1, maxLevel) - 1) * x));
        this.rolled = true;
    }

    /** An animal from before the levels keeps the stats it had: the level-40 spread, nothing drawn. */
    public void setReference() {
        for (Stat s : STATS) {
            this.wild[s.ordinal()] = s.drawn() ? (int) Math.round(this.reference(s)) : 0;
        }
        this.rolled = true;
    }

    /** Points spread at random with the species' weights (birth and taming bonus). */
    public void addWildPoints(RandomSource random, int points) {
        for (int i = 0; i < points; i++) {
            double r = random.nextDouble() * this.totalWeight;
            Stat pick = Stat.HEALTH;
            for (Stat s : STATS) {
                if (!s.drawn()) {
                    continue;
                }
                pick = s;
                r -= this.weights[s.ordinal()];
                if (r <= 0.0D) {
                    break;
                }
            }
            this.wild[pick.ordinal()]++;
        }
    }

    /** Points a level 40 animal has in the stat on average. */
    private double reference(Stat s) {
        return this.totalWeight <= 0.0D ? 0.0D : (REFERENCE_LEVEL - 1) * this.weights[s.ordinal()] / this.totalWeight;
    }

    /** What the stat is worth against the species' table value (1.0 = the table). */
    public double multiplier(Stat s) {
        double m = 1.0D;
        if (s.drawn()) {
            m = (1.0D + s.wildPer * this.wild[s.ordinal()]) / (1.0D + s.wildPer * this.reference(s));
        }
        return m * (1.0D + s.tamedPer * this.tamed[s.ordinal()]);
    }

    public int points(Stat s) {
        return this.wild[s.ordinal()] + this.tamed[s.ordinal()];
    }

    public int wildLevel() {
        int level = 1;
        for (int p : this.wild) {
            level += p;
        }
        return level;
    }

    public int level() {
        return this.wildLevel() + this.tamedLevels;
    }

    public int tamedLevels() {
        return this.tamedLevels;
    }

    public int unspent() {
        int spent = 0;
        for (int p : this.tamed) {
            spent += p;
        }
        return this.tamedLevels - spent;
    }

    public float xp() {
        return this.xp;
    }

    /** Experience for the next tame level: 20 + 4n + n²/20 (v0.15.3): 20 for the first, 60 for the tenth, 590 for
     *  the last, about 19,500 in all. */
    public static int xpToNext(int tamedLevels) {
        return Math.round(20.0F + 4.0F * tamedLevels + tamedLevels * tamedLevels / 20.0F);
    }

    /** Adds experience; returns the levels gained (none past {@link #MAX_TAMED_LEVELS}). */
    public int addXp(float amount) {
        if (this.tamedLevels >= MAX_TAMED_LEVELS || amount <= 0.0F) {
            return 0;
        }
        this.xp += amount;
        int gained = 0;
        while (this.tamedLevels < MAX_TAMED_LEVELS && this.xp >= xpToNext(this.tamedLevels)) {
            this.xp -= xpToNext(this.tamedLevels);
            this.tamedLevels++;
            gained++;
        }
        if (this.tamedLevels >= MAX_TAMED_LEVELS) {
            this.xp = 0.0F;
        }
        return gained;
    }

    /** The owner spends a point; false when there is none or the stat takes none. */
    public boolean spend(Stat s) {
        if (!s.spendable() || this.unspent() <= 0) {
            return false;
        }
        this.tamed[s.ordinal()]++;
        return true;
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        CompoundTag wildTag = new CompoundTag();
        CompoundTag tamedTag = new CompoundTag();
        for (Stat s : STATS) {
            wildTag.putInt(s.key, this.wild[s.ordinal()]);
            if (this.tamed[s.ordinal()] > 0) {
                tamedTag.putInt(s.key, this.tamed[s.ordinal()]);
            }
        }
        tag.put("Wild", wildTag);
        tag.put("Tamed", tamedTag);
        tag.putInt("TamedLevels", this.tamedLevels);
        tag.putFloat("Xp", this.xp);
        return tag;
    }

    public void load(CompoundTag tag) {
        CompoundTag wildTag = tag.getCompound("Wild");
        CompoundTag tamedTag = tag.getCompound("Tamed");
        for (Stat s : STATS) {
            this.wild[s.ordinal()] = Math.max(0, wildTag.getInt(s.key));
            this.tamed[s.ordinal()] = Math.max(0, tamedTag.getInt(s.key));
        }
        this.tamedLevels = Mth.clamp(tag.getInt("TamedLevels"), 0, MAX_TAMED_LEVELS);
        this.xp = Math.max(0.0F, tag.getFloat("Xp"));
        this.rolled = true;
    }
}
