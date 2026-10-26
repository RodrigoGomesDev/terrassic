package com.terrassic.entity;

import com.terrassic.entity.ai.FlightSteering;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/** Exercises production steering through wraparound, close targets, reversals and long cruising flights. */
public final class MovementRegression {
    private static void require(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        Vec3 position = Vec3.ZERO;
        float yaw = 179;
        Vec3 velocity = Vec3.directionFromRotation(0, yaw).scale(.35);
        double distance = 0;
        for (int tick = 0; tick < 10000; tick++) {
            Vec3 target = switch ((tick / 500) % 4) {
                case 0 -> position.add(.1, 20, -.1); // close/behind: never stop to spin
                case 1 -> position.add(-60, -20, 40);
                case 2 -> position.add(80, 0, -60);
                default -> position; // zero-length waypoint must still move forward
            };
            FlightSteering.Step step = FlightSteering.step(position, velocity, yaw, target, .6);
            require(Math.abs(Mth.wrapDegrees(step.yaw() - yaw)) <= FlightSteering.MAX_TURN + .001F,
                    "yaw snapped or wrapped through a full rotation");
            require(step.velocity().horizontalDistance() >= .25, "cruise stalled at a waypoint");
            require(step.velocity().horizontalDistance() <= .66, "unbounded flight acceleration");
            require(step.velocity().y >= -.141 && step.velocity().y <= .181, "unbounded vertical motion");
            require(Double.isFinite(step.velocity().lengthSqr()), "non-finite velocity");
            distance += step.velocity().length();
            position = position.add(step.velocity());
            velocity = step.velocity();
            yaw = step.yaw();
        }
        require(distance > 3000, "bird hovered instead of cruising");
        FlightSteering.Step wrap = FlightSteering.step(Vec3.ZERO, Vec3.ZERO, 179,
                Vec3.directionFromRotation(0, -179).scale(50), .6);
        require(Math.abs(wrap.yaw() - 181) < .1, "turn across -180/180 took the long way");
        System.out.println("PASS: 10,000 production flight steps, no stalls, bounded yaw/velocity and angle wraparound");
    }
}
