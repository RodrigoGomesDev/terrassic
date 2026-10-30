package com.terrassic.client;

import com.terrassic.config.Story;
import com.terrassic.research.Knowledge;
import com.terrassic.network.NbtDelta;
import net.minecraft.nbt.CompoundTag;

/**
 * The local player's {@link Knowledge}, as last sent by the server (ModNetwork.SYNC), read by the notebook screen, and
 * whether the story mode is on in the world (ModNetwork.STORY; outside a world, this game's own config/Story).
 */
public final class ClientResearch {
    private static Knowledge current = new Knowledge();
    private static Boolean story;

    private ClientResearch() {
    }

    public static Knowledge get() {
        return current;
    }

    static void set(Knowledge knowledge) {
        current = knowledge;
    }

    static void applyDelta(CompoundTag patch) {
        current = Knowledge.load(NbtDelta.apply(current.save(), patch));
    }

    static void reset() {
        current = new Knowledge();
        story = null;
    }

    public static boolean story() {
        return story != null ? story : Story.enabled();
    }

    static void setStory(boolean value) {
        story = value;
    }
}
