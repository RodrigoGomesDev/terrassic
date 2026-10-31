package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.terrassic.entity.ThrownBola;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;

/** A bola in flight: the 3D model (item/bola_thrown) lying flat and spinning about three turns a second. */
public class BolaRenderer extends EntityRenderer<ThrownBola> {
    private final ItemRenderer itemRenderer;

    public BolaRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.itemRenderer = context.getItemRenderer();
    }

    @Override
    public void render(ThrownBola bola, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees((bola.tickCount + partialTick) * 54.0F));
        poseStack.scale(0.9F, 0.9F, 0.9F);
        WeaponPoses.BOLA = 0.5F;
        try {
            this.itemRenderer.renderStatic(bola.getItem(), ItemDisplayContext.NONE, packedLight, OverlayTexture.NO_OVERLAY,
                    poseStack, buffer, bola.level(), bola.getId());
        } finally {
            WeaponPoses.BOLA = 0.0F;
        }
        poseStack.popPose();
        super.render(bola, entityYaw, partialTick, poseStack, buffer, packedLight);
    }

    @Override
    public ResourceLocation getTextureLocation(ThrownBola bola) {
        return TextureAtlas.LOCATION_BLOCKS;
    }
}
