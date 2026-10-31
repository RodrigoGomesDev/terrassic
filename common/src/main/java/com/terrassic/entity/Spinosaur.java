package com.terrassic.entity;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.level.Level;

/**
 * The Spinosaurus rig (tools/modelgen/handmade/spinosaurus, the theropod template plus its own fish, display, swipe and
 * swim). The life of an {@link ApexTheropod}, with what the rig does differently:
 * <ul>
 *   <li><b>Fishing</b>: what swims is caught with "fish", head low over the water, the snap at 2.1 s, and is a meal.
 *       One that dives out of reach is let go.</li>
 *   <li><b>The sail</b>: no loud roar and no wave in the air: at a rival, over big prey and at a target already close it
 *       shows the sail ("display"), the plain roar is for what it sees from afar.</li>
 *   <li><b>The thumb claw</b>: "swipe" takes the place of the stomp at small things and alternates with the heavy bite.</li>
 * </ul>
 */
public abstract class Spinosaur extends ApexTheropod {
    /** The cycles: pixels of ground each one covers and its length in ticks (spinoanims.py). */
    private static final double WALK_PX = 62.0D;
    private static final double WALK_TICKS = 40.0D;
    private static final double RUN_PX = 108.0D;
    private static final double RUN_TICKS = 17.0D;
    private static final double STALK_PX = 48.36D;
    private static final double STALK_TICKS = 58.8D;
    private static final int DISPLAY_TICKS = 64;
    /** Closer than this (blocks, size 1.0) a new target gets the sail instead of the roar. */
    private static final double DISPLAY_RANGE = 14.0D;
    /** A fish further up or down than this is out of reach: the fight has no path through the water, so it lets it go. */
    private static final double FISH_REACH_Y = 2.0D;
    /** What a fish fills of the hunger gauge. */
    private static final int FISH_MEAL = 20;
    private static final Strike FISH = new Strike("fish", 42, 76, false);
    private static final Strike SWIPE = new Strike("swipe", 11, 26, false);
    private static final Strike SWIPE_LOW = new Strike("swipe", 11, 26, true);

    private boolean swipeNext;

    protected Spinosaur(EntityType<? extends Spinosaur> type, Level level) {
        super(type, level);
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"roar", "attack_quick", "call", "threat", "drink", "sniff", "look_back", "shake", "yawn", "stretch",
                "fish", "display", "swipe"};
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    @Override
    protected double stalkCycleSpeed() {
        return STALK_PX / 16.0D / STALK_TICKS * this.modelScale();
    }

    @Override
    protected String loudAnim() {
        return "display";
    }

    @Override
    protected int loudTicks() {
        return DISPLAY_TICKS;
    }

    @Override
    protected boolean loudShakesAir() {
        return false;
    }

    /** A target already close gets the sail; the roar is for what it sees from afar. */
    @Override
    public void roar() {
        LivingEntity target = this.getTarget();
        double range = DISPLAY_RANGE * this.getScale();
        if (target != null && !this.isTame() && this.distanceToSqr(target) < range * range) {
            this.roarLoud();
        } else {
            super.roar();
        }
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        return super.canAttack(target) && (!(target instanceof WaterAnimal) || Math.abs(target.getY() - this.getY()) < FISH_REACH_Y);
    }

    @Override
    public boolean killedEntity(ServerLevel level, LivingEntity killed) {
        boolean result = super.killedEntity(level, killed);
        if (killed instanceof WaterAnimal) {
            this.feed(FISH_MEAL);
        }
        return result;
    }

    /** Fish are taken from above with the neck, not at the feet. */
    @Override
    public boolean strikesAtFeet(LivingEntity target) {
        return !(target instanceof WaterAnimal) && super.strikesAtFeet(target);
    }

    @Override
    public Strike feetStrike() {
        return SWIPE_LOW;
    }

    @Override
    public Strike biteFor(LivingEntity target) {
        if (target instanceof WaterAnimal) {
            return FISH;
        }
        if (this.getRandom().nextFloat() >= 0.3F) {
            return QUICK_BITE;
        }
        this.swipeNext = !this.swipeNext;
        return this.swipeNext ? BITE : SWIPE;
    }
}
