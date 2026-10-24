package com.terrassic.client;

import com.terrassic.config.Rules;
import com.terrassic.network.ModNetwork;
import com.terrassic.network.RulesNetwork;
import com.terrassic.research.Knowledge;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientPlayerEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;

/**
 * Client-only entry points called from common code through EnvExecutor (notebook item, research table) and the
 * receivers of the server packets.
 */
public final class ClientHooks {
    /** The intro waits until the world is loaded and no other screen is open. */
    private static boolean introPending;
    /** The Rules screen asked for by /terrassic regras, opened on the next tick. */
    private static boolean rulesPending;

    private ClientHooks() {
    }

    static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, ModNetwork.SYNC, (buf, context) -> {
            CompoundTag tag = buf.readNbt();
            context.queue(() -> ClientResearch.set(tag == null ? new Knowledge() : Knowledge.load(tag)));
        });
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, ModNetwork.DELTA, (buf, context) -> {
            CompoundTag patch = buf.readNbt();
            if (patch != null) {
                context.queue(() -> ClientResearch.applyDelta(patch));
            }
        });
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, ModNetwork.INTRO, (buf, context) ->
                context.queue(() -> introPending = true));
        // world rules (docs/REGRAS.md): the server's values, and the command that opens the screen
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, RulesNetwork.SYNC, (buf, context) -> {
            CompoundTag tag = buf.readNbt();
            boolean edit = buf.readBoolean();
            context.queue(() -> ClientRules.set(tag == null ? new Rules() : Rules.load(tag), edit));
        });
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, RulesNetwork.OPEN, (buf, context) ->
                context.queue(() -> rulesPending = true));
        // a "Terrassic Rules" button in the top left corner: the pause menu edits the world's rules, the title screen
        // the defaults for new worlds
        ClientGuiEvent.INIT_POST.register((screen, access) -> {
            boolean pause = screen instanceof PauseScreen && Minecraft.getInstance().level != null;
            if (pause || screen instanceof TitleScreen) {
                access.addRenderableWidget(new RulesScreen.GlassButton(6, 6, 120, 18,
                        Component.translatable("rules.terrassic.ui.button"),
                        b -> Minecraft.getInstance().setScreen(new RulesScreen(screen, pause)), false, false));
            }
        });
        ClientTickEvent.CLIENT_POST.register(mc -> {
            if (introPending && mc.player != null && mc.level != null && mc.screen == null) {
                introPending = false;
                mc.setScreen(new IntroScreen());
            }
            if (rulesPending && mc.player != null) {
                rulesPending = false;
                mc.setScreen(new RulesScreen(null, true));
            }
        });
        ClientPlayerEvent.CLIENT_PLAYER_QUIT.register(player -> {
            introPending = false;
            rulesPending = false;
            ClientResearch.reset();
            ClientRules.reset();
        });
    }

    /** Opens the Field Notebook on a tab ("journal", "guide", "katarina", "report"), or the last tab used if null. */
    public static void openNotebook(String tab) {
        Minecraft.getInstance().setScreen(new NotebookScreen(tab));
    }
}
