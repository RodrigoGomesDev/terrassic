package com.terrassic.entity;

import com.terrassic.entity.ai.DinoSleepGoal;
import com.terrassic.entity.ai.FollowHerdGoal;
import com.terrassic.entity.ai.MigrateGoal;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowOwnerGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;

/**
 * Plant eaters. Fighters (Triceratops, Stegosaurus, Ankylosaurus, Brachiosaurus, Pachycephalosaurus) defend
 * themselves as a herd; runners (Parasaurolophus, Gallimimus) flee from players and predators instead.
 * Babies always run away. They graze now and then, are tamed by hand-feeding and defend their owner.
 */
public abstract class HerbivoreDinosaur extends DinosaurEntity {
    protected HerbivoreDinosaur(EntityType<? extends HerbivoreDinosaur> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.25F);
    }

    /** Breeding / taming food. Must return a static constant (used during construction). */
    protected abstract Ingredient food();

    /** false = flees instead of fighting back. */
    protected boolean fightsBack() {
        return true;
    }

    /** Distance at which a tamed animal starts following its owner. */
    protected float followStartDistance() {
        return 10.0F;
    }

    protected float followStopDistance() {
        return Math.max(2.0F, this.getBbWidth() * 1.5F);
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"graze"};
    }

    @Override
    protected boolean grazes() {
        return true;
    }

    @Override
    protected double cullingInflate() {
        return 2.5D;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(1, new DinoSleepGoal(this));
        this.goalSelector.addGoal(2, new PanicGoal(this, 1.6D) {
            @Override
            public boolean canUse() {
                return (HerbivoreDinosaur.this.isBaby() || !HerbivoreDinosaur.this.fightsBack()) && super.canUse();
            }
        });
        this.goalSelector.addGoal(3, new AvoidEntityGoal<>(this, Player.class, 10.0F, 1.2D, 1.5D,
                e -> !this.fightsBack() && !this.isTame() && !e.isSpectator() && !((Player) e).isCreative()));
        this.goalSelector.addGoal(3, new AvoidEntityGoal<>(this, DinosaurEntity.class, 14.0F, 1.2D, 1.6D,
                e -> !this.fightsBack() && e instanceof PredatorDinosaur p && !p.isTame() && !p.isBaby()));
        this.goalSelector.addGoal(4, new MeleeAttackGoal(this, 1.4D, true) {
            @Override
            public boolean canUse() {
                return HerbivoreDinosaur.this.fightsBack() && super.canUse();
            }
        });
        this.goalSelector.addGoal(5, new FollowOwnerGoal(this, 1.15D, followStartDistance(), followStopDistance(), false));
        this.goalSelector.addGoal(6, new BreedGoal(this, 1.0D));
        this.goalSelector.addGoal(7, new TemptGoal(this, 1.1D, food(), false));
        this.goalSelector.addGoal(8, new FollowParentGoal(this, 1.1D));
        this.goalSelector.addGoal(8, new MigrateGoal(this));
        this.goalSelector.addGoal(8, new FollowHerdGoal(this));
        this.goalSelector.addGoal(9, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Player.class, 10.0F));
        this.goalSelector.addGoal(11, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this).setAlertOthers());
    }

    /** Grazing: now and then, more often when hungry; if something edible grows within reach, it is a real meal. */
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.getTarget() == null && !this.isVehicle() && !this.isInSittingPose() && !this.isSleeping()
                && this.getNavigation().isDone() && this.random.nextInt(this.isHungry() ? 150 : 700) == 0) {
            triggerAnim(ACTION_CONTROLLER, "graze");
            if (this.grazeNearby()) {
                this.feed(8);
            }
        }
    }

    /** A runner that is hurt sets the whole herd running: the others take the attacker as the one who hurt them. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && !this.isTame() && !this.fightsBack() && source.getEntity() instanceof LivingEntity attacker) {
            for (HerbivoreDinosaur other : this.level().getEntitiesOfClass(this.getClass(), this.getBoundingBox().inflate(16.0D),
                    e -> e != this && !e.isTame() && e.getLastHurtByMob() == null)) {
                other.setLastHurtByMob(attacker);
                other.setSleeping(false);
            }
        }
        return hurt;
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return food().test(stack);
    }

    @Override
    public int getMaxHeadYRot() {
        return 30;
    }

    @Override
    public int getMaxHeadXRot() {
        return 20;
    }
}
