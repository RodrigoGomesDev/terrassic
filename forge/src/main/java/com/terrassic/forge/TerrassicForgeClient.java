package com.terrassic.forge;

import com.terrassic.client.RulesScreen;
import com.terrassic.config.WorldConfig;
import net.minecraftforge.client.ConfigScreenHandler;
import net.minecraftforge.fml.ModLoadingContext;

/** Client-only Forge hooks: the "Config" button of the mods list opens the default world rules (docs/REGRAS.md), only
 *  while the rules can be changed in game (WorldConfig.rulesInGame, off for now since v0.15.1). */
final class TerrassicForgeClient {
    private TerrassicForgeClient() {
    }

    static void init() {
        if (WorldConfig.rulesInGame()) {
            ModLoadingContext.get().registerExtensionPoint(ConfigScreenHandler.ConfigScreenFactory.class,
                    () -> new ConfigScreenHandler.ConfigScreenFactory((minecraft, parent) -> new RulesScreen(parent, false)));
        }
        EraFilterForge.register();
        MountHudForge.register();
    }
}
