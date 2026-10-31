package com.terrassic.client;

import com.terrassic.network.Net;
import net.minecraft.client.Minecraft;
import net.minecraft.network.RegistryFriendlyByteBuf;

/** A packet buffer for what the client sends to the server (1.21: buffers know the registries). */
final class ClientNet {
    private ClientNet() {
    }

    static RegistryFriendlyByteBuf buf() {
        return Net.buf(Minecraft.getInstance().level.registryAccess());
    }
}
