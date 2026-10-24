package com.terrassic.leap;

import com.terrassic.Terrassic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;

import java.util.ArrayList;
import java.util.List;

/**
 * The ring of the Leap Altar (HISTORIA.md §1: "um anel de pedra, osso e couro com o âmbar no centro"):
 * <pre>
 *         . . . S . . .
 *         . B . . . B .
 *         . . . . . . .        S = standing stone (tag terrassic:altar_stones: menhir, stacked stone)
 *         S . . A . . S        B = bone (tag terrassic:altar_bones: ossuary wall, rib arch, bone pile, skull trophies)
 *         . . . . . . .        A = the Leap Altar (stone, bone and hide around the amber)
 *         . B . . . B .
 *         . . . S . . .
 * </pre>
 * Each post counts anywhere in its column from one block below the altar to two above, so the ring can follow
 * uneven ground and a trophy can sit on top of a stone. Living things within {@link #RADIUS} blocks of the altar
 * are "inside the ring" (they go along on the leap).
 */
public final class AltarRing {
    public static final TagKey<Block> STONES = TagKey.create(Registries.BLOCK, Terrassic.id("altar_stones"));
    public static final TagKey<Block> BONES = TagKey.create(Registries.BLOCK, Terrassic.id("altar_bones"));
    public static final int[][] STONE_SPOTS = {{3, 0}, {-3, 0}, {0, 3}, {0, -3}};
    public static final int[][] BONE_SPOTS = {{2, 2}, {2, -2}, {-2, 2}, {-2, -2}};
    public static final double RADIUS = 3.5D;

    private AltarRing() {
    }

    /** The posts still missing (at the altar's height); empty = the ring is complete. */
    public static List<BlockPos> missing(Level level, BlockPos altar) {
        List<BlockPos> out = new ArrayList<>();
        for (int[] s : STONE_SPOTS) {
            BlockPos p = altar.offset(s[0], 0, s[1]);
            if (!column(level, p, STONES)) {
                out.add(p);
            }
        }
        for (int[] b : BONE_SPOTS) {
            BlockPos p = altar.offset(b[0], 0, b[1]);
            if (!column(level, p, BONES)) {
                out.add(p);
            }
        }
        return out;
    }

    public static boolean complete(Level level, BlockPos altar) {
        return missing(level, altar).isEmpty();
    }

    private static boolean column(Level level, BlockPos base, TagKey<Block> tag) {
        for (int dy = -1; dy <= 2; dy++) {
            if (level.getBlockState(base.above(dy)).is(tag)) {
                return true;
            }
        }
        return false;
    }

    public static boolean inside(BlockPos altar, double x, double y, double z) {
        double dx = x - (altar.getX() + 0.5D);
        double dz = z - (altar.getZ() + 0.5D);
        double dy = y - altar.getY();
        return dx * dx + dz * dz <= RADIUS * RADIUS && dy > -3.0D && dy < 6.0D;
    }
}
