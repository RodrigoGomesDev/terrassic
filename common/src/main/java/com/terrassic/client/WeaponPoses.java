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
    /** "terrassic:bola": 0.5 while BolaRenderer draws a bola in flight, 1 while DinosaurRenderer draws one wound round a
     *  tied animal (render thread only); 0 everywhere else, so hands and inventory keep the sprite. */
    public static float BOLA;
    /** "terrassic:mouth": set by mixin/client/BlowgunMouthMixin while it draws a blowgun at a player's mouth. */
    public static boolean MOUTH;

    private WeaponPoses() {
    }

    public static void init() {
        ClientLifecycleEvent.CLIENT_SETUP.register(minecraft -> {
            ItemPropertiesRegistry.register(ModItems.BLOWGUN.get(), ResourceLocation.fromNamespaceAndPath(Terrassic.MOD_ID, "blowing"),
                    (stack, level, entity, seed) -> using(entity, stack) ? 1.0F : 0.0F);
            ItemPropertiesRegistry.register(ModItems.BLOWGUN.get(), ResourceLocation.fromNamespaceAndPath(Terrassic.MOD_ID, "mouth"),
                    (stack, level, entity, seed) -> MOUTH ? 1.0F : 0.0F);
            ItemPropertiesRegistry.register(ModItems.HUNTING_BOW.get(), ResourceLocation.parse("pulling"),
                    (stack, level, entity, seed) -> using(entity, stack) ? 1.0F : 0.0F);
            ItemPropertiesRegistry.register(ModItems.HUNTING_BOW.get(), ResourceLocation.parse("pull"),
                    (stack, level, entity, seed) -> using(entity, stack)
                            ? (float) (stack.getUseDuration(entity) - entity.getUseItemRemainingTicks()) / HuntingBowItem.FULL_DRAW : 0.0F);
            ItemPropertiesRegistry.register(ModItems.BOLA.get(), ResourceLocation.fromNamespaceAndPath(Terrassic.MOD_ID, "bola"),
                    (stack, level, entity, seed) -> BOLA);
            for (Item spear : new Item[]{ModItems.FLINT_SPEAR.get(), ModItems.HORN_SPEAR.get()}) {
                ItemPropertiesRegistry.register(spear, ResourceLocation.fromNamespaceAndPath(Terrassic.MOD_ID, "held"),
                        (stack, level, entity, seed) -> HELD ? 1.0F : 0.0F);
                // raised to throw: the vanilla trident's predicate, so the spear takes the trident's throwing pose
                ItemPropertiesRegistry.register(spear, ResourceLocation.parse("throwing"),
                        (stack, level, entity, seed) -> using(entity, stack) ? 1.0F : 0.0F);
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
