package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The epic duel (06/11/2026, second rewrite; docs/estudos/11_LUTA_EPICA.md). Played, the first duels were "too static,
 * monotonous" (Rodrigo). After studying how the Raxiores mod makes its fights feel big, the duel is a game of reading
 * the other, built our own way:
 * <ul>
 *   <li><b>Guard</b>: side-on to the rival (the theropods; the horned and dome-headed face-on, the Ankylosaurus shows its
 *   flank), the head on it, it walks round it on headings drawn by distance (far: zig-zags in; close: backs off or slips
 *   aside; between: circles), never standing still;</li>
 *   <li><b>Patience</b>: runs out faster the longer nothing happens, and it strikes when it is gone, or at once when the
 *   rival has just struck and is open (the punish);</li>
 *   <li><b>Committed blows</b>: the jab (quick, light), the signature blow, and the <b>lunge</b>: the body turns from the
 *   guard to the front in the wind-up and is thrown 4 to 9 blocks across the ring with its heading locked; it lands for
 *   a lot, and a miss leaves it open. A hit during its own wind-up cancels it;</li>
 *   <li><b>Reading the rhythm</b>: it remembers when the rival's blows came; the steadier the rhythm, the surer it parries;
 *   it also blocks (a guard that wears down and breaks) and sidesteps;</li>
 *   <li><b>Parry</b>: the incoming blow is knocked aside and answered; the one parried <b>staggers</b>, spun aside,
 *   slow and open for a moment. A parry on a feint catches nothing and leaves the parrier open;</li>
 *   <li><b>Impact</b>: every blow that lands jolts the camera of the players near by its weight and throws up the
 *   ground's dust (DinosaurEntity.impact).</li>
 * </ul>
 * The grapple chest to chest and the horn lock are DinosaurEntity's; they start out of the guard. Giving in is still
 * DinosaurEntity.duelAfter.
 */
public class DuelGoal extends Goal {
    private enum State { GUARD, STRIKE, PARRY, BLOCKED, STAGGER }
    private enum Kind { JAB, SPECIAL, LUNGE, COUNTER, FEINT }

    private final DinosaurEntity mob;
    private DuelStyle style;
    private LivingEntity rival;
    private State state = State.GUARD;
    private int stateTick;
    private Kind kind;
    private int hitTick;
    private int totalTicks;
    private boolean landed;
    /** Guard: the heading it walks on (degrees from the line to the rival) and ticks until a new one; the side it keeps. */
    private float heading;
    private int headingLeft;
    private float side = 1.0F;
    private int band = -1;
    private int patience;
    private int drain;
    private int quietTicks;
    /** Reading the rival: when its last blows were wound up, the beat between them, how sure it is of the beat. */
    private final int[] seen = new int[4];
    private int seenCount;
    private int confidence;
    /** The rival is open (its blow just spent) until this tick. */
    private int punishUntil;
    private int punishFrom;
    /** A parry planned for this tick; a block held until this tick; the parry caught something. */
    private int parryAt = -1;
    private int blockUntil;
    private boolean parried;
    private float guard;
    private int brokenLeft;
    private float spin;
    private int now;
    /** Ticks left of the straight run in, the patience spent and the rival out of reach. */
    private int closing;
    /** For the tests (BehaviorTest): lunges, blows landed, misses, parries made, blocks made, staggers taken, sidesteps,
     *  jabs, signature blows, feints. */
    public final int[] stats = new int[10];

    public DuelGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    // ------------------------------------------------------------------ when

    private double enter() {
        return 14.0D + this.mob.getBbWidth() * 1.5D;
    }

