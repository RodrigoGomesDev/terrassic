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
        ClientTickEvent.CLIENT_POST.register(mc -> amplitude = amplitude < 0.02F ? 0.0F : amplitude * 0.82F);
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
