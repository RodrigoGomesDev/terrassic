package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

/**
 * Creatures "of the Rift" (v0.9; ROADMAP "Anomalias da Fenda": "olhos e rachaduras de âmbar"): the model drawn a
 * second time with glowing amber cracks (textures/entity/rift_overlay.png, tools/spritegen/leap_art.py), additive and
 * at full brightness, slowly pulsing. The overlay is one texture for every species: the cracks follow each model's
 * own UV layout, so no species needs its own art and a remodelled species keeps working.
 */
public class RiftLayer<T extends DinosaurEntity> extends GeoRenderLayer<T> {
    private static final ResourceLocation OVERLAY = Terrassic.id("textures/entity/rift_overlay.png");

    public RiftLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    @Override
    public void render(PoseStack poseStack, T animatable, BakedGeoModel model, RenderType renderType, MultiBufferSource buffers,
                       VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        if (!animatable.isRift() || animatable.isInvisible()) {
            return;
        }
        float pulse = 0.6F + 0.4F * Mth.sin((animatable.tickCount + partialTick) * 0.12F + animatable.getId());
        RenderType glow = RenderType.eyes(OVERLAY);
        this.getRenderer().reRender(model, poseStack, buffers, animatable, glow, buffers.getBuffer(glow), partialTick,
                LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, pulse, pulse, pulse, 1.0F);
    }
}
