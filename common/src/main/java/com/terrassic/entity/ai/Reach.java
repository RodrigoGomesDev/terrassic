package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.phys.Vec3;

/**
 * 1.10.1 (the real-world playtest on hilly ground, 09/11): herd, follow and migration spots were the leader's position
 * plus an offset at the leader's height, so on a slope they fell inside the bank or in the air; and
 * {@code Navigation.moveTo} returns true for a path that stops short, so the animal pushed in place for 10-20 s.
 * Here a spot is set on the ground of its own column, and an animal walks only where the path really gets.
 */
public final class Reach {
    private Reach() {
    }

    /** The spot on the ground of its column, or null when that ground is more than {@code maxDy} from the spot. */
    public static Vec3 ground(DinosaurEntity mob, Vec3 at, double maxDy) {
        BlockPos top = mob.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(at.x, 0.0D, at.z));
        if (Math.abs(top.getY() - at.y) > maxDy) {
            return null;
        }
        return new Vec3(at.x, top.getY(), at.z);
    }

    /** Walks to the spot only if a full path reaches it (within a block); false and no move otherwise. */
    public static boolean walk(DinosaurEntity mob, Vec3 at, double speed) {
        if (at == null) {
            return false;
        }
        Path p = mob.getNavigation().createPath(BlockPos.containing(at), 1);
        if (p == null || !p.canReach()) {
            return false;
        }
        return mob.getNavigation().moveTo(p, speed);
    }

    /** The spot set on the ground if it can be reached, else the fallback (a leader or a neighbour), else nothing. */
    public static boolean walkOr(DinosaurEntity mob, Vec3 at, Vec3 fallback, double speed) {
        Vec3 g = at == null ? null : ground(mob, at, 4.0D);
        return walk(mob, g, speed) || walk(mob, fallback, speed);
    }
}
