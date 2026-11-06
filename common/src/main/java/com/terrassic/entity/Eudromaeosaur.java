package com.terrassic.entity;

import com.terrassic.Terrassic;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Dakotaraptor rig (tools/modelgen/handmade/dakotaraptor, its own study). Not a big Velociraptor: a heavy
 * runner of the floodplain with a deep head, long legs, the great sickle claw and big wings. What it adds over a
 * {@link PredatorDinosaur}:
 * <ul>
 *   <li>the walk, run and creeping "stalk" follow the real speed of its legs, so the feet do not slide;</li>
 *   <li>the POUNCE: closing on prey from 4 to 8 blocks, it crouches and leaps feet first with the sickles forward and the
 *       wings flung out ("pounce"), the opening blow worth more;</li>
 *   <li>the PIN (raptor prey restraint, Fowler et al. 2011): a hit on prey smaller than itself holds it down under one
 *       foot ("pin"): the prey is slowed and weakened for a moment while the raptor beats its wings for balance;</li>
 *   <li>the MANTLE: on a kill it spreads its wings low over the carcass and tears at it ("mantle"), as hawks do;</li>
 *   <li>the WING FLASH: wild and not hunting, it throws its wings open and raises the tail fan at a player or a big
 *       animal that walks up close ("wing_flash"), and does it once at the start of a hunt to startle the prey;</li>
 *   <li>life: it sniffs, looks back, preens the long wing feathers, suns with the wings open in daylight, shakes after
 *       the water, stretches and yawns.</li>
 * </ul>
 */
public abstract class Eudromaeosaur extends PredatorDinosaur {
    /** The cycles (dakotaanims.py: walk, run, stalk, strides x K = 0.9): pixels of ground each covers and its ticks. */
    private static final double WALK_PX = 36.0D;
    private static final double WALK_TICKS = 26.0D;
    private static final double RUN_PX = 75.6D;
    private static final double RUN_TICKS = 11.2D;
    private static final double STALK_PX = 28.08D;
    private static final double STALK_TICKS = 38.2D;
    /** Under this speed (blocks per tick, size 1.0) an aggressive one is creeping, not running. */
    private static final double STALK_SPEED = 0.09D;
    private static final double MAX_GAIT = 2.2D;
    private static final ResourceLocation POUNCE_ID = Terrassic.id("dakotaraptor_pounce_damage");
    private static final String[] GESTURES = {"sniff", "look_back", "preen", "stretch", "yawn"};

    private RawAnimation stalkLoop;
    private int pounceCooldown;
    private int flashCooldown = 200;
    private int gestureCooldown = 300;
    private int soaked;
    private int still;
    private boolean pouncing;

