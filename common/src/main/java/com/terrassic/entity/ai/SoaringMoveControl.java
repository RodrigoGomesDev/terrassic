package com.terrassic.entity.ai;

import com.terrassic.entity.FlyingDinosaur;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;

/** SoarGoal owns cruising; ordinary flying navigation still handles owner following, combat and juveniles. */
public class SoaringMoveControl extends FlyingMoveControl {
    private final FlyingDinosaur bird;

    public SoaringMoveControl(FlyingDinosaur bird) {
        super(bird, 10, false);
        this.bird = bird;
    }

    @Override
    public void tick() {
        if (this.bird.isKnockedOut()) {
            this.operation = Operation.WAIT;
            this.bird.setNoGravity(false);
            this.bird.setZza(0.0F);
            this.bird.setYya(0.0F);
            return;
        }
        if (this.bird.isCruising()) {
            this.bird.setNoGravity(true);
            this.bird.setZza(0.0F);
            this.bird.setYya(0.0F);
            return;
        }
        super.tick();
    }

    @Override
    protected float rotlerp(float current, float target, float maximum) {
        return super.rotlerp(current, target, Math.min(maximum, 8.0F));
    }
}
