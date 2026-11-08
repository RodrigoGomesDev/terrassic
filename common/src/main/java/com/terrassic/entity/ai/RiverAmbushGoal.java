package com.terrassic.entity.ai;

import com.terrassic.entity.Carcharodontosaurine;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;

import java.util.EnumSet;

/**
 * The Carcharodontosaurus' ambush at the river's edge (docs/estudos/13, "No jogo" 1; Stevens 2006, a hypothesis): hungry
 * and with nothing in sight, it walks to a dry spot at the edge of the water within 20 blocks (else, now and then, it
 * waits in the plants or the grass where it stands) and
 * lies in wait there, crouched and dead still ("ambush_crouch"), facing the bank the prey comes down to drink from.
 * While it waits, {@link Carcharodontosaurine#canAttack} lets it take only what comes within its reach; the target goals
 * of the base find the prey, and {@link Carcharodontosaurine#setTarget} turns the moment into the burst. A wait that
 * finds nothing ends after a minute.
 */
public class RiverAmbushGoal extends Goal {
    private static final int SEARCH = 20;
    private static final int MAX_WAIT = 1200;
    private static final int MAX_WALK = 400;

    private final Carcharodontosaurine mob;
    private BlockPos spot;
    private float facing;
    private boolean edge;
    private boolean crouched;
    private int ticks;
    private int repath;
    /** Hurt while it waits: it gets up. */
    private int hurtStamp;

    public RiverAmbushGoal(Carcharodontosaurine mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (!this.mob.ambushReady() || this.mob.getRandom().nextInt(reducedTickDelay(60)) != 0) {
            return false;
        }
        this.spot = this.findEdge();
        this.edge = this.spot != null;
        if (this.spot == null) {
            // no water near: now and then it lies in wait where it stands, in the plants or the grass
            Level level = this.mob.level();
            BlockPos at = this.mob.blockPosition();
            boolean plants = level.getBlockState(at).canBeReplaced() && !level.getBlockState(at).isAir();
            if ((plants || level.getBlockState(at.below()).is(BlockTags.DIRT)) && this.mob.getRandom().nextInt(4) == 0) {
                this.spot = at;
            }
        }
        return this.spot != null;
    }

    /** The nearest dry standing spot with water within two blocks of it, within SEARCH blocks. */
    private BlockPos findEdge() {
        Level level = this.mob.level();
        BlockPos at = this.mob.blockPosition();
        BlockPos best = null;
        double bestD = Double.MAX_VALUE;
        for (int dx = -SEARCH; dx <= SEARCH; dx++) {
            for (int dz = -SEARCH; dz <= SEARCH; dz++) {
                double d2 = dx * dx + dz * dz;
                if (d2 >= bestD || d2 > SEARCH * SEARCH) {
                    continue;
                }
                for (int dy = -3; dy <= 3; dy++) {
                    BlockPos p = at.offset(dx, dy, dz);
                    if (dry(level, p) && this.waterBeside(level, p) != null) {
                        best = p;
                        bestD = d2;
                        break;
                    }
                }
            }
        }
        return best;
    }

    private static boolean dry(Level level, BlockPos p) {
        return level.getBlockState(p.below()).isSolidRender(level, p.below()) && level.getBlockState(p).getCollisionShape(level, p).isEmpty()
                && level.getBlockState(p.above()).getCollisionShape(level, p.above()).isEmpty()
                && !level.getFluidState(p).is(FluidTags.WATER) && !level.getFluidState(p.below()).is(FluidTags.WATER);
    }

    /** The direction (dx, dz) to water within two blocks of p at its level or one below, or null. */
    private int[] waterBeside(Level level, BlockPos p) {
        for (int r = 1; r <= 2; r++) {
            for (int[] d : new int[][]{{r, 0}, {-r, 0}, {0, r}, {0, -r}}) {
                BlockPos q = p.offset(d[0], 0, d[1]);
                if (level.getFluidState(q).is(FluidTags.WATER) || level.getFluidState(q.below()).is(FluidTags.WATER)) {
                    return d;
                }
            }
        }
        return null;
    }

    @Override
    public void start() {
        this.ticks = 0;
        this.repath = 0;
        this.crouched = false;
        this.hurtStamp = this.mob.getLastHurtByMobTimestamp();
        this.mob.getNavigation().moveTo(this.spot.getX() + 0.5D, this.spot.getY(), this.spot.getZ() + 0.5D, 0.9D);
        this.mob.logAct(this.edge ? "ambush: goes to the river edge at " + this.spot.toShortString()
                : "ambush: lies in wait in the plants where it stands");
    }

    @Override
    public boolean canContinueToUse() {
        return this.mob.getTarget() == null && !this.mob.isTame() && !this.mob.isVehicle() && !this.mob.isSleeping()
                && !this.mob.isInSittingPose() && !this.mob.isKnockedOut() && !this.mob.isSated() && !this.mob.isDueling()
                && (this.crouched ? this.ticks < MAX_WAIT : this.ticks < MAX_WALK)
                && this.mob.getLastHurtByMobTimestamp() == this.hurtStamp
                && this.mob.mode() != Carcharodontosaurine.MODE_BURST;
    }

    @Override
    public void stop() {
        if (this.mob.mode() == Carcharodontosaurine.MODE_AMBUSH) {
            this.mob.setMode(Carcharodontosaurine.MODE_NONE);
            if (this.mob.getTarget() == null) {
                this.mob.logAct("ambush: gets up without prey (" + this.ticks / 20 + " s)");
            }
        }
        this.mob.ambushCooldown = Math.max(this.mob.ambushCooldown, 400 + this.mob.getRandom().nextInt(800));
        this.mob.getNavigation().stop();
        this.spot = null;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        this.ticks++;
        if (!this.crouched) {
            double d2 = this.mob.distanceToSqr(this.spot.getX() + 0.5D, this.spot.getY(), this.spot.getZ() + 0.5D);
            double near = 1.5D + this.mob.getBbWidth() * 0.5D;
            if (d2 < near * near || (this.mob.getNavigation().isDone() && d2 < 9.0D * near * near)) {
                this.crouch();
            } else if (++this.repath >= 40) {
                this.repath = 0;
                this.mob.getNavigation().moveTo(this.spot.getX() + 0.5D, this.spot.getY(), this.spot.getZ() + 0.5D, 0.9D);
            }
            return;
        }
        this.mob.getNavigation().stop();
        float y = Mth.approachDegrees(this.mob.getYRot(), this.facing, 4.0F);
        this.mob.setYRot(y);
        this.mob.setYBodyRot(y);
        this.mob.setYHeadRot(y);
    }

    /** Down into the crouch, facing away from the water (the bank the prey comes down to). */
    private void crouch() {
        this.crouched = true;
        this.ticks = 0;
        this.mob.getNavigation().stop();
        int[] w = this.edge ? this.waterBeside(this.mob.level(), this.spot) : null;
        if (w == null) {
            w = this.edge ? this.waterBeside(this.mob.level(), this.mob.blockPosition()) : null;
        }
        this.facing = w == null ? this.mob.getYRot() : (float) (Mth.atan2(-w[1], -w[0]) * Mth.RAD_TO_DEG) - 90.0F;
        this.mob.setMode(Carcharodontosaurine.MODE_AMBUSH);
        this.mob.logAct(this.edge ? "ambush: crouches at the river edge, waits" : "ambush: crouches in the plants, waits");
    }
}
