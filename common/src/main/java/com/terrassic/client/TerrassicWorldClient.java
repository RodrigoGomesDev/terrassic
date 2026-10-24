package com.terrassic.client;

/** Client entry of the v0.8 front ("Mundo Terrassic"): Rift Storm effects and the Terrassic HUD. */
public final class TerrassicWorldClient {
    private TerrassicWorldClient() {
    }

    public static void init() {
        RiftStormClient.init();
        TerrassicHud.init();
    }
}
