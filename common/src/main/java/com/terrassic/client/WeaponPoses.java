package com.terrassic.client;

import com.terrassic.Terrassic;
import com.terrassic.item.HuntingBowItem;
import com.terrassic.registry.ModItems;
import dev.architectury.event.events.client.ClientLifecycleEvent;
import dev.architectury.registry.item.ItemPropertiesRegistry;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

/**
 * Item properties that swap a weapon's model while it is in use, the way the vanilla bow swaps its pulling frames.
 * "terrassic:blowing" (blowgun): 1 while the blowgun is at the lips, so the reed tube points at the crosshair.
 * "pulling"/"pull" (hunting bow): the vanilla bow's pair, over the hunting bow's longer draw.
 */
public final class WeaponPoses {
    private WeaponPoses() {
    }

    public static void init() {
        ClientLifecycleEvent.CLIENT_SETUP.register(minecraft -> {
            ItemPropertiesRegistry.register(ModItems.BLOWGUN.get(), new ResourceLocation(Terrassic.MOD_ID, "blowing"),
                    (stack, level, entity, seed) -> using(entity, stack) ? 1.0F : 0.0F);
            ItemPropertiesRegistry.register(ModItems.HUNTING_BOW.get(), new ResourceLocation("pulling"),
                    (stack, level, entity, seed) -> using(entity, stack) ? 1.0F : 0.0F);
            ItemPropertiesRegistry.register(ModItems.HUNTING_BOW.get(), new ResourceLocation("pull"),
                    (stack, level, entity, seed) -> using(entity, stack)
                            ? (float) (stack.getUseDuration() - entity.getUseItemRemainingTicks()) / HuntingBowItem.FULL_DRAW : 0.0F);
        });
    }

    private static boolean using(LivingEntity entity, ItemStack stack) {
        return entity != null && entity.isUsingItem() && entity.getUseItem() == stack;
    }

    /** The hunting bow's draw for the field-of-view zoom (mixin/client/BowZoomMixin): 0..1, eased like the bow's. */
    public static float bowZoom(LivingEntity entity) {
        if (!entity.isUsingItem() || !entity.getUseItem().is(ModItems.HUNTING_BOW.get())) {
            return 0.0F;
        }
        float g = (float) entity.getTicksUsingItem() / HuntingBowItem.FULL_DRAW;
        return g > 1.0F ? 1.0F : g * g;
    }
}
