package com.terrassic.client;

import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
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

    public DinoGeoModel(String speciesId) {
        super(Terrassic.id(speciesId), "head");
        this.maleTexture = Terrassic.id("textures/entity/" + speciesId + "_male.png");
        this.femaleTexture = Terrassic.id("textures/entity/" + speciesId + "_female.png");
    }

    @Override
    public ResourceLocation getTextureResource(T animatable) {
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
        CoreGeoBone b = getAnimationProcessor().getBone(bone);
        if (b != null) {
            b.setHidden(hidden);
        }
    }
}
