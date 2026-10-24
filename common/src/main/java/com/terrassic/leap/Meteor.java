package com.terrassic.leap;

import com.terrassic.config.WorldConfig;
import com.terrassic.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * A meteor of the ritual (v0.9): a burning rock that comes in at a slant from high up, leaving a trail of fire and
 * smoke, and bursts where it lands. The burst pushes and burns what is near (WorldConfig "meteor_damage") but never
 * breaks a block (Rule 0: the world is not destroyed). One in ten leaves a lump of raw amber, "a fallen star".
 */
public class Meteor extends Entity {
    private static final EntityDataAccessor<Float> DATA_SIZE = SynchedEntityData.defineId(Meteor.class, EntityDataSerializers.FLOAT);
    private static final double SPEED = 1.6D;
    private float power = 2.5F;
    private int life;

    public Meteor(EntityType<? extends Meteor> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    /** A meteor that lands between {@code min} and {@code max} blocks from {@code centre}. */
    public static void fallNear(ServerLevel level, BlockPos centre, double min, double max, float power) {
        RandomSource r = level.random;
        double a = r.nextDouble() * Math.PI * 2.0D;
        double d = min + r.nextDouble() * (max - min);
        int x = centre.getX() + (int) Math.round(Math.cos(a) * d);
        int z = centre.getZ() + (int) Math.round(Math.sin(a) * d);
        if (!level.hasChunkAt(new BlockPos(x, 0, z))) {
            return;
        }
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
        fallAt(level, new Vec3(x + 0.5D, y, z + 0.5D), power);
    }

    /** A meteor that lands on {@code target}, coming in from a random side at about 50 degrees. */
    public static Meteor fallAt(ServerLevel level, Vec3 target, float power) {
        Meteor m = LeapRegistry.METEOR.get().create(level);
        if (m == null) {
            return null;
        }
        RandomSource r = level.random;
        double a = r.nextDouble() * Math.PI * 2.0D;
        double height = 70.0D + r.nextDouble() * 20.0D;
        Vec3 start = target.add(Math.cos(a) * height * 0.8D, height, Math.sin(a) * height * 0.8D);
        m.setPos(start.x, Math.min(start.y, level.getMaxBuildHeight() + 40.0D), start.z);
        m.setDeltaMovement(target.subtract(m.position()).normalize().scale(SPEED));
        m.power = power;
        m.entityData.set(DATA_SIZE, 0.7F + power * 0.25F + r.nextFloat() * 0.4F);
        level.addFreshEntity(m);
        level.playSound(null, BlockPos.containing(target), SoundEvents.FIRECHARGE_USE, SoundSource.HOSTILE, 1.5F, 0.4F);
        return m;
    }

    public float size() {
        return this.entityData.get(DATA_SIZE);
    }

    @Override
    protected void defineSynchedData() {
        this.entityData.define(DATA_SIZE, 1.0F);
    }

    @Override
    public void tick() {
        super.tick();
        Vec3 v = this.getDeltaMovement();
        Vec3 next = this.position().add(v);
        if (this.level().isClientSide()) {
            this.setPos(next.x, next.y, next.z);
            this.trail();
            return;
        }
        if (++this.life > 400 || this.getY() < this.level().getMinBuildHeight()) {
            this.discard();
            return;
        }
        // land on the first solid block along the way (two samples per tick, it moves 1.6 blocks)
        for (int i = 1; i <= 2; i++) {
            Vec3 p = this.position().add(v.scale(i / 2.0D));
            BlockPos bp = BlockPos.containing(p);
            BlockState s = this.level().getBlockState(bp);
            boolean solid = !s.getCollisionShape(this.level(), bp).isEmpty() || !s.getFluidState().isEmpty();
            if (solid && this.level().hasChunkAt(bp)) {
                this.impact(p);
                return;
            }
        }
        this.setPos(next.x, next.y, next.z);
    }

    private void impact(Vec3 at) {
        ServerLevel level = (ServerLevel) this.level();
        if (WorldConfig.meteorDamage()) {
            level.explode(this, at.x, at.y + 0.5D, at.z, this.power, false, Level.ExplosionInteraction.NONE);
        } else {
            level.playSound(null, BlockPos.containing(at), SoundEvents.GENERIC_EXPLODE, SoundSource.HOSTILE, 3.0F, 0.8F);
            level.sendParticles(ParticleTypes.EXPLOSION, at.x, at.y + 0.5D, at.z, 3, 0.5D, 0.3D, 0.5D, 0.0D);
        }
        level.sendParticles(ParticleTypes.LAVA, at.x, at.y + 0.5D, at.z, 12, 0.6D, 0.2D, 0.6D, 0.0D);
        level.sendParticles(ParticleTypes.LARGE_SMOKE, at.x, at.y + 0.8D, at.z, 20, 0.8D, 0.6D, 0.8D, 0.02D);
        if (level.random.nextInt(10) == 0) {
            ItemEntity amber = new ItemEntity(level, at.x, at.y + 1.0D, at.z, new ItemStack(ModItems.RAW_AMBER.get()));
            amber.setDefaultPickUpDelay();
            level.addFreshEntity(amber);
        }
        this.discard();
    }

    /** Client: fire and smoke behind the rock, drawn from any distance (always-visible particles). */
    private void trail() {
        RandomSource r = this.random;
        Vec3 back = this.getDeltaMovement().normalize().scale(-0.6D);
        float s = this.size();
        for (int i = 0; i < 3; i++) {
            double ox = (r.nextDouble() - 0.5D) * s * 0.6D;
            double oy = (r.nextDouble() - 0.5D) * s * 0.6D;
            double oz = (r.nextDouble() - 0.5D) * s * 0.6D;
            this.level().addAlwaysVisibleParticle(ParticleTypes.FLAME, true, this.getX() + back.x * i + ox,
                    this.getY() + back.y * i + oy, this.getZ() + back.z * i + oz, back.x * 0.1D, back.y * 0.1D, back.z * 0.1D);
        }
        this.level().addAlwaysVisibleParticle(ParticleTypes.LARGE_SMOKE, true, this.getX() + back.x * 3, this.getY() + back.y * 3,
                this.getZ() + back.z * 3, 0.0D, 0.02D, 0.0D);
        if (r.nextInt(3) == 0) {
            this.level().addAlwaysVisibleParticle(ParticleTypes.LAVA, true, this.getX(), this.getY(), this.getZ(), 0.0D, 0.0D, 0.0D);
        }
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 256.0D * 256.0D;
    }

    @Override
    public boolean isOnFire() {
        return false;
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        this.power = tag.contains("Power") ? tag.getFloat("Power") : 2.5F;
        this.life = tag.getInt("Life");
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        tag.putFloat("Power", this.power);
        tag.putInt("Life", this.life);
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return new ClientboundAddEntityPacket(this);
    }
}
