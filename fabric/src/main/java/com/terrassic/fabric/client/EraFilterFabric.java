package com.terrassic.fabric.client;

import com.terrassic.Terrassic;
import com.terrassic.client.EraFilter;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.WorldRenderEvents;
import net.fabricmc.fabric.api.resource.ResourceManagerHelper;
import net.fabricmc.fabric.api.resource.SimpleSynchronousResourceReloadListener;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.resources.ResourceManager;

/**
 * Client entrypoint ("client" in fabric.mod.json): runs the era filter at the end of the world render and rebuilds
 * it when packs reload.
 */
public final class EraFilterFabric implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        WorldRenderEvents.END.register(context -> EraFilter.render(context.tickDelta()));
        ResourceManagerHelper.get(PackType.CLIENT_RESOURCES).registerReloadListener(new SimpleSynchronousResourceReloadListener() {
            @Override
            public ResourceLocation getFabricId() {
                return new ResourceLocation(Terrassic.MOD_ID, "era_filter");
            }

            @Override
            public void onResourceManagerReload(ResourceManager manager) {
                EraFilter.onResourcesReloaded();
            }
        });
    }
}