    @Override
    public boolean canUse() {
        LivingEntity t = this.mob.getTarget();
        return t != null && t.isAlive() && !this.mob.isVehicle() && !this.mob.isKnockedOut() && this.mob.duels(t)
                && this.mob.distanceTo(t) < this.enter();
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity t = this.mob.getTarget();
        return t != null && t == this.rival && t.isAlive() && !this.mob.isVehicle() && !this.mob.isKnockedOut()
                && this.mob.duels(t) && this.mob.distanceTo(t) < this.enter() * 1.6D;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    public boolean isActive() {
        return this.rival != null;
    }

    @Override
    public void start() {
        this.rival = this.mob.getTarget();
        this.style = DuelStyle.of(this.mob.speciesId());
        this.mob.setDueling(true);
        this.mob.getNavigation().stop();
        this.state = State.GUARD;
        this.stateTick = 0;
        this.side = this.mob.getRandom().nextBoolean() ? 1.0F : -1.0F;
        this.headingLeft = 0;
        this.band = -1;
        this.patience = this.freshPatience();
        this.drain = 0;
        this.closing = 0;
        this.seenCount = 0;
        this.confidence = 0;
        this.guard = this.mob.getMaxHealth() * 0.5F;
        this.brokenLeft = 0;
        this.parryAt = -1;
        // the opening: the big theropods roar (or show the sail), the others show their weapon
        String opener = null;
        if (this.mob instanceof com.terrassic.entity.ApexTheropod apex) {
            opener = apex.hasRoaredAt(this.rival) ? null : apex.duelOpener();
        } else {
            for (String o : new String[]{"crown_display", "claw_display", "paw_scrape", "threat", "display", "stamp"}) {
                if (this.mob.hasAnim(o)) {
                    opener = o;
                    break;
                }
            }
        }
        if (opener != null) {
            this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, opener);
            this.patience += 30;
        }
    }

    @Override
    public void stop() {
        this.rival = null;
        this.mob.setDueling(false);
        this.mob.getNavigation().stop();
        this.mob.getMoveControl().strafe(0.0F, 0.0F);
    }

    private int freshPatience() {
        return Math.round(this.style.patience() * (0.8F + this.mob.getRandom().nextFloat() * 0.6F));
    }

    // ------------------------------------------------------------------ the tick

    @Override
    public void tick() {
        LivingEntity t = this.rival;
        if (t == null) {
            return;
        }
        this.now++;
        this.mob.getLookControl().setLookAt(t, 40.0F, 40.0F);
        if (this.brokenLeft > 0) {
            this.brokenLeft--;
        } else {
            this.guard = Math.min(this.mob.getMaxHealth() * 0.5F, this.guard + this.mob.getMaxHealth() * 0.002F);
        }
        if (this.mob.isLocked()) {
            return;                             // the horn lock moves them (DinosaurEntity.lockTick)
        }
        if (this.mob.clinchLeft > 0 && this.state == State.GUARD && this.mob.clinchTick()) {
            return;
        }
        this.plannedParry();
        if (this.state == State.GUARD && this.mob.dodgeTick(t)) {
            return;                             // a sidestep under way
        }
        this.stateTick++;
        switch (this.state) {
            case STRIKE -> this.strikeTick(t);
            case PARRY -> this.parryTick(t);
            case BLOCKED -> this.blockedTick(t);
            case STAGGER -> this.staggerTick(t);
            default -> this.guardTick(t);
        }
    }

    // ------------------------------------------------------------------ guard

    private double gap(LivingEntity t) {
        return this.mob.distanceTo(t) - (this.mob.getBbWidth() + t.getBbWidth()) * 0.5D;
    }

    private double reach() {
        return this.style.reach() * Math.max(0.5F, this.mob.getScale());
    }

    private float yawTo(LivingEntity t) {
        return (float) (Mth.atan2(t.getZ() - this.mob.getZ(), t.getX() - this.mob.getX()) * Mth.RAD_TO_DEG) - 90.0F;
    }

    private void face(float yaw, float max) {
        float y = Mth.approachDegrees(this.mob.getYRot(), yaw, max);
        this.mob.setYRot(y);
        this.mob.setYBodyRot(y);
    }

    /** Walk the world direction {@code yaw}, whatever way the body faces, at {@code speed} times its walking pace
     *  (negative: backwards). Driven on the velocity: the vanilla strafe caps the pace at a quarter of the walk, and the
     *  duel was a slow shuffle (06/11). */
    private void walk(float yaw, float speed) {
        this.mob.getNavigation().stop();
        this.mob.getMoveControl().strafe(0.0F, 0.0F);
        this.mob.setZza(0.0F);
        this.mob.setXxa(0.0F);
        if (!this.mob.onGround() && !this.mob.isInWater()) {
            return;
        }
        double r = Math.toRadians(yaw);
        double pace = this.mob.getAttributeValue(Attributes.MOVEMENT_SPEED) * 1.15D * speed;
        Vec3 want = new Vec3(-Math.sin(r) * pace, 0.0D, Math.cos(r) * pace);
        Vec3 v = this.mob.getDeltaMovement();
        double k = 0.35D;
        this.mob.setDeltaMovement(v.x + (want.x - v.x) * k, v.y, v.z + (want.z - v.z) * k);
        if (this.mob.horizontalCollision && this.mob.onGround()) {
            this.mob.getJumpControl().jump();       // a step up in the ring
        }
    }

