package com.terrassic.client;

/** Client entry of the v0.8 front ("Mundo Terrassic"): Rift Storm effects and the Terrassic HUD; v0.9 client. */
public final class TerrassicWorldClient {
    private TerrassicWorldClient() {
    }

    public static void init() {
        RiftStormClient.init();
        TerrassicHud.init();
        LeapClient.init(); // v0.9: shooting stars, ritual sky, flash of the leap, Rift Tyrant and meteors
    }
}
