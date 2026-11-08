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
 *   <li>Bones "adult_l" and "adult_r" are hidden on babies (plumage the young did not have)</li>
 *   <li>The growth series of the Pachycephalosaurus: "adult_dome" is hidden on babies and "young_spikes" shown only on
 *       them; "adult_dome_male" / "adult_dome_female" carry the adult crown of each sex</li>
 *   <li>The Parasaurolophus' crest: "adult_crest" is hidden on babies and "young_crest" (the low dome a hatchling had,
 *       Farke et al. 2013) shown only on them</li>
 *   <li>The Triceratops' brow horns: "adult_horns" is hidden on babies and "young_horns" (short, curving back) shown
 *       only on them</li>
 *   <li>The Styracosaurus' crown: "adult_frill" (the spikes, with "male_display" / "female_display" for each sex) is
 *       hidden on babies and "young_frill" (the calf's small points) shown only on them; its nose horn uses
 *       "adult_horns" / "young_horns"</li>
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
        // the Styracosaurus' crown: a calf's frill has small points that later grow into the spikes (1.8)
        // the Edmontosaurus' fleshy comb: the grown male's (under male_display, already hidden on females)
        hide("adult_comb", baby);
        hide("adult_frill", baby);
        hide("young_frill", !baby);
        // 1.9.5: the neck takes 40% of the look's turn from the head (the head alone turned like a vanilla mob's); the
        // sum is the same, so it still looks where it looks
        GeoBone headB = getAnimationProcessor().getBone("head");
        GeoBone neckB = getAnimationProcessor().getBone("neck");
        if (headB != null && neckB != null && !animatable.isSleeping() && !animatable.isKnockedOut() && animatable.isAlive()) {
            float yaw = headB.getRotY();
            float share = yaw * 0.4F;
            neckB.setRotY(neckB.getRotY() + share);
            headB.setRotY(headB.getRotY() - share);
            neckB.resetStateChanges();
            headB.resetStateChanges();
        }
        com.terrassic.entity.LivelyMotion lively = animatable.lively();
        if (lively != null) {
            this.scaleOf = animatable.livelyModelScale() * animatable.getScale();
            this.applyLively(lively, animationState.getPartialTick());
            // HOTFIX 1.9.1: GeckoLib clears the "changed" marks at the end of its own tick, before this; the live layer's
            // additions marked the bones changed again, so on the next frame a bone the playing animation does not key
            // (a jaw, a beak, a tail tip, a leg) was not reset to its rest and the addition piled up frame after frame:
            // jaws and beaks spun round, legs went wrong (found in play, 06/11). The marks are cleared again here, so
            // GeckoLib resets those bones as it should and the addition stays an addition.
            for (String name : NO_FIX ? new String[0] : LIVELY_BONES) {
                GeoBone b = getAnimationProcessor().getBone(name);
                if (b != null) {
                    b.resetStateChanges();
                }
            }
        }
    }

    /** Test only (BehaviorTest "jaws"): TERRASSIC_NO_LIVELY_FIX=1 brings the 1.9.0 bug back to show it. */
    private static final boolean NO_FIX = "1".equals(System.getenv("TERRASSIC_NO_LIVELY_FIX"));

    /** Every bone the live layer adds to (tail, body, neck, jaw, legs). */
    private static final String[] LIVELY_BONES = {"tail1", "tail2", "tail3", "tail4", "tail5", "tail6", "body", "neck", "jaw",
            "thigh_l", "shin_l", "foot_l", "thigh_r", "shin_r", "foot_r",
            "arm_l", "forearm_l", "hand_l", "arm_r", "forearm_r", "hand_r"};

    /** Model scale times the animal's size, set before applyLively (feet: blocks to model px). */
    private float scaleOf = 1.0F;
    private float legPx = 50.0F;

    /** Lifts a foot by {@code lift} model px by bending the leg: the thigh forward, the shin back, the foot level. */
    private void bendLeg(String side, float lift, float d2r) {
        if (lift < 0.2F) {
            return;
        }
        float a = (float) Math.toDegrees(Math.asin(Math.min(0.85F, lift / this.legPx))) * 1.6F;
        GeoBone thigh = getAnimationProcessor().getBone("thigh_" + side);
        GeoBone shin = getAnimationProcessor().getBone("shin_" + side);
        GeoBone foot = getAnimationProcessor().getBone("foot_" + side);
        if (thigh != null && shin != null && foot != null) {
            thigh.setRotX(thigh.getRotX() + a * d2r);
            shin.setRotX(shin.getRotX() - 2.0F * a * d2r);
            foot.setRotX(foot.getRotX() + a * d2r);
        }
    }

    /** The live motion layer (entity/LivelyMotion) on top of the baked pose: the tail spring, and the body leaning and
     *  the neck looking into a curve. */
    private void applyLively(com.terrassic.entity.LivelyMotion m, float partial) {
        float d2r = (float) (Math.PI / 180.0D);
        this.legPx = m.legPx();
        if (!m.hasLegs()) {
            // the rig's own measures, once: the feet's distance from the middle and the thigh + shin length
            GeoBone th = getAnimationProcessor().getBone("thigh_l");
            GeoBone ft = getAnimationProcessor().getBone("foot_l");
            if (th != null && ft != null) {
                m.setLegs(Math.abs(th.getPivotX()), Math.abs(th.getPivotY() - ft.getPivotY()));
            } else {
                m.setLegs(-1.0F, 50.0F);
            }
            GeoBone ar = getAnimationProcessor().getBone("arm_l");
            GeoBone hd = getAnimationProcessor().getBone("hand_l");
            if (ar != null && hd != null) {
                m.setArms(Math.abs(ar.getPivotY() - hd.getPivotY()));
            }
        }
        // 1.10.1: the feet are tracked so the renderer can say where each was drawn (DinosaurRenderer.renderFinal)
        for (String f : com.terrassic.entity.LivelyMotion.FEET) {
            if (getAnimationProcessor().getBone(f) instanceof software.bernie.geckolib.cache.object.GeoBone gb && !gb.isTrackingMatrices()) {
                gb.setTrackingMatrices(true);
            }
        }
        for (int i = 0; i < 6; i++) {
            GeoBone b = getAnimationProcessor().getBone("tail" + (i + 1));
            if (b != null) {
                b.setRotY(b.getRotY() + m.tail(i, partial) * d2r);
            }
        }
        float bank = m.bank(partial);
        GeoBone body = getAnimationProcessor().getBone("body");
        if (body != null) {
            body.setRotZ(body.getRotZ() + bank * d2r);
        }
        GeoBone neck = getAnimationProcessor().getBone("neck");
        if (neck != null) {
            // the neck looks into the curve and stays upright against the lean
            neck.setRotY(neck.getRotY() + bank * 0.9F * d2r);
            neck.setRotZ(neck.getRotZ() - bank * 0.6F * d2r);
        }
        // the feet on uneven ground: the body drops to the lower foot, the other leg bends to set its foot on the higher
        // block, the hips tilt toward the low side
        float l = m.footLeft(partial);
        float r = m.footRight(partial);
        if (!com.terrassic.entity.Behaviour.oldFeet) {
            this.feet(m, body, partial, d2r);
        } else if ((Math.abs(l) > 0.02F || Math.abs(r) > 0.02F) && body != null) {
            float px = 16.0F / Math.max(0.1F, this.scaleOf);
            float drop = Math.min(0.0F, Math.min(l, r));
            body.setPosY(body.getPosY() + drop * px);
            body.setRotZ(body.getRotZ() + (float) Math.toDegrees(Math.atan2(l - r, 2.0F)) * 0.35F * d2r);
            this.bendLeg("l", (l - drop) * px, d2r);
            this.bendLeg("r", (r - drop) * px, d2r);
        }
        // panting after a run: the chest heaves, the head bobs a beat later and the mouth hangs open with each breath
        float ex = m.exertion();
        if (ex > 0.01F) {
            float ph = m.breath(partial);
            float br = (float) Math.sin(ph);
            if (body != null) {
                body.setRotX(body.getRotX() + 1.4F * ex * br * d2r);
                body.setPosY(body.getPosY() + 0.6F * ex * br);
            }
            if (neck != null) {
                neck.setRotX(neck.getRotX() - 1.2F * ex * (float) Math.sin(ph - 0.6F) * d2r);
            }
            GeoBone jaw = getAnimationProcessor().getBone("jaw");   // open = negative x
            if (jaw != null) {
                jaw.setRotX(jaw.getRotX() - (6.0F + 5.0F * Math.max(0.0F, (float) Math.sin(ph - 0.4F))) * ex * d2r);
            }
        }
    }

    /** 1.10.1, each foot on its own ground (LivelyMotion.feetTick): the body drops to the lowest foot (half a block at
     *  most), and every other leg bends to set its foot on its own ground; front legs bend at the elbow. */
    private void feet(com.terrassic.entity.LivelyMotion m, GeoBone body, float partial, float d2r) {
        float w = m.feetWeight(partial);
        if (w < 0.01F || body == null) {
            return;
        }
        float px = 16.0F / Math.max(0.1F, this.scaleOf);
        float[] g = new float[4];
        float drop = 0.0F;
        for (int i = 0; i < 4; i++) {
            g[i] = m.footGround(i, partial) * w;
            if (m.footAt(i) != null && getAnimationProcessor().getBone(com.terrassic.entity.LivelyMotion.FEET[i]) != null) {
                drop = Math.min(drop, g[i]);
            }
        }
        drop = Math.max(drop, -0.5F);
        if (drop < -0.01F) {
            body.setPosY(body.getPosY() + drop * px);
        }
        this.bendLeg("l", (g[0] - drop) * px, d2r);
        this.bendLeg("r", (g[1] - drop) * px, d2r);
        this.bendArm("l", (g[2] - drop) * px, m.armPx(), d2r);
        this.bendArm("r", (g[3] - drop) * px, m.armPx(), d2r);
    }

    /** Lifts a front foot by {@code lift} model px: the upper arm back, the forearm forward, the hand level. */
    private void bendArm(String side, float lift, float armPx, float d2r) {
        if (lift < 0.2F) {
            return;
        }
        float a = (float) Math.toDegrees(Math.asin(Math.min(0.85F, lift / armPx))) * 1.6F;
        GeoBone arm = getAnimationProcessor().getBone("arm_" + side);
        GeoBone fore = getAnimationProcessor().getBone("forearm_" + side);
        GeoBone hand = getAnimationProcessor().getBone("hand_" + side);
        if (arm != null && fore != null && hand != null) {
            arm.setRotX(arm.getRotX() - a * d2r);
            fore.setRotX(fore.getRotX() + 2.0F * a * d2r);
            hand.setRotX(hand.getRotX() - a * d2r);
        }
    }

    private void hide(String bone, boolean hidden) {
        GeoBone b = getAnimationProcessor().getBone(bone);
        if (b != null) {
            b.setHidden(hidden);
        }
    }
}
