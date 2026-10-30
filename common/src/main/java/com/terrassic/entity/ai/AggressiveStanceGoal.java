package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;

/** A tame dinosaur in the aggressive stance goes for the monsters and wild dinosaurs near it (docs/ORDENS.md). */
public class AggressiveStanceGoal extends NearestAttackableTargetGoal<LivingEntity> {
    private final DinosaurEntity dino;

    public AggressiveStanceGoal(DinosaurEntity dino) {
        super(dino, LivingEntity.class, 10, true, false, dino::provokesAggressive);
        this.dino = dino;
    }

    @Override
    public boolean canUse() {
        return this.dino.huntsInAggressiveStance() && super.canUse();
    }

    @Override
    public boolean canContinueToUse() {
        return this.dino.huntsInAggressiveStance() && super.canContinueToUse();
    }
}
