package com.terrassic.neoforge;

import com.terrassic.client.EraFilter;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterClientReloadListenersEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.common.NeoForge;

/** Client only: runs the era filter after the weather pass (the last stage of the world) and rebuilds it on reload. */
final class EraFilterNeoForge {
    private EraFilterNeoForge() {
    }

    static void register(IEventBus modBus) {
        NeoForge.EVENT_BUS.addListener((RenderLevelStageEvent event) -> {
            if (event.getStage() == RenderLevelStageEvent.Stage.AFTER_WEATHER) {
                // 1.21: the partial tick comes from a DeltaTracker
                EraFilter.render(event.getPartialTick().getGameTimeDeltaPartialTick(false));
            }
        });
        modBus.addListener((RegisterClientReloadListenersEvent event) ->
                event.registerReloadListener((ResourceManagerReloadListener) manager -> EraFilter.onResourcesReloaded()));
    }
}