    private void guardTick(LivingEntity t) {
        double gap = this.gap(t);
        float to = this.yawTo(t);
        this.face(to + this.side * this.style.profile(), 9.0F);
        // the heading by distance: far, zig-zag in; close, back off or slip aside; between, circle
        int b = gap > this.reach() + this.style.lunge() * 0.9D ? 0 : gap < this.reach() * 0.5D ? 2 : 1;
        if (this.closing > 0) {
            // the run in: straight at it, face-on, until it is in reach of a blow
            this.closing--;
            this.face(to, 10.0F);
            this.walk(to, 1.4F);
            if (gap <= this.reach() + 0.4D || (gap <= this.reach() + this.style.lunge() && this.lungeAnim() != null)) {
                this.closing = 0;
                this.patience = 0;
            } else {
                return;
            }
        } else if (b != this.band || --this.headingLeft <= 0) {
            this.band = b;
            this.headingLeft = 25 + this.mob.getRandom().nextInt(50);
            float r = this.mob.getRandom().nextFloat();
            this.heading = switch (b) {
                case 0 -> (r - 0.5F) * 90.0F;
                case 2 -> 90.0F + r * 180.0F;
                default -> this.side * (60.0F + r * 60.0F) * (this.mob.getRandom().nextInt(5) == 0 ? -1.0F : 1.0F);
            };
            if (b == 1 && this.mob.getRandom().nextInt(3) == 0) {
                this.side = -this.side;     // it changes the side it shows, swinging round
            }
        }
        if (this.closing == 0) {
            float pace = this.style.circle() * (0.85F + 0.4F * Mth.sin(this.now * 0.19F + this.mob.getId()));
            this.walk(to + this.heading, b == 0 ? pace * 1.3F : pace);
        }

        // the rival comes too close: the grapple (theropods, rivals of a kind) or the horn lock
        if (t instanceof DinosaurEntity d && gap < 1.2D && this.brokenLeft == 0) {
            if (this.mob.locksHorns(d) && this.style.profile() == 0.0F && this.mob.getRandom().nextInt(12) == 0) {
                this.mob.lockHorns(d);
                return;
            }
            if (d.getType() == this.mob.getType() && d.clinchLeft == 0 && this.mob.clinchLeft == 0 && !this.mob.locksHorns(d)
                    && this.mob.getRandom().nextInt(16) == 0) {
                this.mob.startClinch(d, 40 + this.mob.getRandom().nextInt(40));
                return;
            }
        }

        // patience: drains faster the longer nothing happens
        this.quietTicks++;
        if (this.quietTicks % 60 == 0) {
            this.drain++;
        }
        this.patience -= 1 + this.drain;
        boolean punish = this.now >= this.punishFrom && this.now <= this.punishUntil;
        // braced for the rival's blow (a block or a parry planned): it holds its own until that is over
        if (this.now <= this.blockUntil || this.parryAt >= 0) {
            return;
        }
        if (this.patience > 0 && !punish) {
            return;
        }
        if (gap <= this.reach() + 0.5D) {
            float r = this.mob.getRandom().nextFloat();
            if (r < 0.15F && this.mob.hasAnim("feint")) {
                this.begin(Kind.FEINT, t);
            } else if (r < 0.40F && this.style.special() != null) {
                this.begin(Kind.SPECIAL, t);
            } else if (r < 0.62F && this.lungeAnim() != null) {
                this.begin(Kind.LUNGE, t);
            } else {
                this.begin(Kind.JAB, t);
            }
        } else if (gap <= this.reach() + this.style.lunge() * Math.max(0.6F, this.mob.getScale()) && this.lungeAnim() != null) {
            this.begin(Kind.LUNGE, t);
        } else {
            // out of range: it closes in on a straight run, the patience spent
            this.closing = 50;
        }
    }

    // ------------------------------------------------------------------ the blows

