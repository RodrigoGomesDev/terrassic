package com.terrassic.item;

import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;

/** Heavy, slow blunt weapon that knocks targets far back. */
public class ClubItem extends SwordItem {
    private final float knockback;

    public ClubItem(Tier tier, int damage, float speed, float knockback, Properties properties) {
        super(tier, damage, speed, properties);
        this.knockback = knockback;
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        float yaw = attacker.getYRot() * Mth.DEG_TO_RAD;
        target.knockback(this.knockback, Mth.sin(yaw), -Mth.cos(yaw));
        return super.hurtEnemy(stack, target, attacker);
    }
}
