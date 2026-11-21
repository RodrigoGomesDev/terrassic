package com.terrassic.entity;

import com.terrassic.block.DinoEggBlock;
import com.terrassic.config.Eras;
import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import com.terrassic.entity.ai.NestRaidGoal;
import com.terrassic.registry.ModBlocks;
import com.terrassic.registry.ModEntities;
import com.terrassic.world.RegionPopulation;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.List;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Maiasaura rig (tools/modelgen/handmade/maiasaura, its own study: docs/estudos/15_HERBIVOROS_1_11.md,
 * approved by Rodrigo on 10/11/2026). Its touch is the NESTING COLONY of the Two Medicine ("Egg Mountain", Horner &
 * Makela 1979) and the young that walk on two legs. What it adds over a plain grazer:
 * <ul>
 *   <li><b>the colony</b> (world structure Colônia de Ninhos): a wild female near a wild clutch takes the nest as her
 *       HOME, grazes within 12 blocks of it and sleeps beside it; the other grown ones of the colony stay round it as a
 *       herd. Docile out of a colony, defensive in it;</li>
 *   <li><b>the covered nest</b>: now and then the mother pulls leaves with the bill and drops them on the eggs
 *       ("cover_nest"); a covered clutch hatches faster, an open one slower (DinoEggBlock.COVERED; a player can cover it
 *       with leaves or a fern). HYPOTHESIS: the eggs warmed by rotting plants;</li>
 *   <li><b>the calf in the nest</b>: a calf hatched in the colony stays in the nest ({@link #nestTicks}, two game days,
 *       the short version of the 40 to 75 days of Bert et al. 2025), begs ("nest_beg") and grows ONLY when fed: the mother
 *       brings up chewed leaves ("feed_young"; HYPOTHESIS, the worn teeth of the nestlings), and a player who feeds it
 *       starts taming it. A fed calf near a grown one grows twice as fast (the "good mother", only for its own kind now);
 *       a grown female adopts an orphan calf of its kind within 16 blocks ("adopt");</li>
 *   <li><b>the whole colony defends</b>: taking an egg or hurting a calf turns every grown one of the colony on the
 *       culprit (40 blocks, not the 24 of the egg rage); the mother of the nest stands over it ("nest_guard");</li>
 *   <li><b>night visitors</b>: once a night the colony may draw an egg thief (a Velociraptor, a Dakotaraptor now and then)
 *       that slinks in for an egg ({@link NestRaidGoal}); the colony wakes and drives it off;</li>
 *   <li><b>the cycle</b>: when the nest is empty (hatched, eaten or taken), the mother lays again in it some days later,
 *       if the region has room (world/RegionPopulation);</li>
 *   <li><b>on two legs when young</b> (Cubo et al. 2015): under half the grown size it walks and runs on its hind legs
 *       ("biped_walk", "biped_run"); grown, it walks on four and rears only to browse high ("rear_browse");</li>
 *   <li><b>out of a colony</b>: a big herd of the open plain (6 to 12) with the leader of the 1.10; no sentinel (the
 *       Edmontosaurus'): whoever sees a hunting predator gives the short bellow ("alarm") and they run in a block.</li>
 * </ul>
 * One log line per behaviour, "[maia] ..." (logger "terrassic"), for the playtests (BehaviorTest phase "maia").
 */
public abstract class Maiasaurine extends HerbivoreDinosaur {
    /** The cycles (maiaanims.py WALK, RUNP, BWALK, BRUN): pixels of ground each covers at 16.94 px/m and its length in ticks. */
    private static final double WALK_PX = 31.0D;
    private static final double WALK_TICKS = 32.0D;
    private static final double RUN_PX = 76.0D;
    private static final double RUN_TICKS = 12.4D;
    private static final double BWALK_PX = 30.0D;
    private static final double BWALK_TICKS = 18.0D;
    private static final double BRUN_PX = 58.0D;
    private static final double BRUN_TICKS = 10.0D;
    /** The colony's reach: whoever has a home within this of a nest belongs to it, and defends it. */
    public static final double COLONY_RANGE = 40.0D;
    /** How far a mother grazes from her nest. */
    private static final double HOME_RANGE = 12.0D;
    private static final double PREDATOR = 20.0D;

    // the timings of the nest; the behaviour test shortens them (TERRASSIC_MAIA_FAST=1)
    private static final boolean FAST = "1".equals(System.getenv("TERRASSIC_MAIA_FAST"));
    /** Ticks a calf stays in the nest (two game days). */
    public static int nestTicks = FAST ? 2400 : 48000;
    /** Ticks after the nest empties before the mother lays again (three game days). */
    public static int relayTicks = FAST ? 1200 : 72000;
    /** Ticks between two coverings of the nest by the mother. */
    public static int coverEvery = FAST ? 300 : 2400;
    /** Ticks of growth one feeding gives a calf in the nest. */
    public static int feedGrowth = 2400;
    /** Chance a colony draws an egg thief on a given night. */
    public static float raidChance = FAST ? 1.0F : 0.5F;

    private static final RawAnimation BIPED_WALK = RawAnimation.begin().thenLoop("animation.maiasaura.biped_walk");
    private static final RawAnimation BIPED_RUN = RawAnimation.begin().thenLoop("animation.maiasaura.biped_run");
    private static final RawAnimation NEST_SLEEP = RawAnimation.begin().thenLoop("animation.maiasaura.nest_sleep");
    /** v4: at rest it stands half-reared on the tripod; with a rider it stands level on all four (the saddle flat). */
    private static final RawAnimation RIDDEN_IDLE = RawAnimation.begin().thenLoop("animation.maiasaura.ridden_idle");

    /** A mother's nest. */
    private BlockPos home;
    /** A calf's nest, the ticks it still stays in it and the ticks of growth its last feeding gave. */
    private BlockPos nest;
    private int nestLeft;
    private int fedLeft;
    private UUID mother;
    private long relayAt;
    private long lastRaidDay = -1L;
    private boolean colonist;
    private int still;
    private int callCooldown;
    private int alarmCooldown;
    private int coverCooldown = 200;
    private int feedCooldown = 100;
    private int coverIn = -1;
    private int feedIn = -1;
    private Maiasaurine feedTarget;
    private int answerIn = -1;
    private LivingEntity answerTo;
    private LivingEntity fleeing;
    private int fleeTicks;
    private int begCooldown;

    protected Maiasaurine(EntityType<? extends Maiasaurine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    public static void logLine(String line) {
        Behaviour.LOG.info("[maia] " + line);
    }

    private void log(String what) {
        logLine(what + " (#" + this.getId() + " " + this.getBlockX() + " " + this.getBlockY() + " " + this.getBlockZ() + ")");
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "call", "colony_call", "answer", "alarm", "cover_nest", "feed_young", "nest_guard",
                "nest_dig", "nuzzle", "adopt", "rear_browse", "drink", "nest_beg", "hatch"};
    }

    @Override
    protected void addExtraGoals() {
        this.goalSelector.addGoal(1, new NestlingGoal(this));
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
        return 60;
    }

    @Override
    public float babyHeadScale() {
        return 1.3F;
    }

    /** Under half its grown size it goes on two legs (Cubo et al. 2015). */
    public boolean onTwoLegs() {
        return this.isBaby() && this.getScale() < 0.5F * this.getAdultSize();
    }

    @Override
    protected double walkCycleSpeed() {
        return this.onTwoLegs() ? BWALK_PX / 16.0D / BWALK_TICKS * this.modelScale() : WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return this.onTwoLegs() ? BRUN_PX / 16.0D / BRUN_TICKS * this.modelScale() : RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** The young: on two legs, and the calf asleep in the nest curled tight. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.isBaby() && this.isSleeping() && !this.isSwimmingDeep()) {
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(NEST_SLEEP);
        }
        if (this.isVehicle() && !state.isMoving() && !this.isSwimmingDeep() && !this.isBaby() && !this.isKnockedOut()) {
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(RIDDEN_IDLE);
        }
        if (this.onTwoLegs() && state.isMoving() && !this.isSwimmingDeep() && !this.isInSittingPose()) {
            double pace = this.walkCycleSpeed() * this.getScale();
            double moved = Math.sqrt((this.getX() - this.xo) * (this.getX() - this.xo) + (this.getZ() - this.zo) * (this.getZ() - this.zo));
            boolean running = this.getDeltaMovement().horizontalDistanceSqr() > this.runThresholdSqr() || (pace > 0.0D && moved > pace * 1.3D);
            this.cycleSpeed = this.gaitSpeed(running ? this.runCycleSpeed() : this.walkCycleSpeed());
            return state.setAndContinue(running ? BIPED_RUN : BIPED_WALK);
        }
        return super.movementAnimation(state);
    }

    // ------------------------------------------------------------------ temperament
    /** Defensive in a colony (and tame); docile out of it: the herd runs. */
    @Override
    protected boolean fightsBack() {
        return this.isTame() || (this.colonist && !this.isBaby());
    }

    @Override
    protected boolean fleesFrom(Player player) {
        return this.getLastHurtByMob() == player;
    }

    public BlockPos home() {
        return this.home;
    }

    public boolean isNestling() {
        return this.isBaby() && this.nest != null && this.nestLeft > 0;
    }

    public boolean isColonist() {
        return this.colonist;
    }

    private boolean busy() {
        return this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut();
    }

    private static List<Maiasaurine> around(Level level, AABB box) {
        return level.getEntitiesOfClass(Maiasaurine.class, box, e -> e.isAlive() && !e.isTame());
    }

    private List<Maiasaurine> herd(double r) {
        return around(this.level(), this.getBoundingBox().inflate(r)).stream().filter(e -> e != this).toList();
    }

    // ------------------------------------------------------------------ the colony defends
    /**
     * Something took an egg of the colony at {@code pos} or hurt a calf: every grown wild one of the colony within
     * {@link #COLONY_RANGE} goes for the culprit, and the mother of that nest stands over it. Returns false (and the
     * ordinary egg rage happens) when there is no colony there.
     */
    public static boolean colonyDefends(Level level, BlockPos pos, LivingEntity culprit) {
        if (level.isClientSide() || culprit == null || (culprit instanceof Player p && (p.isCreative() || p.isSpectator()))) {
            return false;
        }
        List<Maiasaurine> colony = around(level, new AABB(pos).inflate(COLONY_RANGE, 16.0D, COLONY_RANGE));
        boolean any = colony.stream().anyMatch(e -> e.home != null && e.home.closerThan(pos, COLONY_RANGE));
        if (!any) {
            return false;
        }
        int n = 0;
        for (Maiasaurine m : colony) {
            if (m.isBaby() || m.isKnockedOut() || m == culprit) {
                continue;
            }
            m.colonist = true;
            m.setSleeping(false);
            m.fleeTicks = 0;
            if (culprit instanceof Player thief) {
                m.enrage(thief, 1200);
            } else if (m.canAttack(culprit)) {
                m.setTarget(culprit);
            }
            if (m.home != null && m.home.closerThan(pos, 5.0D)) {
                m.triggerAnim(ACTION_CONTROLLER, "nest_guard");
            }
            n++;
        }
        logLine("colony defends: " + n + " adults go for " + culprit.getName().getString() + " at " + pos.toShortString());
        return true;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && !this.isTame() && source.getEntity() instanceof LivingEntity attacker) {
            if (this.isBaby()) {
                colonyDefends(this.level(), this.blockPosition(), attacker);
            } else if (!this.colonist) {
                this.alarm(attacker);
            }
        }
        return hurt;
    }

    // ------------------------------------------------------------------ out of a colony: the alarm and the block
    private void fleeFrom(LivingEntity threat) {
        Vec3 away = net.minecraft.world.entity.ai.util.DefaultRandomPos.getPosAway(this, 16, 7, threat.position());
        if (away == null) {
            Vec3 d = this.position().subtract(threat.position());
            away = this.position().add(new Vec3(d.x, 0.0D, d.z).normalize().scale(16.0D));
        }
        this.getNavigation().moveTo(away.x, away.y, away.z, 1.6D);
    }

    private void alarm(LivingEntity threat) {
        if (this.alarmCooldown > 0 || this.isTame()) {
            return;
        }
        this.alarmCooldown = 200;
        if (!this.isBaby() && !this.isSleeping()) {
            this.getLookControl().setLookAt(threat, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "alarm");
        }
        this.setSleeping(false);
        this.fleeing = threat;
        this.fleeTicks = 100;
        this.fleeFrom(threat);
        int n = 0;
        for (Maiasaurine other : this.herd(40.0D)) {
            if (other.colonist) {
                continue;
            }
            other.alarmCooldown = Math.max(other.alarmCooldown, 120);
            other.still = 0;
            other.setSleeping(false);
            other.fleeing = threat;
            other.fleeTicks = 100;
            other.fleeFrom(threat);
            n++;
        }
        this.log("alarm: the herd (" + (n + 1) + ") runs from " + threat.getName().getString());
    }

    // ------------------------------------------------------------------ the voice
    private void colonyCall() {
        triggerAnim(ACTION_CONTROLLER, "colony_call");
        this.still = Math.max(this.still, 52);
        this.callCooldown = 400;
        int answers = 0;
        for (Maiasaurine other : this.herd(32.0D)) {
            if (answers >= 3 || other.isBaby() || other.busy() || other.answerIn >= 0) {
                continue;
            }
            other.answerTo = this;
            other.answerIn = 20 + this.random.nextInt(30) + answers * 15;
            other.callCooldown = Math.max(other.callCooldown, 200);
            answers++;
        }
        if (answers > 0 && this.colonist) {
            this.log("colony call, " + answers + " answer");
        }
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!this.level().isClientSide() && !this.isTame() && !this.isBaby() && !this.busy() && this.callCooldown == 0
                && this.random.nextInt(3) == 0) {
            this.colonyCall();
        }
    }

    // ------------------------------------------------------------------ the calf
    @Override
    public void hatchedFrom(BlockPos pos, boolean wild) {
        triggerAnim(ACTION_CONTROLLER, "hatch");
        if (!wild) {
            return;
        }
        Maiasaurine mum = around(this.level(), new AABB(pos).inflate(8.0D, 4.0D, 8.0D)).stream()
                .filter(e -> !e.isBaby() && e.home != null && e.home.closerThan(pos, 6.0D))
                .min(Comparator.comparingDouble(e -> e.home.distSqr(pos))).orElse(null);
        if (mum == null) {
            return;
        }
        this.nest = mum.home;
        this.nestLeft = nestTicks;
        this.mother = mum.getUUID();
        this.log("calf hatched in the nest at " + this.nest.toShortString() + ", stays " + nestTicks + " ticks");
    }

    /** Fed in the nest: {@code ticks} of growth. */
    public void feedNest(int ticks, String by) {
        this.fedLeft = Math.min(this.fedLeft + ticks, 3 * feedGrowth);
        this.feed(20);
        this.log("calf fed by " + by + ", growth " + this.fedLeft + " ticks, age " + this.getAge());
    }

    @Override
    protected void tameBite(Player player, ItemStack food) {
        if (this.isNestling()) {
            this.feedNest(feedGrowth, "player " + player.getName().getString());
            this.log("calf taming by " + player.getName().getString() + " begins");
        }
        super.tameBite(player, food);
    }

    private Maiasaurine motherEntity() {
        if (this.mother == null || !(this.level() instanceof ServerLevel server)) {
            return null;
        }
        return server.getEntity(this.mother) instanceof Maiasaurine m && m.isAlive() ? m : null;
    }

    /** The calf: in the nest it grows only when fed; fed near a grown one it grows twice as fast; it begs. */
    private void calfStep() {
        if (this.nestLeft > 0) {
            if (--this.nestLeft == 0) {
                this.log("calf leaves the nest, age " + this.getAge());
                this.nest = null;
            }
        }
        boolean nestling = this.isNestling();
        if (this.fedLeft > 0) {
            this.fedLeft--;
            boolean grownNear = !this.herd(10.0D).stream().filter(e -> !e.isBaby()).toList().isEmpty();
            if (grownNear && this.getAge() < -1) {
                this.setAge(this.getAge() + 1);      // the good mother: twice as fast
            }
        } else if (nestling && this.getAge() < -1) {
            this.setAge(this.getAge() - 1);          // hungry in the nest: no growth (the ageing tick adds it back)
        }
        if (nestling && this.fedLeft < 200 && --this.begCooldown <= 0) {
            this.begCooldown = 140 + this.random.nextInt(80);
            boolean someone = !this.herd(8.0D).stream().filter(e -> !e.isBaby()).toList().isEmpty()
                    || this.level().getNearestPlayer(this, 8.0D) != null;
            if (someone && !this.isSleeping()) {
                triggerAnim(ACTION_CONTROLLER, "nest_beg");
            }
        }
        if (!nestling && this.tickCount % 200 == 0 && this.motherEntity() == null) {
            this.mother = null;                      // an orphan: a grown female may adopt it
        }
    }

    // ------------------------------------------------------------------ the mother
    private List<BlockPos> eggsAt(BlockPos centre, int r) {
        List<BlockPos> out = new ArrayList<>();
        for (BlockPos p : BlockPos.betweenClosed(centre.offset(-r, -1, -r), centre.offset(r, 1, r))) {
            if (this.level().getBlockState(p).getBlock() instanceof DinoEggBlock egg && egg.nestCare()) {
                out.add(p.immutable());
            }
        }
        return out;
    }

    private List<Maiasaurine> nestlingsOf(BlockPos h) {
        return around(this.level(), new AABB(h).inflate(5.0D, 3.0D, 5.0D)).stream()
                .filter(e -> e.isNestling() && e.nest != null && e.nest.closerThan(h, 4.0D)).toList();
    }

    /** A wild female near a wild clutch no other mother holds takes it as her home. */
    private void claimHome() {
        if (this.home != null || !this.isFemale() || this.isBaby() || this.isTame() || this.tickCount % 20 != this.getId() % 20) {
            return;
        }
        for (BlockPos egg : this.eggsAt(this.blockPosition(), 6)) {
            if (!this.level().getBlockState(egg).getValue(DinoEggBlock.WILD)) {
                continue;
            }
            boolean held = !around(this.level(), new AABB(egg).inflate(8.0D)).stream()
                    .filter(e -> e != this && e.home != null && e.home.closerThan(egg, 3.5D)).toList().isEmpty();
            if (!held) {
                this.home = egg;
                this.colonist = true;
                this.log("takes the nest at " + egg.toShortString() + " as her home");
                return;
            }
        }
    }

    private boolean goHome(double within) {
        double d = Math.sqrt(this.home.distToCenterSqr(this.position()));
        if (d <= within) {
            return true;
        }
        if (this.getNavigation().isDone()) {
            this.getNavigation().moveTo(this.home.getX() + 0.5D, this.home.getY(), this.home.getZ() + 0.5D, 1.0D);
        }
        return false;
    }

    private void homeStep() {
        if (this.coverIn >= 0 && --this.coverIn < 0) {
            int n = 0;
            for (BlockPos egg : this.eggsAt(this.home, 3)) {
                if (DinoEggBlock.cover(this.level(), egg)) {
                    n++;
                }
            }
            if (n > 0) {
                this.log("covers " + n + " eggs with leaves");
            }
        }
        if (this.feedIn >= 0 && --this.feedIn < 0 && this.feedTarget != null && this.feedTarget.isAlive()) {
            this.feedTarget.feedNest(feedGrowth, "its mother");
            this.feedTarget = null;
        }
        if (this.busy() || this.fleeTicks > 0) {
            return;
        }
        if (this.isSleepTime()) {
            this.goHome(4.0D);
            return;
        }
        if (this.still > 0) {
            return;
        }
        if (this.coverCooldown > 0) {
            this.coverCooldown--;
        }
        if (this.feedCooldown > 0) {
            this.feedCooldown--;
        }
        List<BlockPos> eggs = this.eggsAt(this.home, 3);
        List<Maiasaurine> calves = this.nestlingsOf(this.home);
        // the hungry calf first
        Maiasaurine hungry = calves.stream().filter(c -> c.fedLeft < 600).findFirst().orElse(null);
        if (hungry != null && this.feedCooldown == 0) {
            if (this.goHome(4.0D)) {
                this.getNavigation().stop();
                this.getLookControl().setLookAt(hungry, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "feed_young");
                this.still = 68;
                this.feedIn = 40;
                this.feedTarget = hungry;
                this.feedCooldown = 600;
            }
            return;
        }
        boolean open = eggs.stream().anyMatch(p -> !this.level().getBlockState(p).getValue(DinoEggBlock.COVERED));
        if (open && this.coverCooldown == 0) {
            if (this.goHome(4.0D)) {
                this.getNavigation().stop();
                this.getLookControl().setLookAt(this.home.getX() + 0.5D, this.home.getY(), this.home.getZ() + 0.5D);
                triggerAnim(ACTION_CONTROLLER, "cover_nest");
                this.still = 88;
                this.coverIn = 70;
                this.coverCooldown = coverEvery + this.random.nextInt(Math.max(1, coverEvery));
            }
            return;
        }
        // the cycle: the nest empty, she lays again in it some days later if the region has room
        if (eggs.isEmpty() && calves.isEmpty() && this.isFemale()) {
            long now = this.level().getGameTime();
            if (this.relayAt == 0L) {
                this.relayAt = now + relayTicks;
                this.log("nest empty, lays again in " + relayTicks + " ticks");
            } else if (now >= this.relayAt && this.goHome(3.0D)) {
                this.relayAt = 0L;
                this.layAgain();
            }
        } else {
            this.relayAt = 0L;
        }
        if (!this.goHome(HOME_RANGE)) {
            return;
        }
        if (this.getNavigation().isDone() && this.random.nextInt(1200) == 0) {
            Maiasaurine calf = calves.isEmpty() ? null : calves.get(0);
            if (calf != null) {
                this.getLookControl().setLookAt(calf, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "nuzzle");
                this.still = 48;
            } else if (Math.sqrt(this.home.distToCenterSqr(this.position())) < 4.0D) {
                triggerAnim(ACTION_CONTROLLER, "nest_dig");
                this.still = 60;
            }
        }
    }

    private void layAgain() {
        if (!(this.level() instanceof ServerLevel server)) {
            return;
        }
        int room = RegionPopulation.of(server).room(server, this.home, 15);
        if (room <= 0) {
            this.log("does not lay again: the region is full");
            return;
        }
        Block egg = ModBlocks.eggFor(this.speciesId());
        if (egg == null) {
            return;
        }
        int want = Math.min(room, 3 + this.random.nextInt(2));
        int laid = 0;
        for (BlockPos p : BlockPos.betweenClosed(this.home.offset(-1, -1, -1), this.home.offset(1, 1, 1))) {
            if (laid >= want) {
                break;
            }
            BlockState below = server.getBlockState(p.below());
            if (server.isEmptyBlock(p) && below.isFaceSturdy(server, p.below(), net.minecraft.core.Direction.UP)) {
                server.setBlock(p, egg.defaultBlockState().setValue(DinoEggBlock.WILD, true), Block.UPDATE_ALL);
                laid++;
            }
        }
        this.log("lays again: " + laid + " eggs in the nest at " + this.home.toShortString());
    }

    /** A grown female adopts an orphan calf of its kind within 16 blocks. */
    private void adoptStep() {
        if (!this.isFemale() || this.isBaby() || this.tickCount % 200 != this.getId() % 200) {
            return;
        }
        for (Maiasaurine calf : this.herd(16.0D)) {
            if (calf.isBaby() && calf.mother == null && !calf.isNestling()) {
                calf.mother = this.getUUID();
                this.getLookControl().setLookAt(calf, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "adopt");
                this.still = 60;
                this.log("adopts an orphan calf #" + calf.getId());
                return;
            }
        }
    }

    /** The colony keeper (the mother with the lowest id) may draw an egg thief once a night. */
    private void nightRaid() {
        if (!(this.level() instanceof ServerLevel server) || this.home == null) {
            return;
        }
        long time = server.getDayTime() % 24000L;
        long day = server.getDayTime() / 24000L;
        if (time < 13500L || time > 22000L || day == this.lastRaidDay) {
            return;
        }
        boolean keeper = around(server, this.getBoundingBox().inflate(COLONY_RANGE)).stream()
                .noneMatch(e -> e.home != null && e.getId() < this.getId());
        this.lastRaidDay = day;
        if (!keeper || this.random.nextFloat() >= raidChance) {
            return;
        }
        boolean dakota = this.random.nextInt(3) == 0 && Eras.active("dakotaraptor");
        String sp = dakota ? "dakotaraptor" : "velociraptor";
        if (!Eras.active(sp) || Rules.of(server).get(Rule.PREDATOR_SPAWNS) <= 0.0D
                || RegionPopulation.of(server).room(server, this.home, 15) <= 0) {
            return;
        }
        List<BlockPos> eggs = this.eggsAt(this.home, 3);
        if (eggs.isEmpty()) {
            for (Maiasaurine m : around(server, this.getBoundingBox().inflate(COLONY_RANGE))) {
                if (m.home != null) {
                    eggs = this.eggsAt(m.home, 3);
                    if (!eggs.isEmpty()) {
                        break;
                    }
                }
            }
        }
        if (eggs.isEmpty()) {
            return;
        }
        BlockPos target = eggs.get(this.random.nextInt(eggs.size()));
        double a = this.random.nextDouble() * Math.PI * 2.0D;
        BlockPos at = server.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                BlockPos.containing(target.getX() + Math.cos(a) * 28.0D, target.getY(), target.getZ() + Math.sin(a) * 28.0D));
        DinosaurEntity raider = (dakota ? ModEntities.DAKOTARAPTOR.get() : ModEntities.VELOCIRAPTOR.get()).create(server);
        if (raider == null) {
            return;
        }
        raider.moveTo(at.getX() + 0.5D, at.getY(), at.getZ() + 0.5D, this.random.nextFloat() * 360.0F, 0.0F);
        raider.finalizeSpawn(server, server.getCurrentDifficultyAt(at), MobSpawnType.EVENT, null);
        if (raider.isBaby()) {
            raider.setAge(0);
        }
        raider.setRoamer(true);
        server.addFreshEntity(raider);
        // above the sleep (a diurnal raptor sent at night would lie down at once) and the strolls
        raider.goals().addGoal(0, new NestRaidGoal(raider, target));
        logLine("night raid: " + sp + " #" + raider.getId() + " comes for the egg at " + target.toShortString());
    }

    /** A colonist wakes to a predator in the colony and goes for it; the mother stands over her nest. */
    private boolean guardStep() {
        if (this.tickCount % 10 != 0 || this.isTame()) {
            return false;
        }
        BlockPos centre = this.home != null ? this.home : this.blockPosition();
        List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, new AABB(centre).inflate(14.0D, 6.0D, 14.0D),
                p -> p.isAlive() && !p.isTame() && !p.isBaby() && p.getBbWidth() < this.getBbWidth() * 1.4F);
        if (near.isEmpty()) {
            return false;
        }
        PredatorDinosaur p = near.get(0);
        if (this.getTarget() == null && this.canAttack(p)) {
            boolean woke = this.isSleeping();
            this.setSleeping(false);
            this.setTarget(p);
            if (this.home != null) {
                triggerAnim(ACTION_CONTROLLER, "nest_guard");
            }
            this.log((woke ? "wakes and " : "") + "drives off " + p.speciesId() + " #" + p.getId() + " from the colony");
        }
        return true;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.callCooldown > 0) {
            this.callCooldown--;
        }
        if (this.alarmCooldown > 0) {
            this.alarmCooldown--;
        }
        if (this.answerIn >= 0 && --this.answerIn < 0) {
            LivingEntity caller = this.answerTo;
            this.answerTo = null;
            if (caller != null && caller.isAlive() && !this.busy()) {
                this.getLookControl().setLookAt(caller, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "answer");
                this.still = Math.max(this.still, 40);
            }
        }
        if (this.isBaby()) {
            this.calfStep();
            return;
        }
        if (this.isTame()) {
            if (!this.busy() && this.getNavigation().isDone() && this.random.nextInt(900) == 0) {
                this.idleAct();
            }
            return;
        }
        this.claimHome();
        if (this.home != null && this.tickCount % 40 == 0 && this.eggsAt(this.home, 3).isEmpty() && this.nestlingsOf(this.home).isEmpty()
                && !this.isFemale()) {
            this.home = null;
        }
        if (this.tickCount % 40 == this.getId() % 40) {
            this.colonist = this.home != null || this.herd(COLONY_RANGE).stream().anyMatch(e -> e.home != null);
        }
        if (this.colonist) {
            this.nightRaid();
            if (this.guardStep()) {
                return;
            }
        }
        this.adoptStep();
        if (this.fleeTicks > 0) {
            this.fleeTicks--;
            this.still = 0;
            if (this.fleeing != null && this.fleeing.isAlive() && this.getNavigation().isDone()
                    && this.distanceToSqr(this.fleeing) < 24.0D * 24.0D) {
                this.fleeFrom(this.fleeing);
            }
            return;
        }
        if (this.home != null) {
            this.homeStep();
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.busy()) {
            return;
        }
        if (!this.colonist && this.tickCount % 10 == 0 && this.alarmCooldown == 0) {
            List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(PREDATOR),
                    p -> p.isAlive() && !p.isTame() && !p.isBaby() && this.hasLineOfSight(p)
                            && (p.canHunt() || p.getTarget() != null || p.distanceToSqr(this) < 12.0D * 12.0D));
            if (!near.isEmpty()) {
                this.alarm(near.get(0));
                return;
            }
        }
        if (this.getNavigation().isDone() && this.random.nextInt(600) == 0) {
            this.idleAct();
        }
    }

    private void idleAct() {
        if (this.isInWater() || this.waterInFront()) {
            triggerAnim(ACTION_CONTROLLER, "drink");
            this.still = 70;
            return;
        }
        if (this.leavesHigh()) {
            triggerAnim(ACTION_CONTROLLER, "rear_browse");
            this.still = 84;
            this.feed(6);
        }
    }

    private boolean waterInFront() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        BlockPos p = BlockPos.containing(this.getX() + look.x * 2.0D * this.getScale(), this.getY() - 0.5D, this.getZ() + look.z * 2.0D * this.getScale());
        return this.level().getFluidState(p).is(FluidTags.WATER) || this.level().getFluidState(p.above()).is(FluidTags.WATER);
    }

    private boolean leavesHigh() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        for (int up = 3; up <= 5; up++) {
            BlockPos p = BlockPos.containing(this.getX() + look.x * 2.5D, this.getY() + up * this.getScale(), this.getZ() + look.z * 2.5D);
            if (this.level().getBlockState(p).is(BlockTags.LEAVES)) {
                return true;
            }
        }
        return false;
    }

    // ------------------------------------------------------------------ saving
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (this.home != null) {
            tag.put("MaiaHome", NbtUtils.writeBlockPos(this.home));
        }
        if (this.nest != null) {
            tag.put("MaiaNest", NbtUtils.writeBlockPos(this.nest));
            tag.putInt("MaiaNestLeft", this.nestLeft);
        }
        tag.putInt("MaiaFed", this.fedLeft);
        if (this.mother != null) {
            tag.putUUID("MaiaMother", this.mother);
        }
        tag.putLong("MaiaRelay", this.relayAt);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.home = NbtUtils.readBlockPos(tag, "MaiaHome").orElse(null);
        this.nest = NbtUtils.readBlockPos(tag, "MaiaNest").orElse(null);
        this.nestLeft = tag.getInt("MaiaNestLeft");
        this.fedLeft = tag.getInt("MaiaFed");
        this.mother = tag.hasUUID("MaiaMother") ? tag.getUUID("MaiaMother") : null;
        this.relayAt = tag.getLong("MaiaRelay");
        this.colonist = this.home != null;
    }

    /** Test only (BehaviorTest "maia"): the calf's nest and ticks of growth, a mother's home. */
    public void testNest(BlockPos nestPos, UUID mum) {
        this.nest = nestPos;
        this.nestLeft = nestTicks;
        this.mother = mum;
    }

    public void testHome(BlockPos h) {
        this.home = h;
        this.colonist = true;
    }

    public int fedLeft() {
        return this.fedLeft;
    }

    public int nestLeft() {
        return this.nestLeft;
    }

    /** The calf in the nest stays in it (within 2.5 blocks), unless it runs from a hurt. */
    static class NestlingGoal extends Goal {
        private final Maiasaurine calf;

        NestlingGoal(Maiasaurine calf) {
            this.calf = calf;
            this.setFlags(EnumSet.of(Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            return this.calf.isNestling() && !this.calf.isTame() && !this.calf.isVehicle() && !this.calf.isPassenger()
                    && this.calf.fleeLeft <= 0;
        }

        @Override
        public void tick() {
            BlockPos n = this.calf.nest;
            if (n == null) {
                return;
            }
            double d = n.distToCenterSqr(this.calf.position());
            if (d > 2.5D * 2.5D) {
                if (this.calf.getNavigation().isDone()) {
                    this.calf.getNavigation().moveTo(n.getX() + 0.5D, n.getY(), n.getZ() + 0.5D, 0.9D);
                }
            } else if (this.calf.getRandom().nextInt(200) == 0) {
                this.calf.getNavigation().moveTo(n.getX() + 0.5D + this.calf.getRandom().nextGaussian(), n.getY(),
                        n.getZ() + 0.5D + this.calf.getRandom().nextGaussian(), 0.6D);
            }
        }
    }
}
