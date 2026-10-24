package com.terrassic.mixin.client;

import com.terrassic.client.ClientConfig;
import com.terrassic.client.TerrassicTitle;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.LevelLoadingScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** A real fact or a game tip under the chunk map while a world is created or loaded (v0.8, phase M2). */
@Mixin(LevelLoadingScreen.class)
public abstract class LevelLoadingScreenMixin extends Screen {
    @Unique
    private Component terrassic$tip;

    protected LevelLoadingScreenMixin(Component title) {
        super(title);
    }

    @Inject(method = "render", at = @At("TAIL"), require = 0)
    private void terrassic$tip(GuiGraphics graphics, int mouseX, int mouseY, float partialTick, CallbackInfo ci) {
        if (!ClientConfig.loadingTips()) {
            return;
        }
        if (this.terrassic$tip == null) {
            this.terrassic$tip = TerrassicTitle.randomTip();
        }
        TerrassicTitle.renderTip(graphics, this.terrassic$tip, this.width, this.height);
    }
}
