package com.primalera.fabric;

import com.primalera.PrimalEra;
import net.fabricmc.api.ModInitializer;

public final class PrimalEraFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        // Common setup (registries, spawns). Client renderers are registered from
        // PrimalEra.init() through Architectury when running on the client.
        PrimalEra.init();
    }
}
