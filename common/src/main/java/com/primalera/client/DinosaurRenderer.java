package com.primalera.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.primalera.entity.DinosaurEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * One renderer for every dinosaur. Model and animations are looked up by species id:
 *   geo/entity/&lt;id&gt;.geo.json, animations/entity/&lt;id&gt;.animation.json,
 *   textures/entity/&lt;id&gt;_male.png and _female.png
 */
public class DinosaurRenderer<T extends DinosaurEntity> extends GeoEntityRenderer<T> {
    private static final float BABY_SCALE = 0.5F;

    public DinosaurRenderer(EntityRendererProvider.Context context, String speciesId, float modelScale, float shadow) {
        super(context, new DinoGeoModel<>(speciesId));
        this.withScale(modelScale);
        this.shadowRadius = shadow;
    }

    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, T animatable,
                                    BakedGeoModel model, boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float baby = animatable.isBaby() ? BABY_SCALE : 1.0F;
        super.scaleModelForRender(widthScale * baby, heightScale * baby, poseStack, animatable, model, isReRender,
                partialTick, packedLight, packedOverlay);
    }
}
