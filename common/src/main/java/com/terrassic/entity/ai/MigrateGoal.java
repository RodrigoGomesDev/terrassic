package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Migration (docs/MIGRACAO.md): a wild grown herbivore that finds no grazing while hungry, or simply now and then,
 * leads its herd 64 to 96 blocks away. The direction is the season's: it comes from the world day and the species,
 * so every herd of the species in the world drifts the same way for six days and then another way. When one
 * animal sets off, the wild adults of its species within 24 blocks are given the same destination and set off
 * too; the babies follow their parents. The walk is done in waypoints of twelve blocks along the direction
 * (the path finder does not see that far), bending left or right when the way is blocked, and gives up after
 * five blocked tries or three minutes.
 */
public class MigrateGoal extends Goal {
    private static final double HERD = 24.0D;
    private static final int STEP = 12;
    private static final int MAX_TICKS = 3600;
    private final DinosaurEntity mob;
    private BlockPos destination;
    private int ticks;
    private int blocked;
    private int repath;

    public MigrateGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (this.mob.isTame() || this.mob.isBaby() || this.mob.isVehicle() || this.mob.isSleeping() || this.mob.getTarget() != null
                || this.mob.getLastHurtByMob() != null) {
            return false;
        }
        if (this.mob.getMigrationTarget() != null) {
            this.destination = this.mob.getMigrationTarget();
            return true;
        }
        if (this.mob.getRandom().nextInt(reducedTickDelay(1200)) != 0) {
            return false;
        }
        // the grass is gone and the gauge is low, or the season simply calls (once in twenty rolls, ~20 min)
        boolean scarce = this.mob.isHungry() && !this.mob.grazeNearby();
        if (!scarce && this.mob.getRandom().nextInt(20) != 0) {
            return false;
        }
        this.destination = this.pickDestination();
        return this.destination != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.destination != null && this.ticks < MAX_TICKS && this.blocked < 5 && !this.mob.isSleeping()
                && this.mob.getTarget() == null && !this.mob.isVehicle() && this.mob.getLastHurtByMob() == null
                && this.mob.distanceToSqr(Vec3.atBottomCenterOf(this.destination)) > 36.0D;
    }

    @Override
    public void start() {
        this.ticks = 0;
        this.blocked = 0;
        this.repath = 0;
        this.mob.setMigrationTarget(this.destination);
        // the herd sets off together
        for (DinosaurEntity other : this.mob.level().getEntitiesOfClass(this.mob.getClass(), this.mob.getBoundingBox().inflate(HERD),
                e -> e != this.mob && !e.isTame() && !e.isBaby() && e.getMigrationTarget() == null)) {
            other.setMigrationTarget(this.destination);
        }
    }

    @Override
    public void stop() {
        this.mob.setMigrationTarget(null);
        this.destination = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        this.ticks++;
        if (--this.repath > 0 && !this.mob.getNavigation().isDone()) {
            return;
        }
        this.repath = adjustedTickDelay(40);
        double dx = this.destination.getX() + 0.5D - this.mob.getX();
        double dz = this.destination.getZ() + 0.5D - this.mob.getZ();
        double dist = Math.sqrt(dx * dx + dz * dz);
        if (dist < 1.0E-3D) {
            return;
        }
        // a waypoint a dozen blocks ahead, bending aside when the straight way has no path
        for (int attempt = 0; attempt < 3; attempt++) {
            double bend = attempt == 0 ? 0.0D : (attempt == 1 ? 0.7D : -0.7D);
            double cos = Math.cos(bend);
            double sin = Math.sin(bend);
            double step = Math.min(STEP, dist);
            double wx = this.mob.getX() + (dx * cos - dz * sin) / dist * step;
            double wz = this.mob.getZ() + (dx * sin + dz * cos) / dist * step;
            BlockPos wp = this.mob.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(wx, 0.0D, wz));
            if (this.mob.getNavigation().moveTo(wp.getX() + 0.5D, wp.getY(), wp.getZ() + 0.5D, 1.0D)) {
                return;
            }
        }
        this.blocked++;
    }

    /** 64 to 96 blocks away, in the direction of the season. */
    private BlockPos pickDestination() {
        long season = this.mob.level().getDayTime() / (24000L * 6L);
        long seed = season * 31L + this.mob.getType().toString().hashCode();
        seed ^= seed >>> 17;
        seed *= 0x9E3779B97F4A7C15L;
        float angle = (float) ((seed >>> 11) % 3600L) / 3600.0F * Mth.TWO_PI;
        double dist = 64.0D + this.mob.getRandom().nextInt(33);
        double x = this.mob.getX() + Mth.cos(angle) * dist;
        double z = this.mob.getZ() + Mth.sin(angle) * dist;
        BlockPos pos = BlockPos.containing(x, 0.0D, z);
        if (!this.mob.level().hasChunkAt(pos)) {
            return null;
        }
        return this.mob.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, pos);
    }
}
