package com.terrassic.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/** A cleaned fossil of one species ("&lt;species&gt;_fossil"), dug out of fossil rock. Studied at the Research Table. */
public class FossilItem extends Item {
    private final String species;

    public FossilItem(String species, Properties properties) {
        super(properties);
        this.species = species;
    }

    public String species() {
        return this.species;
    }

    @Override
    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.terrassic.study_at_table").withStyle(ChatFormatting.GRAY));
    }
}
