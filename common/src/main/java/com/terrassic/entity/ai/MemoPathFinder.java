package com.terrassic.entity.ai;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.PathNavigationRegion;
import net.minecraft.world.level.pathfinder.Node;
import net.minecraft.world.level.pathfinder.NodeEvaluator;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.level.pathfinder.PathFinder;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * 1.11 (docs/DESEMPENHO_1_11.md): vanilla's A* with a small memory per animal (the last four searches). Asked again within a second for the
 * same targets from the same block (the same search, so the same answer while the ground stays as it is), it hands
 * back a copy of the last answer instead of searching again. The goals ask that a lot: a path that stops short ends at
 * once, "the navigation is done", and several goals re-plan every tick while it is done (a stuck animal searched the
 * whole node budget twenty times a second; a big animal's search reads every block its body covers at each node).
 * With every species in one place this was a third of the server tick. The copy is a new Path over a copy of the node
 * list, so trimming or following one never touches the other.
 */
public class MemoPathFinder extends PathFinder {
    /** How long an answer is reused (ticks), and how many answers are kept (a goal may try a few spots in a row). */
    static final int TICKS = 20;
    static final int SIZE = 4;
    private final Entry[] entries = new Entry[SIZE];
    private int next;

    /** One remembered search: where from, to what, and its answer (null nodes: no path). */
    private static final class Entry {
        long at;
        BlockPos from;
        boolean fromGround;
        boolean fromWater;
        Set<BlockPos> to;
        float range;
        int accuracy;
        float depth;
        List<Node> nodes;
        BlockPos target;
        boolean reached;
    }

    public MemoPathFinder(NodeEvaluator evaluator, int maxVisitedNodes) {
        super(evaluator, maxVisitedNodes);
    }

    @Override
    public Path findPath(PathNavigationRegion region, Mob mob, Set<BlockPos> targets, float maxRange, int accuracy, float depth) {
        long now = mob.level().getGameTime();
        BlockPos start = mob.blockPosition();
        boolean ground = mob.onGround();
        boolean water = mob.isInWater();
        for (Entry e : this.entries) {
            if (e != null && now >= e.at && now - e.at <= TICKS && start.equals(e.from) && ground == e.fromGround
                    && water == e.fromWater && maxRange == e.range && accuracy == e.accuracy && depth == e.depth
                    && targets.equals(e.to)) {
                return e.nodes == null ? null : new Path(new ArrayList<>(e.nodes), e.target, e.reached);
            }
        }
        Path path = super.findPath(region, mob, targets, maxRange, accuracy, depth);
        Entry e = new Entry();
        e.at = now;
        e.from = start.immutable();
        e.fromGround = ground;
        e.fromWater = water;
        e.to = Set.copyOf(targets);
        e.range = maxRange;
        e.accuracy = accuracy;
        e.depth = depth;
        if (path != null) {
            List<Node> copy = new ArrayList<>(path.getNodeCount());
            for (int i = 0; i < path.getNodeCount(); i++) {
                copy.add(path.getNode(i));
            }
            e.nodes = copy;
            e.target = path.getTarget();
            e.reached = path.canReach();
        }
        this.entries[this.next] = e;
        this.next = (this.next + 1) % SIZE;
        return path;
    }
}
