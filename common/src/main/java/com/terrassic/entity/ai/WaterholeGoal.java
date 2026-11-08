package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The evening at the water (06/11/2026, the ecosystem): once a day, as the sun goes down, a wild grown herbivore walks
 * to the nearest water within 48 blocks and drinks; its herd follows it (FollowHerdGoal), so in the late afternoon the
 * herds of a valley gather at the same pools, and the predators that know it (the Deinosuchus in the water, a T. rex at
 * the edge) find them there.
 */
public class WaterholeGoal extends Goal {
    private static final int RANGE = 48;
    private final DinosaurEntity mob;
    private BlockPos water;
    private long doneDay = -1L;
    private int ticks;
    private int drinkLeft;

    public WaterholeGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean available() {
        return !this.mob.isTame() && !this.mob.isBaby() && !this.mob.isVehicle() && !this.mob.isSleeping() && !this.mob.isKnockedOut()
                && this.mob.getTarget() == null && this.mob.getLastHurtByMob() == null && this.mob.getMigrationTarget() == null;
    }

    @Override
    public boolean canUse() {
        long time = this.mob.level().getDayTime();
        long day = time / 24000L;
        long hour = time % 24000L;
        if (day == this.doneDay || hour < 10800L || hour > 12800L || !this.available() || this.mob.getRandom().nextInt(80) != 0) {
            return false;
        }
        this.doneDay = day;
        this.water = this.findWater();
        return this.water != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.water != null && this.available() && this.ticks < 1200 && (this.drinkLeft > 0 || !this.atWater());
    }

    @Override
    public void start() {
        this.ticks = 0;
        this.drinkLeft = 0;
        this.mob.getNavigation().moveTo(this.water.getX() + 0.5D, this.water.getY() + 1.0D, this.water.getZ() + 0.5D, 1.0D);
    }

    @Override
    public void stop() {
        this.water = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        this.ticks++;
        if (this.drinkLeft > 0) {
            this.drinkLeft--;
            this.mob.getNavigation().stop();
            this.mob.getLookControl().setLookAt(Vec3.atCenterOf(this.water));
            return;
        }
        if (this.atWater()) {
            this.drinkLeft = 90;
            this.mob.getNavigation().stop();
            this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "drink");
            return;
        }
        if (this.ticks % 40 == 0 && this.mob.getNavigation().isDone()) {
            this.mob.getNavigation().moveTo(this.water.getX() + 0.5D, this.water.getY() + 1.0D, this.water.getZ() + 0.5D, 1.0D);
        }
    }

    private boolean atWater() {
        double reach = 2.5D + this.mob.getBbWidth();
        return this.mob.distanceToSqr(Vec3.atCenterOf(this.water)) < reach * reach;
    }

    /** The nearest water surface, sampled in rings out to 48 blocks. */
    private BlockPos findWater() {
        return findWater(this.mob, RANGE);
    }

    /** The nearest water surface to the animal, sampled in rings out to range blocks, or null (also the
     *  Majungasaurus' waterhole, WaterholeGuardGoal). */
    public static BlockPos findWater(DinosaurEntity mob, int range) {
        BlockPos at = mob.blockPosition();
        for (int ring = 6; ring <= range; ring += 5) {
            int n = Math.max(8, ring);          // about one sample every 6 blocks round the ring: a small pool is not missed
            for (int i = 0; i < n; i++) {
                double a = (i + mob.getRandom().nextFloat()) / n * Math.PI * 2.0D;
                BlockPos col = at.offset((int) (Math.cos(a) * ring), 0, (int) (Math.sin(a) * ring));
                if (!mob.level().hasChunkAt(col)) {
                    continue;
                }
                BlockPos top = mob.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
                if (mob.level().getFluidState(top.below()).is(FluidTags.WATER)) {
                    return top.below();
                }
            }
        }
        return null;
    }
}
