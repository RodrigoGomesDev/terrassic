package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.terrassic.client.compat.HatsCompat;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.registry.ModItems;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * One renderer for every dinosaur. Model and animations are looked up by species id:
 *   geo/entity/&lt;id&gt;.geo.json, animations/entity/&lt;id&gt;.animation.json,
 *   textures/entity/&lt;id&gt;_male.png and _female.png
 */
public class DinosaurRenderer<T extends DinosaurEntity> extends GeoEntityRenderer<T> {
    /** How far from the player's centre the left shoulder is (blocks). */
    private static final double SHOULDER_SIDE = 0.37D;

    private final ItemRenderer items;

    public DinosaurRenderer(EntityRendererProvider.Context context, String speciesId, float modelScale, float shadow) {
        super(context, new DinoGeoModel<>(speciesId));
        this.items = context.getItemRenderer();
        this.withScale(modelScale);
        this.shadowRadius = shadow;
        this.addRenderLayer(new RiftLayer<>(this));  // v0.9: creatures of the Rift glow with amber cracks
        this.addRenderLayer(new StuckProjectilesLayer<>(this));  // v1.1.4: darts and arrows stuck in the hide
    }

    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, T animatable,
                                    BakedGeoModel model, boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float baby = animatable.getScale();
        super.scaleModelForRender(widthScale * baby, heightScale * baby, poseStack, animatable, model, isReRender,
                partialTick, packedLight, packedOverlay);
    }

    /** How much the model is scaled when drawn (the species' model scale times the growth of a young one). */
    public float renderScale(DinosaurEntity entity) {
        return this.scaleWidth * entity.getScale();
    }

    /** A flyer that tilts in flight pitches and banks the whole body about its saddle (FlyingDinosaur#flightPitch). The
     *  model is already scaled here and faces -Z, so the pivot is in model units. */
    @Override
    protected void applyRotations(T animatable, PoseStack poseStack, float ageInTicks, float rotationYaw, float partialTick) {
        super.applyRotations(animatable, poseStack, ageInTicks, rotationYaw, partialTick);
        if (animatable instanceof FlyingDinosaur flyer && animatable.deathTime <= 0) {
            float pitch = flyer.flightPitch(partialTick);
            float roll = flyer.flightRoll(partialTick);
            if (Math.abs(pitch) > 0.05F || Math.abs(roll) > 0.05F) {
                float size = animatable.getScale();
                double up = flyer.tiltPivotHeight() / (this.scaleHeight * size);
                double back = flyer.tiltPivotForward() / (this.scaleWidth * size);
                poseStack.translate(0.0D, up, -back);
                poseStack.mulPose(Axis.XP.rotationDegrees(pitch));
                poseStack.mulPose(Axis.ZP.rotationDegrees(roll));
                poseStack.translate(0.0D, -up, back);
            }
        }
    }

    @Override
    public void render(T entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        super.render(entity, entityYaw, partialTick, poseStack, buffer, packedLight);
        if (HatsCompat.PRESENT) {
            HatsCompat.capture(entity, this.getGeoModel(), this.renderScale(entity));
        }
        if (entity.isEntangled()) {
            this.renderBola(entity, partialTick, poseStack, buffer, packedLight);
        }
    }

    /** A bola's thongs wound round a tied animal (v1.1, docs/ARMAS.md): one loop the width of the body round the legs,
     *  or round the wings of a flyer, the stones hanging from it (model item/bola_wrap). Drawn the same for every
     *  species, so it needs nothing from their models. */
    private void renderBola(T entity, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        boolean wings = entity instanceof FlyingDinosaur;
        float width = entity.getBbWidth() * (wings ? 1.25F : 1.05F);
        float y = entity.getBbHeight() * (wings ? 0.55F : 0.25F);
        poseStack.pushPose();
        poseStack.translate(0.0D, y, 0.0D);
        poseStack.mulPose(Axis.YP.rotationDegrees(-Mth.rotLerp(partialTick, entity.yBodyRotO, entity.yBodyRot)));
        poseStack.scale(width, Math.max(0.6F, width * 0.5F), width);
        WeaponPoses.BOLA = 1.0F;
        try {
            this.items.renderStatic(new ItemStack(ModItems.BOLA.get()), ItemDisplayContext.NONE, packedLight, OverlayTexture.NO_OVERLAY,
                    poseStack, buffer, entity.level(), entity.getId());
        } finally {
            WeaponPoses.BOLA = 0.0F;
        }
        poseStack.popPose();
    }

    /** No vanilla tipping over: they fall in their own death animation or sink into the knocked_out pose, the one the
     *  carcass lies in (DinosaurEntity#tickDeath). */
    @Override
    protected float getDeathMaxRotation(T animatable) {
        return 0.0F;
    }

    /** Red only while hurt: the vanilla red of the whole dying body (deathTime) is left out, the death animation and the
     *  carcass carry the death (found in play, 06/11: the body flashed red as it fell). */
    @Override
    public int getPackedOverlay(T animatable, float u, float partialTick) {
        return net.minecraft.client.renderer.texture.OverlayTexture.pack(net.minecraft.client.renderer.texture.OverlayTexture.u(u),
                net.minecraft.client.renderer.texture.OverlayTexture.v(animatable.hurtTime > 0 && animatable.deathTime <= 0));
    }

    /** A perched animal rides centred on the player; draw it on the left shoulder instead. */
    @Override
    public Vec3 getRenderOffset(T entity, float partialTick) {
        Vec3 offset = super.getRenderOffset(entity, partialTick);
        if (entity.isPerched() && entity.getVehicle() instanceof Player owner) {
            float yaw = Mth.rotLerp(partialTick, owner.yBodyRotO, owner.yBodyRot) * Mth.DEG_TO_RAD;
            offset = offset.add(Mth.cos(yaw) * SHOULDER_SIDE, -0.05D, Mth.sin(yaw) * SHOULDER_SIDE);
        }
        return offset;
    }
}
