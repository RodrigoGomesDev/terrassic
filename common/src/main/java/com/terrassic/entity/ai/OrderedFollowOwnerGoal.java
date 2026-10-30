package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.ai.goal.FollowOwnerGoal;

/** The vanilla follow (with its teleport), quiet while the dinosaur was told to wander (v0.16, docs/ORDENS.md). */
public class OrderedFollowOwnerGoal extends FollowOwnerGoal {
    private final DinosaurEntity dino;

    public OrderedFollowOwnerGoal(DinosaurEntity dino, double speed, float start, float stop, boolean canFly) {
        super(dino, speed, start, stop, canFly);
        this.dino = dino;
    }

    @Override
    public boolean canUse() {
        return !this.dino.isWandering() && super.canUse();
    }

    @Override
    public boolean canContinueToUse() {
        return !this.dino.isWandering() && super.canContinueToUse();
    }
}
