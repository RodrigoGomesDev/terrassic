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
 *   "title_screen": true,    // the Terrassic main menu in place of the vanilla title screen (docs/MENU.md; off in
 *                            // code since v0.14.3, see titleScreen())
 *   "loading_tips": true,    // a real fact or a game tip on the world loading screens
 *   "hud_style": "amber",    // v0.14 HUD (docs/HUD.md): "amber" (slabs and drops of amber) or "compact"
 *   "hud_scale": "auto",     // v0.14.4: scale of the mount plate and the notices; "auto" = one step under the GUI
 *   "hud_mount": true,       // HUD: plate of the dinosaur you ride
 *   "hud_notices": true,     // HUD: notices about your animals on the right (false = action bar, as before)
 *   "hud_numbers_always": false, // HUD: the mount's health in numbers all the time (default: when it changes)
 *   "hud_nameplate": true,   // HUD: nameplate over the animal you look at
 *   "hud_taming": true,      // HUD: torpor and taming bars beside a knocked-out animal
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
    private static final String[] FLAGS = {"title_screen", "loading_tips", "hud_mount", "hud_notices", "hud_nameplate",
            "hud_taming", "hud_new_species", "hud_era_title", "hud_rift_alert", "shooting_stars", "ritual_sky",
            "terrassic_fonts", "roar_shake", "mount_attack"};
    /** The options that are off until the player turns them on. */
    private static final String[] OFF = {"hud_numbers_always"};

    private ClientConfig() {
    }

    /** The mod's own title screen and loading screens (docs/MENU.md). Off since v0.14.3 whatever the option says:
     *  Rodrigo (30/10/2026) wants Minecraft's own menu for now. The screens stay in the mod for when they come back. */
    private static final boolean MENU_READY = false;

    public static boolean titleScreen() {
        return MENU_READY && flag("title_screen");
    }

    public static boolean loadingTips() {
        return flag("loading_tips");
    }

    /** Any boolean option above; missing ones count as their default (on, except {@link #OFF}). */
    public static boolean flag(String name) {
        JsonObject cfg = load();
        if (!cfg.has(name)) {
            return !java.util.Arrays.asList(OFF).contains(name);
        }
        return cfg.get(name).getAsBoolean();
    }

    /**
     * The scale of the mount plate and the notices (v0.14.4): one step under the GUI scale ("auto": GUI 3 draws them
     * at 2, GUI 4 at 3, never under 1), or the number in "hud_scale", never over the GUI scale. Rodrigo (30/10/2026)
     * found them too big at the GUI's own scale.
     */
    public static int hudScale(net.minecraft.client.Minecraft mc) {
        int gui = Math.max(1, (int) Math.round(mc.getWindow().getGuiScale()));
        JsonObject cfg = load();
        if (cfg.has("hud_scale") && cfg.get("hud_scale").isJsonPrimitive() && cfg.get("hud_scale").getAsJsonPrimitive().isNumber()) {
            return Math.max(1, Math.min(gui, cfg.get("hud_scale").getAsInt()));
        }
        return Math.max(1, gui - 1);
    }

    /** "hud_scale" as the options screen shows it: 0 for "auto", or 1 to 4. */
    public static int hudScaleOption() {
        JsonObject cfg = load();
        if (cfg.has("hud_scale") && cfg.get("hud_scale").isJsonPrimitive() && cfg.get("hud_scale").getAsJsonPrimitive().isNumber()) {
            return Math.max(1, Math.min(4, cfg.get("hud_scale").getAsInt()));
        }
        return 0;
    }

    public static synchronized void setHudScaleOption(int scale) {
        if (scale <= 0) {
            load().addProperty("hud_scale", "auto");
        } else {
            load().addProperty("hud_scale", scale);
        }
        save();
    }

    /** The compact HUD style ("hud_style": "compact"); anything else is the Âmbar look. */
    public static boolean compactHud() {
        JsonObject cfg = load();
        return cfg.has("hud_style") && "compact".equals(cfg.get("hud_style").getAsString());
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
        for (String name : OFF) {
            if (!cfg.has(name)) {
                cfg.addProperty(name, false);
                changed = true;
            }
        }
        if (!cfg.has("hud_style")) {
            cfg.addProperty("hud_style", "amber");
            changed = true;
        }
        if (!cfg.has("hud_scale")) {
            cfg.addProperty("hud_scale", "auto");
            changed = true;
        }
        // the pack bar left in v0.14 (the notices took its place)
        if (cfg.has("hud_pack")) {
            cfg.remove("hud_pack");
            changed = true;
        }
        root = cfg;
        if (changed) {
            save();
        }
        return root;
    }

    /** Changes an option and writes the file (the HUD options screen, v0.14.2). */
    public static synchronized void set(String name, boolean value) {
        load().addProperty(name, value);
        save();
    }

    public static synchronized void setHudStyle(boolean compact) {
        load().addProperty("hud_style", compact ? "compact" : "amber");
        save();
    }

    private static void save() {
        Path file = Platform.getConfigFolder().resolve("terrassic-client.json");
        try {
            Files.createDirectories(file.getParent());
            try (Writer w = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
                GSON.toJson(root, w);
            }
        } catch (IOException e) {
            LOG.warn("Could not write {}: {}", file, e.toString());
        }
    }
}
