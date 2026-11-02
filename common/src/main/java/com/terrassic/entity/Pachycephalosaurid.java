package com.terrassic.entity;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

/**
 * The hand-made Pachycephalosaurus rig (tools/modelgen/handmade/pachycephalosaurus, its own study and 23 animations).
 * What it adds over a plain herbivore is only what those animations and the study need:
 * <ul>
 *   <li>the walk and the run follow the real speed (the feet do not slide);</li>
 *   <li>about one hit in three is the side blow of the dome into the flank ("flank_butt", Carpenter 1997);</li>
 *   <li>two wild adult males close together now and then clash dome to dome ("dome_clash", Peterson et al. 2013):
 *       a hollow knock at the hit and both are pushed back a little; a male near a female shows his dome
 *       ("dome_display");</li>
 *   <li>its own taming: a wild adult does not run from a player, but one who comes within 4 blocks WITHOUT its food in
 *       hand is warned (head down, a foot scuffing: "warn"), and if they stay close they are shoved away with the side
 *       of the dome, without damage. With its food in hand it lets them come and feed it;</li>
 *   <li>idle: it sniffs along the forest floor ("sniff") or rises to pick from a berry bush or low leaves in front of
 *       it ("pluck", a small meal); the young bounce at play ("hop_play").</li>
 * </ul>
 * The growth series is in the model: the renderer hides "adult_dome" on babies and shows them "young_spikes", and
 * shows the taller crown only on adult males (DinoGeoModel). Not rideable: no saddle.
 */
public abstract class Pachycephalosaurid extends HerbivoreDinosaur {
    /** The cycles (pachyanims.py WALK, RUN): pixels of ground each covers at 32 px/m and its length in ticks. */
    private static final double WALK_PX = 44.0D;
    private static final double WALK_TICKS = 22.0D;
    private static final double RUN_PX = 100.0D;
    private static final double RUN_TICKS = 11.0D;
    /** Ticks from the start of "dome_clash" to the moment the domes meet (1.65 s). */
    private static final int CLASH_HIT = 33;
    private int still;
    private int warnCooldown;
    private int warnLeft;
    private Player warned;
    private Pachycephalosaurid clashWith;
    private int clashTick = -1;

    protected Pachycephalosaurid(EntityType<? extends Pachycephalosaurid> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "flank_butt", "dome_clash", "dome_display", "warn", "sniff", "pluck", "hop_play"};
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

