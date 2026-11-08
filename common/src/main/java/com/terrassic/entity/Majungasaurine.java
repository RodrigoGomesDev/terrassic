package com.terrassic.entity;

import com.terrassic.entity.ai.CarcassStealGoal;
import com.terrassic.entity.ai.WaterholeGuardGoal;
import java.util.UUID;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The Majungasaurus rig (tools/modelgen/handmade/majungasaurus, made for it from its own study,
 * docs/estudos/13_PREDADORES_1_10.md; the fourth and last of the 1.10.1 standard after the Daspletosaurus, the
 * Albertosaurus and the Carcharodontosaurus). The life of an {@link ApexTheropod}, told apart from its cousin the
 * Carnotaurus (which runs on long legs and rams with its horns) by what it does:
 * <ul>
 *   <li><b>It bites and holds</b> ({@link #BITE_HOLD}; Sampson &amp; Witmer 2007: a broad snout, a strong neck and a
 *       flexible jaw for a bite that holds). Prey up to {@link #HOLD_SIZE} times its own size is held in the jaws for 2 to
 *       3 s and shaken ("hold_shake"), taking a little damage every second; a small one is carried with the head. A
 *       player held is slowed and bitten lightly until they hit it {@link #ESCAPE_HITS} times (two hard blows do it)
 *       or {@link #HOLD_PLAYER} ticks pass; then it lets go with a toss ("hold_release") and does not take the same
 *       player again for 8 s: never a hold that lasts.</li>
 *   <li><b>The short burst</b>: a target that turns up close ({@link #BURST_RANGE} blocks) is charged at once, low and
 *       silent ("burst": 1.5 s much faster); if the burst misses it gives up at 24 blocks from where it started.</li>
 *   <li><b>The cannibal</b> (Rogers, Krause &amp; Curry Rogers 2003): it eats a dead Majungasaurus like any carcass
 *       (logged); very hungry, a badly wounded neighbour of its kind becomes prey ({@link #cannibalPrey}); two hungry
 *       ones at the same carcass fight a duel over it, the winner eats.</li>
 *   <li><b>The waterhole</b> ({@link WaterholeGuardGoal}; Rogers 2005, a hypothesis): in the afternoon it goes to the
 *       nearest water and crouches by it ("ambush_crouch"); whoever comes is warned off with the dome
 *       ("waterhole_threat") and attacked if it comes on; prey that comes to drink is charged.</li>
 *   <li><b>Short temper</b>: a player who comes within 8 blocks is warned with the dome ("dome_display"); one who keeps
 *       coming is attacked.</li>
 *   <li><b>The low duel</b> (ai/DuelStyle): face on, it blocks a lot, hardly dodges and hardly staggers (the low
 *       centre of gravity); its signature and its parry counter are the DOME SHOVE from below, never a running butt
 *       (the dome was hollow: more display than ram).</li>
 * </ul>
 * One log line per behaviour ("[majunga] ...", logger "terrassic") for the playtests. It has the duel and the lively
 * sets of the remade apex predators by its own class, so the shared lists in DinosaurEntity stay untouched.
 */
public abstract class Majungasaurine extends ApexTheropod {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    /** The cycles (majungaanims.py WALK, RUN, STALK, BURST): pixels of ground per cycle (stride x K = 0.44) and ticks. */
    private static final double WALK_PX = 31.68D;
    private static final double WALK_TICKS = 28.0D;
    private static final double RUN_PX = 52.8D;
    private static final double RUN_TICKS = 14.0D;
    private static final double STALK_PX = 22.18D;
    private static final double STALK_TICKS = 42.0D;
    private static final double BURST_PX = 58.08D;
    private static final double BURST_TICKS = 11.0D;
    /** The blows, timed to the jaws in majungaanims.py (tick the hit lands, ticks to the next). */
    public static final Strike BITE_HOLD = new Strike("bite_hold", 7, 24, false);
    private static final Strike SLAM = new Strike("attack", 10, 28, false);
    private static final Strike QUICK = new Strike("attack_quick", 6, 18, false);
    private static final Strike LOW = new Strike("bite_low", 8, 24, false);
    private static final Strike SIDE = new Strike("bite_side", 9, 26, false);
    private static final Strike DOME_SHOVE = new Strike("dome_shove", 9, 26, false);
    /** The hold: the biggest prey it holds (linear size against its own), its length on a player and on an animal,
     *  the hits that free a player, the bite it takes every second, and how long it leaves the one it let go. */
    public static final double HOLD_SIZE = 1.2D;
    private static final double CARRY_SIZE = 0.55D;
    public static final int HOLD_PLAYER = 60;
    private static final int HOLD_ANIMAL = 40;
    public static final int ESCAPE_HITS = 3;
    private static final float HOLD_BITE_PLAYER = 1.5F;
    private static final int HOLD_AGAIN_PLAYER = 160;
    private static final int HOLD_AGAIN_ANIMAL = 100;
    /** The burst: how close a new target must be, its ticks, how much faster, how far it chases if it misses. */
    public static final double BURST_RANGE = 14.0D;
    private static final int BURST_TICKS_LEFT = 30;
    private static final double BURST_BOOST = 0.6D;
    private static final double BURST_CHASE = 24.0D;
    private static final UUID BURST_ID = UUID.fromString("6a1f0e52-9b3d-4c7e-8a21-5d4c3b2a1f09");
    /** The warning: the dome shown to a player this close; it attacks one who then comes within WARN_ATTACK. */
    private static final double WARN_RANGE = 8.0D;
    private static final double WARN_ATTACK = 4.5D;
    private static final String[] GESTURES = {"sniff", "look_back", "shake", "yawn", "stretch", "snort", "snort",
            "settle", "settle", "scan", "scan"};
    private static final String[] GESTURES_MALE = {"sniff", "look_back", "shake", "yawn", "stretch", "snort", "snort",
            "settle", "settle", "scan", "scan", "dome_display"};
    private static final String[] GESTURES_FED = {"sniff", "look_back", "shake", "snort", "settle", "tooth_spit", "tooth_spit"};
    /** Crouched by the water the only gesture is a glance from the crouch (the standing ones would lift it). */
    private static final String[] GESTURES_CROUCH = {"ambush_look"};
    private static final String[] OWN = {"bite_hold", "hold_release", "dome_shove", "dome_display", "waterhole_threat",
            "carcass_guard", "tooth_spit", "ambush_look"};

    public static final byte MODE_NONE = 0;
    public static final byte MODE_CROUCH = 1;
    public static final byte MODE_BURST = 2;
    public static final byte MODE_HOLD = 3;
    private static final EntityDataAccessor<Byte> DATA_MODE = SynchedEntityData.defineId(Majungasaurine.class, EntityDataSerializers.BYTE);

    private RawAnimation crouchAnim;
    private RawAnimation burstAnim;
    private RawAnimation holdAnim;
    /** Server: the burst under way (ticks left), at what, from where, and whether a blow has landed since. */
    private int burstLeft;
    private int burstTarget = -1;
    private Vec3 burstFrom;
    private boolean burstHit;
    private UUID lostPrey;
    private int lostPreyUntil;
    /** Server: the hold under way (who, ticks left, ticks in, hits taken from them), and the one it let go. */
    private int heldId = -1;
    private int holdLeft;
    private int holdAge;
    private int escapeHits;
    private UUID letGo;
    private int letGoUntil;
    /** Server: the warning shown to a player (when, at whom), the waterhole act, the carcass fight, the last cannibal
     *  meal logged. */
    private int warnCooldown = 100;
    private UUID warned;
    private int warnedUntil;
    public int waterholeCooldown = 600;
    public int threatCooldown;
    private int carcassFightCooldown = 200;
    private int cannibalLogged = -1;

    protected Majungasaurine(EntityType<? extends Majungasaurine> type, Level level) {
        super(type, level);
    }

    /** Logs one behaviour line: "[majunga] what (#id x y z)". */
    public void logAct(String what) {
        LOG.info("[majunga] {} (#{} {} {} {})", what, this.getId(), this.getBlockX(), this.getBlockY(), this.getBlockZ());
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_MODE, MODE_NONE);
    }

    public byte mode() {
        return this.entityData.get(DATA_MODE);
    }

    public void setMode(byte mode) {
        if (this.mode() != mode) {
            this.entityData.set(DATA_MODE, mode);
        }
    }

    // ------------------------------------------------------------------ the sets it has (its own class: no shared list)

    @Override
    public boolean hasDuelMoves() {
        return true;
    }

    @Override
    public boolean hasLivelySet() {
        return true;
    }

    @Override
    protected String[] extraActions() {
        String[] common = super.extraActions();
        String[] all = java.util.Arrays.copyOf(common, common.length + OWN.length);
        System.arraycopy(OWN, 0, all, common.length, OWN.length);
        return all;
    }

    @Override
    protected String[] gestures() {
        if (this.mode() == MODE_CROUCH) {
            return GESTURES_CROUCH;
        }
        if (this.isSated() && this.getRandom().nextInt(3) == 0) {
            return GESTURES_FED;          // fed: now and then a shed tooth spat out (D'Emic et al. 2019)
        }
        return this.isFemale() ? GESTURES : GESTURES_MALE;
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
    protected double stalkCycleSpeed() {
        return STALK_PX / 16.0D / STALK_TICKS * this.modelScale();
    }

    /** Its bite tip against the T. rex's the distances were measured on: a short broad head on a short neck. */
    @Override
    public double reachScale() {
        return 0.62D;
    }

    /** A badly wounded one does not stand a duel: it is prey (see {@link #cannibalPrey}). */
    @Override
    public boolean fightsInDuel() {
        return super.fightsInDuel() && this.getHealth() >= this.getMaxHealth() * 0.25F;
    }

    // ------------------------------------------------------------------ blows and the hold

    /** It holds what it can (most of all), else the slam, the quick bite, the low sweep for small things, the arc. */
    @Override
    public Strike biteFor(LivingEntity target) {
        float r = this.getRandom().nextFloat();
        if (this.canHold(target) && r < 0.65F) {
            return BITE_HOLD;
        }
        if (target.getBbHeight() < 1.2F && r < 0.8F) {
            return LOW;
        }
        return r < 0.8F ? SLAM : r < 0.9F ? QUICK : SIDE;
    }

    /** It holds even small things (only the tiniest are stamped on). */
    @Override
    public boolean strikesAtFeet(LivingEntity target) {
        return target.getBbHeight() < 0.5F && target.getBbWidth() < 0.5F;
    }

    /** Whether it may take this one in a hold now: not in a duel, nothing held, not the one it just let go, and no
     *  bigger than {@link #HOLD_SIZE} times itself. */
    public boolean canHold(LivingEntity target) {
        if (target == null || !target.isAlive() || this.isDueling() || this.heldId >= 0 || this.isVehicle()
                || (target.getUUID().equals(this.letGo) && this.tickCount < this.letGoUntil)) {
            return false;
        }
        if (target instanceof Player p) {
            return !p.isCreative() && !p.isSpectator();
        }
        return Tyrannosaurine.linearSize(target) <= HOLD_SIZE * Tyrannosaurine.linearSize(this);
    }

    public boolean isHolding() {
        return this.heldId >= 0;
    }

    /** A blow landed (ApexBiteGoal): the bite that holds takes hold. */
    @Override
    public void struck(LivingEntity target, Strike strike) {
        super.struck(target, strike);
        this.burstHit = true;
        if (strike == BITE_HOLD && this.canHold(target)) {
            this.startHold(target);
        }
    }

    /** While it holds, the fight goal stands with it (the hold's length, the shake on the movement loop); after the
     *  slam it steps back a moment. */
    @Override
    public Pause pauseAfter(Strike strike) {
        Pause alpha = super.pauseAfter(strike);
        if (alpha != null) {
            return alpha;
        }
        if (strike == BITE_HOLD && this.isHolding()) {
            return new Pause(0, "hold_shake", Math.max(0, this.holdLeft - (strike.total() - strike.hit())), 0);
        }
        return strike == SLAM ? new Pause(4, null, 0, 0) : null;
    }

    private void startHold(LivingEntity target) {
        this.heldId = target.getId();
        this.holdLeft = target instanceof Player ? HOLD_PLAYER : HOLD_ANIMAL + this.getRandom().nextInt(21);
        this.holdAge = 0;
        this.escapeHits = 0;
        this.endBurst();
        this.setMode(MODE_HOLD);
        boolean carry = !(target instanceof Player) && Tyrannosaurine.linearSize(target) <= CARRY_SIZE * Tyrannosaurine.linearSize(this);
        this.logAct(String.format("hold: bites and holds the %s (%s, %.1f s)", target.getType().toShortString(),
                target instanceof Player ? "a player: slowed, escapes by hitting it" : carry ? "carried in the jaws" : "too big to carry, pinned",
                this.holdLeft / 20.0F));
    }

    /** Lets go: the jaws open with a toss of the head; the one let go is left alone for a while. */
    private void release(String why) {
        Entity e = this.level().getEntity(this.heldId);
        this.heldId = -1;
        this.holdLeft = 0;
        if (this.mode() == MODE_HOLD) {
            this.setMode(MODE_NONE);
        }
        this.triggerAnim(ACTION_CONTROLLER, "hold_release");
        if (e instanceof LivingEntity t) {
            this.letGo = t.getUUID();
            this.letGoUntil = this.tickCount + (t instanceof Player ? HOLD_AGAIN_PLAYER : HOLD_AGAIN_ANIMAL);
            if (t.isAlive()) {
                t.knockback(0.5D, this.getX() - t.getX(), this.getZ() - t.getZ());
            }
            this.logAct(String.format("hold: lets the %s go after %.1f s (%s, health %d)", t.getType().toShortString(),
                    this.holdAge / 20.0F, why, Math.round(t.getHealth())));
        } else {
            this.logAct("hold: lets go (" + why + ")");
        }
    }

    /** The hold under way: the held one bitten every second, a player slowed, a small animal carried in the jaws and
     *  shaken, a big one pinned; it ends on time, when the held one is dead or gone, or when a player beats it off. */
    private void holdTick() {
        Entity e = this.level().getEntity(this.heldId);
        if (!(e instanceof LivingEntity t) || !t.isAlive() || t.isRemoved()) {
            this.release(e == null ? "it is gone" : "it is dead");
            return;
        }
        double reach = this.getBbWidth() * 0.5D + t.getBbWidth() * 0.5D + 4.0D * this.getScale();
        if (this.distanceToSqr(t) > reach * reach || this.isVehicle() || this.isKnockedOut() || this.isDueling()) {
            this.release("pulled free");
            return;
        }
        this.holdAge++;
        this.getNavigation().stop();
        this.getLookControl().setLookAt(t, 30.0F, 30.0F);
        if (this.holdAge % 20 == 10) {
            float bite = t instanceof Player ? HOLD_BITE_PLAYER : (float) (this.getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.3D);
            t.hurt(this.damageSources().mobAttack(this), bite);
        }
        if (t instanceof Player p) {
            if (this.holdAge % 5 == 1) {
                p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 10, 3, false, false, true), this);
            }
        } else if (Tyrannosaurine.linearSize(t) <= CARRY_SIZE * Tyrannosaurine.linearSize(this)) {
            // carried in the jaws: held at the mouth, shaken side to side with the head (majungaanims.hold_shake)
            float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
            double fwd = this.getBbWidth() * 0.5D + 1.4D * this.getScale() + t.getBbWidth() * 0.4D;
            double shake = Math.sin(this.holdAge * Math.PI * 2.0D / 8.0D) * 0.35D * this.getScale();
            double x = this.getX() - Mth.sin(yaw) * fwd + Mth.cos(yaw) * shake;
            double z = this.getZ() + Mth.cos(yaw) * fwd + Mth.sin(yaw) * shake;
            double y = this.getY() + Math.max(0.0D, 1.3D * this.getScale() - t.getBbHeight() * 0.5D);
            t.moveTo(x, y, z, t.getYRot(), t.getXRot());
            t.setDeltaMovement(Vec3.ZERO);
            t.fallDistance = 0.0F;
            if (t instanceof Mob mob) {
                mob.getNavigation().stop();
            }
        } else {
            // too big to carry: pinned, slowed to a crawl while the jaws hang on
            if (this.holdAge % 5 == 1) {
                t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 10, 4, false, false, false), this);
            }
        }
        if (--this.holdLeft <= 0) {
            this.release("time");
        }
    }

    /** The held player beats it off: three blows, or two hard ones. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && this.isHolding() && source.getEntity() != null
                && source.getEntity().getId() == this.heldId) {
            this.escapeHits += amount >= 5.0F ? 2 : 1;
            if (this.escapeHits >= ESCAPE_HITS) {
                this.release("escape: hit " + this.escapeHits + " in " + this.holdAge + " ticks");
            }
        }
        return hurt;
    }

    // ------------------------------------------------------------------ the duel

    /** ai/DuelGoal: a duel move started (the dome shove, the parry that ends in one) is logged. */
    public static void duelMove(DinosaurEntity mob, String anim) {
        if (mob instanceof Majungasaurine m && ("dome_shove".equals(anim) || "parry".equals(anim))) {
            m.logAct("parry".equals(anim) ? "dome shove (parry counter)" : "dome shove");
        }
    }

    /** ai/DuelGoal: its lunge bites and holds a moment (the animation); logged. */
    public static void duelHit(DinosaurEntity mob, LivingEntity rival, boolean lunge) {
        if (lunge && mob instanceof Majungasaurine m) {
            m.logAct("duel: bites and holds the " + rival.getType().toShortString());
        }
    }

    /** ai/DuelGoal: staggered, it barely gives (the low centre of gravity): this share of the spin of the others. */
    public static float staggerGive(DinosaurEntity mob) {
        return mob instanceof Majungasaurine ? 0.45F : 1.0F;
    }

    /** Chest to chest with a rival: the dome from below. */
    @Override
    public Strike closeStrike() {
        return DOME_SHOVE;
    }

    /** It opens a duel with the head down, showing the dome. */
    @Override
    public String duelOpener() {
        return "dome_display";
    }

    // ------------------------------------------------------------------ the burst

    @Override
    protected void addExtraGoals() {
        super.addExtraGoals();
        this.goalSelector.addGoal(3, new WaterholeGuardGoal(this));
    }

    /** A prey it gave up after a missed burst is left alone for half a minute. */
    @Override
    public boolean canAttack(LivingEntity target) {
        if (!super.canAttack(target)) {
            return false;
        }
        return target == null || !target.getUUID().equals(this.lostPrey) || this.tickCount >= this.lostPreyUntil;
    }

    /** A target that turns up close: the burst at once instead of the roar. */
    @Override
    public void setTarget(LivingEntity target) {
        boolean burst = !this.level().isClientSide() && target != null && super.getTarget() == null && !this.isTame()
                && !this.isBaby() && !this.isVehicle() && (this.mode() == MODE_NONE || this.mode() == MODE_CROUCH)
                && this.distanceTo(target) < BURST_RANGE * Math.max(0.6D, this.getScale())
                && !(target instanceof DinosaurEntity d && this.duels(d));
        if (burst) {
            this.burstTarget = target.getId();      // before the base hears of it: no roar, it charges
        }
        boolean cannibal = !this.level().isClientSide() && target instanceof Majungasaurine && target != super.getTarget();
        super.setTarget(target);
        if (burst) {
            if (super.getTarget() == target) {
                this.startBurst(target);
            } else {
                this.burstTarget = -1;
            }
        }
        if (cannibal && super.getTarget() == target) {
            this.logAct(this.isDueling() || this.duels(target)
                    ? "takes on the majungasaurus #" + target.getId()
                    : String.format("cannibal: hunts the wounded majungasaurus #%d (%d/%d, own hunger %d)", target.getId(),
                    Math.round(target.getHealth()), Math.round(target.getMaxHealth()), this.getHunger()));
        }
    }

    @Override
    public void roar() {
        if (this.burstTarget >= 0 && this.mode() == MODE_BURST) {
            return;
        }
        super.roar();
    }

    @Override
    public boolean hasRoaredAt(LivingEntity target) {
        return super.hasRoaredAt(target) || (target != null && target.getId() == this.burstTarget);
    }

    private void startBurst(LivingEntity target) {
        this.setMode(MODE_BURST);
        this.burstLeft = BURST_TICKS_LEFT;
        this.burstFrom = this.position();
        this.burstHit = false;
        AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.removeModifier(BURST_ID);
            speed.addTransientModifier(new AttributeModifier(BURST_ID, "majungasaurus burst", BURST_BOOST, AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
        this.logAct(String.format("burst: charges the %s, %.1f blocks off", target.getType().toShortString(), this.distanceTo(target)));
    }

    private void endBurst() {
        AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.removeModifier(BURST_ID);
        }
        if (this.mode() == MODE_BURST) {
            this.setMode(MODE_NONE);
        }
    }

    // ------------------------------------------------------------------ the cannibal

    /** The generated isPrey: a wild Majungasaurus very hungry (below 20) takes a badly wounded one of its kind
     *  (below a quarter of its health) as prey (Rogers et al. 2003: it ate its own kind; whether it killed them is not
     *  known, so only the dying). */
    public static boolean cannibalPrey(DinosaurEntity hunter, LivingEntity e) {
        return e instanceof Majungasaurine m && e != hunter && !hunter.isTame() && !m.isTame() && !hunter.isBaby()
                && hunter.getHunger() < 20 && m.getHealth() < m.getMaxHealth() * 0.25F;
    }

    /** The nearest carcass with meat within this many blocks (at size 1), or null. */
    public CarcassEntity carcassNear(double r) {
        double reach = this.getBbWidth() * 0.5D + r * this.getScale();
        CarcassEntity best = null;
        double bestD = Double.MAX_VALUE;
        for (CarcassEntity c : this.level().getEntitiesOfClass(CarcassEntity.class, this.getBoundingBox().inflate(reach + 2.0D),
                CarcassEntity::hasMeat)) {
            double d = Math.sqrt(this.distanceToSqr(c)) - c.getBbWidth() * 0.5D;
            if (d <= reach && d < bestD) {
                bestD = d;
                best = c;
            }
        }
        return best;
    }

    /** At a carcass: the meal of its own kind logged once; two hungry ones at the same carcass duel for it (the winner
     *  eats; the loser gives in and goes, DinosaurEntity.submitTo); a meat eater that comes near is growled off. */
    private void carcassTick() {
        if (this.carcassFightCooldown > 0) {
            this.carcassFightCooldown--;
        }
        if ((this.tickCount + this.getId()) % 20 != 0 || this.isTame() || this.isBaby() || this.isVehicle() || this.isDueling()
                || this.isHolding()) {
            return;
        }
        CarcassEntity carcass = this.carcassNear(3.0D);
        if (carcass == null) {
            return;
        }
        if ("majungasaurus".equals(carcass.speciesId()) && carcass.getId() != this.cannibalLogged && this.getTarget() == null
                && !this.isSated()) {
            this.cannibalLogged = carcass.getId();
            this.logAct("cannibal: eats the carcass of a majungasaurus (Rogers et al. 2003)");
        }
        if (this.getTarget() != null || this.isSated() || !this.isHungry() || this.carcassFightCooldown > 0) {
            return;
        }
        double r = 8.0D * this.getScale();
        for (Majungasaurine rival : this.level().getEntitiesOfClass(Majungasaurine.class, carcass.getBoundingBox().inflate(r),
                m -> m != this && m.isAlive() && !m.isTame() && !m.isBaby() && m.isHungry() && !m.isDueling()
                        && m.getTarget() == null && m.fightsInDuel())) {
            if (!this.canAttack(rival)) {
                continue;
            }
            this.carcassFightCooldown = 1200;
            rival.carcassFightCooldown = 1200;
            this.logAct(String.format("carcass fight: takes on the majungasaurus #%d over the %s carcass (both hungry: %d, %d)",
                    rival.getId(), carcass.speciesId(), this.getHunger(), rival.getHunger()));
            this.triggerAnim(ACTION_CONTROLLER, "carcass_guard");
            this.setTarget(rival);
            return;
        }
        // over the meat: a growl at another meat eater coming near
        if (this.threatCooldown <= 0) {
            for (DinosaurEntity other : this.level().getEntitiesOfClass(DinosaurEntity.class, this.getBoundingBox().inflate(r),
                    e -> e != this && e.isAlive() && !e.isBaby() && !(e instanceof Majungasaurine) && CarcassStealGoal.eatsMeat(e))) {
                this.getLookControl().setLookAt(other, 30.0F, 30.0F);
                this.triggerAnim(ACTION_CONTROLLER, "carcass_guard");
                this.playSound(this.roarSound(), 1.2F, 0.8F * this.getVoicePitch());
                this.threatCooldown = 120 + this.getRandom().nextInt(80);
                this.logAct("carcass guard: growls over the carcass at the " + other.speciesId());
                return;
            }
        }
    }

    /** The low warning voice (its threat), for the dome and the waterhole. */
    public void warnSound() {
        this.playSound(this.roarSound(), 1.2F, 0.85F * this.getVoicePitch());
    }

    // ------------------------------------------------------------------ the temper

    /** A player who comes within 8 blocks is warned with the dome; one who then comes within 4.5 is attacked. */
    private void temperTick() {
        if (this.warnCooldown > 0) {
            this.warnCooldown--;
        }
        if (this.threatCooldown > 0) {
            this.threatCooldown--;
        }
        if ((this.tickCount + this.getId()) % 10 != 0 || this.isTame() || this.isBaby() || this.getTarget() != null
                || this.isSleeping() || this.isKnockedOut() || this.isVehicle() || this.isHolding() || this.isRoaring()) {
            return;
        }
        Player p = this.level().getNearestPlayer(this, WARN_RANGE * Math.max(0.6D, this.getScale()));
        if (p == null || p.isCreative() || p.isSpectator() || !this.canAttack(p)) {
            return;
        }
        boolean warnedHim = p.getUUID().equals(this.warned) && this.tickCount < this.warnedUntil;
        double d = this.distanceTo(p);
        if (warnedHim && d < WARN_ATTACK * Math.max(0.6D, this.getScale()) + this.getBbWidth() * 0.5D) {
            this.logAct(String.format("temper: the player came on to %.1f blocks after the warning, attacks", d));
            this.setTarget(p);
        } else if (!warnedHim && this.warnCooldown <= 0) {
            this.getLookControl().setLookAt(p, 30.0F, 30.0F);
            this.triggerAnim(ACTION_CONTROLLER, this.mode() == MODE_CROUCH ? "waterhole_threat" : "dome_display");
            this.playSound(this.roarSound(), 1.0F, 0.9F * this.getVoicePitch());
            this.warned = p.getUUID();
            this.warnedUntil = this.tickCount + 100;
            this.warnCooldown = 200;
            this.logAct(String.format("temper: warns the player with the dome at %.1f blocks", d));
        }
    }

    // ------------------------------------------------------------------ the day

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.waterholeCooldown > 0) {
            this.waterholeCooldown--;
        }
        if (this.isHolding()) {
            this.holdTick();
        }
        LivingEntity target = super.getTarget();
        if (this.burstTarget >= 0 && (target == null || target.getId() != this.burstTarget)) {
            this.burstTarget = -1;            // the burst's prey is gone, or it took another target
            this.endBurst();
        }
        if (this.burstLeft > 0 && --this.burstLeft == 0) {
            this.endBurst();
        }
        if (this.burstTarget >= 0 && target != null && this.burstFrom != null && !this.burstHit
                && this.position().distanceToSqr(this.burstFrom) > BURST_CHASE * BURST_CHASE * Math.max(1.0D, this.getScale())) {
            // the burst missed: it does not run far (study 13)
            this.logAct(String.format("burst: missed the %s, gives up %.0f blocks from where it started",
                    target.getType().toShortString(), Math.sqrt(this.position().distanceToSqr(this.burstFrom))));
            this.lostPrey = target.getUUID();
            this.lostPreyUntil = this.tickCount + 600;
            this.burstTarget = -1;
            this.endBurst();
            this.setTarget(null);
        }
        this.carcassTick();
        this.temperTick();
    }

    // ------------------------------------------------------------------ the client: its own loops

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        byte mode = this.mode();
        if (mode != MODE_NONE && !this.isVehicle() && !this.isSleeping() && !this.isInSittingPose() && !this.isSwimmingDeep()
                && !this.isKnockedOut() && !this.isDueling()) {
            boolean moving = state.isMoving();
            if (mode == MODE_HOLD) {
                if (this.holdAnim == null) {
                    this.holdAnim = RawAnimation.begin().thenLoop(anim("hold_shake"));
                }
                return state.setAndContinue(this.holdAnim);
            }
            if (mode == MODE_CROUCH && !moving) {
                if (this.crouchAnim == null) {
                    this.crouchAnim = RawAnimation.begin().thenLoop(anim("ambush_crouch"));
                }
                return state.setAndContinue(this.crouchAnim);
            }
            if (mode == MODE_BURST && moving) {
                if (this.burstAnim == null) {
                    this.burstAnim = RawAnimation.begin().thenLoop(anim("burst"));
                }
                this.cycleSpeed = this.gaitSpeed(BURST_PX / 16.0D / BURST_TICKS * this.modelScale());
                return state.setAndContinue(this.burstAnim);
            }
        }
        return super.movementAnimation(state);
    }
}
