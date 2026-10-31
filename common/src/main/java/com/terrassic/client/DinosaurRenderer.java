package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * One renderer for every dinosaur. Model and animations are looked up by species id:
 *   geo/entity/&lt;id&gt;.geo.json, animations/entity/&lt;id&gt;.animation.json,
 *   textures/entity/&lt;id&gt;_male.png and _female.png
 */
public class DinosaurRenderer<T extends DinosaurEntity> extends GeoEntityRenderer<T> {
    /** How far from the player's centre the left shoulder is (blocks). */
    private static final double SHOULDER_SIDE = 0.37D;

    public DinosaurRenderer(EntityRendererProvider.Context context, String speciesId, float modelScale, float shadow) {
        super(context, new DinoGeoModel<>(speciesId));
        this.withScale(modelScale);
        this.shadowRadius = shadow;
        this.addRenderLayer(new RiftLayer<>(this));  // v0.9: creatures of the Rift glow with amber cracks
    }

    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, T animatable,
                                    BakedGeoModel model, boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float baby = animatable.getScale();
        super.scaleModelForRender(widthScale * baby, heightScale * baby, poseStack, animatable, model, isReRender,
                partialTick, packedLight, packedOverlay);
    }

    /** A flyer that tilts in flight pitches and banks the whole body about its saddle (FlyingDinosaur#flightPitch). The
     *  model is already scaled here and faces -Z, so the pivot is in model units. */
    @Override
    protected void applyRotations(T animatable, PoseStack poseStack, float ageInTicks, float rotationYaw, float partialTick) {
        super.applyRotations(animatable, poseStack, ageInTicks, rotationYaw, partialTick);
        if (animatable instanceof FlyingDinosaur flyer && animatable.deathTime <= 0) {
            float pitch = flyer.flightPitch(partialTick);
            float roll = flyer.flightRoll(partialTick);
            if (Math.abs(pitch) > 0.05F || Math.abs(roll) > 0.05F) {
                float size = animatable.getScale();
                double up = flyer.tiltPivotHeight() / (this.scaleHeight * size);
                double back = flyer.tiltPivotForward() / (this.scaleWidth * size);
                poseStack.translate(0.0D, up, -back);
                poseStack.mulPose(Axis.XP.rotationDegrees(pitch));
                poseStack.mulPose(Axis.ZP.rotationDegrees(roll));
                poseStack.translate(0.0D, -up, back);
            }
        }
    }

    /** Species with their own death animation fall in it; no vanilla tipping over on top. */
    @Override
    protected float getDeathMaxRotation(T animatable) {
        return animatable.hasDeathAnimation() ? 0.0F : super.getDeathMaxRotation(animatable);
    }

    /** A perched animal rides centred on the player; draw it on the left shoulder instead. */
    @Override
    public Vec3 getRenderOffset(T entity, float partialTick) {
        Vec3 offset = super.getRenderOffset(entity, partialTick);
        if (entity.isPerched() && entity.getVehicle() instanceof Player owner) {
            float yaw = Mth.rotLerp(partialTick, owner.yBodyRotO, owner.yBodyRot) * Mth.DEG_TO_RAD;
            offset = offset.add(Mth.cos(yaw) * SHOULDER_SIDE, -0.05D, Mth.sin(yaw) * SHOULDER_SIDE);
        }
        return offset;
    }
}
