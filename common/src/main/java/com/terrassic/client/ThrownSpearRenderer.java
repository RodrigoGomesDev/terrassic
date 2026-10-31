package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.terrassic.entity.ThrownSpear;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemDisplayContext;

/** Renders a thrown spear as its item sprite, pointing along the flight direction. */
public class ThrownSpearRenderer extends EntityRenderer<ThrownSpear> {
    private final ItemRenderer itemRenderer;

    public ThrownSpearRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.itemRenderer = context.getItemRenderer();
    }

    @Override
    public void render(ThrownSpear spear, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        // same orientation as arrows: local +X = flight direction
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.lerp(partialTick, spear.yRotO, spear.getYRot()) - 90.0F));
        // the 3D spear stands upright in its model, tip up (v1.1.1, like the trident): lay it along +X
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTick, spear.xRotO, spear.getXRot()) - 90.0F));
        float shake = spear.shakeTime - partialTick;
        if (shake > 0.0F) {
            // it quivers where it sticks, like an arrow
            poseStack.mulPose(Axis.ZP.rotationDegrees(-Mth.sin(shake * 3.0F) * shake));
        }
        // the base of the head (model point 0, 16, 0; gen_resources._spear_held) on the entity, so a stuck spear has
        // its head in the block and the shaft out, as the trident; the item renderer shifts every model by -0.5
        poseStack.translate(0.5F, -0.5F, 0.5F);
        this.itemRenderer.renderStatic(spear.getRenderStack(), ItemDisplayContext.NONE, packedLight, OverlayTexture.NO_OVERLAY,
                poseStack, buffer, spear.level(), spear.getId());
        poseStack.popPose();
        super.render(spear, entityYaw, partialTick, poseStack, buffer, packedLight);
    }

    @Override
    public ResourceLocation getTextureLocation(ThrownSpear spear) {
        return TextureAtlas.LOCATION_BLOCKS;
    }
}
