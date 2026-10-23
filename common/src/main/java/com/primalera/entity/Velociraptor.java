package com.primalera.entity;

import com.primalera.registry.ModEntities;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.LeapAtTargetGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;


/**
 * Velociraptor mongoliensis - fast feathered pack hunter. When one raptor
 * picks a target, the rest of the pack nearby joins in. Avoids T. rex.
 */
public class Velociraptor extends DinosaurEntity {
    private static final Ingredient FOOD = Ingredient.of(Items.CHICKEN, Items.RABBIT, Items.MUTTON, Items.BEEF, Items.PORKCHOP);
    private static boolean alertingPack;

    public Velociraptor(EntityType<? extends Velociraptor> type, Level level) {
        super(type, level);
        this.xpReward = 8;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Animal.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 24.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.34D)
                .add(Attributes.ATTACK_DAMAGE, 5.0D)
                .add(Attributes.FOLLOW_RANGE, 24.0D);
    }

    @Override
    public String speciesId() {
        return "velociraptor";
    }

    @Override
    protected double runThresholdSqr() {
        return 0.03D;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new AvoidEntityGoal<>(this, Tyrannosaurus.class, 14.0F, 1.2D, 1.5D));
        this.goalSelector.addGoal(2, new LeapAtTargetGoal(this, 0.4F));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.5D, true));
        this.goalSelector.addGoal(4, new BreedGoal(this, 1.0D));
        this.goalSelector.addGoal(5, new TemptGoal(this, 1.2D, FOOD, false));
        this.goalSelector.addGoal(6, new FollowParentGoal(this, 1.2D));
        this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.9D));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 10.0F));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 20, true, false,
                e -> this.canHunt()));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, Animal.class, 80, true, false,
                e -> this.canHunt() && e.getBbWidth() < 1.0F && !(e instanceof Velociraptor)));
    }

    @Override
    public void setTarget(LivingEntity target) {
        super.setTarget(target);
        if (target != null && !this.level().isClientSide() && !alertingPack) {
            alertingPack = true;
            try {
                for (Velociraptor other : this.level().getEntitiesOfClass(Velociraptor.class, this.getBoundingBox().inflate(16.0D),
                        r -> r != this && r != target && r.getTarget() == null && !r.isBaby())) {
                    other.setTarget(target);
                }
            } finally {
                alertingPack = false;
            }
        }
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return FOOD.test(stack);
    }

    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        return ModEntities.VELOCIRAPTOR.get().create(level);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.FOX_SCREECH;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.FOX_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.FOX_DEATH;
    }

    @Override
    public float getVoicePitch() {
        return super.getVoicePitch() * 0.8F;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }
}
