package com.terrassic.item;

import com.terrassic.client.PocketGuideScreen;
import dev.architectury.utils.Env;
import dev.architectury.utils.EnvExecutor;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** The Pocket Guide (v1.1.2, docs/AJUDA.md): the help book. Every player gets one on joining a world; use it to read. */
public class PocketGuideItem extends Item {
    public PocketGuideItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (level.isClientSide()) {
            EnvExecutor.runInEnv(Env.CLIENT, () -> () -> PocketGuideScreen.open());
        }
        player.awardStat(Stats.ITEM_USED.get(this));
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide());
    }
}
