package com.terrassic.entity;

/**
 * 1.10.1, behaviour (docs/estudos/12_ECOSSISTEMA_ARK.md, sections 6 and 7): the switches of the new behaviour, one per
 * system. Each is read from the environment at start (TERRASSIC_OLD_...=1 brings back the 1.9.5 way) and checked while the
 * game runs, never only when a goal is built, so the BehaviorTest can measure old and new side by side in one run.
 */
public final class Behaviour {
    /** The apex roar scares the small ones away; the player is noticed at the temperament's range. */
    public static boolean oldRoar = env("TERRASSIC_OLD_ROAR");
    public static boolean oldAggro = env("TERRASSIC_OLD_AGGRO");
    /** A taken egg enrages the adults; the call for help; the babies keep near their mother. */
    public static boolean oldEgg = env("TERRASSIC_OLD_EGG");
    public static boolean oldHelp = env("TERRASSIC_OLD_HELP");
    public static boolean oldBaby = env("TERRASSIC_OLD_BABY");
    /** The herd moves with its leader; the idle quirks. */
    public static boolean oldHerd = env("TERRASSIC_OLD_HERD");
    public static boolean oldQuirks = env("TERRASSIC_OLD_QUIRKS");
    /** Each foot on its own ground (client); the region keeps its population (world/EcoSpawner). */
    public static boolean oldFeet = env("TERRASSIC_OLD_FEET");
    public static boolean oldPopulation = env("TERRASSIC_OLD_POPULATION");

    private Behaviour() {
    }

    private static boolean env(String name) {
        return "1".equals(System.getenv(name));
    }
}
