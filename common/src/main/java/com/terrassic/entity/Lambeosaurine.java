package com.terrassic.entity;

import com.terrassic.network.ModNetwork;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The hand-made Parasaurolophus rig (tools/modelgen/handmade/parasaurolophus, its own study and 24 animations). Its
 * touch is the HERD and the CREST CALL: the voices are on standby, so the call shows as a behaviour and an animation
 * (the bill shut, the head tipped back, the chest heaving). What it adds over a plain runner:
 * <ul>
 *   <li>the walk (on four) and the run (on two) follow the real speed, so the feet do not slide;</li>
 *   <li>the contact call: with its ambient sound a wild adult now and then calls ("call"); one or two of the herd
 *       within 32 blocks turn to it and answer a moment later ("answer");</li>
 *   <li>the alarm: a wild adult that sees a wild predator within 24 blocks, or is hurt, half-rears and gives the
 *       alarm ("alarm", the tail lifted on its black flag); every wild Parasaurolophus within 32 blocks wakes and
 *       runs from that threat;</li>
 *   <li>the young call: a baby more than 10 blocks from any adult peeps ("peep") and the nearest adult answers;</li>
 *   <li>the taming, built on the herd's watch: a wild herd does not bolt at the first sight of a player. One that
 *       sees a player within 16 blocks stares at them, head high and frozen ("vigilant"). If the player MOVES while
 *       it stares, it gives the alarm and the herd runs from that player for a while. If the player stands still
 *       for three seconds, the herd lets them be: it goes back to feeding and the player may walk up (not sprint)
 *       and hand-feed one. Sprinting or a blow ends it;</li>
 *   <li>idle: it rears to high leaves in front of it ("browse_high", a meal), drinks at the water ("drink"), and a
 *       wild adult male near an adult female rears and shows his crest ("crest_display").</li>
 * </ul>
 * The young have only a low dome: the renderer hides "adult_crest" on babies and shows them "young_crest"
 * (DinoGeoModel). Its own reed saddle is the only one it takes (gen_species: PARASAUROLOPHUS_SADDLE).
 */
public abstract class Lambeosaurine extends HerbivoreDinosaur {
    /** The cycles (paraanims.py WALK, RUNP): pixels of ground each covers at 24 px/m and its length in ticks. */
    private static final double WALK_PX = 46.0D;
    private static final double WALK_TICKS = 34.0D;
    private static final double RUN_PX = 112.0D;
    private static final double RUN_TICKS = 13.2D;
    private static final double HERD = 32.0D;
    private static final double WATCH = 16.0D;
    /** Blocks a watched player may drift in half a second and still count as standing still. */
    private static final double DRIFT = 0.35D;
    /** Ticks a watched player has to stand still before the herd lets them be. */
    private static final int STILL_TO_ACCEPT = 60;
    private static final int ACCEPT_TICKS = 2400;
    private static final int SCARED_TICKS = 400;

    private int still;
    private int callCooldown;
    private int alarmCooldown;
    private int answerIn = -1;
    private LivingEntity answerTo;
    private UUID watching;
    private Vec3 watchedAt;
    private int watchedStill;
    private int watchTicks;
    /** Players this animal tolerates (until game time) and players it runs from (until game time). */
    private final Map<UUID, Long> accepted = new HashMap<>();
    private final Map<UUID, Long> scaredOf = new HashMap<>();

    protected Lambeosaurine(EntityType<? extends Lambeosaurine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "call", "answer", "alarm", "peep", "vigilant", "crest_display", "browse_high", "drink"};
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
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    private long now() {
        return this.level().getGameTime();
    }

    /** It runs from a player it was frightened by, or from one it tolerates who is sprinting at it. A player it has
     *  not made up its mind about is watched instead (see {@link #watch}). */
    @Override
    protected boolean fleesFrom(Player player) {
        if (player.isCreative() || player.isSpectator()) {
            return false;
        }
        UUID id = player.getUUID();
        if (this.scaredOf.getOrDefault(id, 0L) > this.now()) {
            return true;
        }
        if (this.accepted.getOrDefault(id, 0L) > this.now()) {
            if (player.isSprinting()) {
                this.alarm(player);
                return true;
            }
            return false;
        }
        return this.isBaby();
    }

    private boolean busy() {
        return this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut();
    }

    private List<Lambeosaurine> herd(double r) {
        return this.level().getEntitiesOfClass(Lambeosaurine.class, this.getBoundingBox().inflate(r),
                e -> e != this && e.isAlive() && !e.isTame());
    }

