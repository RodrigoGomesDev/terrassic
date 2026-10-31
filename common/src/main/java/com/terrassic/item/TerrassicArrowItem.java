package com.terrassic.item;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ArrowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

import java.util.function.BiFunction;

/** An arrow item that shoots its own entity (entity/FlintArrow, entity/NarcoticArrow); any bow takes it. */
public class TerrassicArrowItem extends ArrowItem {
    private final BiFunction<Level, LivingEntity, AbstractArrow> factory;

    public TerrassicArrowItem(BiFunction<Level, LivingEntity, AbstractArrow> factory, Properties properties) {
        super(properties);
        this.factory = factory;
    }

    @Override
    public AbstractArrow createArrow(Level level, ItemStack stack, LivingEntity shooter) {
        return this.factory.apply(level, shooter);
    }
}
