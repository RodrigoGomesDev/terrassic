package com.terrassic.entity;

import com.terrassic.entity.ai.DinosaurMoveControl;
import com.terrassic.entity.ai.RaptorRetreatGoal;
import com.terrassic.entity.ai.RaptorStrikeGoal;
import com.terrassic.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

import java.util.UUID;

/**
 * The raptors with a full rig of their own (the Velociraptor v3, tools/modelgen/handmade/velociraptor, WHEN in build.py
 * says when each animation plays). On top of a {@link PredatorDinosaur}:
 * <ul>
 *   <li><b>The fight</b> ({@link RaptorStrikeGoal}): creeps up ("stalk"), opens with a leap worth 1.5x, pins prey smaller
 *       than itself ("pounce"), then hit and run: a bite or a kick timed to the animation, a hop back, in again.</li>
 *   <li><b>The pack</b>: the first to pick a target screeches, the others run in without a word.</li>
 *   <li><b>Life</b>: idle gestures (sniff, look back, preen, ruffle, stretch, drink by the water), a call with its ambient
 *       voice, a threat at whatever comes close when it is not hunting, sleep by day, its own swim, flinch and death.</li>
 *   <li><b>Hunting harness</b>: the species' "saddle" (bone "saddle"): +4 armour, and it can never be ridden.</li>
 *   <li><b>Tame</b>: below 30% health it falls back behind its owner until it is above 60% ({@link RaptorRetreatGoal}), and
 *       once it has eaten in the last 5 minutes it recovers 1 HP every 4 s after 10 s without being hurt.</li>
 * </ul>
 */
public abstract class Raptor extends PredatorDinosaur {
    private static final UUID HARNESS_ARMOUR_ID = UUID.fromString("0c9f1b1e-6a54-4e7d-9d3a-7a1f6e2b4c10");
    private static final UUID LEAP_DAMAGE_ID = UUID.fromString("0c9f1b1e-6a54-4e7d-9d3a-7a1f6e2b4c11");
    private static final double HARNESS_ARMOUR = 4.0D;
    /** The cycles: pixels of ground each one covers and its length in ticks (raptanims.py, strides x K = 1.64). */
    private static final double WALK_PX = 26.24D;
    private static final double WALK_TICKS = 16.0D;
    private static final double RUN_PX = 45.92D;
    private static final double RUN_TICKS = 8.0D;
    private static final double STALK_PX = 13.12D;
    private static final double STALK_TICKS = 26.0D;
    /** Under this speed (blocks per tick, size 1.0) an aggressive raptor is creeping, not running. */
    private static final double STALK_SPEED = 0.07D;
    /** Its chase covers more ground than one run cycle at the base's limit (1.8x): the feet slid by a quarter. */
    private static final double MAX_GAIT = 2.4D;
    private static final int DEATH_TICKS = 48;
    private static final int SCREECH_TICKS = 36;
    private static final int SCREECH_VOICE = 10;
    /** First chirp of "call" (0.55 s). */
    private static final int CALL_VOICE = 11;
    /** "wake_sleep" runs 2 s, then it stretches. */
    private static final int WAKE_STRETCH = 40;
    /** Tame regeneration: 1 HP every 4 s, 10 s after the last wound, within 5 minutes of a meal. */
    private static final int REGEN_INTERVAL = 80;
    private static final int REGEN_DELAY = 200;
    private static final long MEAL_LASTS = 6000L;
    private static final float RETREAT_BELOW = 0.3F;
    private static final float RETURN_ABOVE = 0.6F;
    private static final double RETREAT_RANGE_SQR = 32.0D * 32.0D;
    private static final String[] GESTURES = {"sniff", "look_back", "preen", "ruffle", "stretch"};

    private RawAnimation stalkAnim;
    private int gestureCooldown = 200;
    private int threatCooldown;
    private int screechCooldown;
    private int screechLeft;
    private int begCooldown;
    private int rainCooldown;
    private int pendingVoice;
    private int pendingStretch;
    /** Ticks it still counts as wet after the water (then it ruffles the feathers dry). */
    private int soaked;
    private int lastWound = -REGEN_DELAY;
    /** Game time of its last real meal. */
    private long lastMeal = -MEAL_LASTS * 2L;
    private boolean retreating;

