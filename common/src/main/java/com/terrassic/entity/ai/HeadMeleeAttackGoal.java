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
 */
public class HeadMeleeAttackGoal extends MeleeAttackGoal {
    /** How far past the head's box the jaws still reach, in blocks at size 1. */
    private static final double BITE = 0.8D;

    public HeadMeleeAttackGoal(PathfinderMob mob, double speed, boolean followEvenIfNotSeen) {
        super(mob, speed, followEvenIfNotSeen);
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
