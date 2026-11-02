package com.terrassic.entity;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Triceratops rig (tools/modelgen/handmade/triceratops, its own study and 25 animations). What it adds
 * over a plain herbivore is only what those animations need:
 * <ul>
 *   <li>the walk and the gallop follow the real speed (the feet do not slide); with a target it gallops in the
 *       "charge", head down and the horns levelled;</li>
 *   <li>when it first takes a target that is still some way off it stops and stamps a forefoot before the charge;</li>
 *   <li>about one hit in three is the side sweep of the horns instead of the toss;</li>
 *   <li>a wild adult does not run from a wild predator (it fights back): within 14 blocks it stops, turns to face it
 *       and walks its hind end round its planted forefeet ("pivot");</li>
 *   <li>two adult males close together lock horns and twist; two calves butt each other at play;</li>
 *   <li>an adult (wild or tame, not ridden or sitting) in shallow water, on mud or beside water, around midday,
 *       now and then lies down and wallows; idle, it now and then plows the ground with its beak or shears a
 *       branch.</li>
 * </ul>
 * Gameplay is unchanged: these are gestures, timed so they never fight the attack or the eating.
 */
public abstract class Triceratopsine extends HerbivoreDinosaur {
    /** The cycles (triceranims.py WALK, RUNP, CHARGEP): pixels of ground each covers at 24 px/m and its length in ticks. */
    private static final double WALK_PX = 40.0D;
    private static final double WALK_TICKS = 30.0D;
    private static final double RUN_PX = 84.0D;
    private static final double RUN_TICKS = 14.4D;
    private static final double CHARGE_PX = 92.0D;
    private static final double CHARGE_TICKS = 12.4D;
    private RawAnimation chargeAnim;
    private LivingEntity lastTarget;
    private int pivotCooldown;
    private int still;

    protected Triceratopsine(EntityType<? extends Triceratopsine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "horn_sweep", "horn_lock", "stamp", "pivot", "plow", "shear", "wallow", "butt_play"};
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
        return 56;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** With a target it charges: the gallop with the horns levelled. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving() && this.isAggressive() && !this.isVehicle() && !this.isBaby() && !this.isKnockedOut()
                && !this.isSleeping() && !this.isInSittingPose() && !this.isSwimmingDeep()) {
            if (this.chargeAnim == null) {
                this.chargeAnim = RawAnimation.begin().thenLoop(anim("charge"));
            }
            this.cycleSpeed = this.gaitSpeed(CHARGE_PX / 16.0D / CHARGE_TICKS * this.modelScale());
            return state.setAndContinue(this.chargeAnim);
        }
        return super.movementAnimation(state);
    }

    /** About one hit in three is the side sweep of the horns (the animation only: the damage is the same). */
    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.isBaby() && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "horn_sweep");
        }
        return hit;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.pivotCooldown > 0) {
            this.pivotCooldown--;
        }
        LivingEntity target = this.getTarget();
        // a new target some way off: it stops and stamps before it charges
        if (target != null && target != this.lastTarget && !this.isVehicle() && !this.isBaby() && this.distanceToSqr(target) > 36.0D) {
            this.getLookControl().setLookAt(target, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "stamp");
            this.still = 30;
        }
        this.lastTarget = target;
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            if (target != null) {
                this.getLookControl().setLookAt(target, 30.0F, 30.0F);
            }
            return;
        }
        if (target != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut()) {
            return;
        }
        if (!this.isTame() && !this.isBaby() && this.pivotCooldown == 0 && this.tickCount % 20 == 0) {
            List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(14.0D),
                    p -> p.isAlive() && !p.isTame() && !p.isBaby());
            if (!near.isEmpty()) {
                this.getLookControl().setLookAt(near.get(0), 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "pivot");
                this.still = 48;
                this.pivotCooldown = 400;
                return;
            }
        }
        if (!this.getNavigation().isDone()) {
            return;
        }
        if (this.isBaby()) {
            if (this.random.nextInt(600) == 0) {
                Triceratopsine other = this.nearest(3.0D, true);
                if (other != null && !other.isSleeping()) {
                    this.getLookControl().setLookAt(other, 30.0F, 30.0F);
                    other.getLookControl().setLookAt(this, 30.0F, 30.0F);
                    triggerAnim(ACTION_CONTROLLER, "butt_play");
                    other.triggerAnim(ACTION_CONTROLLER, "butt_play");
                }
            }
            return;
        }
        long time = this.level().getDayTime() % 24000L;
        if (time > 4000L && time < 9000L && this.random.nextInt(500) == 0 && this.byWetGround()) {
            triggerAnim(ACTION_CONTROLLER, "wallow");
            this.still = 120;
            return;
        }
        if (this.random.nextInt(800) != 0) {
            return;
        }
        Triceratopsine other = this.nearest(4.5D, false);
        if (other != null && !this.isFemale() && !other.isFemale() && !other.isSleeping() && other.getTarget() == null
                && !other.isVehicle() && this.random.nextBoolean()) {
            this.getLookControl().setLookAt(other, 30.0F, 30.0F);
            other.getLookControl().setLookAt(this, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "horn_lock");
            other.triggerAnim(ACTION_CONTROLLER, "horn_lock");
            this.still = 64;
            other.still = 64;
        } else {
            triggerAnim(ACTION_CONTROLLER, this.random.nextBoolean() ? "plow" : "shear");
        }
    }

    /** Shallow water, mud underfoot, or water within two blocks of its feet: where it lies down to wallow. */
    private boolean byWetGround() {
        if (this.isInWater()) {
            return this.getFluidHeight(FluidTags.WATER) < this.getBbHeight() * 0.35D;
        }
        BlockPos feet = this.blockPosition();
        if (this.level().getBlockState(feet.below()).is(Blocks.MUD) || this.level().getBlockState(feet).is(Blocks.MUD)) {
            return true;
        }
        for (BlockPos p : BlockPos.betweenClosed(feet.offset(-2, -1, -2), feet.offset(2, 0, 2))) {
            if (this.level().getFluidState(p).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }

    private Triceratopsine nearest(double range, boolean baby) {
        Triceratopsine best = null;
        double bestD = Double.MAX_VALUE;
        for (Triceratopsine e : this.level().getEntitiesOfClass(Triceratopsine.class, this.getBoundingBox().inflate(range),
                e -> e != this && e.isAlive() && e.isBaby() == baby)) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }
}
