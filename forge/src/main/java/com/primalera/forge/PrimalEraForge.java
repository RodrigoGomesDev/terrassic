package com.primalera.forge;

import com.primalera.PrimalEra;
import dev.architectury.platform.forge.EventBuses;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(PrimalEra.MOD_ID)
public final class PrimalEraForge {
    public PrimalEraForge() {
        // Submit our event bus to let Architectury API register our content at the right time.
        EventBuses.registerModEventBus(PrimalEra.MOD_ID, FMLJavaModLoadingContext.get().getModEventBus());
        PrimalEra.init();
    }
}
