package com.terrassic.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PlayerRideableJumping;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowOwnerGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomFlyingGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.animal.FlyingAnimal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * Pterosaurs. Wild ones fly around with a flying navigation (like parrots), glide down slowly when they stop
 * flapping and never take fall damage. They are tamed by hand-feeding (fish) and, once saddled, can be flown:
 *
 * <ul>
 *   <li>on the ground it walks like any mount; <b>jump</b> (hold for a stronger leap) takes off, and so does
 *       pushing forward while looking up steeply;</li>
 *   <li>in the air it flies where the rider looks while forward is held; <b>jump</b> flaps for height;</li>
 *   <li>with forward released it glides, keeping its speed and slowly sinking, and lands by touching ground.</li>
 * </ul>
 *
 * Animations: besides the usual ones the model needs "fly" (flapping) and "glide" (wings held open).
 * Ridden movement runs on the rider's client (vanilla vehicles do), so the flying state is derived from
 * {@code onGround()} instead of being synced.
 */
public abstract class FlyingDinosaur extends DinosaurEntity implements FlyingAnimal, PlayerRideableJumping {
    /** Ridden flight: acceleration along the look direction per tick at FLYING_SPEED 0.6, and air drag. */
    private static final double FLIGHT_ACCEL = 0.045D;
    private static final double FLIGHT_DRAG = 0.95D;
    private static final double GLIDE_DRAG = 0.985D;
    private static final double GLIDE_SINK = 0.02D;
    private static final double MAX_SINK = 0.45D;
    /** Rider pitch (degrees, negative = up) above which pushing forward on the ground takes off. */
    private static final float TAKE_OFF_PITCH = -30.0F;

    private RawAnimation flyAnim;
    private RawAnimation glideAnim;
    /** Pending jump from the rider (0..1), consumed by the next ridden travel tick. */
    private float pendingJump;
    /** Ticks since the last flap, for the fly/glide animation choice. */
    private int flapTicks;

    protected FlyingDinosaur(EntityType<? extends FlyingDinosaur> type, Level level) {
        super(type, level);
        this.moveControl = new FlyingMoveControl(this, 20, false);
    }

    /** Breeding / taming food. Must return a static constant (used during construction). */
    protected abstract Ingredient food();

    /** What a wild adult hunts (fish for the Pteranodon). */
    protected abstract boolean isPrey(LivingEntity entity);

