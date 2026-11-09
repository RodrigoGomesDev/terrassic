package com.terrassic.entity.ai;

import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
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
 *
 * <p>06/11/2026 (the ecosystem): the destination is chosen, not drawn: eight places in the season's half of the
 * compass are looked at and the one with the most to eat (and water near) wins. The one that chose it leads; the rest
 * walk in file, each behind the animal ahead of it, so a migrating herd reads as a column from afar. Big animals
 * beat trails: on grass they leave dirt paths now and then (mobGriefing), so the routes herds keep using show.
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
    /** Whether this one chose the destination (the others follow it in file). */
    private boolean leads;

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
            this.leads = false;
            return true;
        }
        // the Migration rule scales how often a herd thinks about it (0 = never, docs/REGRAS.md)
        int every = Rules.interval(reducedTickDelay(1200), Rule.MIGRATION, this.mob.level());
        if (every == Integer.MAX_VALUE || this.mob.getRandom().nextInt(every) != 0) {
            return false;
        }
        // the grass is gone and the gauge is low, or the season simply calls (once in twenty rolls, ~20 min)
        boolean scarce = this.mob.isHungry() && !this.mob.grazeNearby();
        if (!scarce && this.mob.getRandom().nextInt(20) != 0) {
            return false;
        }
        this.destination = this.pickDestination();
        this.leads = true;
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
        this.beatTrail();
        if (!this.leads && this.followAhead()) {
            return;
        }
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
            // only a path that gets there (moveTo also takes one that stops short, and the herd pushed in place)
            if (Reach.walk(this.mob, new Vec3(wp.getX() + 0.5D, wp.getY(), wp.getZ() + 0.5D), 1.0D)) {
                return;
            }
        }
        this.blocked++;
    }

    /** In file: behind the herd member just ahead of it on the way (nearer the destination), at a spacing. */
    private boolean followAhead() {
        Vec3 dest = Vec3.atBottomCenterOf(this.destination);
        double mine = this.mob.distanceToSqr(dest);
        DinosaurEntity ahead = null;
        double best = Double.MAX_VALUE;
        for (DinosaurEntity other : this.mob.level().getEntitiesOfClass(this.mob.getClass(), this.mob.getBoundingBox().inflate(20.0D),
                e -> e != this.mob && e.isAlive() && !e.isBaby() && this.destination.equals(e.getMigrationTarget()))) {
            double theirs = other.distanceToSqr(dest);
            double gap = this.mob.distanceToSqr(other);
            if (theirs < mine - 4.0D && gap < best) {
                ahead = other;
                best = gap;
            }
        }
        if (ahead == null) {
            return false;
        }
        double spacing = Math.max(3.5D, (this.mob.getBbWidth() + ahead.getBbWidth()) * 0.9D);
        if (best < spacing * spacing) {
            this.mob.getNavigation().stop();
            return true;
        }
        if (--this.repath <= 0 || this.mob.getNavigation().isDone()) {
            this.repath = adjustedTickDelay(20);
            Vec3 back = ahead.position().subtract(dest).normalize().scale(spacing);
            Vec3 at = ahead.position().add(back);
            if (!Reach.walkOr(this.mob, at, null, 1.0D)) {
                return false;     // no way in file from here: the waypoints take over
            }
        }
        return true;
    }

    /** Big animals on the move wear the turf into a path now and then (mobGriefing). */
    private void beatTrail() {
        if (this.mob.getBbWidth() < 1.4F || this.mob.getRandom().nextInt(50) != 0 || !this.mob.onGround()
                || !this.mob.level().getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_MOBGRIEFING)) {
            return;
        }
        BlockPos below = this.mob.blockPosition().below();
        if (this.mob.level().getBlockState(below).is(net.minecraft.world.level.block.Blocks.GRASS_BLOCK)
                && this.mob.level().getBlockState(below.above()).isAir()) {
            this.mob.level().setBlockAndUpdate(below, net.minecraft.world.level.block.Blocks.DIRT_PATH.defaultBlockState());
        }
    }

    /** 64 to 112 blocks away, in the season's half of the compass: of eight places looked at, the one with the most to
     *  eat around it (and water near) wins. */
    private BlockPos pickDestination() {
        long season = this.mob.level().getDayTime() / (24000L * 6L);
        long seed = season * 31L + this.mob.getType().toString().hashCode();
        seed ^= seed >>> 17;
        seed *= 0x9E3779B97F4A7C15L;
        float angle = (float) ((seed >>> 11) % 3600L) / 3600.0F * Mth.TWO_PI;
        BlockPos best = null;
        int bestScore = -1;
        for (int i = 0; i < 8; i++) {
            float a = angle + (this.mob.getRandom().nextFloat() - 0.5F) * 2.1F;
            double dist = 64.0D + this.mob.getRandom().nextInt(49);
            BlockPos pos = BlockPos.containing(this.mob.getX() + Mth.cos(a) * dist, 0.0D, this.mob.getZ() + Mth.sin(a) * dist);
            if (!this.mob.level().hasChunkAt(pos)) {
                continue;
            }
            BlockPos top = this.mob.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, pos);
            if (!this.mob.level().getFluidState(top.below()).isEmpty()) {
                continue;
            }
            int score = this.pasture(top);
            if (score > bestScore) {
                best = top;
                bestScore = score;
            }
        }
        return best;
    }

    /** Plants to eat on a 9 x 9 sample round a place, and a bonus for water within 12 blocks. */
    private int pasture(BlockPos at) {
        int food = 0;
        boolean water = false;
        for (int dx = -12; dx <= 12; dx += 3) {
            for (int dz = -12; dz <= 12; dz += 3) {
                BlockPos top = this.mob.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset(dx, 0, dz));
                net.minecraft.world.level.block.state.BlockState under = this.mob.level().getBlockState(top.below());
                net.minecraft.world.level.block.state.BlockState on = this.mob.level().getBlockState(top);
                if (!this.mob.level().getFluidState(top.below()).isEmpty() || !this.mob.level().getFluidState(top).isEmpty()) {
                    water = true;
                } else if (on.is(net.minecraft.world.level.block.Blocks.GRASS) || on.is(net.minecraft.world.level.block.Blocks.TALL_GRASS)
                        || on.is(net.minecraft.world.level.block.Blocks.FERN) || on.is(net.minecraft.world.level.block.Blocks.LARGE_FERN)) {
                    food += 2;
                } else if (under.is(net.minecraft.world.level.block.Blocks.GRASS_BLOCK)) {
                    food += 1;
                }
            }
        }
        return food + (water ? 20 : 0);
    }
}
