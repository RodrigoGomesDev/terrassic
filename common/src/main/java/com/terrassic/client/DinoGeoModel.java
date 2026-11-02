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
 *   <li>Bones "adult_l" and "adult_r" are hidden on babies (plumage the young did not have)</li>
 *   <li>The growth series of the Pachycephalosaurus: "adult_dome" is hidden on babies and "young_spikes" shown only on
 *       them; "adult_dome_male" / "adult_dome_female" carry the adult crown of each sex</li>
 *   <li>The Parasaurolophus' crest: "adult_crest" is hidden on babies and "young_crest" (the low dome a hatchling had,
 *       Farke et al. 2013) shown only on them</li>
 *   <li>The Triceratops' brow horns: "adult_horns" is hidden on babies and "young_horns" (short, curving back) shown
 *       only on them</li>
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
        // adult-only plumage (the Gallimimus' wing fans: the young had only down)
        hide("adult_l", animatable.isBaby());
        hide("adult_r", animatable.isBaby());
        // the Pachycephalosaurus grows its dome: the young are flat-headed and spiky (Horner & Goodwin 2009)
        boolean baby = animatable.isBaby();
        hide("adult_dome", baby);
        hide("adult_dome_male", baby || female);
        hide("adult_dome_female", baby || !female);
        hide("young_spikes", !baby);
        // the Parasaurolophus grows its crest: a year-old had only a low dome over the skull (Farke et al. 2013)
        hide("adult_crest", baby);
        hide("young_crest", !baby);
        // the Ankylosaurus grows its club: a juvenile Pinacosaurus had only a plain tail tip (Currie et al. 2011)
        hide("adult_club", baby);
        hide("young_tail", !baby);
        // the Triceratops' brow horns: a calf's are short stubs curving back (Horner & Goodwin 2006)
        hide("adult_horns", baby);
        hide("young_horns", !baby);
    }

    private void hide(String bone, boolean hidden) {
        CoreGeoBone b = getAnimationProcessor().getBone(bone);
        if (b != null) {
            b.setHidden(hidden);
        }
    }
}
