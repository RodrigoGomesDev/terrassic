package com.terrassic.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * The Field Lens (a magnifying glass of amber in a bone rim): held in either hand, it shows a panel next to the
 * crosshair about the dinosaur you look at, up to 40 blocks away: sex, size, health and hunger, the owner, and for a
 * wild one how it is tamed, what it eats and, once knocked out, its torpor, the taming progress, the effectiveness
 * and the time until it wakes (client/LensOverlay, network/LensNetwork).
 */
public class FieldLensItem extends Item {
    public FieldLensItem(Properties properties) {
        super(properties);
    }

    /** True while the player holds a Field Lens in either hand. */
    public static boolean holding(Player player) {
        return player.getMainHandItem().getItem() instanceof FieldLensItem || player.getOffhandItem().getItem() instanceof FieldLensItem;
    }

    @Override
    public void appendHoverText(ItemStack stack, Level level, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable("item.terrassic.field_lens.tip").withStyle(ChatFormatting.GRAY));
        lines.add(Component.translatable("item.terrassic.field_lens.tip2").withStyle(ChatFormatting.DARK_GRAY));
    }
}
