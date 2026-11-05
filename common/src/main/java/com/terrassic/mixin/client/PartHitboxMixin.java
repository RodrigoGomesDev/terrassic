package com.terrassic.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.parts.DinoPart;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.AABB;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Hit parts (1.7): F3+B draws the creature's head, neck and tail boxes too (head red, neck yellow, tail blue). */
@Mixin(EntityRenderDispatcher.class)
public abstract class PartHitboxMixin {
    @Inject(method = "renderHitbox", at = @At("TAIL"), require = 0)
    private static void terrassic$parts(PoseStack pose, VertexConsumer buffer, Entity entity, float partialTick, CallbackInfo ci) {
        if (!(entity instanceof DinosaurEntity dino) || !dino.partsActive()) {
            return;
        }
        double x = -(entity.xo + (entity.getX() - entity.xo) * partialTick);
        double y = -(entity.yo + (entity.getY() - entity.yo) * partialTick);
        double z = -(entity.zo + (entity.getZ() - entity.zo) * partialTick);
        for (DinoPart part : dino.parts()) {
            AABB box = part.getBoundingBox().move(x, y, z);
            float r = part.kind() == DinoPart.Kind.HEAD ? 1.0F : part.kind() == DinoPart.Kind.NECK ? 1.0F : 0.25F;
            float g = part.kind() == DinoPart.Kind.NECK ? 1.0F : 0.25F;
            float b = part.kind() == DinoPart.Kind.TAIL ? 1.0F : 0.25F;
            LevelRenderer.renderLineBox(pose, buffer, box, r, g, b, 1.0F);
        }
    }
}
