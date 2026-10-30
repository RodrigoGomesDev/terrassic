package com.terrassic.entity;

import com.terrassic.world.VanillaShare;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.MobType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.TryFindWaterGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Marine reptiles (and later the big fish). They live in the water like dolphins (smooth swimming, water-bound
 * navigation), breathe underwater, and dry out when stranded on land for too long. Hungry wild adults hunt sea
 * animals and anyone swimming or rowing near them; out of the water they only defend themselves.
 *
 * <p>Species that return true from {@link #tameable()} are tamed like the land animals (hand-feeding, or only as
 * babies for the live-bearing predators), follow their owner through the water without ever teleporting onto
 * land, rest in place when told to sit (they hover instead of sinking), and the rideable ones take a saddle:
 * the rider steers with the keys, dives and surfaces by looking down or up, and never drowns while mounted.
 * Live-bearers ({@link #liveYoung()}) spawn with the odd calf in the wild, which is how they are tamed.
 */
public abstract class SwimmingDinosaur extends DinosaurEntity {
    /** Ticks on land before it starts to dry out (then 1 damage every 2 s). */
    private static final int STRANDED_TICKS = 1200;
    /** Share of natural spawns of a live-bearing species that are calves. */
    private static final float CALF_CHANCE = 0.15F;

    private int strandedTicks;

    protected SwimmingDinosaur(EntityType<? extends SwimmingDinosaur> type, Level level) {
        super(type, level);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.02F, 0.1F, true);
        this.lookControl = new SmoothSwimmingLookControl(this, 10);
        this.setPathfindingMalus(BlockPathTypes.WATER, 0.0F);
    }

    /** Sea reptiles do not nest yet: the Archelon beaches and the live births at sea come with v0.8. */
    @Override
    protected boolean wildNests() {
        return false;
    }

    /** Favourite food (taming, healing). */
    protected abstract Ingredient food();

    /** What a wild adult hunts in the water. */
    protected abstract boolean isPrey(LivingEntity entity);

    /** Whether the species can be tamed at all (the untameable ones wait for knockout taming). */
    protected boolean tameable() {
        return false;
    }

    /** Whether the species gives birth to live young: some wild spawns are calves. */
    protected boolean liveYoung() {
        return false;
    }

    /** Vertical speed factor when the rider looks up or down. */
    protected double diveSpeed() {
        return 1.0D;
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new WaterBoundPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new TryFindWaterGoal(this));
        this.goalSelector.addGoal(1, new RestInWaterGoal(this));   // tame ones (hand-fed or knocked out) rest when told
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.3D, true));
        this.goalSelector.addGoal(3, new FollowOwnerSwimGoal(this, 1.2D, 10.0F, Math.max(3.0F, this.getBbWidth() * 1.5F)));
        if (this.tameable()) {
            this.goalSelector.addGoal(4, new TemptGoal(this, 1.1D, this.food(), false));
        }
        this.goalSelector.addGoal(5, new RandomSwimmingGoal(this, 1.0D, 30));
        this.goalSelector.addGoal(6, new RandomLookAroundGoal(this));
        // tame ones (hand-fed or knocked out) defend their owner
        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                e -> this.huntsPlayers() && this.canHunt() && (e.isInWaterOrBubble() || e.getVehicle() instanceof Boat)));
        this.targetSelector.addGoal(5, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 80, true, false,
                e -> this.canHunt() && e.isInWaterOrBubble() && this.isPrey(e)));
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return this.tameable() && this.food().test(stack);
    }

    @Override
    protected boolean canBeTamedNow() {
        return this.tameable() && super.canBeTamedNow();
    }

    @Override
    protected boolean koFood(ItemStack stack) {
        return this.food().test(stack);
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        if (!this.tameable() && !this.isTame() && !this.isKnockedOut()) {
            // wild: tamed only by knockout (docs/DOMESTICACAO.md)
            return InteractionResult.PASS;
        }
        return super.mobInteract(player, hand);
    }

    /** Whether wild adults attack players in the water (false for the peaceful grazers, which only fight back). */
    protected boolean huntsPlayers() {
        return true;
    }

    /** Only hunts while in the water; tamed ones only defend. */
    @Override
    protected boolean canHunt() {
        return super.canHunt() && this.isInWaterOrBubble();
    }

    @Override
    public MobType getMobType() {
        return MobType.WATER;
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
    }

    @Override
    public boolean isPushedByFluid() {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distanceToClosestPlayer) {
        // wild ones come and go like dolphins, so the oceans do not fill up with them; only out of sight (64+ blocks),
        // so the pods and schools the ecosystem keeps around the player do not blink out (docs/REGRAS.md)
        return !this.isTame() && !this.hasCustomName() && distanceToClosestPlayer > 64.0D * 64.0D;
    }

    @Override
    public int getMaxSpawnClusterSize() {
        return 1;
    }

    @Override
    public int getMaxHeadXRot() {
        return 1;
    }

    @Override
    public int getMaxHeadYRot() {
        return 1;
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        SpawnGroupData spawnData, CompoundTag tag) {
        SpawnGroupData data = super.finalizeSpawn(level, difficulty, reason, spawnData, tag);
        if (this.liveYoung() && reason == MobSpawnType.NATURAL && this.random.nextFloat() < CALF_CHANCE) {
            this.setAge(-24000);
        }
        return data;
    }

    // ------------------------------------------------------------------ swimming / ridden swimming

    @Override
    public void travel(Vec3 input) {
        if (this.isControlledByLocalInstance() && this.isInWater()) {
            this.moveRelative(this.getSpeed(), input);
            this.move(MoverType.SELF, this.getDeltaMovement());
            this.setDeltaMovement(this.getDeltaMovement().scale(0.9D));
            if (this.isInSittingPose() || this.isVehicle()) {
                // resting or ridden: hover, no slow sinking
                this.setDeltaMovement(this.getDeltaMovement().multiply(1.0D, 0.8D, 1.0D));
            } else if (this.getTarget() == null) {
                this.setDeltaMovement(this.getDeltaMovement().add(0.0D, -0.005D, 0.0D));
            }
            this.calculateEntityAnimation(false);
        } else {
            super.travel(input);
        }
    }

    @Override
    protected Vec3 getRiddenInput(Player player, Vec3 input) {
        Vec3 flat = super.getRiddenInput(player, input);
        if (!this.isInWater()) {
            return flat;
        }
        // look down to dive, up to surface; a little lift when idling so it does not sink under the rider
        double forward = Math.abs(flat.z);
        double dive = forward > 0.01D ? -Mth.sin(player.getXRot() * Mth.DEG_TO_RAD) * forward * this.diveSpeed() : 0.0D;
        return new Vec3(flat.x, dive, flat.z);
    }

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        super.tickRidden(player, input);
        if (this.isInWater()) {
            // in the water it always turns with the rider
            this.setRot(player.getYRot(), player.getXRot() * 0.5F);
            this.yRotO = this.getYRot();
            this.yBodyRot = this.getYRot();
            this.yHeadRot = this.getYRot();
            if (!this.level().isClientSide() && player.isUnderWater()) {
                // the mount keeps its rider breathing
                player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false, false));
            }
        }
    }

    @Override
    public boolean canJump() {
        return false;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.isInWaterOrBubble() || this.isInWaterRainOrBubble()) {
            this.strandedTicks = 0;
        } else if (++this.strandedTicks > STRANDED_TICKS && this.strandedTicks % 40 == 0) {
            this.hurt(this.damageSources().dryOut(), 1.0F);
        }
    }

    @Override
    public boolean checkSpawnObstruction(LevelReader level) {
        return level.isUnobstructed(this);
    }

    // ------------------------------------------------------------------ goals

    /** The vanilla sit goal refuses to work in water; this one lets a tamed swimmer rest in place when told to. */
    static class RestInWaterGoal extends Goal {
        private final SwimmingDinosaur mob;

        RestInWaterGoal(SwimmingDinosaur mob) {
            this.mob = mob;
            this.setFlags(EnumSet.of(Goal.Flag.JUMP, Goal.Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            return this.mob.isTame() && !this.mob.isVehicle() && this.mob.isOrderedToSit();
        }

        @Override
        public boolean canContinueToUse() {
            return this.canUse();
        }

        @Override
        public void start() {
            this.mob.getNavigation().stop();
            this.mob.setInSittingPose(true);
            this.mob.setTarget(null);
        }

        @Override
        public void stop() {
            this.mob.setInSittingPose(false);
        }
    }

    /**
     * Follows the owner through the water. Unlike the vanilla goal it never teleports (which would drop a marine
     * reptile onto the land next to its owner) and gives up while the owner is far from any water.
     */
    static class FollowOwnerSwimGoal extends Goal {
        private final SwimmingDinosaur mob;
        private final double speed;
        private final float start;
        private final float stop;
        private LivingEntity owner;
        private int recalc;

        FollowOwnerSwimGoal(SwimmingDinosaur mob, double speed, float start, float stop) {
            this.mob = mob;
            this.speed = speed;
            this.start = start;
            this.stop = stop;
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity o = this.mob.getOwner();
            if (o == null || o.isSpectator() || this.mob.isOrderedToSit() || this.mob.isWandering() || !this.mob.isInWater()
                    || this.mob.distanceToSqr(o) < (double) (this.start * this.start)) {
                return false;
            }
            this.owner = o;
            return true;
        }

        @Override
        public boolean canContinueToUse() {
            return !this.mob.getNavigation().isDone() && !this.mob.isOrderedToSit() && !this.mob.isWandering()
                    && this.mob.distanceToSqr(this.owner) > (double) (this.stop * this.stop);
        }

        @Override
        public void start() {
            this.recalc = 0;
        }

        @Override
        public void stop() {
            this.owner = null;
            this.mob.getNavigation().stop();
        }

        @Override
        public void tick() {
            this.mob.getLookControl().setLookAt(this.owner, 10.0F, (float) this.mob.getMaxHeadXRot());
            if (--this.recalc <= 0) {
                this.recalc = this.adjustedTickDelay(10);
                this.mob.getNavigation().moveTo(this.owner, this.speed);
            }
        }
    }

    // ------------------------------------------------------------------ spawning

    /** Spawn rule for open-sea reptiles: deep water (at least 6 blocks of it) well below the surface. */
    public static boolean checkSeaSpawnRules(EntityType<? extends DinosaurEntity> type, LevelAccessor level,
                                             MobSpawnType reason, BlockPos pos, RandomSource random) {
        int sea = level.getSeaLevel();
        if (pos.getY() > sea - 6 || pos.getY() < sea - 40) {
            return false;
        }
        for (int dy = -2; dy <= 3; dy++) {
            if (!level.getFluidState(pos.above(dy)).is(FluidTags.WATER)) {
                return false;
            }
        }
        return VanillaShare.allows(type, level, reason, pos);
    }
}
