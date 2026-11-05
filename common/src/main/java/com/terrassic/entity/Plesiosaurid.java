package com.terrassic.entity;

import java.util.EnumSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The hand-made Elasmosaurus rig (tools/modelgen/handmade/elasmosaurus, its own study, page "Elasmossauro: estudo para
 * a 1.8", and 21 animations). What it adds over a plain {@link SwimmingDinosaur}:
 * <ul>
 *   <li>its own gaits: it hovers ("idle"), flies under water on its four flippers ("swim"), strokes and glides
 *       ("walk") and bursts ("run"); on land it lies helpless ("stranded");</li>
 *   <li>every bite is the strike of the long neck ("neck_strike", the attack animation);</li>
 *   <li>it breathes air: every two or three minutes it rises until only the top of its head is out ("breathe"), then
 *       dives nose first ("dive");</li>
 *   <li>near the bottom, idle, it now and then swallows stones ("gastrolith"); a calf near an adult of its kind
 *       touches snouts with it ("nuzzle"); two in love swim together (BreedGoal).</li>
 * </ul>
 * Its own neck saddle is the only saddle it takes (gen_species).
 */
public abstract class Plesiosaurid extends SwimmingDinosaur {
    private RawAnimation idleA;
    private RawAnimation swimA;
    private RawAnimation walkA;
    private RawAnimation runA;
    private RawAnimation strandedA;
    private RawAnimation sitA;
    private RawAnimation sleepA;
    private int breathTimer;

    protected Plesiosaurid(EntityType<? extends Plesiosaurid> type, Level level) {
        super(type, level);
        this.breathTimer = 300 + level.getRandom().nextInt(600);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"neck_strike", "breathe", "dive", "gastrolith", "nuzzle"};
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
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.idleA == null) {
            this.idleA = RawAnimation.begin().thenLoop(anim("idle"));
            this.swimA = RawAnimation.begin().thenLoop(anim("swim"));
            this.walkA = RawAnimation.begin().thenLoop(anim("walk"));
            this.runA = RawAnimation.begin().thenLoop(anim("run"));
            this.strandedA = RawAnimation.begin().thenLoop(anim("stranded"));
            this.sitA = RawAnimation.begin().thenLoop(anim("sit"));
            this.sleepA = RawAnimation.begin().thenLoop(anim("sleep"));
        }
        if (this.isSleeping()) {
            return state.setAndContinue(this.sleepA);
        }
        if (!this.isInWater()) {
            return state.setAndContinue(this.strandedA);
        }
        if (this.isInSittingPose() && !this.isVehicle()) {
            return state.setAndContinue(this.sitA);
        }
        if (state.isMoving()) {
            double v = this.getDeltaMovement().lengthSqr();
            if (this.isAggressive() || v > 0.09D) {
                return state.setAndContinue(this.runA);
            }
            return state.setAndContinue(v < 0.012D ? this.walkA : this.swimA);
        }
        return state.setAndContinue(this.idleA);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(3, new BreatheGoal());
        this.goalSelector.addGoal(2, new com.terrassic.entity.ai.DinoBreedGoal(this, 1.0D));
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit) {
            triggerAnim(ACTION_CONTROLLER, "neck_strike");
        }
        return hit;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.breathTimer > 0) {
            this.breathTimer--;
        }
        if (!this.isInWater() || this.getTarget() != null || this.isVehicle() || this.isOrderedToSit() || this.isSleeping()
                || this.isKnockedOut() || !this.getNavigation().isDone()) {
            return;
        }
        if (this.isBaby()) {
            if (this.random.nextInt(400) == 0) {
                for (Plesiosaurid o : this.level().getEntitiesOfClass(Plesiosaurid.class, this.getBoundingBox().inflate(6.0D),
                        c -> c != this && !c.isBaby() && c.getType() == this.getType())) {
                    this.getLookControl().setLookAt(o, 30.0F, 30.0F);
                    triggerAnim(ACTION_CONTROLLER, "nuzzle");
                    o.getLookControl().setLookAt(this, 30.0F, 30.0F);
                    o.triggerAnim(ACTION_CONTROLLER, "nuzzle");
                    break;
                }
            }
            return;
        }
        // near the bottom: now and then it swallows stones
        if (this.random.nextInt(900) == 0 && !this.level().getFluidState(this.blockPosition().below(2)).is(FluidTags.WATER)) {
            triggerAnim(ACTION_CONTROLLER, "gastrolith");
        }
    }

    private Vec3 forward() {
        float yaw = this.getYRot() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(yaw), 0.0D, Mth.cos(yaw));
    }

    /** The y of the first air over the water above it (40 blocks at most), or NaN under a roof. */
    private double surfaceAbove() {
        BlockPos.MutableBlockPos p = this.blockPosition().mutable();
        for (int dy = 0; dy < 40; dy++) {
            p.setY(this.blockPosition().getY() + dy);
            if (!this.level().getFluidState(p).is(FluidTags.WATER)) {
                return this.level().getBlockState(p).isAir() ? p.getY() : Double.NaN;
            }
        }
        return Double.NaN;
    }

    /** Up for air every two or three minutes: only the top of the head out, a breath, then it dives. */
    class BreatheGoal extends Goal {
        private int ticks;
        private int held;
        private double surface;

        BreatheGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            Plesiosaurid m = Plesiosaurid.this;
            if (m.breathTimer > 0 || !m.isInWater() || m.getTarget() != null || m.isVehicle() || m.isOrderedToSit()
                    || m.isKnockedOut() || m.isSleeping()) {
                return false;
            }
            this.surface = m.surfaceAbove();
            if (Double.isNaN(this.surface)) {
                m.breathTimer = 600;
                return false;
            }
            return true;
        }

        @Override
        public boolean canContinueToUse() {
            return this.ticks < 240 && this.held < 70 && Plesiosaurid.this.getTarget() == null && !Plesiosaurid.this.isVehicle();
        }

        @Override
        public void start() {
            this.ticks = 0;
            this.held = 0;
        }

        @Override
        public void stop() {
            Plesiosaurid m = Plesiosaurid.this;
            m.breathTimer = 1800 + m.random.nextInt(1800);
            if (this.held > 0) {
                m.triggerAnim(ACTION_CONTROLLER, "dive");
            }
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            Plesiosaurid m = Plesiosaurid.this;
            this.ticks++;
            double top = m.getY() + m.getBbHeight();
            if (this.held == 0 && top < this.surface - 0.3D) {
                Vec3 f = m.forward();
                m.getMoveControl().setWantedPosition(m.getX() + f.x * 3.0D, this.surface - m.getBbHeight() * 0.8D,
                        m.getZ() + f.z * 3.0D, 0.8D);
                return;
            }
            if (this.held == 0) {
                m.getNavigation().stop();
                m.triggerAnim(ACTION_CONTROLLER, "breathe");
            }
            this.held++;
            m.setDeltaMovement(m.getDeltaMovement().multiply(0.5D, 0.0D, 0.5D));
            if (this.held == 24 && m.level() instanceof ServerLevel server) {
                Vec3 n = m.position().add(m.forward().scale(7.0D * m.getScale())).add(0.0D, m.getBbHeight(), 0.0D);
                server.sendParticles(ParticleTypes.BUBBLE_POP, n.x, n.y, n.z, 8, 0.3D, 0.1D, 0.3D, 0.05D);
            }
        }
    }
}
