package com.terrassic.entity;

import com.terrassic.entity.ai.BroodGoal;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The hand-made Gallimimus rig (tools/modelgen/handmade/gallimimus, its own study and 24 animations). What it adds
 * over a plain runner is only what those animations and the study need:
 * <ul>
 *   <li>the walk and the sprint follow the real speed (the feet do not slide);</li>
 *   <li>fleeing at full speed it jinks now and then: a hard side-step that throws a chaser off (the "jink");</li>
 *   <li>a wild adult that sees a wild predator further off than it flees from rises tall and watches it
 *       ("sentinel"); now and then a wild one keeps watch for its flock the same way;</li>
 *   <li>a wild adult male near an adult female now and then dances for her with his feathered arms
 *       ("wing_display", Zelenitsky et al. 2012);</li>
 *   <li>idle: it dabbles in shallow water ("sift"), swallows a pebble on sand or gravel ("grit"), hooks a leafy branch
 *       down with its hand and nips it ("browse", a small meal), preens;</li>
 *   <li>it broods: wild ones sit on clutches they find, with the arms spread over the eggs ("brood");</li>
 *   <li>taming: a wild one runs from a standing player, but lets a CROUCHING player who holds its food come close
 *       (a flighty bird is approached low and slow), so it can be hand-fed.</li>
 * </ul>
 * The young have no wing fans: the renderer hides the bones "adult_l" / "adult_r" on babies (DinoGeoModel).
 */
public abstract class Ornithomimid extends HerbivoreDinosaur {
    /** The cycles (gallianims.py WALK, RUN): pixels of ground each covers at 32 px/m and its length in ticks. */
    private static final double WALK_PX = 56.0D;
    private static final double WALK_TICKS = 24.0D;
    private static final double RUN_PX = 120.0D;
    private static final double RUN_TICKS = 10.0D;
    private int jinkCooldown;
    private int watchCooldown;
    private int still;

    protected Ornithomimid(EntityType<? extends Ornithomimid> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "jink", "sentinel", "preen", "wing_display", "grit", "sift", "browse"};
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
        return 60;
    }

    @Override
    protected boolean brooder() {
        return true;
    }

    @Override
    protected void addExtraGoals() {
        this.goalSelector.addGoal(7, new BroodGoal(this));
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** A crouching player holding its food may come close: the way to hand-feed a flighty runner. */
    @Override
    protected boolean fleesFrom(Player player) {
        return !(player.isCrouching() && (this.isFood(player.getMainHandItem()) || this.isFood(player.getOffhandItem())));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.jinkCooldown > 0) {
            this.jinkCooldown--;
        }
        if (this.watchCooldown > 0) {
            this.watchCooldown--;
        }
        // the jink: wild, running flat out, not ridden
        if (!this.isTame() && !this.isVehicle() && !this.isBaby() && this.jinkCooldown == 0 && this.onGround()
                && this.getDeltaMovement().horizontalDistanceSqr() > this.runThresholdSqr() * 1.5D && this.random.nextInt(25) == 0) {
            Vec3 v = this.getDeltaMovement();
            Vec3 side = new Vec3(-v.z, 0.0D, v.x).normalize().scale((this.random.nextBoolean() ? 1.0D : -1.0D) * 0.35D);
            this.setDeltaMovement(v.add(side));
            triggerAnim(ACTION_CONTROLLER, "jink");
            this.jinkCooldown = 50 + this.random.nextInt(40);
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut()
                || !this.getNavigation().isDone() || this.isBaby()) {
            return;
        }
        // the lookout: a wild predator in sight, further than it runs from (14 blocks)
        if (!this.isTame() && this.watchCooldown == 0 && this.tickCount % 20 == 0) {
            List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(26.0D),
                    p -> p.isAlive() && !p.isTame() && !p.isBaby() && p.distanceToSqr(this) > 14.0D * 14.0D && this.hasLineOfSight(p));
            if (!near.isEmpty() || this.random.nextInt(60) == 0) {
                if (!near.isEmpty()) {
                    this.getLookControl().setLookAt(near.get(0), 30.0F, 30.0F);
                }
                triggerAnim(ACTION_CONTROLLER, "sentinel");
                this.still = 84;
                this.watchCooldown = 300 + this.random.nextInt(300);
                return;
            }
        }
        if (this.random.nextInt(500) != 0) {
            return;
        }
        BlockPos below = this.blockPosition().below();
        BlockState ground = this.level().getBlockState(below);
        if (this.isInWater() && this.getFluidHeight(FluidTags.WATER) < this.getBbHeight() * 0.35D) {
            triggerAnim(ACTION_CONTROLLER, "sift");
            this.still = 80;
            return;
        }
        if (ground.is(BlockTags.SAND) || ground.is(Blocks.GRAVEL)) {
            triggerAnim(ACTION_CONTROLLER, "grit");
            this.still = 56;
            return;
        }
        if (this.leavesInReach()) {
            triggerAnim(ACTION_CONTROLLER, "browse");
            this.still = 70;
            this.feed(4);
            return;
        }
        if (!this.isTame() && !this.isFemale()) {
            Ornithomimid mate = this.nearestFemale();
            if (mate != null && this.random.nextInt(3) == 0) {
                this.getLookControl().setLookAt(mate, 30.0F, 30.0F);
                mate.getLookControl().setLookAt(this, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "wing_display");
                this.still = 96;
                mate.still = 60;
                return;
            }
        }
        triggerAnim(ACTION_CONTROLLER, "preen");
        this.still = 80;
    }

    /** Leaves in front of it at head height (2 to 3 blocks up, scaled with the animal). */
    private boolean leavesInReach() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        for (int up = 2; up <= 3; up++) {
            BlockPos p = BlockPos.containing(this.getX() + look.x * 1.5D, this.getY() + up * this.getScale(), this.getZ() + look.z * 1.5D);
            if (this.level().getBlockState(p).is(BlockTags.LEAVES)) {
                return true;
            }
        }
        return false;
    }

    private Ornithomimid nearestFemale() {
        Ornithomimid best = null;
        double bestD = Double.MAX_VALUE;
        for (Ornithomimid e : this.level().getEntitiesOfClass(Ornithomimid.class, this.getBoundingBox().inflate(6.0D),
                o -> o != this && o.isAlive() && o.isFemale() && !o.isBaby() && !o.isSleeping() && o.getTarget() == null)) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }
}
