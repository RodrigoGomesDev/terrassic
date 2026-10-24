package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * Sleep (docs/FOME_E_SONO.md): a wild animal with nothing to do lies down through its resting hours (night for most,
 * day for the nocturnal species) and wakes when hurt, when its hours end, or when a target shows up.
 */
public class DinoSleepGoal extends Goal {
    private final DinosaurEntity mob;

    public DinoSleepGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        if (this.mob.isTame() || !this.mob.isSleepTime() || this.mob.getTarget() != null || this.mob.isVehicle()
                || this.mob.isPassenger() || this.mob.isInWaterOrBubble() || this.mob.getLastHurtByMob() != null) {
            return false;
        }
        return this.mob.getRandom().nextInt(reducedTickDelay(120)) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return !this.mob.isTame() && this.mob.isSleepTime() && this.mob.getTarget() == null && !this.mob.isVehicle()
                && !this.mob.isInWaterOrBubble() && this.mob.getLastHurtByMob() == null;
    }

    @Override
    public void start() {
        this.mob.getNavigation().stop();
        this.mob.setSleeping(true);
    }

    @Override
    public void stop() {
        this.mob.setSleeping(false);
    }

    @Override
    public void tick() {
        this.mob.getNavigation().stop();
        this.mob.setDeltaMovement(this.mob.getDeltaMovement().multiply(0.0D, 1.0D, 0.0D));
    }
}
