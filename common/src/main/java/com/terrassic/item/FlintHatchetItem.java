package com.terrassic.item;

import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.Tier;

/** Hand axe: a weapon that also chops wood. */
public class FlintHatchetItem extends AxeItem {
    public FlintHatchetItem(Tier tier, float damage, float speed, Properties properties) {
        super(tier, damage, speed, properties);
    }
}
