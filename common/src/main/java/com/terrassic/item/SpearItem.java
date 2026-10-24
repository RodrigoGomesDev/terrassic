package com.terrassic.item;

import com.google.common.collect.ImmutableMultimap;
import com.google.common.collect.Multimap;
import com.terrassic.entity.ThrownSpear;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.item.Vanishable;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Throwable spear. Works like a trident without enchantments: hold right click to charge, release to throw.
 * Thrown spears stick in the ground and can be picked up again.
 */
public class SpearItem extends Item implements Vanishable {
    private final Multimap<Attribute, AttributeModifier> modifiers;
    private final float thrownDamage;

    public SpearItem(float meleeDamage, float attackSpeed, float thrownDamage, Properties properties) {
        super(properties);
        this.thrownDamage = thrownDamage;
        ImmutableMultimap.Builder<Attribute, AttributeModifier> builder = ImmutableMultimap.builder();
        builder.put(Attributes.ATTACK_DAMAGE, new AttributeModifier(BASE_ATTACK_DAMAGE_UUID, "Weapon modifier",
                meleeDamage - 1.0F, AttributeModifier.Operation.ADDITION));
        builder.put(Attributes.ATTACK_SPEED, new AttributeModifier(BASE_ATTACK_SPEED_UUID, "Weapon modifier",
                attackSpeed, AttributeModifier.Operation.ADDITION));
        this.modifiers = builder.build();
    }

    public float getThrownDamage() {
        return this.thrownDamage;
    }

    @Override
    public boolean canAttackBlock(BlockState state, Level level, BlockPos pos, Player player) {
        return !player.isCreative();
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.SPEAR;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return 72000;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (stack.getDamageValue() >= stack.getMaxDamage() - 1) {
            return InteractionResultHolder.fail(stack);
        }
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void releaseUsing(ItemStack stack, Level level, LivingEntity user, int timeLeft) {
        if (!(user instanceof Player player)) {
            return;
        }
        int charged = this.getUseDuration(stack) - timeLeft;
        if (charged < 10) {
            return;
        }
        if (!level.isClientSide()) {
            stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(user.getUsedItemHand()));
            ThrownSpear spear = new ThrownSpear(level, player, stack, this.thrownDamage);
            spear.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 2.2F, 1.0F);
            if (player.getAbilities().instabuild) {
                spear.pickup = AbstractArrow.Pickup.CREATIVE_ONLY;
            }
            level.addFreshEntity(spear);
            level.playSound(null, spear, SoundEvents.TRIDENT_THROW, SoundSource.PLAYERS, 1.0F, 0.85F);
            if (!player.getAbilities().instabuild) {
                player.getInventory().removeItem(stack);
            }
        }
        player.awardStat(Stats.ITEM_USED.get(this));
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        stack.hurtAndBreak(1, attacker, e -> e.broadcastBreakEvent(EquipmentSlot.MAINHAND));
        return true;
    }

    @Override
    public boolean mineBlock(ItemStack stack, Level level, BlockState state, BlockPos pos, LivingEntity entity) {
        if (state.getDestroySpeed(level, pos) != 0.0F) {
            stack.hurtAndBreak(2, entity, e -> e.broadcastBreakEvent(EquipmentSlot.MAINHAND));
        }
        return true;
    }

    @Override
    @SuppressWarnings("deprecation")
    public Multimap<Attribute, AttributeModifier> getDefaultAttributeModifiers(EquipmentSlot slot) {
        return slot == EquipmentSlot.MAINHAND ? this.modifiers : super.getDefaultAttributeModifiers(slot);
    }

    @Override
    public int getEnchantmentValue() {
        return 1;
    }
}
