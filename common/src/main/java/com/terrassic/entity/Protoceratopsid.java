package com.terrassic.entity;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Protoceratops rig (tools/modelgen/handmade/protoceratops, its own study and 26 animations): the first
 * quadruped of the hand-made rigs. What it adds over a plain herbivore is only what the animations need:
 * <ul>
 *   <li>the walk and the trot cycles follow the real speed (the feet do not slide); the baby runs on its hind legs
 *       and sleeps curled up ("run_biped", "huddle");</li>
 *   <li>about one bite in three it does not let go ("bite_hold", the Fighting Dinosaurs grip);</li>
 *   <li>a wild one freezes for two seconds when a wild predator comes within 12 blocks;</li>
 *   <li>two adults close together: one shoves, the other shows the frill; alone, now and then it sways the sail of its
 *       tail or shakes the sand off;</li>
 *   <li>at noon on sand a wild adult scrapes a shallow bed and naps in it for a minute (the sleep goal does the rest).</li>
 * </ul>
 * Gameplay is unchanged: these are gestures, timed so they never fight the attack or the eating.
 */
public abstract class Protoceratopsid extends HerbivoreDinosaur {
    /** The cycles (protoanims.py WALK, TROTP): pixels of ground each covers at 48 px/m and its length in ticks. */
    private static final double WALK_PX = 30.0D;
    private static final double WALK_TICKS = 20.0D;
    private static final double RUN_PX = 56.0D;
    private static final double RUN_TICKS = 11.2D;
    private static final double BIPED_PX = 48.0D;
    private static final double BIPED_TICKS = 8.8D;
    private static final int NOON_NAP = 1200;
    private RawAnimation bipedAnim;
    private RawAnimation huddleAnim;
    private int freezeCooldown;
    private int frozen;
    private int noonNap;

    protected Protoceratopsid(EntityType<? extends Protoceratopsid> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "dig", "bite_hold", "shove", "frill_show", "sail_sway", "freeze", "sand_shake", "scrape_rest"};
    }

    @Override
    protected boolean hasSleepAnim() {
        return true;
    }

    @Override
    protected boolean hasSwimAnim() {
        return true;
    }

    @Override
    protected boolean flinches() {
        return true;
    }

    @Override
    protected int deathAnimTicks() {
        return 48;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** The baby: up on two legs when it runs, curled tight when it sleeps. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.isBaby() && !this.isKnockedOut()) {
            if (this.isSleeping()) {
                if (this.huddleAnim == null) {
                    this.huddleAnim = RawAnimation.begin().thenLoop(anim("huddle"));
                }
                this.cycleSpeed = 1.0D;
                return state.setAndContinue(this.huddleAnim);
            }
            boolean running = this.isAggressive() || this.getDeltaMovement().horizontalDistanceSqr() > this.runThresholdSqr();
            if (state.isMoving() && running && !this.isSwimmingDeep() && !this.isInSittingPose()) {
                if (this.bipedAnim == null) {
                    this.bipedAnim = RawAnimation.begin().thenLoop(anim("run_biped"));
                }
                this.cycleSpeed = this.gaitSpeed(BIPED_PX / 16.0D / BIPED_TICKS * this.modelScale());
                return state.setAndContinue(this.bipedAnim);
            }
        }
        return super.movementAnimation(state);
    }

    /** About one bite in three it holds on and wrenches (the animation only: the damage is the same). */
    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.isBaby() && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "bite_hold");
        }
        return hit;
    }

    /** Its noon nap counts as sleep time, so the sleep goal lays it down and wakes it when the minute is over. */
    @Override
    public boolean isSleepTime() {
        return super.isSleepTime() || this.noonNap > 0;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.noonNap > 0) {
            this.noonNap--;
        }
        if (this.freezeCooldown > 0) {
            this.freezeCooldown--;
        }
        if (this.frozen > 0) {
            this.frozen--;
            this.getNavigation().stop();
            return;
        }
        if (this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut()
                || this.isInWater()) {
            return;
        }
        if (!this.isTame() && this.freezeCooldown == 0 && this.tickCount % 20 == 0) {
            List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(12.0D),
                    p -> p.isAlive() && !p.isTame());
            if (!near.isEmpty()) {
                this.getLookControl().setLookAt(near.get(0), 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "freeze");
                this.frozen = 40;
                this.freezeCooldown = 600;
                return;
            }
        }
        if (!this.getNavigation().isDone()) {
            return;
        }
        BlockPos below = this.blockPosition().below();
        boolean sand = this.level().getBlockState(below).is(BlockTags.SAND);
        if (this.isBaby()) {
            if (sand && this.random.nextInt(1400) == 0) {
                triggerAnim(ACTION_CONTROLLER, "sand_shake");
            }
            return;
        }
        long time = this.level().getDayTime() % 24000L;
        if (!this.isTame() && sand && time > 5000L && time < 7500L && this.noonNap == 0 && this.random.nextInt(400) == 0
                && !this.level().isRaining()) {
            triggerAnim(ACTION_CONTROLLER, "scrape_rest");
            this.noonNap = NOON_NAP;
            return;
        }
        if (this.random.nextInt(700) != 0) {
            return;
        }
        Protoceratopsid other = this.nearestAdult(this.random.nextBoolean() ? 2.5D : 8.0D);
        if (other != null && this.distanceToSqr(other) < 6.25D && !other.isSleeping() && other.getTarget() == null) {
            this.getLookControl().setLookAt(other, 30.0F, 30.0F);
            other.getLookControl().setLookAt(this, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "shove");
            other.triggerAnim(ACTION_CONTROLLER, "frill_show");
        } else if (other != null) {
            this.getLookControl().setLookAt(other, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "frill_show");
        } else {
            triggerAnim(ACTION_CONTROLLER, sand && this.random.nextBoolean() ? "sand_shake" : "sail_sway");
        }
    }

    private Protoceratopsid nearestAdult(double range) {
        Protoceratopsid best = null;
        double bestD = Double.MAX_VALUE;
        for (Protoceratopsid e : this.level().getEntitiesOfClass(Protoceratopsid.class, this.getBoundingBox().inflate(range),
                e -> e != this && e.isAlive() && !e.isBaby())) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }
}
