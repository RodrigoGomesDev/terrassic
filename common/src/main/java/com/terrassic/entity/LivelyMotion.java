package com.terrassic.entity;

import net.minecraft.util.Mth;

/**
 * Client only: the live motion layer laid over the baked animations (06/11/2026, from the study of how the Raxiores
 * T. rex moves, docs/estudos/ANIMACAO_RAXIORES.md). A baked loop cannot know that the animal is turning, so on its own
 * the tail stays glued behind the hips and the body turns like a door. Raxiores drives static poses with "followers"
 * (values that chase a target a fraction per tick) and a chain of points that trails the body in the world; this is
 * the same idea in our own form, three springs per animal:
 * <ul>
 *   <li>the TAIL: each of its four segments keeps part of its heading in the world when the body turns (inertia,
 *       growing to the tip), then a damped spring brings it back past the middle and it settles; the swing of each
 *       segment feeds the next, so a sharp turn sends a whip down the tail;</li>
 *   <li>the BANK: walking or running round a curve, the body leans into it and the neck looks into it, in proportion
 *       to the speed;</li>
 *   <li>the TURN RATE, smoothed, that the movement controller reads to play the step-round loops when the animal
 *       turns standing still (ApexTheropod#movementAnimation).</li>
 * </ul>
 * Signs: in game a + rotation round y swings the head to the animal's right and the tail tip to its left; a + roll
 * round z lifts its left side. Minecraft's body yaw grows when the animal turns right.
 */
public final class LivelyMotion {
    /** Share of the body's turn each tail segment keeps in the world (base to tip). */
    private static final float[] INERTIA = {0.26F, 0.36F, 0.45F, 0.52F, 0.58F, 0.63F};
    private static final float STIFF = 0.16F;
    private static final float DAMP = 0.30F;
    private static final float TAIL_MAX = 30.0F;

    /** Up to six tail segments (tail1..tail6, as many as the rig has). */
    private final float[] tail = new float[6];
    private final float[] tailO = new float[6];
    private final float[] vel = new float[6];
    private float bank;
    private float bankO;
    private float turnRate;
    private boolean started;
    /** 0 calm .. 1 out of breath: grows while it runs, fades over about half a minute. */
    private float exertion;
    private float breath;
    private float breathO;
    /** Feet on the ground (06/11, the study of Jurassic Saga's leg IK): blocks of ground under each foot relative to
     *  where the animal stands (negative = the foot hangs over a step down), followed smoothly. */
    private float footL;
    private float footR;
    private float footLO;
    private float footRO;
    /** Half the distance between the feet and the thigh + shin length, in model px: measured from the rig's bones by
     *  the model on its first frame (setLegs); 0 until then. */
    private float footSidePx;
    private float legPx = 50.0F;

    public void setLegs(float sidePx, float legPx) {
        this.footSidePx = sidePx;
        this.legPx = Math.max(8.0F, legPx);
    }

    public boolean hasLegs() {
        return this.footSidePx != 0.0F;      // measured (negative = a rig without legs: no feet layer)
    }

    public float legPx() {
        return this.legPx;
    }

    // 1.9.5, fluid steps (docs/estudos/12, Locomoção): the box climbs a step in one tick; the model now follows a damped
    // spring, so the body rises onto the block over a few ticks instead of jumping up with the box.
    private float stepOff;
    private float stepOffO;
    private float stepVel;
    private double lastY = Double.NaN;
    private boolean lastGround;

    /** How far below the box the model is drawn now (blocks, negative while it climbs). */
    public float stepOffset(float partial) {
        return Mth.lerp(partial, this.stepOffO, this.stepOff);
    }

    private void stepTick(DinosaurEntity e) {
        this.stepOffO = this.stepOff;
        double y = e.getY();
        if (!Double.isNaN(this.lastY) && e.onGround() && this.lastGround && !e.isVehicle()) {
            double dy = y - this.lastY;
            if (dy > 0.2D && dy < 2.1D) {
                this.stepOff -= (float) dy;     // the model stays where it was and catches up
            }
        }
        this.lastY = y;
        this.lastGround = e.onGround();
        float k = 0.14F / (float) Math.sqrt(Math.max(1.0F, e.getBbHeight()));
        this.stepVel += -this.stepOff * k - this.stepVel * 0.5F;
        this.stepOff += this.stepVel;
        if (Math.abs(this.stepOff) < 0.002F && Math.abs(this.stepVel) < 0.002F) {
            this.stepOff = 0.0F;
            this.stepVel = 0.0F;
        }
        this.stepOff = Mth.clamp(this.stepOff, -2.1F, 0.3F);
    }

