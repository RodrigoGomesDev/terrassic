package com.terrassic.client;

import com.terrassic.network.ModNetwork;
import com.terrassic.research.Knowledge;
import dev.architectury.event.events.client.ClientPlayerEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import net.minecraft.client.Minecraft;
import net.minecraft.nbt.CompoundTag;

/**
 * Client-only entry points called from common code through EnvExecutor (notebook item, research table) and the
 * receivers of the server packets.
 */
public final class ClientHooks {
    /** The intro waits until the world is loaded and no other screen is open. */
    private static boolean introPending;

    private ClientHooks() {
    }

    static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, ModNetwork.SYNC, (buf, context) -> {
            CompoundTag tag = buf.readNbt();
            context.queue(() -> ClientResearch.set(tag == null ? new Knowledge() : Knowledge.load(tag)));
        });
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, ModNetwork.INTRO, (buf, context) ->
                context.queue(() -> introPending = true));
        ClientTickEvent.CLIENT_POST.register(mc -> {
            if (introPending && mc.player != null && mc.level != null && mc.screen == null) {
                introPending = false;
                mc.setScreen(new IntroScreen());
            }
        });
        ClientPlayerEvent.CLIENT_PLAYER_QUIT.register(player -> {
            introPending = false;
            ClientResearch.reset();
        });
    }

    /** Opens the Field Notebook on a tab ("journal", "guide", "katarina", "report"), or the last tab used if null. */
    public static void openNotebook(String tab) {
        Minecraft.getInstance().setScreen(new NotebookScreen(tab));
    }
}
