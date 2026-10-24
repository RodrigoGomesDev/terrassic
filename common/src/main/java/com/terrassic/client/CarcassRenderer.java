package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.terrassic.Terrassic;
import com.terrassic.entity.CarcassEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * A carcass is drawn with the dead species' own model and texture (by sex), frozen in its knocked_out pose, at the
 * species' render scale (TerrassicClient.MODEL_SCALES) times the animal's own scale (babies).
 */
public class CarcassRenderer extends GeoEntityRenderer<CarcassEntity> {
    public CarcassRenderer(EntityRendererProvider.Context context) {
        super(context, new CarcassModel());
        this.shadowRadius = 1.0F;
    }

    @Override
    public void render(CarcassEntity entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        this.shadowRadius = entity.getBbWidth() * 0.5F;
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
    }

    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, CarcassEntity animatable,
                                    BakedGeoModel model, boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float scale = TerrassicClient.MODEL_SCALES.getOrDefault(animatable.speciesId(), 1.0F) * animatable.getModelScale();
        super.scaleModelForRender(widthScale * scale, heightScale * scale, poseStack, animatable, model, isReRender,
                partialTick, packedLight, packedOverlay);
    }

    /** The species' assets looked up by id, like DinoGeoModel does for the living animal. */
    static class CarcassModel extends GeoModel<CarcassEntity> {
        @Override
        public ResourceLocation getModelResource(CarcassEntity carcass) {
            return Terrassic.id("geo/entity/" + carcass.speciesId() + ".geo.json");
        }

        @Override
        public ResourceLocation getTextureResource(CarcassEntity carcass) {
            return Terrassic.id("textures/entity/" + carcass.speciesId() + (carcass.isFemale() ? "_female.png" : "_male.png"));
        }

        @Override
        public ResourceLocation getAnimationResource(CarcassEntity carcass) {
            return Terrassic.id("animations/entity/" + carcass.speciesId() + ".animation.json");
        }

        @Override
        public void setCustomAnimations(CarcassEntity carcass, long instanceId, AnimationState<CarcassEntity> animationState) {
            super.setCustomAnimations(carcass, instanceId, animationState);
            boolean female = carcass.isFemale();
            hide("male_display", female);
            hide("female_display", !female);
            hide("saddle", true);
        }

        private void hide(String bone, boolean hidden) {
            CoreGeoBone b = getAnimationProcessor().getBone(bone);
            if (b != null) {
                b.setHidden(hidden);
            }
        }
    }
}
