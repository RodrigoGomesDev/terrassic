package com.primalera.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.util.RandomSource;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Base class of every PrimalEra dinosaur.
 *
 * Animations live in assets/primalera/animations/entity/&lt;species&gt;.animation.json
 * and are named "animation.&lt;species&gt;.&lt;name&gt;". Every species provides
 * idle / walk / run / attack; extra one-shot actions (roar, graze...) are
 * listed by {@link #extraActions()} and fired from the server with
 * {@link #triggerAnim(String, String)}.
 */
public abstract class DinosaurEntity extends Animal implements GeoEntity {
    public static final String ACTION_CONTROLLER = "action";

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private RawAnimation idleAnim;
    private RawAnimation walkAnim;
    private RawAnimation runAnim;

    protected DinosaurEntity(EntityType<? extends DinosaurEntity> type, Level level) {
        super(type, level);
    }

    /** Species id, used for asset and animation names. */
    public abstract String speciesId();

    /** Extra one-shot animations besides "attack". */
    protected String[] extraActions() {
        return new String[0];
    }

    /** Squared horizontal speed (blocks/tick) above which the run cycle is used. */
    protected double runThresholdSqr() {
        return 0.012D;
    }

    /** How far the model sticks out of the hitbox (blocks), for frustum culling. */
    protected double cullingInflate() {
        return 1.0D;
    }

    protected String anim(String name) {
        return "animation." + speciesId() + "." + name;
    }

    /** Predators only hunt when grown up and when the world is not on Peaceful. */
    protected boolean canHunt() {
        return !this.isBaby() && this.level().getDifficulty() != Difficulty.PEACEFUL;
    }

    // ------------------------------------------------------------------ GeckoLib

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        this.idleAnim = RawAnimation.begin().thenLoop(anim("idle"));
        this.walkAnim = RawAnimation.begin().thenLoop(anim("walk"));
        this.runAnim = RawAnimation.begin().thenLoop(anim("run"));

        controllers.add(new AnimationController<>(this, "movement", 6, this::movementAnimation));

        AnimationController<DinosaurEntity> action = new AnimationController<>(this, ACTION_CONTROLLER, 3, state -> PlayState.STOP);
        action.triggerableAnim("attack", RawAnimation.begin().thenPlay(anim("attack")));
        for (String extra : extraActions()) {
            action.triggerableAnim(extra, RawAnimation.begin().thenPlay(anim(extra)));
        }
        controllers.add(action);
    }

    private PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving()) {
            boolean running = this.isAggressive() || this.getDeltaMovement().horizontalDistanceSqr() > runThresholdSqr();
            return state.setAndContinue(running ? this.runAnim : this.walkAnim);
        }
        return state.setAndContinue(this.idleAnim);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.geoCache;
    }

    // ------------------------------------------------------------------ behaviour

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.level().isClientSide()) {
            triggerAnim(ACTION_CONTROLLER, "attack");
        }
        return hit;
    }

    @Override
    public boolean removeWhenFarAway(double distanceToClosestPlayer) {
        return false;
    }

    @Override
    public AABB getBoundingBoxForCulling() {
        return this.getBoundingBox().inflate(cullingInflate());
    }

    /** Spawn rule: like animals, but also allows sand, terracotta, coarse dirt and podzol. */
    public static boolean checkDinoSpawnRules(EntityType<? extends DinosaurEntity> type, LevelAccessor level,
                                              MobSpawnType reason, BlockPos pos, RandomSource random) {
        BlockState below = level.getBlockState(pos.below());
        boolean ground = below.is(BlockTags.ANIMALS_SPAWNABLE_ON) || below.is(BlockTags.SAND)
                || below.is(BlockTags.TERRACOTTA) || below.is(Blocks.COARSE_DIRT) || below.is(Blocks.PODZOL);
        return ground && level.getRawBrightness(pos, 0) > 8;
    }
}
