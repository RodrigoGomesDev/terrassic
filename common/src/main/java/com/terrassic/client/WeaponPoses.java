package com.terrassic.client;

import com.terrassic.Terrassic;
import com.terrassic.registry.ModItems;
import dev.architectury.event.events.client.ClientLifecycleEvent;
import dev.architectury.registry.item.ItemPropertiesRegistry;
import net.minecraft.resources.ResourceLocation;

/**
 * Item properties that swap a weapon's model while it is in use, the way the vanilla bow swaps its pulling frames.
 * "terrassic:blowing" (blowgun): 1 while the blowgun is at the lips, so the reed tube points at the crosshair.
 */
public final class WeaponPoses {
    private WeaponPoses() {
    }

    public static void init() {
        ClientLifecycleEvent.CLIENT_SETUP.register(minecraft ->
                ItemPropertiesRegistry.register(ModItems.BLOWGUN.get(), new ResourceLocation(Terrassic.MOD_ID, "blowing"),
                        (stack, level, entity, seed) -> entity != null && entity.isUsingItem() && entity.getUseItem() == stack ? 1.0F : 0.0F));
    }
}
