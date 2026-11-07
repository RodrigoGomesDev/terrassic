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
        // 1.9.5 (docs/estudos/12): it only lies down where it is safe (a herbivore with no predator near, a predator
        // that is not starving)
        return this.mob.getRandom().nextInt(reducedTickDelay(120)) == 0 && (OLD || this.mob.safeToSleep());
    }

    @Override
    public boolean canContinueToUse() {
        if (!OLD && this.mob.tickCount % 10 == 0 && this.mob.wokenByThreat()) {
            return false;                   // a hunter close by: it wakes
        }
        return !this.mob.isTame() && this.mob.isSleepTime() && this.mob.getTarget() == null && !this.mob.isVehicle()
                && !this.mob.isInWaterOrBubble() && this.mob.getLastHurtByMob() == null;
    }

    /** Test only (BehaviorTest "night"): TERRASSIC_OLD_SLEEP=1 brings back the 1.9.1 sleep to compare. */
    public static final boolean OLD = "1".equals(System.getenv("TERRASSIC_OLD_SLEEP"));

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
