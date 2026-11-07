package com.terrassic.entity.ai;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.pathfinder.Node;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.phys.Vec3;

/**
 * 1.9.5, locomotion (docs/estudos/12, Locomoção): the vanilla ground navigation walks a path node by node, so an animal
 * zig-zags along the grid and turns at every corner. Every 5 ticks this one looks up to 8 nodes ahead on the same
 * level and goes straight for the furthest it can walk to in a line (string pulling), the line tested along the
 * middle and both flanks of the body, so a wide animal does not cut a corner it would catch on.
 *
 * <p>NOT IN USE (07/11/2026): through a field of pillars three of four walkers caught on them and never arrived; to be
 * redone (DinosaurEntity, comment where createNavigation was).
 */
public class DinoPathNavigation extends GroundPathNavigation {
    /** Test only (BehaviorTest "paths"): TERRASSIC_OLD_PATH=1 walks the vanilla way to compare. */
    public static final boolean OLD = "1".equals(System.getenv("TERRASSIC_OLD_PATH"));

    public DinoPathNavigation(Mob mob, Level level) {
        super(mob, level);
    }

    @Override
    public void tick() {
        super.tick();
        Path p = this.path;
        if (OLD || p == null || p.isDone() || !this.mob.onGround() || this.mob.isInWater() || this.tick % 5 != 0) {
            return;
        }
        int next = p.getNextNodeIndex();
        int far = Math.min(p.getNodeCount() - 1, next + 8);
        Vec3 from = this.mob.position();
        int y = this.mob.getBlockY();
        for (int i = far; i > next; i--) {
            Node n = p.getNode(i);
            if (n.y != y) {
                continue;                   // steps and slopes: the nodes know the way
            }
            Vec3 to = new Vec3(n.x + 0.5D, n.y, n.z + 0.5D);
            if (this.clearFor(from, to)) {
                p.setNextNodeIndex(i);
                return;
            }
        }
    }

    /** A straight walk from {@code a} to {@code b}: clear along the middle and both flanks of the body. */
    private boolean clearFor(Vec3 a, Vec3 b) {
        Vec3 d = b.subtract(a);
        double len = Math.sqrt(d.x * d.x + d.z * d.z);
        if (len < 1.0E-3D) {
            return false;
        }
        double half = this.mob.getBbWidth() * 0.5D;
        Vec3 side = new Vec3(-d.z / len * half, 0.0D, d.x / len * half);
        for (Vec3 o : new Vec3[]{Vec3.ZERO, side, side.reverse()}) {
            if (!isClearForMovementBetween(this.mob, a.add(o).add(0.0D, 0.5D, 0.0D), b.add(o).add(0.0D, 0.5D, 0.0D), false)) {
                return false;
            }
        }
        return true;
    }
}
