package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

/**
 * The camera shake of a loud roar (one kick per wave of {@link RoarWaveParticle}): a quick shudder that dies out in a
 * few ticks, full within 8 blocks of the mouth and gone at 40. Applied with the hurt tilt
 * (mixin/client/GameRendererMixin). Client option "roar_shake" (config/terrassic-client.json) turns it off.
 */
public final class RoarShake {
    /** Strongest roll, in degrees, of a full-strength wave right at the mouth. */
    private static final float MAX_DEGREES = 2.2F;
    private static float amplitude;

    private RoarShake() {
    }

    static void init() {
        ClientTickEvent.CLIENT_POST.register(mc -> {
            amplitude = amplitude < 0.02F ? 0.0F : amplitude * 0.82F;
            alphaSteps(mc);
        });
    }

    /** Each alpha nearby: x and z last tick and the ground covered since its last footfall. Measured here and not
     *  with walkDist, which only the server moves (the client just interpolates other entities). */
    private static final java.util.Map<Integer, double[]> STRIDE = new java.util.HashMap<>();

    /** The alpha's footfalls (docs/ALFAS.md, the T. rex's "ground that shakes"): a light kick per step within about
     *  20 blocks, not for its own rider. Same switch as the roar ("roar_shake"). */
    private static void alphaSteps(Minecraft mc) {
        Entity camera = mc.getCameraEntity();
        if (mc.level == null || camera == null || mc.isPaused()) {
            return;
        }
        if (mc.level.getGameTime() % 200 == 0) {
            STRIDE.clear();
        }
        for (com.terrassic.entity.DinosaurEntity d : mc.level.getEntitiesOfClass(com.terrassic.entity.DinosaurEntity.class,
                camera.getBoundingBox().inflate(24.0D), e -> e.isAlpha() && !e.isBaby())) {
            double[] s = STRIDE.get(d.getId());
            if (s == null) {
                STRIDE.put(d.getId(), new double[] {d.getX(), d.getZ(), 0.0D});
                continue;
            }
            double step = Math.sqrt(Mth.square(d.getX() - s[0]) + Mth.square(d.getZ() - s[1]));
            s[0] = d.getX();
            s[1] = d.getZ();
            if (!d.onGround() || step > 4.0D) { // in the air, or a teleport
                s[2] = 0.0D;
                continue;
            }
            s[2] += step;
            double stride = Math.max(1.0D, d.getBbWidth() * 0.8D);
            if (s[2] < stride) {
                continue;
            }
            s[2] -= stride;
            if (camera.getVehicle() == d || !ClientConfig.flag("roar_shake")) {
                continue;
            }
            double dist = Math.sqrt(camera.distanceToSqr(d));
            float near = (float) Mth.clamp(1.0D - (dist - 6.0D) / 14.0D, 0.0D, 1.0D);
            amplitude = Math.min(MAX_DEGREES * 1.5F, amplitude + MAX_DEGREES * 0.3F * near);
        }
    }

    static void pulse(double x, double y, double z, float strength) {
        if (!ClientConfig.flag("roar_shake")) {
            return;
        }
        Entity camera = Minecraft.getInstance().getCameraEntity();
        if (camera == null) {
            return;
        }
        double d = Math.sqrt(camera.distanceToSqr(x, y, z));
        float near = (float) Mth.clamp(1.0D - (d - 8.0D) / 32.0D, 0.0D, 1.0D);
        amplitude = Math.min(MAX_DEGREES * 1.5F, amplitude + MAX_DEGREES * Math.min(1.0F, strength) * near);
    }

    /** A blow or a fall nearby (ModParticles.IMPACT): a shorter, harder jolt than the roar's, full within 6 blocks and gone
     *  at 30; not for the rider of the one that struck. */
    static void impact(double x, double y, double z, float strength) {
        if (!ClientConfig.flag("roar_shake")) {
            return;
        }
        Entity camera = Minecraft.getInstance().getCameraEntity();
        if (camera == null) {
            return;
        }
        double d = Math.sqrt(camera.distanceToSqr(x, y, z));
        float near = (float) Mth.clamp(1.0D - (d - 6.0D) / 24.0D, 0.0D, 1.0D);
        amplitude = Math.min(MAX_DEGREES * 1.6F, amplitude + MAX_DEGREES * 0.9F * Mth.clamp(strength, 0.0F, 1.5F) * near);
    }

    public static void apply(PoseStack poseStack, float partialTick) {
        if (amplitude <= 0.0F) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        float t = (mc.level != null ? mc.level.getGameTime() % 24000L : 0L) + partialTick;
        poseStack.mulPose(Axis.ZP.rotationDegrees(amplitude * Mth.sin(t * 2.9F)));
        poseStack.mulPose(Axis.XP.rotationDegrees(amplitude * 0.6F * Mth.sin(t * 3.7F + 1.3F)));
    }
}
