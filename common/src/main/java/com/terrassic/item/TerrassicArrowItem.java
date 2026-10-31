package com.terrassic.item;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ArrowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;


/** An arrow item that shoots its own entity (entity/FlintArrow, entity/NarcoticArrow); any bow takes it. */
public class TerrassicArrowItem extends ArrowItem {
    private final Factory factory;

    public TerrassicArrowItem(Factory factory, Properties properties) {
        super(properties);
        this.factory = factory;
    }

    @Override
    public AbstractArrow createArrow(Level level, ItemStack stack, LivingEntity shooter, ItemStack weapon) {
        return this.factory.create(level, shooter, weapon);
    }

    /** The arrow an item shoots; the weapon (null for a dispenser) carries its enchantments on 1.21. */
    @FunctionalInterface
    public interface Factory {
        AbstractArrow create(Level level, LivingEntity shooter, ItemStack weapon);
    }
}
