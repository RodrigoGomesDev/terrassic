package com.terrassic.mixin.client;

import com.terrassic.client.ClientConfig;
import com.terrassic.client.TerrassicTitle;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.ReceivingLevelScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** A loading tip on "Loading terrain..." too (joining a server, changing dimension) (v0.8, phase M2). */
@Mixin(ReceivingLevelScreen.class)
public abstract class ReceivingLevelScreenMixin extends Screen {
    @Unique
    private Component terrassic$tip;

    protected ReceivingLevelScreenMixin(Component title) {
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
