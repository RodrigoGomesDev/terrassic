package com.terrassic.world;

/** Pure scheduling and budget arithmetic, independent of a running Minecraft server. */
final class SpawnBudget {
    static final int SKY_PERIOD = 400;
    static final int SKY_TARGET = 4;
    static final int SKY_RADIUS = 192;
    static final int SKY_MIN_DISTANCE = 64;
    static final int SKY_MAX_DISTANCE = 112;
    private SpawnBudget() {
    }

    static boolean isTurn(long tick, int playerHash, int period) {
        return Math.floorMod(tick, period) == Math.floorMod(playerHash, period);
    }

    static int allowance(int target, int nearby, int cap, int total) {
        return Math.max(0, Math.min(target - nearby, cap - total));
    }
}
