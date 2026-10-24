package com.terrassic;

import com.terrassic.client.TerrassicClient;
import com.terrassic.registry.ModBlockEntities;
import com.terrassic.registry.ModBlocks;
import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import com.terrassic.registry.ModSounds;
import com.terrassic.registry.ModTabs;
import com.terrassic.research.Research;
import com.terrassic.world.ModSpawns;
import com.terrassic.world.ModWorldgen;
import dev.architectury.utils.Env;
import dev.architectury.utils.EnvExecutor;
import net.minecraft.resources.ResourceLocation;

/**
 * Terrassic - common entry point shared by Fabric and Forge.
 */
public final class Terrassic {
    public static final String MOD_ID = "terrassic";

    private Terrassic() {
    }

    public static void init() {
        // order matters on Fabric (registered immediately): tabs, entities, blocks, then items
        ModSounds.SOUNDS.register();
        ModTabs.TABS.register();
        ModEntities.ENTITY_TYPES.register();
        ModBlocks.BLOCKS.register();
        ModBlockEntities.BLOCK_ENTITY_TYPES.register();
        ModItems.ITEMS.register();
        ModEntities.registerAttributes();
        ModSpawns.init();
        ModWorldgen.init();
        Research.init();
        EnvExecutor.runInEnv(Env.CLIENT, () -> TerrassicClient::init);
    }

    public static ResourceLocation id(String path) {
        return new ResourceLocation(MOD_ID, path);
    }
}
