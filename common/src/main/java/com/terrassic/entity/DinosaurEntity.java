package com.terrassic.entity;

import com.terrassic.registry.ModBlocks;
import com.terrassic.research.Objective;
import com.terrassic.research.Research;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.PlayerRideableJumping;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Base class of every Terrassic dinosaur.
 *
 * <ul>
 *   <li><b>Animations</b> live in assets/terrassic/animations/entity/&lt;species&gt;.animation.json and are named
 *       "animation.&lt;species&gt;.&lt;name&gt;": idle / walk / run / sit / attack (+ extra actions such as roar or graze).</li>
 *   <li><b>Sex</b>: every dinosaur is male or female (random, saved, synced). Males and females use different
 *       textures, bones called "male_*" / "female_*" are only shown for that sex, and only couples can breed.</li>
 *   <li><b>Taming</b>: herbivores (and the compy) are tamed by hand-feeding; predators only accept food while they
 *       are babies. A baby hatching from an egg imprints on the closest player and is born tame.</li>
 *   <li><b>Riding</b>: species that return true from {@link #isRideable()} accept a saddle once tamed. Space
 *       jumps (hold it for a higher jump, like a horse); shears take the saddle off.</li>
 *   <li><b>Eggs</b>: breeding lays a dinosaur egg block next to the female, which hatches after a few minutes.</li>
 * </ul>
 */
public abstract class DinosaurEntity extends TamableAnimal implements GeoEntity, PlayerRideableJumping {
    public static final String ACTION_CONTROLLER = "action";

    private static final EntityDataAccessor<Boolean> DATA_FEMALE =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> DATA_SADDLED =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);

    /** How a wild animal of this species can be tamed (eggs always work). */
    public enum TameMethod {
        /** Hand-feed its food: each bite has a 1 in {@link #tameChance()} chance. */
        FEEDING,
        /** Only babies accept food from players (predators). */
        BABY_FEEDING
    }

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private RawAnimation idleAnim;
    private RawAnimation walkAnim;
    private RawAnimation runAnim;
    private RawAnimation sitAnim;
    /** Jump asked by the rider (0..1), done on the next ridden tick on the ground. */
    private float riderJump;
    /** Ticks after perching during which the owner's sneak does not shake the animal off (it was sneaking to perch it). */
    private int perchGrace;
    /** Cooldown of the perched animal's danger warning. */
    private int perchWarnCooldown;

    protected DinosaurEntity(EntityType<? extends DinosaurEntity> type, Level level) {
        super(type, level);
        this.entityData.set(DATA_FEMALE, this.random.nextBoolean());
    }

    // ------------------------------------------------------------------ species hooks

    /** Species id, used for asset and animation names. */
    public abstract String speciesId();

    /** Extra one-shot animations besides "attack". */
    protected String[] extraActions() {
        return new String[0];
    }

    public TameMethod tameMethod() {
        return TameMethod.FEEDING;
    }

    /** 1 in N chance per food item to tame. */
    protected int tameChance() {
        return 4;
    }

    /** Whether a tamed adult accepts a saddle and can be ridden. */
    public boolean isRideable() {
        return false;
    }

    /** Whether a tamed adult hops onto its owner's shoulder when they sneak and right-click it with an empty hand. */
    public boolean canPerch() {
        return false;
    }

    /** Whether a perched animal dives for fish now and then when its owner stands near water. */
    protected boolean perchFishes() {
        return false;
    }

    /** Ridden speed multiplier on top of the movement speed attribute. */
    protected float riddenSpeedFactor() {
        return 1.0F;
    }

    /** How far forward of the entity's centre the saddle sits (blocks). */
    protected double riderForwardOffset() {
        return 0.0D;
    }

    /** Upward speed of a full-power ridden jump (0.5 ~ 1.3 blocks, 0.8 ~ 3 blocks). 0 = cannot jump. */
    protected double jumpStrength() {
        return 0.5D;
    }

    /** Squared horizontal speed (blocks/tick) above which the run cycle is used. */
    protected double runThresholdSqr() {
        return 0.012D;
    }

    /** Size of a baby relative to the adult. Applied to the hitbox here and to the model by DinosaurRenderer. */
    protected float babyScale() {
        return 0.5F;
    }

    @Override
    public float getScale() {
        return this.isBaby() ? this.babyScale() : 1.0F;
    }

    /** How far the model sticks out of the hitbox (blocks), for frustum culling. */
    protected double cullingInflate() {
        return 1.0D;
    }

    protected String anim(String name) {
        return "animation." + speciesId() + "." + name;
    }

    /** Wild predators only hunt when grown up and when the world is not on Peaceful. */
    protected boolean canHunt() {
        return !this.isBaby() && !this.isTame() && this.level().getDifficulty() != Difficulty.PEACEFUL;
    }

    // ------------------------------------------------------------------ synced data / save

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_FEMALE, false);
        this.entityData.define(DATA_SADDLED, false);
    }

    public boolean isFemale() {
        return this.entityData.get(DATA_FEMALE);
    }

    public void setFemale(boolean female) {
        this.entityData.set(DATA_FEMALE, female);
    }

    public boolean isSaddled() {
        return this.entityData.get(DATA_SADDLED);
    }

    public void setSaddled(boolean saddled) {
        this.entityData.set(DATA_SADDLED, saddled);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Female", this.isFemale());
        tag.putBoolean("Saddled", this.isSaddled());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Female")) {
            this.setFemale(tag.getBoolean("Female"));
        }
        this.setSaddled(tag.getBoolean("Saddled"));
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        SpawnGroupData spawnData, CompoundTag tag) {
        this.setFemale(this.random.nextBoolean());
        return super.finalizeSpawn(level, difficulty, reason, spawnData, tag);
    }

    // ------------------------------------------------------------------ GeckoLib

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        this.idleAnim = RawAnimation.begin().thenLoop(anim("idle"));
        this.walkAnim = RawAnimation.begin().thenLoop(anim("walk"));
        this.runAnim = RawAnimation.begin().thenLoop(anim("run"));
        this.sitAnim = RawAnimation.begin().thenLoop(anim("sit"));

        controllers.add(new AnimationController<>(this, "movement", 6, this::movementAnimation));

        AnimationController<DinosaurEntity> action = new AnimationController<>(this, ACTION_CONTROLLER, 3, state -> PlayState.STOP);
        action.triggerableAnim("attack", RawAnimation.begin().thenPlay(anim("attack")));
        for (String extra : extraActions()) {
            action.triggerableAnim(extra, RawAnimation.begin().thenPlay(anim(extra)));
        }
        controllers.add(action);
    }

    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.isPerched() || (this.isInSittingPose() && !this.isVehicle())) {
            return state.setAndContinue(this.sitAnim);
        }
        if (state.isMoving()) {
            boolean running = this.isAggressive() || this.getDeltaMovement().horizontalDistanceSqr() > runThresholdSqr();
            return state.setAndContinue(running ? this.runAnim : this.walkAnim);
        }
        return state.setAndContinue(this.idleAnim);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.geoCache;
    }

    // ------------------------------------------------------------------ combat / misc

    /** Players who studied the species know its weak spots: +20% damage. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getEntity() instanceof Player player && Research.isStudied(player, this.speciesId())) {
            amount *= 1.2F;
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.level().isClientSide()) {
            triggerAnim(ACTION_CONTROLLER, "attack");
        }
        return hit;
    }

    @Override
    public boolean removeWhenFarAway(double distanceToClosestPlayer) {
        return false;
    }

    @Override
    public AABB getBoundingBoxForCulling() {
        return this.getBoundingBox().inflate(cullingInflate());
    }

    @Override
    protected void dropEquipment() {
        super.dropEquipment();
        if (this.isSaddled()) {
            this.spawnAtLocation(Items.SADDLE);
        }
    }

    // ------------------------------------------------------------------ taming / interaction

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean client = this.level().isClientSide();

        if (this.isTame() && this.isOwnedBy(player)) {
            // heal with food
            if (this.isFood(stack) && this.getHealth() < this.getMaxHealth()) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.heal(Math.max(2.0F, this.getMaxHealth() * 0.1F));
                }
                return InteractionResult.sidedSuccess(client);
            }
            // shoulder animals hop on when the owner sneaks with an empty hand (sneak again later to shake it off)
            if (this.canPerch() && !this.isBaby() && stack.isEmpty() && player.isShiftKeyDown() && !this.isPassenger()
                    && !player.isVehicle() && !player.isPassenger()) {
                if (!client) {
                    this.setOrderedToSit(false);
                    this.navigation.stop();
                    this.setTarget(null);
                    this.startRiding(player, true);
                    this.perchGrace = 60;
                    player.displayClientMessage(Component.translatable("message.terrassic.perch", this.getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // saddle
            if (this.isRideable() && !this.isBaby() && !this.isSaddled() && stack.is(Items.SADDLE)) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.setSaddled(true);
                    this.playSound(SoundEvents.HORSE_SADDLE, 1.0F, 0.8F);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // shears take the saddle off
            if (this.isSaddled() && !this.isVehicle() && stack.is(Items.SHEARS)) {
                if (!client) {
                    this.setSaddled(false);
                    this.spawnAtLocation(Items.SADDLE);
                    this.playSound(SoundEvents.SHEEP_SHEAR, 1.0F, 1.0F);
                    stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
                }
                return InteractionResult.sidedSuccess(client);
            }
            if (stack.isEmpty()) {
                // ride (saddled) or toggle sit / follow (sneak, or not saddled)
                if (this.isSaddled() && !this.isBaby() && !player.isSecondaryUseActive() && !this.isVehicle()) {
                    if (!client) {
                        this.setOrderedToSit(false);
                        player.startRiding(this);
                        if (player instanceof ServerPlayer sp) {
                            Research.objective(sp, Objective.RIDE);
                        }
                    }
                    return InteractionResult.sidedSuccess(client);
                }
                if (!client) {
                    boolean sit = !this.isOrderedToSit();
                    this.setOrderedToSit(sit);
                    this.jumping = false;
                    this.navigation.stop();
                    this.setTarget(null);
                    player.displayClientMessage(Component.translatable(sit ? "message.terrassic.sit" : "message.terrassic.follow",
                            this.getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            return super.mobInteract(player, hand);
        }

        if (!this.isTame() && this.isFood(stack) && this.canBeTamedNow()) {
            if (!client) {
                this.usePlayerItem(player, hand, stack);
                // studying the species (Field Guide "studied") makes taming faster
                int chance = Research.isStudied(player, this.speciesId()) ? Math.max(2, tameChance() - 1) : tameChance();
                if (this.random.nextInt(chance) == 0) {
                    this.tameBy(player);
                } else {
                    this.level().broadcastEntityEvent(this, (byte) 6);
                }
            }
            return InteractionResult.sidedSuccess(client);
        }
        return super.mobInteract(player, hand);
    }

    protected boolean canBeTamedNow() {
        if (this.getTarget() != null) {
            return false;
        }
        return this.tameMethod() == TameMethod.FEEDING || this.isBaby();
    }

    /** Tames the animal for the player (feeding or egg imprinting). */
    public void tameBy(Player player) {
        this.tame(player);
        if (player instanceof ServerPlayer sp) {
            Research.tamed(sp, this);
        }
        this.navigation.stop();
        this.setTarget(null);
        this.setOrderedToSit(true);
        this.level().broadcastEntityEvent(this, (byte) 7);
        player.displayClientMessage(Component.translatable("message.terrassic.tamed", this.getDisplayName(),
                Component.translatable(this.isFemale() ? "sex.terrassic.female" : "sex.terrassic.male")), true);
    }

    // ------------------------------------------------------------------ shoulder perch

    /** True while riding on a player's shoulder. */
    public boolean isPerched() {
        return this.getVehicle() instanceof Player;
    }

    @Override
    public void tick() {
        super.tick();
        if (this.isPerched()) {
            this.perchedTick((Player) this.getVehicle());
        }
    }

    private void perchedTick(Player owner) {
        // turn with the owner so the animal looks where they look
        this.setYRot(owner.yBodyRot);
        this.yRotO = this.getYRot();
        this.yBodyRot = owner.yBodyRot;
        this.yHeadRot = owner.yHeadRot;
        this.setXRot(0.0F);
        if (this.level().isClientSide()) {
            return;
        }
        if (this.perchGrace > 0) {
            this.perchGrace--;
        }
        if (this.perchWarnCooldown > 0) {
            this.perchWarnCooldown--;
        }
        boolean shakeOff = (owner.isShiftKeyDown() && this.perchGrace == 0) || owner.isDeadOrDying() || owner.isSpectator()
                || owner.isInWater() || owner.isSleeping() || !this.isTame() || !this.isOwnedBy(owner) || this.isDeadOrDying();
        if (shakeOff) {
            this.stopRiding();
            return;
        }
        // a lookout: calls out when a monster is after the owner
        if (this.perchWarnCooldown == 0 && this.tickCount % 20 == 0) {
            for (Monster m : this.level().getEntitiesOfClass(Monster.class, owner.getBoundingBox().inflate(12.0D))) {
                if (m.getTarget() == owner) {
                    SoundEvent call = this.getAmbientSound();
                    if (call != null) {
                        this.playSound(call, 1.0F, 1.3F);
                    }
                    owner.displayClientMessage(Component.translatable("message.terrassic.perch_warn", this.getDisplayName()), true);
                    this.perchWarnCooldown = 200;
                    break;
                }
            }
        }
        // fishing birds dive from the shoulder now and then and bring the owner a fish
        if (this.perchFishes() && this.random.nextInt(1800) == 0 && nearWater(owner.blockPosition())) {
            ItemEntity fish = new ItemEntity(this.level(), owner.getX(), owner.getY() + 1.0D, owner.getZ(), new ItemStack(Items.COD));
            fish.setPickUpDelay(10);
            this.level().addFreshEntity(fish);
            this.playSound(SoundEvents.GENERIC_SPLASH, 0.6F, 1.4F);
            triggerAnim(ACTION_CONTROLLER, "attack");
            owner.displayClientMessage(Component.translatable("message.terrassic.perch_fish", this.getDisplayName()), true);
        }
    }

    private boolean nearWater(BlockPos centre) {
        for (BlockPos pos : BlockPos.betweenClosed(centre.offset(-4, -2, -4), centre.offset(4, 1, 4))) {
            if (this.level().getFluidState(pos).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean isPickable() {
        return !this.isPerched() && super.isPickable();
    }

    @Override
    public boolean isPushable() {
        return !this.isPerched() && super.isPushable();
    }

    @Override
    public double getMyRidingOffset() {
        // on a player the vanilla offset puts us at chest height; lift to the shoulder
        return this.isPerched() ? 0.1D : super.getMyRidingOffset();
    }

    // ------------------------------------------------------------------ riding

    @Override
    public LivingEntity getControllingPassenger() {
        if (this.isSaddled() && this.getFirstPassenger() instanceof Player player) {
            return player;
        }
        return super.getControllingPassenger();
    }

    @Override
    public void positionRider(Entity passenger, Entity.MoveFunction move) {
        if (!this.hasPassenger(passenger)) {
            return;
        }
        double forward = this.riderForwardOffset() * this.getScale();
        float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
        move.accept(passenger, this.getX() - Mth.sin(yaw) * forward,
                this.getY() + this.getPassengersRidingOffset() + passenger.getMyRidingOffset(),
                this.getZ() + Mth.cos(yaw) * forward);
    }

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        super.tickRidden(player, input);
        if (player.zza != 0 || player.xxa != 0) {
            this.setRot(player.getYRot(), player.getXRot() * 0.25F);
            this.yRotO = this.getYRot();
            this.yBodyRot = this.getYRot();
            this.yHeadRot = this.getYRot();
            this.getNavigation().stop();
            this.setTarget(null);
        }
    }

    @Override
    public void travel(Vec3 input) {
        if (this.riderJump > 0.0F && this.isVehicle() && this.onGround() && this.isControlledByLocalInstance()) {
            Vec3 v = this.getDeltaMovement();
            double up = this.jumpStrength() * this.riderJump * this.getBlockJumpFactor() + this.getJumpBoostPower();
            this.setDeltaMovement(v.x, up, v.z);
            if (input.z > 0.0D) {
                float yaw = this.getYRot() * Mth.DEG_TO_RAD;
                this.setDeltaMovement(this.getDeltaMovement().add(-0.4F * Mth.sin(yaw) * this.riderJump, 0.0D,
                        0.4F * Mth.cos(yaw) * this.riderJump));
            }
            this.hasImpulse = true;
            this.riderJump = 0.0F;
        }
        super.travel(input);
    }

    // jumping while ridden (the vanilla horse jump bar)

    @Override
    public void onPlayerJump(int power) {
        if (!this.canJump()) {
            return;
        }
        this.riderJump = power <= 0 ? 0.0F : power >= 90 ? 1.0F : 0.4F + 0.6F * power / 90.0F;
    }

    @Override
    public boolean canJump() {
        return this.isSaddled() && !this.isBaby() && this.jumpStrength() > 0.0D;
    }

    @Override
    public void handleStartJump(int power) {
    }

    @Override
    public void handleStopJump() {
    }

    @Override
    protected Vec3 getRiddenInput(Player player, Vec3 input) {
        float forward = player.zza;
        if (forward <= 0.0F) {
            forward *= 0.3F;
        }
        return new Vec3(player.xxa * 0.4F, 0.0D, forward);
    }

    @Override
    protected float getRiddenSpeed(Player player) {
        return (float) this.getAttributeValue(Attributes.MOVEMENT_SPEED) * riddenSpeedFactor();
    }

    // ------------------------------------------------------------------ breeding & eggs

    @Override
    public boolean canMate(Animal other) {
        if (other == this || other.getClass() != this.getClass() || !(other instanceof DinosaurEntity dino)) {
            return false;
        }
        return this.isInLove() && other.isInLove() && dino.isFemale() != this.isFemale();
    }

    @Override
    public void spawnChildFromBreeding(ServerLevel level, Animal partner) {
        Block egg = ModBlocks.eggFor(this.speciesId());
        if (egg == null) {
            super.spawnChildFromBreeding(level, partner);
            return;
        }
        DinosaurEntity mother = partner instanceof DinosaurEntity d && d.isFemale() ? d : this;
        BlockPos pos = findEggSpot(level, mother.blockPosition());
        if (pos != null) {
            level.setBlock(pos, egg.defaultBlockState(), Block.UPDATE_ALL);
            level.playSound(null, pos, SoundEvents.TURTLE_LAY_EGG, SoundSource.BLOCKS, 0.7F, 0.9F);
        } else {
            mother.spawnAtLocation(egg);
        }

        ServerPlayer cause = this.getLoveCause();
        if (cause == null) {
            cause = partner.getLoveCause();
        }
        if (cause != null) {
            cause.awardStat(Stats.ANIMALS_BRED);
            CriteriaTriggers.BRED_ANIMALS.trigger(cause, this, partner, null);
        }
        this.setAge(6000);
        partner.setAge(6000);
        this.resetLove();
        partner.resetLove();
        level.broadcastEntityEvent(this, (byte) 18);
        if (level.getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT)) {
            level.addFreshEntity(new ExperienceOrb(level, this.getX(), this.getY(), this.getZ(), this.getRandom().nextInt(7) + 1));
        }
    }

    private static BlockPos findEggSpot(ServerLevel level, BlockPos center) {
        for (int r = 1; r <= 3; r++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    for (int dy = 1; dy >= -1; dy--) {
                        BlockPos pos = center.offset(dx, dy, dz);
                        BlockPos below = pos.below();
                        if (level.isEmptyBlock(pos) && level.getBlockState(below).isFaceSturdy(level, below, Direction.UP)) {
                            return pos;
                        }
                    }
                }
            }
        }
        return null;
    }

    // ------------------------------------------------------------------ spawning

    /** Spawn rule: like animals, but also allows sand, terracotta, coarse dirt, podzol and mud. */
    public static boolean checkDinoSpawnRules(EntityType<? extends DinosaurEntity> type, LevelAccessor level,
                                              MobSpawnType reason, BlockPos pos, RandomSource random) {
        BlockState below = level.getBlockState(pos.below());
        boolean ground = below.is(BlockTags.ANIMALS_SPAWNABLE_ON) || below.is(BlockTags.SAND)
                || below.is(BlockTags.TERRACOTTA) || below.is(Blocks.COARSE_DIRT) || below.is(Blocks.PODZOL)
                || below.is(Blocks.MUD);
        return ground && level.getRawBrightness(pos, 0) > 8;
    }
}
