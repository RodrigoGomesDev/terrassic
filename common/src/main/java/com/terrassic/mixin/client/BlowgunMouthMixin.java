package com.terrassic.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.terrassic.client.WeaponPoses;
import com.terrassic.registry.ModItems;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HeadedModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.client.renderer.entity.layers.PlayerItemInHandLayer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * v1.1.1 (docs/ARMAS.md): a player blowing a blowgun, seen from outside (F5, other players), has the tube at the mouth,
 * drawn from the head the way vanilla draws the spyglass at the eye (PlayerItemInHandLayer#renderArmWithSpyglass),
 * with the "terrassic:mouth" model (item/blowgun_mouth). Before, the 24 px tube stuck out of the raised hand.
 * Optional: without it the blowgun stays in the hand.
 */
@Mixin(PlayerItemInHandLayer.class)
public abstract class BlowgunMouthMixin {
    /** From the head's centre down to the mouth (2.5 face pixels), in the space CustomHeadLayer.translateToHead leaves:
     *  scaled by 0.625 and turned upside down, so down is negative. */
    private static final float MOUTH_DROP = -0.25F;

    @Shadow
    @Final
    private ItemInHandRenderer itemInHandRenderer;

    @Inject(method = "renderArmWithItem", at = @At("HEAD"), cancellable = true, require = 0)
    private void terrassic$blowgunAtMouth(LivingEntity entity, ItemStack stack, ItemDisplayContext context, HumanoidArm arm,
                                          PoseStack poseStack, MultiBufferSource buffer, int light, CallbackInfo ci) {
        if (!stack.is(ModItems.BLOWGUN.get()) || !entity.isUsingItem() || entity.getUseItem() != stack || entity.swingTime != 0) {
            return;
        }
        EntityModel<?> parent = ((RenderLayer<?, ?>) (Object) this).getParentModel();
        if (!(parent instanceof HeadedModel headed)) {
            return;
        }
        poseStack.pushPose();
        ModelPart head = headed.getHead();
        float xRot = head.xRot;
        head.xRot = Mth.clamp(head.xRot, -(float) Math.PI / 6.0F, (float) Math.PI / 2.0F);
        head.translateAndRotate(poseStack);
        head.xRot = xRot;
        CustomHeadLayer.translateToHead(poseStack, false);
        poseStack.translate(0.0F, MOUTH_DROP, 0.0F);
        WeaponPoses.MOUTH = true;
        try {
            this.itemInHandRenderer.renderItem(entity, stack, ItemDisplayContext.HEAD, false, poseStack, buffer, light);
        } finally {
            WeaponPoses.MOUTH = false;
        }
        poseStack.popPose();
        ci.cancel();
    }
}
