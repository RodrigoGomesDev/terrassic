package com.terrassic.entity;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The hand-made Corythosaurus rig (tools/modelgen/handmade/corythosaurus, its own study:
 * docs/estudos/15_HERBIVOROS_1_11.md, approved by Rodrigo on 10/11/2026). Its touch is the VOICE and the EAR of the
 * forest: the Parasaurolophus has the alarm flag, the Edmontosaurus the sentinel, the Maiasaura the colony; the
 * Corythosaurus is the voice. What it adds over a plain grazer:
 * <ul>
 *   <li><b>the deep call</b> ("deep_call", through the helmet, the bill shut; Weishampel 1981, Norell et al. 2000,
 *       a HYPOTHESIS as to its use): heard by its kind at {@link #CALL_RANGE} blocks (the other calls reach 16 to 24).
 *       It regroups (a lost one walks back to the caller), it warns (the alarm call: every wild one of its kind within
 *       range, its herd and the herds near, wakes and runs from the threat, even those that do not see it), and it
 *       calms: the herbivores within {@link #CALM_RANGE} blocks stop panicking, drop their target and heal a little
 *       (the old Corythosaurus "calm", now tied to the call, and never while a predator is near);</li>
 *   <li><b>the ear of the forest</b>: it hears a predator on the move within {@link #HEAR_RANGE} blocks with no line
 *       of sight (behind trees), stops and turns the helmet ("listen"), then gives the alarm call (Schmitz & Motani
 *       2011: a sensitive ear);</li>
 *   <li><b>catemeral</b>: it never sleeps a whole night; it naps in short shifts of 1 to 3 minutes by day and by night
 *       (standing by day, "nap"; lying at night, "sleep"), and it only dozes off if another of the herd near is awake:
 *       there is always one on watch;</li>
 *   <li><b>fruit in the forest</b>: it takes berries off a bush ("pluck"; the bush goes back to its first stage) and
 *       rears to fruit and young leaves high up ("fruit_pick"); tame, fruit tames it faster than wheat;</li>
 *   <li><b>the helmet in profile</b> ("helmet_display"): two grown males near each other, or a male before a predator
 *       smaller than itself, stand broadside and show the whole helmet; they never fight, the one that lowers the head
 *       first walks off;</li>
 *   <li>wary: it runs with the herd, strikes back only cornered (kick_back, body_shove, the helmet blow); the fastest
 *       of the three hadrosaurs to ride; wades in the shallows with the head high ("wade").</li>
 * </ul>
 * One log line per behaviour, "[cory] ..." (logger "terrassic"), for the playtests (BehaviorTest phase "cory").
 */
public abstract class Corythosaurine extends HerbivoreDinosaur {
    /** The cycles (coryanims.py WALK, RUNP): pixels of ground each covers at 16.94 px/m and its length in ticks. */
    private static final double WALK_PX = 44.0D;
    private static final double WALK_TICKS = 32.0D;
    private static final double RUN_PX = 92.0D;
    private static final double RUN_TICKS = 12.4D;
    /** How far its kind hears the deep call. */
    public static final double CALL_RANGE = 64.0D;
    /** How far the call calms the herbivores. */
    public static final double CALM_RANGE = 16.0D;
    /** How far it hears a predator on the move without seeing it. */
    public static final double HEAR_RANGE = 24.0D;
    /** How far a herd mate counts as "near" for the watch and for being lost. */
    private static final double HERD = 24.0D;

    // the nap shifts; the behaviour test shortens them (TERRASSIC_CORY_FAST=1)
    private static final boolean FAST = "1".equals(System.getenv("TERRASSIC_CORY_FAST"));
    /** Ticks of a nap: 1 to 3 minutes. */
    public static int napMin = FAST ? 200 : 1200;
    public static int napMax = FAST ? 400 : 3600;
    /** Ticks awake between naps: by night 1 to 3 minutes, by day 3 to 6. */
    public static int awakeNight = FAST ? 300 : 1200;
    public static int awakeDay = FAST ? 600 : 3600;
    /** Ticks between two deep calls of one animal. */
    public static int callEvery = FAST ? 400 : 1200;

    private static final RawAnimation NAP = RawAnimation.begin().thenLoop("animation.corythosaurus.nap");
    private static final RawAnimation WADE = RawAnimation.begin().thenLoop("animation.corythosaurus.wade");

    private int napLeft;
    private int awakeLeft = 600 + (int) (Math.random() * 1200);
    private int still;
    private int callCooldown = 200;
    private int alarmCooldown;
    private int listenIn = -1;
    private LivingEntity heard;
    private LivingEntity fleeing;
    private int fleeTicks;
    private int displayCooldown = 200;
    private int displayLeft;
    private Corythosaurine rival;
    private int answerIn = -1;
    private LivingEntity answerTo;
    private int fruitCooldown = 100;
    private int bushTicks;
    private BlockPos bush;

    protected Corythosaurine(EntityType<? extends Corythosaurine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    public static void logLine(String line) {
        Behaviour.LOG.info("[cory] " + line);
    }

    private void log(String what) {
        logLine(what + " (#" + this.getId() + " " + this.getBlockX() + " " + this.getBlockY() + " " + this.getBlockZ() + ")");
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "call", "answer", "deep_call", "alarm", "listen", "fruit_pick", "pluck",
                "helmet_display", "drink", "hatch"};
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
        return 1.2F;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** The day nap is taken standing; in the shallows it wades with the head high. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.isSleeping() && this.level().isDay() && !this.isBaby() && !this.isSwimmingDeep()) {
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(NAP);
        }
        if (state.isMoving() && this.isInWater() && !this.isSwimmingDeep() && !this.isInSittingPose()
                && this.getDeltaMovement().horizontalDistanceSqr() <= this.runThresholdSqr()) {
            this.cycleSpeed = this.gaitSpeed(this.walkCycleSpeed() * 0.8D);
            return state.setAndContinue(WADE);
        }
        return super.movementAnimation(state);
    }

    // ------------------------------------------------------------------ temperament
    /** Wary: only a tame one fights; a wild one strikes back cornered (the kicks of HerbivoreDinosaur). */
    @Override
    protected boolean fightsBack() {
        return this.isTame();
    }

    @Override
    protected boolean fleesFrom(Player player) {
        return this.getLastHurtByMob() == player;
    }

    /** Fruit tames it faster than wheat (study 15: "aceita fruta melhor que trigo"). */
    @Override
    protected float biteValue(Player player, ItemStack food) {
        float k = food.is(Items.APPLE) || food.is(Items.SWEET_BERRIES) || food.is(Items.GLOW_BERRIES) ? 1.5F
                : food.is(Items.WHEAT) ? 0.75F : 1.0F;
        return super.biteValue(player, food) * k;
    }

    private boolean busy() {
        return this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isKnockedOut();
    }

    private List<Corythosaurine> kind(double r) {
        return this.level().getEntitiesOfClass(Corythosaurine.class, this.getBoundingBox().inflate(r, 16.0D, r),
                e -> e != this && e.isAlive() && !e.isTame());
    }

    public boolean isNapping() {
        return this.isSleeping() && this.napLeft > 0;
    }

    /** Asleep, or about to lie down for its nap. */
    public boolean dozing() {
        return this.isSleeping() || this.napLeft > 0;
    }

    public int napLeft() {
        return this.napLeft;
    }

    // ------------------------------------------------------------------ catemeral: naps in shifts, one always awake
    /** Its resting time is its nap, by day or by night (never the whole night). */
    @Override
    public boolean isSleepTime() {
        return this.napLeft > 0 && this.tickCount > 200 && !this.level().isThundering();
    }

    /** Asleep, it wakes to a predator it HEARS (no line of sight) as well as to what wakes the others. */
    @Override
    public boolean wokenByThreat() {
        return super.wokenByThreat() || this.hears() != null;
    }

    private void napStep() {
        if (this.napLeft > 0) {
            if (--this.napLeft == 0 || (!this.isSleeping() && this.napLeft < this.napMaxLeft() - 200)) {
                if (this.isSleeping()) {
                    this.log("nap over, awake (" + (this.level().isDay() ? "day" : "night") + ")");
                }
                this.napLeft = 0;
                this.setSleeping(false);
                this.awakeLeft = this.awakeFor();
            }
            return;
        }
        if (this.awakeLeft > 0) {
            this.awakeLeft--;
            return;
        }
        if (this.isBaby() || this.busy() || this.fleeTicks > 0 || this.isInWaterOrBubble()) {
            return;
        }
        // the watch: it dozes off only if another of the herd near is awake (alone, it dozes anyway)
        // (one that has just decided to nap counts as dozing: two deciding in the same second left none awake)
        List<Corythosaurine> herd = this.kind(HERD).stream().filter(e -> !e.isBaby()).toList();
        long awake = herd.stream().filter(e -> !e.dozing()).count();
        boolean watched = herd.isEmpty() || awake >= 1;
        boolean watchLeft = herd.isEmpty() || awake >= 2 || herd.size() == 1;
        if (!watched || !watchLeft) {
            this.awakeLeft = 200;
            this.log("keeps watch: the herd near (" + herd.size() + ") is dozing");
            return;
        }
        this.napLeft = napMin + this.random.nextInt(Math.max(1, napMax - napMin));
        this.napMax0 = this.napLeft;
        this.log("naps " + this.napLeft / 20 + " s (" + (this.level().isDay() ? "standing, day" : "lying, night") + "), "
                + awake + " of " + herd.size() + " near awake");
    }

    private int napMax0;

    private int napMaxLeft() {
        return this.napMax0;
    }

    private int awakeFor() {
        int base = this.level().isDay() ? awakeDay : awakeNight;
        return base + this.random.nextInt(base + 1);
    }

    // ------------------------------------------------------------------ the ear
    /** A wild grown predator on the move within HEAR_RANGE, awake: running, hunting or with a target. Null if none. */
    private LivingEntity hears() {
        for (PredatorDinosaur p : this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(HEAR_RANGE),
                q -> q.isAlive() && !q.isTame() && !q.isBaby() && !q.isSleeping() && q.distanceTo(this) < HEAR_RANGE)) {
            boolean moving = p.getDeltaMovement().horizontalDistanceSqr() > 0.004D || p.getTarget() != null;
            if (moving && (p.getTarget() != null || p.canHunt() || p.distanceTo(this) < 14.0F)) {
                return p;
            }
        }
        return null;
    }

    private void earStep() {
        if (this.listenIn >= 0) {
            this.getNavigation().stop();
            if (this.heard != null) {
                this.getLookControl().setLookAt(this.heard, 10.0F, 10.0F);
            }
            if (--this.listenIn < 0 && this.heard != null && this.heard.isAlive()) {
                this.deepAlarm(this.heard);
            }
            return;
        }
        if (this.tickCount % 10 != this.getId() % 10 || this.alarmCooldown > 0 || this.isTame() || this.isBaby()) {
            return;
        }
        LivingEntity p = this.hears();
        if (p == null) {
            return;
        }
        boolean sees = this.hasLineOfSight(p);
        boolean woke = this.isSleeping();
        this.napLeft = 0;
        this.setSleeping(false);
        this.awakeLeft = this.awakeFor();
        if (sees) {
            this.log((woke ? "wakes, " : "") + "sees " + ((DinosaurEntity) p).speciesId() + " at " + Math.round(p.distanceTo(this)) + " blocks");
            this.deepAlarm(p);
        } else {
            this.log((woke ? "wakes, " : "") + "hears " + ((DinosaurEntity) p).speciesId() + " at " + Math.round(p.distanceTo(this))
                    + " blocks without line of sight, listens");
            triggerAnim(ACTION_CONTROLLER, "listen");
            this.heardBlind = true;
            this.heard = p;
            this.listenIn = 40;
        }
    }

    // ------------------------------------------------------------------ the voice
    private void fleeFrom(LivingEntity threat) {
        Vec3 away = net.minecraft.world.entity.ai.util.DefaultRandomPos.getPosAway(this, 16, 7, threat.position());
        if (away == null) {
            Vec3 d = this.position().subtract(threat.position());
            away = this.position().add(new Vec3(d.x, 0.0D, d.z).normalize().scale(16.0D));
        }
        this.getNavigation().moveTo(away.x, away.y, away.z, 1.6D);
    }

    /** The voice carries: the deep call sounds deeper and four times further than the ambient voice (64 blocks). */
    private void voice(float pitch) {
        net.minecraft.sounds.SoundEvent s = this.getAmbientSound();
        if (s != null) {
            this.level().playSound(null, this.getX(), this.getY(), this.getZ(), s, SoundSource.NEUTRAL, 4.0F, pitch);
        }
    }

    /** The alarm call: every wild one of its kind within CALL_RANGE wakes and runs from the threat, seen or not. */
    public void deepAlarm(LivingEntity threat) {
        if (this.alarmCooldown > 0 || this.isTame()) {
            return;
        }
        this.alarmCooldown = 200;
        this.heard = null;
        this.listenIn = -1;
        if (!this.isBaby()) {
            this.getLookControl().setLookAt(threat, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "alarm");
            this.voice(0.5F);
        }
        this.setSleeping(false);
        this.napLeft = 0;
        this.fleeing = threat;
        this.fleeTicks = 100;
        this.alarmsGot++;
        this.fleeFrom(threat);
        int n = 0, far = 0, woke = 0, blind = 0;
        for (Corythosaurine other : this.kind(CALL_RANGE)) {
            if (other.distanceTo(this) > CALL_RANGE) {
                continue;
            }
            if (other.isSleeping()) {
                woke++;
                other.wokeToAlarm = true;
            }
            other.alarmsGot++;
            if (!other.hasLineOfSight(threat)) {
                blind++;
            }
            other.alarmCooldown = Math.max(other.alarmCooldown, 120);
            other.still = 0;
            other.napLeft = 0;
            other.setSleeping(false);
            other.awakeLeft = other.awakeFor();
            other.listenIn = -1;
            other.displayLeft = 0;
            other.goal = null;
            other.fleeing = threat;
            other.fleeTicks = 100;
            other.fleeFrom(threat);
            if (other.distanceTo(this) > HERD) {
                far++;
            }
            n++;
        }
        this.log("alarm call: " + (n + 1) + " of its kind run from " + threat.getName().getString() + " (" + far
                + " beyond " + (int) HERD + " blocks, " + woke + " woken, " + blind + " without sight of it)");
    }

    /** The deep call at rest: the lost come back to the caller, the herbivores near calm down, some answer. */
    public void deepCall() {
        triggerAnim(ACTION_CONTROLLER, "deep_call");
        this.voice(0.6F);
        this.still = Math.max(this.still, 90);
        this.callCooldown = callEvery + this.random.nextInt(callEvery);
        int regroup = 0, answers = 0, calmed = 0;
        for (Corythosaurine other : this.kind(CALL_RANGE)) {
            double d = other.distanceTo(this);
            if (d > CALL_RANGE || other.busy() || other.fleeTicks > 0) {
                continue;
            }
            boolean lost = !this.isTame() && d > HERD && other.kind(16.0D).stream().noneMatch(e -> !e.isBaby() && e != this);
            if (lost) {
                Vec3 to = this.position().add(other.position().subtract(this.position()).normalize().scale(6.0D));
                other.napLeft = 0;
                other.setSleeping(false);
                other.headFor(to, 600, 1.1D);
                regroup++;
            } else if (answers < 2 && !other.isSleeping() && other.answerIn < 0 && d < 40.0D) {
                other.answerTo = this;
                other.answerIn = 30 + this.random.nextInt(30) + answers * 20;
                other.callCooldown = Math.max(other.callCooldown, 300);
                answers++;
            }
        }
        // the calm: never while a hunter is near (there is something to run from then)
        if (this.nearestPredator(HEAR_RANGE, true) == null && this.level() instanceof ServerLevel server) {
            for (HerbivoreDinosaur h : server.getEntitiesOfClass(HerbivoreDinosaur.class, this.getBoundingBox().inflate(CALM_RANGE), e -> e != this)) {
                if (h.getLastHurtByMob() != null || h.getTarget() != null) {
                    calmed++;
                }
                h.setLastHurtByMob(null);
                h.setTarget(null);
                h.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0));
            }
        }
        this.log("deep call: " + regroup + " lost come back, " + answers + " answer, " + calmed + " herbivores calmed");
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        // a tame one calls too (its call still calms the pen); only the wild one regroups its kind
        if (!this.level().isClientSide() && !this.isBaby() && !this.busy() && !this.isSleeping()
                && this.callCooldown == 0 && this.fleeTicks == 0 && this.random.nextInt(2) == 0) {
            this.deepCall();
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && !this.isTame() && source.getEntity() instanceof LivingEntity attacker
                && !(attacker instanceof Player p && (p.isCreative() || p.isSpectator()))) {
            this.napLeft = 0;
            this.deepAlarm(attacker);
        }
        return hurt;
    }

    // ------------------------------------------------------------------ the helmet in profile
    private void displayStep() {
        if (this.displayCooldown > 0) {
            this.displayCooldown--;
        }
        if (this.displayLeft > 0) {
            this.displayLeft--;
            this.getNavigation().stop();
            LivingEntity other = this.rival;
            if (other != null && other.isAlive()) {
                // broadside: the body turned square to the line between them, the head toward it
                double dx = other.getX() - this.getX(), dz = other.getZ() - this.getZ();
                float toward = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
                float side = toward + (this.getId() % 2 == 0 ? 90.0F : -90.0F);
                this.setYRot(Mth.approachDegrees(this.getYRot(), side, 6.0F));
                this.yBodyRot = this.getYRot();
                this.getLookControl().setLookAt(other, 10.0F, 10.0F);
            }
            if (this.displayLeft % 96 == 95) {
                triggerAnim(ACTION_CONTROLLER, "helmet_display");
            }
            if (this.displayLeft == 0 && this.rival != null) {
                this.endDisplay();
            }
            return;
        }
        if (this.displayCooldown > 0 || this.isFemale() || this.isBaby() || this.isTame() || this.busy() || this.isSleeping()
                || this.tickCount % 20 != this.getId() % 20) {
            return;
        }
        for (Corythosaurine o : this.kind(10.0D)) {
            if (!o.isFemale() && !o.isBaby() && !o.busy() && !o.isSleeping() && o.displayLeft == 0 && o.displayCooldown == 0
                    && o.fleeTicks == 0) {
                int len = 190 + this.random.nextInt(100);
                this.startDisplay(o, len);
                o.startDisplay(this, len + 1);
                this.log("helmet display with male #" + o.getId() + ", " + len / 20 + " s");
                return;
            }
        }
        DinosaurEntity p = this.nearestPredator(12.0D, true);
        if (p != null && p.getBbWidth() < this.getBbWidth() && p.getTarget() != this && this.hasLineOfSight(p)) {
            this.startDisplay(p, 100);
            this.log("helmet display to " + p.speciesId() + " #" + p.getId());
        }
    }

    private void startDisplay(LivingEntity other, int ticks) {
        this.rival = other instanceof Corythosaurine c ? c : null;
        this.displayLeft = ticks;
        this.displayCooldown = 1200;
        this.still = 0;
        this.getNavigation().stop();
        if (this.rival == null) {
            this.rivalOther = other;
        }
        triggerAnim(ACTION_CONTROLLER, "helmet_display");
    }

    private LivingEntity rivalOther;

    /** The end: whoever lowers the head first (the lower health, or by lot) walks off. */
    private void endDisplay() {
        Corythosaurine o = this.rival;
        this.rival = null;
        if (o == null || !o.isAlive() || o.rival != this) {
            return;
        }
        o.rival = null;
        o.displayLeft = 0;
        Corythosaurine loser = this.getHealth() < o.getHealth() || (this.getHealth() == o.getHealth() && this.random.nextBoolean()) ? this : o;
        Corythosaurine winner = loser == this ? o : this;
        loser.triggerAnim(ACTION_CONTROLLER, "graze");
        Vec3 d = loser.position().subtract(winner.position());
        Vec3 to = loser.position().add(new Vec3(d.x, 0.0D, d.z).normalize().scale(14.0D));
        loser.headFor(to, 300, 1.0D);
        winner.displayCooldown = Math.max(winner.displayCooldown, 1200);
        // the winner holds its ground: when the loser led their herd, the winner's herd goal walked it straight after
        // the loser (6 to 8 blocks apart ten seconds later, in the test)
        winner.still = Math.max(winner.still, 300);
        winner.getNavigation().stop();
        this.log("helmet display over: #" + loser.getId() + " lowers the head and walks off, #" + winner.getId() + " stays");
    }

    // ------------------------------------------------------------------ walking somewhere far, leg by leg
    private Vec3 goal;
    private int goalTicks;
    private double goalSpeed;

    /** Walks to {@code to} over up to {@code ticks}, in legs of 14 blocks (a path is only found within the follow range). */
    private void headFor(Vec3 to, int ticks, double speed) {
        this.goal = to;
        this.goalTicks = ticks;
        this.goalSpeed = speed;
        this.still = 0;
        this.legTo();
    }

    private BlockPos leg;

    private void legTo() {
        Vec3 d = this.goal.subtract(this.position());
        Vec3 to = d.horizontalDistance() > 14.0D ? this.position().add(new Vec3(d.x, 0.0D, d.z).normalize().scale(14.0D)) : this.goal;
        this.leg = BlockPos.containing(to.x, this.goal.y, to.z);
        this.getNavigation().moveTo(to.x, this.goal.y, to.z, this.goalSpeed);
    }

    /** True while it is still on its way. */
    private boolean goalStep() {
        if (this.goal == null) {
            return false;
        }
        if (--this.goalTicks <= 0 || this.goal.distanceToSqr(this.position()) < 9.0D) {
            this.goal = null;
            return false;
        }
        // the herd goals pull it back to the others: while on its way its own leg wins
        net.minecraft.world.level.pathfinder.Path path = this.getNavigation().getPath();
        if (this.getNavigation().isDone() || path == null || this.leg == null || path.getTarget().distSqr(this.leg) > 9.0D) {
            this.legTo();
        }
        return true;
    }

    public boolean isDisplaying() {
        return this.displayLeft > 0;
    }

    // ------------------------------------------------------------------ fruit in the forest
    private BlockPos ripeBush(int r) {
        BlockPos here = this.blockPosition();
        BlockPos best = null;
        double bd = Double.MAX_VALUE;
        for (BlockPos p : BlockPos.betweenClosed(here.offset(-r, -2, -r), here.offset(r, 2, r))) {
            BlockState s = this.level().getBlockState(p);
            if (s.is(Blocks.SWEET_BERRY_BUSH) && s.getValue(SweetBerryBushBlock.AGE) >= 2) {
                double d = p.distSqr(here);
                if (d < bd) {
                    bd = d;
                    best = p.immutable();
                }
            }
        }
        return best;
    }

    private void fruitStep() {
        if (this.fruitCooldown > 0) {
            this.fruitCooldown--;
            return;
        }
        if (this.bush != null) {
            BlockState s = this.level().getBlockState(this.bush);
            if (!s.is(Blocks.SWEET_BERRY_BUSH) || s.getValue(SweetBerryBushBlock.AGE) < 2) {
                this.bush = null;
                return;
            }
            double d = this.bush.distToCenterSqr(this.position());
            double reach = 2.2D + this.getBbWidth();
            if (d < reach * reach) {
                this.getNavigation().stop();
                this.getLookControl().setLookAt(this.bush.getX() + 0.5D, this.bush.getY() + 0.5D, this.bush.getZ() + 0.5D);
                triggerAnim(ACTION_CONTROLLER, "pluck");
                this.level().setBlock(this.bush, s.setValue(SweetBerryBushBlock.AGE, 1), 2);
                this.level().playSound(null, this.bush, SoundEvents.SWEET_BERRY_BUSH_PICK_BERRIES, SoundSource.BLOCKS, 1.0F, 0.8F);
                this.feed(8);
                this.still = 64;
                this.log("plucks berries from the bush at " + this.bush.toShortString() + " (the bush back to stage 1)");
                this.bush = null;
                this.fruitCooldown = FAST ? 100 : 600;
            } else if (++this.bushTicks > 600) {
                // 30 s without reaching it (no way through): it gives up for a while
                this.log("gives up on the bush at " + this.bush.toShortString());
                this.bush = null;
                this.fruitCooldown = FAST ? 100 : 600;
            } else {
                // the herd and grazing goals take the navigation over and lead it elsewhere (the test bush was
                // never reached in 41 s): while it heads for the bush its own path wins, as in goalStep
                net.minecraft.world.level.pathfinder.Path path = this.getNavigation().getPath();
                if (this.bushTicks % 10 == 1 && (this.getNavigation().isDone() || path == null || path.getTarget().distSqr(this.bush) > 4.0D)) {
                    this.getNavigation().moveTo(this.bush.getX() + 0.5D, this.bush.getY(), this.bush.getZ() + 0.5D, 0.9D);
                }
            }
            return;
        }
        if (this.tickCount % 40 == this.getId() % 40 && (this.isHungry() || this.random.nextInt(4) == 0)) {
            this.bush = this.ripeBush(10);
            this.bushTicks = 0;
            if (this.bush == null && this.leavesHigh()) {
                triggerAnim(ACTION_CONTROLLER, "fruit_pick");
                this.still = 84;
                this.feed(6);
                this.fruitCooldown = FAST ? 200 : 900;
                this.log("rears to the fruit and young leaves high up");
            }
        }
    }

    private boolean leavesHigh() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        for (int up = 4; up <= 6; up++) {
            BlockPos p = BlockPos.containing(this.getX() + look.x * 2.5D, this.getY() + up * this.getScale(), this.getZ() + look.z * 2.5D);
            if (this.level().getBlockState(p).is(BlockTags.LEAVES)) {
                return true;
            }
        }
        return false;
    }

    private boolean waterInFront() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        BlockPos p = BlockPos.containing(this.getX() + look.x * 2.0D * this.getScale(), this.getY() - 0.5D, this.getZ() + look.z * 2.0D * this.getScale());
        return this.level().getFluidState(p).is(FluidTags.WATER) || this.level().getFluidState(p.above()).is(FluidTags.WATER);
    }

    // ------------------------------------------------------------------ the step
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
            if (caller != null && caller.isAlive() && !this.busy() && !this.isSleeping()) {
                this.getLookControl().setLookAt(caller, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "answer");
                this.still = Math.max(this.still, 40);
            }
        }
        if (this.isTame()) {
            if (!this.busy() && this.getNavigation().isDone() && this.random.nextInt(900) == 0 && this.waterInFront()) {
                triggerAnim(ACTION_CONTROLLER, "drink");
            }
            return;
        }
        this.earStep();
        this.napStep();
        if (this.fleeTicks > 0) {
            this.fleeTicks--;
            this.still = 0;
            if (this.fleeing != null && this.fleeing.isAlive() && this.getNavigation().isDone()
                    && this.distanceToSqr(this.fleeing) < HEAR_RANGE * HEAR_RANGE) {
                this.fleeFrom(this.fleeing);
            }
            return;
        }
        if (this.isSleeping() || this.listenIn >= 0 || this.isBaby()) {
            return;
        }
        this.displayStep();
        if (this.displayLeft > 0 || this.goalStep()) {
            return;
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.busy()) {
            return;
        }
        this.fruitStep();
        if (this.getNavigation().isDone() && this.random.nextInt(700) == 0 && (this.isInWater() || this.waterInFront())) {
            triggerAnim(ACTION_CONTROLLER, "drink");
            this.still = 70;
        }
    }

    // ------------------------------------------------------------------ saving
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("CoryNap", this.napLeft);
        tag.putInt("CoryAwake", this.awakeLeft);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.napLeft = tag.getInt("CoryNap");
        this.napMax0 = this.napLeft;
        if (tag.contains("CoryAwake")) {
            this.awakeLeft = tag.getInt("CoryAwake");
        }
    }

    /** Test only (BehaviorTest "cory"): drowsy now (it naps at the next check, if the watch lets it), or wide awake. */
    public void testDrowsy(boolean drowsy) {
        this.awakeLeft = drowsy ? 0 : 1_000_000;
        this.callCooldown = drowsy ? this.callCooldown : 1_000_000;
    }

    /** Test only: it heard a predator it could not see (since the last reset). */
    public boolean heardBlind;
    /** Test: alarms this one gave or got, and whether one of them woke it from a nap (latched; the shortened test
     *  shifts let it doze again a few seconds later). */
    public int alarmsGot;
    public boolean wokeToAlarm;

    public boolean isFleeing() {
        return this.fleeTicks > 0;
    }

    public void testCallCooldown(int ticks) {
        this.callCooldown = ticks;
    }

    /** Test only: asleep now in a nap of {@code ticks}. */
    public void testNap(int ticks) {
        this.napLeft = ticks;
        this.napMax0 = ticks;
        this.getNavigation().stop();
        this.setSleeping(true);
    }

    public void testNoDisplay() {
        this.displayCooldown = 1_000_000;
    }

    public void testDisplayReady() {
        this.displayCooldown = 0;
    }
}
