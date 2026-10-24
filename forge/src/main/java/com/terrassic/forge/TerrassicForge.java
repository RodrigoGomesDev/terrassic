package com.terrassic.forge;

import com.terrassic.Terrassic;
import dev.architectury.platform.forge.EventBuses;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(Terrassic.MOD_ID)
public final class TerrassicForge {
    public TerrassicForge() {
        // Submit our event bus to let Architectury API register our content at the right time.
        EventBuses.registerModEventBus(Terrassic.MOD_ID, FMLJavaModLoadingContext.get().getModEventBus());
        Terrassic.init();
    }
}
