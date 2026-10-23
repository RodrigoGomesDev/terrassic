package com.primalera.entity;

import com.primalera.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
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
import net.minecraft.world.level.block.state.BlockState;

/**
 * Tyrannosaurus rex - apex predator. Hostile to players (except on Peaceful)
 * and hunts large animals. Roars when it locks onto a new target.
 */
public class Tyrannosaurus extends DinosaurEntity {
    private static final Ingredient FOOD = Ingredient.of(Items.BEEF, Items.PORKCHOP, Items.MUTTON);
    private int roarCooldown;

    public Tyrannosaurus(EntityType<? extends Tyrannosaurus> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.5F);
        this.xpReward = 40;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Animal.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 160.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.24D)
                .add(Attributes.ATTACK_DAMAGE, 16.0D)
                .add(Attributes.ATTACK_KNOCKBACK, 1.5D)
                .add(Attributes.ARMOR, 6.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.9D)
                .add(Attributes.FOLLOW_RANGE, 32.0D);
    }

    @Override
    public String speciesId() {
        return "tyrannosaurus";
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"roar"};
    }

    @Override
    protected double cullingInflate() {
        return 3.5D;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.35D, true));
        this.goalSelector.addGoal(2, new BreedGoal(this, 1.0D));
        this.goalSelector.addGoal(3, new TemptGoal(this, 1.1D, FOOD, false));
        this.goalSelector.addGoal(4, new FollowParentGoal(this, 1.1D));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0F));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false,
                e -> this.canHunt()));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, Animal.class, 200, true, false,
                e -> this.canHunt() && !(e instanceof Tyrannosaurus) && !(e instanceof Compsognathus) && !e.isBaby()));
    }

    @Override
    public void setTarget(LivingEntity target) {
        LivingEntity previous = this.getTarget();
        super.setTarget(target);
        if (!this.level().isClientSide() && target != null && previous == null && this.roarCooldown <= 0) {
            this.roarCooldown = 400;
            triggerAnim(ACTION_CONTROLLER, "roar");
            this.playSound(SoundEvents.RAVAGER_ROAR, 3.0F, 0.55F);
        }
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.roarCooldown > 0) {
            this.roarCooldown--;
        }
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return FOOD.test(stack);
    }

    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        return ModEntities.TYRANNOSAURUS.get().create(level);
    }

    @Override
    public int getMaxHeadYRot() {
        return 35;
    }

    @Override
    public int getMaxHeadXRot() {
        return 25;
    }

    // ------------------------------------------------------------------ sounds (vanilla placeholders)

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.RAVAGER_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.RAVAGER_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.RAVAGER_DEATH;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        this.playSound(SoundEvents.RAVAGER_STEP, 0.9F, 0.6F);
    }

    @Override
    protected float getSoundVolume() {
        return 2.0F;
    }

    @Override
    public float getVoicePitch() {
        return super.getVoicePitch() * 0.6F;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 240;
    }
}
