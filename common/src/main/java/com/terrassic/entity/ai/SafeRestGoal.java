package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * 1.9.5, the night that makes sense (docs/estudos/12_ECOSSISTEMA_ARK.md): in its sleeping hours a wild herbivore that
 * is not safe where it stands (a predator near, awake or asleep) walks off away from it before it lies down; its herd
 * follows it (FollowHerdGoal), so the herd beds down away from the hunters instead of beside them.
 */
public class SafeRestGoal extends Goal {
    private final DinosaurEntity mob;
    private int ticks;

    public SafeRestGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (DinoSleepGoal.OLD || this.mob.isTame() || this.mob.isBaby() || this.mob.isSleeping() || this.mob.getTarget() != null
                || this.mob.isVehicle() || !this.mob.isSleepTime() || this.mob.tickCount % 40 != 0 || this.mob.safeToSleep()) {
            return false;
        }
        return this.moveAway();
    }

    private boolean moveAway() {
        DinosaurEntity p = this.mob.nearestPredator(34.0D, false);
        if (p == null) {
            return false;
        }
        Vec3 away = DefaultRandomPos.getPosAway(this.mob, 28, 7, p.position());
        return away != null && this.mob.getNavigation().moveTo(away.x, away.y, away.z, 1.1D);
    }

    @Override
    public void start() {
        this.ticks = 0;
    }

    @Override
    public boolean canContinueToUse() {
        return ++this.ticks < 400 && !this.mob.getNavigation().isDone() && this.mob.getTarget() == null && !this.mob.isSleeping();
    }

    @Override
    public void stop() {
        this.mob.getNavigation().stop();
    }
}
