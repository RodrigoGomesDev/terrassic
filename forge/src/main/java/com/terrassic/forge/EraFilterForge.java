package com.terrassic.forge;

import com.terrassic.client.EraFilter;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraftforge.client.event.RegisterClientReloadListenersEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

/** Client only: runs the era filter after the weather pass (the last stage of the world) and rebuilds it on reload. */
final class EraFilterForge {
    private EraFilterForge() {
    }

    static void register() {
        MinecraftForge.EVENT_BUS.addListener((RenderLevelStageEvent event) -> {
            if (event.getStage() == RenderLevelStageEvent.Stage.AFTER_WEATHER) {
                EraFilter.render(event.getPartialTick());
            }
        });
        FMLJavaModLoadingContext.get().getModEventBus().addListener((RegisterClientReloadListenersEvent event) ->
                event.registerReloadListener((ResourceManagerReloadListener) manager -> EraFilter.onResourcesReloaded()));
    }
}
