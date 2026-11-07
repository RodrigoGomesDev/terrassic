package com.terrassic.entity;

import java.util.Comparator;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The hand-made Edmontosaurus rig (tools/modelgen/handmade/edmontosaurus, its own study). Its touch is the BIG HERD
 * WITH A SENTINEL and the BELLOW of the nasal sacs. What it adds over a plain grazer:
 * <ul>
 *   <li>the walk (on four) and the run (on two) follow the real speed, so the feet do not slide;</li>
 *   <li>the sentinel: in a wild herd one adult at a time keeps watch while the others graze, standing with the head
 *       high ("vigilant" now and then); the watch passes to another every half minute or so;</li>
 *   <li>the alarm: the sentinel (or any adult) that sees a wild predator within 20 blocks bellows short and hard
 *       ("alarm") and the whole herd within 40 blocks runs from it at once, the young among the adults;</li>
 *   <li>the voice: with its ambient sound a wild adult now and then calls through its half-filled sacs ("call") and one
 *       or two of the herd answer; a grown male near a female bellows with the sacs full and the comb up
 *       ("bellow"); a baby far from the adults peeps ("peep");</li>
 *   <li>idle: it grazes low in long sweeps ("graze"), rears to high leaves in front of it ("browse_high", a meal) and
 *       drinks at the water ("drink").</li>
 * </ul>
 * The comb is the grown male's: the renderer hides "male_display" on females and "adult_comb" on the young.
 * <p>Wild, it never charges: it runs, the herd with it (first seen in the behaviour test, 06/11: as a plain fighting
 * herbivore the whole herd walked up to the T. rex the alarm had named). Tame, it defends itself and its owner.
 */
public abstract class Saurolophine extends HerbivoreDinosaur {
    /** The cycles (edmontoanims.py WALK, RUNP): pixels of ground each covers at 20 px/m and its length in ticks. */
    private static final double WALK_PX = 46.0D;
    private static final double WALK_TICKS = 34.0D;
    private static final double RUN_PX = 112.0D;
    private static final double RUN_TICKS = 13.2D;
    private static final double HERD = 40.0D;
    private static final double PREDATOR = 20.0D;
    /** Ticks a sentinel keeps the watch before it passes on. */
    private static final int WATCH_SHIFT = 600;

    private int still;
    private int callCooldown;
    private int alarmCooldown;
    private int answerIn = -1;
    private LivingEntity answerTo;
    /** Ticks left of this one's watch (0 = not the sentinel). */
    private int sentinel;
    /** What the herd runs from, and for how long it keeps running. */
    private LivingEntity fleeing;
    private int fleeTicks;

    protected Saurolophine(EntityType<? extends Saurolophine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "call", "answer", "alarm", "peep", "vigilant", "bellow", "browse_high", "drink"};
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

    /** Wild it flees (the herd runs together from whatever the alarm named); tame it stands and fights. */
    @Override
    protected boolean fightsBack() {
        return this.isTame();
    }

    /** It does not run from a player who has not hurt it: a herd grazes on while one walks up with food. */
    @Override
    protected boolean fleesFrom(net.minecraft.world.entity.player.Player player) {
        return this.getLastHurtByMob() == player;
    }

    /** Runs straight away from the threat, about 16 blocks (scaled), at a gallop. */
    private void fleeFrom(LivingEntity threat) {
        Vec3 away = net.minecraft.world.entity.ai.util.DefaultRandomPos.getPosAway(this, 16, 7, threat.position());
        if (away == null) {
            Vec3 d = this.position().subtract(threat.position());
            Vec3 flat = new Vec3(d.x, 0.0D, d.z).normalize().scale(16.0D);
            away = this.position().add(flat);
        }
        this.getNavigation().moveTo(away.x, away.y, away.z, 1.6D);
    }

    /** 1.9.5: the one on watch stays awake through the herd's night (docs/estudos/12). */
    @Override
    public boolean safeToSleep() {
        return this.sentinel == 0 && super.safeToSleep();
    }

    @Override
    public boolean wokenByThreat() {
        return this.sentinel > 0 || super.wokenByThreat();
    }

    private boolean busy() {
        return this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut();
    }

    private List<Saurolophine> herd(double r) {
        return this.level().getEntitiesOfClass(Saurolophine.class, this.getBoundingBox().inflate(r),
                e -> e != this && e.isAlive() && !e.isTame() && e.getType() == this.getType());
    }

