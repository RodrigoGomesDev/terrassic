package com.terrassic.entity;

import net.minecraft.resources.ResourceLocation;

import com.terrassic.Terrassic;

import com.terrassic.entity.ai.CarcassDragGoal;
import com.terrassic.entity.ai.CarcassStealGoal;
import com.terrassic.entity.ai.RiverAmbushGoal;
import com.terrassic.registry.ModEffects;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The Carcharodontosaurus rig (tools/modelgen/handmade/carcharodontosaurus, made for it from its own study,
 * docs/estudos/13_PREDADORES_1_10.md; the third of the 1.10.1 standard after the Daspletosaurus and the Albertosaurus).
 * The life of an {@link ApexTheropod}, told apart from the Giganotosaurus (which circles, cuts from the side and backs
 * off) by what it does:
 * <ul>
 *   <li><b>The ambush at the river's edge</b> ({@link RiverAmbushGoal}): hungry, it walks to the edge of the water and
 *       waits crouched, dead still ("ambush_crouch"). From there it only takes what comes within {@link #AMBUSH_REACH}
 *       blocks (a player who passes farther off is let go); then it bursts out ("burst": two seconds much faster, no
 *       roar), and if it misses it does not chase far (24 blocks from where it lay). Stevens 2006: limited binocular
 *       vision, like a crocodile's; a hypothesis.</li>
 *   <li><b>The tear</b>: its main bite holds and heaves back sawing the head ("tear"); the blade teeth leave the victim
 *       BLEEDING ({@link com.terrassic.effect.BleedingEffect}) for a few seconds. In a duel the lunge tears too.</li>
 *   <li><b>It drags its kill</b> ({@link CarcassDragGoal}): a small or middling carcass is hauled backwards a few
 *       blocks into the shade (under leaves) or away before it eats ("drag"). Over its kill it hisses with the jaws
 *       wide at a meat eater that comes near ("gape_hiss") and butts a smaller one that comes too close with the
 *       brow ("brow_butt").</li>
 *   <li><b>The brow</b>: in a duel it is patient, blocks a middling amount and hardly dodges; it tears from the front
 *       and answers with a butt of the brow shelf (Chure 1998, a hypothesis; ai/DuelStyle). It opens a duel showing
 *       the brow and the mask broadside ("brow_display"), which the male also does by himself now and then.</li>
 *   <li><b>Trophies</b> (the old species' trait, kept in the generated class): every kill makes it stronger and faster
 *       for a while.</li>
 * </ul>
 * One log line per behaviour ("[carcharo] ...", logger "terrassic") for the playtests. It has the duel and the lively
 * sets of the remade apex predators by its own class, so the shared lists in DinosaurEntity stay untouched.
 */
public abstract class Carcharodontosaurine extends ApexTheropod {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    /** The cycles (carcharoanims.py WALK, RUN, STALK, BURST, DRAG): pixels of ground per cycle (stride x K = 0.88) and
     *  ticks. */
    private static final double WALK_PX = 68.64D;
    private static final double WALK_TICKS = 40.0D;
    private static final double RUN_PX = 109.12D;
    private static final double RUN_TICKS = 18.0D;
    private static final double STALK_PX = 48.05D;
    private static final double STALK_TICKS = 60.0D;
    private static final double BURST_PX = 132.0D;
    private static final double BURST_TICKS = 15.0D;
    private static final double DRAG_PX = 40.48D;
    private static final double DRAG_TICKS = 40.0D;
    /** The blows, timed to the jaws in carcharoanims.py (tick the hit lands, ticks to the next). */
    private static final Strike TEAR = new Strike("tear", 9, 32, false);
    private static final Strike QUICK = new Strike("attack_quick", 6, 24, false);
    private static final Strike LOW = new Strike("bite_low", 8, 24, false);
    private static final Strike SIDE = new Strike("bite_side", 9, 26, false);
    private static final Strike BROW_BUTT = new Strike("brow_butt", 9, 26, false);
    /** From the ambush it takes only what comes this close (blocks, at size 1). */
    public static final double AMBUSH_REACH = 11.0D;
    /** The burst: ticks of it, how much faster, and how far from where it lay it chases before giving up. */
    private static final int BURST_TICKS_LEFT = 40;
    private static final double BURST_BOOST = 0.75D;
    private static final double BURST_CHASE = 24.0D;
    private static final ResourceLocation BURST_ID = Terrassic.id("carcharodontosaurus_burst");
    /** Bleeding: seconds of it on a player and on an animal. */
    private static final int BLEED_PLAYER = 100;
    private static final int BLEED_ANIMAL = 160;
    private static final String[] GESTURES = {"sniff", "look_back", "shake", "yawn", "stretch", "snort", "snort",
            "settle", "settle", "scan", "scan"};
    private static final String[] GESTURES_MALE = {"sniff", "look_back", "shake", "yawn", "stretch", "snort", "snort",
            "settle", "settle", "scan", "scan", "brow_display"};
    /** In the ambush crouch the only gesture is a glance from the crouch (the standing ones would lift it). */
    private static final String[] GESTURES_AMBUSH = {"ambush_look"};
    private static final String[] OWN = {"tear", "brow_butt", "brow_display", "gape_hiss", "ambush_look"};

    public static final byte MODE_NONE = 0;
    public static final byte MODE_AMBUSH = 1;
    public static final byte MODE_BURST = 2;
    public static final byte MODE_DRAG = 3;
    private static final EntityDataAccessor<Byte> DATA_MODE = SynchedEntityData.defineId(Carcharodontosaurine.class, EntityDataSerializers.BYTE);

    private RawAnimation ambushAnim;
    private RawAnimation burstAnim;
    private RawAnimation dragAnim;
    /** Server: the burst under way (ticks left), at what, from where, and whether a blow has landed since. */
    private int burstLeft;
    private int burstTarget = -1;
    private Vec3 burstFrom;
    private boolean burstHit;
    /** Server: the prey it gave up after a missed burst, left alone for a while. */
    private UUID lostPrey;
    private int lostPreyUntil;
    /** Server: ticks before the next ambush (RiverAmbushGoal). */
    public int ambushCooldown = 200;
    /** Server: its last kill (tick, where, entity id) for the drag. */
    private int lastKillTick = -1000;
    private Vec3 lastKillPos;
    private int draggedCarcass = -1;
    /** Server: the carcass act (hiss, butt) and the pending butt's hit. */
    private int carcassActCooldown;
    private int buttIn;
    private LivingEntity buttAt;

    protected Carcharodontosaurine(EntityType<? extends Carcharodontosaurine> type, Level level) {
        super(type, level);
    }

    /** Logs one behaviour line: "[carcharo] what (#id x y z)". */
    public void logAct(String what) {
        LOG.info("[carcharo] {} (#{} {} {} {})", what, this.getId(), this.getBlockX(), this.getBlockY(), this.getBlockZ());
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(DATA_MODE, MODE_NONE);
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
        if (this.mode() == MODE_AMBUSH) {
            return GESTURES_AMBUSH;
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

    /** Its bite tip against the T. rex's the distances were measured on: a big deep head on a short thick neck. */
    @Override
    public double reachScale() {
        return 0.95D;
    }

    // ------------------------------------------------------------------ blows, the tear and the duel

    /** The tear most of all (big prey and players more), the quick bite, the low sweep for small things, the arc. */
    @Override
    public Strike biteFor(LivingEntity target) {
        float r = this.getRandom().nextFloat();
        if (target.getBbHeight() < 1.4F && r < 0.35F) {
            return LOW;
        }
        if (target.getBbWidth() >= 1.2F || target instanceof Player) {
            return r < 0.6F ? TEAR : r < 0.8F ? SIDE : QUICK;
        }
        return r < 0.45F ? TEAR : r < 0.75F ? QUICK : SIDE;
    }

    /** After the tear it steps back with the piece a moment; no circling (that is the Giganotosaurus). */
    @Override
    public Pause pauseAfter(Strike strike) {
        Pause alpha = super.pauseAfter(strike);
        if (alpha != null) {
            return alpha;
        }
        return strike == TEAR ? new Pause(6, null, 0, 0) : null;
    }

    /** A blow landed (ApexBiteGoal): the tear leaves the victim bleeding. */
    @Override
    public void struck(LivingEntity target, Strike strike) {
        super.struck(target, strike);
        this.burstHit = true;
        if (strike == TEAR) {
            this.bleed(target, "tear");
        }
    }

    /** The blade teeth cut: a few seconds of bleeding on the victim (shorter on a player). */
    public void bleed(LivingEntity target, String how) {
        if (target == null || !target.isAlive() || this.level().isClientSide()) {
            return;
        }
        int ticks = target instanceof Player ? BLEED_PLAYER : BLEED_ANIMAL;
        target.addEffect(new MobEffectInstance(ModEffects.bleeding(), ticks, 0), this);
        this.logAct(how + ": the " + target.getType().toShortString() + " bleeds (" + ticks / 20 + " s, health "
                + Math.round(target.getHealth()) + ")");
    }

    /** ai/DuelGoal: a duel move started (the brow butt, the parry that ends in one) is logged. */
    public static void duelMove(DinosaurEntity mob, String anim) {
        if (mob instanceof Carcharodontosaurine c && ("brow_butt".equals(anim) || "parry".equals(anim))) {
            c.logAct("parry".equals(anim) ? "brow butt (parry counter)" : "brow butt");
        }
    }

    /** ai/DuelGoal: a duel blow landed; its lunge ends in the tear, so the rival bleeds. */
    public static void duelHit(DinosaurEntity mob, LivingEntity rival, boolean lunge) {
        if (lunge && mob instanceof Carcharodontosaurine c) {
            c.bleed(rival, "duel tear");
        }
    }

    /** Chest to chest with a rival: the brow. */
    @Override
    public Strike closeStrike() {
        return BROW_BUTT;
    }

    /** It opens a duel showing the brow shelf and the mask broadside. */
    @Override
    public String duelOpener() {
        return "brow_display";
    }

    // ------------------------------------------------------------------ the ambush and the burst

    @Override
    protected void addExtraGoals() {
        super.addExtraGoals();
        this.goalSelector.addGoal(1, new CarcassDragGoal(this));
        this.goalSelector.addGoal(3, new RiverAmbushGoal(this));
    }

    /** RiverAmbushGoal: free to lie in wait (wild, grown, hungry, nothing else on). */
    public boolean ambushReady() {
        return !this.isTame() && !this.isBaby() && this.canHunt() && this.getTarget() == null && this.ambushCooldown <= 0
                && !this.isVehicle() && !this.isSleeping() && !this.isInSittingPose() && !this.isKnockedOut()
                && !this.isDueling() && this.onGround() && !this.isInWater() && this.mode() == MODE_NONE;
    }

    /** From the ambush it takes only what comes into its reach, and a prey it gave up after a missed burst is left
     *  alone for half a minute. */
    @Override
    public boolean canAttack(LivingEntity target) {
        if (!super.canAttack(target)) {
            return false;
        }
        if (target != null && target.getUUID().equals(this.lostPrey) && this.tickCount < this.lostPreyUntil) {
            return false;
        }
        if (target != null && this.mode() == MODE_AMBUSH && super.getTarget() == null && target != this.getLastHurtByMob()) {
            double r = AMBUSH_REACH * Math.max(0.6D, this.getScale()) + this.getBbWidth() * 0.5D;
            return this.distanceToSqr(target) < r * r;
        }
        return true;
    }

    /** A target found from the ambush: the burst instead of the roar. */
    @Override
    public void setTarget(LivingEntity target) {
        boolean fromAmbush = !this.level().isClientSide() && target != null && super.getTarget() == null
                && this.mode() == MODE_AMBUSH;
        if (fromAmbush) {
            this.burstTarget = target.getId();      // before the base hears of it: no roar, it charges
        }
        super.setTarget(target);
        if (fromAmbush) {
            if (super.getTarget() == target) {
                this.startBurst(target);
            } else {
                this.burstTarget = -1;
            }
        }
    }

    /** No roar out of the ambush (it would stand for it); the burst is silent. */
    @Override
    public void roar() {
        if (this.burstTarget >= 0 && this.mode() != MODE_NONE) {
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
        this.ambushCooldown = 600 + this.getRandom().nextInt(600);
        AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.removeModifier(BURST_ID);
            speed.addTransientModifier(new AttributeModifier(BURST_ID, BURST_BOOST, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
        }
        this.logAct(String.format("ambush: bursts out at the %s, %.1f blocks off", target.getType().toShortString(),
                Math.sqrt(this.distanceToSqr(target))));
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

    // ------------------------------------------------------------------ the kill and the carcass

    @Override
    public boolean killedEntity(ServerLevel level, LivingEntity killed) {
        boolean result = super.killedEntity(level, killed);
        this.lastKillTick = this.tickCount;
        this.lastKillPos = killed.position();
        return result;
    }

    /** CarcassDragGoal: its own fresh kill lying close, small or middling, not dragged yet; or null. */
    public CarcassEntity carcassToDrag() {
        if (this.lastKillPos == null || this.tickCount - this.lastKillTick > 100 || this.isBaby() || this.isVehicle()
                || this.getTarget() != null || this.isSated() || this.isInSittingPose() || this.isKnockedOut()) {
            return null;
        }
        double max = this.getBbWidth() * 1.05D;
        for (CarcassEntity c : this.level().getEntitiesOfClass(CarcassEntity.class,
                new net.minecraft.world.phys.AABB(this.lastKillPos, this.lastKillPos).inflate(4.0D), CarcassEntity::hasMeat)) {
            if (c.getId() != this.draggedCarcass && c.getBbWidth() <= max && !this.shadeAt(c.position())) {
                return c;                      // (a kill already in the shade is eaten where it lies)
            }
        }
        return null;
    }

    public void dragStarted(CarcassEntity carcass) {
        this.draggedCarcass = carcass.getId();
        this.setMode(MODE_DRAG);
    }

    public void dragEnded() {
        if (this.mode() == MODE_DRAG) {
            this.setMode(MODE_NONE);
        }
        this.carcassActCooldown = Math.max(this.carcassActCooldown, 60);
    }

    /** Where to walk (backwards) so the carcass ends in the shade: the nearest standing spot under leaves 3 to 10
     *  blocks from the carcass, and past it by the carcass' trailing distance; else away from the water, else straight
     *  back, 6 blocks. */
    public Vec3 dragDestination(CarcassEntity carcass, double hold) {
        Level level = this.level();
        BlockPos at = carcass.blockPosition();
        BlockPos best = null;
        double bestD = Double.MAX_VALUE;
        for (int dx = -10; dx <= 10; dx++) {
            for (int dz = -10; dz <= 10; dz++) {
                double d2 = dx * dx + dz * dz;
                if (d2 < 9.0D || d2 > 100.0D || d2 >= bestD) {
                    continue;
                }
                for (int dy = -2; dy <= 2; dy++) {
                    BlockPos p = at.offset(dx, dy, dz);
                    if (standable(level, p) && !level.canSeeSky(p.above(2))) {
                        best = p;
                        bestD = d2;
                        break;
                    }
                }
            }
        }
        if (best != null) {
            Vec3 shade = Vec3.atBottomCenterOf(best);
            Vec3 dir = shade.subtract(carcass.position()).multiply(1.0D, 0.0D, 1.0D).normalize();
            return shade.add(dir.scale(hold + 1.0D));      // the carcass a block in under the leaves
        }
        BlockPos me = this.blockPosition();
        Vec3 away = null;
        for (int dx = -6; dx <= 6 && away == null; dx += 2) {
            for (int dz = -6; dz <= 6; dz += 2) {
                if (level.getFluidState(me.offset(dx, -1, dz)).is(FluidTags.WATER)) {
                    away = new Vec3(-dx, 0.0D, -dz);
                    break;
                }
            }
        }
        if (away == null || away.lengthSqr() < 1.0E-3D) {
            away = this.position().subtract(carcass.position()).multiply(1.0D, 0.0D, 1.0D);     // straight back
        }
        if (away.lengthSqr() < 1.0E-3D) {
            float yaw = this.getYRot() * Mth.DEG_TO_RAD;
            away = new Vec3(Mth.sin(yaw), 0.0D, -Mth.cos(yaw));
        }
        return this.position().add(away.normalize().scale(6.0D));
    }

    public boolean shadeAt(Vec3 p) {
        return !this.level().canSeeSky(BlockPos.containing(p).above(2));
    }

    private static boolean standable(Level level, BlockPos p) {
        return level.getBlockState(p.below()).isSolidRender(level, p.below()) && level.getBlockState(p).getCollisionShape(level, p).isEmpty()
                && level.getBlockState(p.above()).getCollisionShape(level, p.above()).isEmpty()
                && !level.getFluidState(p).is(FluidTags.WATER);
    }

    /** The nearest carcass with meat right at its jaws, or null. */
    public CarcassEntity carcassAtJaws() {
        double reach = this.getBbWidth() * 0.5D + 2.0D + 2.0D * this.getScale();
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

    /** Over its kill: the wide-jawed hiss at a meat eater that comes near, and the brow at a smaller one too close. */
    private void carcassGuardTick() {
        if (this.carcassActCooldown > 0) {
            this.carcassActCooldown--;
        }
        if (this.buttIn > 0 && --this.buttIn == 0) {
            LivingEntity t = this.buttAt;
            this.buttAt = null;
            if (t != null && t.isAlive() && this.distanceTo(t) < this.getBbWidth() * 0.5D + t.getBbWidth() * 0.5D + 4.5D * this.getScale()) {
                float dmg = (float) (this.getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.6D);
                t.hurt(this.damageSources().mobAttack(this), dmg);
                t.knockback(1.2D, this.getX() - t.getX(), this.getZ() - t.getZ());
                this.impact(t.getX(), t.getY(), t.getZ(), 0.6F, true);
                this.logAct("carcass guard: butts the " + t.getType().toShortString() + " off its kill with the brow");
            }
        }
        if (this.carcassActCooldown > 0 || (this.tickCount + this.getId()) % 20 != 0 || this.isTame() || this.isBaby()
                || this.getTarget() != null || this.isRoaring() || !this.onGround() || this.mode() == MODE_DRAG) {
            return;
        }
        CarcassEntity carcass = this.carcassAtJaws();
        if (carcass == null) {
            return;
        }
        double r = 10.0D * this.getScale();
        for (DinosaurEntity other : this.level().getEntitiesOfClass(DinosaurEntity.class, this.getBoundingBox().inflate(r),
                e -> e != this && e.isAlive() && !e.isBaby() && !(e instanceof Carcharodontosaurine) && CarcassStealGoal.eatsMeat(e))) {
            this.getLookControl().setLookAt(other, 30.0F, 30.0F);
            double gap = this.distanceTo(other) - this.getBbWidth() * 0.5D - other.getBbWidth() * 0.5D;
            if (gap < 4.0D * this.getScale() && Tyrannosaurine.linearSize(other) < Tyrannosaurine.linearSize(this)) {
                this.triggerAnim(ACTION_CONTROLLER, "brow_butt");
                this.buttIn = 9;
                this.buttAt = other;
                this.carcassActCooldown = 60;
                return;
            }
            this.triggerAnim(ACTION_CONTROLLER, "gape_hiss");
            this.playSound(this.roarSound(), 1.4F, 0.7F * this.getVoicePitch());
            this.logAct("carcass guard: hisses at the " + other.speciesId());
            this.carcassActCooldown = 120 + this.getRandom().nextInt(80);
            return;
        }
    }

    // ------------------------------------------------------------------ the day

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.ambushCooldown > 0) {
            this.ambushCooldown--;
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
            // the burst missed: it does not chase far (study 13)
            this.logAct(String.format("ambush: missed the %s, gives up %.0f blocks from where it lay",
                    target.getType().toShortString(), Math.sqrt(this.position().distanceToSqr(this.burstFrom))));
            this.lostPrey = target.getUUID();
            this.lostPreyUntil = this.tickCount + 600;
            this.burstTarget = -1;
            this.endBurst();
            this.setTarget(null);
        }
        this.carcassGuardTick();
    }

    // ------------------------------------------------------------------ the client: its own loops

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        byte mode = this.mode();
        if (mode != MODE_NONE && !this.isVehicle() && !this.isSleeping() && !this.isInSittingPose() && !this.isSwimmingDeep()
                && !this.isKnockedOut() && !this.isDueling()) {
            boolean moving = state.isMoving();
            if (mode == MODE_AMBUSH && !moving) {
                if (this.ambushAnim == null) {
                    this.ambushAnim = RawAnimation.begin().thenLoop(anim("ambush_crouch"));
                }
                return state.setAndContinue(this.ambushAnim);
            }
            if (mode == MODE_BURST && moving) {
                if (this.burstAnim == null) {
                    this.burstAnim = RawAnimation.begin().thenLoop(anim("burst"));
                }
                this.cycleSpeed = this.gaitSpeed(BURST_PX / 16.0D / BURST_TICKS * this.modelScale());
                return state.setAndContinue(this.burstAnim);
            }
            if (mode == MODE_DRAG && moving) {
                if (this.dragAnim == null) {
                    this.dragAnim = RawAnimation.begin().thenLoop(anim("drag"));
                }
                this.cycleSpeed = this.gaitSpeed(DRAG_PX / 16.0D / DRAG_TICKS * this.modelScale());
                return state.setAndContinue(this.dragAnim);
            }
        }
        return super.movementAnimation(state);
    }
}