    public void tick(DinosaurEntity e) {
        this.stepTick(e);
        float dyaw = Mth.wrapDegrees(e.yBodyRot - e.yBodyRotO);
        if (!this.started) {
            this.started = true;
            dyaw = 0.0F;
        }
        if (!e.isAlive() || e.isKnockedOut()) {
            dyaw = 0.0F;   // a body that has fallen does not swing its tail
        }
        this.turnRate += (dyaw - this.turnRate) * 0.35F;
        for (int i = 0; i < 6; i++) {
            this.tailO[i] = this.tail[i];
            this.tail[i] -= dyaw * INERTIA[i];
            this.vel[i] += -STIFF * this.tail[i] - DAMP * this.vel[i] + (i > 0 ? 0.22F * this.vel[i - 1] : 0.0F);
            this.tail[i] = Mth.clamp(this.tail[i] + this.vel[i], -TAIL_MAX, TAIL_MAX);
        }
        double dx = e.getX() - e.xo;
        double dz = e.getZ() - e.zo;
        float moving = (float) Mth.clamp(Math.sqrt(dx * dx + dz * dz) / (0.12D * Math.max(0.3F, e.getScale())), 0.0D, 1.0D);
        this.bankO = this.bank;
        float target = Mth.clamp(this.turnRate * 1.8F * moving, -10.0F, 10.0F);
        this.bank += (target - this.bank) * 0.18F;
        // the breath: a calm animal breathes every ~3 s (the baked idle does that); after a run it pants, fast and with
        // the mouth open, and calms down slowly; this layer only adds the panting on top
        float speed = (float) (Math.sqrt(dx * dx + dz * dz) / Math.max(0.3F, e.getScale()));
        if (speed > 0.16F) {
            this.exertion = Math.min(1.0F, this.exertion + 0.006F);
        } else {
            this.exertion = Math.max(0.0F, this.exertion - 0.0018F);
        }
        if (this.breath > 2.0F * (float) Math.PI) {
            this.breath -= 2.0F * (float) Math.PI;     // wrapped, with its previous value, so nothing jumps
        }
        this.breathO = this.breath;
        this.breath += (float) (2.0D * Math.PI / (60.0D - 40.0D * this.exertion));
        // the ground under each foot
        this.footLO = this.footL;
        this.footRO = this.footR;
        float gl = 0.0F;
        float gr = 0.0F;
        if (this.footSidePx > 0.0F && e.livelyBiped() && e.onGround() && e.isAlive() && !e.isKnockedOut() && !e.isInWater()
                && !e.isSleeping() && !e.isInSittingPose()) {
            double side = this.footSidePx / 16.0D * e.livelyModelScale() * e.getScale();
            double yaw = Math.toRadians(e.yBodyRot);
            double cx = Math.cos(yaw) * side;
            double cz = Math.sin(yaw) * side;
            gl = ground(e, e.getX() + cx, e.getZ() + cz);
            gr = ground(e, e.getX() - cx, e.getZ() - cz);
        }
        this.footL += (gl - this.footL) * 0.3F;
        this.footR += (gr - this.footR) * 0.3F;
    }

    /** The top of the ground under (x, z) relative to the animal's feet, -1.5 .. 1.2 blocks. */
    static float ground(DinosaurEntity e, double x, double z) {
        double y = e.getY();
        net.minecraft.world.level.Level level = e.level();
        for (int dy = 1; dy >= -2; dy--) {
            net.minecraft.core.BlockPos p = net.minecraft.core.BlockPos.containing(x, y + dy, z);
            net.minecraft.world.phys.shapes.VoxelShape shape = level.getBlockState(p).getCollisionShape(level, p);
            if (!shape.isEmpty()) {
                double top = p.getY() + shape.max(net.minecraft.core.Direction.Axis.Y);
                if (top <= y + 1.2D) {
                    return (float) Mth.clamp(top - y, -1.5D, 1.2D);
                }
            }
        }
        return -1.5F;
    }

    /** Blocks of ground under the left / right foot relative to the stance (smoothed). */
    public float footLeft(float partial) {
        return Mth.lerp(partial, this.footLO, this.footL);
    }

    public float footRight(float partial) {
        return Mth.lerp(partial, this.footRO, this.footR);
    }

    /** Panting amount (0 .. 1), eased. */
    public float exertion() {
        return this.exertion * this.exertion * (3.0F - 2.0F * this.exertion);
    }

    /** The breath phase (radians), interpolated. */
    public float breath(float partial) {
        return Mth.lerp(partial, this.breathO, this.breath);
    }

    /** Degrees of yaw to add to tail segment {@code i} (0 = the base). */
    public float tail(int i, float partial) {
        return Mth.lerp(partial, this.tailO[i], this.tail[i]);
    }

    /** Degrees of roll into the curve (negative while turning left: the left side goes down). */
    public float bank(float partial) {
        return Mth.lerp(partial, this.bankO, this.bank);
    }

    /** Degrees per tick the body is turning, smoothed (positive = to the right). */
    public float turnRate() {
        return this.turnRate;
    }
}
