package com.primalera;

import com.primalera.client.PrimalEraClient;
import com.primalera.registry.ModBlocks;
import com.primalera.registry.ModEntities;
import com.primalera.registry.ModItems;
import com.primalera.registry.ModTabs;
import com.primalera.world.ModSpawns;
import dev.architectury.utils.Env;
import dev.architectury.utils.EnvExecutor;
import net.minecraft.resources.ResourceLocation;

/**
 * PrimalEra - common entry point shared by Fabric and Forge.
 */
public final class PrimalEra {
    public static final String MOD_ID = "primalera";

    private PrimalEra() {
    }

    public static void init() {
        // order matters on Fabric (registered immediately): tabs, entities, blocks, then items
        ModTabs.TABS.register();
        ModEntities.ENTITY_TYPES.register();
        ModBlocks.BLOCKS.register();
        ModItems.ITEMS.register();
        ModEntities.registerAttributes();
        ModSpawns.init();
        EnvExecutor.runInEnv(Env.CLIENT, () -> PrimalEraClient::init);
    }

    public static ResourceLocation id(String path) {
        return new ResourceLocation(MOD_ID, path);
    }
}
