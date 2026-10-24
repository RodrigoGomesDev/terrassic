package com.terrassic.client;

import com.terrassic.research.Knowledge;

/** The local player's {@link Knowledge}, as last sent by the server (ModNetwork.SYNC). Read by the notebook screen. */
public final class ClientResearch {
    private static Knowledge current = new Knowledge();

    private ClientResearch() {
    }

    public static Knowledge get() {
        return current;
    }

    static void set(Knowledge knowledge) {
        current = knowledge;
    }

    static void reset() {
        current = new Knowledge();
    }
}
