package com.terrassic.item;

import com.terrassic.research.Lore;
import com.terrassic.research.Knowledge;
import com.terrassic.research.Research;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.List;

/**
 * A loose page of Katarina's notebook. As soon as it is in a player's inventory it goes into their Field
 * Notebook: the page in NBT "Page" if set, otherwise one of the pages that player has not found yet (so chest
 * loot is per player). When the player already has every page it turns into paper.
 */
public class LoosePageItem extends Item {
    public static final String TAG = "Page";

    public LoosePageItem(Properties properties) {
        super(properties);
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        if (level.isClientSide() || !(entity instanceof ServerPlayer player) || stack.isEmpty()) {
            return;
        }
        String page = stack.hasTag() && stack.getTag().contains(TAG) ? stack.getTag().getString(TAG) : null;
        if (page == null) {
            Knowledge k = Research.knowledge(player);
            List<String> missing = new ArrayList<>();
            for (Lore.Page p : Lore.ALL) {
                if (!k.pages().contains(p.id())) {
                    missing.add(p.id());
                }
            }
            if (missing.isEmpty()) {
                int count = stack.getCount();
                stack.setCount(0);
                ItemStack paper = new ItemStack(Items.PAPER, count);
                if (!player.getInventory().add(paper)) {
                    player.drop(paper, false);
                }
                return;
            }
            page = missing.get(level.random.nextInt(missing.size()));
        }
        stack.shrink(1);
        Lore.Page p = Lore.byId(page);
        if (p != null && Research.addPage(player, page)) {
            player.displayClientMessage(Component.translatable("message.terrassic.page_found",
                    Component.translatable("page.terrassic." + page + ".title")), true);
            player.playNotifySound(SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1.0F, 1.2F);
        }
    }
}