    protected Raptor(EntityType<? extends Raptor> type, Level level) {
        super(type, level);
        // narrower than a block but this fast it would circle a waypoint for ever at the limited turn rate: it pivots
        this.moveControl = new DinosaurMoveControl(this, true);
    }

    /** Renderer scale of the model (MODEL_SCALE of the species class). */
    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"sniff", "look_back", "preen", "ruffle", "stretch", "call", "screech", "display", "kick", "pounce",
                "leap", "drink"};
    }

    /** Packs of one to three: the vanilla spawner would stack its tries up to four in one spot. */
    @Override
    public int getMaxSpawnClusterSize() {
        return 3;
    }

    // ------------------------------------------------------------------ the rig's animations

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
    protected int deathAnimTicks() {
        return DEATH_TICKS;
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

    /** RaptorStrikeGoal plays the bite and the kick and times their hits. */
    @Override
    protected boolean animatesHits() {
        return false;
    }

    /** Creeping up on a target (aggressive but slow): the stalk cycle. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving() && this.isAggressive() && !this.isSleeping() && !this.isSwimmingDeep()) {
            double dx = this.getX() - this.xo;
            double dz = this.getZ() - this.zo;
            double limit = STALK_SPEED * this.getScale();
            if (dx * dx + dz * dz < limit * limit) {
                if (this.stalkAnim == null) {
                    this.stalkAnim = RawAnimation.begin().thenLoop(anim("stalk"));
                }
                PlayState play = state.setAndContinue(this.stalkAnim);
                this.cycleSpeed = this.gaitSpeed(STALK_PX / 16.0D / STALK_TICKS * this.modelScale());
                return play;
            }
        }
        return super.movementAnimation(state);
    }

    /** Afloat it paddles at the surface ("swim" has the water line at y = 0), however shallow. */
    @Override
    protected boolean isSwimmingDeep() {
        return this.isInWater() && !this.onGround();
    }

    /** One of the rig's one-shot animations, for the fight goal. */
    public void play(String name) {
        triggerAnim(ACTION_CONTROLLER, name);
    }

    /** Cuts a one-shot short (the prey got out of the pin). */
    public void stopPlaying(String name) {
        stopTriggeredAnimation(ACTION_CONTROLLER, name);
    }

    // ------------------------------------------------------------------ goals

    @Override
    protected Goal createAttackGoal() {
        return new RaptorStrikeGoal(this, this.attackSpeed());
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(2, new RaptorRetreatGoal(this));
    }

    // ------------------------------------------------------------------ the fight

    /** Standing for the hunting cry. */
    public boolean isScreeching() {
        return this.screechLeft > 0;
    }

    /** Hurt and tame: falling back behind its owner. */
    public boolean isRetreating() {
        return this.retreating;
    }

    /** The hit of a bite, a kick or the leap, its damage multiplied by {@code factor}. */
    public boolean strike(LivingEntity target, double factor) {
        AttributeInstance attack = this.getAttribute(Attributes.ATTACK_DAMAGE);
        if (factor == 1.0D || attack == null) {
            return this.doHurtTarget(target);
        }
        attack.addTransientModifier(new AttributeModifier(LEAP_DAMAGE_ID, "Raptor leap", factor - 1.0D,
                AttributeModifier.Operation.MULTIPLY_TOTAL));
        try {
            return this.doHurtTarget(target);
        } finally {
            attack.removeModifier(LEAP_DAMAGE_ID);
        }
    }

    @Override
    public void setTarget(LivingEntity target) {
        LivingEntity next = this.retreating ? null : target;
        LivingEntity previous = this.getTarget();
        super.setTarget(next);
        if (this.level().isClientSide() || next == null || previous != null || !this.isAlive() || this.isBaby()
                || !this.canAttack(next)) {
            return;
        }
        if (this.isTame()) {
            // the owner's attack order: wings open and a hiss on the way in
            if (this.threatCooldown <= 0) {
                this.threatCooldown = 600;
                this.play("display");
            }
        } else if (this.screechCooldown <= 0 && !this.packIsHunting()) {
            this.screechCooldown = 400;
            this.screechLeft = SCREECH_TICKS;
            this.getNavigation().stop();
            this.play("screech");
        }
    }

    /** Another raptor nearby already has a target: this one was called in, the cry has been given. */
    private boolean packIsHunting() {
        return !this.level().getEntitiesOfClass(Raptor.class, this.getBoundingBox().inflate(16.0D),
                e -> e != this && !e.isTame() && e.getTarget() != null).isEmpty();
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && amount > 0.0F) {
            this.lastWound = this.tickCount;
        }
        return hurt;
    }

    /** No regeneration on the gauge's passive drips: only what it really ate counts as a meal. */
    @Override
    public void feed(int amount) {
        super.feed(amount);
        if (amount > 1) {
            this.lastMeal = this.level().getGameTime();
        }
    }

    // ------------------------------------------------------------------ the harness

    /** Never a mount: a 20 kg animal carries nobody. */
    @Override
    protected boolean canAddPassenger(Entity passenger) {
        return false;
    }

    @Override
    public void setSaddled(boolean saddled) {
        super.setSaddled(saddled);
        AttributeInstance armour = this.getAttribute(Attributes.ARMOR);
        if (armour != null && !this.level().isClientSide()) {
            armour.removeModifier(HARNESS_ARMOUR_ID);
            if (saddled) {
                armour.addTransientModifier(new AttributeModifier(HARNESS_ARMOUR_ID, "Hunting harness", HARNESS_ARMOUR,
                        AttributeModifier.Operation.ADDITION));
            }
        }
    }

    /** The harness goes on like a saddle, though it is not one (isRideable stays false); shears take it off. */
    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (this.isTame() && this.isOwnedBy(player) && !this.isBaby() && !this.isKnockedOut() && !this.isSaddled()
                && stack.is(this.speciesSaddle())) {
            boolean client = this.level().isClientSide();
            if (!client) {
                this.usePlayerItem(player, hand, stack);
                this.setSaddled(true);
                this.playSound(ModSounds.SFX_SADDLE_ON.get(), 1.0F, 1.1F);
            }
            return InteractionResult.sidedSuccess(client);
        }
        return super.mobInteract(player, hand);
    }

    @Override
    public void tameBy(Player player, boolean hatched) {
        super.tameBy(player, hatched);
        this.play("tame");
    }

    // ------------------------------------------------------------------ the day

    @Override
    public void setSleeping(boolean sleeping) {
        boolean was = this.isSleeping();
        super.setSleeping(sleeping);
        if (was && !sleeping) {
            this.pendingStretch = WAKE_STRETCH;
        }
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        ServerLevel level = (ServerLevel) this.level();
        this.retreatTick();
        this.regenTick();
        if (this.screechLeft > 0) {
            this.getNavigation().stop();
            if (this.screechLeft == SCREECH_TICKS - SCREECH_VOICE) {
                SoundEvent voice = this.getAmbientSound();
                if (voice != null) {
                    this.playSound(voice, 2.0F, 1.15F * this.getVoicePitch());
                }
            }
            this.screechLeft--;
        }
        if (this.screechCooldown > 0) {
            this.screechCooldown--;
        }
        if (this.threatCooldown > 0) {
            this.threatCooldown--;
        }
        if (this.begCooldown > 0) {
            this.begCooldown--;
        }
        if (this.rainCooldown > 0) {
            this.rainCooldown--;
        }
        if (this.pendingVoice > 0 && --this.pendingVoice == 0) {
            SoundEvent voice = this.getAmbientSound();
            if (voice != null) {
                this.playSound(voice, this.getSoundVolume(), this.getVoicePitch());
            }
        }
        if (this.pendingStretch > 0 && --this.pendingStretch == 0 && this.calm()) {
            this.play("stretch");
            this.gestureCooldown = Math.max(this.gestureCooldown, 100);
        }
        // out of the water, or standing in the rain: it ruffles the feathers
        if (this.isInWater()) {
            this.soaked = 200;
        } else if (this.soaked > 0) {
            this.soaked--;
            if (this.calm()) {
                this.soaked = 0;
                this.ruffle();
            }
        } else if (this.rainCooldown <= 0 && this.calm() && level.isRainingAt(this.blockPosition().above())) {
            this.rainCooldown = 300 + this.random.nextInt(300);
            this.ruffle();
        }
        if ((this.tickCount + this.getId()) % 40 == 0) {
            this.threatTick(level);
            this.begTick();
        }
        if (this.calm() && --this.gestureCooldown <= 0) {
            this.gestureCooldown = 300 + this.random.nextInt(500);
            this.play(this.waterAhead(level) ? "drink" : GESTURES[this.random.nextInt(GESTURES.length)]);
        }
    }

    private void ruffle() {
        this.play("ruffle");
        this.gestureCooldown = Math.max(this.gestureCooldown, 100);
    }

    /** Up and about with nothing to do: standing, awake, wild or tame. */
    private boolean calm() {
        return this.isAlive() && !this.isScreeching() && this.getTarget() == null && !this.isAggressive() && !this.isSleeping()
                && !this.isKnockedOut() && !this.isInSittingPose() && !this.isPassenger() && this.onGround() && !this.isInWater()
                && this.getNavigation().isDone() && this.getDeltaMovement().horizontalDistanceSqr() < 1.0E-4D;
    }

    /** Water at its feet a step or two in front of it (it drinks like a bird). */
    private boolean waterAhead(ServerLevel level) {
        float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
        for (double d = 1.0D; d <= 2.5D; d += 0.75D) {
            BlockPos at = BlockPos.containing(this.getX() - Mth.sin(yaw) * d, this.getY() - 0.5D, this.getZ() + Mth.cos(yaw) * d);
            if (level.getFluidState(at).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }

    /** Not hunting, and a player or a bigger animal comes close: wings open and a hiss. */
    private void threatTick(ServerLevel level) {
        if (this.threatCooldown > 0 || this.isTame() || this.isBaby() || this.canHunt() || !this.calm()) {
            return;
        }
        LivingEntity near = level.getNearestPlayer(this, 7.0D);
        if (near instanceof Player player && (player.isCreative() || player.isSpectator())) {
            near = null;
        }
        if (near == null) {
            float width = this.getBbWidth() * 1.2F;
            near = level.getEntitiesOfClass(Animal.class, this.getBoundingBox().inflate(7.0D),
                    e -> e.getBbWidth() > width && !(e instanceof Raptor)).stream().findFirst().orElse(null);
        }
        if (near != null) {
            this.threatCooldown = 300 + this.random.nextInt(200);
            this.getLookControl().setLookAt(near, 30.0F, 30.0F);
            this.play("display");
        }
    }

    /** Tame, and the owner close by holds its food. */
    private void begTick() {
        if (this.begCooldown > 0 || !this.isTame() || !this.calm() || !(this.getOwner() instanceof Player owner)
                || this.distanceToSqr(owner) > 36.0D || !(this.isFood(owner.getMainHandItem()) || this.isFood(owner.getOffhandItem()))) {
            return;
        }
        this.begCooldown = 60;
        this.getLookControl().setLookAt(owner, 30.0F, 30.0F);
        this.play("beg");
    }

    private void retreatTick() {
        if (!this.isTame()) {
            this.retreating = false;
            return;
        }
        LivingEntity owner = this.getOwner();
        float share = this.getHealth() / this.getMaxHealth();
        if (owner == null || !owner.isAlive() || owner.level() != this.level() || this.distanceToSqr(owner) > RETREAT_RANGE_SQR) {
            this.retreating = false;
        } else if (share < RETREAT_BELOW) {
            this.retreating = true;
            this.setTarget(null);
        } else if (share >= RETURN_ABOVE) {
            this.retreating = false;
        }
    }

    private void regenTick() {
        if (this.isTame() && this.isAlive() && this.getHealth() < this.getMaxHealth() && this.tickCount % REGEN_INTERVAL == 0
                && this.tickCount - this.lastWound >= REGEN_DELAY && this.level().getGameTime() - this.lastMeal < MEAL_LASTS) {
            this.heal(1.0F);
        }
    }

    /** Its call goes with the ambient voice, the first chirp when the beak opens. */
    @Override
    public void playAmbientSound() {
        if (!this.level().isClientSide() && this.calm() && !this.isBaby() && this.random.nextInt(5) < 2) {
            this.play("call");
            this.pendingVoice = CALL_VOICE;
            return;
        }
        super.playAmbientSound();
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putLong("LastMeal", this.lastMeal);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("LastMeal")) {
            this.lastMeal = tag.getLong("LastMeal");
        }
    }
}
