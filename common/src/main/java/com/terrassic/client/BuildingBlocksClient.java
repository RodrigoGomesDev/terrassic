package com.terrassic.client;

import com.terrassic.registry.BuildingBlocks;
import com.terrassic.registry.ModBlocks;
import dev.architectury.event.events.client.ClientLifecycleEvent;
import dev.architectury.registry.client.rendering.RenderTypeRegistry;
import net.minecraft.client.renderer.RenderType;

/** Client setup of the building blocks: leaves, saplings, doors and trapdoors have see-through pixels. */
public final class BuildingBlocksClient {
    private BuildingBlocksClient() {
    }

    public static void init() {
        ClientLifecycleEvent.CLIENT_SETUP.register(minecraft -> {
            for (String id : BuildingBlocks.CUTOUT) {
                RenderTypeRegistry.register(RenderType.cutoutMipped(), ModBlocks.BUILDING.get(id).get());
            }
        });
    }
}
