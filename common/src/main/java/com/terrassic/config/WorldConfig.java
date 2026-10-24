package com.terrassic.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.terrassic.Terrassic;
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
 * World options of the v0.8 front ("Mundo Terrassic"), in {@code config/terrassic-world.json}, read once and written
 * back with the defaults that are missing:
 * <pre>
 * {
 *   "rift_storms": true,          // Rift Storms happen at all
 *   "storm_chance": 0.2,          // chance of a storm at each dusk, once the pause below has passed
 *   "storm_min_days": 3,          // in-game days between two storms
 *   "storm_minutes_min": 3,       // length of a storm, in real minutes
 *   "storm_minutes_max": 5,
 *   "storm_creatures": 3,         // creatures from other eras that can be around each player at once
 *   "mundo_padrao": true,         // "Criar novo mundo" opens on the Terrassic world type (docs/MUNDO.md, 10.3)
 *   "borda": true,                // a new continent world gets a world border around its sea (10.2)
 *   "borda_em_raios": 2.0         // distance from the middle of the continent to the border, in continent radii
 * }
 * </pre>
 */
public final class WorldConfig {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static JsonObject root;

    private WorldConfig() {
    }

    public static boolean riftStorms() {
        try {
            return get().get("rift_storms").getAsBoolean();
        } catch (RuntimeException e) {
            return true;
        }
    }

    public static double stormChance() {
        return number("storm_chance", 0.2D);
    }

    public static int stormMinDays() {
        return (int) number("storm_min_days", 3);
    }

    public static int stormMinutesMin() {
        return Math.max(1, (int) number("storm_minutes_min", 3));
    }

    public static int stormMinutesMax() {
        return Math.max(stormMinutesMin(), (int) number("storm_minutes_max", 5));
    }

    public static int stormCreatures() {
        return Math.max(0, (int) number("storm_creatures", 3));
    }

    /** "Criar novo mundo" opens on the Terrassic world type. */
    public static boolean defaultWorldType() {
        return bool("mundo_padrao", true);
    }

    /** A new continent world gets a square world border around its sea. */
    public static boolean continentBorder() {
        return bool("borda", true);
    }

    /** Distance from the middle of the continent to the world border, in continent radii (at least 1.1). */
    public static double continentBorderRadii() {
        return Math.max(1.1D, number("borda_em_raios", 2.0D));
    }

    /** A boolean from the file, or the default when the value is missing or not a boolean (never throws). */
    private static boolean bool(String key, boolean fallback) {
        try {
            return get().get(key).getAsBoolean();
        } catch (RuntimeException e) {
            return fallback;
        }
    }

    /** A number from the file, or the default when the value is missing or not a number (never throws). */
    private static double number(String key, double fallback) {
        try {
            return get().get(key).getAsDouble();
        } catch (RuntimeException e) {
            return fallback;
        }
    }

    private static synchronized JsonObject get() {
        if (root != null) {
            return root;
        }
        Path file = Platform.getConfigFolder().resolve(Terrassic.MOD_ID + "-world.json");
        JsonObject cfg = new JsonObject();
        if (Files.exists(file)) {
            try (Reader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                JsonObject read = GSON.fromJson(r, JsonObject.class);
                if (read != null) {
                    cfg = read;
                }
            } catch (Exception e) {
                LOG.error("Could not read {}, using defaults: {}", file, e.toString());
                cfg = new JsonObject();
            }
        }
        boolean changed = false;
        changed |= def(cfg, "rift_storms", true);
        changed |= def(cfg, "storm_chance", 0.2D);
        changed |= def(cfg, "storm_min_days", 3);
        changed |= def(cfg, "storm_minutes_min", 3);
        changed |= def(cfg, "storm_minutes_max", 5);
        changed |= def(cfg, "storm_creatures", 3);
        changed |= def(cfg, "mundo_padrao", true);
        changed |= def(cfg, "borda", true);
        changed |= def(cfg, "borda_em_raios", 2.0D);
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

    private static boolean def(JsonObject cfg, String key, Object value) {
        if (cfg.has(key)) {
            return false;
        }
        if (value instanceof Boolean b) {
            cfg.addProperty(key, b);
        } else {
            cfg.addProperty(key, (Number) value);
        }
        return true;
    }
}
