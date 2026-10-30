package com.terrassic.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.terrassic.Terrassic;
import com.terrassic.research.GuideSpecies;
import dev.architectury.platform.Platform;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * config/terrassic.json: how often each species spawns naturally. Read once when the game starts (biome spawn
 * lists are built then), so changes need a restart. Missing entries are added with defaults on the next start.
 *
 * <pre>
 * {
 *   "spawn_multiplier": 1.0,                       // all species: 0 turns natural spawning off, 2 doubles it
 *   "species": {
 *     "tyrannosaurus": { "enabled": true, "weight_multiplier": 1.0 },
 *     ...
 *   }
 * }
 * </pre>
 */
public final class SpawnConfig {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static JsonObject root;

    private SpawnConfig() {
    }

    /**
     * Spawn weight to use for a species whose default weight is {@code weight}; 0 = do not spawn. Species of an era
     * that is switched off (config/Eras) never spawn.
     */
    public static int weight(String species, int weight) {
        if (!Eras.active(species)) {
            return 0;
        }
        JsonObject cfg = load();
        double global = cfg.has("spawn_multiplier") ? cfg.get("spawn_multiplier").getAsDouble() : 1.0D;
        JsonObject all = cfg.getAsJsonObject("species");
        JsonObject s = all != null && all.has(species) ? all.getAsJsonObject(species) : null;
        if (s != null && s.has("enabled") && !s.get("enabled").getAsBoolean()) {
            return 0;
        }
        double own = s != null && s.has("weight_multiplier") ? s.get("weight_multiplier").getAsDouble() : 1.0D;
        double w = weight * global * own;
        return w <= 0.0D ? 0 : Math.max(1, (int) Math.round(w));
    }

    private static synchronized JsonObject load() {
        if (root != null) {
            return root;
        }
        Path file = Platform.getConfigFolder().resolve(Terrassic.MOD_ID + ".json");
        JsonObject cfg = new JsonObject();
        if (Files.exists(file)) {
            try (Reader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                cfg = GSON.fromJson(r, JsonObject.class);
            } catch (Exception e) {
                LOG.error("Could not read {}, using defaults: {}", file, e.toString());
                root = new JsonObject();
                return root;
            }
        }
        // fill in what is missing and write it back, so the file always lists every species
        boolean changed = false;
        if (!cfg.has("spawn_multiplier")) {
            cfg.addProperty("spawn_multiplier", 1.0D);
            changed = true;
        }
        if (!cfg.has("species")) {
            cfg.add("species", new JsonObject());
            changed = true;
        }
        JsonObject all = cfg.getAsJsonObject("species");
        for (GuideSpecies s : GuideSpecies.ALL) {
            if (!all.has(s.id())) {
                JsonObject e = new JsonObject();
                e.addProperty("enabled", true);
                e.addProperty("weight_multiplier", 1.0D);
                all.add(s.id(), e);
                changed = true;
            }
        }
        if (changed) {
            try {
                Files.createDirectories(file.getParent());
                try (Writer w = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
                    GSON.toJson(cfg, w);
                }
            } catch (IOException e) {
                LOG.warn("Could not write {}: {}", file, e.toString());
            }
        }
        root = cfg;
        return root;
    }
}
