package com.terrassic.entity;

import com.terrassic.entity.ai.ColonyGoal;
import com.terrassic.entity.ai.FishingFlightGoal;
import com.terrassic.entity.ai.SoarGoal;
import com.terrassic.entity.ai.FlightSteering;
import com.terrassic.entity.ai.SoaringMoveControl;
import com.terrassic.entity.ai.OrderedFollowOwnerGoal;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.tags.BlockTags;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
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
import net.minecraft.world.level.levelgen.Heightmap;
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
 *   <li>in the air it flies where the rider looks while forward is held, turning at its own pace towards the
 *       rider's view (it carves the turn instead of snapping round); <b>jump</b> flaps for height;</li>
 *   <li>diving trades height for speed, climbing costs speed;</li>
 *   <li>with forward released it glides, keeping its speed and slowly sinking, and lands by touching ground;</li>
 *   <li>in the air <b>sneak</b> brings it down like the descend key instead of dropping the rider off
 *       (mixin/PlayerMixin); on the ground sneak gets off as usual.</li>
 * </ul>
 * Species that {@link #tiltsInFlight()} also pitch the whole body up and down with the flight path and bank into turns
 * ({@link #flightPitch(float)}, {@link #flightRoll(float)}, drawn by client/DinosaurRenderer about the saddle).
 *
 * Animations: besides the usual ones the model needs "fly" (flapping) and "glide" (wings held open).
 * Ridden movement runs on the rider's client (vanilla vehicles do), so the flying state is derived from
 * {@code onGround()} instead of being synced.
 *
 * <p>Wild adults soar high over the land in flocks for a few minutes at a time, then glide down and rest
 * ({@link SoarGoal}); the ecosystem spawner places new flocks already in the air (docs/REGRAS.md).
 */
public abstract class FlyingDinosaur extends DinosaurEntity implements FlyingAnimal {
    /**
     * The rider holds the descend key (client/DinoControls, v0.12). Set on the rider's side only, which is the side that
     * moves a ridden flyer; the server never reads it.
     */
    public boolean riderDescending;

    /** Ridden flight: acceleration along the look direction per tick at FLYING_SPEED 0.6, and air drag. */
    private static final double FLIGHT_ACCEL = 0.045D;
    private static final double FLIGHT_DRAG = 0.95D;
    private static final double GLIDE_DRAG = 0.985D;
    private static final double GLIDE_SINK = 0.02D;
    private static final double MAX_SINK = 0.45D;
    /** Ridden, a steep dive with forward held: the sink limit, and the lighter drag that lets it build speed. */
    private static final double DIVE_SINK = 0.7D;
    private static final double DIVE_DRAG = 0.97D;
    /** Ridden in the air: how fast it turns towards the rider's view, degrees per tick. */
    private static final float MAX_TURN = 7.0F;
    /** Body tilt in flight (degrees): nose up climbing, nose down diving, and the bank into a turn per degree of turn
     *  (a rig's own bank animations, Pterosaur "bank_left"/"bank_right", roll the body further on top). */
    private static final float MAX_CLIMB_PITCH = 50.0F;
    private static final float MAX_DIVE_PITCH = 60.0F;
    private static final float MAX_ROLL = 20.0F;
    private static final float ROLL_PER_TURN = 3.0F;
    /** Ridden, the descend key held (v0.12): extra sink per tick. */
    private static final double DESCEND = 0.07D;
    /** Rider pitch (degrees, negative = up) above which pushing forward on the ground takes off. */
    private static final float TAKE_OFF_PITCH = -30.0F;

    private RawAnimation flyAnim;
    private RawAnimation glideAnim;
    /** Pending jump from the rider (0..1), consumed by the next ridden travel tick. */
    private float pendingJump;
    /** Ticks since the last flap, for the fly/glide animation choice. */
    private int flapTicks;
    /** Ticks left of the current soaring flight (0 = not soaring), and of the rest after it (SoarGoal). */
    private int soarTicks;
    private int restTicks;
    /** Where the soaring flight heads now, and where the animal first took off (it does not stray far from it). */
    private Vec3 soarTarget;
    private Vec3 soarHome;
    private boolean cruising;
    /** The coastal colony a colonial wild flyer belongs to (world/PteroColonies), or null. */
    private BlockPos colonyHome;
    /** A fishing sortie a colony mate asked this one to join: where over the sea (FishingFlightGoal). */
    private Vec3 sortieCall;
    // client: the body tilt in flight (tiltsInFlight), eased, with last tick's value for the frame in between
    private float tiltPitch;
    private float tiltPitchO;
    private float tiltRoll;
    private float tiltRollO;

    protected FlyingDinosaur(EntityType<? extends FlyingDinosaur> type, Level level) {
        super(type, level);
        this.moveControl = new SoaringMoveControl(this);
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

    /** Hook for extra goals (avoid, flee...). Called at the end of {@link #registerGoals()}. */
    protected void addExtraGoals() {
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.2D, true));
        this.goalSelector.addGoal(4, new OrderedFollowOwnerGoal(this, 1.2D, 10.0F, 3.0F, true));
        this.goalSelector.addGoal(5, new BreedGoal(this, 1.0D));
        this.goalSelector.addGoal(6, new TemptGoal(this, 1.1D, food(), false));
        this.goalSelector.addGoal(7, new FollowParentGoal(this, 1.1D));
        if (this.colonial()) {
            this.goalSelector.addGoal(7, new FishingFlightGoal(this));
        }
        this.goalSelector.addGoal(8, new SoarGoal(this));
        if (this.colonial()) {
            this.goalSelector.addGoal(9, new ColonyGoal(this));
        }
        this.goalSelector.addGoal(9, new WaterAvoidingRandomFlyingGoal(this, 1.0D) {
            @Override
            public boolean canUse() {
                return allowed() && super.canUse();
            }

            @Override
            public boolean canContinueToUse() {
                return allowed() && super.canContinueToUse();
            }

            private boolean allowed() {
                return !FlyingDinosaur.this.isResting() && !FlyingDinosaur.this.isKnockedOut() && !FlyingDinosaur.this.isColonist()
                        && (FlyingDinosaur.this.isTame() || FlyingDinosaur.this.isBaby() || !FlyingDinosaur.this.isSleepTime());
            }
        });
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Player.class, 16.0F));
        this.goalSelector.addGoal(11, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(5, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 100, true, false,
                e -> this.canHunt() && this.isPrey(e)));
        addExtraGoals();
    }

    /** 0 on the ground, 1 in the air, eased over about half a second: how far the seat has risen (see {@link #seatLift()}). */
    private float airSeat;

    /** How much higher the saddle sits in flight than on the ground, in blocks at size 1 (gen_species "ride_air_lift").
     *  The Pteranodon's flight poses lift its body 14 px above the standing pose: with the ground seat the body
     *  closed over the rider in the air. */
    protected double airSeatLift() {
        return 0.0D;
    }

    @Override
    public void tick() {
        super.tick();
        this.airSeat += ((this.isAirborne() ? 1.0F : 0.0F) - this.airSeat) * 0.2F;
        if (this.level().isClientSide() && this.tiltsInFlight()) {
            this.tiltTick();
        }
    }

    // ------------------------------------------------------------------ body tilt in flight (client)

    /** Whether the whole body pitches with the flight path and banks into turns (a rig made for it: the Pterosaur). */
    protected boolean tiltsInFlight() {
        return false;
    }

    /** How much of the path's pitch the body takes now (less while an animation of its own lifts it off). */
    protected float tiltWeight() {
        return 1.0F;
    }

    /** Body pitch in flight, degrees, nose up positive. */
    public float flightPitch(float partialTick) {
        return Mth.lerp(partialTick, this.tiltPitchO, this.tiltPitch);
    }

    /** Body roll in flight, degrees, positive = left wing down (turning left). */
    public float flightRoll(float partialTick) {
        return Mth.lerp(partialTick, this.tiltRollO, this.tiltRoll);
    }

    /** Where the tilt turns about: the saddle, near the wing roots, so a rider stays in the seat. Blocks, from the feet. */
    public double tiltPivotForward() {
        return this.riderForwardOffset() * this.getScale();
    }

    public double tiltPivotHeight() {
        return this.getPassengersRidingOffset() + this.seatLift();
    }

    /** From how it actually moved this tick (the client knows the motion of other players' mounts and of wild ones only
     *  from their positions). */
    private void tiltTick() {
        this.tiltPitchO = this.tiltPitch;
        this.tiltRollO = this.tiltRoll;
        float turn = Mth.wrapDegrees(this.getYRot() - this.yRotO);
        float pitch = 0.0F;
        float roll = 0.0F;
        if (this.isAirborne() && !this.isKnockedOut() && this.isAlive()) {
            double dy = this.getY() - this.yo;
            double dh = Math.sqrt(Mth.square(this.getX() - this.xo) + Mth.square(this.getZ() - this.zo));
            // it points where it goes: nose up in a climb (even flapping straight up), down in a dive, level hovering
            pitch = (float) (Mth.atan2(dy, Math.max(dh, 0.15D)) * Mth.RAD_TO_DEG);
            pitch = Mth.clamp(pitch, -MAX_DIVE_PITCH, MAX_CLIMB_PITCH) * this.tiltWeight();
            roll = Mth.clamp(-turn * ROLL_PER_TURN, -MAX_ROLL, MAX_ROLL);
        }
        this.tiltPitch += (pitch - this.tiltPitch) * 0.2F;
        this.tiltRoll += (roll - this.tiltRoll) * 0.25F;
    }

    /** The head's own pitch on top of the body's: none for a body that already tilts. */
    private float headPitch(float pitch) {
        return this.tiltsInFlight() ? 0.0F : pitch;
    }

    @Override
    protected double seatLift() {
        return this.airSeat * this.airSeatLift() * this.getScale();
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return food().test(stack);
    }

    @Override
    public boolean isFlying() {
        return !this.onGround() && !this.isInWater() && !this.isPassenger();
    }

    /** In the air for the animations. The client learns onGround only from movement packets, so an animal standing
     *  still since it was loaded would read as flying: there it also needs nothing solid just under its feet. */
    public boolean isAirborne() {
        return this.isFlying() && (!this.level().isClientSide()
                || this.level().noCollision(this, this.getBoundingBox().move(0.0D, -0.25D, 0.0D)));
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
        // Immobilized mobs can skip goal/controller updates: release lift before vanilla applies physics.
        if (!this.level().isClientSide() && this.isKnockedOut()) {
            if (this.cruising) this.endSoar();
            this.setNoGravity(false);
        }
        super.aiStep();
        // unridden: fall slowly with the wings open, like a parrot
        Vec3 v = this.getDeltaMovement();
        if (!this.isVehicle() && !this.isCruising() && !this.isResting() && !this.isKnockedOut() && !this.onGround() && v.y < 0.0D) {
            this.setDeltaMovement(v.multiply(1.0D, 0.6D, 1.0D));
        }
        if (this.flapTicks < 100) {
            this.flapTicks++;
        }
        if (!this.level().isClientSide()) {
            this.soarTick();
        }
        // wing beats while flapping (not while gliding), about once per cycle of the fly animation
        SoundEvent flap = this.flapSound();
        if (flap != null && !this.level().isClientSide() && this.isFlying() && this.tickCount % 16 == 0
                && (this.flapTicks < 15 || this.getDeltaMovement().y > -0.03D)) {
            this.playSound(flap, 0.8F, 0.9F + this.random.nextFloat() * 0.2F);
        }
    }

    // ------------------------------------------------------------------ colonies (world/PteroColonies)

    /** A colonial species lives in coastal colonies: it roosts there and leaves in small parties to fish over the sea
     *  (ai/FishingFlightGoal, ai/ColonyGoal) instead of soaring in flocks over the land (SoarGoal). */
    protected boolean colonial() {
        return false;
    }

    public boolean isColonial() {
        return this.colonial();
    }

    /** A wild one that belongs to a colony (tamed ones follow their owner instead). */
    public boolean isColonist() {
        return this.colonyHome != null && !this.isTame();
    }

    public BlockPos getColonyHome() {
        return this.colonyHome;
    }

    public void setColonyHome(BlockPos home) {
        this.colonyHome = home;
    }

    public Vec3 takeSortieCall() {
        Vec3 call = this.sortieCall;
        this.sortieCall = null;
        return call;
    }

    public boolean hasSortieCall() {
        return this.sortieCall != null;
    }

    public void callToSortie(Vec3 sea) {
        this.sortieCall = sea;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (this.colonyHome != null) {
            tag.put("Colony", NbtUtils.writeBlockPos(this.colonyHome));
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.colonyHome = tag.contains("Colony") ? NbtUtils.readBlockPos(tag.getCompound("Colony")) : null;
    }

    // ------------------------------------------------------------------ soaring (SoarGoal)

    public boolean isSoaring() {
        return this.soarTicks > 0;
    }

    /** True only while SoarGoal actually owns movement, never during combat, riding or torpor. */
    public boolean isCruising() {
        return this.cruising && !this.isKnockedOut() && !this.isVehicle() && !this.isPassenger();
    }

    public void setCruising(boolean cruising) {
        this.cruising = cruising;
        if (!cruising) {
            this.setNoGravity(false);
        }
    }

    public boolean isResting() {
        return this.restTicks > 0;
    }

    public int soarTicksLeft() {
        return this.soarTicks;
    }

    /** Starts a soaring flight of one to three minutes. */
    public void beginSoar() {
        this.soarTicks = 1200 + this.random.nextInt(2400);
        if (this.soarHome == null) {
            this.soarHome = this.position();
        }
    }

    /** Placed in mid-air by the ecosystem spawner: already soaring, gliding along the flock's heading. */
    public void startSoaring(Vec3 heading) {
        this.beginSoar();
        this.soarTicks += 1200;
        this.soarHome = this.position();
        this.setDeltaMovement(heading.normalize().scale(0.35D));
        this.soarTarget = this.position().add(heading.normalize().scale(40.0D));
    }

    /** The flight is over: glide down and rest for half a minute to a minute and a half. */
    public void endSoar() {
        this.setCruising(false);
        this.soarTicks = 0;
        this.restTicks = 600 + this.random.nextInt(1200);
        this.soarTarget = null;
    }

    public Vec3 getSoarTarget() {
        return this.soarTarget;
    }

    public void setSoarTarget(Vec3 target) {
        this.soarTarget = target;
    }

    public Vec3 getSoarHome() {
        return this.soarHome;
    }

    private void soarTick() {
        if (this.soarTicks > 0) {
            // never come down over open water: keep flying until there is land below
            if (this.soarTicks == 1 && !this.level().getFluidState(
                    this.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING, this.blockPosition()).below()).isEmpty()) {
                this.soarTicks += 200;
            }
            this.soarTicks--;
        } else if (this.restTicks > 0) {
            this.restTicks--;
        }
    }

    /** A one-shot of a fishing flight ("dive" down at the water, "scoop" along the surface), for rigs that have them
     *  ({@link Pterosaur}); nothing by default. */
    public void flightAction(String name) {
    }

    /** Wing beat sound, or null for none. */
    protected SoundEvent flapSound() {
        return null;
    }

    // ------------------------------------------------------------------ animation

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.flyAnim == null) {
            this.flyAnim = RawAnimation.begin().thenLoop(anim("fly"));
            this.glideAnim = RawAnimation.begin().thenLoop(anim("glide"));
        }
        if (this.isAirborne()) {
            Vec3 v = this.getDeltaMovement();
            // Level cruising also alternates wing beats and gliding; phase differs between animals.
            boolean gliding = v.y < 0.035D && v.horizontalDistanceSqr() > 0.04D
                    && (this.tickCount + this.getId() * 7) % 100 > 30;
            return state.setAndContinue(gliding ? this.glideAnim : this.flyAnim);
        }
        return super.movementAnimation(state);
    }

    // ------------------------------------------------------------------ ridden flight

    /** The rider got off in the air: gravity back (the slow parrot fall of aiStep takes over), unless it is soaring. */
    @Override
    protected void removePassenger(net.minecraft.world.entity.Entity passenger) {
        super.removePassenger(passenger);
        if (!this.isVehicle() && !this.cruising) {
            this.setNoGravity(false);
        }
    }

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        float yaw = this.getYRot();
        super.tickRidden(player, input);
        // ridden flight moves itself (travel below); without NoGravity a server with allow-flight=false (the default)
        // kicks the rider "for floating a vehicle too long" after 4 s in the air (v0.12 test)
        this.setNoGravity(this.isFlying());
        if (this.isFlying()) {
            // in the air it always turns towards the rider's view, even gliding with no keys pressed, but at its own
            // pace: it carves the turn (and banks) instead of snapping round. The rider's side steers; the server keeps
            // the heading the rider's client sent.
            if (this.isControlledByLocalInstance()) {
                yaw = Mth.approachDegrees(yaw, player.getYRot(), MAX_TURN);
            }
            this.setRot(yaw, this.headPitch(player.getXRot() * 0.5F));
            this.yBodyRot = yaw;
            this.yHeadRot = yaw;
        }
    }

    @Override
    public void travel(Vec3 input) {
        if (this.isCruising() && !this.level().isClientSide()) {
            Vec3 target = this.soarTarget != null ? this.soarTarget
                    : this.position().add(Vec3.directionFromRotation(0, this.getYRot()).scale(32));
            FlightSteering.Step step = FlightSteering.step(this.position(), this.getDeltaMovement(), this.getYRot(),
                    target, this.getAttributeValue(Attributes.FLYING_SPEED));
            this.setYRot(step.yaw());
            this.yBodyRot = this.getYRot();
            this.yHeadRot = this.getYRot();
            this.setXRot(Mth.rotLerp(0.15F, this.getXRot(), this.headPitch(
                    (float) (-Mth.atan2(step.velocity().y, step.velocity().horizontalDistance()) * Mth.RAD_TO_DEG))));
            this.setDeltaMovement(step.velocity());
            this.move(MoverType.SELF, step.velocity());
            this.calculateEntityAnimation(true);
            this.tryCheckInsideBlocks();
            return;
        }
        if (!this.level().isClientSide() && this.isResting() && this.isFlying() && !this.isVehicle()
                && !this.isKnockedOut() && !this.isSleeping() && this.getTarget() == null) {
            // Finish a flight by gliding forward and losing height, instead of braking to an airborne standstill.
            Vec3 v = this.getDeltaMovement();
            double speed = Math.max(0.20D, v.horizontalDistance() * 0.985D);
            Vec3 forward = Vec3.directionFromRotation(0, this.getYRot()).scale(speed);
            v = new Vec3(forward.x, Math.max(-0.16D, Math.min(v.y, -0.04D) - 0.008D), forward.z);
            this.setDeltaMovement(v);
            this.move(MoverType.SELF, v);
            this.calculateEntityAnimation(true);
            this.tryCheckInsideBlocks();
            return;
        }
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
        double maxSink = MAX_SINK;
        if (input.z > 0.0D) {
            double accel = FLIGHT_ACCEL * this.getAttributeValue(Attributes.FLYING_SPEED) / 0.6D * this.riddenSpeedFactor();
            Vec3 look = Vec3.directionFromRotation(rider.getXRot(), this.getYRot());
            if (look.y > 0.0D) {
                // climbing is work: the steeper, the slower it gains
                accel *= 1.0D - 0.45D * look.y;
                this.flapTicks = 0;
            }
            v = v.add(look.scale(accel * input.z));
            if (look.y < -0.4D) {
                // a dive builds speed
                drag = DIVE_DRAG;
                maxSink = DIVE_SINK;
            } else {
                drag = FLIGHT_DRAG;
            }
        } else {
            v = v.add(0.0D, -GLIDE_SINK, 0.0D);
            drag = GLIDE_DRAG;
        }
        if (input.x != 0.0D) {
            // sideways keys bank a little
            float yaw = this.getYRot() * Mth.DEG_TO_RAD;
            v = v.add(Mth.cos(yaw) * input.x * 0.02D, 0.0D, Mth.sin(yaw) * input.x * 0.02D);
        }
        if (this.riderDescending) {
            v = v.add(0.0D, -DESCEND, 0.0D);
        }
        v = new Vec3(v.x * drag, Math.max(v.y * drag, -maxSink), v.z * drag);
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

    /** Wild sky populations belong to EcoSpawner. Explicit placement retains the daytime ground check. */
    public static boolean checkFlyerSpawnRules(EntityType<? extends DinosaurEntity> type, LevelAccessor level,
                                               MobSpawnType reason, BlockPos pos, RandomSource random) {
        // EcoSpawner is the population authority for wild flyers; biome tables still supply habitat/weights.
        // Otherwise every newly generated chunk can add persistent flocks outside the regional sky budget.
        if (reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) {
            return false;
        }
        BlockState below = level.getBlockState(pos.below());
        boolean ground = below.is(BlockTags.SAND) || below.is(Blocks.GRAVEL) || below.is(BlockTags.BASE_STONE_OVERWORLD)
                || below.is(BlockTags.ANIMALS_SPAWNABLE_ON);
        return ground && level.getRawBrightness(pos, 0) > 8;
    }
}
