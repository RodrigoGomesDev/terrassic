package com.terrassic.entity;

import com.terrassic.entity.ai.DinoSleepGoal;
import com.terrassic.entity.ai.FollowHerdGoal;
import com.terrassic.entity.ai.MigrateGoal;
import com.terrassic.entity.ai.OrderedFollowOwnerGoal;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
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

    /** Only a herbivore that fights back takes the aggressive stance. */
    @Override
    protected boolean fightsInStance() {
        return this.fightsBack();
    }

    /** 1.9.5: a herbivore lies down only with no predator awake within 32 blocks, nor one asleep within 28 (they slept
     *  side by side, 06/11); otherwise it first moves off (SafeRestGoal). */
    @Override
    public boolean safeToSleep() {
        return this.isTame() || (this.nearestPredator(32.0D, true) == null && this.nearestPredator(28.0D, false) == null);
    }

    /** Asleep, it wakes when a predator that is awake comes within 12 blocks (16 if it hunts). */
    @Override
    public boolean wokenByThreat() {
        DinosaurEntity p = this.nearestPredator(16.0D, true);
        return p != null && (p.getTarget() != null || p.distanceTo(this) < 12.0F);
    }

    /** A grown herbivore that fights back meets a big predator head on (horns, club, claws): a duel. */
    @Override
    public boolean fightsInDuel() {
        return this.fightsBack() && !this.isBaby();
    }

    /** false = flees instead of fighting back. */
    protected boolean fightsBack() {
        return true;
    }

    /** false = keeps its stance but fights with its own goal (the Ankylosaurus swings its tail instead of charging). */
    protected boolean usesMeleeGoal() {
        return true;
    }

    /** Whether a wild runner flees from this player (false lets the player come close, e.g. crouching with food). */
    protected boolean fleesFrom(Player player) {
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

    /** Hook for extra goals (avoid, flee...). Called at the end of {@link #registerGoals()}. */
    protected void addExtraGoals() {
    }

    /** Speed modifier of the idle wander (a species slows it so its walk cycle keeps up and the feet do not slide). */
    protected double strollSpeed() {
        return 0.8D;
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
                e -> !e.isSpectator() && !((Player) e).isCreative() && this.fleesFrom((Player) e)) {
            @Override
            public boolean canUse() {
                return !HerbivoreDinosaur.this.fightsBack() && !HerbivoreDinosaur.this.isTame() && super.canUse();
            }
        });
        this.goalSelector.addGoal(3, new AvoidEntityGoal<>(this, DinosaurEntity.class, 14.0F, 1.2D, 1.6D,
                e -> e instanceof PredatorDinosaur p && !p.isTame() && !p.isBaby()) {
            @Override
            public boolean canUse() {
                return !HerbivoreDinosaur.this.fightsBack() && !HerbivoreDinosaur.this.isTame() && super.canUse();
            }
        });
        this.goalSelector.addGoal(1, new com.terrassic.entity.ai.FleeHurtGoal(this));
        this.addDuelGoal(3);
        this.goalSelector.addGoal(3, new com.terrassic.entity.ai.SafeRestGoal(this));
        this.goalSelector.addGoal(4, new com.terrassic.entity.ai.HeadMeleeAttackGoal(this, 1.4D, true) {
            @Override
            public boolean canUse() {
                return HerbivoreDinosaur.this.fightsBack() && HerbivoreDinosaur.this.usesMeleeGoal() && super.canUse();
            }
        });
        this.goalSelector.addGoal(5, new OrderedFollowOwnerGoal(this, 1.15D, followStartDistance(), followStopDistance(), false));
        this.goalSelector.addGoal(6, new com.terrassic.entity.ai.DinoBreedGoal(this, 1.0D));
        this.goalSelector.addGoal(7, new TemptGoal(this, 1.1D, food(), false));
        this.goalSelector.addGoal(8, new FollowParentGoal(this, 1.1D));
        this.goalSelector.addGoal(8, new MigrateGoal(this));
        this.goalSelector.addGoal(8, new com.terrassic.entity.ai.WaterholeGoal(this));
        this.goalSelector.addGoal(8, new FollowHerdGoal(this));
        this.goalSelector.addGoal(9, new WaterAvoidingRandomStrollGoal(this, this.strollSpeed()));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Player.class, 10.0F));
        this.goalSelector.addGoal(11, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this).setAlertOthers());
        addExtraGoals();
    }

    /** Grazing: now and then, more often when hungry; if something edible grows within reach, it is a real meal. */
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.kickTick();
        if (this.getTarget() == null && !this.isVehicle() && !this.isInSittingPose() && !this.isSleeping()
                && this.getNavigation().isDone() && this.random.nextInt(this.isHungry() ? 150 : 700) == 0) {
            triggerAnim(ACTION_CONTROLLER, "graze");
            if (this.grazeEat()) {
                this.feed(8);
            }
        }
    }

    // ------------------------------------------------------------------ the runners' kick (06/11/2026)
    /** Runners that kick what bites them from behind and shove what comes at the flank (DePalma et al. 2013: an
     *  Edmontosaurus survived a tyrannosaur's bite): the tick each blow lands (kick_back, body_shove). */
    private static final java.util.Map<String, int[]> KICKS = java.util.Map.of(
            "gallimimus", new int[]{9, 0}, "parasaurolophus", new int[]{11, 12}, "edmontosaurus", new int[]{13, 13});
    private LivingEntity kickAt;
    private int kickIn;
    private int kickCooldown;

    private void kickBackFor(LivingEntity attacker) {
        int[] k = KICKS.get(this.speciesId());
        if (k == null || this.kickCooldown > 0 || this.isBaby() || this.isTame() || this.isVehicle() || this.distanceTo(attacker) > this.getBbWidth() + attacker.getBbWidth() + 2.0F) {
            return;
        }
        double dx = attacker.getX() - this.getX();
        double dz = attacker.getZ() - this.getZ();
        float off = Math.abs(net.minecraft.util.Mth.wrapDegrees((float) (net.minecraft.util.Mth.atan2(dz, dx) * net.minecraft.util.Mth.RAD_TO_DEG) - 90.0F - this.yBodyRot));
        if (off > 120.0F && this.random.nextFloat() < 0.6F) {
            triggerAnim(ACTION_CONTROLLER, "kick_back");
            this.kickIn = k[0];
        } else if (k[1] > 0 && off > 50.0F && off <= 120.0F && this.random.nextFloat() < 0.4F) {
            triggerAnim(ACTION_CONTROLLER, "body_shove");
            this.kickIn = k[1];
        } else {
            return;
        }
        this.kickAt = attacker;
        this.kickCooldown = 50;
    }

    private void kickTick() {
        if (this.kickCooldown > 0) {
            this.kickCooldown--;
        }
        if (this.kickIn > 0 && --this.kickIn == 0 && this.kickAt != null && this.kickAt.isAlive()
                && this.distanceTo(this.kickAt) < this.getBbWidth() + this.kickAt.getBbWidth() + 2.5F) {
            this.kickAt.hurt(this.damageSources().mobAttack(this), (float) Math.max(2.0D, this.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE)));
            this.kickAt.knockback(1.0D, this.getX() - this.kickAt.getX(), this.getZ() - this.kickAt.getZ());
            this.kickAt = null;
        }
    }

    /** A runner that is hurt sets the whole herd running: the others take the attacker as the one who hurt them. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && source.getEntity() instanceof LivingEntity kicker) {
            this.kickBackFor(kicker);
        }
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
