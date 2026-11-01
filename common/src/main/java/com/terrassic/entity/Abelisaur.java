package com.terrassic.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;

/**
 * The Carnotaurus rig (tools/modelgen/handmade/carnotaurus, made for it from its own study: 33 animations of its own).
 * The life of an {@link ApexTheropod}, with what this animal does differently:
 * <ul>
 *   <li><b>No loud roar</b>: its roar is short and low. At a rival, over big prey and at a target already close it
 *       locks on instead ("lock_on": it stops, drops the head and stares with both forward eyes, the warning before
 *       the sprint); the plain roar is for what it sees from afar.</li>
 *   <li><b>A weak jaw</b>: mostly quick snaps; the heavy bite rips back with the whole body; now and then the head
 *       turns on its side and a horn flicks the target away ("hook"), which is also the blow at small things at its
 *       feet (the jaws cannot reach down there).</li>
 *   <li><b>Its own idle gestures</b>: besides the common ones, it rubs a horn on a trunk and its tiny arms twitch.</li>
 * </ul>
 */
public abstract class Abelisaur extends ApexTheropod {
    /** The cycles: pixels of ground each one covers (the stride) and its length in ticks (carnoanims.py WALK, RUN,
     *  stalk = the walk at 0.7 of the stride and 1.6 times as long). */
    private static final double WALK_PX = 70.0D;
    private static final double WALK_TICKS = 30.0D;
    private static final double RUN_PX = 128.0D;
    private static final double RUN_TICKS = 12.0D;
    private static final double STALK_PX = 49.0D;
    private static final double STALK_TICKS = 48.0D;
    private static final int LOCK_ON_TICKS = 44;
    /** Closer than this (blocks, size 1.0) a new target gets the stare instead of the roar. */
    private static final double LOCK_RANGE = 12.0D;
    private static final Strike SNAP = new Strike("attack_quick", 4, 19, false);
    private static final Strike BITE_PULL = new Strike("attack", 9, 36, false);
    private static final Strike HOOK = new Strike("hook", 9, 24, false);
    /** The feet blow plays "stomp", which this rig maps onto its hook (actionAnimation). */
    private static final Strike HOOK_LOW = new Strike("stomp", 9, 24, true);
    private static final String[] GESTURES = {"sniff", "look_back", "shake", "yawn", "stretch", "horn_rub", "arm_twitch"};

    protected Abelisaur(EntityType<? extends Abelisaur> type, Level level) {
        super(type, level);
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"roar", "attack_quick", "call", "threat", "drink", "sniff", "look_back", "shake", "yawn", "stretch",
                "stomp", "hook", "lock_on", "shove", "horn_rub", "arm_twitch"};
    }

    @Override
    protected String actionAnimation(String trigger) {
        return "stomp".equals(trigger) ? "hook" : trigger;
    }

    @Override
    protected String[] gestures() {
        return GESTURES;
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
        return "lock_on";
    }

    @Override
    protected int loudTicks() {
        return LOCK_ON_TICKS;
    }

    @Override
    protected boolean loudShakesAir() {
        return false;
    }

    /** A target already close gets the stare; the roar is for what it sees from afar. */
    @Override
    public void roar() {
        LivingEntity target = this.getTarget();
        double range = LOCK_RANGE * this.getScale();
        if (target != null && !this.isTame() && this.distanceToSqr(target) < range * range) {
            this.roarLoud();
        } else {
            super.roar();
        }
    }

    /** Its bite tip stops 4.3 blocks ahead (attack), the T. rex's 6.5 blocks: the same rig units at 16 / 24. */
    @Override
    public double reachScale() {
        return 0.667D;
    }

    @Override
    public Strike feetStrike() {
        return HOOK_LOW;
    }

    @Override
    public Strike biteFor(LivingEntity target) {
        float r = this.getRandom().nextFloat();
        return r < 0.55F ? SNAP : (r < 0.85F ? BITE_PULL : HOOK);
    }
}
