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
 *   "title_screen": true,    // the Terrassic main menu in place of the vanilla title screen (docs/MENU.md)
 *   "loading_tips": true,    // a real fact or a game tip on the world loading screens
 *   "hud_mount": true,       // HUD: panel of the dinosaur you ride
 *   "hud_pack": true,        // HUD: your tamed dinosaurs nearby
 *   "hud_new_species": true, // HUD: toast when a species reaches a new Field Guide level
 *   "hud_era_title": true,   // HUD: the era's name when you arrive
 *   "hud_rift_alert": true,  // HUD: pulsing amber shard during a Rift Storm
 *   "shooting_stars": true,  // v0.9: shooting stars at night, more with each amber fragment
 *   "ritual_sky": true,      // v0.9: red sky and fog around an altar during the ritual of the meteors
 *   "terrassic_fonts": true, // the mod's own typefaces (Sedimento, Entalhe, Caderno); false = vanilla font
 *   "roar_shake": true,      // the camera shakes near a loud roar (T. rex)
 *   "mount_attack": true     // v0.12: riding your dinosaur, a left click is its attack (false = your own hand)
 * }
 * </pre>
 */
public final class ClientConfig {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static JsonObject root;
    private static final String[] FLAGS = {"title_screen", "loading_tips", "hud_mount", "hud_pack", "hud_new_species",
            "hud_era_title", "hud_rift_alert", "shooting_stars", "ritual_sky",
            "terrassic_fonts", "roar_shake", "mount_attack"};

    private ClientConfig() {
    }

    public static boolean titleScreen() {
        return flag("title_screen");
    }

    public static boolean loadingTips() {
        return flag("loading_tips");
    }

    /** Any boolean option above; missing ones count as on. */
    public static boolean flag(String name) {
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
        for (String name : FLAGS) {
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
