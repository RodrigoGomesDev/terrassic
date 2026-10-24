package com.terrassic.forge;

import com.terrassic.Terrassic;
import dev.architectury.platform.forge.EventBuses;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;

@Mod(Terrassic.MOD_ID)
public final class TerrassicForge {
    public TerrassicForge() {
        // Submit our event bus to let Architectury API register our content at the right time.
        EventBuses.registerModEventBus(Terrassic.MOD_ID, FMLJavaModLoadingContext.get().getModEventBus());
        Terrassic.init();
        // built-in era resource packs (forge/EraPacks): found before options.txt is applied
        FMLJavaModLoadingContext.get().getModEventBus().addListener(EraPacks::onAddPackFinders);
        // the mods list's Config button opens the default world rules (docs/REGRAS.md)
        if (FMLEnvironment.dist.isClient()) {
            TerrassicForgeClient.init();
        }
    }
}
