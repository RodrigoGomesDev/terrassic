package com.terrassic.forge;

import com.terrassic.client.RulesScreen;
import net.minecraftforge.client.ConfigScreenHandler;
import net.minecraftforge.fml.ModLoadingContext;

/** Client-only Forge hooks: the "Config" button of the mods list opens the default world rules (docs/REGRAS.md). */
final class TerrassicForgeClient {
    private TerrassicForgeClient() {
    }

    static void init() {
        ModLoadingContext.get().registerExtensionPoint(ConfigScreenHandler.ConfigScreenFactory.class,
                () -> new ConfigScreenHandler.ConfigScreenFactory((minecraft, parent) -> new RulesScreen(parent, false)));
        EraFilterForge.register();
        MountHudForge.register();
    }
}
