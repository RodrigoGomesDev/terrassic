package com.terrassic.entity.ai;

import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/** Continuous cruising, independent of the parrot controller's stop-at-waypoint behaviour. */
public final class FlightSteering {
    public static final float MAX_TURN = 3.0F;

    private FlightSteering() { }

    public record Step(float yaw, Vec3 velocity) { }

    public static Step step(Vec3 position, Vec3 velocity, float yaw, Vec3 target, double flyingSpeed) {
        Vec3 delta = target.subtract(position);
        float wanted = delta.horizontalDistanceSqr() < 0.01D ? yaw
                : (float) (Mth.atan2(delta.z, delta.x) * Mth.RAD_TO_DEG) - 90.0F;
        float nextYaw = yaw + Mth.clamp(Mth.wrapDegrees(wanted - yaw), -MAX_TURN, MAX_TURN);
        double speed = Mth.clamp(flyingSpeed * 0.8D, 0.28D, 0.65D);
        double vertical = Mth.clamp(delta.y * 0.035D, -0.14D, 0.18D);
        Vec3 forward = Vec3.directionFromRotation(0, nextYaw).scale(speed);
        Vec3 desired = new Vec3(forward.x, vertical, forward.z);
        return new Step(nextYaw, velocity.add(desired.subtract(velocity).scale(0.12D)));
    }
}
