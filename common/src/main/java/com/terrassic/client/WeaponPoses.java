package com.terrassic.client;

import com.terrassic.Terrassic;
import com.terrassic.item.HuntingBowItem;
import com.terrassic.registry.ModItems;
import dev.architectury.event.events.client.ClientLifecycleEvent;
import dev.architectury.registry.item.ItemPropertiesRegistry;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * Item properties that swap a weapon's model while it is in use, the way the vanilla bow swaps its pulling frames.
 * "terrassic:blowing" (blowgun): 1 while the blowgun is at the lips, so the reed tube points at the crosshair.
 * "pulling"/"pull" (hunting bow): the vanilla bow's pair, over the hunting bow's longer draw.
 * "terrassic:held" (spears): 1 only while {@link #HELD} is set, which mixin/client/HeldSpearMixin does when a spear is
 * drawn in a hand or in flight, so the 3D spear replaces the sprite there and the inventory keeps the sprite.
 */
public final class WeaponPoses {
    /** Set by HeldSpearMixin around the model lookup of a spear in a hand or in flight (render thread only). */
    public static boolean HELD;

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
            for (Item spear : new Item[]{ModItems.FLINT_SPEAR.get(), ModItems.HORN_SPEAR.get()}) {
                ItemPropertiesRegistry.register(spear, new ResourceLocation(Terrassic.MOD_ID, "held"),
                        (stack, level, entity, seed) -> HELD ? 1.0F : 0.0F);
            }
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
