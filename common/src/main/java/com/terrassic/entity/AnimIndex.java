package com.terrassic.entity;

import com.terrassic.Terrassic;
import software.bernie.geckolib.cache.GeckoLibCache;
import software.bernie.geckolib.loading.object.BakedAnimations;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Which animations a species' file has (06/11/2026): the live layer plays a guard, sidesteps, step-round turns or tired
 * loops only for the rigs that were given them. Reads GeckoLib's cache (filled on the client; on a server it is empty
 * and every answer is false, which is fine: the server never picks movement loops). Cached per species and name.
 */
public final class AnimIndex {
    private static final Map<String, Boolean> CACHE = new ConcurrentHashMap<>();

    private AnimIndex() {
    }

    public static boolean has(String species, String name) {
        return CACHE.computeIfAbsent(species + "/" + name, k -> {
            BakedAnimations anims = GeckoLibCache.getBakedAnimations().get(Terrassic.id("animations/entity/" + species + ".animation.json"));
            if (anims != null) {
                return anims.getAnimation("animation." + species + "." + name) != null;
            }
            // a dedicated server has no GeckoLib cache: the names straight from the file in the jar
            return fileNames(species).contains("animation." + species + "." + name);
        });
    }

    private static final Map<String, java.util.Set<String>> FILES = new ConcurrentHashMap<>();

    private static java.util.Set<String> fileNames(String species) {
        return FILES.computeIfAbsent(species, sp -> {
            String path = "/assets/terrassic/animations/entity/" + sp + ".animation.json";
            try (java.io.InputStream in = AnimIndex.class.getResourceAsStream(path)) {
                if (in == null) {
                    return java.util.Set.of();
                }
                com.google.gson.JsonObject root = com.google.gson.JsonParser.parseReader(
                        new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
                return java.util.Set.copyOf(root.getAsJsonObject("animations").keySet());
            } catch (Exception e) {
                return java.util.Set.of();
            }
        });
    }

    /** Resources reloaded: ask again. */
    public static void clear() {
        CACHE.clear();
    }
}