    @Override
    protected PathNavigation createNavigation(Level level) {
        FlyingPathNavigation nav = new FlyingPathNavigation(this, level);
        nav.setCanOpenDoors(false);
        nav.setCanFloat(true);
        nav.setCanPassDoors(true);
        return nav;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.2D, true));
        this.goalSelector.addGoal(4, new FollowOwnerGoal(this, 1.2D, 10.0F, 3.0F, true));
        this.goalSelector.addGoal(5, new BreedGoal(this, 1.0D));
        this.goalSelector.addGoal(6, new TemptGoal(this, 1.1D, food(), false));
        this.goalSelector.addGoal(7, new FollowParentGoal(this, 1.1D));
        this.goalSelector.addGoal(8, new WaterAvoidingRandomFlyingGoal(this, 1.0D));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 16.0F));
        this.goalSelector.addGoal(10, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(5, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 100, true, false,
                e -> this.canHunt() && this.isPrey(e)));
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return food().test(stack);
    }

    @Override
    public boolean isFlying() {
        return !this.onGround() && !this.isInWater();
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {
    }

    @Override
    public void aiStep() {
        super.aiStep();
        // unridden: fall slowly with the wings open, like a parrot
        Vec3 v = this.getDeltaMovement();
        if (!this.isVehicle() && !this.onGround() && v.y < 0.0D) {
            this.setDeltaMovement(v.multiply(1.0D, 0.6D, 1.0D));
        }
        if (this.flapTicks < 100) {
            this.flapTicks++;
        }
    }

    // ------------------------------------------------------------------ animation

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.flyAnim == null) {
            this.flyAnim = RawAnimation.begin().thenLoop(anim("fly"));
            this.glideAnim = RawAnimation.begin().thenLoop(anim("glide"));
        }
        if (this.isFlying() && !this.isPassenger()) {
            Vec3 v = this.getDeltaMovement();
            boolean gliding = v.y < -0.03D && this.flapTicks > 15 && v.horizontalDistanceSqr() > 0.01D;
            return state.setAndContinue(gliding ? this.glideAnim : this.flyAnim);
        }
        return super.movementAnimation(state);
    }

    // ------------------------------------------------------------------ ridden flight

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        super.tickRidden(player, input);
        this.setNoGravity(false);
        if (this.isFlying()) {
            // in the air it always turns with the rider, even when gliding with no keys pressed
            this.setRot(player.getYRot(), player.getXRot() * 0.5F);
            this.yRotO = this.getYRot();
            this.yBodyRot = this.getYRot();
            this.yHeadRot = this.getYRot();
        }
    }

    @Override
    public void travel(Vec3 input) {
        if (!(this.isVehicle() && this.getControllingPassenger() instanceof Player rider)) {
            super.travel(input);
            return;
        }
        if (!this.isControlledByLocalInstance()) {
            // the rider's client moves us; the server only keeps the last motion
            this.setDeltaMovement(Vec3.ZERO);
            return;
        }
        boolean takeOff = this.onGround() && (this.pendingJump > 0.0F || (input.z > 0.0D && rider.getXRot() < TAKE_OFF_PITCH));
        if (takeOff) {
            float power = Math.max(this.pendingJump, 0.5F);
            Vec3 v = this.getDeltaMovement();
            this.setDeltaMovement(v.x, 0.55D + 0.5D * power, v.z);
            this.pendingJump = 0.0F;
            this.flapTicks = 0;
            this.hasImpulse = true;
        }
        if (!this.isFlying() && !takeOff) {
            this.pendingJump = 0.0F;
            super.travel(input);
            return;
        }
        Vec3 v = this.getDeltaMovement();
        if (this.pendingJump > 0.0F) {
            v = new Vec3(v.x, Math.max(v.y, 0.0D) + 0.25D + 0.35D * this.pendingJump, v.z);
            this.pendingJump = 0.0F;
            this.flapTicks = 0;
        }
        double drag;
        if (input.z > 0.0D) {
            double accel = FLIGHT_ACCEL * this.getAttributeValue(Attributes.FLYING_SPEED) / 0.6D * this.riddenSpeedFactor();
            Vec3 look = Vec3.directionFromRotation(rider.getXRot(), this.getYRot());
            v = v.add(look.scale(accel * input.z));
            if (look.y > 0.0D) {
                this.flapTicks = 0;
            }
            drag = FLIGHT_DRAG;
        } else {
            v = v.add(0.0D, -GLIDE_SINK, 0.0D);
            drag = GLIDE_DRAG;
        }
        if (input.x != 0.0D) {
            // sideways keys bank a little
            float yaw = this.getYRot() * Mth.DEG_TO_RAD;
            v = v.add(Mth.cos(yaw) * input.x * 0.02D, 0.0D, Mth.sin(yaw) * input.x * 0.02D);
        }
        v = new Vec3(v.x * drag, Math.max(v.y * drag, -MAX_SINK), v.z * drag);
        this.move(MoverType.SELF, v);
        this.setDeltaMovement(v);
        this.calculateEntityAnimation(true);
        this.tryCheckInsideBlocks();
    }

    @Override
    protected Vec3 getRiddenInput(Player player, Vec3 input) {
        if (this.isFlying()) {
            return new Vec3(player.xxa, 0.0D, Math.max(player.zza, 0.0F));
        }
        return super.getRiddenInput(player, input);
    }

    @Override
    public void onPlayerJump(int power) {
        if (!this.isSaddled()) {
            return;
        }
        this.pendingJump = power <= 0 ? 0.4F : power >= 90 ? 1.0F : 0.4F + 0.6F * power / 90.0F;
    }

    @Override
    public boolean canJump() {
        return this.isSaddled();
    }

    @Override
    public void handleStartJump(int power) {
        this.flapTicks = 0;
    }

    @Override
    public void handleStopJump() {
    }

    // ------------------------------------------------------------------ spawning

    /** Spawn rule for coast flyers: sand, gravel, stone or grass, in daylight. */
    public static boolean checkFlyerSpawnRules(EntityType<? extends DinosaurEntity> type, LevelAccessor level,
                                               MobSpawnType reason, BlockPos pos, RandomSource random) {
        BlockState below = level.getBlockState(pos.below());
        boolean ground = below.is(BlockTags.SAND) || below.is(Blocks.GRAVEL) || below.is(BlockTags.BASE_STONE_OVERWORLD)
                || below.is(BlockTags.ANIMALS_SPAWNABLE_ON);
        return ground && level.getRawBrightness(pos, 0) > 8;
    }
}