    /** About one hit in three is the side blow of the dome (the animation only: the damage is the same). */
    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && !this.isBaby() && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "flank_butt");
        }
        return hit;
    }

    private boolean holdsFood(Player player) {
        return this.isFood(player.getMainHandItem()) || this.isFood(player.getOffhandItem());
    }

    private boolean busy() {
        return this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut();
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.warnCooldown > 0) {
            this.warnCooldown--;
        }
        this.tickClash();
        if (this.warnLeft > 0) {
            this.tickWarning();
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.busy()) {
            return;
        }
        // the warning: a wild adult and a player close by without its food in hand
        if (!this.isTame() && !this.isBaby() && this.warnCooldown == 0 && this.tickCount % 10 == 0) {
            Player p = this.level().getNearestPlayer(this, 4.0D);
            if (p != null && !p.isCreative() && !p.isSpectator() && !this.holdsFood(p) && this.hasLineOfSight(p)) {
                this.getLookControl().setLookAt(p, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "warn");
                this.warned = p;
                this.warnLeft = 40;
                this.still = 40;
                this.warnCooldown = 160;
                return;
            }
        }
        if (!this.getNavigation().isDone()) {
            return;
        }
        if (this.isBaby()) {
            if (this.random.nextInt(400) == 0) {
                triggerAnim(ACTION_CONTROLLER, "hop_play");
                this.still = 32;
            }
            return;
        }
        if (this.random.nextInt(600) != 0) {
            return;
        }
        if (!this.isTame() && !this.isFemale()) {
            Pachycephalosaurid other = this.nearestAdult(5.0D);
            if (other != null && !other.isTame() && !other.busy() && other.clashTick < 0) {
                this.getLookControl().setLookAt(other, 30.0F, 30.0F);
                other.getLookControl().setLookAt(this, 30.0F, 30.0F);
                if (!other.isFemale()) {
                    triggerAnim(ACTION_CONTROLLER, "dome_clash");
                    other.triggerAnim(ACTION_CONTROLLER, "dome_clash");
                    this.clashWith = other;
                    this.clashTick = 0;
                    this.still = 80;
                    other.still = 80;
                } else {
                    triggerAnim(ACTION_CONTROLLER, "dome_display");
                    this.still = 80;
                    other.still = 40;
                }
                return;
            }
        }
        if (this.berriesInReach()) {
            triggerAnim(ACTION_CONTROLLER, "pluck");
            this.still = 68;
            this.feed(4);
            return;
        }
        triggerAnim(ACTION_CONTROLLER, "sniff");
        this.still = 68;
    }

    /** The warned player still close and still without food when the warning ends: shoved away, no damage. */
    private void tickWarning() {
        this.warnLeft--;
        Player p = this.warned;
        if (p == null || !p.isAlive()) {
            this.warnLeft = 0;
            return;
        }
        this.getLookControl().setLookAt(p, 30.0F, 30.0F);
        if (this.warnLeft == 0) {
            this.warned = null;
            if (this.distanceToSqr(p) < 9.0D && !this.holdsFood(p) && this.getTarget() == null) {
                triggerAnim(ACTION_CONTROLLER, "flank_butt");
                p.knockback(1.1D, this.getX() - p.getX(), this.getZ() - p.getZ());
                p.hurtMarked = true;
                this.playSound(SoundEvents.GOAT_RAM_IMPACT, 0.8F, 1.1F);
                this.still = 20;
            }
        }
    }

    /** The clash: at the moment the domes meet, a hollow knock and both are pushed back a little. */
    private void tickClash() {
        if (this.clashTick < 0) {
            return;
        }
        this.clashTick++;
        Pachycephalosaurid other = this.clashWith;
        if (other == null || !other.isAlive() || this.clashTick > 80) {
            this.clashTick = -1;
            this.clashWith = null;
            return;
        }
        if (this.clashTick == CLASH_HIT) {
            this.level().playSound(null, this.getX(), this.getY(), this.getZ(), SoundEvents.GOAT_RAM_IMPACT, SoundSource.NEUTRAL, 1.2F, 0.8F);
            Vec3 away = this.position().subtract(other.position()).multiply(1.0D, 0.0D, 1.0D);
            if (away.lengthSqr() > 1.0E-4D) {
                away = away.normalize().scale(0.35D);
                this.setDeltaMovement(this.getDeltaMovement().add(away));
                other.setDeltaMovement(other.getDeltaMovement().subtract(away));
            }
        }
    }

    /** A berry bush or leaves right in front of it, from the ground to its head height. */
    private boolean berriesInReach() {
        Vec3 look = Vec3.directionFromRotation(0.0F, this.getYRot());
        for (int up = 0; up <= 2; up++) {
            BlockPos p = BlockPos.containing(this.getX() + look.x * 1.6D, this.getY() + up, this.getZ() + look.z * 1.6D);
            var state = this.level().getBlockState(p);
            if (state.is(Blocks.SWEET_BERRY_BUSH) || (up >= 1 && state.is(BlockTags.LEAVES))) {
                return true;
            }
        }
        return false;
    }

    private Pachycephalosaurid nearestAdult(double range) {
        Pachycephalosaurid best = null;
        double bestD = Double.MAX_VALUE;
        List<Pachycephalosaurid> list = this.level().getEntitiesOfClass(Pachycephalosaurid.class, this.getBoundingBox().inflate(range),
                e -> e != this && e.isAlive() && !e.isBaby());
        for (Pachycephalosaurid e : list) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }
}
