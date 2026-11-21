package com.terrassic.client.dev;

/** Frames drawn since the game started (1.21.1, counted by mixin/client/FrameCountMixin; render thread only). */
public final class FrameCount {
    public static long frames;

    private FrameCount() {
    }
}
