package com.terrassic.entity;

import com.terrassic.entity.ai.BroodGoal;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
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
 *   <li>fleeing at full speed it jinks: a hard side-step away from a chaser close behind (the "jink"), now and
 *       then also with no one close;</li>
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
    /** The idle one-shot it is holding still for (cut short by a threat). */
    private String idleAction;

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
        // the jink: wild, running flat out, not ridden. A chaser close behind (a player it runs from, whoever hurt it,
        // a predator after it, within 7 blocks) draws one as soon as the cooldown allows; otherwise now and then. It
        // side-steps AWAY from the chaser's side, a little over a block (review 1.5: the old 0.35 push moved it
        // under a block, by chance only, and the Mac test never saw it)
        if (!this.isTame() && !this.isVehicle() && !this.isBaby() && this.jinkCooldown == 0 && this.onGround()
                && this.getDeltaMovement().horizontalDistanceSqr() > this.runThresholdSqr()) {
            LivingEntity chaser = this.chaser();
            if (chaser != null || this.random.nextInt(25) == 0) {
                Vec3 v = this.getDeltaMovement();
                Vec3 side = new Vec3(-v.z, 0.0D, v.x).normalize();
                double sign = this.random.nextBoolean() ? 1.0D : -1.0D;
                if (chaser != null) {
                    Vec3 toChaser = chaser.position().subtract(this.position());
                    sign = toChaser.dot(side) > 0.0D ? -1.0D : 1.0D;
                }
                this.setDeltaMovement(v.add(side.scale(sign * 0.6D)));
                this.hasImpulse = true;
                triggerAnim(ACTION_CONTROLLER, "jink");
                this.jinkCooldown = 40 + this.random.nextInt(30);
            }
        }
        // a threat cuts an idle pose short: a preening or watching animal must still run (review 1.5)
        if (this.still > 0 && (this.hurtTime > 0 || this.isFleeing())) {
            this.still = 0;
            if (this.idleAction != null) {
                stopTriggeredAnimation(ACTION_CONTROLLER, this.idleAction);
                this.idleAction = null;
            }
        }
        if (this.still > 0) {
            if (--this.still == 0) {
                this.idleAction = null;
            }
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
                this.hold("sentinel", 84);
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
            this.hold("sift", 80);
            return;
        }
        if (ground.is(BlockTags.SAND) || ground.is(Blocks.GRAVEL)) {
            this.hold("grit", 56);
            return;
        }
        if (this.leavesInReach()) {
            this.hold("browse", 70);
            this.feed(4);
            return;
        }
        if (!this.isTame() && !this.isFemale()) {
            Ornithomimid mate = this.nearestFemale();
            if (mate != null && this.random.nextInt(3) == 0) {
                this.getLookControl().setLookAt(mate, 30.0F, 30.0F);
                mate.getLookControl().setLookAt(this, 30.0F, 30.0F);
                this.hold("wing_display", 96);
                mate.still = 60;
                return;
            }
        }
        this.hold("preen", 80);
    }

    private void hold(String action, int ticks) {
        triggerAnim(ACTION_CONTROLLER, action);
        this.idleAction = action;
        this.still = ticks;
    }

    /** Running from something: the flee or the panic goal is on. */
    private boolean isFleeing() {
        return this.goalSelector.getRunningGoals().anyMatch(g -> g.getGoal() instanceof AvoidEntityGoal<?> || g.getGoal() instanceof PanicGoal);
    }

    /** Who is close behind it, if anyone: whoever hurt it lately, a player it runs from, a wild predator hunting it. */
    private LivingEntity chaser() {
        LivingEntity hurtBy = this.getLastHurtByMob();
        if (hurtBy != null && hurtBy.isAlive() && this.tickCount - this.getLastHurtByMobTimestamp() < 200 && hurtBy.distanceToSqr(this) < 49.0D) {
            return hurtBy;
        }
        Player p = this.level().getNearestPlayer(this, 7.0D);
        if (p != null && !p.isSpectator() && !p.isCreative() && this.fleesFrom(p)) {
            return p;
        }
        List<PredatorDinosaur> hunters = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(7.0D),
                h -> h.isAlive() && h.getTarget() == this);
        return hunters.isEmpty() ? null : hunters.get(0);
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
