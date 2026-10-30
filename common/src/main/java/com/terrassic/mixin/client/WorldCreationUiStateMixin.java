package com.terrassic.mixin.client;

import com.terrassic.config.WorldConfig;
import com.terrassic.world.continent.ModContinent;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.presets.WorldPreset;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * With {@code "mundo_terrassic": true} in config/terrassic-world.json, "Criar novo mundo" starts on the Terrassic
 * world type instead of "Padrão" (docs/MUNDO.md, section 10.3): whenever the screen opens on the vanilla default type
 * it switches to Terrassic (re-creating a world of another type keeps that type). Off by default since v0.15: the
 * game opens on Minecraft's own "Padrão" and the Terrassic types wait in the list.
 */
@Mixin(WorldCreationUiState.class)
public abstract class WorldCreationUiStateMixin {
    @Inject(method = "<init>", at = @At("RETURN"))
    private void terrassic$defaultToTerrassic(CallbackInfo ci) {
        WorldCreationUiState self = (WorldCreationUiState) (Object) this;
        Holder<WorldPreset> current = self.getWorldType().preset();
        if (current == null || !current.is(WorldPresets.NORMAL) || !WorldConfig.defaultWorldType()) {
            return;
        }
        for (WorldCreationUiState.WorldTypeEntry entry : self.getNormalPresetList()) {
            Holder<WorldPreset> preset = entry.preset();
            if (preset != null && preset.is(ModContinent.DEFAULT_PRESET)) {
                self.setWorldType(entry);
                return;
            }
        }
        // the type is listed through the world_preset/normal tag; if the list is not filled yet, look it up directly
        self.getSettings().worldgenLoadContext().registryOrThrow(Registries.WORLD_PRESET)
                .getHolder(ModContinent.DEFAULT_PRESET)
                .ifPresent(preset -> self.setWorldType(new WorldCreationUiState.WorldTypeEntry(preset)));
    }
}
