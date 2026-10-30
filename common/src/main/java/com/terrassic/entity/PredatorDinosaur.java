package com.terrassic.entity;

import com.terrassic.entity.ai.DinoSleepGoal;
import com.terrassic.entity.ai.EatCarcassGoal;
import com.terrassic.entity.ai.FollowHerdGoal;
import com.terrassic.entity.ai.FollowOwnerPathGoal;
import com.terrassic.entity.ai.OrderedFollowOwnerGoal;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;

/**
 * Meat eaters. Wild adults hunt players (not on Peaceful) and their prey; they can only be tamed as babies
 * (hand-feeding a baby, or hatching an egg next to you). Tamed predators follow and defend their owner.
 */
public abstract class PredatorDinosaur extends DinosaurEntity {
    protected PredatorDinosaur(EntityType<? extends PredatorDinosaur> type, Level level) {
        super(type, level);
    }

    /** Breeding / taming food. Must return a static constant (used during construction). */
    protected abstract Ingredient food();

    /** Which animals a wild adult hunts. */
    protected abstract boolean isPrey(LivingEntity entity);

    /** Whether wild adults attack players on sight. */
    protected boolean huntsPlayers() {
        return true;
    }

    protected double attackSpeed() {
        return 1.35D;
    }

    /** Lower = hunts prey more often (it is the random interval of the target goal). */
    protected int preyInterval() {
        return 120;
    }

    @Override
    public TameMethod tameMethod() {
        return TameMethod.BABY_FEEDING;
    }

    /** Every meat eater takes carrion (docs/CARCACAS.md). */
    @Override
    protected boolean scavenges() {
        return true;
    }

    /** Solitary hunters keep no herd (no FollowHerdGoal). Called during construction: return a constant. */
    protected boolean solitary() {
        return false;
    }

    /** The fight itself (priority 3): the vanilla melee by default. */
    protected Goal createAttackGoal() {
        return new MeleeAttackGoal(this, attackSpeed(), true);
    }

    /** Hook for extra goals (leap, avoid...). Called at the end of {@link #registerGoals()}. */
    protected void addExtraGoals() {
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(1, new DinoSleepGoal(this));
        this.goalSelector.addGoal(2, new EatCarcassGoal(this));
        this.goalSelector.addGoal(3, this.createAttackGoal());
        float stop = Math.max(2.0F, this.getBbWidth() * 1.5F);
        this.goalSelector.addGoal(4, this.getNavigation() instanceof GroundPathNavigation
                || this.getNavigation() instanceof FlyingPathNavigation
                ? new OrderedFollowOwnerGoal(this, 1.2D, 10.0F, stop, false)
                : new FollowOwnerPathGoal(this, 1.2D, 10.0F, stop));
        this.goalSelector.addGoal(5, new BreedGoal(this, 1.0D));
        this.goalSelector.addGoal(6, new TemptGoal(this, 1.1D, food(), false));
        this.goalSelector.addGoal(7, new FollowParentGoal(this, 1.1D));
        if (!this.solitary()) {
            this.goalSelector.addGoal(7, new FollowHerdGoal(this));
        }
        this.goalSelector.addGoal(8, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 16.0F));
        this.goalSelector.addGoal(10, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this).setAlertOthers());
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false,
                e -> this.huntsPlayers() && this.canHunt()) {
            @Override
            public boolean canUse() {
                return PredatorDinosaur.this.huntsPlayers() && PredatorDinosaur.this.canHunt() && super.canUse();
            }
        });
        this.targetSelector.addGoal(5, new NearestAttackableTargetGoal<>(this, Animal.class, preyInterval(), true, false,
                e -> this.canHunt() && this.isPrey(e)) {
            @Override
            public boolean canUse() {
                return PredatorDinosaur.this.canHunt() && super.canUse();
            }
        });
        addExtraGoals();
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return food().test(stack);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.isVehicle() && this.getTarget() != null) {
            this.setTarget(null);
        }
        // the pack: a wild hunter with a target brings the idle hunters of its species nearby onto it
        if (this.packHunter() && !this.isTame() && this.getTarget() != null && (this.tickCount + this.getId()) % 20 == 0) {
            for (PredatorDinosaur other : this.level().getEntitiesOfClass(this.getClass(), this.getBoundingBox().inflate(16.0D),
                    e -> e != this && !e.isTame() && !e.isBaby() && e.getTarget() == null && e.canHunt())) {
                other.setTarget(this.getTarget());
            }
        }
    }
}
