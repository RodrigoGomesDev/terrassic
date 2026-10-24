package com.terrassic.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.MobType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.TryFindWaterGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.phys.Vec3;

/**
 * Marine reptiles. They live in the water like dolphins (smooth swimming, water-bound navigation), breathe
 * underwater, and dry out when stranded on land for too long. Wild only for now: they cannot be tamed or bred
 * (the aquatic mount and saddle come in a later version). Hungry adults hunt sea animals and anyone swimming or
 * rowing near them; out of the water they only defend themselves.
 */
public abstract class SwimmingDinosaur extends DinosaurEntity {
    /** Ticks on land before it starts to dry out (then 1 damage every 2 s). */
    private static final int STRANDED_TICKS = 1200;

    private int strandedTicks;

    protected SwimmingDinosaur(EntityType<? extends SwimmingDinosaur> type, Level level) {
        super(type, level);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.02F, 0.1F, true);
        this.lookControl = new SmoothSwimmingLookControl(this, 10);
        this.setPathfindingMalus(BlockPathTypes.WATER, 0.0F);
    }

    /** Favourite food. Unused while the species is wild only; kept for the future taming. */
    protected abstract Ingredient food();

    /** What a wild adult hunts in the water. */
    protected abstract boolean isPrey(LivingEntity entity);

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new WaterBoundPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new TryFindWaterGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.3D, true));
        this.goalSelector.addGoal(5, new RandomSwimmingGoal(this, 1.0D, 30));
        this.goalSelector.addGoal(6, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                e -> this.canHunt() && (e.isInWaterOrBubble() || e.getVehicle() instanceof Boat)));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 80, true, false,
                e -> this.canHunt() && e.isInWaterOrBubble() && this.isPrey(e)));
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return false;
    }

    @Override
    protected boolean canBeTamedNow() {
        return false;
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        // wild only: no feeding, sitting or riding yet
        return InteractionResult.PASS;
    }

    /** Only hunts while in the water. */
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
        // wild ones come and go like dolphins, so the oceans do not fill up with them
        return !this.isTame() && !this.hasCustomName();
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
    public void travel(Vec3 input) {
        if (this.isControlledByLocalInstance() && this.isInWater()) {
            this.moveRelative(this.getSpeed(), input);
            this.move(MoverType.SELF, this.getDeltaMovement());
            this.setDeltaMovement(this.getDeltaMovement().scale(0.9D));
            if (this.getTarget() == null) {
                this.setDeltaMovement(this.getDeltaMovement().add(0.0D, -0.005D, 0.0D));
            }
            this.calculateEntityAnimation(false);
        } else {
            super.travel(input);
        }
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
        return true;
    }
}
