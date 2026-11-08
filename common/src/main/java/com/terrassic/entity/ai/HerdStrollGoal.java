package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;

/**
 * 1.10.1 (docs/estudos/12, section 6): the idle wander, but only for the leader of a herd (or one alone). A follower does
 * not pick its own random spot: it goes where its leader goes (HerdMoveGoal), so the herd moves as one.
 */
public class HerdStrollGoal extends WaterAvoidingRandomStrollGoal {
    private final DinosaurEntity dino;

    public HerdStrollGoal(DinosaurEntity mob, double speed) {
        super(mob, speed);
        this.dino = mob;
    }

    @Override
    public boolean canUse() {
        if (this.dino.herdFollower()) {
            return false;
        }
        // a herd's leader wanders half as often: the whole group goes with it, a restless one drags it about
        if (!com.terrassic.entity.Behaviour.oldHerd && this.dino.herdSpecies() && !this.dino.isTame() && this.dino.getRandom().nextBoolean()) {
            return false;
        }
        return super.canUse();
    }

    @Override
    public boolean canContinueToUse() {
        return !this.dino.herdFollower() && super.canContinueToUse();
    }
}
