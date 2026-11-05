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

/**
 * The Pocket Guide (v1.1.2, docs/AJUDA.md): the help book. Every player gets one on joining a world; use it to read.
 * The same item, with a volume, is one of the four Bestiaries (1.7.1): the species of one group, a page each.
 */
public class PocketGuideItem extends Item {
    /** "carnivores", "herbivores", "flyers", "marine", or empty for the Pocket Guide. */
    private final String volume;

    public PocketGuideItem(Properties properties) {
        this(properties, "");
    }

    public PocketGuideItem(Properties properties, String volume) {
        super(properties);
        this.volume = volume;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (level.isClientSide()) {
            EnvExecutor.runInEnv(Env.CLIENT, () -> () -> PocketGuideScreen.open(this.volume));
        }
        player.awardStat(Stats.ITEM_USED.get(this));
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide());
    }
}
