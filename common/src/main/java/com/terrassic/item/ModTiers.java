package com.terrassic.item;

import com.terrassic.registry.ModItems;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.function.Supplier;

/** Materials of the archaic weapons. */
public enum ModTiers implements Tier {
    FLINT(1, 160, 5.0F, 1.5F, 8, () -> Ingredient.of(Items.FLINT)),
    BONE(1, 220, 4.0F, 1.5F, 12, () -> Ingredient.of(Items.BONE)),
    HORN(2, 520, 5.5F, 2.5F, 12, () -> Ingredient.of(ModItems.TRICERATOPS_HORN.get())),
    REX_TOOTH(2, 640, 6.0F, 3.0F, 14, () -> Ingredient.of(ModItems.REX_TOOTH.get())),
    ANKYLO_CLUB(2, 900, 4.0F, 4.0F, 10, () -> Ingredient.of(ModItems.ANKYLOSAURUS_CLUB.get()));

    private final int level;
    private final int uses;
    private final float speed;
    private final float damage;
    private final int enchantmentValue;
    private final Supplier<Ingredient> repair;

    ModTiers(int level, int uses, float speed, float damage, int enchantmentValue, Supplier<Ingredient> repair) {
        this.level = level;
        this.uses = uses;
        this.speed = speed;
        this.damage = damage;
        this.enchantmentValue = enchantmentValue;
        this.repair = repair;
    }

    @Override
    public int getUses() {
        return this.uses;
    }

    @Override
    public float getSpeed() {
        return this.speed;
    }

    @Override
    public float getAttackDamageBonus() {
        return this.damage;
    }

    @Override
    public int getLevel() {
        return this.level;
    }

    @Override
    public int getEnchantmentValue() {
        return this.enchantmentValue;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return this.repair.get();
    }
}
