package com.terrassic.network;

import com.terrassic.Terrassic;
import com.terrassic.research.Knowledge;
import dev.architectury.networking.NetworkManager;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.event.events.common.PlayerEvent;
import io.netty.buffer.Unpooled;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.nbt.CompoundTag;

/**
 * Server to client packets. The receivers are registered on the client only (TerrassicClient).
 * <ul>
 *   <li>{@link #SYNC}: the whole Knowledge on join/rejoin, and for clients without delta support.</li>
 *   <li>{@link #DELTA}: only changed NBT fields, against the last snapshot sent on this connection.</li>
 *   <li>{@link #INTRO}: open the intro screen (first time in the world only).</li>
 *   <li>{@link #STORY}: whether the story mode is on in this world (config/Story), on join.</li>
 *   <li>{@link #ERA_TITLE}: show the era's title (TerrassicHud), the first time the player is in that era.</li>
 *   <li>{@link #NOTICE}: a notice about one of your animals on the right of the HUD (v0.14, client/HudNotices).</li>
 * </ul>
 */
public final class ModNetwork {
    public static final ResourceLocation SYNC = Terrassic.id("research_sync");
    public static final ResourceLocation DELTA = Terrassic.id("research_delta");
    public static final ResourceLocation INTRO = Terrassic.id("intro");
    public static final ResourceLocation STORY = Terrassic.id("story");
    public static final ResourceLocation ERA_TITLE = Terrassic.id("era_title");
    public static final ResourceLocation NOTICE = Terrassic.id("notice");
    /** The colour of a notice's first line. */
    public static final int NOTICE_AMBER = 0;
    public static final int NOTICE_FERN = 1;
    public static final int NOTICE_RIFT = 2;
    public static final int NOTICE_BLOOD = 3;
    private static final KnowledgeSyncState STATE = new KnowledgeSyncState();

    private ModNetwork() {
    }

    public static void init() {
        PlayerEvent.PLAYER_QUIT.register(player -> STATE.forget(player.getUUID()));
        LifecycleEvent.SERVER_STOPPED.register(server -> STATE.clear());
    }

    /** A new connection always receives a complete snapshot, even when the UUID was already online before. */
    public static void sendFullKnowledge(ServerPlayer player, Knowledge knowledge) {
        send(player, STATE.full(player.getUUID(), knowledge.save()));
    }

    public static void sendKnowledge(ServerPlayer player, Knowledge knowledge) {
        send(player, STATE.update(player.getUUID(), knowledge.save(), NetworkManager.canPlayerReceive(player, DELTA)));
    }

    private static void send(ServerPlayer player, KnowledgeSyncState.Update update) {
        if (update == null) {
            return;
        }
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeNbt(update.payload());
        NetworkManager.sendToPlayer(player, update.full() ? SYNC : DELTA, buf);
    }

    public static void sendIntro(ServerPlayer player) {
        NetworkManager.sendToPlayer(player, INTRO, new FriendlyByteBuf(Unpooled.buffer()));
    }

    public static void sendStory(ServerPlayer player, boolean story) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeBoolean(story);
        NetworkManager.sendToPlayer(player, STORY, buf);
    }

    public static void sendEraTitle(ServerPlayer player, String era) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeUtf(era);
        NetworkManager.sendToPlayer(player, ERA_TITLE, buf);
    }

    /** A notice on the right of the HUD: a title in the tone's colour, a line under it and the animal in amber. Always
     *  sent as a packet (the mod is needed on both sides; on Forge canPlayerReceive said false to clients that have the
     *  receiver); with "hud_notices": false the client itself puts it in the action bar (HudNotices.add). */
    public static void sendNotice(ServerPlayer player, int tone, Component title, Component line, ResourceLocation species) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeVarInt(tone);
        buf.writeComponent(title);
        buf.writeComponent(line);
        buf.writeResourceLocation(species);
        NetworkManager.sendToPlayer(player, NOTICE, buf);
    }
}
