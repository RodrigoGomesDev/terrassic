package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.parts.DinoPart;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.phys.AABB;

/**
 * The vanilla melee, but the bite is measured from the head (1.7, hit parts): a creature with a head part bites what
 * is in front of its snout and no longer what stands beside or behind its body, which the vanilla reach (twice the
 * box width, all round) allowed. Creatures without parts keep the vanilla reach.
 *
 * <p>06/11/2026, the duel (docs/DUELOS.md): a species with duel moves facing a big rival that fights back does not walk
 * straight in. It squares up, circles sideways at the ring while its patience runs out (feinting now and then), and
 * only then goes in for the vanilla blow; after each blow it circles again. When the rival comes in, it fights back at
 * once. The blocks, the reeling and the giving in are the entity's (DinosaurEntity duel hooks).
 */
public class HeadMeleeAttackGoal extends MeleeAttackGoal {
    /** How far past the head's box the jaws still reach, in blocks at size 1. */
    private static final double BITE = 0.8D;

    public HeadMeleeAttackGoal(PathfinderMob mob, double speed, boolean followEvenIfNotSeen) {
        super(mob, speed, followEvenIfNotSeen);
    }

    /** 0 none, 1 squaring up, 2 circling, 3 going in; ticks left of the phase; the side it circles to. */
    private int duel;
    private int duelLeft;
    private float duelSide = 1.0F;
    private int lastCooldown;
    /** The exchange (06/11, second pass): the step back after a blow, the quick probe in and out, the follow-up blow. */
    private int backLeft;
    private int probeLeft;
    private int followLeft;

    @Override
    public void stop() {
        super.stop();
        this.duel = 0;
        if (this.mob instanceof DinosaurEntity d) {
            d.setDueling(false);
        }
    }

    @Override
    public void tick() {
        LivingEntity target = this.mob.getTarget();
        if (target != null && this.mob instanceof DinosaurEntity d && d.duels(target) && this.duelTick(d, target)) {
            return;
        }
        super.tick();
        int cd = this.getTicksUntilNextAttack();
        if (cd > this.lastCooldown && this.duel > 0 && target != null && this.mob instanceof DinosaurEntity d) {
            // a blow went out: the body goes in with it, the rival reels; now and then a second one follows
            d.lungeAt(target, 0.18D);
            if (target instanceof DinosaurEntity rival && d.distanceTo(target) < this.reach(d, target) + 1.0D) {
                rival.tookDuelBlow(d, 1.0D);
            }
            if (this.followLeft == 0 && d.getRandom().nextFloat() < 0.4F) {
                this.followLeft = 8 + d.getRandom().nextInt(4);
            } else {
                this.duel = 2;
                this.duelLeft = 12 + d.getRandom().nextInt(24);
                this.backLeft = 5 + d.getRandom().nextInt(5);
            }
        }
        this.lastCooldown = cd;
    }

    private boolean faces(LivingEntity who, LivingEntity at) {
        double dx = at.getX() - who.getX();
        double dz = at.getZ() - who.getZ();
        float yawTo = (float) (net.minecraft.util.Mth.atan2(dz, dx) * net.minecraft.util.Mth.RAD_TO_DEG) - 90.0F;
        return Math.abs(net.minecraft.util.Mth.wrapDegrees(yawTo - who.yBodyRot)) < 30.0F;
    }

    private double reach(DinosaurEntity d, LivingEntity target) {
        return (d.getBbWidth() + target.getBbWidth()) * 0.6D + 1.2D;
    }

    /** A blow straight away (the follow-up, the answer), outside the vanilla cooldown. */
    private void strikeNow(DinosaurEntity d, LivingEntity target) {
        d.getLookControl().setLookAt(target, 60.0F, 60.0F);
        d.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
        d.lungeAt(target, 0.16D);
        if (d.doHurtTarget(target) && target instanceof DinosaurEntity rival) {
            rival.tookDuelBlow(d, 1.0D);
        }
    }