    private void begin(Kind k, LivingEntity t) {
        this.state = State.STRIKE;
        this.stateTick = 0;
        this.kind = k;
        this.landed = false;
        this.quietTicks = 0;
        this.drain = 0;
        this.patience = this.freshPatience();
        String anim;
        switch (k) {
            case LUNGE -> {
                anim = this.lungeAnim();
                this.hitTick = DuelStyle.LUNGE_HIT;
                this.totalTicks = DuelStyle.LUNGE_TOTAL;
            }
            case SPECIAL -> {
                anim = this.style.special();
                this.hitTick = this.style.specialHit();
                this.totalTicks = this.style.specialTotal();
            }
            case FEINT -> {
                anim = "feint";
                this.hitTick = 8;
                this.totalTicks = 18;
            }
            default -> {
                anim = this.style.jab();
                this.hitTick = this.style.jabHit();
                this.totalTicks = this.style.jabTotal();
            }
        }
        this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, anim);
        this.mob.getNavigation().stop();
        this.stats[switch (k) { case LUNGE -> 0; case SPECIAL -> 8; case FEINT -> 9; default -> 7; }]++;
        if (t instanceof DinosaurEntity d && d.duelBrain() != null) {
            d.duelBrain().incoming(this.mob, this.hitTick, k == Kind.FEINT);
        }
    }

    /** The duel's lunge (the Giganotosaurus' is "duel_lunge": its "lunge" is the low cut at a big prey's leg). */
    private String lungeAnim() {
        return this.mob.hasAnim("duel_lunge") ? "duel_lunge" : this.mob.hasAnim("lunge") ? "lunge" : null;
    }

    private void strikeTick(LivingEntity t) {
        float to = this.yawTo(t);
        int i = this.stateTick;
        boolean lunge = this.kind == Kind.LUNGE;
        if (i < this.hitTick - 3) {
            // the wind-up: from the guard round to the front, the weight drawn back
            this.face(to, lunge ? 14.0F : 10.0F);
            this.walk(to, lunge ? -0.3F : 0.0F);
        } else if (i <= this.hitTick + (lunge ? 7 : 1)) {
            // the throw: the heading locked, the body carried across the ring
            this.mob.getNavigation().stop();
            this.mob.getMoveControl().strafe(0.0F, 0.0F);
            double dist = lunge ? this.style.lunge() * Math.min(1.3D, 0.6D + 0.4D * this.mob.getScale())
                    : this.kind == Kind.SPECIAL ? 2.0D : 0.8D;
            int ticks = lunge ? 11 : 5;
            if (this.gap(t) > 0.2D || this.style.around()) {
                double r = Math.toRadians(this.mob.getYRot());
                Vec3 v = new Vec3(-Math.sin(r), 0.0D, Math.cos(r)).scale(dist / ticks);
                this.mob.setDeltaMovement(v.x, this.mob.getDeltaMovement().y, v.z);
                this.mob.hasImpulse = true;
            }
        } else {
            // the follow-through and the settle, the head back on the rival
            this.face(to + this.side * this.style.profile() * Math.min(1.0F, (i - this.hitTick) / 20.0F), 6.0F);
            this.walk(to, lunge ? 0.0F : -0.35F);
        }
        if (i == this.hitTick && this.kind != Kind.FEINT) {
            this.resolve(t);
        }
        if (i >= this.totalTicks) {
            this.toGuard();
        }
    }

    /** Whether the weapon is on the rival now: in reach past the front of the box, and in front (or round, the club). */
    private boolean inReach(LivingEntity t, double extra) {
        if (this.gap(t) > this.reach() + extra) {
            return false;
        }
        if (this.style.around()) {
            return true;
        }
        float off = Math.abs(Mth.wrapDegrees(this.yawTo(t) - this.mob.getYRot()));
        return off < 55.0F;
    }

    private double damageOf(Kind k) {
        double atk = this.mob.getAttributeValue(Attributes.ATTACK_DAMAGE);
        return atk * switch (k) {
            case LUNGE -> 1.3D;
            case SPECIAL -> 1.1D;
            case COUNTER -> 0.9D;
            default -> 0.55D;
        };
    }

    private void resolve(LivingEntity t) {
        if (!this.inReach(t, this.kind == Kind.LUNGE ? 1.0D : 0.4D)) {
            // a miss: the lunge that found nothing leaves it open (its rival punishes)
            this.stats[2]++;
            if (t instanceof DinosaurEntity d && d.duelBrain() != null) {
                d.duelBrain().punishFrom = d.duelBrain().now;
                d.duelBrain().punishUntil = d.duelBrain().now + 14;
            }
            return;
        }
        this.landed = true;
        this.stats[1]++;
        float dmg = (float) this.damageOf(this.kind);
        if (t instanceof DinosaurEntity d && d.duelBrain() != null && d.duelBrain().isActive()) {
            d.duelBrain().receive(this.mob, this.kind, dmg);
        } else {
            this.hurt(t, dmg, this.kind);
        }
    }

    private void hurt(LivingEntity t, float dmg, Kind k) {
        t.hurt(this.mob.damageSources().mobAttack(this.mob), dmg);
        this.mob.setLastHurtMob(t);
        double push = switch (k) {
            case LUNGE -> 0.55D;
            case SPECIAL -> 0.7D;
            case COUNTER -> 0.9D;
            default -> 0.22D;
        };
        if (t instanceof DinosaurEntity d) {
            d.pushedBy(this.mob, push);
        } else {
            t.knockback(push * 1.5D, this.mob.getX() - t.getX(), this.mob.getZ() - t.getZ());
        }
        float weight = (float) Math.min(1.4D, (k == Kind.JAB ? 0.25D : 0.6D) * Math.max(0.5D, this.mob.getBbWidth() / 2.5D));
        this.mob.impact(t.getX(), t.getY(), t.getZ(), weight, k != Kind.JAB);
    }

    // ------------------------------------------------------------------ the other side: incoming, received

    /** The rival winds up a blow landing in {@code hitIn} ticks (a feint lands nothing): read it, plan the answer. */
    void incoming(DinosaurEntity attacker, int hitIn, boolean feint) {
        if (!this.isActive()) {
            return;
        }
        // the rhythm: the beat between its blows, and how well this one kept it
        if (this.seenCount > 0) {
            int last = this.seen[(this.seenCount - 1) % 4];
            int predicted = last + this.beat();
            this.confidence = Math.abs(this.now - predicted) <= 6 ? Math.min(50, this.confidence + 12) : Math.max(0, this.confidence - 6);
        }
        this.seen[this.seenCount % 4] = this.now;
        this.seenCount++;
        // its blow spent, it is open for a moment: the punish (not during the wind-up, which only trades blows)
        this.punishFrom = this.now + hitIn + 4;
        this.punishUntil = this.now + hitIn + 4 + 10;
        if (this.state != State.GUARD || this.brokenLeft > 0) {
            return;
        }
        float off = Math.abs(Mth.wrapDegrees(this.yawTo(attacker) - this.mob.getYRot()));
        if (off > this.style.profile() + 55.0F && !this.style.around()) {
            return;                             // caught from the side or behind: no answer
        }
        float r = this.mob.getRandom().nextFloat();
        float parry = this.style.parry() + this.confidence / 50.0F * 0.45F;
        if (this.mob.hasAnim("parry") && r < parry) {
            this.parryAt = this.now + Math.max(0, hitIn - 3);
            return;
        }
        if (r < parry + this.style.block() && this.guard > 0.0F) {
            this.blockUntil = this.now + hitIn + 3;
            return;
        }
        if (r < parry + this.style.block() + this.style.dodge()) {
            this.mob.dodgeSide = this.mob.getRandom().nextBoolean() ? 1.0F : -1.0F;
            this.mob.incomingDodge(Math.max(4, hitIn));
            this.stats[6]++;
        }
    }

    private int beat() {
        int n = Math.min(4, this.seenCount);
        if (n < 2) {
            return 40;
        }
        int sum = 0, w = 0;
        for (int k = 1; k < n; k++) {
            int a = this.seen[(this.seenCount - k) % 4], b = this.seen[(this.seenCount - k - 1) % 4];
            int weight = 4 - k;
            sum += (a - b) * weight;
            w += weight;
        }
        return Math.max(8, sum / Math.max(1, w));
    }

    /** A blow arrives: parried, blocked, or taken. */
    void receive(DinosaurEntity attacker, Kind k, float dmg) {
        DuelGoal other = attacker.duelBrain();
        if (this.state == State.PARRY && this.stateTick <= 6 && k != Kind.COUNTER) {
            // knocked aside: the attacker reels round, the answer comes out of the turn
            this.parried = true;
            this.stats[3]++;
            if (other != null) {
                other.staggered(this.mob);
            }
            this.mob.impact(attacker.getX(), attacker.getY(), attacker.getZ(), 0.35F, false);
            return;
        }
        if (this.now <= this.blockUntil && this.state == State.GUARD && this.guard > 0.0F) {
            this.guard -= dmg;
            this.stats[4]++;
            this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "block");
            attacker.pushedBy(this.mob, 0.25D);
            this.mob.pushedBy(attacker, 0.2D);
            this.mob.impact(this.mob.getX(), this.mob.getY(), this.mob.getZ(), 0.3F, false);
            if (other != null) {
                other.blocked();
            }
            if (this.guard <= 0.0F) {
                // the guard breaks: it reels, and for a while it neither blocks nor parries
                this.brokenLeft = 100;
                this.staggered(attacker);
            } else {
                this.punishFrom = this.now;
                this.punishUntil = this.now + 10;
            }
            return;
        }
        if (other != null) {
            other.hurt(this.mob, dmg, k);
        }
        if (this.state == State.STRIKE && this.stateTick < this.hitTick) {
            // hit in its own wind-up: the blow is lost
            this.toGuard();
            this.patience += 20;
        }
        if (this.state == State.GUARD && this.mob.getRandom().nextFloat() < 0.5F && this.mob.hasAnim("recoil")) {
            this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "recoil");
        }

    }

    // ------------------------------------------------------------------ parry, blocked, stagger

    private void parryTick(LivingEntity t) {
        this.face(this.yawTo(t), 12.0F);
        this.walk(this.yawTo(t), 0.0F);
        if (this.stateTick == DuelStyle.PARRY_COUNTER && this.parried && this.inReach(t, 1.0D)) {
            float dmg = (float) this.damageOf(Kind.COUNTER);
            if (t instanceof DinosaurEntity d && d.duelBrain() != null && d.duelBrain().isActive()) {
                d.duelBrain().receive(this.mob, Kind.COUNTER, dmg);
            } else {
                this.hurt(t, dmg, Kind.COUNTER);
            }
        }
        if (this.stateTick >= DuelStyle.PARRY_TOTAL) {
            this.toGuard();
        }
    }

    void blocked() {
        this.state = State.BLOCKED;
        this.stateTick = 0;
        if (this.mob.hasAnim("recoil")) {
            this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "recoil");
        }
    }

    private void blockedTick(LivingEntity t) {
        this.face(this.yawTo(t), 6.0F);
        this.walk(this.yawTo(t), this.stateTick < 10 ? -0.8F : 0.0F);
        if (this.stateTick >= 16) {
            this.toGuard();
        }
    }

    /** Parried (or its guard broken): spun aside, slow and open. */
    void staggered(LivingEntity by) {
        this.state = State.STAGGER;
        this.stateTick = 0;
        this.stats[5]++;
        float away = Mth.wrapDegrees(this.yawTo(by) - this.mob.getYRot()) > 0.0F ? -1.0F : 1.0F;
        this.spin = away * (90.0F + this.mob.getRandom().nextFloat() * 60.0F);
        this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, this.mob.hasAnim("stagger") ? "stagger" : "recoil");
        this.mob.pushedBy(by, 0.3D);
        DuelGoal other = by instanceof DinosaurEntity d ? d.duelBrain() : null;
        if (other != null) {
            other.punishFrom = other.now;
            other.punishUntil = other.now + 30;
        }
    }

    private void staggerTick(LivingEntity t) {
        if (this.stateTick <= 16) {
            float y = this.mob.getYRot() + this.spin / 16.0F;
            this.mob.setYRot(y);
            this.mob.setYBodyRot(y);
        }
        this.mob.getNavigation().stop();
        this.mob.getMoveControl().strafe(-0.1F, 0.0F);
        if (this.stateTick >= DuelStyle.STAGGER_TOTAL) {
            this.toGuard();
        }
    }

    private void toGuard() {
        this.state = State.GUARD;
        this.stateTick = 0;
        this.parried = false;
        this.headingLeft = 0;
    }

    /** Each tick before the state machine: a planned parry starts (out of the guard only). */
    void plannedParry() {
        if (this.parryAt >= 0 && this.now >= this.parryAt) {
            this.parryAt = -1;
            if (this.state == State.GUARD) {
                this.state = State.PARRY;
                this.stateTick = 0;
                this.parried = false;
                this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "parry");
            }
        }
    }
}
