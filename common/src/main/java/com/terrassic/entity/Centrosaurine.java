package com.terrassic.entity;

import java.util.List;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Styracosaurus rig (tools/modelgen/handmade/styracosaurus, its own study, page "Estiracossauro: estudo
 * para a 1.8", and 25 animations). What it adds over a plain herbivore is only what those animations need:
 * <ul>
 *   <li>the walk and the gallop follow the real speed (the feet do not slide); with a target it gallops in the
 *       "charge", the head low and the nose horn pointing ahead;</li>
 *   <li>when it first takes a target that is still some way off it stops and scrapes the ground with a forefoot
 *       before the charge ("paw_scrape");</li>
 *   <li>about one hit in three is the side hook of the horn instead of the gore;</li>
 *   <li>a wild adult facing a wild predator within 14 blocks stops, turns to it and shows its crown of spikes
 *       ("crown_display"): the frill is for show (Padian &amp; Horner 2011);</li>
 *   <li>two adult males close together stand side by side and show their crowns, never touching; two calves push
 *       frill against frill; idle, it now and then rubs its nose horn on the ground, shakes the flies off its crown
 *       or calls the herd.</li>
 * </ul>
 * Gameplay is unchanged: these are gestures, timed so they never fight the attack or the eating.
 */
public abstract class Centrosaurine extends HerbivoreDinosaur {
    /** The cycles (styracoanims.py WALK, RUNP, CHARGEP): pixels of ground each covers at 32 px/m and its length in ticks. */
    private static final double WALK_PX = 40.0D;
    private static final double WALK_TICKS = 23.0D;
    private static final double RUN_PX = 96.0D;
    private static final double RUN_TICKS = 11.2D;
    private static final double CHARGE_PX = 104.0D;
    private static final double CHARGE_TICKS = 10.0D;
    private RawAnimation chargeAnim;
    private LivingEntity lastTarget;
    private int displayCooldown;
    private int still;

    protected Centrosaurine(EntityType<? extends Centrosaurine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "horn_hook", "paw_scrape", "crown_display", "rival_display", "horn_rub", "head_shake",
                "call", "frill_shove", "nose_jab"};
    }

    @Override
    protected boolean hasSleepAnim() {
        return true;
    }

    @Override
    protected boolean hasSwimAnim() {
        return true;
    }

    @Override
    protected boolean flinches() {
        return true;
    }

    @Override
    protected int deathAnimTicks() {
        return 52;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** With a target it charges: the gallop with the horn levelled. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving() && this.isAggressive() && !this.isVehicle() && !this.isBaby() && !this.isKnockedOut()
                && !this.isSleeping() && !this.isInSittingPose() && !this.isSwimmingDeep()) {
            if (this.chargeAnim == null) {
                this.chargeAnim = RawAnimation.begin().thenLoop(anim("charge"));
            }
            this.cycleSpeed = this.gaitSpeed(CHARGE_PX / 16.0D / CHARGE_TICKS * this.modelScale());
            return state.setAndContinue(this.chargeAnim);
        }
        return super.movementAnimation(state);
    }

    /** About one hit in three is the side hook of the horn (the animation only: the damage is the same). */
    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.isBaby()) {
            int r = this.random.nextInt(3);
            if (r == 0) {
                triggerAnim(ACTION_CONTROLLER, "horn_hook");
            } else if (r == 1) {
                triggerAnim(ACTION_CONTROLLER, "nose_jab");    // 06/11: the short stab of the nose horn (styraflow.py)
            }
        }
        return hit;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.displayCooldown > 0) {
            this.displayCooldown--;
        }
        LivingEntity target = this.getTarget();
        // a new target some way off: it stops and scrapes the ground before it charges
        if (target != null && target != this.lastTarget && !this.isVehicle() && !this.isBaby() && this.distanceToSqr(target) > 36.0D) {
            this.getLookControl().setLookAt(target, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "paw_scrape");
            this.still = 30;
        }
        this.lastTarget = target;
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            if (target != null) {
                this.getLookControl().setLookAt(target, 30.0F, 30.0F);
            }
            return;
        }
        if (target != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut()) {
            return;
        }
        if (!this.isTame() && !this.isBaby() && this.displayCooldown == 0 && this.tickCount % 20 == 0) {
            List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(14.0D),
                    p -> p.isAlive() && !p.isTame() && !p.isBaby());
            if (!near.isEmpty()) {
                this.getLookControl().setLookAt(near.get(0), 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "crown_display");
                this.still = 66;
                this.displayCooldown = 400;
                return;
            }
        }
        if (!this.getNavigation().isDone()) {
            return;
        }
        if (this.isBaby()) {
            if (this.random.nextInt(2400) == 0) {
                Centrosaurine other = this.nearest(3.0D, true);
                if (other != null && !other.isSleeping()) {
                    this.getLookControl().setLookAt(other, 30.0F, 30.0F);
                    other.getLookControl().setLookAt(this, 30.0F, 30.0F);
                    triggerAnim(ACTION_CONTROLLER, "frill_shove");
                    other.triggerAnim(ACTION_CONTROLLER, "frill_shove");
                }
            }
            return;
        }
        if (this.random.nextInt(700) != 0) {
            return;
        }
        Centrosaurine other = this.nearest(5.0D, false);
        if (other != null && !this.isFemale() && !other.isFemale() && !other.isSleeping() && other.getTarget() == null
                && !other.isVehicle() && this.random.nextBoolean()) {
            this.getLookControl().setLookAt(other, 30.0F, 30.0F);
            other.getLookControl().setLookAt(this, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "rival_display");
            other.triggerAnim(ACTION_CONTROLLER, "rival_display");
            this.still = 72;
            other.still = 72;
            return;
        }
        switch (this.random.nextInt(3)) {
            case 0 -> triggerAnim(ACTION_CONTROLLER, "horn_rub");
            case 1 -> triggerAnim(ACTION_CONTROLLER, "head_shake");
            default -> {
                // the call only when there are others of its kind around to hear it
                if (this.nearest(24.0D, false) != null) {
                    triggerAnim(ACTION_CONTROLLER, "call");
                    this.playAmbientSound();
                }
            }
        }
    }

    private Centrosaurine nearest(double range, boolean baby) {
        Centrosaurine best = null;
        double bestD = Double.MAX_VALUE;
        for (Centrosaurine e : this.level().getEntitiesOfClass(Centrosaurine.class, this.getBoundingBox().inflate(range),
                e -> e != this && e.isAlive() && e.isBaby() == baby)) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }
}
