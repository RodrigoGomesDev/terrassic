package com.terrassic.fabric;

import com.terrassic.Terrassic;
import net.fabricmc.api.ModInitializer;

public final class TerrassicFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        // Common setup (registries, spawns). Client renderers are registered from
        // Terrassic.init() through Architectury when running on the client.
        Terrassic.init();
    }
}
