package com.terrassic.forge;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.client.Minecraft;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.common.MinecraftForge;

/** Client only: a ridden dinosaur's health is on the mount panel (client/TerrassicHud), so Forge's mount hearts are
 *  skipped and the player's own food bar is drawn in their place (Forge hides it under any living mount). Horses and
 *  other vanilla mounts are untouched. On Fabric the same is done by mixin/client/GuiMixin. */
final class MountHudForge {
    private MountHudForge() {
    }

    static void register() {
        MinecraftForge.EVENT_BUS.addListener((RenderGuiOverlayEvent.Pre event) -> {
            Minecraft mc = Minecraft.getInstance();
            if (event.getOverlay() != VanillaGuiOverlay.MOUNT_HEALTH.type() || mc.player == null
                    || !(mc.player.getVehicle() instanceof DinosaurEntity) || !(mc.gui instanceof ForgeGui gui)) {
                return;
            }
            event.setCanceled(true);
            if (!mc.options.hideGui && gui.shouldDrawSurvivalElements()) {
                gui.setupOverlayRenderState(true, false);
                gui.renderFood(event.getWindow().getGuiScaledWidth(), event.getWindow().getGuiScaledHeight(), event.getGuiGraphics());
            }
        });
    }
}
