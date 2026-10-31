package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.terrassic.Terrassic;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.ArrowRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.projectile.AbstractArrow;

/**
 * The mod's arrows and darts in flight and stuck in the ground: the vanilla arrow's crossed planes with a texture
 * of its own (textures/entity/&lt;name&gt;.png, drawn in tools/spritegen/armas.py) and a size (the dart is 60%).
 */
public class PrimitiveArrowRenderer<T extends AbstractArrow> extends ArrowRenderer<T> {
    private final ResourceLocation texture;
    private final float scale;

    public PrimitiveArrowRenderer(EntityRendererProvider.Context context, String name, float scale) {
        super(context);
        this.texture = new ResourceLocation(Terrassic.MOD_ID, "textures/entity/" + name + ".png");
        this.scale = scale;
    }

    @Override
    public void render(T arrow, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.scale(this.scale, this.scale, this.scale);
        super.render(arrow, entityYaw, partialTick, poseStack, buffer, packedLight);
        poseStack.popPose();
    }

    @Override
    public ResourceLocation getTextureLocation(T arrow) {
        return this.texture;
    }
}
