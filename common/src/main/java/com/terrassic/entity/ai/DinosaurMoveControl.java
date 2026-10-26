package com.terrassic.entity.ai;

import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.control.MoveControl;

/** Keep vanilla walking, jumping and pathfinding, with gradual heading and acceleration. */
public class DinosaurMoveControl extends MoveControl {
    private float walkingSpeed;
    public DinosaurMoveControl(Mob mob) {
        super(mob);
    }

    @Override
    protected float rotlerp(float current, float target, float maximum) {
        float turn = Mth.clamp(12.0F / Math.max(1.0F, this.mob.getBbWidth()), 4.0F, 12.0F);
        return super.rotlerp(current, target, Math.min(maximum, turn));
    }

    @Override
    public void tick() {
        boolean walking = this.operation == Operation.MOVE_TO;
        super.tick();
        if (walking && this.mob.zza > 0.0F && this.mob.onGround() && !this.mob.isVehicle()) {
            this.walkingSpeed = Mth.lerp(0.25F, this.walkingSpeed, this.mob.getSpeed());
            this.mob.setSpeed(this.walkingSpeed);
        } else {
            // WAIT only clears the vanilla input, not getSpeed(). Never restore that stale forward input.
            this.walkingSpeed = 0;
        }
    }
}
