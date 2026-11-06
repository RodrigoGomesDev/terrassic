package com.terrassic.entity;

import java.util.Arrays;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Quetzalcoatlus rig (tools/modelgen/handmade/quetzalcoatlus, its own study). An azhdarchid: on top of
 * the pterosaur flight it lives on the ground like a giant stork (Witton &amp; Naish 2008):
 * <ul>
 *   <li>on the ground with a target it stalks: the slow hunting walk, the head low and held still ("stalk");</li>
 *   <li>its strike is the spear of the beak at prey on the ground; a kill is tossed up and swallowed whole ("eat");</li>
 *   <li>standing by water it now and then reaches its long neck down to drink ("drink").</li>
 * </ul>
 */
public abstract class Azhdarchid extends Pterosaur {
    private RawAnimation stalkLoop;
    private int drinkCooldown = 400;

    protected Azhdarchid(EntityType<? extends Azhdarchid> type, Level level) {
        super(type, level);
    }

    @Override
    protected String[] extraActions() {
        String[] base = super.extraActions();
        String[] out = Arrays.copyOf(base, base.length + 1);
        out[base.length] = "drink";
        return out;
    }

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving() && this.isAggressive() && !this.isAirborne() && !this.isVehicle() && !this.isInWater()
                && !this.isBaby()) {
            if (this.stalkLoop == null) {
                this.stalkLoop = RawAnimation.begin().thenLoop(anim("stalk"));
            }
            return state.setAndContinue(this.stalkLoop);
        }
        return super.movementAnimation(state);
    }

    /** A strike that kills: the prey is tossed up and swallowed whole. */
    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity living && !living.isAlive()) {
            triggerAnim(ACTION_CONTROLLER, "eat");
        }
        return hit;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.drinkCooldown > 0) {
            this.drinkCooldown--;
            return;
        }
        if (this.getTarget() == null && !this.isVehicle() && this.onGround() && !this.isInWater() && !this.isSleeping()
                && !this.isKnockedOut() && this.getNavigation().isDone() && this.random.nextInt(200) == 0 && this.nearWater()) {
            triggerAnim(ACTION_CONTROLLER, "drink");
            this.drinkCooldown = 1200;
        }
    }

    /** Water within reach of its neck round its feet. */
    private boolean nearWater() {
        // its neck reaches about twice its width (a 10 m animal standing three blocks from a pool did not drink)
        BlockPos feet = this.blockPosition();
        int r = Math.max(3, (int) Math.ceil(this.getBbWidth() * 2.0D));
        for (BlockPos p : BlockPos.betweenClosed(feet.offset(-r, -1, -r), feet.offset(r, 0, r))) {
            if (this.level().getFluidState(p).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }
}
