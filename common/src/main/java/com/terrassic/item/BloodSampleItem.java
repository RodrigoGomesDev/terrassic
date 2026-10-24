package com.terrassic.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** A Clay Jar with the blood of one species (NBT "Species", like a sketch). Studied at the Research Table. */
public class BloodSampleItem extends SketchItem {
    public BloodSampleItem(Properties properties) {
        super(properties);
    }

    @Override
    public Component getName(ItemStack stack) {
        String species = species(stack);
        return species == null ? super.getName(stack)
                : Component.translatable("item.terrassic.blood_sample.of", Component.translatable("entity.terrassic." + species));
    }
}
