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

/** Hit parts (1.7): F3+B draws the creature's part boxes too (head red, neck yellow, body green, tail blue, wing violet). */
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
            if (!part.enabled()) {
                continue;
            }
            AABB box = part.getBoundingBox().move(x, y, z);
            // head red, neck yellow, body green, tail blue, wing violet
            float[] c = switch (part.kind()) {
                case HEAD -> new float[]{1.0F, 0.2F, 0.2F};
                case NECK -> new float[]{1.0F, 1.0F, 0.2F};
                case BODY -> new float[]{0.2F, 1.0F, 0.3F};
                case TAIL -> new float[]{0.3F, 0.5F, 1.0F};
                case WING -> new float[]{0.8F, 0.4F, 1.0F};
            };
            LevelRenderer.renderLineBox(pose, buffer, box, c[0], c[1], c[2], 1.0F);
        }
    }
}
