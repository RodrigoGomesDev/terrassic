package com.terrassic.item;

import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/** A charcoal sketch of one species (NBT "Species"). Studied at the Research Table. */
public class SketchItem extends Item {
    private static final String TAG = "Species";

    public SketchItem(Properties properties) {
        super(properties);
    }

    public static ItemStack of(Item item, String species) {
        ItemStack stack = new ItemStack(item);
        stack.getOrCreateTag().putString(TAG, species);
        return stack;
    }

    /** The species drawn on this sketch, or null for a blank one. */
    public static String species(ItemStack stack) {
        CompoundTag tag = stack.getTag();
        return tag != null && tag.contains(TAG) ? tag.getString(TAG) : null;
    }

    @Override
    public Component getName(ItemStack stack) {
        String species = species(stack);
        return species == null ? super.getName(stack)
                : Component.translatable("item.terrassic.sketch.of", Component.translatable("entity.terrassic." + species));
    }

    @Override
    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {
        if (species(stack) != null) {
            tooltip.add(Component.translatable("tooltip.terrassic.study_at_table").withStyle(ChatFormatting.GRAY));
        }
    }
}