    /** The alarm: this one calls, and every wild one in the herd wakes and runs from the threat. */
    private void alarm(LivingEntity threat) {
        if (this.alarmCooldown > 0 || this.isTame()) {
            return;
        }
        this.alarmCooldown = 200;
        this.watching = null;
        if (!this.isBaby() && !this.isSleeping()) {
            this.getLookControl().setLookAt(threat, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "alarm");
        }
        boolean fromPlayer = threat instanceof Player;
        this.frighten(threat, fromPlayer);
        for (Lambeosaurine other : this.herd(HERD)) {
            other.alarmCooldown = Math.max(other.alarmCooldown, 120);
            other.watching = null;
            other.still = 0;
            other.frighten(threat, fromPlayer);
        }
        if (fromPlayer) {
            this.notice(threat, ModNetwork.NOTICE_BLOOD, Component.translatable("hud.terrassic.notice.herd_fled"), this.speciesName());
        }
    }

    private void frighten(LivingEntity threat, boolean fromPlayer) {
        this.setSleeping(false);
        if (fromPlayer) {
            this.scaredOf.put(threat.getUUID(), this.now() + SCARED_TICKS);
            this.accepted.remove(threat.getUUID());
        } else {
            this.setLastHurtByMob(threat);
        }
    }

    /** The herd lets this player be: back to feeding, the player may walk up. */
    private void accept(Player player) {
        long until = this.now() + ACCEPT_TICKS;
        this.accepted.put(player.getUUID(), until);
        this.watching = null;
        for (Lambeosaurine other : this.herd(HERD)) {
            other.accepted.put(player.getUUID(), until);
            if (player.getUUID().equals(other.watching)) {
                other.watching = null;
            }
        }
        this.notice(player, ModNetwork.NOTICE_FERN, Component.translatable("hud.terrassic.notice.herd_calm"), this.speciesName());
        triggerAnim(ACTION_CONTROLLER, "graze");
        this.still = 50;
    }

