package com.terrassic.entity.ai;

import java.util.EnumSet;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.Animal;

/**
 * The vanilla breed goal, sized for dinosaurs (1.8, found in the behaviour test): two animals in love walk to each other
 * and mate once they have been together for three seconds. Vanilla mates them only with their centres closer than 3
 * blocks, which two big animals pushing against each other rarely reach (two Deinosuchus in love stood 3.4 blocks apart
 * for a minute); here the distance and the search range grow with the animal's width.
 */
public class DinoBreedGoal extends Goal {
    private final Animal animal;
    private final double speed;
    private Animal partner;
    private int loveTime;

    public DinoBreedGoal(Animal animal, double speed) {
        this.animal = animal;
        this.speed = speed;
        this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
    }

    private double reach() {
        return 3.0D + this.animal.getBbWidth();
    }

    @Override
    public boolean canUse() {
        if (!this.animal.isInLove()) {
            return false;
        }
        this.partner = this.freePartner();
        return this.partner != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.partner != null && this.partner.isAlive() && this.partner.isInLove() && this.loveTime < 60;
    }

    @Override
    public void stop() {
        this.partner = null;
        this.loveTime = 0;
    }

    @Override
    public void tick() {
        this.animal.getLookControl().setLookAt(this.partner, 10.0F, this.animal.getMaxHeadXRot());
        this.animal.getNavigation().moveTo(this.partner, this.speed);
        this.loveTime++;
        double reach = this.reach();
        if (this.loveTime >= this.adjustedTickDelay(60) && this.animal.distanceToSqr(this.partner) < reach * reach
                && this.animal.level() instanceof ServerLevel level) {
            this.animal.spawnChildFromBreeding(level, this.partner);
        }
    }

    private Animal freePartner() {
        // a plain search by distance: the vanilla targeting conditions scale the range by how visible the other is
        // (water, a saddle cloth...) and missed a partner three blocks away for twenty seconds
        double range = Math.max(8.0D, this.animal.getBbWidth() * 3.0D);
        double best = range * range;
        Animal found = null;
        for (Animal other : this.animal.level().getEntitiesOfClass(this.animal.getClass(), this.animal.getBoundingBox().inflate(range),
                o -> o != this.animal && o.isAlive())) {
            double d = this.animal.distanceToSqr(other);
            if (d < best && this.animal.canMate(other)) {
                found = other;
                best = d;
            }
        }
        return found;
    }
}
