package com.terrassic.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
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
 * Client-only options, in {@code config/terrassic-client.json} (read once, written back with the defaults that are
 * missing so the file always lists every option):
 * <pre>
 * {
 *   "title_screen": true,    // Terrassic panorama, logo and splashes on the title screen
 *   "loading_tips": true     // a real fact or a game tip on the world loading screens
 * }
 * </pre>
 */
public final class ClientConfig {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static JsonObject root;

    private ClientConfig() {
    }

    public static boolean titleScreen() {
        return flag("title_screen");
    }

    public static boolean loadingTips() {
        return flag("loading_tips");
    }

    private static boolean flag(String name) {
        JsonObject cfg = load();
        return !cfg.has(name) || cfg.get(name).getAsBoolean();
    }

    private static synchronized JsonObject load() {
        if (root != null) {
            return root;
        }
        Path file = Platform.getConfigFolder().resolve("terrassic-client.json");
        JsonObject cfg = new JsonObject();
        if (Files.exists(file)) {
            try (Reader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                JsonObject read = GSON.fromJson(r, JsonObject.class);
                if (read != null) {
                    cfg = read;
                }
            } catch (Exception e) {
                LOG.error("Could not read {}, using defaults: {}", file, e.toString());
                root = new JsonObject();
                return root;
            }
        }
        boolean changed = false;
        for (String name : new String[]{"title_screen", "loading_tips"}) {
            if (!cfg.has(name)) {
                cfg.addProperty(name, true);
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
