package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.Majungasaurine;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The Majungasaurus at the waterhole (docs/estudos/13, "No jogo" 4; the Maevarano's dry seasons and mass deaths by the
 * water, Rogers 2005: a hypothesis). The game has no seasons, so it is the afternoon: once a day a wild grown one goes
 * to the nearest water within 32 blocks (found the way the herbivores find their evening pool,
 * {@link WaterholeGoal#findWater}) and crouches on dry ground at the edge ("ambush_crouch"), facing the water, for up to
 * two minutes. The herds come down to drink there in the late afternoon (WaterholeGoal).
 * <ul>
 *   <li>Whoever comes that it does not hunt (a player, another meat eater, a big herbivore) is warned off with the dome
 *       ("waterhole_threat") at 8 blocks; one that keeps coming (to 4.5 blocks) is attacked.</li>
 *   <li>Prey (when it is hungry) is left to the target goals of the base; the moment it is taken, the burst
 *       ({@link Majungasaurine#setTarget}) ends the wait.</li>
 * </ul>
 */
public class WaterholeGuardGoal extends Goal {
    private static final int SEARCH = 32;
    private static final int MAX_WAIT = 2400;
    private static final int MAX_WALK = 600;
    private static final double WARN = 8.0D;
    private static final double CLOSE = 4.5D;

    private final Majungasaurine mob;
    private BlockPos water;
    private BlockPos spot;
    private boolean crouched;
    private int ticks;
    private int repath;
    private int hurtStamp;
    private long doneDay = -1L;
    private LivingEntity warned;
    private int warnedAt;

    public WaterholeGuardGoal(Majungasaurine mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean free() {
        return !this.mob.isTame() && !this.mob.isBaby() && !this.mob.isVehicle() && !this.mob.isSleeping()
                && !this.mob.isKnockedOut() && !this.mob.isInSittingPose() && !this.mob.isDueling() && !this.mob.isHolding()
                && this.mob.getTarget() == null && this.mob.getLastHurtByMob() == null;
    }

    @Override
    public boolean canUse() {
        long time = this.mob.level().getDayTime();
        long day = time / 24000L;
        long hour = time % 24000L;
        boolean forced = this.mob.waterholeCooldown < 0;        // the playtest sends it at once
        if (!forced && (day == this.doneDay || hour < 6000L || hour > 13000L || this.mob.waterholeCooldown > 0
                || this.mob.getRandom().nextInt(reducedTickDelay(100)) != 0)) {
            return false;
        }
        if (!this.free() || this.mob.mode() != Majungasaurine.MODE_NONE) {
            return false;
        }
        this.water = WaterholeGoal.findWater(this.mob, SEARCH);
        if (this.water == null) {
            this.mob.waterholeCooldown = 1200;
            return false;
        }
        this.spot = this.edgeBy(this.water);
        this.doneDay = day;
        return this.spot != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.spot != null && this.free() && this.ticks < MAX_WAIT && (this.crouched || this.ticks < MAX_WALK)
                && this.mob.getLastHurtByMob() == null && this.mob.getLastHurtByMobTimestamp() == this.hurtStamp;
    }

    @Override
    public void start() {
        this.ticks = 0;
        this.repath = 0;
        this.crouched = false;
        this.warned = null;
        this.hurtStamp = this.mob.getLastHurtByMobTimestamp();
        this.mob.waterholeCooldown = 0;
        this.mob.logAct(String.format("waterhole: goes to guard the water at %d %d %d (%.0f blocks)", this.water.getX(),
                this.water.getY(), this.water.getZ(), Math.sqrt(this.mob.distanceToSqr(Vec3.atCenterOf(this.water)))));
    }

    @Override
    public void stop() {
        if (this.crouched) {
            this.mob.logAct(this.mob.getTarget() != null
                    ? "waterhole: gets up after the " + this.mob.getTarget().getType().toShortString()
                    : "waterhole: leaves the water after " + this.ticks / 20 + " s");
        }
        if (this.mob.mode() == Majungasaurine.MODE_CROUCH) {
            this.mob.setMode(Majungasaurine.MODE_NONE);
        }
        this.mob.getNavigation().stop();
        this.mob.waterholeCooldown = 2400 + this.mob.getRandom().nextInt(1200);
        this.spot = null;
        this.water = null;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        this.ticks++;
        if (!this.crouched) {
            double d = this.mob.distanceToSqr(Vec3.atBottomCenterOf(this.spot));
            if (d < 2.5D * 2.5D || (d < 5.0D * 5.0D && this.mob.getNavigation().isDone())) {
                this.crouched = true;
                this.mob.getNavigation().stop();
                this.mob.setMode(Majungasaurine.MODE_CROUCH);
                this.mob.logAct("waterhole: crouches at the edge of the water");
            } else if (--this.repath <= 0) {
                this.repath = 40;
                this.mob.getNavigation().moveTo(this.spot.getX() + 0.5D, this.spot.getY(), this.spot.getZ() + 0.5D, 0.9D);
            }
            return;
        }
        this.mob.getNavigation().stop();
        // face the water (where they come to drink), the head on whoever comes
        double dx = this.water.getX() + 0.5D - this.mob.getX();
        double dz = this.water.getZ() + 0.5D - this.mob.getZ();
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        this.mob.setYRot(Mth.approachDegrees(this.mob.getYRot(), yaw, 4.0F));
        this.mob.setYBodyRot(this.mob.getYRot());
        if (this.ticks % 10 != 0) {
            return;
        }
        double warn = WARN * Math.max(0.6D, this.mob.getScale()) + this.mob.getBbWidth() * 0.5D;
        LivingEntity comer = null;
        double best = Double.MAX_VALUE;
        for (LivingEntity e : this.mob.level().getEntitiesOfClass(LivingEntity.class, this.mob.getBoundingBox().inflate(warn),
                e -> e != this.mob && e.isAlive() && this.intruder(e))) {
            double d = this.mob.distanceTo(e);
            if (d < best) {
                best = d;
                comer = e;
            }
        }
        if (comer == null) {
            return;
        }
        this.mob.getLookControl().setLookAt(comer, 30.0F, 30.0F);
        if (comer == this.warned && this.ticks - this.warnedAt < 160) {
            if (best < CLOSE * Math.max(0.6D, this.mob.getScale()) + this.mob.getBbWidth() * 0.5D + comer.getBbWidth() * 0.5D
                    && this.mob.canAttack(comer)) {
                this.mob.logAct(String.format("waterhole: the %s came on to %.1f blocks, drives it off",
                        comer.getType().toShortString(), best));
                this.mob.setTarget(comer);
            }
            return;
        }
        if (this.mob.threatCooldown <= 0) {
            this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "waterhole_threat");
            this.mob.warnSound();
            this.mob.threatCooldown = 100;
            this.warned = comer;
            this.warnedAt = this.ticks;
            this.mob.logAct(String.format("waterhole: warns the %s off with the dome at %.1f blocks",
                    comer.getType().toShortString(), best));
        }
    }

    /** What it warns off: a player, another grown meat eater, a grown herbivore at least half its size (the prey it
     *  hunts is left to the base's target goals). */
    private boolean intruder(LivingEntity e) {
        if (e instanceof Player p) {
            return !p.isCreative() && !p.isSpectator();
        }
        if (!(e instanceof DinosaurEntity d) || d.isBaby() || d instanceof Majungasaurine) {
            return false;
        }
        return CarcassStealGoal.eatsMeat(d) || d.getBbWidth() >= this.mob.getBbWidth() * 0.5F;
    }

    /** A dry standing spot on the bank next to the water, nearest the water first; or null. */
    private BlockPos edgeBy(BlockPos w) {
        for (int r = 1; r <= 4; r++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != r) {
                        continue;
                    }
                    for (int dy = -1; dy <= 2; dy++) {
                        BlockPos p = w.offset(dx, dy, dz);
                        if (!this.mob.level().getFluidState(p).is(FluidTags.WATER)
                                && this.mob.level().getBlockState(p.below()).isSolidRender(this.mob.level(), p.below())
                                && this.mob.level().getBlockState(p).getCollisionShape(this.mob.level(), p).isEmpty()
                                && this.mob.level().getBlockState(p.above()).getCollisionShape(this.mob.level(), p.above()).isEmpty()) {
                            return p;
                        }
                    }
                }
            }
        }
        return null;
    }
}
