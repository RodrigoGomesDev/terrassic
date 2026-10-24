package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.terrassic.Terrassic;
import com.terrassic.leap.Meteor;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

/**
 * A meteor of the ritual: a burning rock drawn as a camera-facing sprite at full brightness (textures/entity/meteor.png,
 * tools/spritegen/leap_art.py), spinning slowly; its fire trail is made of particles by {@link Meteor} itself.
 */
public class MeteorRenderer extends EntityRenderer<Meteor> {
    private static final ResourceLocation TEXTURE = Terrassic.id("textures/entity/meteor.png");
    private static final RenderType RENDER_TYPE = RenderType.entityCutoutNoCull(TEXTURE);

    public MeteorRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.shadowRadius = 0.0F;
    }

    @Override
    protected int getBlockLightLevel(Meteor entity, BlockPos pos) {
        return 15;
    }

    @Override
    public void render(Meteor entity, float yaw, float partialTick, PoseStack poseStack, MultiBufferSource buffers, int light) {
        float s = 2.0F * entity.size();
        poseStack.pushPose();
        poseStack.translate(0.0F, 0.5F, 0.0F);
        poseStack.scale(s, s, s);
        poseStack.mulPose(this.entityRenderDispatcher.cameraOrientation());
        poseStack.mulPose(Axis.YP.rotationDegrees(180.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees((entity.tickCount + partialTick) * 12.0F));
        PoseStack.Pose pose = poseStack.last();
        Matrix4f m = pose.pose();
        Matrix3f n = pose.normal();
        VertexConsumer vc = buffers.getBuffer(RENDER_TYPE);
        vertex(vc, m, n, -0.5F, -0.5F, 0, 1);
        vertex(vc, m, n, 0.5F, -0.5F, 1, 1);
        vertex(vc, m, n, 0.5F, 0.5F, 1, 0);
        vertex(vc, m, n, -0.5F, 0.5F, 0, 0);
        poseStack.popPose();
        super.render(entity, yaw, partialTick, poseStack, buffers, light);
    }

    private static void vertex(VertexConsumer vc, Matrix4f m, Matrix3f n, float x, float y, int u, int v) {
        vc.vertex(m, x, y, 0.0F).color(255, 255, 255, 255).uv(u, v).overlayCoords(OverlayTexture.NO_OVERLAY)
                .uv2(LightTexture.FULL_BRIGHT).normal(n, 0.0F, 1.0F, 0.0F).endVertex();
    }

    @Override
    public ResourceLocation getTextureLocation(Meteor entity) {
        return TEXTURE;
    }
}
