package com.terrassic.entity;

import com.terrassic.registry.ModSounds;
import com.terrassic.registry.ModEntities;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

/** A thrown spear (flint or horn). Behaves like a thrown trident without loyalty/riptide. */
public class ThrownSpear extends AbstractArrow {
    private static final EntityDataAccessor<ItemStack> DATA_ITEM =
            SynchedEntityData.defineId(ThrownSpear.class, EntityDataSerializers.ITEM_STACK);

    private ItemStack spearItem = ItemStack.EMPTY;
    private float thrownDamage = 7.0F;
    private boolean dealtDamage;

    public ThrownSpear(EntityType<? extends ThrownSpear> type, Level level) {
        super(type, level);
    }

    public ThrownSpear(Level level, LivingEntity shooter, ItemStack stack, float damage) {
        super(ModEntities.SPEAR.get(), shooter, level);
        this.spearItem = stack.copy();
        this.thrownDamage = damage;
        this.entityData.set(DATA_ITEM, this.spearItem.copy());
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_ITEM, ItemStack.EMPTY);
    }

    /** The spear item, synced to clients for rendering. */
    public ItemStack getRenderStack() {
        return this.entityData.get(DATA_ITEM);
    }

    @Override
    public void tick() {
        if (this.inGroundTime > 4) {
            this.dealtDamage = true;
        }
        super.tick();
    }

    @Override
    protected ItemStack getPickupItem() {
        return this.spearItem.copy();
    }

    @Override
    protected EntityHitResult findHitEntity(Vec3 start, Vec3 end) {
        return this.dealtDamage ? null : super.findHitEntity(start, end);
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        Entity target = result.getEntity();
        float damage = this.thrownDamage;
        if (target instanceof LivingEntity living) {
            damage += EnchantmentHelper.getDamageBonus(this.spearItem, living.getMobType());
        }
        Entity owner = this.getOwner();
        DamageSource source = this.damageSources().trident(this, owner == null ? this : owner);
        this.dealtDamage = true;
        if (target.hurt(source, damage)) {
            if (target.getType() == EntityType.ENDERMAN) {
                return;
            }
            if (target instanceof LivingEntity living) {
                if (owner instanceof LivingEntity livingOwner) {
                    EnchantmentHelper.doPostHurtEffects(living, livingOwner);
                    EnchantmentHelper.doPostDamageEffects(livingOwner, living);
                }
                this.doPostHurtEffects(living);
            }
        }
        this.setDeltaMovement(this.getDeltaMovement().multiply(-0.01D, -0.1D, -0.01D));
        this.playSound(ModSounds.SFX_SPEAR_HIT.get(), 1.0F, 1.0F);
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return ModSounds.SFX_SPEAR_GROUND.get();
    }

    @Override
    protected void tickDespawn() {
        if (this.pickup != AbstractArrow.Pickup.ALLOWED) {
            super.tickDespawn();
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Spear", 10)) {
            this.spearItem = ItemStack.of(tag.getCompound("Spear"));
            this.entityData.set(DATA_ITEM, this.spearItem.copy());
        }
        this.dealtDamage = tag.getBoolean("DealtDamage");
        if (tag.contains("ThrownDamage")) {
            this.thrownDamage = tag.getFloat("ThrownDamage");
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.put("Spear", this.spearItem.save(new CompoundTag()));
        tag.putBoolean("DealtDamage", this.dealtDamage);
        tag.putFloat("ThrownDamage", this.thrownDamage);
    }

    @Override
    public boolean shouldRender(double x, double y, double z) {
        return true;
    }
}
