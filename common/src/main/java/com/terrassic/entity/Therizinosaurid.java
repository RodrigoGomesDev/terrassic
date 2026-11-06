package com.terrassic.entity;

import java.util.List;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * The hand-made Therizinosaurus rig (tools/modelgen/handmade/therizinosaurus, its own study, page "Terizinossauro:
 * estudo e modelo"). What it adds over a plain herbivore is only what those animations need:
 * <ul>
 *   <li>its grazing is the high browse: it hooks a branch with the claws, pulls it to the beak and strips it (the young
 *       copy it on low bushes);</li>
 *   <li>a wild adult facing a wild predator within 14 blocks stops, rears and spreads its arms with the quill fans
 *       open and the six blades out ("claw_display"); a player who walks up to a wild one gets the short warning
 *       ("threat") first;</li>
 *   <li>it fights with the arms: the slash, now and then the scissor cut with both arms, and the chest shove when the
 *       target is pressed against it;</li>
 *   <li>two adult males close together face off with the arms open, never touching, until one turns its head away;
 *       idle, it now and then preens the quills of its arm, sniffs, shakes or calls.</li>
 * </ul>
 * Gameplay is unchanged: these are gestures, timed so they never fight the attack or the eating.
 */
public abstract class Therizinosaurid extends HerbivoreDinosaur {
    /** The cycles (therianims.py, the Plan's walk and run): pixels of ground each covers at 24 px/m and its length in ticks. */
    private static final double WALK_PX = 56.0D;
    private static final double WALK_TICKS = 44.0D;
    private static final double RUN_PX = 96.0D;
    private static final double RUN_TICKS = 22.0D;
    private int displayCooldown;
    private int warnCooldown;
    private int still;

    protected Therizinosaurid(EntityType<? extends Therizinosaurid> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "claw_display", "threat", "rival", "preen", "scissor", "shove", "call", "sniff", "shake",
                "look_back", "stretch"};
    }

    /** Its grazing is the high browse (the young: the low one). */
    @Override
    protected String actionAnimation(String trigger) {
        if ("graze".equals(trigger)) {
            return this.isBaby() ? "baby_browse" : "browse";
        }
        return super.actionAnimation(trigger);
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
        return 60;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** One hit in three is the scissor cut; a target pressed against it gets the chest shove (the animation only). */
    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.isBaby()) {
            double close = this.getBbWidth() * 0.5D + target.getBbWidth() * 0.5D + 0.6D;
            if (this.distanceToSqr(target) < close * close && this.random.nextInt(3) == 0) {
                triggerAnim(ACTION_CONTROLLER, "shove");
            } else if (this.random.nextInt(3) == 0) {
                triggerAnim(ACTION_CONTROLLER, "scissor");
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
        if (this.warnCooldown > 0) {
            this.warnCooldown--;
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut()) {
            return;
        }
        if (!this.isTame() && !this.isBaby() && this.tickCount % 20 == 0) {
            if (this.displayCooldown == 0) {
                List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(14.0D),
                        p -> p.isAlive() && !p.isTame() && !p.isBaby());
                if (!near.isEmpty()) {
                    this.getLookControl().setLookAt(near.get(0), 30.0F, 30.0F);
                    triggerAnim(ACTION_CONTROLLER, "claw_display");
                    this.still = 68;
                    this.displayCooldown = 400;
                    return;
                }
            }
            if (this.warnCooldown == 0) {
                Player player = this.level().getNearestPlayer(this, 8.0D);
                if (player != null && !player.isCreative() && !player.isSpectator() && this.hasLineOfSight(player)) {
                    this.getLookControl().setLookAt(player, 30.0F, 30.0F);
                    triggerAnim(ACTION_CONTROLLER, "threat");
                    this.still = 40;
                    this.warnCooldown = 600;
                    return;
                }
            }
        }
        if (!this.getNavigation().isDone() || this.isBaby() || this.random.nextInt(800) != 0) {
            return;
        }
        Therizinosaurid other = this.nearestAdult(6.0D);
        if (other != null && !this.isFemale() && !other.isFemale() && !other.isSleeping() && other.getTarget() == null
                && !other.isVehicle() && this.random.nextBoolean()) {
            this.getLookControl().setLookAt(other, 30.0F, 30.0F);
            other.getLookControl().setLookAt(this, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "rival");
            other.triggerAnim(ACTION_CONTROLLER, "rival");
            this.still = 96;
            other.still = 96;
            return;
        }
        switch (this.random.nextInt(5)) {
            case 0 -> triggerAnim(ACTION_CONTROLLER, "preen");
            case 1 -> triggerAnim(ACTION_CONTROLLER, "sniff");
            case 2 -> triggerAnim(ACTION_CONTROLLER, "shake");
            case 3 -> triggerAnim(ACTION_CONTROLLER, "look_back");
            default -> {
                if (this.nearestAdult(24.0D) != null) {
                    triggerAnim(ACTION_CONTROLLER, "call");
                    this.playAmbientSound();
                } else {
                    triggerAnim(ACTION_CONTROLLER, "stretch");
                }
            }
        }
    }

    private Therizinosaurid nearestAdult(double range) {
        Therizinosaurid best = null;
        double bestD = Double.MAX_VALUE;
        for (Therizinosaurid e : this.level().getEntitiesOfClass(Therizinosaurid.class, this.getBoundingBox().inflate(range),
                e -> e != this && e.isAlive() && !e.isBaby())) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }
}
