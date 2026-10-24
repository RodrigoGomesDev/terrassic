package com.terrassic.network;

import com.terrassic.Terrassic;
import com.terrassic.research.Knowledge;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;

/**
 * Server to client packets. The receivers are registered on the client only (TerrassicClient).
 * <ul>
 *   <li>{@link #SYNC}: the player's whole {@link Knowledge} as NBT, sent on join and after every change.</li>
 *   <li>{@link #INTRO}: open the intro screen (first time in the world only).</li>
 * </ul>
 */
public final class ModNetwork {
    public static final ResourceLocation SYNC = Terrassic.id("research_sync");
    public static final ResourceLocation INTRO = Terrassic.id("intro");

    private ModNetwork() {
    }

    public static void sendKnowledge(ServerPlayer player, Knowledge knowledge) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeNbt(knowledge.save());
        NetworkManager.sendToPlayer(player, SYNC, buf);
    }

    public static void sendIntro(ServerPlayer player) {
        NetworkManager.sendToPlayer(player, INTRO, new FriendlyByteBuf(Unpooled.buffer()));
    }
}
