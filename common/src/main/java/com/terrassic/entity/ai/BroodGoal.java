package com.terrassic.entity.ai;

import com.terrassic.block.DinoEggBlock;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * Brooding (docs/NINHOS.md): a wild, grown {@link DinosaurEntity#brooder()} with nothing else to do walks to a
 * dinosaur egg block within six blocks and sits by it for a few minutes, wings spread (the "brood" animation,
 * chosen by the entity while it sits next to eggs). While it sits there the eggs hatch much faster
 * ({@link DinosaurEntity#broodEggs()} runs for wild and tame animals alike). A tame one broods wherever its owner
 * tells it to sit.
 */
public class BroodGoal extends Goal {
    private final DinosaurEntity dino;
    private BlockPos egg;
    private int timer;

    public BroodGoal(DinosaurEntity dino) {
        this.dino = dino;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        if (this.dino.isTame() || this.dino.isBaby() || this.dino.isSleeping() || this.dino.getTarget() != null
                || this.dino.isVehicle() || this.dino.getRandom().nextInt(reducedTickDelay(200)) != 0) {
            return false;
        }
        this.egg = this.dino.nearestEgg(6);
        return this.egg != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.timer > 0 && this.dino.getTarget() == null && !this.dino.isVehicle()
                && this.dino.level().getBlockState(this.egg).getBlock() instanceof DinoEggBlock;
    }

    @Override
    public void start() {
        this.timer = 2400 + this.dino.getRandom().nextInt(2400);
        this.dino.getNavigation().moveTo(this.egg.getX() + 0.5D, this.egg.getY(), this.egg.getZ() + 0.5D, 1.0D);
    }

    @Override
    public void tick() {
        this.timer--;
        if (this.dino.isInSittingPose()) {
            return;
        }
        if (this.dino.blockPosition().distSqr(this.egg) <= 4.0D) {
            this.dino.getNavigation().stop();
            this.dino.setInSittingPose(true);
        } else if (this.dino.getNavigation().isDone()) {
            this.dino.getNavigation().moveTo(this.egg.getX() + 0.5D, this.egg.getY(), this.egg.getZ() + 0.5D, 1.0D);
        }
    }

    @Override
    public void stop() {
        this.timer = 0;
        if (!this.dino.isTame()) {
            this.dino.setInSittingPose(false);
        }
        this.egg = null;
    }
}
