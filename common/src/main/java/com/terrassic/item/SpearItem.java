package com.terrassic.item;

import com.terrassic.registry.ModSounds;
import com.google.common.collect.ImmutableMultimap;
import com.google.common.collect.Multimap;
import com.terrassic.entity.ThrownSpear;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
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
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.item.Vanishable;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Throwable spear (docs/ARMAS.md). A quick tap of right click is a thrust that reaches 4.5 blocks (farther than an
 * arm's reach); holding it charges a throw like a trident without enchantments (a soft cue when ready), release to
 * throw. Thrown spears stick in the ground and can be picked up again. In hand and in flight it is drawn as a 3D
 * spear (client/WeaponPoses, mixin/client/HeldSpearMixin); the inventory keeps the sprite.
 */
public class SpearItem extends Item implements Vanishable {
    /** Ticks of charge for a throw; a shorter press is a thrust. */
    public static final int THROW_CHARGE = 10;
    public static final double THRUST_REACH = 4.5D;
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
        if (charged < THROW_CHARGE) {
            this.thrust(stack, level, player);
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
            level.playSound(null, spear, ModSounds.SFX_SPEAR_THROW.get(), SoundSource.PLAYERS, 1.0F, 0.85F);
            if (!player.getAbilities().instabuild) {
                player.getInventory().removeItem(stack);
            }
        }
        player.awardStat(Stats.ITEM_USED.get(this));
    }

    @Override
    public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
        if (this.getUseDuration(stack) - remaining == THROW_CHARGE && !level.isClientSide()) {
            level.playSound(null, user.getX(), user.getEyeY(), user.getZ(), SoundEvents.CROSSBOW_LOADING_END, SoundSource.PLAYERS,
                    0.4F, 1.2F);
        }
    }

    /** The quick thrust: the first creature along the aim within reach takes a normal melee blow. */
    private void thrust(ItemStack stack, Level level, Player player) {
        player.swing(player.getUsedItemHand(), true);
        player.getCooldowns().addCooldown(this, 12);
        if (level.isClientSide()) {
            return;
        }
        Vec3 eye = player.getEyePosition();
        Vec3 reach = player.getViewVector(1.0F).scale(THRUST_REACH);
        BlockHitResult wall = level.clip(new ClipContext(eye, eye.add(reach), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        Vec3 end = wall.getType() == HitResult.Type.MISS ? eye.add(reach) : wall.getLocation();
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end, player.getBoundingBox().expandTowards(reach).inflate(1.0D),
                e -> e instanceof LivingEntity && e.isPickable() && !e.isSpectator() && e != player.getVehicle(), eye.distanceToSqr(end));
        level.playSound(null, player.getX(), player.getEyeY(), player.getZ(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS,
                0.5F, 1.5F);
        if (hit != null) {
            player.attack(hit.getEntity());
            if (level instanceof ServerLevel server) {
                Vec3 at = hit.getLocation();
                server.sendParticles(ParticleTypes.CRIT, at.x, at.y, at.z, 6, 0.15D, 0.15D, 0.15D, 0.2D);
            }
        }
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