    /** The alarm: a short hard bellow, and the whole herd runs from the threat at once. */
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
        this.fleeFrom(threat);
        this.fleeing = threat;
        this.fleeTicks = 100;
        for (Saurolophine other : this.herd(HERD)) {
            other.alarmCooldown = Math.max(other.alarmCooldown, 120);
            other.still = 0;
            other.sentinel = 0;
            other.setSleeping(false);
            other.fleeing = threat;
            other.fleeTicks = 100;
            other.fleeFrom(threat);
        }
    }

    /** A call through the half-filled sacs; one or two of the herd answer, turned toward it. */
    private void call() {
        triggerAnim(ACTION_CONTROLLER, "call");
        this.still = Math.max(this.still, 60);
        this.callCooldown = 400;
        int answers = 0;
        for (Saurolophine other : this.herd(HERD * 0.8D)) {
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
        if (this.answerIn >= 0 && --this.answerIn < 0) {
            LivingEntity caller = this.answerTo;
            this.answerTo = null;
            if (caller != null && caller.isAlive() && !this.busy()) {
                this.getLookControl().setLookAt(caller, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, caller.isBaby() ? "call" : "answer");
                this.still = Math.max(this.still, 40);
            }
        }
        if (this.fleeTicks > 0) {
            this.fleeTicks--;
            this.still = 0;
            if (this.fleeing != null && this.fleeing.isAlive() && !this.isTame() && this.getNavigation().isDone()
                    && this.distanceToSqr(this.fleeing) < 24.0D * 24.0D) {
                this.fleeFrom(this.fleeing);
            }
            return;
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
        if (this.isBaby()) {
            this.youngStep();
            return;
        }
        if (this.tickCount % 10 == 0 && this.alarmCooldown == 0) {
            // any adult that sees a wild predator raises the alarm; the sentinel sees farther
            double range = this.sentinel > 0 ? PREDATOR * 1.4D : PREDATOR;
            // a herd lets a fed predator be at a distance (it shadows them all day): only one that hunts, or one that
            // comes close, raises the alarm (06/11: a full T. rex at 30 blocks kept the herd running and broke migrations)
            List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(range),
                    p -> p.isAlive() && !p.isTame() && !p.isBaby() && this.hasLineOfSight(p)
                            && (p.canHunt() || p.getTarget() != null || p.distanceToSqr(this) < 12.0D * 12.0D));
            if (!near.isEmpty()) {
                this.alarm(near.get(0));
                return;
            }
        }
        if (this.getMigrationTarget() != null) {
            this.sentinel = 0;      // on the move nobody stands watch
            return;
        }
        this.watchStep();
        if (this.sentinel > 0 || !this.getNavigation().isDone() || this.random.nextInt(600) != 0) {
            return;
        }
        this.idleAct();
    }

    /** The sentinel's shift: if no one in the herd keeps watch, this one takes it; on watch it stands with the head
     *  high, now and then the stare; at the end of the shift it goes back to grazing. */
    private void watchStep() {
        if (this.sentinel > 0) {
            this.sentinel--;
            this.getNavigation().stop();
            if (this.sentinel % 80 == 40) {
                triggerAnim(ACTION_CONTROLLER, "vigilant");
            }
            if (this.sentinel == 0) {
                if (this.isSleepTime()) {
                    // 1.9.5, the night watch: it wakes a sleeping one of the herd to take over before it lies down
                    for (Saurolophine o : this.herd(HERD * 0.6D)) {
                        if (o.isSleeping() && !o.isBaby()) {
                            o.setSleeping(false);
                            o.sentinel = WATCH_SHIFT + this.random.nextInt(WATCH_SHIFT);
                            o.triggerAnim(ACTION_CONTROLLER, "vigilant");
                            break;
                        }
                    }
                } else {
                    triggerAnim(ACTION_CONTROLLER, "graze");
                    this.still = 60;
                }
            }
            return;
        }
        if (this.tickCount % 100 != this.getId() % 100) {
            return;
        }
        List<Saurolophine> herd = this.herd(HERD * 0.6D);
        if (herd.isEmpty() || herd.stream().anyMatch(e -> e.sentinel > 0)) {
            return;
        }
        this.sentinel = WATCH_SHIFT / 2 + this.random.nextInt(WATCH_SHIFT);
        triggerAnim(ACTION_CONTROLLER, "vigilant");
    }

    /** The young: far from every adult it peeps and the nearest adult answers. */
    private void youngStep() {
        if (this.callCooldown > 0 || this.tickCount % 40 != 0) {
            return;
        }
        List<Saurolophine> near = this.herd(HERD);
        boolean adultClose = near.stream().anyMatch(e -> !e.isBaby() && e.distanceToSqr(this) < 100.0D);
        Saurolophine adult = near.stream().filter(e -> !e.isBaby() && !e.busy())
                .min(Comparator.comparingDouble(e -> e.distanceToSqr(this))).orElse(null);
        if (!adultClose && adult != null) {
            triggerAnim(ACTION_CONTROLLER, "peep");
            this.callCooldown = 200;
            adult.answerTo = this;
            adult.answerIn = 15;
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
            Saurolophine mate = this.nearestFemale();
            if (mate != null && this.random.nextInt(3) == 0) {
                this.getLookControl().setLookAt(mate, 30.0F, 30.0F);
                mate.getLookControl().setLookAt(this, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "bellow");
                this.still = 88;
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

    /** Leaves in front of it out of reach on four legs but in reach reared up (3 to 5 blocks up, scaled). */
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

    private Saurolophine nearestFemale() {
        Saurolophine best = null;
        double bestD = Double.MAX_VALUE;
        for (Saurolophine e : this.level().getEntitiesOfClass(Saurolophine.class, this.getBoundingBox().inflate(10.0D),
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
