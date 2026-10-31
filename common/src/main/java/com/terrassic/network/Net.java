package com.terrassic.network;

import com.terrassic.leap.LeapNetwork;
import com.terrassic.world.RiftStorm;
import com.terrassic.world.continent.IslandMap;
import dev.architectury.networking.NetworkManager;
import dev.architectury.platform.Platform;
import dev.architectury.utils.Env;
import io.netty.buffer.Unpooled;
import net.minecraft.core.RegistryAccess;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;

/** 1.21: packets are read and written on a buffer that knows the registries, and a server must declare what it sends
 *  (the client declares the same ids by registering their receivers). */
public final class Net {
    private Net() {
    }

    public static RegistryFriendlyByteBuf buf(RegistryAccess access) {
        return new RegistryFriendlyByteBuf(Unpooled.buffer(), access);
    }

    /** Only on a dedicated server: on a client the receivers (client/) already declared them. */
    public static void declareServerToClient() {
        if (Platform.getEnvironment() != Env.SERVER) {
            return;
        }
        for (ResourceLocation id : new ResourceLocation[]{ModNetwork.SYNC, ModNetwork.DELTA, ModNetwork.INTRO, ModNetwork.STORY,
                ModNetwork.ERA_TITLE, ModNetwork.NOTICE, RulesNetwork.SYNC, RulesNetwork.OPEN, DinoNetwork.SCREEN, LensNetwork.INFO,
                IslandMap.SYNC, RiftStorm.SYNC, LeapNetwork.RITUAL, LeapNetwork.FLASH}) {
            NetworkManager.registerS2CPayloadType(id);
        }
    }
}