    private boolean duelTick(DinosaurEntity d, LivingEntity target) {
        if (d.clinchLeft > 0 && d.clinchTick()) {
            return true;
        }
        if (d.dodgeTick(target)) {
            return true;
        }
        if (d.stagger > 0) {
            d.stagger--;
            d.getNavigation().stop();
            d.getMoveControl().strafe(-0.4F, 0.0F);
            return true;
        }
        double s = Math.max(0.5F, d.getScale());
        double ring = (1.8D + d.getBbWidth() * 1.0D + target.getBbWidth() * 0.5D) * s;
        double dist = d.distanceTo(target);
        boolean inReach = dist < this.reach(d, target);
        // the follow-up blow, and the answer to a blow taken / blocked / sidestepped
        if (this.followLeft > 0 && --this.followLeft == 0 && inReach) {
            this.strikeNow(d, target);
            this.duel = 2;
            this.duelLeft = 12 + d.getRandom().nextInt(24);
            this.backLeft = 6;
            return true;
        }
        if (d.counterLeft > 0 && --d.counterLeft == 0 && inReach) {
            this.strikeNow(d, target);
            return true;
        }
        if (this.backLeft > 0) {
            this.backLeft--;
            d.getNavigation().stop();
            d.getLookControl().setLookAt(target, 30.0F, 30.0F);
            d.getMoveControl().strafe(-0.55F, 0.2F * this.duelSide);
            return true;
        }
        if (this.duel == 0) {
            if (dist > ring * 1.5D) {
                return false;
            }
            this.duel = 1;
            this.duelLeft = 12;
            this.duelSide = d.getRandom().nextBoolean() ? 1.0F : -1.0F;
            d.setDueling(true);
        }
        d.getLookControl().setLookAt(target, 30.0F, 30.0F);
        if (this.duel == 1) {
            d.getNavigation().stop();
            if (--this.duelLeft <= 0) {
                this.duel = 2;
                this.duelLeft = 12 + d.getRandom().nextInt(26);
            }
            return true;
        }
        if (d.isLocked()) {
            return true;    // the lock moves them (DinosaurEntity.lockTick)
        }
        // horns against horns: face to face and close, they lock (Triceratops, Farke et al. 2009)
        if (d.locksHorns(target) && dist < (d.getBbWidth() + target.getBbWidth()) * 0.7D + 1.0D
                && this.faces(d, target) && this.faces((DinosaurEntity) target, d) && d.getRandom().nextInt(10) == 0) {
            d.lockHorns((DinosaurEntity) target);
            return true;
        }
        if (this.duel == 2) {
            // the rival comes in: no more circling
            if (dist < (d.getBbWidth() + target.getBbWidth()) * 0.75D + 1.0D) {
                this.duel = 3;
                return false;
            }
            d.getNavigation().stop();
            // its own kind, face to face and close: they grapple (heads, chests, claws) and wheel round pushing
            if (target instanceof DinosaurEntity rd && rd.getType() == d.getType() && !d.locksHorns(target) && rd.clinchLeft == 0
                    && dist < this.reach(d, target) + 1.2D && d.getRandom().nextInt(4) == 0) {
                d.startClinch(rd, 36 + d.getRandom().nextInt(36));
                return true;
            }
            // never still: the sidestep quickens and slows, and now and then a quick step in and back out
            float in = dist > ring + 1.0D ? 0.45F : dist < ring - 1.0D ? -0.4F : 0.0F;
            if (this.probeLeft > 0) {
                this.probeLeft--;
                in = this.probeLeft > 4 ? 0.85F : -0.7F;
            } else if (d.getRandom().nextInt(26) == 0) {
                this.probeLeft = 9;
            }
            float pace = 0.42F + 0.22F * net.minecraft.util.Mth.sin(d.tickCount * 0.23F + d.getId());
            d.getMoveControl().strafe(in, pace * this.duelSide);
            if (d.getRandom().nextInt(45) == 0 || d.horizontalCollision) {
                this.duelSide = -this.duelSide;
            }
            // the rival reels: press it now
            if (target instanceof DinosaurEntity rd2 && rd2.stagger > 0) {
                this.duel = 3;
                return false;
            }
            if (--this.duelLeft > 0) {
                return true;
            }
            if (d.getRandom().nextFloat() < 0.3F) {
                d.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "feint");
                d.lungeAt(target, 0.12D);
                this.duelLeft = 10 + d.getRandom().nextInt(18);
            } else {
                this.duel = 3;
            }
            return true;
        }
        return false;
    }

    @Override
    protected boolean canPerformAttack(LivingEntity target) {
        AABB head = this.head();
        if (head == null) {
            return super.canPerformAttack(target);
        }
        // in reach of the head, or pressed against the body (a small target under the chin)
        boolean reach = head.inflate(BITE * Math.max(0.5F, ((DinosaurEntity) this.mob).getScale())).intersects(target.getBoundingBox())
                || this.mob.getBoundingBox().inflate(0.3D).intersects(target.getBoundingBox());
        return reach && this.isTimeToAttack() && this.mob.getSensing().hasLineOfSight(target);
    }

    /** The union of the head parts, or null when there are none (or they are not active). */
    private AABB head() {
        if (!(this.mob instanceof DinosaurEntity dino) || !dino.partsActive()) {
            return null;
        }
        AABB box = null;
        for (DinoPart part : dino.parts()) {
            if (part.kind() == DinoPart.Kind.HEAD) {
                box = box == null ? part.getBoundingBox() : box.minmax(part.getBoundingBox());
            }
        }
        return box;
    }
}
