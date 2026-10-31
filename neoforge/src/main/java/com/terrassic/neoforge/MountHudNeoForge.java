package com.terrassic.neoforge;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.client.Minecraft;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;

/** Client only: a ridden dinosaur's health is on the mount panel (client/TerrassicHud), so the vanilla mount hearts are
 *  skipped. mixin/client/GuiMixin counts no vehicle hearts for it, which keeps the player's own food bar. Horses and
 *  other vanilla mounts are untouched. */
final class MountHudNeoForge {
    private MountHudNeoForge() {
    }

    static void register() {
        NeoForge.EVENT_BUS.addListener((RenderGuiLayerEvent.Pre event) -> {
            Minecraft mc = Minecraft.getInstance();
            if (event.getName().equals(VanillaGuiLayers.VEHICLE_HEALTH) && mc.player != null
                    && mc.player.getVehicle() instanceof DinosaurEntity) {
                event.setCanceled(true);
            }
        });
    }
}