    /** The contact call; one or two of the herd answer in a moment, turned toward it. */
    private void call() {
        triggerAnim(ACTION_CONTROLLER, "call");
        this.still = Math.max(this.still, 60);
        this.callCooldown = 400;
        int answers = 0;
        for (Lambeosaurine other : this.herd(HERD)) {
            if (answers >= 2 || other.isBaby() || other.busy() || other.answerIn >= 0) {
                continue;
            }
            other.answerTo = this;
            other.answerIn = 20 + this.random.nextInt(30) + answers * 18;
            other.callCooldown = Math.max(other.callCooldown, 200);
            answers++;
        }
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!this.level().isClientSide() && !this.isTame() && !this.isBaby() && !this.busy() && this.callCooldown == 0
                && this.random.nextInt(3) == 0) {
            this.call();
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && !this.isTame() && source.getEntity() instanceof LivingEntity attacker) {
            this.alarm(attacker);
        }
        return hurt;
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
        if (this.tickCount % 200 == 0) {
            long t = this.now();
            this.accepted.values().removeIf(until -> until < t);
            this.scaredOf.values().removeIf(until -> until < t);
        }
        // an answer due to another's call
        if (this.answerIn >= 0 && --this.answerIn < 0) {
            LivingEntity caller = this.answerTo;
            this.answerTo = null;
            if (caller != null && caller.isAlive() && !this.busy()) {
                this.getLookControl().setLookAt(caller, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "answer");
                this.still = Math.max(this.still, 40);
            }
        }
        if (this.watching != null) {
            this.watch();
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.busy() || this.isTame()) {
            if (this.isTame() && !this.busy() && this.getNavigation().isDone() && this.random.nextInt(900) == 0) {
                this.idleAct();
            }
            return;
        }
        // the young: far from every adult, it peeps and the nearest adult answers
        if (this.isBaby()) {
            if (this.callCooldown == 0 && this.tickCount % 40 == 0) {
                List<Lambeosaurine> near = this.herd(HERD);
                boolean adultClose = near.stream().anyMatch(e -> !e.isBaby() && e.distanceToSqr(this) < 100.0D);
                Lambeosaurine adult = near.stream().filter(e -> !e.isBaby() && !e.busy())
                        .min((a, b) -> Double.compare(a.distanceToSqr(this), b.distanceToSqr(this))).orElse(null);
                if (!adultClose && adult != null) {
                    triggerAnim(ACTION_CONTROLLER, "peep");
                    this.callCooldown = 200;
                    adult.answerTo = this;
                    adult.answerIn = 15;
                }
            }
            return;
        }
        if (this.tickCount % 10 == 0) {
            // a wild predator in sight: the alarm
            if (this.alarmCooldown == 0) {
                List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(24.0D),
                        p -> p.isAlive() && !p.isTame() && !p.isBaby() && this.hasLineOfSight(p));
                if (!near.isEmpty()) {
                    this.alarm(near.get(0));
                    return;
                }
            }
            // a player it has not made up its mind about: watch them
            if (this.watching == null && this.alarmCooldown == 0) {
                Player p = this.level().getNearestPlayer(this, WATCH);
                if (p != null && !p.isCreative() && !p.isSpectator() && this.hasLineOfSight(p)
                        && this.accepted.getOrDefault(p.getUUID(), 0L) <= this.now()
                        && this.scaredOf.getOrDefault(p.getUUID(), 0L) <= this.now()) {
                    this.watching = p.getUUID();
                    this.watchedAt = p.position();
                    this.watchedStill = 0;
                    this.watchTicks = 0;
                    triggerAnim(ACTION_CONTROLLER, "vigilant");
                    return;
                }
            }
        }
        if (!this.getNavigation().isDone() || this.random.nextInt(600) != 0) {
            return;
        }
        this.idleAct();
    }

    /** The stare: the player is watched every tick; moving gives the alarm, standing still earns the herd's leave. */
    private void watch() {
        Player p = this.watching == null ? null : this.level().getPlayerByUUID(this.watching);
        if (p == null || !p.isAlive() || p.isCreative() || p.isSpectator() || this.distanceToSqr(p) > (WATCH + 8) * (WATCH + 8)
                || this.isTame() || this.busy()) {
            this.watching = null;
            return;
        }
        this.getNavigation().stop();
        this.getLookControl().setLookAt(p, 30.0F, 30.0F);
        this.watchTicks++;
        if (this.watchTicks % 60 == 0) {
            triggerAnim(ACTION_CONTROLLER, "vigilant");
        }
        if (this.watchTicks % 10 != 0) {
            return;
        }
        Vec3 pos = p.position();
        double moved = Math.sqrt(Math.pow(pos.x - this.watchedAt.x, 2) + Math.pow(pos.z - this.watchedAt.z, 2));
        this.watchedAt = pos;
        if (moved > DRIFT || p.isSprinting()) {
            this.alarm(p);
            return;
        }
        this.watchedStill += 10;
        if (this.watchedStill >= STILL_TO_ACCEPT) {
            this.accept(p);
        }
    }

    /** Now and then, when nothing else is going on. */
    private void idleAct() {
        if (this.isInWater() || this.waterInFront()) {
            triggerAnim(ACTION_CONTROLLER, "drink");
            this.still = 70;
            return;
        }
        if (this.leavesHigh()) {
            triggerAnim(ACTION_CONTROLLER, "browse_high");
            this.still = 84;
            this.feed(6);
            return;
        }
        if (!this.isTame() && !this.isFemale()) {
            Lambeosaurine mate = this.nearestFemale();
            if (mate != null && this.random.nextInt(3) == 0) {
                this.getLookControl().setLookAt(mate, 30.0F, 30.0F);
                mate.getLookControl().setLookAt(this, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "crest_display");
                this.still = 92;
                mate.still = Math.max(mate.still, 60);
            }
        }
    }

    /** Water at its feet or in front of it (the bill reaches about two blocks ahead). */
    private boolean waterInFront() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        BlockPos p = BlockPos.containing(this.getX() + look.x * 2.0D * this.getScale(), this.getY() - 0.5D, this.getZ() + look.z * 2.0D * this.getScale());
        return this.level().getFluidState(p).is(FluidTags.WATER) || this.level().getFluidState(p.above()).is(FluidTags.WATER);
    }

    /** Leaves in front of it out of reach on four legs but in reach reared up (3 to 4 blocks up, scaled). */
    private boolean leavesHigh() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        for (int up = 3; up <= 4; up++) {
            BlockPos p = BlockPos.containing(this.getX() + look.x * 2.0D, this.getY() + up * this.getScale(), this.getZ() + look.z * 2.0D);
            if (this.level().getBlockState(p).is(BlockTags.LEAVES)) {
                return true;
            }
        }
        return false;
    }

    private Lambeosaurine nearestFemale() {
        Lambeosaurine best = null;
        double bestD = Double.MAX_VALUE;
        for (Lambeosaurine e : this.level().getEntitiesOfClass(Lambeosaurine.class, this.getBoundingBox().inflate(8.0D),
                o -> o != this && o.isAlive() && o.isFemale() && !o.isBaby() && !o.isSleeping() && o.getTarget() == null)) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }
}
