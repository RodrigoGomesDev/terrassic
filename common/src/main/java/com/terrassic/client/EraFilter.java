package com.terrassic.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.systems.RenderSystem;
import com.terrassic.Terrassic;
import dev.architectury.platform.Platform;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.PostChain;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Reader;
import java.io.Writer;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * The era filter (docs/TEXTURAS_ERA.md, layer D): a light colour grade over the world, warm and a little faded for
 * the Late Cretaceous. The post chain ships inside the era resource pack, so turning the pack off turns the filter
 * off too. It stands down while an Iris/Oculus shaderpack is in use, and can be switched off in
 * config/terrassic-packs.json ("era_filter": false, "era_filter_strength": 0.0 to 1.0).
 * Called by each loader at the end of the world render, before the hand and the HUD.
 */
public final class EraFilter {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final ResourceLocation CHAIN = new ResourceLocation(Terrassic.MOD_ID, "shaders/post/era_cretaceo.json");

    private static PostChain chain;
    private static boolean unavailable;
    private static int width = -1;
    private static int height = -1;
    private static Boolean enabled;
    private static float strength = 0.6f;

    private static boolean irisChecked;
    private static Object irisApi;
    private static Method irisInUse;

    private EraFilter() {
    }

    /** Resource packs were reloaded (F3+T or a pack switched): drop the chain and re-read the config. */
    public static void onResourcesReloaded() {
        close();
        unavailable = false;
        enabled = null;
    }

    public static void render(float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (unavailable || mc.level == null || !enabled() || strength <= 0f || shaderPackInUse()) {
            return;
        }
        RenderTarget main = mc.getMainRenderTarget();
        if (chain == null) {
            try {
                chain = new PostChain(mc.getTextureManager(), mc.getResourceManager(), main, CHAIN);
                setStrength(chain, strength);
            } catch (Exception e) {
                // the era pack is off (no chain in the active packs) or the GPU refused the shader
                unavailable = true;
                LOG.info("Terrassic: era filter not active ({})", e.toString());
                return;
            }
            width = -1;
        }
        if (main.width != width || main.height != height) {
            chain.resize(main.width, main.height);
            width = main.width;
            height = main.height;
        }
        RenderSystem.disableBlend();
        RenderSystem.disableDepthTest();
        RenderSystem.resetTextureMatrix();
        chain.process(partialTick);
        main.bindWrite(true);
        RenderSystem.enableDepthTest();
    }

    /**
     * PostChain has no setUniform in 1.20.1, so the strength goes to each pass's shader. The pass list is private;
     * it is found by type, not by name, so it works with every mapping. If that fails, the default in the shader JSON stays.
     */
    private static void setStrength(PostChain postChain, float value) {
        try {
            for (java.lang.reflect.Field field : PostChain.class.getDeclaredFields()) {
                if (!java.util.List.class.isAssignableFrom(field.getType())) {
                    continue;
                }
                field.setAccessible(true);
                for (Object o : (java.util.List<?>) field.get(postChain)) {
                    if (o instanceof net.minecraft.client.renderer.PostPass pass) {
                        pass.getEffect().safeGetUniform("Strength").set(value);
                    }
                }
            }
        } catch (ReflectiveOperationException | RuntimeException e) {
            LOG.info("Terrassic: era filter strength left at the shader default ({})", e.toString());
        }
    }

    private static void close() {
        if (chain != null) {
            chain.close();
            chain = null;
        }
    }

    private static boolean enabled() {
        if (enabled == null) {
            loadSettings();
        }
        return enabled;
    }

    /** Reads (and fills in) the filter settings in config/terrassic-packs.json, keeping any other keys there. */
    private static void loadSettings() {
        enabled = true;
        Path file = Platform.getConfigFolder().resolve(Terrassic.MOD_ID + "-packs.json");
        try {
            JsonObject root = new JsonObject();
            if (Files.exists(file)) {
                try (Reader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                    JsonObject read = GSON.fromJson(r, JsonObject.class);
                    if (read != null) {
                        root = read;
                    }
                }
            }
            boolean changed = false;
            if (root.has("era_filter")) {
                enabled = root.get("era_filter").getAsBoolean();
            } else {
                root.addProperty("era_filter", true);
                changed = true;
            }
            if (root.has("era_filter_strength")) {
                strength = Math.max(0f, Math.min(1f, root.get("era_filter_strength").getAsFloat()));
            } else {
                root.addProperty("era_filter_strength", strength);
                changed = true;
            }
            if (changed) {
                Files.createDirectories(file.getParent());
                try (Writer w = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
                    GSON.toJson(root, w);
                }
            }
        } catch (Exception e) {
            LOG.warn("Terrassic: could not read {} ({}); era filter stays on", file, e.toString());
        }
    }

    /** Iris (Fabric) and Oculus (Forge) expose the same API; looked up by name so neither is a dependency. */
    private static boolean shaderPackInUse() {
        if (!irisChecked) {
            irisChecked = true;
            try {
                Class<?> api = Class.forName("net.irisshaders.iris.api.v0.IrisApi");
                irisApi = api.getMethod("getInstance").invoke(null);
                irisInUse = api.getMethod("isShaderPackInUse");
            } catch (Throwable t) {
                irisApi = null;
            }
        }
        if (irisApi == null) {
            return false;
        }
        try {
            return (Boolean) irisInUse.invoke(irisApi);
        } catch (Throwable t) {
            return false;
        }
    }
}
