package com.terrassic.client;

import com.terrassic.config.Rules;

/** The rules of the world the client is in, as last sent by the server (RulesNetwork.SYNC), for the Rules screen. */
public final class ClientRules {
    private static Rules rules = new Rules();
    private static boolean canEdit;
    private static boolean received;

    private ClientRules() {
    }

    static void set(Rules value, boolean edit) {
        rules = value;
        canEdit = edit;
        received = true;
    }

    static void reset() {
        rules = new Rules();
        canEdit = false;
        received = false;
    }

    public static Rules get() {
        return rules;
    }

    public static boolean canEdit() {
        return canEdit;
    }

    public static boolean received() {
        return received;
    }
}
