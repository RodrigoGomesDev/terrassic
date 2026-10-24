package com.terrassic.forge;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.terrassic.Terrassic;
import net.minecraft.client.Minecraft;
import net.minecraftforge.fml.loading.FMLPaths;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Switches a built-in pack on once, the first time the mod runs, by adding it to the selected packs in options.txt
 * (the packs are found before options.txt is applied). config/terrassic-packs.json remembers it, so a player who
 * turns the pack off keeps it off. Client only.
 */
final class EraPacksClient {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    private EraPacksClient() {
    }

    static void enableOnce(String id) {
        try {
            Minecraft mc = Minecraft.getInstance();
            if (mc == null || mc.options == null) {
                return;
            }
            Path file = FMLPaths.CONFIGDIR.get().resolve(Terrassic.MOD_ID + "-packs.json");
            JsonObject root = new JsonObject();
            if (Files.exists(file)) {
                try (Reader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                    root = GSON.fromJson(r, JsonObject.class);
                }
            }
            JsonArray done = root != null && root.has("enabled_once") ? root.getAsJsonArray("enabled_once") : new JsonArray();
            for (JsonElement e : done) {
                if (id.equals(e.getAsString())) {
                    return;
                }
            }
            if (!mc.options.resourcePacks.contains(id)) {
                mc.options.resourcePacks.add(id);
                mc.options.save();
            }
            done.add(id);
            JsonObject out = root != null ? root : new JsonObject();   // keep the other settings (era filter)
            out.add("enabled_once", done);
            Files.createDirectories(file.getParent());
            try (Writer w = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
                GSON.toJson(out, w);
            }
        } catch (Exception e) {
            LOG.warn("Terrassic: could not switch on the built-in pack {} ({})", id, e.toString());
        }
    }
}
