package com.terrassic.leap;

import com.terrassic.Terrassic;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;

/**
 * Server to client packets of v0.9 (received by client/LeapClient):
 * <ul>
 *   <li>{@link #RITUAL}: a ritual of the meteors is on (or ended) at an altar: the red sky and the shower of
 *       shooting stars around it. Sent every 2 s to players within {@link #RANGE} blocks while it lasts.</li>
 *   <li>{@link #FLASH}: the flash of the leap.</li>
 * </ul>
 */
public final class LeapNetwork {
    public static final ResourceLocation RITUAL = Terrassic.id("leap_ritual");
    public static final ResourceLocation FLASH = Terrassic.id("leap_flash");
    public static final double RANGE = 192.0D;

    private LeapNetwork() {
    }

    static void init() {
        // S2C only: the receivers are registered on the client (LeapClient)
    }

    static void ritual(ServerLevel level, BlockPos altar, boolean on) {
        for (ServerPlayer p : level.players()) {
            if (p.blockPosition().distSqr(altar) < RANGE * RANGE) {
                FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
                buf.writeBlockPos(altar);
                buf.writeBoolean(on);
                NetworkManager.sendToPlayer(p, RITUAL, buf);
            }
        }
    }

    static void flash(ServerPlayer player, boolean unstable) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeBoolean(unstable);
        NetworkManager.sendToPlayer(player, FLASH, buf);
    }
}
