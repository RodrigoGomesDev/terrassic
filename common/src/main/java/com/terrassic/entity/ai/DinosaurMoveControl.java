package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.control.MoveControl;

/** Keep vanilla walking, jumping and pathfinding, with gradual heading and acceleration. */
public class DinosaurMoveControl extends MoveControl {
    /** Off the heading by more than this, a pivoting animal stops and turns on the spot before it walks on. */
    private static final float PIVOT_ANGLE = 50.0F;
    private final boolean pivots;
    private float walkingSpeed;

    public DinosaurMoveControl(Mob mob) {
        this(mob, false);
    }

    /**
     * @param pivots always turn on the spot towards a waypoint well off its heading. Since v0.11 every land animal
     *               wider than a block does it anyway ({@link DinosaurEntity#pivotsToTurn()}): at the slow turn rate
     *               of a wide animal a waypoint beside or behind it sits inside its turning circle, and walking while
     *               turning it would circle it for ever (29/10 tests: stairs down, the bite that walked away).
     */
    public DinosaurMoveControl(Mob mob, boolean pivots) {
        super(mob);
        this.pivots = pivots;
    }

    @Override
    protected float rotlerp(float current, float target, float maximum) {
        float turn = Mth.clamp(12.0F / Math.max(1.0F, this.mob.getBbWidth()), 4.0F, 12.0F);
        return super.rotlerp(current, target, Math.min(maximum, turn));
    }

    @Override
    public void tick() {
        boolean walking = this.operation == Operation.MOVE_TO;
        double dx = this.wantedX - this.mob.getX();
        double dz = this.wantedZ - this.mob.getZ();
        super.tick();
        // on its feet only: afloat the path's first node is the block it is in, the heading to it flips every tick and it
        // spun on the spot (rc2 swim test)
        boolean pivots = this.pivots || this.mob instanceof DinosaurEntity dino && dino.pivotsToTurn();
        if (walking && pivots && this.mob.onGround() && !this.mob.isInWater() && !this.mob.isVehicle() && dx * dx + dz * dz > 0.0625D) {
            float heading = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
            if (Math.abs(Mth.wrapDegrees(heading - this.mob.getYRot())) > PIVOT_ANGLE) {
                this.walkingSpeed = 0;
                this.mob.setSpeed(0.0F);
                this.mob.setZza(0.0F);
                return;
            }
        }
        if (walking && this.mob.zza > 0.0F && this.mob.onGround() && !this.mob.isVehicle()) {
            this.walkingSpeed = Mth.lerp(0.25F, this.walkingSpeed, this.mob.getSpeed());
            this.mob.setSpeed(this.walkingSpeed);
        } else {
            // WAIT only clears the vanilla input, not getSpeed(). Never restore that stale forward input.
            this.walkingSpeed = 0;
        }
    }
}
