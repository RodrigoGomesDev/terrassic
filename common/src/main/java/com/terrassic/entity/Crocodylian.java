package com.terrassic.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Deinosuchus rig (tools/modelgen/handmade/deinosuchus, its own study, page "Deinossuco: estudo para a
 * 1.8", and 23 animations). What it adds over a plain predator is only what those animations need:
 * <ul>
 *   <li>the high walk and the run follow the real speed; still in the water it floats like a log ("float");</li>
 *   <li>its first strike on a target is the lunge from the water's edge; a strike on a target in the water is
 *       followed by the death roll; now and then a strike is the tail sweep instead;</li>
 *   <li>idle on land near water in the warm of the day it basks with its mouth open; an adult male in the water
 *       now and then bellows or slaps its jaw on the water; a baby chirps for the adults nearby.</li>
 * </ul>
 * Gameplay is unchanged: these are gestures, timed so they never fight the attack or the eating.
 */
public abstract class Crocodylian extends PredatorDinosaur {
    /** The cycles (deinoanims.py WALK, RUNP): ground each covers at 20 px/m (about 1.4 and 1.9 m) and its length in ticks. */
    private static final double WALK_BLOCKS = 1.4D;
    private static final double WALK_TICKS = 32.0D;
    private static final double RUN_BLOCKS = 1.9D;
    private static final double RUN_TICKS = 18.0D;
    private RawAnimation floatAnim;
    private LivingEntity lastTarget;
    private int still;

    protected Crocodylian(EntityType<? extends Crocodylian> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"lunge", "death_roll", "tail_sweep", "bask", "bellow", "head_slap", "chirp", "gape_threat"};
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
        return 52;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_BLOCKS / WALK_TICKS * this.modelScale() / 0.8D;
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_BLOCKS / RUN_TICKS * this.modelScale() / 0.8D;
    }

    /** Still in the water: it floats like a log. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (!state.isMoving() && this.isInWater() && !this.onGround() && !this.isSleeping() && !this.isKnockedOut()
                && !this.isInSittingPose()) {
            if (this.floatAnim == null) {
                this.floatAnim = RawAnimation.begin().thenLoop(anim("float"));
            }
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(this.floatAnim);
        }
        return super.movementAnimation(state);
    }

    /** At home in the water: floats and dives smoothly, no hops (HOTFIX 1.9.1, DinosaurEntity.smoothWater). */
    @Override
    protected boolean smoothWater() {
        return true;
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean first = target != this.lastTarget;
        this.lastTarget = target instanceof LivingEntity living ? living : null;
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.isBaby()) {
            if (first) {
                triggerAnim(ACTION_CONTROLLER, "lunge");
            } else if (target.isInWaterOrBubble()) {
                triggerAnim(ACTION_CONTROLLER, "death_roll");
                this.still = 36;
            } else if (this.random.nextInt(4) == 0) {
                triggerAnim(ACTION_CONTROLLER, "tail_sweep");
            }
        }
        return hit;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut()
                || !this.getNavigation().isDone()) {
            return;
        }
        if (this.isBaby()) {
            if (this.random.nextInt(500) == 0) {
                triggerAnim(ACTION_CONTROLLER, "chirp");
                this.playAmbientSound();
            }
            return;
        }
        if (this.isInWater()) {
            if (!this.isFemale() && this.random.nextInt(1200) == 0) {
                triggerAnim(ACTION_CONTROLLER, "bellow");
                this.playAmbientSound();
                this.still = 80;
            } else if (this.random.nextInt(1000) == 0) {
                triggerAnim(ACTION_CONTROLLER, "head_slap");
            }
            return;
        }
        long time = this.level().getDayTime() % 24000L;
        if (time > 2000L && time < 10000L && this.random.nextInt(600) == 0 && this.nearWater()) {
            triggerAnim(ACTION_CONTROLLER, "bask");
            this.still = 120;
        }
    }

    /** Water within three blocks: the bank where it basks. */
    private boolean nearWater() {
        BlockPos feet = this.blockPosition();
        for (BlockPos p : BlockPos.betweenClosed(feet.offset(-3, -1, -3), feet.offset(3, 0, 3))) {
            if (this.level().getFluidState(p).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }
}
