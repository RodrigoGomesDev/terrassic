package com.terrassic.entity;

import com.terrassic.block.DinoEggBlock;
import com.terrassic.registry.ModBlocks;
import com.terrassic.registry.ModItems;
import com.terrassic.research.Objective;
import com.terrassic.research.Research;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.Containers;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.HasCustomInventoryScreen;
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
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.MenuType;
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

import java.util.ArrayList;
import java.util.List;

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
 *   <li><b>Cargo</b>: species with {@link #cargoRows()} &gt; 0 take a chest once tamed and grown; the chest is a
 *       cargo inventory of that many rows (sneak + use opens it, or the inventory key while riding), and the animal
 *       picks up the drops around its feet while it is up and about (docs/CARGA.md).</li>
 *   <li><b>Carcass</b>: a dead dinosaur leaves a {@link CarcassEntity} holding its death loot (docs/CARCACAS.md);
 *       meat eaters scavenge it ({@link #scavenges()}) and are sated for a while afterwards.</li>
 *   <li><b>Hunger and sleep</b> (docs/FOME_E_SONO.md): every animal has a hunger gauge 0-100 that empties with
 *       time; herbivores graze it back, meat eaters eat carrion and kills, tame animals eat what they are fed (or
 *       their own cargo). Well fed animals heal; starving ones take damage; a fed predator does not hunt. Wild
 *       animals sleep through their resting hours ({@link #nocturnal()}).</li>
 *   <li><b>Herds and packs</b> (docs/BANDOS.md): wild adults keep a neighbour of their species within seven blocks
 *       (FollowHerdGoal); fleeing herds stampede together; pack hunters ({@link #packHunter()}) share a target.</li>
 *   <li><b>Wild nests</b> (docs/NINHOS.md): a wild, well fed adult with a mate nearby and room in the herd
 *       ({@link #wildPopulationCap()}) breeds on its own and lays a clutch of wild eggs ({@link #clutchSize()});
 *       a herd may spawn with an egg already laid. Wild eggs hatch wild babies and the herd guards them.
 *       Brooders ({@link #brooder()}) sit on eggs they find and eggs beside a sitting one hatch fast; egg thieves
 *       ({@link #eggThief()}) eat the wild clutches they find, and the herd turns on them.</li>
 *   <li><b>Migration</b> (docs/MIGRACAO.md): wild herbivore herds set off together for new grazing, 64 to 96
 *       blocks away in the season's direction (MigrateGoal, {@link #getMigrationTarget()}).</li>
 *   <li><b>Platform saddle</b>: species with {@link #platformSpecies()} take the platform saddle instead of a plain
 *       one; it seats four along the back, anyone may climb on, and the owner drives (docs/CARGA.md).</li>
 * </ul>
 */
public abstract class DinosaurEntity extends TamableAnimal implements GeoEntity, PlayerRideableJumping, HasCustomInventoryScreen {
    public static final String ACTION_CONTROLLER = "action";

    /** A wild nest decided in finalizeSpawn during world generation, laid on the first tick (docs/NINHOS.md). */
    private boolean pendingNest;
    private static final EntityDataAccessor<Boolean> DATA_FEMALE =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> DATA_SADDLED =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> DATA_CHESTED =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> DATA_PLATFORM =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> DATA_HUNGER =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_SLEEPING =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    public static final int MAX_HUNGER = 100;
    /** Below this a wild predator hunts; at or above it, it lets prey and players be. */
    public static final int HUNTS_BELOW = 85;
    /** Riders a platform saddle seats (the owner drives, the rest sit along the back). */
    public static final int PLATFORM_SEATS = 4;

    /** How a wild animal of this species can be tamed (eggs always work). */
    public enum TameMethod {
        /** Hand-feed its food: each bite has a 1 in {@link #tameChance()} chance. */
        FEEDING,
        /** Only babies accept food from players (predators). */
        BABY_FEEDING
    }

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    /** The cargo inventory (null when the species carries none); only reachable once a chest is strapped on. */
    private final SimpleContainer cargo;
    private RawAnimation idleAnim;
    private RawAnimation walkAnim;
    private RawAnimation runAnim;
    private RawAnimation sitAnim;
    private RawAnimation broodAnim;
    /** Whether it sits beside an egg right now (the brood pose; refreshed every ten ticks while it rests). */
    private boolean brooding;
    /** Jump asked by the rider (0..1), done on the next ridden tick on the ground. */
    private float riderJump;
    /** Ticks after perching during which the owner's sneak does not shake the animal off (it was sneaking to perch it). */
    private int perchGrace;
    /** Cooldown of the perched animal's danger warning. */
    private int perchWarnCooldown;
    /** While dying, the death loot is collected here for the carcass instead of being dropped. */
    private List<ItemStack> capturedLoot;
    /** Ticks a meat eater stays full after a meal (it does not hunt while sated). */
    private int sated;
    /** Ticks until the hunger gauge drops by one. */
    private int hungerTimer;
    /** Cooldown of the "is hungry" message to the owner. */
    private int hungryMessageCooldown;
    /** Where the herd is migrating to (MigrateGoal), or null; not saved: a reloaded herd settles where it is. */
    private BlockPos migrationTarget;

    protected DinosaurEntity(EntityType<? extends DinosaurEntity> type, Level level) {
        super(type, level);
        this.entityData.set(DATA_FEMALE, this.random.nextBoolean());
        this.cargo = this.cargoRows() > 0 ? new SimpleContainer(this.cargoRows() * 9) : null;
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

    /** Rows of nine cargo slots a tamed adult carries once a chest is strapped on; 0 = carries no cargo. */
    public int cargoRows() {
        return 0;
    }

    /** Ticks per point of hunger lost (the generator scales it with the species' size). */
    protected int hungerInterval() {
        return 600;
    }

    /** Whether the species rests by day and is up at night. */
    protected boolean nocturnal() {
        return false;
    }

    /** Whether it feeds itself from the ground: grass, ferns, leaves within reach (herbivores). */
    protected boolean grazes() {
        return false;
    }

    public int getHunger() {
        return this.entityData.get(DATA_HUNGER);
    }

    public void setHunger(int hunger) {
        this.entityData.set(DATA_HUNGER, Mth.clamp(hunger, 0, MAX_HUNGER));
    }

    /** Eats: the gauge goes up (never past full). */
    public void feed(int amount) {
        this.setHunger(this.getHunger() + amount);
    }

    public boolean isHungry() {
        return this.getHunger() < 50;
    }

    public boolean isStarving() {
        return this.getHunger() <= 0;
    }

    public boolean isSleeping() {
        return this.entityData.get(DATA_SLEEPING);
    }

    public void setSleeping(boolean sleeping) {
        this.entityData.set(DATA_SLEEPING, sleeping);
    }

    /** The species' resting hours: night for most, day for the nocturnal ones (never in the rain of a thunderstorm). */
    public boolean isSleepTime() {
        boolean day = this.level().isDay();
        return (this.nocturnal() ? day : !day) && !this.level().isThundering();
    }

    /** Whether a wild adult with a target brings the others of its species within 16 blocks onto it. */
    protected boolean packHunter() {
        return false;
    }

    /** Whether this animal eats carcasses (meat eaters). */
    protected boolean scavenges() {
        return false;
    }

    /** Whether it sits on eggs (docs/NINHOS.md): wild ones brood clutches they find (BroodGoal), it takes the "brood"
     *  pose sitting beside an egg, and eggs within two blocks of a sitting one hatch fast ({@link #broodEggs}). */
    protected boolean brooder() {
        return false;
    }

    /** Whether wild ones eat the dinosaur eggs they find (EggThiefGoal, docs/NINHOS.md): the Didelphodon. */
    protected boolean eggThief() {
        return false;
    }

    /** The nearest dinosaur egg block within r blocks (two up or down), or null. */
    public BlockPos nearestEgg(int r) {
        BlockPos here = this.blockPosition();
        BlockPos best = null;
        double bestDistance = Double.MAX_VALUE;
        for (BlockPos pos : BlockPos.betweenClosed(here.offset(-r, -2, -r), here.offset(r, 2, r))) {
            if (this.level().getBlockState(pos).getBlock() instanceof DinoEggBlock) {
                double distance = pos.distSqr(here);
                if (distance < bestDistance) {
                    bestDistance = distance;
                    best = pos.immutable();
                }
            }
        }
        return best;
    }

    /** Fast hatching: every eight seconds each egg block within two blocks of a sitting brooder gets an extra random
     *  tick (one in two advances a hatch stage), so a clutch hatches in about a minute instead of several. */
    private void broodEggs(ServerLevel server) {
        BlockPos here = this.blockPosition();
        for (BlockPos pos : BlockPos.betweenClosed(here.offset(-2, -1, -2), here.offset(2, 1, 2))) {
            BlockState state = server.getBlockState(pos);
            if (state.getBlock() instanceof DinoEggBlock) {
                state.randomTick(server, pos.immutable(), this.random);
            }
        }
    }

    /** Whether the wild ones of this species breed and nest on their own (land animals; the sea comes in v0.8). */
    protected boolean wildNests() {
        return true;
    }

    /** How many wild ones of the species may live within 32 blocks before they stop breeding: fewer the bigger. */
    protected int wildPopulationCap() {
        float w = this.getType().getWidth();
        return w >= 4.0F ? 3 : w >= 2.0F ? 5 : w >= 1.0F ? 8 : 12;
    }

    /** Eggs in a wild clutch: one for the giants, two for the mid-sized, three for the small. */
    protected int clutchSize() {
        float w = this.getType().getWidth();
        return w >= 3.0F ? 1 : w >= 1.2F ? 2 : 3;
    }

    /** Bites of carrion that fill this animal up (then it is sated for a few minutes). */
    public int carcassFill() {
        return 2 + Math.round(this.getBbWidth() * 2.0F);
    }

    public boolean isSated() {
        return this.sated > 0;
    }

    public void setSated(int ticks) {
        this.sated = ticks;
    }

    /** Called when it bites a carcass: the eating animation, and a good share of the gauge. */
    public void onAteCarrion() {
        triggerAnim(ACTION_CONTROLLER, "eat");
        this.feed(20);
    }

    /** Whether the species takes the platform saddle (the titans): four riders, anyone may climb on. */
    protected boolean platformSpecies() {
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

    /** Wild predators only hunt when grown up, awake, hungry (not sated, gauge below HUNTS_BELOW) and off Peaceful. */
    protected boolean canHunt() {
        return !this.isBaby() && !this.isTame() && !this.isSated() && !this.isSleeping() && this.getHunger() < HUNTS_BELOW
                && this.level().getDifficulty() != Difficulty.PEACEFUL;
    }

    // ------------------------------------------------------------------ synced data / save

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_FEMALE, false);
        this.entityData.define(DATA_SADDLED, false);
        this.entityData.define(DATA_CHESTED, false);
        this.entityData.define(DATA_PLATFORM, false);
        this.entityData.define(DATA_HUNGER, 70);
        this.entityData.define(DATA_SLEEPING, false);
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

    /** True once a chest is strapped on (the cargo inventory is open for business). */
    public boolean isChested() {
        return this.entityData.get(DATA_CHESTED);
    }

    public void setChested(boolean chested) {
        this.entityData.set(DATA_CHESTED, chested);
    }

    /** True while the saddle on it is the platform saddle. */
    public boolean isPlatform() {
        return this.entityData.get(DATA_PLATFORM);
    }

    public void setPlatform(boolean platform) {
        this.entityData.set(DATA_PLATFORM, platform);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Female", this.isFemale());
        tag.putBoolean("Saddled", this.isSaddled());
        if (this.pendingNest) {
            tag.putBoolean("PendingNest", true);
        }
        tag.putBoolean("Chested", this.isChested());
        tag.putBoolean("Platform", this.isPlatform());
        tag.putInt("Sated", this.sated);
        tag.putInt("Hunger", this.getHunger());
        if (this.cargo != null) {
            ListTag list = new ListTag();
            for (int i = 0; i < this.cargo.getContainerSize(); i++) {
                ItemStack stack = this.cargo.getItem(i);
                if (!stack.isEmpty()) {
                    CompoundTag item = new CompoundTag();
                    item.putByte("Slot", (byte) i);
                    stack.save(item);
                    list.add(item);
                }
            }
            tag.put("Cargo", list);
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Female")) {
            this.setFemale(tag.getBoolean("Female"));
        }
        this.setSaddled(tag.getBoolean("Saddled"));
        this.pendingNest = tag.getBoolean("PendingNest");
        this.setChested(tag.getBoolean("Chested"));
        this.setPlatform(tag.getBoolean("Platform"));
        this.sated = tag.getInt("Sated");
        if (tag.contains("Hunger")) {
            this.setHunger(tag.getInt("Hunger"));
        }
        if (this.cargo != null && tag.contains("Cargo", Tag.TAG_LIST)) {
            ListTag list = tag.getList("Cargo", Tag.TAG_COMPOUND);
            for (int i = 0; i < list.size(); i++) {
                CompoundTag item = list.getCompound(i);
                int slot = item.getByte("Slot") & 255;
                if (slot < this.cargo.getContainerSize()) {
                    this.cargo.setItem(slot, ItemStack.of(item));
                }
            }
        }
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        SpawnGroupData spawnData, CompoundTag tag) {
        this.setFemale(this.random.nextBoolean());
        SpawnGroupData data = super.finalizeSpawn(level, difficulty, reason, spawnData, tag);
        // one herd in five spawns with a nest already laid next to a grown female (docs/NINHOS.md)
        if ((reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) && this.wildNests() && !this.isBaby()
                && this.isFemale() && this.random.nextInt(5) == 0) {
            if (level instanceof WorldGenRegion) {
                this.pendingNest = true;  // nothing can be placed while the chunk generates: lay it on the first tick
            } else {
                this.layWildEgg(level);
            }
        }
        return data;
    }

    // ------------------------------------------------------------------ GeckoLib

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        this.idleAnim = RawAnimation.begin().thenLoop(anim("idle"));
        this.walkAnim = RawAnimation.begin().thenLoop(anim("walk"));
        this.runAnim = RawAnimation.begin().thenLoop(anim("run"));
        this.sitAnim = RawAnimation.begin().thenLoop(anim("sit"));
        this.broodAnim = RawAnimation.begin().thenLoop(anim("brood"));

        controllers.add(new AnimationController<>(this, "movement", 6, this::movementAnimation));

        AnimationController<DinosaurEntity> action = new AnimationController<>(this, ACTION_CONTROLLER, 3, state -> PlayState.STOP);
        action.triggerableAnim("attack", RawAnimation.begin().thenPlay(anim("attack")));
        action.triggerableAnim("eat", RawAnimation.begin().thenPlay(anim("eat")));
        action.triggerableAnim("beg", RawAnimation.begin().thenPlay(anim("beg")));
        for (String extra : extraActions()) {
            action.triggerableAnim(extra, RawAnimation.begin().thenPlay(anim(extra)));
        }
        controllers.add(action);
    }

    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.isPerched() || this.isSleeping() || (this.isInSittingPose() && !this.isVehicle())) {
            if (this.brooder() && this.tickCount % 10 == 0) {
                this.brooding = !this.isBaby() && this.nearestEgg(2) != null;
            }
            return state.setAndContinue(this.brooder() && this.brooding ? this.broodAnim : this.sitAnim);
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
        // the gear drops where the animal fell, not inside the carcass
        List<ItemStack> hold = this.capturedLoot;
        this.capturedLoot = null;
        super.dropEquipment();
        if (this.isSaddled()) {
            this.spawnAtLocation(this.saddleItem());
        }
        this.dropCargo();
        this.capturedLoot = hold;
    }

    // ------------------------------------------------------------------ death: the carcass

    /** The death loot goes into a carcass (docs/CARCACAS.md) instead of flying out of the body. */
    @Override
    protected void dropAllDeathLoot(DamageSource source) {
        if (!(this.level() instanceof ServerLevel server)) {
            super.dropAllDeathLoot(source);
            return;
        }
        this.capturedLoot = new ArrayList<>();
        List<ItemStack> loot;
        try {
            super.dropAllDeathLoot(source);
        } finally {
            loot = this.capturedLoot;
            this.capturedLoot = null;
        }
        server.addFreshEntity(CarcassEntity.of(server, this, loot));
    }

    @Override
    public ItemEntity spawnAtLocation(ItemStack stack, float yOffset) {
        if (this.capturedLoot != null) {
            if (!stack.isEmpty()) {
                this.capturedLoot.add(stack.copy());
            }
            return null;
        }
        return super.spawnAtLocation(stack, yOffset);
    }

    /** The saddle item this animal wears (plain saddle or the platform saddle). */
    protected ItemStack saddleItem() {
        return new ItemStack(this.isPlatform() ? ModItems.PLATFORM_SADDLE.get() : Items.SADDLE);
    }

    // ------------------------------------------------------------------ cargo

    /** Takes the chest off and drops it with everything in it. */
    protected void dropCargo() {
        if (!this.isChested()) {
            return;
        }
        this.setChested(false);
        this.spawnAtLocation(Items.CHEST);
        if (this.cargo != null && !this.level().isClientSide()) {
            Containers.dropContents(this.level(), this, this.cargo);
        }
    }

    /** Opens the cargo as a plain chest screen of {@link #cargoRows()} rows. */
    protected void openCargo(Player player) {
        if (this.cargo == null) {
            return;
        }
        int rows = this.cargoRows();
        player.openMenu(new SimpleMenuProvider((id, inventory, p) -> new ChestMenu(cargoMenuType(rows), id, inventory, this.cargo, rows),
                this.getDisplayName()));
        this.playSound(SoundEvents.DONKEY_CHEST, 0.5F, 1.2F);
    }

    /** The generic chest menu of that many rows (only threeRows/sixRows take a container in 1.20.1, so build it directly). */
    private static MenuType<ChestMenu> cargoMenuType(int rows) {
        return switch (rows) {
            case 1 -> MenuType.GENERIC_9x1;
            case 2 -> MenuType.GENERIC_9x2;
            case 3 -> MenuType.GENERIC_9x3;
            case 4 -> MenuType.GENERIC_9x4;
            case 5 -> MenuType.GENERIC_9x5;
            default -> MenuType.GENERIC_9x6;
        };
    }

    /** The inventory key while riding opens the cargo (vanilla sends OPEN_INVENTORY for a HasCustomInventoryScreen vehicle). */
    @Override
    public void openCustomInventoryScreen(Player player) {
        if (!this.level().isClientSide() && this.isChested() && this.isTame() && this.isOwnedBy(player)) {
            this.openCargo(player);
        }
    }

    /** A pack animal up and about picks up the drops around its feet: what it, or its owner, harvested. */
    private void collectCargo() {
        for (ItemEntity item : this.level().getEntitiesOfClass(ItemEntity.class, this.getBoundingBox().inflate(1.0D, 0.5D, 1.0D))) {
            if (!item.isAlive() || item.hasPickUpDelay()) {
                continue;
            }
            ItemStack stack = item.getItem();
            int before = stack.getCount();
            ItemStack rest = this.cargo.addItem(stack);
            if (rest.getCount() < before) {
                this.take(item, before - rest.getCount());
                if (rest.isEmpty()) {
                    item.discard();
                } else {
                    item.setItem(rest);
                }
                this.playSound(SoundEvents.ITEM_PICKUP, 0.3F, 1.0F + (this.random.nextFloat() - 0.5F) * 0.4F);
            }
        }
    }

    // ------------------------------------------------------------------ taming / interaction

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean client = this.level().isClientSide();

        // anyone may climb onto a platform saddle as a passenger (only the owner drives)
        if (this.isTame() && this.isPlatform() && !this.isOwnedBy(player) && !this.isBaby() && stack.isEmpty()
                && !player.isSecondaryUseActive() && !player.isPassenger() && this.canAddPassenger(player)) {
            if (!client) {
                player.startRiding(this);
            }
            return InteractionResult.sidedSuccess(client);
        }

        if (this.isTame() && this.isOwnedBy(player)) {
            // feed: food heals and fills the hunger gauge
            if (this.isFood(stack) && (this.getHealth() < this.getMaxHealth() || this.getHunger() < MAX_HUNGER - 10)) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.heal(Math.max(2.0F, this.getMaxHealth() * 0.1F));
                    this.feed(25);
                    triggerAnim(ACTION_CONTROLLER, "eat");
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
            // a chest strapped on makes a pack animal of it (the cargo inventory, docs/CARGA.md)
            if (this.cargo != null && !this.isBaby() && !this.isChested() && stack.is(Items.CHEST)) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.setChested(true);
                    this.playSound(SoundEvents.DONKEY_CHEST, 1.0F, 1.0F);
                    player.displayClientMessage(Component.translatable(this.isRideable() ? "message.terrassic.cargo_chest_ride"
                            : "message.terrassic.cargo_chest", this.getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // without a saddle, sneak + empty hand opens the cargo (saddled: mount it and press the inventory key)
            if (this.isChested() && !this.isSaddled() && stack.isEmpty() && player.isSecondaryUseActive()) {
                if (!client) {
                    this.openCargo(player);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // the platform saddle of the titans (docs/CARGA.md)
            if (this.platformSpecies() && !this.isBaby() && !this.isSaddled() && stack.is(ModItems.PLATFORM_SADDLE.get())) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.setSaddled(true);
                    this.setPlatform(true);
                    this.playSound(SoundEvents.HORSE_SADDLE, 1.0F, 0.7F);
                    player.displayClientMessage(Component.translatable("message.terrassic.platform", this.getDisplayName()), true);
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
                    this.spawnAtLocation(this.saddleItem());
                    this.setSaddled(false);
                    this.setPlatform(false);
                    this.playSound(SoundEvents.SHEEP_SHEAR, 1.0F, 1.0F);
                    stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
                }
                return InteractionResult.sidedSuccess(client);
            }
            // shears again take the chest off (with its contents)
            if (this.isChested() && !this.isSaddled() && stack.is(Items.SHEARS)) {
                if (!client) {
                    this.dropCargo();
                    this.playSound(SoundEvents.SHEEP_SHEAR, 1.0F, 1.0F);
                    stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
                    player.displayClientMessage(Component.translatable("message.terrassic.cargo_off", this.getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            if (stack.isEmpty()) {
                // ride (saddled) or toggle sit / follow (sneak, or not saddled)
                if (this.isSaddled() && !this.isBaby() && !player.isSecondaryUseActive() && this.canAddPassenger(player)) {
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
        if (this.pendingNest && !this.level().isClientSide()) {
            this.pendingNest = false;
            this.layWildEgg(this.level());
        }
        if (this.isPerched()) {
            this.perchedTick((Player) this.getVehicle());
        }
        if (!this.level().isClientSide() && this.cargo != null && this.isChested() && this.isTame() && this.isAlive()
                && !this.isInSittingPose() && this.tickCount % 10 == 0) {
            this.collectCargo();
        }
        if (!this.level().isClientSide() && this.sated > 0) {
            this.sated--;
        }
        if (!this.level().isClientSide() && this.isAlive()) {
            this.hungerTick();
            if (this.tickCount % 200 == 0) {
                this.wildBreedingTick();
            }
            if (this.brooder() && this.tickCount % 160 == 0 && !this.isBaby() && (this.isInSittingPose() || this.isSleeping())
                    && this.level() instanceof ServerLevel server) {
                this.broodEggs(server);
            }
        }
    }

    // ------------------------------------------------------------------ hunger (docs/FOME_E_SONO.md)

    private void hungerTick() {
        // the gauge empties with time (twice as fast for a growing baby)
        if (--this.hungerTimer <= 0) {
            this.hungerTimer = this.isBaby() ? this.hungerInterval() / 2 : this.hungerInterval();
            // a wild animal out of sight finds something to eat now and then, so the wild never starves offscreen
            if (!this.isTame() && this.random.nextInt(4) == 0) {
                this.feed(1);
            } else {
                this.setHunger(this.getHunger() - 1);
            }
        }
        // a chested animal helps itself to its own cargo when hungry
        if (this.isHungry() && this.cargo != null && this.isChested() && this.tickCount % 100 == 0) {
            for (int i = 0; i < this.cargo.getContainerSize(); i++) {
                ItemStack stack = this.cargo.getItem(i);
                if (!stack.isEmpty() && this.isFood(stack)) {
                    stack.shrink(1);
                    this.feed(25);
                    triggerAnim(ACTION_CONTROLLER, "eat");
                    this.playSound(SoundEvents.GENERIC_EAT, 1.0F, 1.0F);
                    break;
                }
            }
        }
        // well fed: it heals; starving: it suffers
        if (this.getHunger() > 60 && this.getHealth() < this.getMaxHealth() && this.tickCount % 400 == 0) {
            this.heal(1.0F);
        }
        if (this.isStarving() && this.tickCount % 400 == 0) {
            this.hurt(this.damageSources().starve(), 1.0F);
        }
        // a hungry tame animal begs its owner
        if (this.hungryMessageCooldown > 0) {
            this.hungryMessageCooldown--;
        }
        if (this.isTame() && this.getHunger() < 30 && this.tickCount % 200 == 0 && this.getOwner() instanceof Player owner
                && owner.distanceToSqr(this) < 64.0D) {
            triggerAnim(ACTION_CONTROLLER, "beg");
            if (this.hungryMessageCooldown == 0) {
                this.hungryMessageCooldown = 2400;
                owner.displayClientMessage(Component.translatable("message.terrassic.hungry", this.getDisplayName()), true);
            }
        }
    }

    public BlockPos getMigrationTarget() {
        return this.migrationTarget;
    }

    public void setMigrationTarget(BlockPos target) {
        this.migrationTarget = target;
    }

    /** Grazing animals eat what grows within reach: grass, ferns, leaves, the grass block itself. */
    public boolean grazeNearby() {
        BlockPos centre = this.blockPosition();
        int r = Math.max(1, Math.round(this.getBbWidth() * 0.6F));
        for (BlockPos pos : BlockPos.betweenClosed(centre.offset(-r, -1, -r), centre.offset(r, 2, r))) {
            BlockState state = this.level().getBlockState(pos);
            if (state.is(Blocks.GRASS_BLOCK) || state.is(Blocks.GRASS) || state.is(Blocks.TALL_GRASS) || state.is(Blocks.FERN)
                    || state.is(Blocks.LARGE_FERN) || state.is(BlockTags.LEAVES) || state.is(BlockTags.SAPLINGS) || state.is(Blocks.MOSS_BLOCK)) {
                return true;
            }
        }
        return false;
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

    /** A plain saddle seats one; the platform saddle seats {@link #PLATFORM_SEATS}. */
    @Override
    protected boolean canAddPassenger(Entity passenger) {
        return this.getPassengers().size() < (this.isPlatform() ? PLATFORM_SEATS : 1);
    }

    /** The rider drives; on a platform only the owner does, wherever they sit (nobody aboard = the animal walks itself). */
    @Override
    public LivingEntity getControllingPassenger() {
        if (this.isSaddled()) {
            for (Entity e : this.getPassengers()) {
                if (e instanceof Player player && (!this.isPlatform() || this.isOwnedBy(player))) {
                    return player;
                }
            }
            if (this.isPlatform()) {
                return null;
            }
        }
        return super.getControllingPassenger();
    }

    @Override
    public void positionRider(Entity passenger, Entity.MoveFunction move) {
        if (!this.hasPassenger(passenger)) {
            return;
        }
        double forward = this.riderForwardOffset() * this.getScale();
        // the platform's seats run back along the spine from the saddle, a third of the body width apart
        int seat = this.getPassengers().indexOf(passenger);
        if (seat > 0) {
            forward -= seat * this.getBbWidth() * 0.35D;
        }
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

    /**
     * Wild breeding (docs/NINHOS.md), checked every ten seconds with a one in twelve chance: a wild, grown, well
     * fed (gauge 80+), awake, idle animal whose species has room nearby looks for a wild mate of the other sex in the
     * same state within 16 blocks, and both fall in love; the vanilla BreedGoal does the rest.
     */
    private void wildBreedingTick() {
        if (this.isTame() || this.isBaby() || !this.wildNests() || !this.canFallInLove() || this.getAge() != 0
                || this.getHunger() < 80 || this.isSleeping() || this.getTarget() != null || this.isVehicle()
                || this.random.nextInt(12) != 0 || !(this.level() instanceof ServerLevel level)) {
            return;
        }
        if (level.getEntitiesOfClass(this.getClass(), this.getBoundingBox().inflate(32.0D), e -> !e.isTame()).size()
                >= this.wildPopulationCap()) {
            return;
        }
        DinosaurEntity mate = null;
        double best = Double.MAX_VALUE;
        for (DinosaurEntity other : level.getEntitiesOfClass(this.getClass(), this.getBoundingBox().inflate(16.0D),
                e -> e != this && !e.isTame() && !e.isBaby() && e.isFemale() != this.isFemale() && e.canFallInLove()
                        && e.getAge() == 0 && e.getHunger() >= 80 && !e.isSleeping() && e.getTarget() == null && !e.isVehicle())) {
            double d = this.distanceToSqr(other);
            if (d < best) {
                best = d;
                mate = other;
            }
        }
        if (mate != null) {
            this.setInLove(null);
            mate.setInLove(null);
        }
    }

    /** Lays one wild egg next to the animal (a nest found with a herd, or a clutch). */
    protected boolean layWildEgg(LevelAccessor level) {
        Block egg = ModBlocks.eggFor(this.speciesId());
        if (egg == null) {
            return false;
        }
        BlockPos pos = findEggSpot(level, this.blockPosition());
        if (pos == null) {
            return false;
        }
        BlockState state = egg.defaultBlockState();
        if (state.hasProperty(DinoEggBlock.WILD)) {
            state = state.setValue(DinoEggBlock.WILD, true);
        }
        return level.setBlock(pos, state, Block.UPDATE_ALL);
    }

    @Override
    public void spawnChildFromBreeding(ServerLevel level, Animal partner) {
        Block egg = ModBlocks.eggFor(this.speciesId());
        if (egg == null) {
            super.spawnChildFromBreeding(level, partner);
            return;
        }
        DinosaurEntity mother = partner instanceof DinosaurEntity d && d.isFemale() ? d : this;
        if (!mother.isTame() && !this.isTame()) {
            // a wild couple lays a clutch of wild eggs and the two of them spend some of their reserves on it
            int laid = 0;
            for (int i = 0; i < mother.clutchSize(); i++) {
                if (mother.layWildEgg(level)) {
                    laid++;
                }
            }
            if (laid > 0) {
                level.playSound(null, mother.blockPosition(), SoundEvents.TURTLE_LAY_EGG, SoundSource.BLOCKS, 0.7F, 0.9F);
            }
            this.setHunger(this.getHunger() - 15);
            if (partner instanceof DinosaurEntity other) {
                other.setHunger(other.getHunger() - 15);
            }
        } else {
            BlockPos pos = findEggSpot(level, mother.blockPosition());
            if (pos != null) {
                level.setBlock(pos, egg.defaultBlockState(), Block.UPDATE_ALL);
                level.playSound(null, pos, SoundEvents.TURTLE_LAY_EGG, SoundSource.BLOCKS, 0.7F, 0.9F);
            } else {
                mother.spawnAtLocation(egg);
            }
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

    private static BlockPos findEggSpot(LevelAccessor level, BlockPos center) {
        // While a chunk is generating (mobs spawned with it), the level is a WorldGenRegion: reading or writing outside
        // that chunk crashes the game ("asking a region for a chunk out of bound"), so the egg stays in it.
        // Otherwise only chunks that are loaded are looked at.
        boolean worldgen = level instanceof WorldGenRegion;
        int cx = center.getX() >> 4;
        int cz = center.getZ() >> 4;
        for (int r = 1; r <= 3; r++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    for (int dy = 1; dy >= -1; dy--) {
                        BlockPos pos = center.offset(dx, dy, dz);
                        int px = pos.getX() >> 4;
                        int pz = pos.getZ() >> 4;
                        if (worldgen ? (px != cx || pz != cz) : !level.hasChunk(px, pz)) {
                            continue;
                        }
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
