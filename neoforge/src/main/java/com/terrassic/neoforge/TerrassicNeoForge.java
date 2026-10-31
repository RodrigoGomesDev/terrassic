package com.terrassic.neoforge;

import com.terrassic.Terrassic;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;

@Mod(Terrassic.MOD_ID)
public final class TerrassicNeoForge {
    public TerrassicNeoForge(IEventBus modBus, ModContainer container) {
        // Architectury 13 finds the mod event bus by itself on NeoForge (no EventBuses.registerModEventBus).
        Terrassic.init();
        // built-in era resource packs (neoforge/EraPacks): found before options.txt is applied
        modBus.addListener(EraPacks::onAddPackFinders);
        // the mods list's Config button opens the default world rules (docs/REGRAS.md)
        if (FMLEnvironment.dist.isClient()) {
            TerrassicNeoForgeClient.init(modBus, container);
        }
    }
}
