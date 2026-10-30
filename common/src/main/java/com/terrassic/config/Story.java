package com.terrassic.config;

import com.terrassic.Terrassic;
import net.minecraft.resources.ResourceLocation;

import java.util.List;

/**
 * The story mode (docs/HISTORIA.md): the intro, Katarina's pages, the Field Journal objectives and the "Echoes of the
 * End" advancements, the arrival crater, Rift Storms, the Leap Altar, its ritual and the Rift Tyrant. Switched off
 * since v0.10 ("historia": false in config/terrassic-world.json) and kept for a future version: nothing of it was
 * removed, every piece asks {@link #enabled()} and works as before when the key is true.
 * <p>
 * Server logic reads the config here; the client gets the server's value on join (ClientResearch.story()).
 */
public final class Story {
    /** Recipes of story items, left out of the recipe book and the crafting grid while the story is off. */
    public static final List<ResourceLocation> RECIPES = List.of(Terrassic.id("leap_altar"));

    private Story() {
    }

    public static boolean enabled() {
        return WorldConfig.story();
    }
}