    protected Eudromaeosaur(EntityType<? extends Eudromaeosaur> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"sniff", "look_back", "preen", "stretch", "yawn", "shake", "sun", "drink", "call", "threat",
                "bite", "pounce", "pin", "mantle", "wing_flash"};
    }

    @Override
    public int getMaxSpawnClusterSize() {
        return 3;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    @Override
    protected double gaitSpeed(double cycle) {
        double dx = this.getX() - this.xo;
        double dz = this.getZ() - this.zo;
        return cycle <= 0.0D ? 1.0D : Mth.clamp(Math.sqrt(dx * dx + dz * dz) / (cycle * this.getScale()), 0.5D, MAX_GAIT);
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
        return 48;
    }

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving() && this.isAggressive() && this.onGround() && !this.isVehicle() && !this.isInWater() && !this.isBaby()) {
            double dx = this.getX() - this.xo;
            double dz = this.getZ() - this.zo;
            if (Math.sqrt(dx * dx + dz * dz) < STALK_SPEED * this.getScale()) {
                if (this.stalkLoop == null) {
                    this.stalkLoop = RawAnimation.begin().thenLoop(anim("stalk"));
                }
                state.getController().setAnimationSpeed(Mth.clamp(Math.sqrt(dx * dx + dz * dz)
                        / (STALK_PX / 16.0D / STALK_TICKS * this.modelScale() * this.getScale()), 0.5D, 1.6D));
                return state.setAndContinue(this.stalkLoop);
            }
        }
        return super.movementAnimation(state);
    }

    @Override
    public void setTarget(LivingEntity target) {
        LivingEntity before = this.getTarget();
        super.setTarget(target);
        // the start of a hunt: the wings thrown open once to startle the prey into running
        if (target != null && before == null && !this.level().isClientSide() && !this.isTame() && !this.isBaby()
                && this.flashCooldown == 0 && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "wing_flash");
            this.flashCooldown = 400;
        }
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean pounced = this.pouncing;
        this.pouncing = false;
        // the sickles land first: the opening blow of a pounce counts half again (in the same blow, so the prey's
        // hurt cooldown cannot swallow it)
        AttributeInstance damage = this.getAttribute(Attributes.ATTACK_DAMAGE);
        if (pounced && damage != null) {
            damage.addTransientModifier(new AttributeModifier(POUNCE_ID, 0.5D, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
        }
        boolean hit;
        try {
            hit = super.doHurtTarget(target);
        } finally {
            if (damage != null) {
                damage.removeModifier(POUNCE_ID);
            }
        }
        if (!hit || !(target instanceof LivingEntity living)) {
            return hit;
        }
        if (!living.isAlive()) {
            triggerAnim(ACTION_CONTROLLER, "mantle");
            this.still = 90;
            this.feed(4);
        } else if (living.getBbWidth() < this.getBbWidth() && !(living instanceof Player && ((Player) living).isCreative())) {
            // the pin: held down under one foot for a moment
            triggerAnim(ACTION_CONTROLLER, "pin");
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 50, 3), this);
            living.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 50, 0), this);
            this.still = Math.max(this.still, 20);
        } else if (this.random.nextBoolean()) {
            triggerAnim(ACTION_CONTROLLER, "bite");
        }
        return hit;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt) {
            this.still = 0;
        }
        return hurt;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.pounceCooldown > 0) {
            this.pounceCooldown--;
        }
        if (this.flashCooldown > 0) {
            this.flashCooldown--;
        }
        if (this.gestureCooldown > 0) {
            this.gestureCooldown--;
        }
        if (this.isInWater()) {
            this.soaked = 200;
        } else if (this.soaked > 0 && --this.soaked == 0 && !this.isSleeping() && !this.isKnockedOut()) {
            triggerAnim(ACTION_CONTROLLER, "shake");
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.isSleeping() || this.isKnockedOut() || this.isVehicle() || this.isInSittingPose()) {
            return;
        }
        LivingEntity target = this.getTarget();
        if (target != null) {
            this.tryPounce(target);
            return;
        }
        if (!this.isTame() && !this.isBaby() && this.flashCooldown == 0 && this.tickCount % 10 == 0) {
            this.flashAtIntruder();
        }
        if (this.gestureCooldown == 0 && this.getNavigation().isDone() && this.random.nextInt(240) == 0) {
            this.gesture();
        }
    }

    /** From 4 to 8 blocks, on the ground and with a clear line: the crouch and the leap feet first. */
    private void tryPounce(LivingEntity target) {
        if (this.pounceCooldown > 0 || !this.onGround() || this.isInWater() || this.isBaby() || !this.hasLineOfSight(target)) {
            return;
        }
        double d = this.distanceTo(target) / Math.max(0.5F, this.getScale());
        if (d < 4.0D || d > 8.0D) {
            return;
        }
        triggerAnim(ACTION_CONTROLLER, "pounce");
        Vec3 to = target.position().subtract(this.position());
        Vec3 flat = new Vec3(to.x, 0.0D, to.z).normalize();
        double reach = Math.min(1.4D, to.horizontalDistance() * 0.16D);
        this.setDeltaMovement(flat.x * reach, 0.5D, flat.z * reach);
        this.lookAt(target, 60.0F, 30.0F);
        this.pouncing = true;
        this.pounceCooldown = 100 + this.random.nextInt(60);
    }

    /** Wild and not hunting: a player (not in creative or spectator) or a big animal walking up within 6 blocks. */
    private void flashAtIntruder() {
        LivingEntity near = this.level().getNearestPlayer(this, 6.0D * this.getScale());
        if (near instanceof Player p && (p.isCreative() || p.isSpectator())) {
            near = null;
        }
        if (near == null) {
            near = this.level().getEntitiesOfClass(DinosaurEntity.class, this.getBoundingBox().inflate(6.0D),
                    e -> e.isAlive() && !(e instanceof Eudromaeosaur) && e.getBbWidth() > this.getBbWidth() * 1.5F
                            && this.hasLineOfSight(e)).stream().findFirst().orElse(null);
        }
        if (near != null) {
            this.getLookControl().setLookAt(near, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "wing_flash");
            this.flashCooldown = 600;
            this.still = 28;
        }
    }

    private void gesture() {
        this.gestureCooldown = 300 + this.random.nextInt(300);
        if (this.isNearWater() && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "drink");
            this.still = 80;
            return;
        }
        if (this.level().isDay() && this.level().canSeeSky(this.blockPosition()) && !this.level().isRaining()
                && this.random.nextInt(4) == 0) {
            triggerAnim(ACTION_CONTROLLER, "sun");
            this.still = 100;
            return;
        }
        triggerAnim(ACTION_CONTROLLER, GESTURES[this.random.nextInt(GESTURES.length)]);
        this.still = 40;
    }

    private boolean isNearWater() {
        for (net.minecraft.core.BlockPos p : net.minecraft.core.BlockPos.betweenClosed(this.blockPosition().offset(-2, -1, -2),
                this.blockPosition().offset(2, 0, 2))) {
            if (this.level().getFluidState(p).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }
}
