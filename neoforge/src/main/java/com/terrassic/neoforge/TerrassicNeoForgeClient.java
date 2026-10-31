package com.terrassic.neoforge;

import com.terrassic.client.RulesScreen;
import com.terrassic.config.WorldConfig;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

/** Client-only NeoForge hooks: the "Config" button of the mods list opens the default world rules (docs/REGRAS.md), only
 *  while the rules can be changed in game (WorldConfig.rulesInGame, off for now since v0.15.1). */
final class TerrassicNeoForgeClient {
    private TerrassicNeoForgeClient() {
    }

    static void init(IEventBus modBus, ModContainer container) {
        if (WorldConfig.rulesInGame()) {
            container.registerExtensionPoint(IConfigScreenFactory.class,
                    (IConfigScreenFactory) (mod, parent) -> new RulesScreen(parent, false));
        }
        EraFilterNeoForge.register(modBus);
        MountHudNeoForge.register();
    }
}
