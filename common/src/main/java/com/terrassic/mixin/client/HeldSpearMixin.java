package com.terrassic.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.terrassic.client.WeaponPoses;
import com.terrassic.item.SpearItem;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Spears in a hand or in flight are drawn with their 3D model (the "terrassic:held" override, client/WeaponPoses),
 *  like the vanilla trident; the inventory, the ground and item frames keep the sprite.
 *  Optional: without it spears are the sprite everywhere. */
@Mixin(ItemRenderer.class)
public abstract class HeldSpearMixin {
    @Unique
    private static boolean terrassic$swapping;

    @Shadow
    public abstract void render(ItemStack stack, ItemDisplayContext context, boolean leftHand, PoseStack poseStack,
                                MultiBufferSource buffer, int light, int overlay, BakedModel model);

    @Inject(method = "render", at = @At("HEAD"), cancellable = true, require = 0)
    private void terrassic$heldSpear(ItemStack stack, ItemDisplayContext context, boolean leftHand, PoseStack poseStack,
                                     MultiBufferSource buffer, int light, int overlay, BakedModel model, CallbackInfo ci) {
        if (terrassic$swapping || !(stack.getItem() instanceof SpearItem)) {
            return;
        }
        boolean hand = context.firstPerson() || context == ItemDisplayContext.THIRD_PERSON_LEFT_HAND
                || context == ItemDisplayContext.THIRD_PERSON_RIGHT_HAND || context == ItemDisplayContext.NONE;
        if (!hand) {
            return;
        }
        WeaponPoses.HELD = true;
        BakedModel held = model.getOverrides().resolve(model, stack, null, null, 0);
        WeaponPoses.HELD = false;
        if (held == null || held == model) {
            return;
        }
        terrassic$swapping = true;
        try {
            this.render(stack, context, leftHand, poseStack, buffer, light, overlay, held);
        } finally {
            terrassic$swapping = false;
        }
        ci.cancel();
    }
}
