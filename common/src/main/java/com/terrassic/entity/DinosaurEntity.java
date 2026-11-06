package com.terrassic.entity;

import com.terrassic.Terrassic;
import com.terrassic.entity.parts.DinoPart;
import com.terrassic.entity.parts.PartOwners;
import com.terrassic.mixin.parts.AbstractArrowInvoker;
import com.terrassic.mixin.parts.EntityCounterAccessor;
import com.terrassic.registry.ModSounds;
import com.terrassic.block.DinoEggBlock;
import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import com.terrassic.config.WorldConfig;
import com.terrassic.world.VanillaShare;
import com.terrassic.network.ModNetwork;
import com.terrassic.registry.ModBlocks;
import com.terrassic.registry.ModItems;
import com.terrassic.research.Objective;
import com.terrassic.research.Research;
import com.terrassic.entity.ai.AggressiveStanceGoal;
import dev.architectury.event.EventResult;
import dev.architectury.event.events.common.EntityEvent;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetPassengersPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
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
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.HasCustomInventoryScreen;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.PlayerRideableJumping;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import com.terrassic.item.ClubItem;
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
import java.util.UUID;

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
 *   <li><b>Size</b> (docs/TAMANHOS.md): every animal rolls its own adult size between {@link #minSize()} and
 *       {@link #maxSize()} of the species' standard (most near the middle, extremes rare), and every baby hatches
 *       at its own size and grows smoothly into its adult size. Hitbox, model, rider seat and carcass follow the
 *       size; health grows with its square and bite damage with it. Saved as "Size" and "BirthSize".</li>
 *   <li><b>Platform saddle</b>: species with {@link #platformSpecies()} take the platform saddle instead of a plain
 *       one; it seats four along the back, anyone may climb on, and the owner drives (docs/CARGA.md).</li>
 *   <li><b>World rules</b> (docs/REGRAS.md): damage, resistance, wild strength, taming, XP, hunger, hatching,
 *       growth, mating and nests follow the world's {@link Rules}. Animals placed by the ecosystem spawner
 *       ({@link #isRoamer()}) despawn once every player is far away, unless tamed or named.</li>
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
    /** A creature "of the Rift" (v0.9): amber cracks and eyes glowing on the model (client/RiftLayer). */
    private static final EntityDataAccessor<Boolean> DATA_RIFT =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    /** Unconscious from torpor (knockout taming, docs/DOMESTICACAO.md); synced for the knocked_out pose. */
    private static final EntityDataAccessor<Boolean> DATA_KNOCKED_OUT =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    /** Tied by a bola (v1.1, docs/ARMAS.md); synced so the rider's client stops steering and the thongs are drawn. */
    private static final EntityDataAccessor<Boolean> DATA_ENTANGLED =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    /** Narcotic darts stuck in its hide (v1.1.4, docs/ARMAS.md); arrows use the vanilla arrow count. Drawn by
     *  client/StuckProjectilesLayer. */
    private static final EntityDataAccessor<Integer> DATA_STUCK_DARTS =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.INT);
    /** 1.7: where each stuck dart went in, 2 bits per dart, the newest in the lowest bits (DinoPart.Kind#zone). */
    private static final EntityDataAccessor<Integer> DATA_DART_ZONES =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_HUNGER =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_SLEEPING =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    /** Adult size relative to the species' standard (1.0 = the SIZES row of gen_species.py). */
    private static final EntityDataAccessor<Float> DATA_SIZE =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.FLOAT);
    /** Hatchling size relative to the species' babyScale() (0.8 - 1.2). */
    private static final EntityDataAccessor<Float> DATA_BIRTH_SIZE =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.FLOAT);
    /** How far a baby has grown, 0 (hatchling) to 1 (adult); refreshed by the server as it ages. */
    private static final EntityDataAccessor<Float> DATA_GROWTH =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.FLOAT);
    private static final UUID SIZE_HEALTH_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e301");
    private static final UUID SIZE_DAMAGE_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e302");
    /** The level's stats (DinoLevels): one id per stat, the same id on walking and flying speed. */
    private static final UUID LEVEL_HEALTH_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e311");
    private static final UUID LEVEL_DAMAGE_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e312");
    private static final UUID LEVEL_SPEED_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e313");
    /** An alpha (docs/ALFAS.md, entity/Alphas): bigger, stronger, its own coat; synced for the texture and the tremor. */
    private static final EntityDataAccessor<Boolean> DATA_ALPHA =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.BOOLEAN);
    private static final UUID ALPHA_HEALTH_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e321");
    private static final UUID ALPHA_DAMAGE_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e322");
    private static final UUID ALPHA_CROWD_ID = UUID.fromString("2f6c9b84-1d3e-4a57-9c08-5be1a7d4e323");
    /** The level, synced for the name (0 until the server has drawn it). */
    private static final EntityDataAccessor<Integer> DATA_LEVEL =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.INT);
    /** The rider's special for the HUD's key socket (v0.14): ticks until ready in the high 16 bits, the full recharge
     *  in the low 16 (0 = no special). Updated while someone rides it. */
    private static final EntityDataAccessor<Integer> DATA_SPECIAL =
            SynchedEntityData.defineId(DinosaurEntity.class, EntityDataSerializers.INT);
    /** Ticks a baby takes to grow up (vanilla age counter). */
    private static final float GROW_TICKS = 24000.0F;
    public static final int MAX_HUNGER = 100;
    /** Below this a wild predator hunts; at or above it, it lets prey and players be. */
    public static final int HUNTS_BELOW = 85;
    /** Riders a platform saddle seats (the owner drives, the rest sit along the back). */
    public static final int PLATFORM_SEATS = 4;
    /** Squared distance to the nearest player beyond which a wild roamer may despawn. */
    private static final double ROAMER_DESPAWN_SQR = 96.0D * 96.0D;

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

    /** How it meets a fight (v0.16, docs/ORDENS.md); saved as "Stance". */
    private DinoStance stance = DinoStance.NEUTRAL;
    /** Where it was told to wander (null = it follows or waits); saved as "WanderPos". */
    private BlockPos wanderPos;
    /** Game time until which a "Stop" keeps it out of fights (not saved: ten seconds). */
    private long calmUntil = Long.MIN_VALUE;
    /** Cooldown of the perched animal's danger warning. */
    private int perchWarnCooldown;
    /** While dying, the death loot is collected here for the carcass instead of being dropped. */
    private List<ItemStack> capturedLoot;
    /** Species with a death animation: the death loot waits here until the animation ends and the carcass is laid. */
    private List<ItemStack> pendingCarcassLoot;
    /** Ticks a meat eater stays full after a meal (it does not hunt while sated). */
    private int sated;
    /** Ticks until the hunger gauge drops by one. */
    private int hungerTimer;
    /** Cooldown of the "is hungry" message to the owner. */
    private int hungryMessageCooldown;
    /** Where the herd is migrating to (MigrateGoal), or null; not saved: a reloaded herd settles where it is. */
    private BlockPos migrationTarget;
    /** Placed by the ecosystem spawner (EcoSpawner): despawns when far from every player while wild and unnamed. */
    private boolean roamer;
    /** Knockout taming (docs/DOMESTICACAO.md): torpor fills with blunt blows and narcotics and drains over time;
     *  full, the animal collapses. Fed while unconscious it builds taming progress; every wound taken meanwhile costs
     *  effectiveness, which sets the health bonus it wakes up with. Server side only (the pose is synced). */
    private float torpor;
    private float tameProgress;
    private int tameEffectiveness = 100;
    private UUID tamer;
    /** 1.7: game time until which a knocked-out animal does not drain torpor (it is being fed). Not saved. */
    private long eatingUntil = Long.MIN_VALUE;
    /** 1.7: how long one bite keeps a knocked-out animal from waking (ticks): holding use feeds every 4 ticks. */
    private static final long EATING_HOLD_TICKS = 40L;
    /** 1.7: mobs it may fight even where the world rules spare them (they hit it or its owner, or the owner ordered
     *  the attack), with the game time the leave runs out. Not saved. */
    private final java.util.Map<UUID, Long> provoked = new java.util.HashMap<>();
    private static final long PROVOKED_TICKS = 600L;
    private RawAnimation knockedOutAnim;
    private RawAnimation deathAnim;
    private RawAnimation sleepAnim;
    private RawAnimation swimAnim;
    /** Client: playback speed of the walk / run cycle, following the real ground speed (see {@link #walkCycleSpeed()}). */
    protected double cycleSpeed = 1.0D;
    /** Client: hurtTime seen by the flinch controller on the previous frame (a higher value means a new hit). */
    private int lastFlinch;
    /** Levels and stat points (DinoLevels, docs/NIVEIS.md); a new animal draws them on its first server tick. */
    private final DinoLevels levels;
    /** Loaded from a save made before the levels: a tame animal keeps its stats, a wild one draws a level. */
    private boolean legacyLevels;
    /** Where the owner was riding it last tick, and the distance carried since the last point of experience. */
    private Vec3 ridePos;
    private double rideDistance;

    protected DinosaurEntity(EntityType<? extends DinosaurEntity> type, Level level) {
        super(type, level);
        DinoPart.Spec[] specs = this.partSpecs();
        this.parts = new DinoPart[specs.length];
        for (int i = 0; i < specs.length; i++) {
            this.parts[i] = new DinoPart(this, specs[i]);
        }
        if (specs.length > 0) {
            // a block of ids: the creature's, then one per part (the client rebuilds the same ones in setId)
            this.setId(EntityCounterAccessor.terrassic$counter().getAndAdd(specs.length + 1) + 1);
        }
        this.moveControl = new com.terrassic.entity.ai.DinosaurMoveControl(this);
        if (!level.isClientSide()) {
            // server only: "male" is the default value, which is never sent, so a sex rolled on the client stayed
            this.entityData.set(DATA_FEMALE, this.random.nextBoolean());
            this.rollSize();
        }
        this.cargo = this.cargoRows() > 0 ? new SimpleContainer(this.cargoRows() * 9) : null;
        AttributeInstance health = this.getAttribute(Attributes.MAX_HEALTH);
        AttributeInstance damage = this.getAttribute(Attributes.ATTACK_DAMAGE);
        this.levels = new DinoLevels(DinoLevels.weightsFor(health != null ? health.getBaseValue() : 20.0D,
                damage != null ? damage.getBaseValue() : 0.0D));
        if (!level.isClientSide()) {
            // registered here and not in each registerGoals, so every species (generated or by hand) has it
            this.targetSelector.addGoal(4, new AggressiveStanceGoal(this));
        }
    }

    // ------------------------------------------------------------------ big walkers (v0.11)
    //
    // The fixes of the T. rex v2 tests (29/10), for every land animal they apply to: a wide animal turns slowly
    // (DinosaurMoveControl), so a waypoint beside or behind it sits inside its turning circle and it walked round it
    // for ever (the bite that walked away, the circling at the foot of stairs); afloat, its feet are too deep to reach
    // the path's nodes laid on the water surface (it spun in the water).

    /** From this width (blocks) a land animal floats chest-deep and paddles in deep water. */
    public static final float BIG_WIDTH = 2.0F;

    /** A land animal on vanilla ground paths: not a flyer, a swimmer or the amphibious Deinosuchus. */
    protected boolean walksOnGroundPaths() {
        return this.getNavigation() instanceof GroundPathNavigation;
    }

    /** Its turn rate is limited by its width (wider than 1 block), so it turns on the spot instead of circling. */
    public boolean pivotsToTurn() {
        return this.walksOnGroundPaths() && this.getBbWidth() > 1.0F;
    }

    /** A big land animal: chest-deep in deep water, legs paddling, instead of bobbing on the surface. */
    protected boolean wadesDeep() {
        return this.walksOnGroundPaths() && this.getBbWidth() >= BIG_WIDTH;
    }

    @Override
    public double getFluidJumpThreshold() {
        return this.wadesDeep() ? this.getBbHeight() * 0.5D : super.getFluidJumpThreshold();
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.duelTick();
        // 1.8 (found in the behaviour test): a herd member set on a target by the alarm keeps it after it dies, since no
        // target goal of its own is running to drop it; a dead target blocked hand taming forever (canBeTamedNow)
        LivingEntity target = this.getTarget();
        if (target != null && (!target.isAlive() || target.isRemoved())) {
            this.setTarget(null);
        }
        this.ordersTick();
        if (!this.pivotsToTurn()) {
            return;
        }
        Path path = this.getNavigation().getPath();
        // a fresh path starts at the block it stands on; on a stair or a slab edge that block can be behind it, and
        // going back to it (a pivot, a step up, a pivot, the step down) it rocked on the bottom step (rc3c stairs
        // test): a first node it is already past is skipped, as vanilla does for small mobs within 2 blocks
        if (path != null && !path.isDone() && path.getNextNodeIndex() == 0 && path.getNodeCount() > 1) {
            Vec3 first = path.getEntityPosAtNode(this, 0);
            Vec3 second = path.getEntityPosAtNode(this, 1);
            if (Mth.square(second.x - this.getX()) + Mth.square(second.z - this.getZ())
                    < Mth.square(second.x - first.x) + Mth.square(second.z - first.z)) {
                path.advance();
            }
        }
        // afloat chest-deep its feet are more than a block under the path's nodes (laid on the water surface), so vanilla
        // never counts one as reached and it paddled round the first: here a node counts when it is over it
        if (path != null && !path.isDone() && this.isInWater() && !this.onGround()) {
            Vec3 node = path.getNextEntityPos(this);
            double r = this.getBbWidth() / 2.0D + 0.5D;
            if (Mth.square(node.x - this.getX()) + Mth.square(node.z - this.getZ()) < r * r) {
                path.advance();
            }
        }
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
        boolean was = this.entityData.get(DATA_SLEEPING);
        this.entityData.set(DATA_SLEEPING, sleeping);
        if (was && !sleeping && this.hasSleepAnim() && this.isAlive() && !this.isKnockedOut() && !this.level().isClientSide()) {
            triggerAnim(ACTION_CONTROLLER, "wake_sleep");
        }
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

    /** Ground speed (blocks per tick, at size 1.0) one cycle of the "walk" animation covers. Above 0 the cycle plays
     *  faster or slower with the animal's real speed, so the feet do not slide; 0 = always at its authored speed. */
    protected double walkCycleSpeed() {
        return 0.0D;
    }

    /** Same as {@link #walkCycleSpeed()} for the "run" cycle. */
    protected double runCycleSpeed() {
        return 0.0D;
    }

    /** Ticks of the species' "death" animation; the body stays that long and then turns into the carcass (lying in
     *  its knocked_out pose, which the animation ends in). 0 = no death animation of its own: it sinks into the
     *  knocked_out pose for a second (05/11/2026, player report: the vanilla tipping over fell to one side and the
     *  carcass then lay on the other, "it falls and suddenly flicks to the other side"). */
    protected int deathAnimTicks() {
        return 0;
    }

    public boolean hasDeathAnimation() {
        return this.deathAnimTicks() > 0;
    }

    /** The facing becomes the body yaw it falls with, so the client can match it (see tickHeadTurn). */
    private void settleYaw() {
        this.setYRot(this.yBodyRot);
        this.yRotO = this.yBodyRot;
    }

    /** How long the dying body stays before the carcass takes its place. */
    private int dyingTicks() {
        return this.hasDeathAnimation() ? this.deathAnimTicks() + SETTLE_TICKS : 20;
    }

    /** After its own death animation the body settles into the knocked_out pose the carcass lies in (the two differ by up
     *  to 45 degrees at the knees in some rigs, and the carcass used to snap from one to the other). */
    private static final int SETTLE_TICKS = 8;

    /** Dead or knocked out, the body does not turn any more: the knockback of the last blow used to swing it round
     *  towards where it slid (65 degrees in a tenth of a second, a Triceratops in the 05/11 test) and the head look
     *  pulled it back after. It slides, but lies the way it fell; the carcass is laid with the same yaw. */
    @Override
    protected float tickHeadTurn(float bodyTarget, float walked) {
        if (this.isDeadOrDying() || this.isKnockedOut()) {
            // the client works its body yaw out by itself and can be some degrees off the server's, the one the carcass
            // is laid with: the server sends it as the facing when the animal falls, and the client eases onto it
            this.yBodyRot = this.level().isClientSide()
                    ? Mth.approachDegrees(this.yBodyRotO, this.getYRot(), 3.0F) : this.yBodyRotO;
            this.yHeadRot = this.yHeadRotO;
            return walked;
        }
        return super.tickHeadTurn(bodyTarget, walked);
    }

    /** Whether the species has its own "sleep" loop and "wake_sleep" (else it sleeps in the "sit" pose). */
    protected boolean hasSleepAnim() {
        return false;
    }

    /** Whether the species has a "swim" cycle for deep water. */
    protected boolean hasSwimAnim() {
        return false;
    }

    /** Whether the species flinches (its "hurt" animation) when it takes a hit. */
    protected boolean flinches() {
        return false;
    }

    /** Whether a landed hit triggers "attack" (false for species whose attack goal plays the bite and times the hit). */
    protected boolean animatesHits() {
        return true;
    }

    /** Size of a baby relative to the adult. Applied to the hitbox here and to the model by DinosaurRenderer. */
    protected float babyScale() {
        return 0.5F;
    }

    /** Smallest adult of the species, relative to its SIZES row (the row is the upper end of the fossil estimates). */
    protected float minSize() {
        return 0.94F;
    }

    /** Largest adult of the species, relative to its SIZES row. */
    protected float maxSize() {
        return 1.06F;
    }

    /** This animal's adult size relative to the species' standard. */
    public float getAdultSize() {
        return this.entityData.get(DATA_SIZE);
    }

    /** Sets the adult size (clamped to 0.5 - 1.5) and the health and damage that go with it. */
    /** Above the biggest animal there is: the T. rex alpha reaches 1.55, the Rift Tyrant is 1.65. */
    private static final float MAX_ADULT_SIZE = 1.7F;

    public void setAdultSize(float size) {
        this.entityData.set(DATA_SIZE, Mth.clamp(size, 0.5F, MAX_ADULT_SIZE));
        this.applySizeModifiers();
    }

    /** Adults: most near the middle of minSize..maxSize, extremes rare (sum of two dice); babies: 0.8 - 1.2 at birth. */
    private void rollSize() {
        float t = (this.random.nextFloat() + this.random.nextFloat()) / 2.0F;
        this.entityData.set(DATA_BIRTH_SIZE, 0.8F + 0.4F * this.random.nextFloat());
        this.setAdultSize(this.minSize() + (this.maxSize() - this.minSize()) * t);
    }

    /** Health with the square of the size (a 10% bigger animal has 21% more), bite damage in proportion. Server only;
     *  the modifiers are permanent, so they are saved with the attributes. */
    private void applySizeModifiers() {
        if (this.level().isClientSide()) {
            return;
        }
        float size = this.getAdultSize();
        boolean full = this.getHealth() >= this.getMaxHealth();
        AttributeInstance health = this.getAttribute(Attributes.MAX_HEALTH);
        if (health != null) {
            health.removeModifier(SIZE_HEALTH_ID);
            health.addPermanentModifier(new AttributeModifier(SIZE_HEALTH_ID, "Size", size * size - 1.0F,
                    AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
        AttributeInstance damage = this.getAttribute(Attributes.ATTACK_DAMAGE);
        if (damage != null) {
            damage.removeModifier(SIZE_DAMAGE_ID);
            damage.addPermanentModifier(new AttributeModifier(SIZE_DAMAGE_ID, "Size", size - 1.0F,
                    AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
        if (full || this.getHealth() > this.getMaxHealth()) {
            this.setHealth(this.getMaxHealth());
        }
    }

    /** Model and hitbox scale: the adult size, or for a baby its hatchling size growing into it. */
    @Override
    public float getScale() {
        float adult = this.entityData.get(DATA_SIZE);
        if (!this.isBaby()) {
            return adult;
        }
        float birth = this.babyScale() * this.entityData.get(DATA_BIRTH_SIZE);
        return birth + (adult - birth) * this.entityData.get(DATA_GROWTH);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (DATA_SIZE.equals(key) || DATA_BIRTH_SIZE.equals(key) || DATA_GROWTH.equals(key) || DATA_ALPHA.equals(key)) {
            this.refreshDimensions();
        }
    }

    /** Server: a baby's growth follows its age; sent to the clients in steps of 1% (about every 12 s). */
    private void growthTick() {
        if (!this.isBaby() || this.tickCount % 20 != 1) {
            return;
        }
        float growth = Mth.clamp(1.0F + this.getAge() / GROW_TICKS, 0.0F, 1.0F);
        if (Math.abs(growth - this.entityData.get(DATA_GROWTH)) >= 0.01F) {
            this.entityData.set(DATA_GROWTH, growth);
        }
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
        this.entityData.define(DATA_DUEL, false);
        this.entityData.define(DATA_LOCKED, false);
        this.entityData.define(DATA_TIRED, false);
        this.entityData.define(DATA_FEMALE, false);
        this.entityData.define(DATA_SADDLED, false);
        this.entityData.define(DATA_CHESTED, false);
        this.entityData.define(DATA_PLATFORM, false);
        this.entityData.define(DATA_RIFT, false);
        this.entityData.define(DATA_HUNGER, 70);
        this.entityData.define(DATA_KNOCKED_OUT, false);
        this.entityData.define(DATA_ENTANGLED, false);
        this.entityData.define(DATA_STUCK_DARTS, 0);
        this.entityData.define(DATA_DART_ZONES, 0);
        this.entityData.define(DATA_SLEEPING, false);
        this.entityData.define(DATA_SIZE, 1.0F);
        this.entityData.define(DATA_BIRTH_SIZE, 1.0F);
        this.entityData.define(DATA_GROWTH, 0.0F);
        this.entityData.define(DATA_LEVEL, 0);
        this.entityData.define(DATA_ALPHA, false);
        this.entityData.define(DATA_SPECIAL, 0);
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

    public boolean isRoamer() {
        return this.roamer;
    }

    public void setRoamer(boolean roamer) {
        this.roamer = roamer;
    }

    /** Disposable ecosystem population; taming or naming immediately makes it persistent again. */
    public boolean isTransientRoamer() {
        return this.roamer && !this.isTame() && !this.hasCustomName();
    }

    @Override
    public boolean shouldBeSaved() {
        return !this.isTransientRoamer() && super.shouldBeSaved();
    }

    /** Whether it came through the Rift (Rift Storm leaks, the Rift Tyrant): drawn with glowing amber cracks. */
    public boolean isRift() {
        return this.entityData.get(DATA_RIFT);
    }

    public void setRift(boolean rift) {
        this.entityData.set(DATA_RIFT, rift);
    }

    // ------------------------------------------------------------------ the alpha (docs/ALFAS.md, entity/Alphas)

    /** Players beyond the first last counted around this wild alpha (-1 = not counted since it loaded). */
    private int alphaCrowd = -1;

    public boolean isAlpha() {
        return this.entityData.get(DATA_ALPHA);
    }

    /** Server: makes this animal an alpha of its species (the spawn roll or the command): grown, permanent, at the
     *  alpha's size, its level drawn again in the alpha's band. {@code female}: the sex to give it, or null to keep. */
    public void becomeAlpha(Boolean female) {
        if (this.level().isClientSide()) {
            return;
        }
        this.entityData.set(DATA_ALPHA, true);
        if (female != null) {
            this.setFemale(female);
        }
        if (this.isBaby()) {
            this.setAge(0);
        }
        this.roamer = false;
        this.setPersistenceRequired();
        this.setAdultSize(Alphas.size(this.speciesId(), this.random));
        if (this.levels.isRolled() && this.level() instanceof ServerLevel server) {
            int[] band = Alphas.levelBand(server);
            this.levels.rollBetween(this.random, band[0], band[1]);
            this.applyLevelModifiers(true);
        }
        this.applyAlphaModifiers();
        this.refreshDimensions();
        Alphas.seen(this);
    }

    /** The "Alpha strength" and "Alpha taming difficulty" rules. */
    private float alphaStrength() {
        return (float) Rules.of(this.level()).get(Rule.ALPHA_STRENGTH);
    }

    private float alphaTaming() {
        return (float) Rules.of(this.level()).get(Rule.ALPHA_TAMING);
    }

    /** Darts and sleep herb work half as well on an alpha. */
    public float narcoticEffect() {
        return this.isAlpha() && !this.isTame() ? Alphas.NARCOTIC_EFFECT : 1.0F;
    }

    /** What an unconscious animal accepts from the hand: an alpha only prime meat. */
    private boolean acceptsKoFood(ItemStack stack) {
        return this.isAlpha() ? stack.is(ModItems.RAW_PRIME_MEAT.get()) : this.koFood(stack);
    }

    /** Whether the player may feed this unconscious alpha into a tame one (the alpha rules); tells them why not. */
    private boolean alphaMayBeTamedBy(Player player) {
        if (Rules.of(this.level()).get(Rule.ALPHA_TAMEABLE) < 0.5D) {
            player.displayClientMessage(Component.translatable("message.terrassic.alpha.untameable", this.getDisplayName()), true);
            return false;
        }
        if (!Alphas.mayOwnAnother(player, this.speciesId())) {
            player.displayClientMessage(Component.translatable("message.terrassic.alpha.limit", this.getDisplayName()), true);
            return false;
        }
        return true;
    }

    /** The wild alpha's own bonus (+25% health, both times the "Alpha strength" rule), gone once it is tamed. Server;
     *  permanent modifiers, saved with the attributes. */
    private void applyAlphaModifiers() {
        if (this.level().isClientSide()) {
            return;
        }
        boolean wild = this.isAlpha() && !this.isTame();
        float strength = wild ? this.alphaStrength() : 1.0F;
        float share = this.getMaxHealth() > 0.0F ? this.getHealth() / this.getMaxHealth() : 1.0F;
        AttributeInstance health = this.getAttribute(Attributes.MAX_HEALTH);
        if (health != null) {
            health.removeModifier(ALPHA_HEALTH_ID);
            if (!wild) {
                health.removeModifier(ALPHA_CROWD_ID);
            }
            float bonus = wild ? (1.0F + Alphas.WILD_HEALTH_BONUS) * strength - 1.0F : 0.0F;
            if (Math.abs(bonus) > 1.0E-4F) {
                health.addPermanentModifier(new AttributeModifier(ALPHA_HEALTH_ID, "Alpha", bonus, AttributeModifier.Operation.MULTIPLY_TOTAL));
            }
        }
        AttributeInstance damage = this.getAttribute(Attributes.ATTACK_DAMAGE);
        if (damage != null) {
            damage.removeModifier(ALPHA_DAMAGE_ID);
            if (Math.abs(strength - 1.0F) > 1.0E-4F) {
                damage.addPermanentModifier(new AttributeModifier(ALPHA_DAMAGE_ID, "Alpha", strength - 1.0F, AttributeModifier.Operation.MULTIPLY_TOTAL));
            }
        }
        AttributeInstance knockback = this.getAttribute(Attributes.KNOCKBACK_RESISTANCE);
        if (wild && knockback != null && knockback.getBaseValue() < 1.0D) {
            knockback.setBaseValue(1.0D);
        }
        this.setHealth(Math.max(1.0F, share * this.getMaxHealth()));
    }

    /** Server, every five seconds for a wild alpha: keeps its place in the register and gives it +25% health for each
     *  player beyond the first within 32 blocks (up to +100%), as the Rift Tyrant does with +50%. */
    private void alphaTick() {
        Alphas.seen(this);
        int players = this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(32.0D),
                p -> p.isAlive() && !p.isSpectator() && !p.isCreative()).size();
        int extra = Mth.clamp(players - 1, 0, Alphas.MAX_EXTRA_PLAYERS);
        AttributeInstance health = this.getAttribute(Attributes.MAX_HEALTH);
        if (health == null) {
            return;
        }
        if (extra == this.alphaCrowd) {
            return;
        }
        this.alphaCrowd = extra;
        double want = extra * Alphas.PER_PLAYER_HEALTH;
        float share = this.getHealth() / this.getMaxHealth();
        health.removeModifier(ALPHA_CROWD_ID);
        if (want > 0.0D) {
            health.addPermanentModifier(new AttributeModifier(ALPHA_CROWD_ID, "Alpha crowd", want, AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
        this.setHealth(Math.max(1.0F, share * this.getMaxHealth()));
    }

    /** An alpha keeps the species' widest hitbox (the model is bigger): a box any wider would not find its way between
     *  the trees. Babies and the others scale as usual. */
    @Override
    public net.minecraft.world.entity.EntityDimensions getDimensions(net.minecraft.world.entity.Pose pose) {
        net.minecraft.world.entity.EntityDimensions d = super.getDimensions(pose);
        float scale = this.getScale();
        if (this.isAlpha() && !this.isBaby() && scale > this.maxSize()) {
            return d.scale(this.maxSize() / scale, 1.0F);
        }
        return d;
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
        if (this.entangledTicks > 0) {
            tag.putInt("Entangled", this.entangledTicks);
        }
        tag.putBoolean("Platform", this.isPlatform());
        tag.putInt("Sated", this.sated);
        tag.putInt("Hunger", this.getHunger());
        tag.putBoolean("Roamer", this.roamer);
        if (this.stance != DinoStance.NEUTRAL) {
            tag.putString("Stance", this.stance.key);
        }
        if (this.wanderPos != null) {
            tag.put("WanderPos", NbtUtils.writeBlockPos(this.wanderPos));
        }
        if (this.isRift()) {
            tag.putBoolean("Rift", true);
        }
        if (this.isAlpha()) {
            tag.putBoolean("Alpha", true);
        }
        tag.putFloat("Size", this.getAdultSize());
        tag.putFloat("BirthSize", this.entityData.get(DATA_BIRTH_SIZE));
        if (this.levels.isRolled()) {
            tag.put("Levels", this.levels.save());
        }
        if (this.torpor > 0.0F) {
            tag.putFloat("Torpor", this.torpor);
        }
        if (this.isKnockedOut()) {
            tag.putBoolean("KnockedOut", true);
        }
        if (this.tameProgress > 0.0F) {
            tag.putFloat("TameProgress", this.tameProgress);
        }
        // Wounds can lower effectiveness before the first meal; it already belongs to the unconscious animal.
        if (this.isKnockedOut() || this.tameProgress > 0.0F) {
            tag.putInt("TameEffectiveness", this.tameEffectiveness);
        }
        if (this.tamer != null) {
            tag.putUUID("Tamer", this.tamer);
        }
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
        this.refreshBaseHealth();
        if (tag.contains("Female")) {
            this.setFemale(tag.getBoolean("Female"));
        }
        this.setSaddled(tag.getBoolean("Saddled"));
        this.pendingNest = tag.getBoolean("PendingNest");
        this.setChested(tag.getBoolean("Chested"));
        this.setPlatform(tag.getBoolean("Platform"));
        this.sated = tag.getInt("Sated");
        this.roamer = tag.getBoolean("Roamer");
        this.stance = DinoStance.byKey(tag.getString("Stance"));
        this.wanderPos = tag.contains("WanderPos", Tag.TAG_COMPOUND) ? NbtUtils.readBlockPos(tag.getCompound("WanderPos")) : null;
        if (this.wanderPos != null) {
            this.restrictTo(this.wanderPos, WANDER_RADIUS);
        }
        this.setRift(tag.getBoolean("Rift"));
        this.entityData.set(DATA_ALPHA, tag.getBoolean("Alpha"));
        this.torpor = tag.getFloat("Torpor");
        this.entityData.set(DATA_KNOCKED_OUT, tag.getBoolean("KnockedOut"));
        this.entangledTicks = tag.getInt("Entangled");
        this.entityData.set(DATA_ENTANGLED, this.entangledTicks > 0);
        this.tameProgress = tag.getFloat("TameProgress");
        this.tameEffectiveness = tag.contains("TameEffectiveness") ? tag.getInt("TameEffectiveness") : 100;
        this.tamer = tag.hasUUID("Tamer") ? tag.getUUID("Tamer") : null;
        if (tag.contains("Hunger")) {
            this.setHunger(tag.getInt("Hunger"));
        }
        if (tag.contains("Levels", Tag.TAG_COMPOUND)) {
            this.levels.load(tag.getCompound("Levels"));
            this.applyLevelModifiers(false);
        } else {
            this.legacyLevels = true;
        }
        // size: worlds from before the size variation keep the size rolled when the entity was created
        if (tag.contains("BirthSize")) {
            this.entityData.set(DATA_BIRTH_SIZE, tag.getFloat("BirthSize"));
        }
        this.setAdultSize(tag.contains("Size") ? tag.getFloat("Size") : this.getAdultSize());
        if (tag.contains("Health", Tag.TAG_ANY_NUMERIC)) {
            this.setHealth(tag.getFloat("Health"));  // read again: it was clamped to the max health before the size modifier
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
        // Permanent herds can leave nests; disposable ecosystem roamers must not leave permanent blocks behind.
        float nest = 0.2F * (float) Rules.of(level.getLevel()).get(Rule.NEST_FREQUENCY);
        if (!this.isTransientRoamer() && (reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) && this.wildNests() && !this.isBaby()
                && this.isFemale() && this.random.nextFloat() < nest) {
            if (level instanceof WorldGenRegion) {
                this.pendingNest = true;  // nothing can be placed while the chunk generates: lay it on the first tick
            } else {
                this.layWildEgg(level);
            }
        }
        if (level.getLevel() != null && Alphas.rollAtSpawn(this, level.getLevel(), reason)) {
            this.becomeAlpha(null);
        }
        this.ensureLevels();
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

        this.knockedOutAnim = RawAnimation.begin().thenLoop(anim("knocked_out"));
        this.deathAnim = this.hasDeathAnimation() ? RawAnimation.begin().thenPlayAndHold(anim("death")) : this.knockedOutAnim;
        this.sleepAnim = RawAnimation.begin().thenLoop(anim("sleep"));
        this.swimAnim = RawAnimation.begin().thenLoop(anim("swim"));
        AnimationController<DinosaurEntity> movement = new AnimationController<>(this, "movement", 6, state -> {
            if (this.isDeadOrDying()) {
                this.cycleSpeed = 1.0D;
                return state.setAndContinue(this.deathTime > this.deathAnimTicks() ? this.knockedOutAnim : this.deathAnim);
            }
            if (this.isKnockedOut()) {
                this.cycleSpeed = 1.0D;
                return this.knockedOutAnimation(state);
            }
            return this.movementAnimation(state);
        });
        if (this.walkCycleSpeed() > 0.0D) {
            movement.setAnimationSpeedHandler(animal -> this.cycleSpeed);
        }
        controllers.add(movement);

        // the flinch sits between movement and action: a bite or a roar under way wins over it
        if (this.flinches()) {
            RawAnimation hurtAnim = RawAnimation.begin().thenPlay(anim("hurt"));
            controllers.add(new AnimationController<>(this, "flinch", 2, state -> {
                if (this.hurtTime <= 0 || !this.isAlive()) {
                    this.lastFlinch = 0;
                    return PlayState.STOP;
                }
                if (this.hurtTime > this.lastFlinch) {
                    state.getController().forceAnimationReset();
                }
                this.lastFlinch = this.hurtTime;
                return state.setAndContinue(hurtAnim);
            }));
        }

        AnimationController<DinosaurEntity> action = new AnimationController<>(this, ACTION_CONTROLLER, 3, state -> PlayState.STOP);
        for (String name : new String[]{"attack", "eat", "beg", "wake", "tame"}) {
            action.triggerableAnim(name, RawAnimation.begin().thenPlay(anim(this.actionAnimation(name))));
        }
        if (this.hasSleepAnim()) {
            action.triggerableAnim("wake_sleep", RawAnimation.begin().thenPlay(anim(this.actionAnimation("wake_sleep"))));
        }
        java.util.Set<String> registered = new java.util.HashSet<>();
        for (String extra : extraActions()) {
            action.triggerableAnim(extra, RawAnimation.begin().thenPlay(anim(this.actionAnimation(extra))));
            registered.add(extra);
        }
        if (this.hasLivelySet() || this.hasDuelMoves()) {
            for (String extra : LIVELY_ACTIONS) {
                if (registered.add(extra)) {
                    action.triggerableAnim(extra, RawAnimation.begin().thenPlay(anim(extra)));
                }
            }
        }
        controllers.add(action);
    }

    /** The animation a one-shot trigger plays: its own name, unless the rig has none by that name (a rig without
     *  "tame" or "wake_sleep" maps them onto one of its own). */
    protected String actionAnimation(String trigger) {
        return trigger;
    }

    /** Knocked out: the "knocked_out" loop (a flyer can have its own pose for the fall). */
    protected PlayState knockedOutAnimation(AnimationState<DinosaurEntity> state) {
        return state.setAndContinue(this.knockedOutAnim);
    }

    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        this.cycleSpeed = 1.0D;
        PlayState lively = this.livelyStances(state);
        if (lively != null) {
            return lively;
        }
        if (this.isSleeping() && this.hasSleepAnim() && !this.isPerched()) {
            return state.setAndContinue(this.sleepAnim);
        }
        if (this.isPerched() || this.isSleeping() || (this.isInSittingPose() && !this.isVehicle())) {
            if (this.brooder() && this.tickCount % 10 == 0) {
                this.brooding = !this.isBaby() && this.nearestEgg(2) != null;
            }
            return state.setAndContinue(this.brooder() && this.brooding ? this.broodAnim : this.sitAnim);
        }
        if (this.isSwimmingDeep()) {
            return state.setAndContinue(this.swimAnim);
        }
        if (state.isMoving()) {
            boolean running = this.isAggressive() || this.getDeltaMovement().horizontalDistanceSqr() > runThresholdSqr();
            this.cycleSpeed = this.gaitSpeed(running ? this.runCycleSpeed() : this.walkCycleSpeed());
            return state.setAndContinue(running ? this.runAnim : this.walkAnim);
        }
        return state.setAndContinue(this.idleAnim);
    }

    /** Species with a swim cycle use it once the water is over a third of their height and the feet are off the bottom. */
    protected boolean isSwimmingDeep() {
        return this.hasSwimAnim() && this.isInWater() && !this.onGround()
                && this.getFluidHeight(FluidTags.WATER) > this.getBbHeight() * 0.35D;
    }

    /** Client: playback speed for a cycle that covers {@code cycle} blocks per tick at size 1.0, from the distance the
     *  animal really moved this tick (0.5x - 1.8x). */
    protected double gaitSpeed(double cycle) {
        if (cycle <= 0.0D) {
            return 1.0D;
        }
        double dx = this.getX() - this.xo;
        double dz = this.getZ() - this.zo;
        double speed = Math.sqrt(dx * dx + dz * dz);
        return Mth.clamp(speed / (cycle * this.getScale()), 0.5D, 1.8D);
    }

    /** A living animal and a carcass of its species share the model's bones (GeckoLib bakes one model per file), and GeckoLib
     *  skips the pose of a second draw in the same frame (a shader's shadow pass) and draws whatever the bones hold: a
     *  carcass drawn after a living T. rex stood up, depending on where the camera looked (found in play, 06/11). Each
     *  draw gets a time a hair apart (under a ten-thousandth of a tick), so every draw sets its own pose. */
    private int drawSalt;

    @Override
    public double getTick(Object entity) {
        this.drawSalt = (this.drawSalt + 1) & 1023;
        return this.tickCount + this.drawSalt * 1.0E-7D;
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.geoCache;
    }

    // ------------------------------------------------------------------ hit parts (1.7, docs/PLANO_PARTES.md)

    private static final DinoPart.Spec[] NO_PARTS = new DinoPart.Spec[0];
    private final DinoPart[] parts;
    /** Union of the parts' boxes, for a quick test before the parts themselves. */
    private AABB partsBounds = new AABB(0, 0, 0, 0, 0, 0);
    private boolean partsRegistered;
    /** Where the blow being dealt landed (DinoPart.Kind#zone), 0 for the body; read by a dart that sticks. */
    private int hitZone;

    /** The one-shot animations with the head down to eat or drink (tools/javagen/parts.py HEAD_DOWN_POSES). */
    private static final java.util.Set<String> HEAD_DOWN = java.util.Set.of("graze", "eat", "drink", "sift", "grit", "pluck");
    /** Server: until when the head is down (the client reads the animation playing). */
    private int headDownUntil;

    /** Grazing, eating or drinking: the parts take their head-down layout. The client asks GeckoLib what the action
     *  controller plays (what is drawn); the server keeps the time of the last such trigger. */
    public boolean isHeadDown() {
        if (!this.level().isClientSide()) {
            return this.tickCount < this.headDownUntil;
        }
        var manager = this.getAnimatableInstanceCache().getManagerForId(this.getId());
        var action = manager.getAnimationControllers().get(ACTION_CONTROLLER);
        if (action == null || action.getCurrentAnimation() == null || action.hasAnimationFinished()) {
            return false;
        }
        String name = action.getCurrentAnimation().animation().name();
        return HEAD_DOWN.contains(name.substring(name.lastIndexOf('.') + 1));
    }

    /** Development only (client/dev/BehaviorTest): told of every one-shot animation a creature triggers; null in play. */
    public static volatile java.util.function.BiConsumer<DinosaurEntity, String> triggerLog;

    @Override
    public void triggerAnim(String controllerName, String animName) {
        java.util.function.BiConsumer<DinosaurEntity, String> log = triggerLog;
        if (log != null && !this.level().isClientSide()) {
            log.accept(this, animName);
        }
        if (ACTION_CONTROLLER.equals(controllerName) && HEAD_DOWN.contains(animName)) {
            this.headDownUntil = this.tickCount + 60;
        }
        GeoEntity.super.triggerAnim(controllerName, animName);
    }

    /** The species' hit parts at size 1 (generated by tools/javagen/parts.py); none by default. */
    public DinoPart.Spec[] partSpecs() {
        return NO_PARTS;
    }

    /** Where the head turns to look, in front of the centre (blocks at size 1): the bone "head", which GeckoLib turns
     *  by the head yaw and pitch. The head parts swing and tilt about it. */
    public float partPivot() {
        return 0.0F;
    }

    /** The height of that pivot above the feet (blocks at size 1). */
    public float partPivotUp() {
        return 0.0F;
    }

    public DinoPart[] parts() {
        return this.parts;
    }

    /** Parts are hit only while it stands on its own (not on a player's shoulder). */
    public boolean partsActive() {
        return this.parts.length > 0 && !this.isPassenger();
    }

    public AABB partsBounds() {
        return this.partsBounds;
    }

    /** The part with this entity id, or null. */
    public DinoPart partById(int id) {
        int i = id - this.getId() - 1;
        return i >= 0 && i < this.parts.length ? this.parts[i] : null;
    }

    @Override
    public void setId(int id) {
        super.setId(id);
        if (this.parts != null) {
            for (int i = 0; i < this.parts.length; i++) {
                this.parts[i].setId(id + i + 1);
            }
        }
    }

    /** Every tick, on both sides: registers the creature with its level and puts the parts where the model is. */
    private void tickParts() {
        if (this.parts.length == 0) {
            return;
        }
        if (!this.partsRegistered) {
            this.partsRegistered = true;
            ((PartOwners) this.level()).terrassic$addPartOwner(this);
        }
        this.placeParts(1.0F);
    }

    /** Puts the parts where the model is drawn at this point between two ticks (1 = the tick itself; the client calls
     *  it every frame before it aims the crosshair, so what is seen is what is hit). Each piece is a box in the body's
     *  frame (forward, side, up) turned with the model: the head about the bone "head" by the look (yaw and pitch, as
     *  GeckoLib turns that bone), a flyer's whole body by its flight pitch and roll (as DinosaurRenderer tilts it), all
     *  by the body yaw; its part's box is the smallest one holding it. Lying down (asleep, sitting, knocked out) the
     *  pieces take their lying layout. A flyer's wings stand only while it flies. */
    public void placeParts(float partialTick) {
        if (this.parts.length == 0) {
            return;
        }
        float scale = this.getScale();
        int layout = this.isKnockedOut() || this.isSleeping() || this.isInSittingPose() ? DinoPart.Spec.LYING
                : this.isHeadDown() ? DinoPart.Spec.HEAD_DOWN : DinoPart.Spec.STANDING;
        FlyingDinosaur flyer = this instanceof FlyingDinosaur f ? f : null;
        boolean wings = flyer != null && flyer.isAirborne();
        double px = Mth.lerp(partialTick, this.xo, this.getX());
        double py = Mth.lerp(partialTick, this.yo, this.getY());
        double pz = Mth.lerp(partialTick, this.zo, this.getZ());
        float bodyYaw = Mth.rotLerp(partialTick, this.yBodyRotO, this.yBodyRot) * Mth.DEG_TO_RAD;
        float look = Mth.wrapDegrees(Mth.rotLerp(partialTick, this.yHeadRotO, this.yHeadRot) - Mth.rotLerp(partialTick, this.yBodyRotO,
                this.yBodyRot)) * Mth.DEG_TO_RAD;
        float pitch = Mth.lerp(partialTick, this.xRotO, this.getXRot()) * Mth.DEG_TO_RAD;   // positive: looking down
        // the body's frame in the world: forward, the model's +x, up
        double fX = -Mth.sin(bodyYaw), fZ = Mth.cos(bodyYaw);
        double sX = -Mth.cos(bodyYaw), sZ = -Mth.sin(bodyYaw);
        // the head's axes in the body's frame (forward, side, up): turned by the look, tilted by the pitch
        double cl = Mth.cos(look), sl = Mth.sin(look), cp = Mth.cos(pitch), sp = Mth.sin(pitch);
        double[][] head = {{cp * cl, cp * sl, -sp}, {-sl, cl, 0.0D}, {sp * cl, sp * sl, cp}};
        double[][] flat = {{1.0D, 0.0D, 0.0D}, {0.0D, 1.0D, 0.0D}, {0.0D, 0.0D, 1.0D}};
        // a flyer's tilt about its saddle (DinosaurRenderer): roll about forward, then pitch about the side
        double tf = 0.0D, tu = 0.0D, ct = 1.0D, st = 0.0D, cr = 1.0D, sr = 0.0D;
        if (flyer != null && this.deathTime <= 0) {
            double tp = flyer.flightPitch(partialTick) * Mth.DEG_TO_RAD, tr = flyer.flightRoll(partialTick) * Mth.DEG_TO_RAD;
            ct = Math.cos(tp);
            st = Math.sin(tp);
            cr = Math.cos(tr);
            sr = Math.sin(tr);
            tf = flyer.tiltPivotForward();
            tu = flyer.tiltPivotHeight();
        }
        double pivotF = this.partPivot() * scale, pivotU = this.partPivotUp() * scale;
        double minX = px, minY = py, minZ = pz, maxX = px, maxY = py, maxZ = pz;
        double[] c = new double[3];
        double[][] axes = new double[3][];
        for (DinoPart part : this.parts) {
            DinoPart.Kind kind = part.kind();
            float[] l = part.spec.layout(layout);
            boolean on = l[3] > 0.0F && l[5] > 0.0F && (kind != DinoPart.Kind.WING || wings);
            double half0 = l[3] * scale * 0.5D, half1 = l[4] * scale * 0.5D, half2 = l[5] * scale * 0.5D;
            double f = l[0] * scale, side = l[1] * scale, up = l[2] * scale + half2;
            double[][] a = kind == DinoPart.Kind.HEAD ? head : flat;
            if (kind == DinoPart.Kind.HEAD) {
                double d = f - pivotF, e = up - pivotU;
                for (int i = 0; i < 3; i++) {
                    c[i] = d * a[0][i] + side * a[1][i] + e * a[2][i];
                }
                c[0] += pivotF;
                c[2] += pivotU;
            } else {
                c[0] = f;
                c[1] = side;
                c[2] = up;
            }
            for (int k = 0; k < 3; k++) {
                axes[k] = a[k].clone();
            }
            if (st != 0.0D || sr != 0.0D) {
                tilt(c, tf, tu, ct, st, cr, sr, true);
                for (int k = 0; k < 3; k++) {
                    tilt(axes[k], 0.0D, 0.0D, ct, st, cr, sr, false);
                }
            }
            // to the world: x = forward*fX + side*sX, y = up, z = forward*fZ + side*sZ
            double x = px + c[0] * fX + c[1] * sX, y = py + c[2], z = pz + c[0] * fZ + c[1] * sZ;
            double[] half = {half0, half1, half2};
            double hx = 0.0D, hy = 0.0D, hz = 0.0D;
            for (int k = 0; k < 3; k++) {
                hx += Math.abs(axes[k][0] * fX + axes[k][1] * sX) * half[k];
                hy += Math.abs(axes[k][2]) * half[k];
                hz += Math.abs(axes[k][0] * fZ + axes[k][1] * sZ) * half[k];
            }
            part.place(x, y, z, hx, hy, hz, on);
            if (!on) {
                continue;
            }
            AABB box = part.getBoundingBox();
            minX = Math.min(minX, box.minX);
            minY = Math.min(minY, box.minY);
            minZ = Math.min(minZ, box.minZ);
            maxX = Math.max(maxX, box.maxX);
            maxY = Math.max(maxY, box.maxY);
            maxZ = Math.max(maxZ, box.maxZ);
        }
        this.partsBounds = new AABB(minX, minY, minZ, maxX, maxY, maxZ);
    }

    /** A flyer's tilt on a vector of the body's frame (forward, side, up), about (pivotF, 0, pivotU) for a point: roll
     *  first (the model's +x side up), then pitch (the nose up), as DinosaurRenderer#applyRotations turns the model. */
    private static void tilt(double[] v, double pivotF, double pivotU, double ct, double st, double cr, double sr, boolean point) {
        double f = v[0] - (point ? pivotF : 0.0D), s = v[1], u = v[2] - (point ? pivotU : 0.0D);
        double s1 = s * cr - u * sr, u1 = s * sr + u * cr;
        double f2 = f * ct - u1 * st, u2 = f * st + u1 * ct;
        v[0] = f2 + (point ? pivotF : 0.0D);
        v[1] = s1;
        v[2] = u2 + (point ? pivotU : 0.0D);
    }

    /** A blow on a part: the part's multiplier (head 125%, neck 100%, tail 75%; the club's torpor follows it), and what
     *  the engine only does for a living target (a melee weapon's own effect and wear, an arrow's dart or count). */
    public boolean hurtByPart(DinoPart part, DamageSource source, float amount) {
        int before = this.hitZone;
        this.hitZone = part.kind().zone;
        try {
            boolean hurt = this.hurt(source, amount * part.kind().damage);
            if (hurt && !this.level().isClientSide()) {
                this.afterPartHit(source);
            }
            return hurt;
        } finally {
            this.hitZone = before;
        }
    }

    private void afterPartHit(DamageSource source) {
        Entity direct = source.getDirectEntity();
        if (direct instanceof Player player && source.getEntity() == player && source.is(DamageTypes.PLAYER_ATTACK)) {
            // Player#attack only does these for a living target (or the dragon's parts)
            player.setLastHurtMob(this);
            ItemStack weapon = player.getMainHandItem();
            if (!weapon.isEmpty()) {
                weapon.hurtEnemy(this, player);
                if (weapon.isEmpty()) {
                    player.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
                }
            }
            EnchantmentHelper.doPostHurtEffects(this, player);
        } else if (direct instanceof AbstractArrow arrow && !(direct instanceof ThrownSpear)) {
            // AbstractArrow#onHitEntity: the stuck arrow, the enchantments and the arrow's own effect (a dart's)
            if (arrow.getPierceLevel() <= 0) {
                this.setArrowCount(this.getArrowCount() + 1);
            }
            if (arrow.getOwner() instanceof LivingEntity shooter) {
                EnchantmentHelper.doPostHurtEffects(this, shooter);
                EnchantmentHelper.doPostDamageEffects(shooter, this);
            }
            ((AbstractArrowInvoker) arrow).terrassic$doPostHurtEffects(this);
        }
    }


    // ================================================================== duels, stances, transitions, tiredness
    // (06/11/2026, from the T. rex: docs/DUELOS.md, docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md). The server side
    // (duels, blocks, giving in, fatigue) runs for the species in DUEL_SPECIES; the client plays the guard, sidesteps,
    // step-round turns and tired loops of any species whose animation file has them (hasAnim).

    /** Server, every tick: the duel's counters and the live states (transitions into and out of rest, fatigue). */
    private void duelTick() {
        if (this.lockedWith != null || this.isLocked()) {
            this.lockTick();
        }
        if (this.hasLivelySet()) {
            this.livelyStateTick();
        }
        if (this.blockCooldown > 0) {
            this.blockCooldown--;
        }
        if (this.counterLeft > 0 && !this.isDueling()) {
            this.counterLeft = 0;
        }
        if (this.yieldTicks > 0) {
            this.yieldTicks--;
        }
        if (this.duelCooldown > 0) {
            this.duelCooldown--;
        }
        if (this.isDueling() && (this.getTarget() == null || !this.getTarget().isAlive())) {
            this.setDueling(false);
        }
    }

    /** The species whose AI duels (their rigs have guard, sidesteps, feint, block, recoil, submit). */
    private static final java.util.Set<String> DUEL_SPECIES = java.util.Set.of("tyrannosaurus", "carnotaurus", "giganotosaurus", "spinosaurus",
            "dakotaraptor", "pachycephalosaurus", "therizinosaurus", "triceratops", "styracosaurus", "protoceratops");

    public boolean hasDuelMoves() {
        return DUEL_SPECIES.contains(this.speciesId());
    }

    /** The species whose rigs have the common set (lie_down, get_up, fall_asleep, walk_tired, idle_tired): the server
     *  triggers their rest transitions and tracks their fatigue. */
    private static final java.util.Set<String> LIVELY_SET_SPECIES = java.util.Set.of("tyrannosaurus", "carnotaurus", "giganotosaurus",
            "spinosaurus", "velociraptor", "dakotaraptor", "pachycephalosaurus", "gallimimus", "parasaurolophus", "edmontosaurus",
            "ankylosaurus", "therizinosaurus", "deinosuchus", "triceratops", "styracosaurus", "protoceratops");

    public boolean hasLivelySet() {
        return LIVELY_SET_SPECIES.contains(this.speciesId());
    }

    // ------------------------------------------------------------------ horn lock (Farke et al. 2009)
    /** Species whose grown rivals lock horns and push (horn_lock loop, horn_lock_start, horn_lock_break). */
    private static final java.util.Set<String> HORN_LOCK_SPECIES = java.util.Set.of("triceratops");
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> DATA_LOCKED =
            net.minecraft.network.syncher.SynchedEntityData.defineId(DinosaurEntity.class, net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);
    private DinosaurEntity lockedWith;
    private int lockLeft;
    private RawAnimation hornLockAnim;

    public boolean locksHorns(LivingEntity other) {
        return HORN_LOCK_SPECIES.contains(this.speciesId()) && other instanceof DinosaurEntity d && d.getType() == this.getType()
                && !this.isBaby() && !d.isBaby();
    }

    public boolean isLocked() {
        return this.entityData.get(DATA_LOCKED);
    }

    /** Two rivals face to face and close: the horns lock, both push and twist for four to seven seconds. */
    public void lockHorns(DinosaurEntity other) {
        if (this.isLocked() || other.isLocked()) {
            return;
        }
        int ticks = 80 + this.random.nextInt(60);
        for (DinosaurEntity e : new DinosaurEntity[]{this, other}) {
            e.lockedWith = e == this ? other : this;
            e.lockLeft = ticks;
            e.entityData.set(DATA_LOCKED, true);
            e.getNavigation().stop();
            e.triggerAnim(ACTION_CONTROLLER, "horn_lock_start");
        }
    }

    /** Server, every tick while locked: face each other, push back and forth, a little damage, then let go. */
    private void lockTick() {
        DinosaurEntity o = this.lockedWith;
        if (o == null || !o.isAlive() || !this.isAlive() || --this.lockLeft <= 0 || this.distanceTo(o) > (this.getBbWidth() + o.getBbWidth())) {
            this.unlock();
            return;
        }
        this.getNavigation().stop();
        this.getLookControl().setLookAt(o, 30.0F, 30.0F);
        double dx = o.getX() - this.getX();
        double dz = o.getZ() - this.getZ();
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        this.setYRot(Mth.approachDegrees(this.getYRot(), yaw, 6.0F));
        this.yBodyRot = this.getYRot();
        // the shoving: who pushes harder this second wins a little ground
        if ((this.tickCount + this.getId()) % 20 == 0 && this.getId() < o.getId()) {
            DinosaurEntity winner = this.random.nextBoolean() ? this : o;
            DinosaurEntity loser = winner == this ? o : this;
            loser.knockback(0.35D, winner.getX() - loser.getX(), winner.getZ() - loser.getZ());
            if (this.isDueling() || o.isDueling()) {
                // a real fight hurts; rivals sparring for show only push
                loser.hurt(this.damageSources().mobAttack(winner), 1.0F + this.random.nextFloat());
            }
        }
    }

    private void unlock() {
        if (this.isLocked()) {
            this.entityData.set(DATA_LOCKED, false);
            this.triggerAnim(ACTION_CONTROLLER, "horn_lock_break");
            this.stagger = 15;
        }
        this.lockedWith = null;
        this.lockLeft = 0;
    }

    /** The one-shots of the common set, registered for the species that have it. */
    private static final String[] LIVELY_ACTIONS = {"lie_down", "get_up", "fall_asleep", "feint", "block", "recoil", "submit",
            "horn_lock_start", "horn_lock_break", "kick_back", "body_shove"};

    /** The winner of a duel: a roar (a rig may give a louder one). */
    protected void wonDuel() {
        triggerAnim(ACTION_CONTROLLER, "roar");
    }

    /** Client: whether this species' animation file has {@code name} (cached per species). */
    public boolean hasAnim(String name) {
        return AnimIndex.has(this.speciesId(), name);
    }

    /** The movement loops of the live layer, before the species' own: the duel guard and sidesteps, the step-round
     *  turns, the tired loops (each only if the rig has it). */
    protected PlayState livelyStances(AnimationState<DinosaurEntity> state) {
        if (!this.livelyMotion()) {
            return null;
        }
        if (this.isLocked() && this.hasAnim("horn_lock")) {
            if (this.hornLockAnim == null) {
                this.hornLockAnim = RawAnimation.begin().thenLoop(anim("horn_lock"));
            }
            return state.setAndContinue(this.hornLockAnim);
        }
        PlayState p = this.duelStance(state);
        if (p == null) {
            p = this.turnInPlace(state);
        }
        if (p == null) {
            p = this.tiredStance(state);
        }
        return p;
    }




    private RawAnimation turnLeftAnim;
    private RawAnimation turnRightAnim;
    private RawAnimation guardAnim;
    private RawAnimation strafeLeftAnim;
    private RawAnimation strafeRightAnim;

    // ------------------------------------------------------------------ the duel (06/11/2026)
    /** Facing a big rival or a horned herbivore that fights: guard, circling, feints, blocks (ApexBiteGoal). Synced:
     *  the client plays the guard and the sidesteps while it is set. */
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> DATA_DUEL =
            net.minecraft.network.syncher.SynchedEntityData.defineId(DinosaurEntity.class, net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);
    /** Ticks it reels after its bite was blocked (no blows meanwhile). */
    public int stagger;
    private int blockCooldown;
    /** A territorial duel (two grown males of a size): the loser gives in at half its health, not a third. */
    protected boolean territorial;
    private java.util.UUID yieldedTo;
    private int yieldTicks;
    protected int duelCooldown = 1200;

    // ------------------------------------------------------------------ rest transitions and tiredness (06/11/2026)
    private boolean wasSitting;
    private boolean wasSleeping;
    /** 0 .. 1: grows while it runs, falls while it walks or stands; spent above 0.75 until it is back under 0.3. */
    private float fatigue;
    private double lastX;
    private double lastZ;
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> DATA_TIRED =
            net.minecraft.network.syncher.SynchedEntityData.defineId(DinosaurEntity.class, net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);
    private static final java.util.UUID TIRED_SLOW = java.util.UUID.fromString("7d1f0c1e-3b6a-4f2e-9c1d-5e8a2b4c6d70");
    private RawAnimation walkTiredAnim;
    private RawAnimation idleTiredAnim;

    /** Server: the fatigue, 0 .. 1 (for the dev test). */
    public float fatigue() {
        return this.fatigue;
    }

    public boolean isTired() {
        return this.entityData.get(DATA_TIRED);
    }

    /** Server, every tick: the transitions into and out of rest, and the fatigue of a long chase. */
    protected void livelyStateTick() {
        boolean sitting = this.isInSittingPose() && !this.isVehicle();
        boolean sleeping = this.isSleeping();
        if (sleeping && !this.wasSleeping && !this.wasSitting) {
            triggerAnim(ACTION_CONTROLLER, "fall_asleep");
        } else if (sitting && !this.wasSitting && !sleeping) {
            triggerAnim(ACTION_CONTROLLER, "lie_down");
        } else if (!sitting && this.wasSitting && !sleeping && !this.wasSleeping && this.isAlive()) {
            triggerAnim(ACTION_CONTROLLER, "get_up");
        }
        this.wasSitting = sitting;
        this.wasSleeping = sleeping;
        // the distance it really covered since the last tick (the AI runs before this tick's move, so x - xo is 0 here)
        double mx = this.getX() - this.lastX;
        double mz = this.getZ() - this.lastZ;
        this.lastX = this.getX();
        this.lastZ = this.getZ();
        double speed = mx * mx + mz * mz;
        if (speed > this.runThresholdSqr()) {
            this.fatigue = Math.min(1.0F, this.fatigue + 0.0025F);     // ~20 s of running wears it out
        } else {
            this.fatigue = Math.max(0.0F, this.fatigue - (speed < 1.0E-4D ? 0.0035F : 0.0015F));
        }
        boolean tired = this.isTired();
        if (!tired && this.fatigue > 0.75F) {
            this.setTired(true);
        } else if (tired && this.fatigue < 0.3F) {
            this.setTired(false);
        }
    }

    private void setTired(boolean tired) {
        this.entityData.set(DATA_TIRED, tired);
        net.minecraft.world.entity.ai.attributes.AttributeInstance speed = this.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.removeModifier(TIRED_SLOW);
            if (tired) {
                speed.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(TIRED_SLOW, "tired", -0.25D,
                        net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.MULTIPLY_TOTAL));
            }
        }
    }

    /** Spent: the tired walk and the panting stand (the run stays the run). */
    protected PlayState tiredStance(AnimationState<DinosaurEntity> state) {
        if (!this.hasAnim("walk_tired") || !this.isTired() || this.isSwimmingDeep() || this.isSleeping() || this.isInSittingPose() || !this.isAlive()) {
            return null;
        }
        if (this.walkTiredAnim == null) {
            this.walkTiredAnim = RawAnimation.begin().thenLoop(anim("walk_tired"));
            this.idleTiredAnim = RawAnimation.begin().thenLoop(anim("idle_tired"));
        }
        if (!state.isMoving()) {
            return state.setAndContinue(this.idleTiredAnim);
        }
        if (this.getDeltaMovement().horizontalDistanceSqr() <= this.runThresholdSqr()) {
            this.cycleSpeed = this.gaitSpeed(56.0D / 16.0D / 48.0D * this.livelyModelScale());
            return state.setAndContinue(this.walkTiredAnim);
        }
        return null;
    }


    public boolean isDueling() {
        return this.entityData.get(DATA_DUEL);
    }

    public void setDueling(boolean dueling) {
        this.entityData.set(DATA_DUEL, dueling);
        if (!dueling) {
            this.territorial = false;
        }
    }

    /** Whether its fight goal duels this target (only the T. rex for now, the live-motion species). */
    public boolean duels(LivingEntity target) {
        return this.hasDuelMoves() && !this.isBaby() && target instanceof DinosaurEntity d && d.fightsInDuel()
                && d.getBbWidth() >= this.getBbWidth() * 0.5F;
    }



    // ------------------------------------------------------------------ the exchange (06/11/2026, second pass)
    // Played, the first duel was "too static, monotonous" (Rodrigo): the two circled eight blocks apart and stood after
    // every blow. A fight is an exchange: the blow carries the body in, the one hit slides back and now and then answers
    // at once, a wind-up can be sidestepped, rivals chest to chest grapple and wheel round pushing until one throws the
    // other. These are the shared pieces; the fight goals (ApexBiteGoal, HeadMeleeAttackGoal) drive them.

    /** Ticks until it answers a blow it took (0: no answer pending), of a sidestep under way, of a grapple. */
    public int counterLeft;
    public int dodgeLeft;
    public float dodgeSide;
    public int clinchLeft;
    public DinosaurEntity clinchWith;
    public float clinchSpin;
    public boolean clinchLead;

    /** How hard a push moves it: big bodies slide less (by the box width against the other's). */
    private double heft(LivingEntity other) {
        return Mth.clamp(other.getBbWidth() / Math.max(0.6F, this.getBbWidth()), 0.35D, 1.6D);
    }

    /** The blow carries the body in: a step of {@code power} towards the target, in blocks per tick at size 1. */
    public void lungeAt(LivingEntity target, double power) {
        Vec3 d = new Vec3(target.getX() - this.getX(), 0.0D, target.getZ() - this.getZ());
        if (d.lengthSqr() < 1.0E-4D || !this.onGround()) {
            return;
        }
        d = d.normalize().scale(power * Math.min(1.4D, 0.7D + 0.3D * this.getScale()));
        this.setDeltaMovement(this.getDeltaMovement().add(d.x, 0.02D, d.z));
        this.hasImpulse = true;
    }

    /** Pushed by {@code from}: slides away from it by {@code power} (scaled by the two sizes), whatever its knockback
     *  resistance (the vanilla knockback leaves the big ones standing like posts). */
    public void pushedBy(LivingEntity from, double power) {
        Vec3 d = new Vec3(this.getX() - from.getX(), 0.0D, this.getZ() - from.getZ());
        if (d.lengthSqr() < 1.0E-4D) {
            return;
        }
        d = d.normalize().scale(power * this.heft(from));
        this.setDeltaMovement(this.getDeltaMovement().add(d.x, 0.04D, d.z));
        this.hasImpulse = true;
        this.hurtMarked = true;
    }

    /** A duel blow landed on it: it slides back, reels (the recoil now and then) and may answer at once. */
    public void tookDuelBlow(DinosaurEntity attacker, double weight) {
        if (this.level().isClientSide() || !this.isAlive()) {
            return;
        }
        this.pushedBy(attacker, 0.32D * weight);
        if (this.isLocked() || this.clinchLeft > 0) {
            return;
        }
        if (this.random.nextFloat() < 0.55F && this.hasAnim("recoil")) {
            triggerAnim(ACTION_CONTROLLER, "recoil");
        }
        this.stagger = Math.max(this.stagger, 6 + this.random.nextInt(5));
        if (this.random.nextFloat() < 0.45F) {
            this.counterLeft = this.stagger + 2 + this.random.nextInt(5);   // the answer, right after the reel
        }
    }

    /** A rival winds up at it: now and then it sidesteps the blow (and answers out of the step). */
    public void incoming(DinosaurEntity attacker, int hitIn) {
        if (this.level().isClientSide() || !this.isDueling() || this.stagger > 0 || this.isLocked() || this.clinchLeft > 0
                || this.dodgeLeft > 0 || !this.onGround() || this.random.nextFloat() > 0.22F) {
            return;
        }
        this.dodgeSide = this.random.nextBoolean() ? 1.0F : -1.0F;
        this.dodgeLeft = Math.max(6, Math.min(12, hitIn + 3));
        double yaw = Math.toRadians(this.getYRot());
        Vec3 side = new Vec3(Math.cos(yaw), 0.0D, Math.sin(yaw)).scale(this.dodgeSide * 0.42D * Math.min(1.3D, 0.7D + 0.3D * this.getScale()));
        this.setDeltaMovement(this.getDeltaMovement().add(side.x, 0.05D, side.z));
        this.hasImpulse = true;
        this.counterLeft = this.dodgeLeft + 3;
    }

    /** Chest to chest, facing each other: they grapple, wheel round pushing, trade short blows, and one throws the other. */
    public void startClinch(DinosaurEntity other, int ticks) {
        float spin = this.random.nextBoolean() ? 1.0F : -1.0F;
        this.clinchWith = other;
        other.clinchWith = this;
        this.clinchLeft = ticks;
        other.clinchLeft = ticks;
        this.clinchSpin = spin;
        other.clinchSpin = spin;
        this.clinchLead = true;
        other.clinchLead = false;
        this.dodgeLeft = 0;
        other.dodgeLeft = 0;
    }

    /** The grapple, every tick of the goal: returns false when it is over (or broken). */
    public boolean clinchTick() {
        DinosaurEntity o = this.clinchWith;
        if (this.clinchLeft <= 0 || o == null || !o.isAlive() || !this.isAlive() || o.clinchWith != this
                || this.distanceTo(o) > (this.getBbWidth() + o.getBbWidth()) * 1.3D + 3.0D) {
            this.clinchLeft = 0;
            this.clinchWith = null;
            return false;
        }
        this.getNavigation().stop();
        double dx = o.getX() - this.getX();
        double dz = o.getZ() - this.getZ();
        float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        float y = Mth.approachDegrees(this.getYRot(), yawTo, 12.0F);
        this.setYRot(y);
        this.setYBodyRot(y);
        this.getLookControl().setLookAt(o, 30.0F, 30.0F);
        // pressing in and wheeling round the middle: both strafe the same way, so the pair turns like a wheel
        float surge = 0.35F + 0.2F * Mth.sin(this.clinchLeft * 0.31F + (this.clinchLead ? 0.0F : 1.6F));
        this.getMoveControl().strafe(surge, 0.55F * this.clinchSpin);
        int beat = this.clinchLeft + (this.clinchLead ? 0 : 7);
        if (beat % 14 == 0) {
            String[] moves = {"shove", "bite_side", "attack_quick", "head_clash", "body_shove", "attack"};
            for (int i = 0, k = this.random.nextInt(moves.length); i < moves.length; i++, k = (k + 1) % moves.length) {
                if (this.hasAnim(moves[k])) {
                    triggerAnim(ACTION_CONTROLLER, moves[k]);
                    break;
                }
            }
            float dmg = (float) this.getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.3F;
            o.hurt(this.damageSources().mobAttack(this), dmg);
            o.pushedBy(this, 0.22D);
        }
        if (--this.clinchLeft == 0 && this.clinchLead) {
            // the throw: the one with more left in it heaves the other off
            float mine = this.getHealth() / this.getMaxHealth() + this.random.nextFloat() * 0.5F;
            float theirs = o.getHealth() / o.getMaxHealth() + this.random.nextFloat() * 0.5F;
            DinosaurEntity win = mine >= theirs ? this : o;
            DinosaurEntity lose = win == this ? o : this;
            win.triggerAnim(ACTION_CONTROLLER, win.hasAnim("shove") ? "shove" : "attack");
            lose.pushedBy(win, 0.9D);
            if (lose.hasAnim("recoil")) {
                lose.triggerAnim(ACTION_CONTROLLER, "recoil");
            }
            lose.stagger = 22;
            lose.hurt(this.damageSources().mobAttack(win), (float) win.getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.6F);
            o.clinchLeft = 0;
            o.clinchWith = null;
            this.clinchWith = null;
        }
        return true;
    }

    /** A sidestep under way, every tick of the goal (true while it moves itself). */
    public boolean dodgeTick(LivingEntity target) {
        if (this.dodgeLeft <= 0) {
            return false;
        }
        this.dodgeLeft--;
        this.getNavigation().stop();
        double dx = target.getX() - this.getX();
        double dz = target.getZ() - this.getZ();
        float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        float y = Mth.approachDegrees(this.getYRot(), yawTo, 15.0F);
        this.setYRot(y);
        this.setYBodyRot(y);
        this.getMoveControl().strafe(-0.15F, 0.9F * this.dodgeSide);
        return true;
    }

    /** The duel's guard (before the wound): a bite from in front of the rival it duels is now and then taken on the
     *  neck / horns / armour, a quarter of it, and the attacker reels. */
    protected float duelBlock(net.minecraft.world.damagesource.DamageSource source, float amount) {
        net.minecraft.world.entity.Entity att = source.getEntity();
        if (!this.level().isClientSide() && this.isDueling() && att instanceof LivingEntity a && a == this.getTarget()
                && this.blockCooldown == 0 && !this.isKnockedOut()) {
            // the bite comes from in front: now and then it takes it on the thick of the neck
            double dx = a.getX() - this.getX();
            double dz = a.getZ() - this.getZ();
            float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
            if (Math.abs(Mth.wrapDegrees(yawTo - this.yBodyRot)) < 55.0F && this.random.nextFloat() < 0.3F && this.clinchLeft == 0) {
                amount *= 0.25F;
                this.blockCooldown = 40;
                triggerAnim(ACTION_CONTROLLER, "block");
                if (a instanceof DinosaurEntity rival) {
                    rival.triggerAnim(ACTION_CONTROLLER, "recoil");
                    rival.stagger = 14;
                    rival.pushedBy(this, 0.3D);
                    this.counterLeft = 8 + this.random.nextInt(4);   // the riposte, out of the block
                }
            }
        }
        return amount;
    }

    /** The duel's end (after the wound): beaten, it gives in and runs. */
    protected void duelAfter(net.minecraft.world.damagesource.DamageSource source, boolean hurt) {
        net.minecraft.world.entity.Entity att = source.getEntity();
        if (hurt && !this.level().isClientSide() && !this.isTame() && this.isDueling() && att instanceof DinosaurEntity rival && rival.hasDuelMoves()
                && this.isAlive() && this.getHealth() < this.getMaxHealth() * (this.territorial ? 0.5F : 0.3F)) {
            this.submitTo(rival);
        }
    }

    /** Beaten: it drops the head and tail, turns away and runs; the winner lets it go and roars. */
    private void submitTo(DinosaurEntity rival) {
        triggerAnim(ACTION_CONTROLLER, "submit");
        this.setTarget(null);
        this.setDueling(false);
        this.yieldedTo = rival.getUUID();
        this.yieldTicks = 2400;
        net.minecraft.world.phys.Vec3 away = net.minecraft.world.entity.ai.util.DefaultRandomPos.getPosAway(this, 24, 7, rival.position());
        if (away != null) {
            this.getNavigation().moveTo(away.x, away.y, away.z, 1.3D);
        }
        if (rival.getTarget() == this) {
            rival.setTarget(null);
            rival.setDueling(false);
            rival.wonDuel();
        }
    }

    /** In a duel: the guard when it stands, the sidesteps when it moves across (forward it walks as usual). */
    protected PlayState duelStance(AnimationState<DinosaurEntity> state) {
        if (!this.hasAnim("guard") || !this.isDueling() || this.isSwimmingDeep() || this.isVehicle() || !this.isAlive()) {
            return null;
        }
        if (this.guardAnim == null) {
            this.guardAnim = RawAnimation.begin().thenLoop(anim("guard"));
            this.strafeLeftAnim = RawAnimation.begin().thenLoop(anim("strafe_left"));
            this.strafeRightAnim = RawAnimation.begin().thenLoop(anim("strafe_right"));
        }
        double vx = this.getX() - this.xo;
        double vz = this.getZ() - this.zo;
        double yaw = Math.toRadians(this.yBodyRot);
        double forward = -Math.sin(yaw) * vx + Math.cos(yaw) * vz;
        double right = -Math.cos(yaw) * vx - Math.sin(yaw) * vz;
        double speed = Math.sqrt(vx * vx + vz * vz);
        if (speed < 0.012D * this.getScale()) {
            return state.setAndContinue(this.guardAnim);
        }
        if (Math.abs(right) > Math.abs(forward) * 0.8D) {
            this.cycleSpeed = Mth.clamp(speed / (0.06D * this.getScale()), 0.6D, 1.6D);
            return state.setAndContinue(right > 0.0D ? this.strafeRightAnim : this.strafeLeftAnim);
        }
        return null;
    }

    /** Standing and turning: it steps round ("turn_left" / "turn_right") instead of spinning on its feet. */
    protected PlayState turnInPlace(AnimationState<DinosaurEntity> state) {
        LivelyMotion m = this.lively();
        if (m == null || !this.hasAnim("turn_left") || state.isMoving() || !this.onGround() || this.isSleeping() || this.isInSittingPose() || this.isKnockedOut()
                || !this.isAlive() || this.isSwimmingDeep() || this.isVehicle() || Math.abs(m.turnRate()) < 1.2F) {
            return null;
        }
        if (this.turnLeftAnim == null) {
            this.turnLeftAnim = RawAnimation.begin().thenLoop(anim("turn_left"));
            this.turnRightAnim = RawAnimation.begin().thenLoop(anim("turn_right"));
        }
        // a faster turn steps faster (about 25 degrees a loop at 1x)
        this.cycleSpeed = Mth.clamp(Math.abs(m.turnRate()) / 1.6D, 0.6D, 1.8D);
        return state.setAndContinue(m.turnRate() < 0.0F ? this.turnLeftAnim : this.turnRightAnim);
    }


    // ------------------------------------------------------------------ combat / misc

    /** Players who studied the species know its weak spots: +20% damage. The world rules scale the rest
     *  (player and creature damage, creature resistance, wild strength; docs/REGRAS.md). */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        amount = this.duelBlock(source, amount);
        boolean hurt = this.hurtInner(source, amount);
        this.duelAfter(source, hurt);
        return hurt;
    }

    private boolean hurtInner(DamageSource source, float amount) {
        if (source.getEntity() instanceof Player player && Research.isStudied(player, this.speciesId())) {
            amount *= 1.2F;
        }
        if (!this.level().isClientSide() && source.getEntity() instanceof LivingEntity attacker && attacker != this) {
            this.provokedBy(attacker);   // 1.7: whoever hits it may be fought back, whatever mod it comes from
        }
        float torporHit = 0.0F;
        if (!this.level().isClientSide() && !this.isTame()) {
            if (source.getDirectEntity() instanceof TranqDart dart) {
                // The dose is delivered only when the arrow's hit is accepted, like other torpor-producing blows.
                torporHit = dart.dose(this.maxTorpor()) * this.narcoticEffect();
            } else if (source.getDirectEntity() instanceof Player striker && source.getEntity() == striker) {
                ItemStack weapon = striker.getMainHandItem();
                if (weapon.getItem() instanceof ClubItem) {
                    torporHit = amount * 2.5F;   // a club stuns: much torpor, half the wound
                    amount *= 0.5F;
                } else if (weapon.isEmpty()) {
                    torporHit = 2.0F + amount * 2.0F;
                } else {
                    torporHit = amount * 0.1F;   // edges and points wound, they hardly stun
                }
            }
        }
        if (!this.level().isClientSide()) {
            amount = Rules.damageTaken(this, source, amount);
        }
        boolean hurt = super.hurt(source, amount);
        if (!hurt && torporHit > 0.0F && this.isAlive() && this.invulnerableTime > 10 && !this.isInvulnerableTo(source)
                && source.getDirectEntity() instanceof TranqDart dart) {
            // v1.1.4: a second dart inside the half second of invulnerability after a hit (two shooters, or bow and
            // blowgun together) used to bounce off and lose its dose. The dose goes in; the dart is spent.
            this.addTorpor(torporHit, source.getEntity());
            dart.dosedThroughInvulnerability(this);
        }
        if (hurt && amount > 0.0F && !this.level().isClientSide() && !this.isTame() && this.isKnockedOut()) {
            this.tameEffectiveness = Math.max(20, this.tameEffectiveness - (this.isAlpha() ? Alphas.WOUND_EFFECTIVENESS : 10));
        }
        if (hurt && torporHit > 0.0F && this.isAlive()) {
            this.addTorpor(torporHit, source.getEntity());
        }
        return hurt;
    }

    /** The bite or blow, scaled by the world rules when the target is not a creature (a creature target scales it
     *  in its own {@link #hurt}): creature damage, wild strength, player resistance. */
    @Override
    public boolean doHurtTarget(Entity target) {
        AttributeInstance attack = this.getAttribute(Attributes.ATTACK_DAMAGE);
        double base = attack != null ? attack.getBaseValue() : 0.0D;
        double factor = !this.level().isClientSide() && attack != null && !(target instanceof DinosaurEntity)
                ? Rules.damageDealt(this, target) : 1.0D;
        boolean hit;
        if (factor != 1.0D) {
            attack.setBaseValue(base * factor);
            try {
                hit = super.doHurtTarget(target);
            } finally {
                attack.setBaseValue(base);
            }
        } else {
            hit = super.doHurtTarget(target);
        }
        if (hit && !this.level().isClientSide() && this.animatesHits()) {
            triggerAnim(ACTION_CONTROLLER, "attack");
        }
        return hit;
    }

    /** Experience of the species (its xpReward, which Animal would ignore) times the XP multiplier rule. */
    @Override
    public int getExperienceReward() {
        int base = this.isBaby() ? 1 + this.random.nextInt(3) : Math.max(1, this.xpReward) * (this.isAlpha() ? 2 : 1);
        return (int) Math.round(base * Rules.of(this.level()).get(Rule.XP_MULTIPLIER));
    }

    /** Animals live on like cows; only the ecosystem's wild, unnamed roamers leave once every player is far away. */
    @Override
    public boolean removeWhenFarAway(double distanceToClosestPlayer) {
        return this.isTransientRoamer() && distanceToClosestPlayer > ROAMER_DESPAWN_SQR;
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
        this.pendingCarcassLoot = loot;  // laid when the body has finished falling (tickDeath)
    }

    /** The body plays its death animation (or sinks into the knocked_out pose) to the end, then the carcass takes its
     *  place in the same pose and yaw (no puff). */
    @Override
    protected void tickDeath() {
        ++this.deathTime;
        if (this.deathTime >= this.dyingTicks() && !this.isRemoved() && this.level() instanceof ServerLevel server) {
            if (this.pendingCarcassLoot != null) {
                server.addFreshEntity(CarcassEntity.of(server, this, this.pendingCarcassLoot));
                this.pendingCarcassLoot = null;
            }
            this.remove(RemovalReason.KILLED);
        }
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
        if (this.isPlatform()) {
            return new ItemStack(ModItems.PLATFORM_SADDLE.get());
        }
        Item own = this.speciesSaddle();
        return new ItemStack(own != null ? own : Items.SADDLE);
    }

    /** The species' own saddle, the only item that saddles it (null = the vanilla saddle). Its saddle comes with
     *  saddlebags: a saddled animal carries its {@link #cargoRows()} rows of cargo without a chest. */
    protected Item speciesSaddle() {
        return null;
    }

    /** Saddled with its own saddle, whose bags hold the cargo. */
    public boolean hasSaddlebags() {
        return this.cargo != null && this.isSaddled() && !this.isPlatform() && this.speciesSaddle() != null;
    }

    /** The cargo can be reached: a chest strapped on, or the saddlebags of its own saddle. */
    public boolean hasCargo() {
        return this.isChested() || this.hasSaddlebags();
    }

    // ------------------------------------------------------------------ cargo

    /** Takes the chest off and drops it with everything in it. */
    protected void dropCargo() {
        if (this.hasSaddlebags() && !this.level().isClientSide()) {
            Containers.dropContents(this.level(), this, this.cargo);   // the bags go with the saddle
        }
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
        this.playSound(ModSounds.SFX_CARGO.get(), 0.5F, 1.2F);
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
        if (!this.level().isClientSide() && this.hasCargo() && this.isTame() && this.isOwnedBy(player)) {
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
                this.gainXp((before - rest.getCount()) * 0.1F);  // one point every 10 items (v0.15.3)
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

        if (this.isKnockedOut()) {
            return this.interactKnockedOut(player, hand, stack);
        }

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
            // v0.12: sneak + empty hand opens the dino screen (orders, cargo, shoulder), which replaced the sneak shortcuts
            if (stack.isEmpty() && player.isSecondaryUseActive() && !player.isPassenger()) {
                if (!client && player instanceof ServerPlayer sp) {
                    com.terrassic.network.DinoNetwork.sendScreen(sp, this);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // a chest strapped on makes a pack animal of it (the cargo inventory, docs/CARGA.md)
            if (this.cargo != null && !this.isBaby() && !this.isChested() && this.speciesSaddle() == null && stack.is(Items.CHEST)) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.setChested(true);
                    this.playSound(ModSounds.SFX_CARGO.get(), 1.0F, 1.0F);
                    player.displayClientMessage(Component.translatable(this.isRideable() ? "message.terrassic.cargo_chest_ride"
                            : "message.terrassic.cargo_chest", this.getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // the platform saddle of the titans (docs/CARGA.md)
            if (this.platformSpecies() && !this.isBaby() && !this.isSaddled() && stack.is(ModItems.PLATFORM_SADDLE.get())) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.setSaddled(true);
                    this.setPlatform(true);
                    this.playSound(ModSounds.SFX_SADDLE_ON.get(), 1.0F, 0.7F);
                    player.displayClientMessage(Component.translatable("message.terrassic.platform", this.getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // saddle
            if (this.isRideable() && !this.isBaby() && !this.isSaddled() && this.speciesSaddle() != null && stack.is(Items.SADDLE)) {
                if (!client) {
                    player.displayClientMessage(Component.translatable("message.terrassic.needs_own_saddle", this.getDisplayName(),
                            this.speciesSaddle().getDescription()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            if (this.isRideable() && !this.isBaby() && !this.isSaddled()
                    && stack.is(this.speciesSaddle() != null ? this.speciesSaddle() : Items.SADDLE)) {
                if (!client) {
                    this.usePlayerItem(player, hand, stack);
                    this.setSaddled(true);
                    this.playSound(ModSounds.SFX_SADDLE_ON.get(), 1.0F, 0.8F);
                }
                return InteractionResult.sidedSuccess(client);
            }
            // shears take the saddle off
            if (this.isSaddled() && !this.isVehicle() && stack.is(Items.SHEARS)) {
                if (!client) {
                    if (this.hasSaddlebags()) {
                        Containers.dropContents(this.level(), this, this.cargo);
                    }
                    this.spawnAtLocation(this.saddleItem());
                    this.setSaddled(false);
                    this.setPlatform(false);
                    this.playSound(ModSounds.SFX_SADDLE_OFF.get(), 1.0F, 1.0F);
                    stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
                }
                return InteractionResult.sidedSuccess(client);
            }
            // shears again take the chest off (with its contents)
            if (this.isChested() && !this.isSaddled() && stack.is(Items.SHEARS)) {
                if (!client) {
                    this.dropCargo();
                    this.playSound(ModSounds.SFX_SADDLE_OFF.get(), 1.0F, 1.0F);
                    stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
                    player.displayClientMessage(Component.translatable("message.terrassic.cargo_off", this.getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
            if (stack.isEmpty()) {
                // ride (saddled) or toggle sit / follow (not saddled; sneaking opened the dino screen above)
                if (this.isSaddled() && !this.isBaby() && !player.isSecondaryUseActive() && this.canAddPassenger(player)) {
                    if (!client) {
                        this.setOrderedToSit(false);
                        this.stopWandering();
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
                    this.stopWandering();
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
                ItemStack bite = stack.copyWithCount(1);
                this.usePlayerItem(player, hand, stack);
                this.tameBite(player, bite);
            }
            return InteractionResult.sidedSuccess(client);
        }
        return super.mobInteract(player, hand);
    }

    protected boolean canBeTamedNow() {
        if (this.getTarget() != null || this.isAlpha()) {   // an alpha only by knockout
            return false;
        }
        return this.tameMethod() == TameMethod.FEEDING || this.isBaby();
    }

    /** Tames the animal for the player (feeding or egg imprinting). */
    public void tameBy(Player player) {
        this.tameBy(player, false);
    }

    /**
     * 1.7 (player feedback: "taming is too easy, at least a stack of meat for the smaller carnivores and several for the
     * bigger ones"): an awake animal is no longer won over by a 1-in-4 roll per bite. Every bite adds to its taming
     * progress, as in the knockout, until it reaches {@link #tameGoal}; then it is tamed at full effectiveness.
     */
    protected void tameBite(Player player, ItemStack food) {
        this.tamer = player.getUUID();
        this.tameProgress += this.biteValue(player, food);
        float goal = this.tameGoal();
        if (this.tameProgress >= goal) {
            if (!this.isBaby()) {
                this.grantTamingBonus(100);   // hand-fed without a fight: full effectiveness
            }
            this.tameBy(player);
            return;
        }
        this.level().broadcastEntityEvent(this, (byte) 6);
        int percent = Mth.floor(100.0F * this.tameProgress / goal);
        int left = Mth.ceil((goal - this.tameProgress) / Math.max(0.01F, this.biteValue(player, food)));
        player.displayClientMessage(Component.translatable("message.terrassic.tame_try", this.getDisplayName(), percent, left), true);
    }

    /** What one bite of this food counts towards taming: prime meat double, a studied species a quarter more, times
     *  the "Taming speed" rule. */
    protected float biteValue(Player player, ItemStack food) {
        float bite = food.is(ModItems.RAW_PRIME_MEAT.get()) ? 2.0F : 1.0F;
        if (Research.isStudied(player, this.speciesId())) {
            bite *= 1.25F;   // studied: it knows what the animal likes best
        }
        return bite * (float) Rules.of(this.level()).get(Rule.TAMING_SPEED);
    }

    /** Tamed by the player; {@code hatched}: it just came out of an egg next to them (the notice says so). */
    public void tameBy(Player player, boolean hatched) {
        this.tameProgress = 0.0F;
        this.tame(player);
        TamedRegistry.update(this);
        if (player instanceof ServerPlayer sp) {
            Research.tamed(sp, this);
        }
        this.navigation.stop();
        this.setTarget(null);
        this.setOrderedToSit(true);
        this.level().broadcastEntityEvent(this, (byte) 7);
        Component sex = Component.translatable(this.isFemale() ? "sex.terrassic.female" : "sex.terrassic.male");
        this.notice(player, hatched ? ModNetwork.NOTICE_FERN : ModNetwork.NOTICE_AMBER,
                Component.translatable(hatched ? "hud.terrassic.notice.hatched" : "hud.terrassic.notice.tamed"),
                Component.translatable("hud.terrassic.notice.name_sex", this.getDisplayName(), sex));
    }

    // ------------------------------------------------------------------ voices (off since v0.14.3)

    /** The voices go quiet while "vozes" is off (config/WorldConfig): calls, roars, threats, hurt, death and the
     *  mod's own steps. Wing flaps, eating, ground hits and the other sounds of things stay. */
    @Override
    public void playSound(SoundEvent sound, float volume, float pitch) {
        if (!WorldConfig.voices() && this.isVoice(sound)) {
            return;
        }
        super.playSound(sound, volume, pitch);
    }

    @Override
    public void playAmbientSound() {
        if (WorldConfig.voices()) {
            super.playAmbientSound();
        }
    }

    @Override
    protected void playHurtSound(DamageSource source) {
        if (WorldConfig.voices()) {
            super.playHurtSound(source);
        }
    }

    /** One of the mod's voices ("voice.&lt;species&gt;.*": calls, threats, hurt, death and its own steps), or this
     *  animal's call or death sound (some borrow vanilla ones). The wing flaps of the flyers ("voice.*.flap") are not a
     *  voice and stay (Mac test: the Pteranodon flew silent). Animals without steps of their own keep vanilla's block
     *  steps, like any Minecraft animal. */
    private boolean isVoice(SoundEvent sound) {
        ResourceLocation id = sound.getLocation();
        return id.getNamespace().equals(Terrassic.MOD_ID) && id.getPath().startsWith("voice.") && !id.getPath().endsWith(".flap")
                || sound == this.getAmbientSound() || sound == this.getDeathSound();
    }

    /** A notice about this animal on the player's HUD (v0.14, client/HudNotices): the right side, the animal in its
     *  drop of amber, {@code title} in the tone's colour (ModNetwork.NOTICE_*) and {@code line} under it. */
    public void notice(LivingEntity to, int tone, Component title, Component line) {
        if (to instanceof ServerPlayer player) {
            ModNetwork.sendNotice(player, tone, title, line, BuiltInRegistries.ENTITY_TYPE.getKey(this.getType()));
        }
    }

    /** Its owner hears of its death wherever they are, with where it lies (vanilla also says it in the chat). */
    @Override
    public void die(DamageSource source) {
        if (!this.level().isClientSide() && !this.dead) {
            this.settleYaw();
            // a call or a bite under way would keep moving the bones over the fall
            this.stopTriggeredAnimation(ACTION_CONTROLLER, null);
        }
        if (!this.level().isClientSide() && this.isAlpha() && !this.isRemoved() && !this.dead) {
            if (!this.isTame()) {
                Alphas.announce(this, "fell", source.getEntity());
            }
            Alphas.spoils(this, source);
            Alphas.gone(this, !this.isTame(), true);
        }
        if (!this.level().isClientSide() && this.isTame() && !this.isRemoved() && !this.dead) {
            TamedRegistry.remove(this);
            Component name = this.hasCustomName() ? this.getCustomName() : this.getType().getDescription();
            this.notice(this.getOwner(), ModNetwork.NOTICE_BLOOD, Component.translatable("hud.terrassic.notice.died", name),
                    Component.translatable("hud.terrassic.notice.where", this.getBlockX(), this.getBlockY(), this.getBlockZ()));
        }
        super.die(source);
    }

    // ------------------------------------------------------------------ the rider's special (v0.14 HUD)

    /** The rider's special and its recharge, {ticks until ready, full recharge}, or null when it has none. Server. */
    protected int[] specialRecharge() {
        return null;
    }

    /** The special's name for the compact HUD ("hud.terrassic.special.&lt;name&gt;"), or null. */
    public String specialName() {
        return null;
    }

    /** Client: how charged the rider's special is (1 = ready), or -1 without one. */
    public float specialCharge() {
        int v = this.entityData.get(DATA_SPECIAL);
        int full = v & 0xFFFF;
        return full == 0 ? -1.0F : 1.0F - Math.min(1.0F, (v >>> 16) / (float) full);
    }

    /** Client: ticks until the rider's special is ready. */
    public int specialTicksLeft() {
        return this.entityData.get(DATA_SPECIAL) >>> 16;
    }

    // ------------------------------------------------------------------ levels (v0.13, docs/NIVEIS.md)

    public DinoLevels levels() {
        return this.levels;
    }

    /** The level shown with the name (synced; 0 on a client that has not heard it yet). */
    public int getLevel() {
        return this.entityData.get(DATA_LEVEL);
    }

    /** The name with the level: "Velociraptor · Nv 34" (the Field Lens, the dino screen, the mount panel, messages). */
    @Override
    public Component getName() {
        Component name = this.hasCustomName() ? super.getName() : this.speciesName();
        int level = this.getLevel();
        return level > 0 ? Component.translatable("entity.terrassic.leveled", name, level) : name;
    }

    /** The species as shown on the HUD (Lens, nameplate, dino screen): "Alpha T. rex" for an alpha. */
    public Component speciesName() {
        Component name = this.getType().getDescription();
        return this.isAlpha() ? Component.translatable("entity.terrassic.alpha", name) : name;
    }

    /** Server: a new animal draws its level (at spawn, or on its first tick when hatched or bred); one loaded from a
     *  save made before the levels keeps its stats if tame (the level-40 spread) and draws if wild. */
    private void ensureLevels() {
        if (this.levels.isRolled() || this.level().isClientSide()) {
            return;
        }
        int fixed = this.fixedWildLevel();
        if (this.legacyLevels && this.isTame()) {
            this.levels.setReference();
        } else if (this.isAlpha() && this.level() instanceof ServerLevel server) {
            int[] band = Alphas.levelBand(server);
            this.levels.rollBetween(this.random, band[0], band[1]);
        } else if (fixed > 0) {
            this.levels.rollBetween(this.random, fixed, fixed);
        } else {
            this.levels.roll(this.random, this.wildLevelCap());
        }
        this.legacyLevels = false;
        this.applyLevelModifiers(true);
    }

    /** A wild level that is not drawn (0 = drawn as usual): the Rift Tyrant is always at the "Max wild level" rule. */
    protected int fixedWildLevel() {
        return 0;
    }

    /** The highest level a wild animal can be born at here: the "Max wild level" rule; with "Levels by distance"
     *  on, 30 within 500 blocks of the world spawn, rising to the full rule at 3,000 blocks. */
    private int wildLevelCap() {
        Rules rules = Rules.of(this.level());
        int max = (int) Math.round(rules.get(Rule.MAX_WILD_LEVEL));
        if (rules.get(Rule.LEVEL_DISTANCE) >= 0.5D) {
            BlockPos spawn = this.level().getSharedSpawnPos();
            double distance = Math.sqrt(Mth.square(this.getX() - spawn.getX()) + Mth.square(this.getZ() - spawn.getZ()));
            double t = Mth.clamp((distance - 500.0D) / 2500.0D, 0.0D, 1.0D);
            max = (int) Math.round(Mth.lerp(t, Math.min(30, max), max));
        }
        return Math.max(1, max);
    }

    /** Health, damage and speed from the level, as permanent modifiers on top of the size ones (saved with the
     *  attributes, applied again on load). Keeps the share of health it had, or fills it. Server only. */
    private void applyLevelModifiers(boolean fill) {
        if (this.level().isClientSide()) {
            return;
        }
        float share = this.getMaxHealth() > 0.0F ? this.getHealth() / this.getMaxHealth() : 1.0F;
        this.levelModifier(Attributes.MAX_HEALTH, LEVEL_HEALTH_ID, DinoLevels.Stat.HEALTH);
        this.levelModifier(Attributes.ATTACK_DAMAGE, LEVEL_DAMAGE_ID, DinoLevels.Stat.ATTACK);
        this.levelModifier(Attributes.MOVEMENT_SPEED, LEVEL_SPEED_ID, DinoLevels.Stat.SPEED);
        this.levelModifier(Attributes.FLYING_SPEED, LEVEL_SPEED_ID, DinoLevels.Stat.SPEED);
        this.setHealth(fill ? this.getMaxHealth() : Math.max(1.0F, share * this.getMaxHealth()));
        this.entityData.set(DATA_LEVEL, this.levels.level());
    }

    private void levelModifier(Attribute attribute, UUID id, DinoLevels.Stat stat) {
        AttributeInstance instance = this.getAttribute(attribute);
        if (instance == null) {
            return;
        }
        instance.removeModifier(id);
        double bonus = this.levels.multiplier(stat) - 1.0D;
        if (Math.abs(bonus) > 1.0E-4D) {
            instance.addPermanentModifier(new AttributeModifier(id, "Level", bonus, AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
    }

    /** Bonus levels for taming a wild adult: half its wild level times the effectiveness (in %). */
    public int tamingBonusLevels(int effectiveness) {
        return (int) (this.levels.wildLevel() * 0.5D * effectiveness / 100.0D);
    }

    /** Adds the taming bonus levels, drawn like the wild ones, and wakes it at full health. */
    protected void grantTamingBonus(int effectiveness) {
        this.ensureLevels();
        this.levels.addWildPoints(this.random, this.tamingBonusLevels(effectiveness));
        this.applyLevelModifiers(true);
    }

    /** A tame animal's experience, times the "Tamed XP" rule; each level gained is a point for the owner, announced
     *  on the action bar. */
    public void gainXp(float amount) {
        if (this.level().isClientSide() || !this.isTame() || amount <= 0.0F) {
            return;
        }
        int gained = this.levels.addXp(amount * (float) Rules.of(this.level()).get(Rule.TAMED_XP));
        if (gained <= 0) {
            return;
        }
        this.applyLevelModifiers(false);
        this.level().playSound(null, this, SoundEvents.PLAYER_LEVELUP, SoundSource.NEUTRAL, 0.6F, 0.8F);
        this.notice(this.getOwner(), ModNetwork.NOTICE_AMBER, Component.translatable("hud.terrassic.notice.level_up"),
                this.getDisplayName());
    }

    /** Experience for every kill, from {@link KillXp} (v0.15.3: by the victim's size and level, no longer its whole
     *  health). Read from the death event, not awardKillScore: Forge gives a tame animal's kills to its owner (the
     *  wolf rule in LivingEntity.hurt), so the animal never heard of them. */
    public static void registerEvents() {
        EntityEvent.LIVING_DEATH.register((entity, source) -> {
            if (source.getEntity() instanceof DinosaurEntity dino && dino != entity && !entity.level().isClientSide()) {
                dino.gainXp(KillXp.of(entity));
            }
            return EventResult.pass();
        });
    }

    /** One point of experience every 20 blocks carried with the owner riding (8 before v0.15.3). */
    private static final double RIDE_XP_BLOCKS = 20.0D;

    private void rideXpTick() {
        if (!this.isTame() || !(this.getControllingPassenger() instanceof Player rider) || !this.isOwnedBy(rider)) {
            this.ridePos = null;
            return;
        }
        Vec3 here = this.position();
        if (this.ridePos != null) {
            double step = Math.sqrt(Mth.square(here.x - this.ridePos.x) + Mth.square(here.z - this.ridePos.z));
            if (step < 4.0D) {   // a teleport is not a ride
                this.rideDistance += step;
            }
            if (this.rideDistance >= RIDE_XP_BLOCKS) {
                int points = (int) (this.rideDistance / RIDE_XP_BLOCKS);
                this.rideDistance -= points * RIDE_XP_BLOCKS;
                this.gainXp(points);
            }
        }
        this.ridePos = here;
    }

    // ------------------------------------------------------------------ knockout taming (docs/DOMESTICACAO.md)

    public boolean isKnockedOut() {
        return this.entityData.get(DATA_KNOCKED_OUT);
    }

    /** Torpor needed to knock it out: grows with its health, so the giants need a long fight or a volley of darts. */
    public float maxTorpor() {
        float gauge = Math.max(10.0F, this.getMaxHealth()) * (float) this.levels.multiplier(DinoLevels.Stat.TORPOR);
        return this.isAlpha() && !this.isTame() ? gauge * Alphas.TORPOR_GAUGE * this.alphaTaming() : gauge;
    }

    public float getTorpor() {
        return this.torpor;
    }

    /** Big biters wake up faster (the plan's "top predators wake sooner"). */
    protected boolean wakesFast() {
        AttributeInstance attack = this.getAttribute(Attributes.ATTACK_DAMAGE);
        return attack != null && attack.getBaseValue() >= 8.0D;
    }

    /** Food bites it needs to be tamed, awake or knocked out (prime meat counts double): {@link #foodGoal()}, a
     *  quarter of it for a young one, more for an alpha. */
    public float tameGoal() {
        float goal = this.foodGoal();
        if (this.isBaby()) {
            goal = Math.max(4.0F, goal * 0.25F);
        }
        return this.isAlpha() ? goal * Alphas.FOOD_GOAL * this.alphaTaming() : goal;
    }

    /**
     * 1.7: the bites a wild adult of the species needs (Field Guide and Pocket Guide show it too). A carnivore
     * ({@link #isHunter}) a stack of 64 for every 100 points of the species' health, from one to five stacks: a
     * Velociraptor or a Troodon one stack, a Carnotaurus two, a T. rex four. The rest about one bite for every 6 points
     * of health, from 6 to 64. The animal's own level and size do not change it.
     */
    public int foodGoal() {
        AttributeInstance health = this.getAttribute(Attributes.MAX_HEALTH);
        double base = health != null ? health.getBaseValue() : 20.0D;
        if (this.isHunter()) {
            return 64 * Mth.clamp(Mth.ceil(base / 100.0D), 1, 5);
        }
        return Mth.clamp((int) Math.round(base / 6.0D), 6, 64);
    }

    /** A meat- or fish-eater with a real bite (4 damage or more): what the stack goals and the rarer spawns mean by
     *  "carnivore" (the tiny scavengers and the fish stay with the rest). */
    public boolean isHunter() {
        return isHunter(this.getType());
    }

    private static final java.util.Map<EntityType<?>, Boolean> HUNTERS = new java.util.concurrent.ConcurrentHashMap<>();

    /** {@link #isHunter()} for a type, from the Field Guide's diet and the type's default attack (any thread). */
    @SuppressWarnings("unchecked")
    public static boolean isHunter(EntityType<?> type) {
        return HUNTERS.computeIfAbsent(type, t -> {
            net.minecraft.resources.ResourceLocation id = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(t);
            com.terrassic.research.GuideSpecies g = com.terrassic.research.GuideSpecies.byId(id.getPath());
            if (g == null || !Terrassic.MOD_ID.equals(id.getNamespace())
                    || !(g.diet().equals("carnivore") || g.diet().equals("piscivore"))) {
                return false;
            }
            try {
                var supplier = net.minecraft.world.entity.ai.attributes.DefaultAttributes.getSupplier(
                        (EntityType<? extends LivingEntity>) t);
                return supplier.hasAttribute(Attributes.ATTACK_DAMAGE) && supplier.getBaseValue(Attributes.ATTACK_DAMAGE) >= 4.0D;
            } catch (RuntimeException e) {
                return false;
            }
        });
    }

    /** 1.7: brings a saved animal's base health to its species' current value (the health table went up), keeping
     *  the share of health it had. Its levels, size and alpha bonus are modifiers and stay as they were. */
    private void refreshBaseHealth() {
        AttributeInstance health = this.getAttribute(Attributes.MAX_HEALTH);
        if (health == null || this.level().isClientSide()) {
            return;
        }
        double want;
        try {
            @SuppressWarnings("unchecked")
            EntityType<? extends LivingEntity> type = (EntityType<? extends LivingEntity>) this.getType();
            want = net.minecraft.world.entity.ai.attributes.DefaultAttributes.getSupplier(type).getBaseValue(Attributes.MAX_HEALTH);
        } catch (RuntimeException e) {
            return;
        }
        if (Math.abs(health.getBaseValue() - want) < 1.0E-3D) {
            return;
        }
        float share = this.getMaxHealth() > 0.0F ? this.getHealth() / this.getMaxHealth() : 1.0F;
        health.setBaseValue(want);
        this.setHealth(Math.max(1.0F, share * this.getMaxHealth()));
    }

    /** What an unconscious animal accepts from the hand (its usual food). */
    protected boolean koFood(ItemStack stack) {
        return this.isFood(stack);
    }

    /** Adds torpor (blunt blows, fists, narcotic darts); a wild animal whose gauge fills collapses. */
    public void addTorpor(float amount, Entity by) {
        if (this.level().isClientSide() || this.isTame() || amount <= 0.0F || !this.isAlive()) {
            return;
        }
        this.torpor = Math.min(this.maxTorpor(), this.torpor + amount);
        if (!this.isKnockedOut() && this.torpor >= this.maxTorpor()) {
            this.knockOut(by);
        }
    }

    private void knockOut(Entity by) {
        this.entityData.set(DATA_KNOCKED_OUT, true);
        this.settleYaw();
        this.tameEffectiveness = 100;
        this.navigation.stop();
        this.setTarget(null);
        this.setAggressive(false);
        this.setSleeping(false);
        this.ejectPassengers();
        if (this.isPassenger()) {
            this.stopRiding();
        }
        this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 0.6F);
        if (by instanceof Player player) {
            this.tamer = player.getUUID();
            player.displayClientMessage(Component.translatable("message.terrassic.knocked_out", this.getDisplayName()), true);
        }
    }

    /** An alpha knocked out already tried once to rise (reset when it wakes). */
    private boolean stirred;

    /** Drains the torpor; an unconscious animal wakes when it reaches zero (half the taming progress is lost). */
    private void torporTick() {
        float max = this.maxTorpor();
        if (this.isKnockedOut()) {
            // 1.7 (player feedback: "the stun is way too long, it should be about 20 seconds"): the "Knockout duration"
            // rule from a full gauge, 20 s by default (three quarters for the big biters), unless kept down with
            // narcotics; it does not drain while it is being fed (EATING_HOLD_TICKS after each bite), so a tamer with
            // the food at hand finishes. An alpha: one minute, and it gets up at a quarter of the gauge.
            if (this.level().getGameTime() < this.eatingUntil) {
                return;
            }
            this.torpor -= this.isAlpha() ? max * (1.0F - Alphas.WAKE_SHARE) / (Alphas.KO_SECONDS * 20.0F)
                    : max / (this.knockoutSeconds() * 20.0F);
            if (this.torpor <= (this.isAlpha() ? max * Alphas.WAKE_SHARE : 0.0F)) {
                this.wakeUp();
            } else if (this.isAlpha() && !this.stirred && this.torpor <= max * Alphas.WAKE_SHARE * 1.25F) {
                this.stirred = true;     // about 5 s before it gets up: it tries once to rise (the tamer's warning)
                this.nearlyAwake();
            } else if (this.tickCount % 60 == 0 && this.level() instanceof ServerLevel server) {
                server.sendParticles(net.minecraft.core.particles.ParticleTypes.CLOUD, this.getX(),
                        this.getY() + this.getBbHeight() * 0.6D, this.getZ(), 1, 0.2D, 0.1D, 0.2D, 0.0D);
            }
        } else {
            float recovery = this.isAlpha() ? Alphas.AWAKE_RECOVERY : 1.0F;
            this.torpor = Math.max(0.0F, this.torpor - max * 0.02F * recovery / 20.0F);   // awake: 2% of the gauge a second
        }
    }

    /** Seconds it stays down from a full gauge (the "Knockout duration" rule; three quarters for the big biters). */
    protected float knockoutSeconds() {
        float seconds = (float) Rules.of(this.level()).get(Rule.KNOCKOUT_SECONDS);
        return Math.max(1.0F, this.wakesFast() ? seconds * 0.75F : seconds);
    }

    /** Knocked out and about to wake (an alpha, a few seconds before it gets up); a rig may show it. */
    protected void nearlyAwake() {
    }

    private void wakeUp() {
        this.stirred = false;
        this.torpor = 0.0F;
        this.entityData.set(DATA_KNOCKED_OUT, false);
        this.tameProgress *= 0.5F;
        triggerAnim(ACTION_CONTROLLER, "wake");
        Player tamer = this.tamer != null ? this.level().getPlayerByUUID(this.tamer) : null;
        if (tamer != null && tamer.distanceToSqr(this) < 48.0D * 48.0D) {
            this.notice(tamer, ModNetwork.NOTICE_RIFT, Component.translatable("hud.terrassic.notice.woke"), this.getDisplayName());
            if (!tamer.getAbilities().instabuild && this.getAttribute(Attributes.ATTACK_DAMAGE) != null) {
                this.setTarget(tamer);
            }
        }
    }

    private InteractionResult interactKnockedOut(Player player, InteractionHand hand, ItemStack stack) {
        boolean client = this.level().isClientSide();
        if (stack.is(ModItems.SLEEP_HERB.get())) {
            if (!client) {
                this.usePlayerItem(player, hand, stack);
                this.torpor = Math.min(this.maxTorpor(), this.torpor + this.maxTorpor() * 0.35F * this.narcoticEffect());
                this.playSound(SoundEvents.GENERIC_EAT, 0.6F, 0.8F);
                this.knockoutStatus(player);
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (this.acceptsKoFood(stack)) {
            if (!client && this.isAlpha() && !this.alphaMayBeTamedBy(player)) {
                return InteractionResult.sidedSuccess(client);
            }
            if (!client) {
                float bite = this.biteValue(player, stack);
                this.usePlayerItem(player, hand, stack);
                this.tamer = player.getUUID();
                this.tameProgress += bite;
                this.eatingUntil = this.level().getGameTime() + EATING_HOLD_TICKS;   // eating, it stays down
                this.feed(10);
                triggerAnim(ACTION_CONTROLLER, "eat");
                this.playSound(SoundEvents.GENERIC_EAT, 0.7F, 0.9F);
                if (this.tameProgress >= this.tameGoal()) {
                    this.finishKnockoutTaming(player);
                } else {
                    this.knockoutStatus(player);
                }
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (!client) {
            this.knockoutStatus(player);
        }
        return InteractionResult.sidedSuccess(client);
    }

    /** The gauges on the action bar: torpor, taming progress and effectiveness. */
    private void knockoutStatus(Player player) {
        int progress = Mth.floor(100.0F * Math.min(1.0F, this.tameProgress / this.tameGoal()));
        player.displayClientMessage(Component.translatable("message.terrassic.ko_status", this.getDisplayName(),
                Mth.ceil(this.torpor), Mth.ceil(this.maxTorpor()), progress, this.tameEffectiveness), true);
    }

    /** Foods each species accepts from the hand, found once by testing every item (the Field Lens lists them). */
    private static final java.util.Map<String, List<String>> FOODS = new java.util.HashMap<>();

    /** The item ids it eats from the hand (at most 8; the Field Lens and the Pocket Guide show them). */
    public List<String> acceptedFoods() {
        return FOODS.computeIfAbsent(this.speciesId(), id -> {
            List<String> found = new java.util.ArrayList<>();
            for (Item item : net.minecraft.core.registries.BuiltInRegistries.ITEM) {
                if (found.size() < 8 && item != Items.AIR && this.koFood(new ItemStack(item))) {
                    found.add(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(item).toString());
                }
            }
            return found;
        });
    }

    /** What the Field Lens shows to the player looking at it (network/LensNetwork): the values only the server
     *  knows (torpor, taming progress, effectiveness, time to wake, cargo) plus the accepted foods. */
    // ------------------------------------------------------------------ the dino screen and the mounted controls (v0.12)

    /** Ticks between two attacks ordered by the rider ({@link #riderAttack}). */
    protected int riderAttackInterval() {
        return 16;
    }

    /** Game time of the last attack ordered by the rider. */
    private long lastRiderAttack = -1000L;

    /** What the dino screen shows (client/DinoScreen): the Field Lens card and the orders it takes now. */
    public CompoundTag screenInfo(Player viewer) {
        CompoundTag t = this.lensInfo(viewer);
        t.putBoolean("Sitting", this.isOrderedToSit());
        t.putBoolean("Wandering", this.isWandering());
        t.putString("Stance", this.stance.key);
        t.putBoolean("HasCargo", this.cargo != null && (this.isChested() || this.hasSaddlebags()));
        t.putBoolean("CanPerch", this.canPerch() && !this.isBaby());
        t.putBoolean("Ridden", this.hasPassenger(viewer));
        t.putBoolean("Rideable", this.isRideable());
        t.putInt("TamedLevels", this.levels.tamedLevels());
        t.putFloat("Xp", this.levels.xp());
        t.putInt("XpNext", DinoLevels.xpToNext(this.levels.tamedLevels()));
        CompoundTag stats = new CompoundTag();
        for (DinoLevels.Stat stat : DinoLevels.Stat.values()) {
            stats.putFloat(stat.key, (float) this.levels.multiplier(stat));
        }
        t.put("Stats", stats);
        return t;
    }

    /**
     * An order from the owner's dino screen (network/DinoNetwork checks owner and distance): "sit", "follow", "wander",
     * "stop", "stance" (the next stance), "cargo", "perch" or "up:&lt;stat&gt;" (spend a level point). Returns true when the
     * screen should be sent again with the new state.
     */
    public boolean screenOrder(ServerPlayer player, String order) {
        switch (order) {
            case "wander" -> {
                this.wanderHere();
                player.displayClientMessage(Component.translatable("message.terrassic.wander", this.getDisplayName()), true);
                return true;
            }
            case "stop" -> {
                this.stopFighting();
                player.displayClientMessage(Component.translatable("message.terrassic.stop", this.getDisplayName()), true);
                return true;
            }
            case "stance" -> {
                this.setStance(this.stance.next());
                player.displayClientMessage(Component.translatable("message.terrassic.stance", this.getDisplayName(),
                        Component.translatable("gui.terrassic.dino.stance." + this.stance.key)), true);
                return true;
            }
            case "sit", "follow" -> {
                boolean sit = order.equals("sit");
                this.setOrderedToSit(sit);
                this.stopWandering();
                this.jumping = false;
                this.navigation.stop();
                this.setTarget(null);
                player.displayClientMessage(Component.translatable(sit ? "message.terrassic.sit" : "message.terrassic.follow",
                        this.getDisplayName()), true);
                return true;
            }
            case "cargo" -> {
                if (this.cargo != null && (this.isChested() || this.hasSaddlebags())) {
                    this.openCargo(player);
                }
                return false;
            }
            case "perch" -> {
                if (this.canPerch() && !this.isBaby() && !this.isPassenger() && !player.isVehicle() && !player.isPassenger()) {
                    this.perchOn(player);
                }
                return false;
            }
            default -> {
                DinoLevels.Stat stat = order.startsWith("up:") ? DinoLevels.Stat.byKey(order.substring(3)) : null;
                if (stat != null && this.levels.spend(stat)) {
                    this.applyLevelModifiers(false);
                    this.playSound(SoundEvents.EXPERIENCE_ORB_PICKUP, 0.5F, 0.8F);
                    return true;
                }
                return false;
            }
        }
    }

    // ------------------------------------------------------------------ orders: stop, stance, wander (v0.16, docs/ORDENS.md)

    /** How far from where it was told to wander it roams (blocks). */
    public static final int WANDER_RADIUS = 16;
    /** Beyond this it walks back to its wander spot (dragged off by a fight, a herd, a flight). */
    private static final int WANDER_LEASH = 24;
    /** How long a "Stop" keeps it out of fights (ticks). */
    public static final int CALM_TICKS = 200;
    /** How near a monster or wild dinosaur must come for the aggressive stance to go for it (blocks). */
    public static final double AGGRESSIVE_RANGE = 12.0D;

    public DinoStance getStance() {
        return this.stance;
    }

    public void setStance(DinoStance stance) {
        this.stance = stance;
        if (stance == DinoStance.PASSIVE) {
            this.setTarget(null);
            this.setAggressive(false);
        }
    }

    /** Told to wander around a spot instead of following its owner. */
    public boolean isWandering() {
        return this.wanderPos != null;
    }

    /** Roams within {@link #WANDER_RADIUS} blocks of where it stands, neither following nor sitting. */
    public void wanderHere() {
        this.setOrderedToSit(false);
        this.jumping = false;
        this.navigation.stop();
        this.wanderPos = this.blockPosition();
        this.restrictTo(this.wanderPos, WANDER_RADIUS);
    }

    /** Back to following or waiting (an order, a rider, the shoulder). */
    public void stopWandering() {
        if (this.wanderPos != null) {
            this.wanderPos = null;
            this.clearRestriction();
        }
    }

    /** "Stop": it lets go of its target at once and keeps out of fights for {@link #CALM_TICKS}, even if hit. */
    public void stopFighting() {
        this.calmUntil = this.level().getGameTime() + CALM_TICKS;
        this.setTarget(null);
        this.setAggressive(false);
        this.navigation.stop();
    }

    /**
     * The whistle's "attack my target" (1.5, entity/Whistle): it goes for the target even where its neutral stance
     * would stay out (a player, someone's tamed animal) and even right after a "Stop". It refuses in the passive
     * stance, while waiting, as a young one, when its species flees instead of fighting, against its owner's own
     * animals, and as a swimmer when the target is out of the water. True when it took the target.
     */
    public boolean orderAttack(LivingEntity target) {
        if (target == null || target == this || !target.isAlive() || this.isOrderedToSit() || this.isBaby()
                || !this.fightsInStance() || this.isKnockedOut() || this.isSleeping()
                || this instanceof SwimmingDinosaur && !target.isInWater()) {
            return false;
        }
        this.calmUntil = Long.MIN_VALUE;
        this.provokedBy(target);   // 1.7: the owner's order lets it fight a mob the rules would spare
        if (!this.canAttack(target)) {
            return false;
        }
        this.setTarget(target);
        this.setAggressive(true);
        return true;
    }

    /** Within the ten seconds after a "Stop". */
    public boolean isCalmed() {
        return this.level().getGameTime() < this.calmUntil;
    }

    /** Whether the species fights at all (herbivores that flee do not take the aggressive stance). */
    protected boolean fightsInStance() {
        return true;
    }

    /** The aggressive stance looks for a target now: tame, grown, free to move and awake. */
    public boolean huntsInAggressiveStance() {
        return this.isTame() && this.stance == DinoStance.AGGRESSIVE && this.fightsInStance() && !this.isBaby()
                && !this.isOrderedToSit() && !this.isVehicle() && !this.isPassenger() && !this.isKnockedOut()
                && !this.isSleeping() && !this.isCalmed();
    }

    /** What the aggressive stance goes for: monsters but creepers, and grown wild dinosaurs, near it (swimmers: in the water). */
    public boolean provokesAggressive(LivingEntity e) {
        if (e.distanceToSqr(this) > AGGRESSIVE_RANGE * AGGRESSIVE_RANGE || (this instanceof SwimmingDinosaur && !e.isInWater())) {
            return false;
        }
        return e instanceof Enemy && !(e instanceof Creeper)
                || e.getType().getCategory() == net.minecraft.world.entity.MobCategory.MONSTER && !(e instanceof Creeper)
                && !(e instanceof OwnableEntity pet && pet.getOwnerUUID() != null)
                || e instanceof DinosaurEntity d && !d.isTame() && !d.isBaby() && !d.isKnockedOut();
    }

    /** v1.6: never a mob the world rules spare (Rules.spares), however the target was picked (packs, alarms, orders);
     *  1.7: unless it provoked this one ({@link #spared}). */
    @Override
    public void setTarget(LivingEntity target) {
        super.setTarget(target != null && this.spared(target) ? null : target);
    }

    /** 1.7: lets it fight this mob for the next {@link #PROVOKED_TICKS} even if the rules spare it (never a
     *  protected one: Rules.sparesAlways). */
    public void provokedBy(LivingEntity e) {
        if (e != null && e != this && !this.level().isClientSide() && !Rules.sparesAlways(e)) {
            if (this.provoked.size() > 16) {
                long now = this.level().getGameTime();
                this.provoked.values().removeIf(until -> until < now);
            }
            this.provoked.put(e.getUUID(), this.level().getGameTime() + PROVOKED_TICKS);
        }
    }

    /**
     * 1.7 (player feedback: "dinos can't defend themselves from mobs from other mods, and tames can't attack them, not
     * even when commanded"): a mob the rules spare from the hunt is still fair game once it picks the fight. It hit
     * this one lately, or the owner gave the order ({@link #provokedBy}), or it is going for this one, its owner or
     * another dinosaur, or (tamed) it hurt the owner or the owner hit it in the last ten seconds.
     */
    private boolean provokes(LivingEntity t) {
        long now = this.level().getGameTime();
        Long until = this.provoked.get(t.getUUID());
        if (until != null) {
            if (now < until) {
                return true;
            }
            this.provoked.remove(t.getUUID());
        }
        LivingEntity owner = this.isTame() ? this.getOwner() : null;
        if (t instanceof Mob mob && mob.getTarget() != null
                && (mob.getTarget() == this || mob.getTarget() instanceof DinosaurEntity || owner != null && mob.getTarget() == owner)) {
            return true;
        }
        return owner != null && (owner.getLastHurtByMob() == t
                || owner.getLastHurtMob() == t && owner.tickCount - owner.getLastHurtMobTimestamp() < 200);
    }

    /** Whether the world rules keep it off this mob now (see {@link #provokes}). */
    private boolean spared(LivingEntity t) {
        return Rules.sparesAlways(t) || Rules.spares(t) && !this.provokes(t);
    }

    /** Tamed by its own owner: a wolf, a horse, another dinosaur. */
    private boolean sameOwner(LivingEntity target) {
        return target instanceof OwnableEntity pet && this.getOwnerUUID() != null && this.getOwnerUUID().equals(pet.getOwnerUUID());
    }

    /**
     * Every target goal asks this, when it starts and on every tick it runs: a tame animal in the passive stance or
     * calmed by a "Stop" fights nobody, and none ever fights another animal of its owner (the vanilla rule let them,
     * so one stray blow of the owner set the rest of the herd on it).
     */
    @Override
    public boolean canAttack(LivingEntity target) {
        if (this.spared(target) || Rules.sparesPlayer(this, target)) {
            return false;
        }
        // it gave in to this one in a duel: it keeps away from it for a while
        if (this.yieldTicks > 0 && target != null && target.getUUID().equals(this.yieldedTo)) {
            return false;
        }
        if (this.isTame() && (this.stance == DinoStance.PASSIVE || this.isCalmed() || this.sameOwner(target))) {
            return false;
        }
        return super.canAttack(target);
    }

    /**
     * The owner's fights (the vanilla "owner hurt" and "owner hurt by" goals). Never against the owner's own animals,
     * nor a player the owner may not harm (PvP off, same team), as the wolf. In the neutral stance it stays out of a
     * fight the owner starts against a player or someone's tamed animal; defending the owner from them still counts
     * (the target hurt the owner in the last five seconds).
     */
    @Override
    public boolean wantsToAttack(LivingEntity target, LivingEntity owner) {
        if (target == owner || this.sameOwner(target)) {
            return false;
        }
        if (target instanceof Player victim && owner instanceof Player player && !player.canHarmPlayer(victim)) {
            return false;
        }
        if (this.stance == DinoStance.NEUTRAL && owner.getLastHurtByMob() != target
                && (target instanceof Player || target instanceof OwnableEntity pet && pet.getOwnerUUID() != null)) {
            return false;
        }
        return super.wantsToAttack(target, owner);
    }

    /** Server, every tick: drop a target it may no longer fight, keep the wander spot. */
    private void ordersTick() {
        if (!this.isTame()) {
            return;
        }
        LivingEntity target = this.getTarget();
        if (target != null && !this.canAttack(target)) {
            // a target set from outside the target goals (a herd mate's alarm) while passive or calmed
            this.setTarget(null);
            this.setAggressive(false);
        }
        if (this.wanderPos == null || this.isVehicle() || this.isPassenger() || this.isLeashed() || this.isOrderedToSit()) {
            return;
        }
        if (!this.hasRestriction()) {
            this.restrictTo(this.wanderPos, WANDER_RADIUS);   // a leash taken off clears it
        }
        if ((this.tickCount + this.getId()) % 20 == 0 && this.getTarget() == null
                && this.wanderPos.distSqr(this.blockPosition()) > WANDER_LEASH * WANDER_LEASH && this.navigation.isDone()) {
            this.navigation.moveTo(this.wanderPos.getX() + 0.5D, this.wanderPos.getY(), this.wanderPos.getZ() + 0.5D, 1.0D);
        }
    }

    /** The server tells every tracking player who rides whom, except the vehicle itself: without this the owner alone
     *  would keep seeing the animal where it stood. */
    private void tellOwnerAboutPerch(Player owner) {
        if (owner instanceof ServerPlayer player) {
            player.connection.send(new ClientboundSetPassengersPacket(owner));
        }
    }

    /** A shoulder animal hops onto its owner's shoulder (the owner sneaks later to shake it off). */
    protected void perchOn(Player player) {
        this.setOrderedToSit(false);
        this.stopWandering();
        this.navigation.stop();
        this.setTarget(null);
        this.startRiding(player, true);
        this.tellOwnerAboutPerch(player);
        this.perchGrace = 60;
        player.displayClientMessage(Component.translatable("message.terrassic.perch", this.getDisplayName()), true);
    }

    /**
     * The rider's attack (left click while riding, client/DinoControls): the mount strikes the creature in front of it
     * nearest to where the rider looks, within the reach of its head, or snaps at the air.
     */
    public void riderAttack(ServerPlayer rider) {
        long now = this.level().getGameTime();
        if (now - this.lastRiderAttack < this.riderAttackInterval() || this.isKnockedOut() || this.isSleeping()) {
            return;
        }
        this.lastRiderAttack = now;
        this.startRiderAttack(this.riderTarget(rider));
    }

    /** Plays the attack and lands the hit (null = nothing in reach: it snaps at the air). */
    protected void startRiderAttack(LivingEntity target) {
        if (target == null || !this.doHurtTarget(target) || !this.animatesHits()) {
            triggerAnim(ACTION_CONTROLLER, "attack");
        }
    }

    /** How far from its centre the mount's head reaches. */
    protected double riderReach() {
        return this.getBbWidth() * 0.5D + 2.5D * Math.max(0.6F, this.getScale());
    }

    /** Within the reach of the head (edge of the target's box, horizontally; a little up and down). */
    protected boolean inRiderReach(LivingEntity target) {
        double dx = target.getX() - this.getX();
        double dz = target.getZ() - this.getZ();
        double reach = this.riderReach() + target.getBbWidth() * 0.5D;
        return dx * dx + dz * dz <= reach * reach && target.getY() < this.getY() + this.getBbHeight() + 1.5D
                && target.getY() + target.getBbHeight() > this.getY() - 1.5D;
    }

    /** The creature in reach in front of the mount (within 60 degrees of where the rider looks), nearest to that line. */
    protected LivingEntity riderTarget(Player rider) {
        double reach = this.riderReach() + 2.0D;
        Vec3 look = rider.getViewVector(1.0F);
        double lookYaw = Math.atan2(look.z, look.x);
        LivingEntity best = null;
        double bestAngle = Math.toRadians(60.0D);
        for (LivingEntity e : this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(reach, 2.0D, reach),
                c -> c != this && c != rider && c.isAlive() && !this.hasPassenger(c) && !c.isAlliedTo(rider)
                        && !(c instanceof DinosaurEntity d && d.isTame() && d.isOwnedBy(rider))
                        && !(c instanceof Player p && (p.isCreative() || p.isSpectator())))) {
            if (!this.inRiderReach(e)) {
                continue;
            }
            double angle = Math.abs(Mth.wrapDegrees((float) Math.toDegrees(Math.atan2(e.getZ() - this.getZ(), e.getX() - this.getX()) - lookYaw)));
            double rad = Math.toRadians(angle);
            if (rad < bestAngle) {
                bestAngle = rad;
                best = e;
            }
        }
        return best;
    }

    public CompoundTag lensInfo(Player viewer) {
        CompoundTag t = new CompoundTag();
        t.putBoolean("Female", this.isFemale());
        t.putBoolean("Alpha", this.isAlpha());
        t.putFloat("Size", this.getAdultSize());
        t.putBoolean("Baby", this.isBaby());
        t.putFloat("Growth", this.isBaby() ? this.entityData.get(DATA_GROWTH) : 1.0F);
        t.putFloat("Health", this.getHealth());
        t.putFloat("MaxHealth", this.getMaxHealth());
        t.putInt("Hunger", this.getHunger());
        t.putBoolean("Tame", this.isTame());
        t.putBoolean("Mine", this.isOwnedBy(viewer));
        LivingEntity owner = this.getOwner();
        if (owner != null) {
            t.putString("Owner", owner.getName().getString());
        }
        // feeding species can also be knocked out and fed; the rest only by knockout (or as babies)
        t.putString("Method", this.isTame() ? "" : this.isBaby() ? "feed"
                : this.tameMethod() == TameMethod.FEEDING ? "feed_or_knockout" : "knockout");
        // 1.7: the bites still needed (the taming goal minus the progress, at this viewer's bite value)
        t.putInt("Chance", Mth.ceil(Math.max(0.0F, this.tameGoal() - this.tameProgress) / Math.max(0.01F, this.biteValue(viewer, ItemStack.EMPTY))));
        t.putBoolean("KnockedOut", this.isKnockedOut());
        t.putFloat("Torpor", this.torpor);
        t.putFloat("MaxTorpor", this.maxTorpor());
        t.putFloat("Progress", this.tameProgress);
        t.putFloat("Goal", this.tameGoal());
        t.putInt("Effectiveness", this.tameEffectiveness);
        t.putInt("Level", this.levels.level());
        if (this.isKnockedOut()) {
            t.putInt("BonusLevels", this.tamingBonusLevels(this.tameEffectiveness));
        }
        if (this.isOwnedBy(viewer)) {
            t.putInt("Points", this.levels.unspent());
        }
        if (this.isKnockedOut()) {
            t.putInt("WakeSeconds", this.isAlpha()
                    ? Mth.ceil(Math.max(0.0F, this.torpor / this.maxTorpor() - Alphas.WAKE_SHARE) / (1.0F - Alphas.WAKE_SHARE) * Alphas.KO_SECONDS)
                    : Mth.ceil(this.torpor * this.knockoutSeconds() / this.maxTorpor()));
        }
        t.putBoolean("Saddled", this.isSaddled());
        if (this.cargo != null && this.hasCargo()) {
            int used = 0;
            for (int i = 0; i < this.cargo.getContainerSize(); i++) {
                if (!this.cargo.getItem(i).isEmpty()) {
                    used++;
                }
            }
            t.putInt("CargoUsed", used);
            t.putInt("CargoSize", this.cargo.getContainerSize());
        }
        ListTag foods = new ListTag();
        for (String id : this.isAlpha() && !this.isTame() ? List.of("terrassic:raw_prime_meat") : this.acceptedFoods()) {
            foods.add(net.minecraft.nbt.StringTag.valueOf(id));
        }
        t.put("Foods", foods);
        return t;
    }

    /** Wakes up tame at full health, with bonus levels for an effective taming (few wounds while asleep). */
    private void finishKnockoutTaming(Player player) {
        int effectiveness = this.tameEffectiveness;
        this.entityData.set(DATA_KNOCKED_OUT, false);
        this.torpor = 0.0F;
        this.tameProgress = 0.0F;
        this.tamer = null;
        // bonus levels instead of the old +20% health (animals tamed before v0.13 keep theirs, saved with the attributes)
        this.grantTamingBonus(effectiveness);
        this.tameBy(player);
        if (this.isAlpha()) {
            Alphas.gone(this, true, false);
            Alphas.tamed(player, this);
            Alphas.announce(this, "tamed", player);
            this.applyAlphaModifiers();
        }
        triggerAnim(ACTION_CONTROLLER, "tame");
        player.sendSystemMessage(Component.translatable("message.terrassic.ko_tamed", this.getDisplayName(), effectiveness));
    }

    /** Unconscious or tied by a bola: no goals, no steering (LivingEntity skips the AI of an immobile mob). */
    @Override
    protected boolean isImmobile() {
        return super.isImmobile() || this.isKnockedOut() || this.isEntangled();
    }

    // ------------------------------------------------------------------ bola (v1.1, docs/ARMAS.md; entity/ThrownBola)

    /** Server ticks left tied; 0 when free. */
    private int entangledTicks;

    /** Legs (or wings) bound by a bola: it can neither move, fight nor fly. Readable on both sides. */
    public boolean isEntangled() {
        return this.entityData.get(DATA_ENTANGLED);
    }

    /** Ties it for the given ticks (server). A flyer drops (FlyingDinosaur turns its lift off while tied). */
    public void entangle(int ticks) {
        this.entangledTicks = Math.max(this.entangledTicks, ticks);
        this.entityData.set(DATA_ENTANGLED, true);
        this.getNavigation().stop();
        Vec3 v = this.getDeltaMovement();
        this.setDeltaMovement(0.0D, Math.min(v.y, 0.0D), 0.0D);
    }

    /** Server, every tick while tied: when the time is up it works free and the bola falls, whole half of the times. */
    private void entangledTick() {
        if (--this.entangledTicks > 0) {
            return;
        }
        this.entangledTicks = 0;
        this.entityData.set(DATA_ENTANGLED, false);
        this.playSound(SoundEvents.LEASH_KNOT_BREAK, 0.8F, 1.0F);
        if (this.random.nextBoolean()) {
            this.spawnAtLocation(new ItemStack(ModItems.BOLA.get()), 0.2F);
        }
    }

    // ------------------------------------------------------------------ stuck darts (v1.1.4, docs/ARMAS.md)

    /** Server ticks until the next stuck dart falls out. */
    private int stuckDartTicks;

    /** How many narcotic darts are stuck in it (both sides). */
    public int getStuckDarts() {
        return this.entityData.get(DATA_STUCK_DARTS);
    }

    /** A dart went in and stays in the hide for a while (server). */
    public void addStuckDart() {
        this.entityData.set(DATA_STUCK_DARTS, Math.min(this.getStuckDarts() + 1, 16));
        this.entityData.set(DATA_DART_ZONES, this.entityData.get(DATA_DART_ZONES) << 2 | this.hitZone & 3);
    }

    /** Where the i-th stuck dart went in (0 = the newest): 0 body, 1 head or neck, 2 tail (1.7, hit parts). */
    public int stuckDartZone(int i) {
        return i >= 16 ? 0 : this.entityData.get(DATA_DART_ZONES) >>> (2 * i) & 3;
    }

    /** Darts work loose one at a time, like arrows in a player: the more there are, the faster they fall. */
    private void stuckDartTick() {
        int darts = this.getStuckDarts();
        if (this.stuckDartTicks <= 0) {
            this.stuckDartTicks = 20 * Math.max(5, 30 - darts);
        }
        if (--this.stuckDartTicks <= 0) {
            this.entityData.set(DATA_STUCK_DARTS, darts - 1);
        }
    }

    // ------------------------------------------------------------------ shoulder perch

    /** True while riding on a player's shoulder. */
    public boolean isPerched() {
        return this.getVehicle() instanceof Player;
    }

    /** Client: the live motion layer (tail spring, bank, turn rate), for the species that have it (LivelyMotion). */
    private LivelyMotion lively;

    /** Whether it stands and fights a duel with a big predator (circling, guarding, blocking) instead of being plain
     *  prey: the T. rex's ApexBiteGoal duels such targets. */
    public boolean fightsInDuel() {
        return false;
    }

    /** Whether this species gets the live motion layer (tail spring, lean into curves, panting; feet on the ground
     *  for the bipeds): every species remade by hand (Eras.REMADE), 06/11/2026. */
    protected boolean livelyMotion() {
        return com.terrassic.config.Eras.REMADE.contains(this.speciesId());
    }

    /** Whether it walks on two legs (the live layer puts both feet on the ground under it). */
    public boolean livelyBiped() {
        return BIPEDS.contains(this.speciesId());
    }

    private static final java.util.Set<String> BIPEDS = java.util.Set.of("tyrannosaurus", "carnotaurus", "giganotosaurus",
            "velociraptor", "dakotaraptor", "gallimimus", "pachycephalosaurus", "therizinosaurus");

    /** The model's scale (MODEL_SCALE of the species class), for the live layer's feet. */
    public float livelyModelScale() {
        return 1.0F;
    }

    /** Client: the live motion layer, or null. */
    public LivelyMotion lively() {
        return this.lively;
    }

    @Override
    public void tick() {
        super.tick();
        this.tickParts();
        if (this.level().isClientSide() && this.livelyMotion()) {
            if (this.lively == null) {
                this.lively = new LivelyMotion();
            }
            this.lively.tick(this);
        }
        if (!this.level().isClientSide()) {
            if (!this.levels.isRolled()) {
                this.ensureLevels();
            }
            this.rideXpTick();
            if (this.isTame() && this.isAlive() && (this.tickCount + this.getId()) % TamedRegistry.REFRESH_TICKS == 0) {
                TamedRegistry.update(this);   // 1.7: where it is, for the owner's "My dinos" list
            }
            if (this.isAlpha() && !this.isTame() && this.isAlive() && (this.tickCount + this.getId()) % 100 == 0) {
                this.alphaTick();
            }
            if (this.tickCount % 5 == 0 && this.getControllingPassenger() instanceof Player) {
                int[] r = this.specialRecharge();
                this.entityData.set(DATA_SPECIAL, r == null ? 0
                        : Math.min(Math.max(0, r[0]), 0xFFFF) << 16 | Math.min(Math.max(1, r[1]), 0xFFFF));
            }
        }
        if (this.pendingNest && !this.level().isClientSide()) {
            this.pendingNest = false;
            this.layWildEgg(this.level());
        }
        if (this.isPerched()) {
            this.perchedTick((Player) this.getVehicle());
        }
        if (!this.level().isClientSide() && this.cargo != null && this.isChested() && this.isTame() && this.isAlive()
                && !this.isInSittingPose() && (this.tickCount + this.getId()) % 10 == 0) {
            this.collectCargo();
        }
        if (!this.level().isClientSide() && this.sated > 0) {
            this.sated--;
        }
        if (!this.level().isClientSide() && this.isAlive() && (this.torpor > 0.0F || this.isKnockedOut())) {
            this.torporTick();
        }
        if (!this.level().isClientSide() && this.entangledTicks > 0) {
            this.entangledTick();
        }
        if (!this.level().isClientSide() && this.getStuckDarts() > 0) {
            this.stuckDartTick();
        }
        if (!this.level().isClientSide() && this.isAlive()) {
            this.growthTick();
            this.hungerTick();
            if (this.isBaby() && (this.tickCount + this.getId()) % 20 == 0) {
                this.maturationTick();
            }
            if ((this.tickCount + this.getId()) % 200 == 0) {
                this.wildBreedingTick();
            }
            if (this.brooder() && this.tickCount % 160 == 0 && !this.isBaby() && (this.isInSittingPose() || this.isSleeping())
                    && this.level() instanceof ServerLevel server) {
                this.broodEggs(server);
            }
        }
    }

    // ------------------------------------------------------------------ hunger (docs/FOME_E_SONO.md)

    /** The Maturation speed rule (docs/REGRAS.md): babies grow 20 ticks of age per second; this adds or takes the rest. */
    private void maturationTick() {
        double speed = Rules.of(this.level()).get(Rule.MATURATION_SPEED);
        int extra = (int) Math.round(20.0D * (speed - 1.0D));
        if (extra != 0) {
            this.setAge(Math.min(0, this.getAge() + extra));
        }
    }

    private void hungerTick() {
        // the gauge empties with time (twice as fast for a growing baby), at the pace of the Food drain rule
        if (--this.hungerTimer <= 0) {
            int base = (int) Math.round((this.isBaby() ? this.hungerInterval() / 2 : this.hungerInterval())
                    * this.levels.multiplier(DinoLevels.Stat.FOOD));
            double drain = Rules.of(this.level()).get(Rule.FOOD_DRAIN);
            this.hungerTimer = drain <= 0.0D ? base : Math.max(1, (int) Math.round(base / drain));
            if (drain <= 0.0D) {
                // never hungry: the gauge stays where it is
                if (this.getHunger() < MAX_HUNGER) {
                    this.feed(1);
                }
            } else if (!this.isTame() && this.random.nextInt(4) == 0) {
                // a wild animal out of sight finds something to eat now and then, so the wild never starves offscreen
                this.feed(1);
            } else {
                this.setHunger(this.getHunger() - 1);
            }
        }
        // a chested animal helps itself to its own cargo when hungry
        if (this.isHungry() && this.cargo != null && this.hasCargo() && this.tickCount % 100 == 0) {
            for (int i = 0; i < this.cargo.getContainerSize(); i++) {
                ItemStack stack = this.cargo.getItem(i);
                if (!stack.isEmpty() && this.isFood(stack)) {
                    stack.shrink(1);
                    this.feed(25);
                    triggerAnim(ACTION_CONTROLLER, "eat");
                    this.playSound(ModSounds.SFX_EAT.get(), 1.0F, 1.0F);
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
        if (this.isTame() && this.getHunger() < 30 && this.tickCount % 200 == 0 && this.getOwner() instanceof Player owner) {
            boolean near = owner.distanceToSqr(this) < 64.0D;
            if (near) {
                triggerAnim(ACTION_CONTROLLER, "beg");
            }
            // the notice reaches the owner anywhere in the dimension: with twenty dinos you are not next to each one
            if (this.hungryMessageCooldown == 0) {
                this.hungryMessageCooldown = 2400;
                this.notice(owner, ModNetwork.NOTICE_RIFT,
                        Component.translatable(near ? "hud.terrassic.notice.hungry" : "hud.terrassic.notice.hungry_far"),
                        this.getDisplayName());
            }
        }
    }

    public BlockPos getMigrationTarget() {
        return this.migrationTarget;
    }

    public void setMigrationTarget(BlockPos target) {
        this.migrationTarget = target;
    }

    /**
     * A real mouthful (06/11/2026, the ecosystem): the plant within reach is eaten, so a herd that stays long in one
     * place crops it bare and has to move on (MigrateGoal's "scarce"). Short plants go first (grass, ferns); where
     * none are left, now and then the turf itself is cropped to dirt; vanilla grass spreads back over it in time.
     * Leaves and saplings are browsed without being destroyed. Only with the mobGriefing game rule.
     */
    public boolean grazeEat() {
        if (!(this.level() instanceof net.minecraft.server.level.ServerLevel level)) {
            return false;
        }
        boolean grief = level.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_MOBGRIEFING);
        BlockPos centre = this.blockPosition();
        int r = Math.max(1, Math.round(this.getBbWidth() * 0.6F));
        BlockPos turf = null;
        boolean browse = false;
        for (BlockPos pos : BlockPos.betweenClosed(centre.offset(-r, -1, -r), centre.offset(r, 2, r))) {
            BlockState state = level.getBlockState(pos);
            if (state.is(Blocks.GRASS) || state.is(Blocks.TALL_GRASS) || state.is(Blocks.FERN) || state.is(Blocks.LARGE_FERN)) {
                if (grief) {
                    level.destroyBlock(pos.immutable(), false, this);
                }
                return true;
            }
            if (state.is(Blocks.GRASS_BLOCK) && turf == null) {
                turf = pos.immutable();
            }
            if (state.is(BlockTags.LEAVES) || state.is(BlockTags.SAPLINGS) || state.is(Blocks.MOSS_BLOCK)) {
                browse = true;
            }
        }
        if (turf != null) {
            if (grief && this.random.nextInt(4) == 0) {
                level.levelEvent(2001, turf, Block.getId(level.getBlockState(turf)));
                level.setBlockAndUpdate(turf, Blocks.DIRT.defaultBlockState());
            }
            return true;
        }
        return browse;
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
            this.tellOwnerAboutPerch(owner);
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

    /** Extra seat height on top of {@link #getPassengersRidingOffset()} for a pose that raises the back (flight). */
    protected double seatLift() {
        return 0.0D;
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
                this.getY() + this.getPassengersRidingOffset() + this.seatLift() + passenger.getMyRidingOffset(),
                this.getZ() + Mth.cos(yaw) * forward);
    }

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        super.tickRidden(player, input);
        if (!this.isEntangled() && (player.zza != 0 || player.xxa != 0)) {
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
        if (this.isEntangled()) {
            // tied by a bola: no steps, no jump, ridden or not; it just stands (or drops) where it is
            input = Vec3.ZERO;
            this.riderJump = 0.0F;
        }
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
        if (this.walksOnGroundPaths() && this.isControlledByLocalInstance() && this.isInWater()) {
            // the legs paddle: a big one swims at a walk (a T. rex about 2 blocks a second) rather than drifting
            if (this.wadesDeep() && !this.onGround() && input.z > 0.0D) {
                float yaw = this.getYRot() * Mth.DEG_TO_RAD;
                double push = 0.075D * this.getAttributeValue(Attributes.MOVEMENT_SPEED);   // 0.018 for the T. rex
                this.setDeltaMovement(this.getDeltaMovement().add(-Mth.sin(yaw) * push, 0.0D, Mth.cos(yaw) * push));
            }
            // ridden, no FloatGoal keeps it up (goals do not run on the rider's side): it kicks up like the goal would,
            // instead of sinking slowly to the bottom with its rider (v0.11 test)
            if (this.isVehicle() && this.getFluidHeight(FluidTags.WATER) > this.getFluidJumpThreshold()) {
                this.setDeltaMovement(this.getDeltaMovement().add(0.0D, 0.04D, 0.0D));
            }
            // pushing against the bank: it climbs out. Afloat chest-deep, a big one's feet are deeper than the step it
            // can take, and vanilla's jump out of the water needs room it does not have (v0.11 test: none got out, not
            // even over 1-block steps)
            if (this.wadesDeep() && this.horizontalCollision && (input.z > 0.0D || !this.getNavigation().isDone())) {
                Vec3 v = this.getDeltaMovement();
                this.setDeltaMovement(v.x, Math.max(v.y, 0.2D), v.z);
            }
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
     * Wild breeding (docs/NINHOS.md), checked every ten seconds with a one in twelve chance (times the Wild nests
     * rule): a wild, grown, well fed (gauge 80+), awake, idle animal whose species has room nearby looks for a wild
     * mate of the other sex in the same state within 16 blocks, and both fall in love; the vanilla BreedGoal does the
     * rest.
     */
    private void wildBreedingTick() {
        if (this.isTransientRoamer() || this.isTame() || this.isBaby() || !this.wildNests() || !this.canFallInLove() || this.getAge() != 0
                || this.getHunger() < 80 || this.isSleeping() || this.getTarget() != null || this.isVehicle()
                || this.random.nextDouble() >= Rules.of(this.level()).get(Rule.NEST_FREQUENCY) / 12.0D
                || !(this.level() instanceof ServerLevel level)) {
            return;
        }
        if (level.getEntitiesOfClass(this.getClass(), this.getBoundingBox().inflate(32.0D), e -> !e.isTame()).size()
                >= this.wildPopulationCap()) {
            return;
        }
        DinosaurEntity mate = null;
        double best = Double.MAX_VALUE;
        for (DinosaurEntity other : level.getEntitiesOfClass(this.getClass(), this.getBoundingBox().inflate(16.0D),
                e -> e != this && !e.isTransientRoamer() && !e.isTame() && !e.isBaby() && e.isFemale() != this.isFemale() && e.canFallInLove()
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
        if (this.isTransientRoamer()) {
            return false;
        }
        Block egg = ModBlocks.eggFor(this.speciesId());
        if (egg == null) {
            return false;
        }
        BlockPos pos = findEggSpot(level, groundUnder(level, this));
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
                level.playSound(null, mother.blockPosition(), ModSounds.SFX_EGG_LAY.get(), SoundSource.BLOCKS, 0.7F, 0.9F);
            }
            this.setHunger(this.getHunger() - 15);
            if (partner instanceof DinosaurEntity other) {
                other.setHunger(other.getHunger() - 15);
            }
        } else {
            BlockPos pos = findEggSpot(level, groundUnder(level, mother));
            if (pos != null) {
                level.setBlock(pos, egg.defaultBlockState(), Block.UPDATE_ALL);
                level.playSound(null, pos, ModSounds.SFX_EGG_LAY.get(), SoundSource.BLOCKS, 0.7F, 0.9F);
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
        // the wait before mating again follows the Mating interval rule
        int wait = (int) Math.round(6000 * Rules.of(level).get(Rule.MATING_INTERVAL));
        this.setAge(wait);
        partner.setAge(wait);
        this.resetLove();
        partner.resetLove();
        level.broadcastEntityEvent(this, (byte) 18);
        if (level.getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT)) {
            int xp = (int) Math.round((this.getRandom().nextInt(7) + 1) * Rules.of(level).get(Rule.XP_MULTIPLIER));
            if (xp > 0) {
                level.addFreshEntity(new ExperienceOrb(level, this.getX(), this.getY(), this.getZ(), xp));
            }
        }
    }

    /** Where a mother lays: her own block on the ground, or the ground under her when she mates on the wing or swimming
     *  (1.9: a Quetzalcoatlus pair mating in the air looked for a nest spot one block round the flying mother, found
     *  none and dropped the egg as an item from the sky). */
    private static BlockPos groundUnder(LevelAccessor level, DinosaurEntity mother) {
        BlockPos at = mother.blockPosition();
        if (mother.onGround()) {
            return at;
        }
        for (int down = 0; down < 48 && at.getY() > level.getMinBuildHeight(); down++) {
            BlockPos below = at.below();
            if (!level.isEmptyBlock(below) || !level.getFluidState(below).isEmpty()) {
                return at;
            }
            at = below;
        }
        return mother.blockPosition();
    }

    private static BlockPos findEggSpot(LevelAccessor level, BlockPos center) {
        // While a chunk is generating (mobs spawned with it), the level is a WorldGenRegion: reading or writing outside
        // that chunk crashes the game ("asking a region for a chunk out of bound"), so the egg stays in it.
        // Otherwise only chunks that are loaded are looked at.
        boolean worldgen = level instanceof WorldGenRegion;
        int cx = center.getX() >> 4;
        int cz = center.getZ() >> 4;
        // 1.8: out to 8 blocks (was 3): a pair mating in a river lays on the bank instead of dropping the egg in the water
        for (int r = 1; r <= 8; r++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != r) {
                        continue;   // the ring at this distance only: the inner ones were looked at already
                    }
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
        return ground && level.getRawBrightness(pos, 0) > 8 && VanillaShare.allows(type, level, reason, pos)
                && !((reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) && Rules.inSafeZone(level, pos));
    }

    // ---- passos e asas sem "spam" (2026-11) ------------------------------------------------------------
    private static final java.util.Map<net.minecraft.world.level.Level, java.util.Map<Long, long[]>> BODY_SOUND_BUDGET =
            new java.util.WeakHashMap<>();
    private long lastBodySoundTick = -100L;

    /**
     * Passo ou batida de asa. Respeita a passada (quanto mais largo o bicho, menos vezes pisa) e um limite por
     * região: no máximo 2 desses sons a cada 4 ticks num quadrado de 16x16 blocos, para um bando andando junto
     * não virar uma metralhadora de passos. O tom varia um pouco a cada passo.
     */
    protected void playBodySound(SoundEvent sound, float volume, float pitch) {
        if (sound == null || this.isSilent()) {
            return;
        }
        long now = this.level().getGameTime();
        int stride = Math.max(5, Math.round(this.getBbWidth() * 4.0F));
        if (now - this.lastBodySoundTick < stride) {
            return;
        }
        if (!this.level().isClientSide()) {
            java.util.Map<Long, long[]> budget = BODY_SOUND_BUDGET.computeIfAbsent(this.level(), l -> new java.util.HashMap<>());
            long region = (((long) (this.getBlockX() >> 4)) << 32) ^ ((this.getBlockZ() >> 4) & 0xffffffffL);
            long window = now >> 2;
            long[] slot = budget.get(region);
            if (slot == null || slot[0] != window) {
                if (budget.size() > 512) {
                    budget.clear();
                }
                slot = new long[] {window, 0L};
                budget.put(region, slot);
            }
            if (slot[1] >= 2) {
                return;
            }
            slot[1]++;
        }
        this.lastBodySoundTick = now;
        this.playSound(sound, volume, pitch * (0.92F + this.random.nextFloat() * 0.16F));
    }
}
