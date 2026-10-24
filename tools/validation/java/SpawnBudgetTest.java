package com.terrassic.world;

import java.util.HashSet;
import java.util.Random;
import java.util.Set;

/** Executable property tests; no Minecraft or test framework dependencies. */
public final class SpawnBudgetTest {
    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void main(String[] args) {
        Random random = new Random(20261024L);
        Set<Integer> slots = new HashSet<>();
        for (int i = 0; i < 1000; i++) {
            int hash = i < 2 ? (i == 0 ? Integer.MIN_VALUE : Integer.MAX_VALUE) : random.nextInt();
            int turns = 0;
            for (long tick = 800; tick < 840; tick++) {
                if (SpawnBudget.isTurn(tick, hash, 40)) {
                    turns++;
                    slots.add((int) (tick % 40));
                }
            }
            require(turns == 1, "every player must run once in a full period, including negative hashes");
            require(SpawnBudget.isTurn(800, hash, 40) == SpawnBudget.isTurn(840, hash, 40), "periodicity");
        }
        require(slots.size() == 40, "work must be spread across the entire period");
        for (int i = 0; i < 10000; i++) {
            int target = random.nextInt(500);
            int nearby = random.nextInt(600);
            int cap = random.nextInt(2000);
            int total = random.nextInt(2500);
            int remaining = SpawnBudget.allowance(target, nearby, cap, total);
            int group = Math.min(remaining, 1 + random.nextInt(20));
            require(remaining >= 0, "negative budgets must become zero");
            if (group > 0) {
                require(nearby + group <= target, "a whole group must respect the local target");
                require(total + group <= cap, "a whole group must respect the global cap");
            }
            require(SpawnBudget.allowance(target, nearby + group, cap, total + group) <= remaining,
                    "the next category cannot reuse the budget already spent");
        }
        require(SpawnBudget.allowance(18, 0, 400, 399) == 1, "last global slot");
        require(SpawnBudget.allowance(18, 17, 400, 0) == 1, "last local slot");
        require(SpawnBudget.allowance(18, 0, 400, 400) == 0, "full world");
        System.out.println("PASS: 1,000 player schedules and 10,000 group budget scenarios");
    }
}
