package com.terrassic.entity;

import com.terrassic.entity.ai.DinoSleepGoal;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The pterosaurs with a full rig of their own (the Pteranodon v3, tools/modelgen/handmade/pteranodon, ANIMS in
 * build.py says when each one plays). On top of a {@link FlyingDinosaur}:
 * <ul>
 *   <li><b>Flight</b>: "takeoff" leaving the ground and "water_takeoff" leaving the water, "fly" climbing or slow,
 *       "glide" level or coming down, "bank_left" / "bank_right" gliding through a turn, "land" touching down.</li>
 *   <li><b>Fishing</b> (ai/FishingFlightGoal): "dive" down at the water and "scoop" along the surface, the beak
 *       snapping shut on the fish about 1.1 s in.</li>
 *   <li><b>Water</b>: "swim" afloat, "shake" once it is out and on its feet, now and then "sun" (wings opened to dry).</li>
 *   <li><b>Life on the ground</b>: "call" with the voice 0.4 s in, "preen", "sun", "display" (males with a female
 *       near), "beg" (young near an adult), "sleep" at night (a colonist at its colony), knockout poses for the ground
 *       and for the fall ("knocked_out_air"), and its own "death".</li>
 * </ul>
 * The rig has no "tame" or "wake_sleep": taming plays "call", waking up plays "shake". In the air the whole body also
 * pitches with the flight path and banks into turns ({@link FlyingDinosaur#flightPitch(float)}).
 */
public abstract class Pterosaur extends FlyingDinosaur {
    /** Smoothed turn rate (degrees per tick) over which a glide banks. */
    private static final float BANK_RATE = 2.0F;
    private static final int TAKEOFF_TICKS = 36;
    private static final int LAND_TICKS = 30;
    /** Ticks into "call" when the voice starts (0.4 s). */
    private static final int CALL_VOICE = 8;

    // client: the flight states, from how it moves
    private RawAnimation flyLoop;
    private RawAnimation glideLoop;
    private RawAnimation bankLeft;
    private RawAnimation bankRight;
    private RawAnimation takeoff;
    private RawAnimation waterTakeoff;
    private RawAnimation land;
    private RawAnimation knockedOutAir;
    private boolean wasAir;
    private boolean leftWater;
    private double liftY;
    private int airTicks;
    private int takeoffUntil;
    private int waterTakeoffUntil;
    private int landUntil;
    private float yawRate;
    private float lastYaw;

    // server
    private int gestureCooldown = 200;
    private int soaked;
    /** Just out of the water: the next gesture in the sun is to open the wings and dry. */
    private boolean drying;
    private int pendingVoice;

    protected Pterosaur(EntityType<? extends Pterosaur> type, Level level) {
        super(type, level);
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"dive", "scoop", "call", "display", "preen", "sun", "shake"};
    }

    @Override
    protected String actionAnimation(String trigger) {
        return switch (trigger) {
            case "tame" -> "call";
            case "wake_sleep" -> "shake";
            default -> trigger;
        };
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
    protected int deathAnimTicks() {
        return 52;
    }

    @Override
    protected boolean tiltsInFlight() {
        return true;
    }

    /** The takeoff animations already raise the body: only a little of the climb on top. */
    @Override
    protected float tiltWeight() {
        return this.tickCount < this.takeoffUntil || this.tickCount < this.waterTakeoffUntil ? 0.3F : 1.0F;
    }

    @Override
    public void flightAction(String name) {
        triggerAnim(ACTION_CONTROLLER, name);
    }

    /** Afloat it sits on the water (the "swim" pose has the water line at y = 0), however shallow. */
    @Override
    protected boolean isSwimmingDeep() {
        return this.isInWater() && !this.onGround();
    }

    @Override
    protected void addExtraGoals() {
        // asleep through the night on the ground; a colonist only once it is home
        this.goalSelector.addGoal(2, new DinoSleepGoal(this) {
            @Override
            public boolean canUse() {
                return Pterosaur.this.onGround() && Pterosaur.this.atHome() && super.canUse();
            }
        });
    }

    private boolean atHome() {
        BlockPos home = this.getColonyHome();
        return !this.isColonist() || home == null
                || Mth.square(home.getX() + 0.5D - this.getX()) + Mth.square(home.getZ() + 0.5D - this.getZ()) < 144.0D;
    }

    // ------------------------------------------------------------------ animation (client)

    @Override
    public void tick() {
        super.tick();
        if (this.level().isClientSide()) {
            this.flightStateTick();
        }
    }

    /** Takeoff, landing and turn rate, from how the animal moves (the rider's client runs the ridden flight). */
    private void flightStateTick() {
        boolean air = this.isAirborne();
        if (air) {
            if (!this.wasAir) {
                this.liftY = this.getY();
                this.airTicks = 0;
            }
            this.airTicks++;
            // three ticks up and still rising: it took off (stepping off a ledge drops instead)
            if (this.airTicks == 3 && this.getY() > this.liftY + 0.3D) {
                if (this.leftWater) {
                    this.waterTakeoffUntil = this.tickCount + TAKEOFF_TICKS - 3;
                } else {
                    this.takeoffUntil = this.tickCount + TAKEOFF_TICKS - 3;
                }
            }
        } else {
            if (this.wasAir && this.airTicks > 20 && !this.isInWater() && !this.isKnockedOut()) {
                this.landUntil = this.tickCount + LAND_TICKS;
            }
            this.airTicks = 0;
            this.leftWater = this.isInWater();
        }
        this.wasAir = air;
        float turn = Mth.wrapDegrees(this.getYRot() - this.lastYaw);
        this.lastYaw = this.getYRot();
        this.yawRate = this.yawRate * 0.8F + turn * 0.2F;
    }

    @Override
    protected PlayState knockedOutAnimation(AnimationState<DinosaurEntity> state) {
        if (this.isAirborne()) {
            this.ensureAnims();
            return state.setAndContinue(this.knockedOutAir);
        }
        return super.knockedOutAnimation(state);
    }

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        this.ensureAnims();
        if (this.isAirborne()) {
            return state.setAndContinue(this.flightAnimation());
        }
        if (this.tickCount < this.landUntil && !this.isInWater() && !this.isSleeping() && !this.isInSittingPose()
                && this.getDeltaMovement().horizontalDistanceSqr() < 0.01D) {
            return state.setAndContinue(this.land);
        }
        return super.movementAnimation(state);
    }

    private RawAnimation flightAnimation() {
        if (this.tickCount < this.waterTakeoffUntil) {
            return this.waterTakeoff;
        }
        if (this.tickCount < this.takeoffUntil) {
            return this.takeoff;
        }
        Vec3 v = this.getDeltaMovement();
        boolean climbingOrSlow = v.y > 0.035D || v.horizontalDistanceSqr() < 0.04D;
        if (!climbingOrSlow) {
            // yaw grows turning right
            if (this.yawRate > BANK_RATE) {
                return this.bankRight;
            }
            if (this.yawRate < -BANK_RATE) {
                return this.bankLeft;
            }
            // coming down it glides; level, it glides most of the time with a few wing beats (phase differs per animal)
            if (v.y < -0.02D || (this.tickCount + this.getId() * 7) % 100 > 30) {
                return this.glideLoop;
            }
        }
        return this.flyLoop;
    }

    private void ensureAnims() {
        if (this.flyLoop != null) {
            return;
        }
        this.flyLoop = RawAnimation.begin().thenLoop(anim("fly"));
        this.glideLoop = RawAnimation.begin().thenLoop(anim("glide"));
        this.bankLeft = RawAnimation.begin().thenLoop(anim("bank_left"));
        this.bankRight = RawAnimation.begin().thenLoop(anim("bank_right"));
        this.takeoff = RawAnimation.begin().thenPlay(anim("takeoff")).thenLoop(anim("fly"));
        this.waterTakeoff = RawAnimation.begin().thenPlay(anim("water_takeoff")).thenLoop(anim("fly"));
        this.land = RawAnimation.begin().thenPlay(anim("land")).thenLoop(anim("idle"));
        this.knockedOutAir = RawAnimation.begin().thenLoop(anim("knocked_out_air"));
    }

    // ------------------------------------------------------------------ life (server)

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.pendingVoice > 0 && --this.pendingVoice == 0) {
            SoundEvent voice = this.getAmbientSound();
            if (voice != null) {
                this.playSound(voice, this.getSoundVolume(), this.getVoicePitch());
            }
        }
        // out of the water and on its feet: it shakes the water off, and later may open its wings in the sun to dry
        if (this.isInWater()) {
            this.soaked = 200;
        } else if (this.soaked > 0) {
            this.soaked--;
            if (this.calm()) {
                triggerAnim(ACTION_CONTROLLER, "shake");
                this.soaked = 0;
                this.gestureCooldown = 60 + this.random.nextInt(60);
                this.drying = true;
            }
        }
        if (this.calm() && --this.gestureCooldown <= 0) {
            this.gestureCooldown = 300 + this.random.nextInt(500);
            this.gesture();
        }
    }

    /** Standing about with nothing to do. */
    private boolean calm() {
        return this.isAlive() && this.getTarget() == null && !this.isAggressive() && !this.isSleeping() && !this.isKnockedOut()
                && !this.isInSittingPose() && !this.isVehicle() && !this.isPassenger() && this.onGround() && !this.isInWater()
                && this.getNavigation().isDone() && this.getDeltaMovement().horizontalDistanceSqr() < 1.0E-4D;
    }

    private void gesture() {
        if (this.isBaby()) {
            // young near an adult beg for fish
            if (!this.level().getEntitiesOfClass(Pterosaur.class, this.getBoundingBox().inflate(6.0D),
                    e -> e.getType() == this.getType() && !e.isBaby()).isEmpty()) {
                triggerAnim(ACTION_CONTROLLER, "beg");
            }
            return;
        }
        boolean sunny = this.level().isDay() && !this.level().isRaining() && this.level().canSeeSky(this.blockPosition().above(3));
        if (this.drying && sunny) {
            this.drying = false;
            triggerAnim(ACTION_CONTROLLER, "sun");
            return;
        }
        this.drying = false;
        int roll = this.random.nextInt(6);
        if (roll == 0 && !this.isFemale() && this.level().isDay() && !this.level().getEntitiesOfClass(Pterosaur.class,
                this.getBoundingBox().inflate(8.0D), e -> e.getType() == this.getType() && e.isFemale() && !e.isBaby()).isEmpty()) {
            triggerAnim(ACTION_CONTROLLER, "display");
        } else if (roll == 1 && sunny) {
            triggerAnim(ACTION_CONTROLLER, "sun");
        } else if (roll <= 3) {
            triggerAnim(ACTION_CONTROLLER, "preen");
        } else {
            this.call();
        }
    }

    /** The call, with the voice when the beak opens. */
    private void call() {
        triggerAnim(ACTION_CONTROLLER, "call");
        this.pendingVoice = CALL_VOICE;
    }

    /** On the ground its ambient voice comes with the call. */
    @Override
    public void playAmbientSound() {
        if (!this.level().isClientSide() && this.calm() && !this.isBaby() && this.random.nextInt(5) < 2) {
            this.call();
            return;
        }
        super.playAmbientSound();
    }
}
