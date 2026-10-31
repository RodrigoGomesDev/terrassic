package com.terrassic.mixin.client;

import com.terrassic.client.ClientConfig;
import com.terrassic.client.TerrassicTitle;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.LogoRenderer;
import net.minecraft.client.gui.components.SplashRenderer;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.renderer.PanoramaRenderer;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.client.resources.SplashManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;

/**
 * The Terrassic title screen (v0.8, phase M2): Cretaceous panorama, stone logo with the chapter line, and our own
 * splashes. Purely cosmetic, so every injection is optional (require = 0): if another mod or a loader patch moved a
 * target, the vanilla screen simply stays. Off with "title_screen": false in config/terrassic-client.json.
 */
@Mixin(TitleScreen.class)
public abstract class TitleScreenMixin {
    @Unique
    private static PanoramaRenderer terrassic$panorama;

    @Shadow
    private float panoramaFade;

    /** 1.21 keeps one panorama for every screen, so the title draws ours in its place. */
    @Inject(method = "renderPanorama", at = @At("HEAD"), cancellable = true)
    private void terrassic$panorama(GuiGraphics graphics, float partialTick, CallbackInfo ci) {
        if (ClientConfig.titleScreen()) {
            if (terrassic$panorama == null) {
                terrassic$panorama = new PanoramaRenderer(TerrassicTitle.CUBE_MAP);
            }
            Screen screen = (Screen) (Object) this;
            terrassic$panorama.render(graphics, screen.width, screen.height, this.panoramaFade, partialTick);
            ci.cancel();
        }
    }

    @Inject(method = "preloadResources", at = @At("RETURN"), cancellable = true, require = 0)
    private static void terrassic$preload(TextureManager textures, Executor executor, CallbackInfoReturnable<CompletableFuture<Void>> cir) {
        if (ClientConfig.titleScreen()) {
            cir.setReturnValue(CompletableFuture.allOf(cir.getReturnValue(), TerrassicTitle.CUBE_MAP.preload(textures, executor)));
        }
    }

    @Redirect(method = "render", require = 0, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/gui/components/LogoRenderer;renderLogo(Lnet/minecraft/client/gui/GuiGraphics;IF)V"))
    private void terrassic$logo(LogoRenderer renderer, GuiGraphics graphics, int width, float alpha) {
        if (ClientConfig.titleScreen()) {
            TerrassicTitle.renderLogo(graphics, width, alpha);
        } else {
            renderer.renderLogo(graphics, width, alpha);
        }
    }

    @Redirect(method = "init", require = 0, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/resources/SplashManager;getSplash()Lnet/minecraft/client/gui/components/SplashRenderer;"))
    private SplashRenderer terrassic$splash(SplashManager manager) {
        if (ClientConfig.titleScreen()) {
            String line = TerrassicTitle.randomSplash();
            if (line != null) {
                return new SplashRenderer(line);
            }
        }
        return manager.getSplash();
    }
}
