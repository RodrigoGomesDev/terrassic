package com.terrassic.entity;

import com.terrassic.registry.ModEntities;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TieredItem;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.ArrayList;
import java.util.List;

/**
 * The body a dead dinosaur leaves behind (docs/CARCACAS.md). It holds the animal's death loot and a number of
 * "meat" shares that grows with the animal's size; players harvest it by hitting or using it (tools take two shares
 * a time), scavengers bite it (the share is eaten, they heal), and it rots away after a few minutes, dropping
 * whatever is left. Rendered with the species' own model frozen in the knocked_out pose.
 */
public class CarcassEntity extends Entity implements GeoEntity {
    private static final EntityDataAccessor<String> DATA_SPECIES = SynchedEntityData.defineId(CarcassEntity.class, EntityDataSerializers.STRING);
    private static final EntityDataAccessor<Boolean> DATA_FEMALE = SynchedEntityData.defineId(CarcassEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Float> DATA_WIDTH = SynchedEntityData.defineId(CarcassEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_HEIGHT = SynchedEntityData.defineId(CarcassEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> DATA_SCALE = SynchedEntityData.defineId(CarcassEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> DATA_MEAT = SynchedEntityData.defineId(CarcassEntity.class, EntityDataSerializers.INT);

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private RawAnimation poseAnim;
    /** The death loot still inside, handed out share by share. */
    private final List<ItemStack> loot = new ArrayList<>();
    private int totalMeat = 1;
    /** Ticks left before it rots away. */
    private int life = 6000;

    public CarcassEntity(EntityType<? extends CarcassEntity> type, Level level) {
        super(type, level);
    }

    /** The carcass of a dinosaur that just died, holding its death loot. */
    public static CarcassEntity of(ServerLevel level, DinosaurEntity dino, List<ItemStack> loot) {
        CarcassEntity carcass = new CarcassEntity(ModEntities.CARCASS.get(), level);
        carcass.entityData.set(DATA_SPECIES, dino.speciesId());
        carcass.entityData.set(DATA_FEMALE, dino.isFemale());
        carcass.entityData.set(DATA_SCALE, dino.getScale());
        carcass.entityData.set(DATA_WIDTH, Math.max(0.6F, dino.getBbWidth() * 1.1F));
        carcass.entityData.set(DATA_HEIGHT, Math.max(0.4F, dino.getBbHeight() * 0.45F));
        int meat = Math.max(2, Math.round(dino.getBbWidth() * 4.0F));
        carcass.totalMeat = meat;
        carcass.entityData.set(DATA_MEAT, meat);
        carcass.life = 20 * (120 + Math.round(60.0F * dino.getBbWidth()));
        carcass.loot.addAll(loot);
        carcass.moveTo(dino.getX(), dino.getY(), dino.getZ(), dino.yBodyRot, 0.0F);
        carcass.refreshDimensions();
        return carcass;
    }

    // ------------------------------------------------------------------ data

    @Override
    protected void defineSynchedData() {
        this.entityData.define(DATA_SPECIES, "tyrannosaurus");
        this.entityData.define(DATA_FEMALE, false);
        this.entityData.define(DATA_WIDTH, 1.0F);
        this.entityData.define(DATA_HEIGHT, 0.5F);
        this.entityData.define(DATA_SCALE, 1.0F);
        this.entityData.define(DATA_MEAT, 1);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (DATA_WIDTH.equals(key) || DATA_HEIGHT.equals(key)) {
            this.refreshDimensions();
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.scalable(this.entityData.get(DATA_WIDTH), this.entityData.get(DATA_HEIGHT));
    }

    public String speciesId() {
        return this.entityData.get(DATA_SPECIES);
    }

    public boolean isFemale() {
        return this.entityData.get(DATA_FEMALE);
    }

    /** The dead animal's scale (a baby's carcass is small). */
    public float getModelScale() {
        return this.entityData.get(DATA_SCALE);
    }

    public int getMeat() {
        return this.entityData.get(DATA_MEAT);
    }

    public boolean hasMeat() {
        return this.getMeat() > 0;
    }

    @Override
    public Component getName() {
        return Component.translatable("entity.terrassic.carcass.of", Component.translatable("entity.terrassic." + this.speciesId()));
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        tag.putString("Species", this.speciesId());
        tag.putBoolean("Female", this.isFemale());
        tag.putFloat("Width", this.entityData.get(DATA_WIDTH));
        tag.putFloat("Height", this.entityData.get(DATA_HEIGHT));
        tag.putFloat("Scale", this.getModelScale());
        tag.putInt("Meat", this.getMeat());
        tag.putInt("TotalMeat", this.totalMeat);
        tag.putInt("Life", this.life);
        ListTag list = new ListTag();
        for (ItemStack stack : this.loot) {
            list.add(stack.save(new CompoundTag()));
        }
        tag.put("Loot", list);
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        this.entityData.set(DATA_SPECIES, tag.getString("Species"));
        this.entityData.set(DATA_FEMALE, tag.getBoolean("Female"));
        this.entityData.set(DATA_WIDTH, tag.getFloat("Width"));
        this.entityData.set(DATA_HEIGHT, tag.getFloat("Height"));
        this.entityData.set(DATA_SCALE, tag.contains("Scale") ? tag.getFloat("Scale") : 1.0F);
        this.entityData.set(DATA_MEAT, tag.getInt("Meat"));
        this.totalMeat = Math.max(1, tag.getInt("TotalMeat"));
        this.life = tag.getInt("Life");
        this.loot.clear();
        ListTag list = tag.getList("Loot", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            ItemStack stack = ItemStack.of(list.getCompound(i));
            if (!stack.isEmpty()) {
                this.loot.add(stack);
            }
        }
        this.refreshDimensions();
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return new ClientboundAddEntityPacket(this);
    }

    // ------------------------------------------------------------------ ticking: it lies there and rots

    @Override
    public void tick() {
        super.tick();
        if (!this.isNoGravity()) {
            this.setDeltaMovement(this.getDeltaMovement().add(0.0D, -0.04D, 0.0D));
        }
        this.move(MoverType.SELF, this.getDeltaMovement());
        this.setDeltaMovement(this.getDeltaMovement().multiply(0.6D, this.onGround() ? 0.0D : 1.0D, 0.6D));
        if (this.level().isClientSide()) {
            return;
        }
        if (--this.life <= 0) {
            this.finish(true);
        } else if (this.life < 1200 && this.tickCount % 20 == 0 && this.level() instanceof ServerLevel server) {
            // the last minute: flies
            server.sendParticles(ParticleTypes.ASH, this.getX(), this.getY() + this.getBbHeight(), this.getZ(), 3,
                    this.getBbWidth() * 0.3D, 0.2D, this.getBbWidth() * 0.3D, 0.0D);
        }
    }

    @Override
    public boolean isPickable() {
        return !this.isRemoved();
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean canBeCollidedWith() {
        return false;
    }

    // ------------------------------------------------------------------ harvesting and scavenging

    /** Hitting the carcass harvests it (players) or bites it (animals). */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (this.level().isClientSide() || this.isRemoved()) {
            return true;
        }
        if (source.getEntity() instanceof Player player) {
            this.harvest(player, InteractionHand.MAIN_HAND);
        } else if (source.getEntity() instanceof LivingEntity living) {
            this.bite(living);
        }
        return true;
    }

    @Override
    public InteractionResult interact(Player player, InteractionHand hand) {
        if (!this.level().isClientSide()) {
            this.harvest(player, hand);
        }
        return InteractionResult.sidedSuccess(this.level().isClientSide());
    }

    /** One share of the loot for the player (two with a tool), dropped at their feet. */
    private void harvest(Player player, InteractionHand hand) {
        if (!this.hasMeat()) {
            return;
        }
        ItemStack tool = player.getItemInHand(hand);
        int shares = tool.getItem() instanceof TieredItem ? 2 : 1;
        for (int i = 0; i < shares && this.hasMeat(); i++) {
            for (ItemStack stack : this.takeShare()) {
                ItemEntity drop = new ItemEntity(this.level(), player.getX(), player.getY() + 0.5D, player.getZ(), stack);
                drop.setDefaultPickUpDelay();
                this.level().addFreshEntity(drop);
            }
        }
        if (tool.getItem() instanceof TieredItem) {
            tool.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
        }
        this.splash();
        if (!this.hasMeat()) {
            this.finish(false);
        }
    }

    /** A scavenger's bite: the share is eaten (gone), the eater heals. */
    public void bite(LivingEntity eater) {
        if (!this.hasMeat()) {
            return;
        }
        this.takeShare();
        eater.heal(4.0F);
        if (eater instanceof DinosaurEntity dino) {
            dino.onAteCarrion();
        }
        this.splash();
        this.playSound(SoundEvents.GENERIC_EAT, 1.0F, 0.8F + this.random.nextFloat() * 0.3F);
        if (!this.hasMeat()) {
            this.finish(false);
        }
    }

    /** Takes one meat share: a proportional slice of the loot stacks (consumed or dropped by the caller). */
    private List<ItemStack> takeShare() {
        int meat = this.getMeat();
        List<ItemStack> share = new ArrayList<>();
        if (meat <= 0) {
            return share;
        }
        int stacks = this.loot.isEmpty() ? 0 : Math.max(1, (int) Math.ceil(this.loot.size() / (double) meat));
        for (int i = 0; i < stacks && !this.loot.isEmpty(); i++) {
            share.add(this.loot.remove(this.loot.size() - 1));
        }
        this.entityData.set(DATA_MEAT, meat - 1);
        return share;
    }

    private void splash() {
        if (this.level() instanceof ServerLevel server) {
            server.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, new ItemStack(Items.BEEF)),
                    this.getX(), this.getY() + this.getBbHeight() * 0.5D, this.getZ(), 8,
                    this.getBbWidth() * 0.3D, 0.2D, this.getBbWidth() * 0.3D, 0.05D);
        }
        this.playSound(SoundEvents.SLIME_SQUISH, 0.8F, 0.7F + this.random.nextFloat() * 0.3F);
    }

    /** Gone: whatever loot is left drops on the spot (nothing is lost to rot), then the body disappears. */
    private void finish(boolean rotted) {
        if (!this.level().isClientSide()) {
            for (ItemStack stack : this.loot) {
                this.spawnAtLocation(stack);
            }
            this.loot.clear();
            if (this.level() instanceof ServerLevel server) {
                server.sendParticles(rotted ? ParticleTypes.SMOKE : ParticleTypes.POOF, this.getX(), this.getY() + 0.3D, this.getZ(),
                        12, this.getBbWidth() * 0.4D, 0.2D, this.getBbWidth() * 0.4D, 0.02D);
            }
            this.playSound(rotted ? SoundEvents.COMPOSTER_FILL_SUCCESS : SoundEvents.SLIME_BLOCK_BREAK, 1.0F, 0.8F);
        }
        this.discard();
    }

    // ------------------------------------------------------------------ GeckoLib: the species' model, lying still

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "pose", 0, state -> {
            if (this.poseAnim == null) {
                this.poseAnim = RawAnimation.begin().thenLoop("animation." + this.speciesId() + ".knocked_out");
            }
            return state.setAndContinue(this.poseAnim);
        }));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.geoCache;
    }
}
