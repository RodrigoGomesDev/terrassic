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
    private static final float[] INERTIA = {0.30F, 0.42F, 0.52F, 0.60F};
    private static final float STIFF = 0.16F;
    private static final float DAMP = 0.30F;
    private static final float TAIL_MAX = 30.0F;

    private final float[] tail = new float[4];
    private final float[] tailO = new float[4];
    private final float[] vel = new float[4];
    private float bank;
    private float bankO;
    private float turnRate;
    private boolean started;
    /** 0 calm .. 1 out of breath: grows while it runs, fades over about half a minute. */
    private float exertion;
    private float breath;
    private float breathO;

    public void tick(DinosaurEntity e) {
        float dyaw = Mth.wrapDegrees(e.yBodyRot - e.yBodyRotO);
        if (!this.started) {
            this.started = true;
            dyaw = 0.0F;
        }
        if (!e.isAlive() || e.isKnockedOut()) {
            dyaw = 0.0F;   // a body that has fallen does not swing its tail
        }
        this.turnRate += (dyaw - this.turnRate) * 0.35F;
        for (int i = 0; i < 4; i++) {
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
