package com.terrassic.entity;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The hand-made Pachyrhinosaurus rig (tools/modelgen/handmade/pachyrhinosaurus, its own study:
 * docs/estudos/15_HERBIVOROS_1_11.md, approved by Rodrigo on 10/11/2026; the "bisão" silhouette of 16/11). The
 * Triceratops and the Styracosaurus charge; the Pachyrhinosaurus makes a WALL. What it adds over a plain herbivore:
 * <ul>
 *   <li><b>the defence ring</b> ("ring_defence", "brace"): a wild grown predator of some size within
 *       {@link #RING_ALERT} blocks and the grown ones of the herd ({@link #HERD} blocks) neither run nor charge one by
 *       one: they take places on a ring round the middle of the herd, facing out (the one the predator is on faces it),
 *       braced with the head low showing the boss; the calves and the wounded (under 40% of their health) go into the
 *       middle and stay there. Only the one the predator comes within {@link #SALLY} blocks of breaks out, a short butt
 *       of the boss ("boss_ram", a real blow) and back to its place. It lasts while the predator is within
 *       {@link #RING_KEEP} blocks of the ring (the musk ox, the animal Hieronymus et al. 2009 compared the boss with;
 *       the four age groups of Pipestone Creek, Currie, Langston &amp; Tanke 2008: a HYPOTHESIS);</li>
 *   <li><b>the boss duel</b>: two grown wild males near each other back off a few steps, run at each other and butt
 *       boss to boss ("boss_ram"), then push brow to brow (the horn lock of DinosaurEntity, its loop the "boss_push")
 *       until one gives in and walks off; for show, nobody is hurt. A real duel (ai/DuelGoal, ai/DuelStyle) is the
 *       same weapons: it blocks a lot, hardly dodges and hardly staggers ({@link #staggerGive});</li>
 *   <li><b>the river crossing</b>: the herbivore that migrates. When the herd's route meets water, the herd waits on
 *       the bank ("hesitate"), the leader wades in first and the others follow together, the head high ("wade");</li>
 *   <li>a beast of the cold: on snow it scrapes the snow off with the beak and the boss to graze what is under it
 *       ("snow_dig"); idle, it rubs the boss on a trunk or a rock ("boss_rub"); the toss of the head is its threat
 *       ("head_toss"). Territorial in the herd: whoever comes close to the calves gets the boss. The old musk is gone
 *       (the ring takes its part: it draws the predator to itself and keeps the others safe).</li>
 * </ul>
 * One log line per behaviour, "[pachy] ..." (logger "terrassic"), for the playtests (BehaviorTest phase "pachy").
 */
public abstract class Pachyrhinosaurine extends HerbivoreDinosaur {
    /** The cycles (pachyanims.py WALK, RUNP, CHARGEP): pixels of ground each covers at 16.94 px/m and its length in
     *  ticks. */
    private static final double WALK_PX = 26.0D;
    private static final double WALK_TICKS = 30.0D;
    private static final double RUN_PX = 54.0D;
    private static final double RUN_TICKS = 12.4D;
    private static final double CHARGE_PX = 60.0D;
    private static final double CHARGE_TICKS = 11.2D;

    /** A predator this close makes the herd ring up; the ring holds while it stays within RING_KEEP of the middle. */
    public static final double RING_ALERT = 20.0D;
    public static final double RING_KEEP = 28.0D;
    /** The herd: the ones of its kind this close. */
    public static final double HERD = 24.0D;
    /** The gap (box to box) at which the nearest of the ring breaks out at the predator. */
    public static final double SALLY = 4.0D;
    /** The smallest predator the ring is for (a raptor is just fought). */
    private static final float BIG = 1.2F;

    private static final boolean FAST = "1".equals(System.getenv("TERRASSIC_PACHY_FAST"));
    /** Ticks between two boss bouts of one male. */
    public static int boutEvery = FAST ? 200 : 2400;

    private static final EntityDataAccessor<Boolean> DATA_BRACED =
            SynchedEntityData.defineId(Pachyrhinosaurine.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation BRACE = RawAnimation.begin().thenLoop("animation.pachyrhinosaurus.brace");
    private static final RawAnimation WADE = RawAnimation.begin().thenLoop("animation.pachyrhinosaurus.wade");
    private RawAnimation chargeAnim;

    private Ring ring;
    private int sallyTick = -1;
    /** Ticks the loser of a bout keeps walking off, and where to. */
    private int walkOff;
    private Vec3 walkOffTo;
    /** Ticks it holds its place after a sally before it may break out again. */
    private int sallyRest;
    private boolean placed;
    private int still;
    private int gestureCooldown = 200;
    private int boutCooldown = 600 + (int) (Math.random() * 1200);
    private Pachyrhinosaurine boutWith;
    private int boutStage;
    private int boutTicks;
    private Crossing crossing;
    private int threatCooldown;

    protected Pachyrhinosaurine(EntityType<? extends Pachyrhinosaurine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    public static void logLine(String line) {
        Behaviour.LOG.info("[pachy] " + line);
    }

    private void log(String what) {
        logLine(what + " (#" + this.getId() + " " + this.getBlockX() + " " + this.getBlockY() + " " + this.getBlockZ() + ")");
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_BRACED, false);
    }

    public boolean isBraced() {
        return this.entityData.get(DATA_BRACED);
    }

    private void setBraced(boolean b) {
        if (this.isBraced() != b) {
            this.entityData.set(DATA_BRACED, b);
        }
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "call", "roar", "ring_defence", "boss_ram", "boss_rub", "snow_dig", "hesitate",
                "head_toss", "drink", "hatch"};
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
    protected boolean ownGestures() {
        return true;
    }

    @Override
    protected int deathAnimTicks() {
        return 60;
    }

    @Override
    public float babyHeadScale() {
        return 1.25F;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** Braced in the ring it stands square with the head low; with a target it charges, the boss levelled; in the
     *  shallows it wades with the head high. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.isBraced() && !state.isMoving() && !this.isSleeping() && !this.isKnockedOut()) {
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(BRACE);
        }
        if (state.isMoving() && this.isAggressive() && !this.isVehicle() && !this.isBaby() && !this.isKnockedOut()
                && !this.isSleeping() && !this.isInSittingPose() && !this.isSwimmingDeep() && !this.isDueling()) {
            if (this.chargeAnim == null) {
                this.chargeAnim = RawAnimation.begin().thenLoop(anim("charge"));
            }
            this.cycleSpeed = this.gaitSpeed(CHARGE_PX / 16.0D / CHARGE_TICKS * this.modelScale());
            return state.setAndContinue(this.chargeAnim);
        }
        if (state.isMoving() && this.isInWater() && !this.isSwimmingDeep() && !this.isInSittingPose()
                && this.getDeltaMovement().horizontalDistanceSqr() <= this.runThresholdSqr()) {
            this.cycleSpeed = this.gaitSpeed(this.walkCycleSpeed() * 0.8D);
            return state.setAndContinue(WADE);
        }
        return super.movementAnimation(state);
    }

    /** ai/DuelGoal: staggered, it barely gives (the heavy low body, the boss taking the blow): a share of the spin. */
    public static float staggerGive(DinosaurEntity mob) {
        return mob instanceof Pachyrhinosaurine ? 0.35F : 1.0F;
    }

    @Override
    protected void addExtraGoals() {
        this.goalSelector.addGoal(0, new RingGoal());
        this.goalSelector.addGoal(7, new CrossGoal());
    }

    private List<Pachyrhinosaurine> kind(double r) {
        return this.level().getEntitiesOfClass(Pachyrhinosaurine.class, this.getBoundingBox().inflate(r, 8.0D, r),
                e -> e != this && e.isAlive() && !e.isTame() && e.distanceTo(this) <= r);
    }

    private boolean busy() {
        return this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isKnockedOut() || this.inRing()
                || this.isLocked();
    }

    // ================================================================== the defence ring

    /** One ring: the middle, the predator, the grown ones on it (in slot order) and the ones in the middle. */
    public static final class Ring {
        public Vec3 centre;
        public double radius;
        public LivingEntity predator;
        public final List<Pachyrhinosaurine> adults = new ArrayList<>();
        public final List<Pachyrhinosaurine> middle = new ArrayList<>();
        public int sallies;
        public int hits;
        public boolean over;
        public long started;
        Pachyrhinosaurine sallier;
        int sallyCooldown;
        long tickedAt = -1;
        float baseAngle;

        Vec3 slot(Pachyrhinosaurine p) {
            int i = this.adults.indexOf(p);
            int n = Math.max(1, this.adults.size());
            if (n == 1) {
                // a lone grown one stands between the predator and the calves
                Vec3 d = this.predator.position().subtract(this.centre);
                Vec3 h = new Vec3(d.x, 0.0D, d.z);
                return h.lengthSqr() < 1.0E-4D ? this.centre : this.centre.add(h.normalize().scale(this.radius));
            }
            double a = this.baseAngle + Mth.TWO_PI * i / n;
            return this.centre.add(Math.cos(a) * this.radius, 0.0D, Math.sin(a) * this.radius);
        }

        Vec3 inside(Pachyrhinosaurine p) {
            int i = this.middle.indexOf(p);
            if (this.middle.size() <= 1) {
                return this.centre;
            }
            double a = Mth.TWO_PI * i / this.middle.size();
            double r = Math.min(1.2D, this.radius * 0.3D);
            return this.centre.add(Math.cos(a) * r, 0.0D, Math.sin(a) * r);
        }

        /** The predator's bearing from the middle sets slot 0 on its side; the grown ones take the nearest slots. */
        void layout() {
            Vec3 d = this.predator.position().subtract(this.centre);
            this.baseAngle = (float) Math.atan2(d.z, d.x);
            int n = this.adults.size();
            float w = 0.0F;
            for (Pachyrhinosaurine p : this.adults) {
                w = Math.max(w, p.getBbWidth());
            }
            this.radius = Math.max(w * 1.5D + 1.5D, n * w * 1.4D / Mth.TWO_PI);
            // the greedy assignment: each slot in turn takes the nearest free grown one
            List<Pachyrhinosaurine> free = new ArrayList<>(this.adults);
            List<Pachyrhinosaurine> order = new ArrayList<>();
            for (int k = 0; k < n; k++) {
                double a = this.baseAngle + Mth.TWO_PI * k / Math.max(1, n);
                Vec3 s = this.centre.add(Math.cos(a) * this.radius, 0.0D, Math.sin(a) * this.radius);
                Pachyrhinosaurine best = free.stream().min(Comparator.comparingDouble(p -> p.position().distanceToSqr(s))).orElse(null);
                free.remove(best);
                order.add(best);
            }
            this.adults.clear();
            this.adults.addAll(order);
        }

        boolean holds() {
            return !this.over && this.predator != null && this.predator.isAlive() && !(this.predator instanceof DinosaurEntity d && d.isTame())
                    && this.predator.position().distanceTo(this.centre) <= RING_KEEP && !this.adults.isEmpty();
        }
    }

    public Ring ring() {
        return this.ring;
    }

    public boolean inRing() {
        return this.ring != null && !this.ring.over;
    }

    /** In the middle of the ring (a calf or a wounded one). */
    public boolean inMiddle() {
        return this.inRing() && this.ring.middle.contains(this);
    }

    private static boolean wounded(Pachyrhinosaurine p) {
        return p.isBaby() || p.getHealth() < p.getMaxHealth() * 0.4F;
    }

    /** A wild grown predator of some size within RING_ALERT, awake. */
    private LivingEntity bigPredator() {
        LivingEntity best = null;
        double bd = RING_ALERT * RING_ALERT;
        for (PredatorDinosaur p : this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(RING_ALERT),
                q -> q.isAlive() && !q.isTame() && !q.isBaby() && !q.isSleeping() && q.getBbWidth() >= BIG)) {
            double d = p.distanceToSqr(this);
            if (d < bd) {
                bd = d;
                best = p;
            }
        }
        return best;
    }

    private void ringStep() {
        if (this.ring != null && this.ring.over) {
            this.ring = null;
        }
        if (this.inRing() || this.isTame() || this.tickCount % 10 != this.getId() % 10) {
            return;
        }
        LivingEntity p = this.bigPredator();
        if (p == null) {
            return;
        }
        // join a ring of the herd that is already standing, or close a new one
        for (Pachyrhinosaurine o : this.kind(HERD)) {
            if (o.inRing() && o.ring.predator == p) {
                this.join(o.ring);
                o.ring.layout();
                this.log("joins the ring " + (wounded(this) ? "in the middle" : "on the edge"));
                return;
            }
        }
        List<Pachyrhinosaurine> herd = new ArrayList<>(this.kind(HERD));
        herd.add(this);
        if (herd.stream().noneMatch(e -> !wounded(e))) {
            return;     // calves alone: they run (PanicGoal, BabyStayGoal)
        }
        Ring r = new Ring();
        r.predator = p;
        r.started = this.level().getGameTime();
        double x = 0.0D, y = 0.0D, z = 0.0D;
        for (Pachyrhinosaurine e : herd) {
            x += e.getX();
            y += e.getY();
            z += e.getZ();
        }
        r.centre = new Vec3(x / herd.size(), y / herd.size(), z / herd.size());
        for (Pachyrhinosaurine e : herd) {
            if (!e.inRing()) {
                e.join(r);
            }
        }
        r.layout();
        logLine(String.format(java.util.Locale.ROOT, "ring: %d grown ones close a ring of %.1f blocks round %d in the middle, facing %s at %.0f blocks",
                r.adults.size(), r.radius, r.middle.size(), ((DinosaurEntity) p).speciesId(), p.position().distanceTo(r.centre)));
    }

    private void join(Ring r) {
        this.ring = r;
        this.placed = false;
        this.sallyTick = -1;
        this.setSleeping(false);
        this.setTarget(null);
        this.getNavigation().stop();
        this.boutWith = null;
        this.boutStage = 0;
        if (wounded(this)) {
            r.middle.add(this);
        } else {
            r.adults.add(this);
        }
    }

    private void leaveRing() {
        this.setBraced(false);
        this.placed = false;
        this.sallyTick = -1;
        this.ring = null;
    }

    /** The ring's shared bookkeeping, once a tick (by whichever member ticks first). */
    private void ringTick(Ring r) {
        long now = this.level().getGameTime();
        if (r.tickedAt == now) {
            return;
        }
        r.tickedAt = now;
        r.adults.removeIf(e -> !e.isAlive() || e.ring != r);
        r.middle.removeIf(e -> !e.isAlive() || e.ring != r);
        // one hurt badly on the edge steps into the middle
        for (Pachyrhinosaurine e : new ArrayList<>(r.adults)) {
            if (wounded(e) && r.adults.size() > 1) {
                r.adults.remove(e);
                r.middle.add(e);
                e.placed = false;
                e.setBraced(false);
                logLine("ring: #" + e.getId() + " hurt, steps into the middle");
                r.layout();
            }
        }
        if (r.sallyCooldown > 0) {
            r.sallyCooldown--;
        }
        if (!r.holds()) {
            r.over = true;
            String why = r.predator == null || !r.predator.isAlive() ? "the predator is dead"
                    : "the predator is " + Math.round(r.predator.position().distanceTo(r.centre)) + " blocks off";
            logLine(String.format(java.util.Locale.ROOT, "ring over after %d s: %s; %d sallies, %d blows landed",
                    (now - r.started) / 20, why, r.sallies, r.hits));
        }
    }

    private final class RingGoal extends Goal {
        RingGoal() {
            this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            return me.inRing() && !me.isVehicle() && !me.isKnockedOut() && !me.isTame();
        }

        @Override
        public boolean canContinueToUse() {
            return this.canUse();
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void stop() {
            Pachyrhinosaurine.this.leaveRing();
        }

        @Override
        public void tick() {
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            Ring r = me.ring;
            if (r == null) {
                return;
            }
            me.ringTick(r);
            if (r.over) {
                return;
            }
            LivingEntity pred = r.predator;
            me.setTarget(null);
            if (r.middle.contains(me)) {
                me.setBraced(false);
                me.goTo(r.inside(me), 0.8D, 1.0D);
                me.getLookControl().setLookAt(pred, 20.0F, 20.0F);
                return;
            }
            if (me.sallyTick >= 0) {
                me.sally(r, pred);
                return;
            }
            Vec3 slot = r.slot(me);
            boolean there = me.goTo(slot, 1.1D, 2.0D);
            // facing: out from the middle; the one the predator is on (within 12 blocks, on its side) faces it
            Vec3 out = slot.subtract(r.centre);
            if (out.lengthSqr() < 1.0E-4D) {
                out = pred.position().subtract(r.centre);
            }
            float outYaw = (float) (Mth.atan2(out.z, out.x) * Mth.RAD_TO_DEG) - 90.0F;
            double dx = pred.getX() - me.getX(), dz = pred.getZ() - me.getZ();
            float predYaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
            float yaw = Math.abs(Mth.wrapDegrees(predYaw - outYaw)) < 100.0F && me.distanceTo(pred) < 12.0F ? predYaw : outYaw;
            if (there) {
                me.setYRot(Mth.approachDegrees(me.getYRot(), yaw, 8.0F));
                me.yBodyRot = me.getYRot();
                me.yHeadRot = Mth.approachDegrees(me.yHeadRot, predYaw, 10.0F);
                if (!me.placed) {
                    me.placed = true;
                    me.triggerAnim(ACTION_CONTROLLER, "ring_defence");
                }
            }
            me.setBraced(there);
            me.getLookControl().setLookAt(pred, 20.0F, 20.0F);
            // the sally: the nearest grown one breaks out when the predator comes within SALLY of it
            // (in its place or still shuffling into it: a predator at the wall is met either way)
            if (me.sallyRest > 0) {
                me.sallyRest--;
            }
            if (r.sallier == null && r.sallyCooldown == 0 && me.sallyRest == 0 && me.gap(pred) <= SALLY) {
                Pachyrhinosaurine nearest = r.adults.stream().min(Comparator.comparingDouble(e -> e.distanceToSqr(pred))).orElse(me);
                if (nearest == me) {
                    r.sallier = me;
                    me.sallyTick = 0;
                    me.setBraced(false);
                    me.triggerAnim(ACTION_CONTROLLER, "boss_ram");
                    r.sallies++;
                    me.log("ring: breaks out at the " + ((DinosaurEntity) pred).speciesId() + String.format(java.util.Locale.ROOT, " (%.1f blocks)", me.gap(pred)));
                }
            }
        }
    }

    /** Box-to-box gap to an entity. */
    private double gap(Entity e) {
        return this.distanceTo(e) - (this.getBbWidth() + e.getBbWidth()) * 0.5D;
    }

    /** Walks to {@code at}; true when there (within {@code tol} blocks). */
    private boolean goTo(Vec3 at, double speed, double tol) {
        double dx = at.x - this.getX(), dz = at.z - this.getZ();
        if (dx * dx + dz * dz <= tol * tol) {
            this.getNavigation().stop();
            return true;
        }
        if (this.getNavigation().isDone() || this.tickCount % 20 == 0) {
            this.getNavigation().moveTo(at.x, at.y, at.z, speed);
        }
        return false;
    }

    /** The sally: three or four quick steps at the predator, the butt at tick 12 (boss_ram), and back to the place. */
    private void sally(Ring r, LivingEntity pred) {
        this.sallyTick++;
        this.getLookControl().setLookAt(pred, 30.0F, 30.0F);
        double dx = pred.getX() - this.getX(), dz = pred.getZ() - this.getZ();
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        this.setYRot(Mth.approachDegrees(this.getYRot(), yaw, 12.0F));
        this.yBodyRot = this.getYRot();
        if (this.sallyTick <= 12) {
            Vec3 d = new Vec3(dx, 0.0D, dz).normalize().scale(0.22D);
            this.setDeltaMovement(this.getDeltaMovement().add(d.x * 0.5D, 0.0D, d.z * 0.5D));
            this.getNavigation().moveTo(pred, 1.5D);
        }
        if (this.sallyTick == 12) {
            if (this.gap(pred) <= 2.6D) {
                this.doHurtTarget(pred);
                r.hits++;
                this.impact(pred.getX(), pred.getY(), pred.getZ(), 0.6F, true);
                this.log("ring: the boss lands on the " + ((DinosaurEntity) pred).speciesId());
            }
            this.getNavigation().stop();
        }
        if (this.sallyTick >= 30) {
            this.sallyTick = -1;
            r.sallier = null;
            r.sallyCooldown = 30;
            this.sallyRest = 100;      // back in its place and braced before it breaks out again
            this.placed = false;
            this.log("ring: back to its place");
        }
    }

    @Override
    public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        // in the ring it holds: the herd does not scatter after the one hit, the ring answers with its sallies
        if (hurt && this.inRing() && !this.level().isClientSide()) {
            this.setTarget(null);
        }
        return hurt;
    }

    // ================================================================== the boss duel of two males

    private void boutStep() {
        if (this.boutCooldown > 0) {
            this.boutCooldown--;
        }
        if (this.boutWith != null) {
            this.boutTick();
            return;
        }
        if (this.boutCooldown > 0 || this.isFemale() || this.isBaby() || this.isTame() || this.busy() || this.isSleeping()
                || this.tickCount % 20 != this.getId() % 20 || (this.crossing != null && !this.crossing.done)) {
            return;
        }
        for (Pachyrhinosaurine o : this.kind(10.0D)) {
            if (!o.isFemale() && !o.isBaby() && !o.busy() && !o.isSleeping() && o.boutWith == null && o.boutCooldown == 0
                    && o.getId() > this.getId()) {
                this.startBout(o);
                o.startBout(this);
                this.log("boss bout with male #" + o.getId());
                return;
            }
        }
    }

    private void startBout(Pachyrhinosaurine o) {
        this.boutWith = o;
        this.boutStage = 1;
        this.boutTicks = 0;
        this.boutCooldown = boutEvery + this.random.nextInt(boutEvery + 1);
        this.getNavigation().stop();
    }

    public boolean inBout() {
        return this.boutWith != null;
    }

    /** Bout counters for the tests: butts, locks, ended bouts. */
    public static int bouts, boutRams, boutLocks;

    private void boutTick() {
        Pachyrhinosaurine o = this.boutWith;
        if (o == null || !o.isAlive() || o.boutWith != this || this.inRing() || this.getTarget() != null || this.isVehicle()) {
            this.boutWith = null;
            this.boutStage = 0;
            return;
        }
        this.boutTicks++;
        this.getLookControl().setLookAt(o, 30.0F, 30.0F);
        double dx = o.getX() - this.getX(), dz = o.getZ() - this.getZ();
        float toward = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        Vec3 d = new Vec3(dx, 0.0D, dz);
        switch (this.boutStage) {
            case 1 -> {
                // face each other, a toss of the head
                this.getNavigation().stop();
                this.setYRot(Mth.approachDegrees(this.getYRot(), toward, 8.0F));
                this.yBodyRot = this.getYRot();
                if (this.boutTicks == 6) {
                    this.triggerAnim(ACTION_CONTROLLER, "head_toss");
                }
                if (this.boutTicks >= 30) {
                    this.boutStage = 2;
                    this.boutTicks = 0;
                }
            }
            case 2 -> {
                // back off a few steps
                Vec3 back = this.position().subtract(d.normalize().scale(4.0D));
                this.getNavigation().moveTo(back.x, this.getY(), back.z, 0.7D);
                if (this.boutTicks >= 40 || d.length() > 9.0D + this.getBbWidth()) {
                    this.getNavigation().stop();
                    this.boutStage = 3;
                    this.boutTicks = 0;
                }
            }
            case 3 -> {
                // turn back, a moment, then the run at each other and the butt
                this.setYRot(Mth.approachDegrees(this.getYRot(), toward, 10.0F));
                this.yBodyRot = this.getYRot();
                if (this.boutTicks == 15) {
                    this.triggerAnim(ACTION_CONTROLLER, "boss_ram");
                    boutRams++;
                }
                if (this.boutTicks > 15 && (this.boutTicks % 10 == 6 || this.getNavigation().isDone())) {
                    this.getNavigation().moveTo(o, 1.5D);
                }
                if (this.boutTicks > 15 && this.gap(o) < 1.0D) {
                    this.getNavigation().stop();
                    this.impact(o.getX(), o.getY(), o.getZ(), 0.8F, true);
                    if (this.getId() < o.getId()) {
                        this.lockHorns(o);          // brow to brow: the boss_push loop (DinosaurEntity.lockHorns)
                        boutLocks++;
                        this.log("boss bout: the butt, then brow to brow with #" + o.getId());
                    }
                    this.boutStage = 4;
                    this.boutTicks = 0;
                } else if (this.boutTicks > 120) {
                    this.boutStage = 4;
                    this.boutTicks = 0;
                }
            }
            default -> {
                // pushing until the lock lets go; then the weaker gives in and walks off
                if (!this.isLocked() && !o.isLocked() && this.boutTicks > 10) {
                    if (this.getId() < o.getId()) {
                        Pachyrhinosaurine loser = this.getHealth() < o.getHealth()
                                || (this.getHealth() == o.getHealth() && this.random.nextBoolean()) ? this : o;
                        Pachyrhinosaurine winner = loser == this ? o : this;
                        Vec3 away = loser.position().subtract(winner.position());
                        Vec3 to = loser.position().add(new Vec3(away.x, 0.0D, away.z).normalize().scale(14.0D));
                        loser.getNavigation().moveTo(to.x, to.y, to.z, 1.0D);
                        loser.still = 0;
                        loser.walkOff = 200;            // it keeps walking off, and leaves the winner alone for a while
                        loser.walkOffTo = to;
                        loser.boutCooldown = Math.max(loser.boutCooldown, 2400);
                        winner.boutCooldown = Math.max(winner.boutCooldown, 600);
                        winner.still = 120;             // the winner holds its ground (and does not follow it)
                        winner.triggerAnim(ACTION_CONTROLLER, "roar");
                        bouts++;
                        this.log("boss bout over: #" + loser.getId() + " gives in and walks off, #" + winner.getId() + " stays");
                    }
                    this.boutWith = null;
                    this.boutStage = 0;
                } else if (this.boutTicks > 300) {
                    this.boutWith = null;
                    this.boutStage = 0;
                }
            }
        }
    }

    // ================================================================== the river crossing

    /** One crossing of the herd: the bank, the far side, the leader's wait, who has crossed. */
    public static final class Crossing {
        public Vec3 bank;
        public Vec3 far;
        public final Pachyrhinosaurine leader;
        public int wait;
        public boolean leaderIn;
        public long leaderInAt = -1;
        public int firstFollowerIn = -1;
        public final List<Integer> crossed = new ArrayList<>();
        public int waited;
        public boolean done;

        Crossing(Pachyrhinosaurine leader) {
            this.leader = leader;
        }
    }

    /** The last crossing started (for the tests). */
    public static volatile Crossing lastCrossing;

    public Crossing crossing() {
        return this.crossing;
    }

    /** Water within {@code r} blocks ahead toward {@code to}, at the feet. */
    private boolean waterToward(Vec3 dir, int r) {
        for (int k = 1; k <= r; k++) {
            BlockPos p = BlockPos.containing(this.getX() + dir.x * k, this.getY() - 0.5D, this.getZ() + dir.z * k);
            if (this.level().getFluidState(p).is(FluidTags.WATER) || this.level().getFluidState(p.above()).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }

    /** The first dry ground past the water toward {@code dir}, plus a few blocks; null if none within 32. */
    private Vec3 farBank(Vec3 dir) {
        boolean wet = false;
        for (int k = 1; k <= 32; k++) {
            double x = this.getX() + dir.x * k, z = this.getZ() + dir.z * k;
            BlockPos p = BlockPos.containing(x, this.getY() - 0.5D, z);
            boolean water = this.level().getFluidState(p).is(FluidTags.WATER) || this.level().getFluidState(p.above()).is(FluidTags.WATER);
            if (water) {
                wet = true;
            } else if (wet) {
                return new Vec3(x + dir.x * 5.0D, this.getY(), z + dir.z * 5.0D);
            }
        }
        return null;
    }

    private final class CrossGoal extends Goal {
        private int stage;
        private int delay;

        CrossGoal() {
            this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        private Crossing find() {
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            if (me.isBaby() || me.isTame()) {
                return null;
            }
            if (me.getMigrationTarget() == null) {
                return me.crossing != null && !me.crossing.done && me.crossing.leader != me
                        && !me.crossing.crossed.contains(me.getId()) ? me.crossing : null;
            }
            DinosaurEntity lead = me.herdLeader();
            if (lead == null) {
                // it leads: water ahead on the way?
                if (me.crossing != null && !me.crossing.done) {
                    // its own crossing: until it is over on the far bank (then it waits for the rest, no new one)
                    return me.crossing.crossed.contains(me.getId()) ? null : me.crossing;
                }
                if (me.tickCount % 5 != 0) {
                    return null;
                }
                Vec3 to = Vec3.atBottomCenterOf(me.getMigrationTarget()).subtract(me.position());
                Vec3 dir = new Vec3(to.x, 0.0D, to.z);
                if (dir.lengthSqr() < 1.0E-4D) {
                    return null;
                }
                dir = dir.normalize();
                // on the bank, or just in at the edge (the ground 3 blocks back still dry): a fast herd steps in before it looks
                boolean edge = !me.isInWater() || me.level().getFluidState(BlockPos.containing(
                        me.position().subtract(dir.scale(3.0D)))).isEmpty();
                if (edge && me.waterToward(dir, 6 + (int) me.getBbWidth())) {
                    Vec3 far = me.farBank(dir);
                    if (far != null) {
                        Crossing c = new Crossing(me);
                        c.bank = me.position();
                        c.far = far;
                        c.wait = 50 + me.random.nextInt(40);
                        me.crossing = c;
                        lastCrossing = c;
                        me.log("river crossing: the herd stops on the bank and waits");
                        return c;
                    }
                }
                return null;
            }
            if (lead instanceof Pachyrhinosaurine p && p.crossing != null && !p.crossing.done && !p.crossing.crossed.contains(me.getId())
                    && me.distanceTo(p) < HERD + 8.0D) {
                return p.crossing;
            }
            return null;
        }

        @Override
        public boolean canUse() {
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            if (me.inRing() || me.getTarget() != null || me.isVehicle()) {
                return false;
            }
            Crossing c = this.find();
            if (c == null) {
                return false;
            }
            me.crossing = c;
            return true;
        }

        @Override
        public boolean canContinueToUse() {
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            return me.crossing != null && !me.crossing.done && !me.inRing() && me.getTarget() == null
                    && !me.crossing.crossed.contains(me.getId());
        }

        @Override
        public void start() {
            this.stage = 0;
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            Crossing c = me.crossing;
            me.getNavigation().stop();
            this.delay = c.leader == me ? 0 : 40 + (me.getId() % 6) * 10;     // the leader a good way in before the first follows
            me.triggerAnim(ACTION_CONTROLLER, "hesitate");
        }

        @Override
        public void stop() {
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            if (me.crossing != null && me.crossing.leader != me) {
                me.crossing = null;
            }
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            Pachyrhinosaurine me = Pachyrhinosaurine.this;
            Crossing c = me.crossing;
            boolean leader = c.leader == me;
            if (leader && c.wait > 0) {
                c.wait--;
                c.waited++;
                me.getNavigation().stop();
                me.getLookControl().setLookAt(c.far.x, c.far.y, c.far.z);
                if (c.wait == 0) {
                    me.log("river crossing: the leader wades in first, after " + c.waited / 20 + " s on the bank");
                }
                return;
            }
            if (!leader && !c.leaderIn) {
                // on the bank, behind the leader, waiting (one already in at the edge steps back out first)
                me.getLookControl().setLookAt(c.far.x, c.far.y, c.far.z);
                if (me.isInWater()) {
                    Vec3 back = c.bank.subtract(c.far.subtract(c.bank).normalize().scale(4.0D));
                    if (me.getNavigation().isDone() || me.tickCount % 20 == 0) {
                        me.getNavigation().moveTo(back.x, back.y, back.z, 1.0D);
                    }
                } else {
                    me.getNavigation().stop();
                }
                return;
            }
            if (!leader && this.delay > 0) {
                this.delay--;
                return;
            }
            if (leader && !c.leaderIn && me.isInWater()) {
                c.leaderIn = true;
                c.leaderInAt = me.level().getGameTime();
            }
            if (!leader && me.isInWater() && c.firstFollowerIn < 0) {
                c.firstFollowerIn = me.getId();
            }
            Vec3 side = new Vec3(c.far.z - c.bank.z, 0.0D, c.bank.x - c.far.x);
            side = side.lengthSqr() < 1.0E-4D ? Vec3.ZERO : side.normalize().scale(((me.getId() % 5) - 2) * 1.5D);
            Vec3 at = leader ? c.far : c.far.add(side);
            if (me.goTo(at, 1.0D, 3.0D) || me.position().distanceTo(at) < 4.0D) {
                if (c.crossed.contains(me.getId())) {
                    return;
                }
                c.crossed.add(me.getId());
                long n = c.crossed.size();
                me.log("river crossing: across (" + n + (leader ? ", the leader)" : ")"));
                if (leader) {
                    // the leader waits on the far bank for the others, up to 30 s
                    me.getNavigation().stop();
                }
            }
        }
    }

    private void crossStep() {
        Crossing c = this.crossing;
        if (c == null || c.leader != this) {
            return;
        }
        if (c.done) {
            this.crossing = null;
            return;
        }
        // the crossing ends when every grown one of the herd near is over, or after 90 s
        List<Pachyrhinosaurine> herd = this.kind(HERD + 16.0D).stream().filter(e -> !e.isBaby()).toList();
        boolean all = c.crossed.contains(this.getId()) && herd.stream().allMatch(e -> c.crossed.contains(e.getId()));
        if (all || this.level().getGameTime() - Math.max(0, c.leaderInAt) > 1800 && c.leaderInAt >= 0) {
            c.done = true;
            logLine("river crossing over: " + c.crossed.size() + " of " + (herd.size() + 1) + " grown ones across, the leader #"
                    + this.getId() + " first");
        }
    }

    // ================================================================== the cold, the calves, the gestures

    private boolean onSnow() {
        BlockPos at = this.blockPosition();
        return this.level().getBlockState(at).is(Blocks.SNOW) || this.level().getBlockState(at.below()).is(BlockTags.SNOW);
    }

    private void gestureStep() {
        if (this.gestureCooldown > 0) {
            this.gestureCooldown--;
            return;
        }
        if (this.isBaby() || this.busy() || this.isSleeping() || this.boutWith != null || (this.crossing != null && !this.crossing.done)) {
            return;
        }
        // on snow it stops where it is to dig (checked once a second, walking or not: grazing is what it does there)
        if (this.onSnow() && this.tickCount % 20 == this.getId() % 20 && this.random.nextInt(this.isHungry() ? 2 : 10) == 0) {
            this.getNavigation().stop();
            this.triggerAnim(ACTION_CONTROLLER, "snow_dig");
            BlockPos at = this.blockPosition();
            int cleared = 0;
            for (BlockPos p : BlockPos.betweenClosed(at.offset(-1, -1, -1), at.offset(1, 0, 1))) {
                BlockState s = this.level().getBlockState(p);
                if (s.is(Blocks.SNOW)) {
                    this.level().destroyBlock(p, false, this);
                    cleared++;
                }
            }
            this.feed(6);
            this.still = 64;
            this.gestureCooldown = FAST ? 100 : 400;
            this.log("digs the snow off to graze (" + cleared + " snow layers cleared)");
            return;
        }
        if (!this.getNavigation().isDone()) {
            return;
        }
        if (this.random.nextInt(900) == 0) {
            BlockPos rub = this.rubSpot();
            if (rub != null) {
                this.getLookControl().setLookAt(rub.getX() + 0.5D, rub.getY() + 0.5D, rub.getZ() + 0.5D);
                this.triggerAnim(ACTION_CONTROLLER, "boss_rub");
                this.still = 60;
                this.gestureCooldown = 600;
                this.log("rubs its boss on " + this.level().getBlockState(rub).getBlock().getName().getString());
                return;
            }
        }
        if (this.random.nextInt(1200) == 0 && !this.kind(24.0D).isEmpty()) {
            this.triggerAnim(ACTION_CONTROLLER, "call");
            this.playAmbientSound();
            this.gestureCooldown = 400;
        }
    }

    private BlockPos rubSpot() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        for (int k = 1; k <= 3; k++) {
            BlockPos p = BlockPos.containing(this.getX() + look.x * (this.getBbWidth() * 0.5D + k), this.getY() + 0.5D,
                    this.getZ() + look.z * (this.getBbWidth() * 0.5D + k));
            BlockState s = this.level().getBlockState(p);
            if (s.is(BlockTags.LOGS) || s.is(BlockTags.BASE_STONE_OVERWORLD) || s.is(Blocks.COBBLESTONE) || s.is(Blocks.MOSSY_COBBLESTONE)) {
                return p;
            }
        }
        return null;
    }

    /** Whoever comes close to the calves gets the boss: a toss of the head, then the charge. */
    private void calfGuardStep() {
        if (this.threatCooldown > 0) {
            this.threatCooldown--;
            return;
        }
        if (this.isBaby() || this.isTame() || this.busy() || this.isSleeping() || this.tickCount % 20 != this.getId() % 20) {
            return;
        }
        for (Pachyrhinosaurine calf : this.level().getEntitiesOfClass(Pachyrhinosaurine.class, this.getBoundingBox().inflate(12.0D),
                e -> e.isBaby() && e.isAlive() && !e.isTame())) {
            for (LivingEntity near : this.level().getEntitiesOfClass(LivingEntity.class, calf.getBoundingBox().inflate(4.0D),
                    e -> e.isAlive() && (e instanceof Player p && !p.isCreative() && !p.isSpectator()
                            || e instanceof PredatorDinosaur q && !q.isTame() && q.getBbWidth() < BIG))) {
                this.getLookControl().setLookAt(near, 30.0F, 30.0F);
                this.triggerAnim(ACTION_CONTROLLER, "head_toss");
                this.setTarget(near);
                this.threatCooldown = 200;
                this.log("guards the calf #" + calf.getId() + ": goes for the " + near.getType().toShortString());
                return;
            }
        }
    }

    // ------------------------------------------------------------------ the step
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.isTame()) {
            if (this.inRing()) {
                this.leaveRing();
            }
            return;
        }
        this.ringStep();
        if (this.inRing()) {
            return;
        }
        this.setBraced(false);
        this.crossStep();
        if (this.isBaby()) {
            return;
        }
        this.calfGuardStep();
        this.boutStep();
        if (this.boutWith != null) {
            return;
        }
        if (this.walkOff > 0) {
            this.walkOff--;
            // the herd's goals would pull it straight back to the winner: its own walk wins until it is done
            if (this.walkOffTo != null && (this.getNavigation().isDone() || this.walkOff % 20 == 0)
                    && this.walkOffTo.distanceToSqr(this.position()) > 4.0D) {
                this.getNavigation().moveTo(this.walkOffTo.x, this.walkOffTo.y, this.walkOffTo.z, 1.2D);
            }
            return;
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        this.gestureStep();
        if (this.getNavigation().isDone() && !this.busy() && this.random.nextInt(900) == 0 && this.isInWater()) {
            this.triggerAnim(ACTION_CONTROLLER, "drink");
            this.still = 70;
        }
    }

    /** Ridden, it crosses a river without fear (no hesitation for a rider). */
    @Override
    public boolean isPushedByFluid() {
        return !this.isVehicle() && super.isPushedByFluid();
    }

    // ------------------------------------------------------------------ test hooks (BehaviorTest "pachy")
    public void testBoutReady() {
        this.boutCooldown = 0;
    }

    public void testNoBout() {
        this.boutCooldown = 1_000_000;
    }

    public void testQuiet() {
        this.gestureCooldown = 1_000_000;
        this.threatCooldown = 1_000_000;
    }

    /** Whether a sound of the boss bout or the ring should be heard (kept for the voice later). */
    void thud() {
        this.level().playSound(null, this.getX(), this.getY(), this.getZ(), net.minecraft.sounds.SoundEvents.RAVAGER_ATTACK,
                SoundSource.NEUTRAL, 1.0F, 0.6F);
    }
}
