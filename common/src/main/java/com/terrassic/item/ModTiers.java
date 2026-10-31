package com.terrassic.item;

import com.terrassic.registry.ModItems;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;

import java.util.function.Supplier;

/** Materials of the archaic weapons. */
public enum ModTiers implements Tier {
    FLINT(BlockTags.INCORRECT_FOR_STONE_TOOL, 160, 5.0F, 1.5F, 8, () -> Ingredient.of(Items.FLINT)),
    BONE(BlockTags.INCORRECT_FOR_STONE_TOOL, 220, 4.0F, 1.5F, 12, () -> Ingredient.of(Items.BONE)),
    HORN(BlockTags.INCORRECT_FOR_IRON_TOOL, 520, 5.5F, 2.5F, 12, () -> Ingredient.of(ModItems.TRICERATOPS_HORN.get())),
    REX_TOOTH(BlockTags.INCORRECT_FOR_IRON_TOOL, 640, 6.0F, 3.0F, 14, () -> Ingredient.of(ModItems.REX_TOOTH.get())),
    ANKYLO_CLUB(BlockTags.INCORRECT_FOR_IRON_TOOL, 900, 4.0F, 4.0F, 10, () -> Ingredient.of(ModItems.ANKYLOSAURUS_CLUB.get()));

    private final TagKey<Block> incorrect;
    private final int uses;
    private final float speed;
    private final float damage;
    private final int enchantmentValue;
    private final Supplier<Ingredient> repair;

    ModTiers(TagKey<Block> incorrect, int uses, float speed, float damage, int enchantmentValue, Supplier<Ingredient> repair) {
        this.incorrect = incorrect;
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
    public TagKey<Block> getIncorrectBlocksForDrops() {
        return this.incorrect;
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
