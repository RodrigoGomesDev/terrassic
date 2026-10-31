package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.terrassic.Terrassic;
import com.terrassic.entity.TranqDart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.ArrowRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;

/** The narcotic dart in flight and stuck in the ground: the vanilla arrow's crossed planes, shorter and thinner. */
public class TranqDartRenderer extends ArrowRenderer<TranqDart> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(Terrassic.MOD_ID, "textures/entity/tranq_dart.png");

    public TranqDartRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(TranqDart dart, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.scale(0.6F, 0.6F, 0.6F);
        super.render(dart, entityYaw, partialTick, poseStack, buffer, packedLight);
        poseStack.popPose();
    }

    @Override
    public ResourceLocation getTextureLocation(TranqDart dart) {
        return TEXTURE;
    }
}
