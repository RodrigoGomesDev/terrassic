package com.terrassic.neoforge;

import com.terrassic.client.RulesScreen;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

/** Client-only NeoForge hooks: the "Config" button of the mods list opens the default world rules (docs/REGRAS.md). */
final class TerrassicNeoForgeClient {
    private TerrassicNeoForgeClient() {
    }

    static void init(IEventBus modBus, ModContainer container) {
        container.registerExtensionPoint(IConfigScreenFactory.class,
                (IConfigScreenFactory) (mod, parent) -> new RulesScreen(parent, false));
        EraFilterNeoForge.register(modBus);
    }
}
