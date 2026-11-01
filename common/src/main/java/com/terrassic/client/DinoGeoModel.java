package com.terrassic.client;

import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;

/**
 * GeckoLib model shared by all dinosaurs.
 * <ul>
 *   <li>Texture depends on sex: textures/entity/&lt;id&gt;_male.png / _female.png</li>
 *   <li>Bone "male_display" is only shown on males, "female_display" only on females</li>
 *   <li>Bone "saddle" is only shown when the animal is saddled</li>
 *   <li>Bone "head" follows the look direction (handled by DefaultedEntityGeoModel)</li>
 * </ul>
 */
public class DinoGeoModel<T extends DinosaurEntity> extends DefaultedEntityGeoModel<T> {
    private final ResourceLocation maleTexture;
    private final ResourceLocation femaleTexture;
    /** The alpha's own coats (docs/ALFAS.md), for the species in entity/Alphas.SPECIES; null for the others. */
    private final ResourceLocation alphaMaleTexture;
    private final ResourceLocation alphaFemaleTexture;

    public DinoGeoModel(String speciesId) {
        super(Terrassic.id(speciesId), "head");
        this.maleTexture = Terrassic.id("textures/entity/" + speciesId + "_male.png");
        this.femaleTexture = Terrassic.id("textures/entity/" + speciesId + "_female.png");
        boolean alpha = com.terrassic.entity.Alphas.hasAlpha(speciesId);
        this.alphaMaleTexture = alpha ? Terrassic.id("textures/entity/" + speciesId + "_alpha_male.png") : null;
        this.alphaFemaleTexture = alpha ? Terrassic.id("textures/entity/" + speciesId + "_alpha_female.png") : null;
    }

    @Override
    public ResourceLocation getTextureResource(T animatable) {
        if (this.alphaMaleTexture != null && animatable.isAlpha()) {
            return animatable.isFemale() ? this.alphaFemaleTexture : this.alphaMaleTexture;
        }
        return animatable.isFemale() ? this.femaleTexture : this.maleTexture;
    }

    @Override
    public void setCustomAnimations(T animatable, long instanceId, AnimationState<T> animationState) {
        super.setCustomAnimations(animatable, instanceId, animationState);
        boolean female = animatable.isFemale();
        hide("male_display", female);
        hide("female_display", !female);
        hide("saddle", !animatable.isSaddled());
    }

    private void hide(String bone, boolean hidden) {
        GeoBone b = getAnimationProcessor().getBone(bone);
        if (b != null) {
            b.setHidden(hidden);
        }
    }
}
