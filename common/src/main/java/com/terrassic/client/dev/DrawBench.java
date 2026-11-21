package com.terrassic.client.dev;

import com.terrassic.client.LeanGeoRenderer;
import com.terrassic.config.Eras;
import com.terrassic.entity.DinosaurEntity;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPreset;
import net.minecraft.world.level.levelgen.presets.WorldPresets;

import java.io.File;
import java.lang.management.ManagementFactory;
import java.lang.management.ThreadMXBean;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Locale;

/**
 * Development only (TERRASSIC_DRAWBENCH=1): what one animal of each species costs to draw (1.11, docs/DESEMPENHO_1_11.md,
 * "Modelos"). A fresh superflat world, no spawning, a creative player looking at a 4 x 4 grid of TERRASSIC_DRAWBENCH_COUNT
 * (16) animals of one species standing still (NoAI: they play their idle). For each species: the empty view first, then
 * the grid drawn three ways (GeckoLib's own cube writer, the lean writer, the lean writer with back faces of closed
 * cubes left out, LeanGeoRenderer), each for TERRASSIC_DRAWBENCH_SECONDS (3). Per way: frames, render-thread CPU per
 * frame, wall time per frame, quads written and the time inside the renderers. The cost of one animal is the
 * render-thread time per frame above the empty view, over the count. 64 cows give the vanilla yardstick.
 * Writes perf/terrassic_drawbench_&lt;label&gt;.tsv and .txt in the game directory, then closes the game.
 * TERRASSIC_DRAWBENCH_SPECIES=a,b limits the list; TERRASSIC_DRAWBENCH_MODES=A,B,C the ways.
 */
public final class DrawBench {
    private interface Step {
        int run(Minecraft mc);
    }

    private static final Deque<Step> STEPS = new ArrayDeque<>();
    private static final List<String> ROWS = new ArrayList<>();
    private static final List<String> NOTES = new ArrayList<>();
    private static int wait;
    private static boolean started;
    private static int titleTicks;
    private static int gy;
    // the window being measured
    private static boolean measuring;
    private static long cpu0;
    private static long wall0;
    private static long frames;
    private static long lastLogEnd;
    private static long rendered;

    private DrawBench() {
    }

    public static void init() {
        if (!"1".equals(System.getenv("TERRASSIC_DRAWBENCH"))) {
            return;
        }
        ClientTickEvent.CLIENT_POST.register(DrawBench::tick);
        plan();
    }

    private static String env(String key, String def) {
        return System.getenv().getOrDefault(key, def);
    }

    private static void tick(Minecraft mc) {
        if (!started) {
            if (mc.screen instanceof TitleScreen && mc.getOverlay() == null && ++titleTicks > 40) {
                started = true;
                makeWorld(mc);
            }
            return;
        }
        if (measuring) {
            long end = FrameCount.frames;
            frames += (end - lastLogEnd);
            lastLogEnd = end;
        }
        if (wait > 0) {
            wait--;
            return;
        }
        Step s = STEPS.peek();
        if (s == null) {
            return;
        }
        int w;
        try {
            w = s.run(mc);
        } catch (Throwable e) {
            NOTES.add("STEP FAILED: " + e);
            org.slf4j.LoggerFactory.getLogger("terrassic").error("[drawbench] step failed", e);
            w = 1;
        }
        if (w < 0) {
            return;
        }
        STEPS.poll();
        wait = w;
    }

    private static void makeWorld(Minecraft mc) {
        String name = "drawbench";
        deleteTree(new File(mc.gameDirectory, "saves/" + name));
        GameRules rules = new GameRules();
        rules.getRule(GameRules.RULE_DAYLIGHT).set(false, null);
        rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false, null);
        rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false, null);
        rules.getRule(GameRules.RULE_DOENTITYDROPS).set(false, null);
        LevelSettings settings = new LevelSettings(name, GameType.CREATIVE, false, Difficulty.PEACEFUL, true, rules,
                WorldDataConfiguration.DEFAULT);
        ResourceKey<WorldPreset> preset = WorldPresets.FLAT;
        mc.createWorldOpenFlows().createFreshLevel(name, settings, new WorldOptions(1L, false, false),
                access -> access.registryOrThrow(Registries.WORLD_PRESET).getHolderOrThrow(preset).value().createWorldDimensions(), mc.screen);
    }

    private static void deleteTree(File f) {
        File[] in = f.listFiles();
        if (in != null) {
            for (File c : in) {
                deleteTree(c);
            }
        }
        f.delete();
    }

    private static void command(Minecraft mc, String c) {
        mc.player.connection.sendCommand(c);
    }

    private static long cpu() {
        ThreadMXBean mx = ManagementFactory.getThreadMXBean();
        return mx.getCurrentThreadCpuTime();
    }

    private static void begin(Minecraft mc) {
        measuring = true;
        frames = 0;
        lastLogEnd = FrameCount.frames;
        cpu0 = cpu();
        wall0 = System.nanoTime();
        LeanGeoRenderer.takeQuads();
        LeanGeoRenderer.takeRenderNanos();
    }

    /** One row: species, count, way, frames, cpu ms/frame, wall ms/frame, quads/frame, renderer ms/frame. */
    private static void end(Minecraft mc, String id, int count, String mode) {
        long e = FrameCount.frames;
        frames += (e - lastLogEnd);
        measuring = false;
        double f = Math.max(1, frames);
        double cpuMs = (cpu() - cpu0) / 1.0E6D / f;
        double wallMs = (System.nanoTime() - wall0) / 1.0E6D / f;
        double q = LeanGeoRenderer.takeQuads() / f;
        double r = LeanGeoRenderer.takeRenderNanos() / 1.0E6D / f;
        ROWS.add(String.format(Locale.ROOT, "%s\t%d\t%s\t%d\t%.4f\t%.4f\t%.1f\t%.4f", id, count, mode, frames, cpuMs, wallMs, q, r));
        org.slf4j.LoggerFactory.getLogger("terrassic").info("[drawbench] {}", ROWS.get(ROWS.size() - 1));
    }

    private static void plan() {
        int count = Integer.parseInt(env("TERRASSIC_DRAWBENCH_COUNT", "16"));
        int seconds = Integer.parseInt(env("TERRASSIC_DRAWBENCH_SECONDS", "3"));
        String only = env("TERRASSIC_DRAWBENCH_SPECIES", "");
        String[] modes = env("TERRASSIC_DRAWBENCH_MODES", "A,B,C").split(",");
        STEPS.add(mc -> mc.level == null || mc.player == null || mc.getSingleplayerServer() == null ? -1 : 100);
        STEPS.add(mc -> {
            mc.options.hideGui = true;
            mc.options.framerateLimit().set(260);
            mc.options.enableVsync().set(false);
            mc.options.renderDistance().set(6);
            mc.options.entityDistanceScaling().set(5.0D);
            command(mc, "gamemode spectator");
            command(mc, "time set 6000");
            command(mc, "kill @e[type=!player]");
            gy = mc.getSingleplayerServer().overworld().getMinBuildHeight() + 4;
            NOTES.add("superflat, ground at y " + gy + "; " + count + " of each species, 64 cows; " + seconds + " s per way");
            NOTES.add("ways: A = GeckoLib's cube writer, B = lean writer, C = lean writer + back faces of closed opaque cubes left out");
            return 400;   // chunks around, shaders and textures warmed
        });
        List<String> ids = new ArrayList<>();
        if (only.isEmpty() || only.contains("cow")) {
            ids.add("minecraft:cow");
        }
        // the list is read once the registries are up, at the first species step
        STEPS.add(mc -> {
            ServerLevel lv = mc.getSingleplayerServer().overworld();
            List<String> found = new ArrayList<>();
            for (EntityType<?> type : BuiltInRegistries.ENTITY_TYPE) {
                ResourceLocation key = BuiltInRegistries.ENTITY_TYPE.getKey(type);
                if (!"terrassic".equals(key.getNamespace()) || (only.isEmpty() && !Eras.active(key.getPath()))) {
                    continue;
                }
                if (!only.isEmpty() && !List.of(only.split(",")).contains(key.getPath())) {
                    continue;
                }
                Entity probe = type.create(lv);
                if (probe instanceof DinosaurEntity) {
                    found.add(key.toString());
                }
                if (probe != null) {
                    probe.discard();
                }
            }
            found.sort(String::compareTo);
            ids.addAll(found);
            for (String id : ids) {
                species(id, id.equals("minecraft:cow") ? Integer.parseInt(env("TERRASSIC_DRAWBENCH_COWS", "64")) : count, seconds, modes);
            }
            STEPS.add(DrawBench::finish);
            return 1;
        });
    }

    private static void species(String id, int count, int seconds, String[] modes) {
        int side = (int) Math.ceil(Math.sqrt(count));
        STEPS.add(mc -> {
            EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.parse(id));
            float w = type.getWidth();
            float h = type.getHeight();
            double spacing = Math.max(1.5D, Math.ceil(w * 1.15D));
            double extent = (side - 1) * spacing + w;
            // TERRASSIC_DRAWBENCH_VIEW: where the camera stands, in degrees round the grid (0 = behind the animals,
            // which face south; 150 = in front, to their right); TERRASSIC_DRAWBENCH_ZOOM brings it nearer (photos)
            double view = Math.toRadians(Double.parseDouble(env("TERRASSIC_DRAWBENCH_VIEW", "0")));
            double zoom = Double.parseDouble(env("TERRASSIC_DRAWBENCH_ZOOM", "1"));
            double dist = (Math.max(extent, h * 1.6D) * 1.15D + 4.0D) * zoom;
            double cx = 0.5D, cz = 0.5D;
            double ey = gy + h * 0.6D + dist * 0.45D;
            command(mc, "kill @e[type=!player]");
            command(mc, String.format(Locale.ROOT, "tp @s %.2f %.2f %.2f facing %.2f %.2f %.2f", cx + dist * Math.sin(view), ey,
                    cz - dist * Math.cos(view), cx, gy + h * 0.4D, cz));
            BENCH_ID = id;
            BENCH_SPACING = spacing;
            BENCH_SIDE = side;
            BENCH_COUNT = count;
            return 40;
        });
        STEPS.add(mc -> {
            begin(mc);
            return seconds * 20;
        });
        STEPS.add(mc -> {
            end(mc, id, 0, "empty");
            for (int i = 0; i < BENCH_COUNT; i++) {
                double x = 0.5D + (i % BENCH_SIDE - (BENCH_SIDE - 1) / 2.0D) * BENCH_SPACING;
                double z = 0.5D + (i / BENCH_SIDE - (BENCH_SIDE - 1) / 2.0D) * BENCH_SPACING;
                command(mc, String.format(Locale.ROOT, "summon %s %.2f %d %.2f {NoAI:1b,PersistenceRequired:1b,Invulnerable:1b,Rotation:[180f,0f]}",
                        id, x, gy, z));
            }
            return 60;
        });
        for (String mode : modes) {
            STEPS.add(mc -> {
                LeanGeoRenderer.setLean(!"A".equals(mode));
                LeanGeoRenderer.setBackfaces("C".equals(mode));
                return 10;
            });
            STEPS.add(mc -> {
                begin(mc);
                return seconds * 20;
            });
            STEPS.add(mc -> {
                end(mc, id, BENCH_COUNT, mode);
                return 1;
            });
        }
        if ("1".equals(env("TERRASSIC_DRAWBENCH_SHOTS", "0"))) {
            // the same frozen frame drawn the three ways (paused: the animations and the live layer stand still)
            STEPS.add(mc -> {
                mc.setScreen(new Freeze());
                return 20;
            });
            for (String mode : new String[]{"A", "B", "C"}) {
                STEPS.add(mc -> {
                    LeanGeoRenderer.setLean(!"A".equals(mode));
                    LeanGeoRenderer.setBackfaces("C".equals(mode));
                    return 6;
                });
                STEPS.add(mc -> {
                    Screenshot.grab(mc.gameDirectory, "drawbench_" + label() + "_" + id.replace("minecraft:", "").replace("terrassic:", "")
                            + "_" + mode + ".png", mc.getMainRenderTarget(), msg -> {
                    });
                    return 4;
                });
            }
            STEPS.add(mc -> {
                mc.setScreen(null);
                return 4;
            });
        }
        STEPS.add(mc -> {
            LeanGeoRenderer.setLean(true);
            LeanGeoRenderer.setBackfaces(true);
            command(mc, "kill @e[type=!player]");
            return 30;
        });
        STEPS.add(mc -> {
            command(mc, "kill @e[type=!player]");   // the carcasses the first kill left
            return 30;
        });
        STEPS.add(mc -> {
            begin(mc);
            return seconds * 20;
        });
        STEPS.add(mc -> {
            end(mc, id, 0, "empty2");
            return 1;
        });
    }

    /** A pause screen that draws nothing: the world stands still and shows through untouched. */
    private static final class Freeze extends net.minecraft.client.gui.screens.Screen {
        Freeze() {
            super(net.minecraft.network.chat.Component.empty());
        }

        @Override
        public boolean isPauseScreen() {
            return true;
        }

        @Override
        public void render(net.minecraft.client.gui.GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        }
    }

    private static String BENCH_ID = "";
    private static double BENCH_SPACING;
    private static int BENCH_SIDE;
    private static int BENCH_COUNT;

    private static String label() {
        return env("TERRASSIC_DRAWBENCH_LABEL", "run");
    }

    private static int finish(Minecraft mc) {
        try {
            Path dir = new File(mc.gameDirectory, "perf").toPath();
            Files.createDirectories(dir);
            List<String> out = new ArrayList<>();
            out.add("species\tcount\tway\tframes\tcpu_ms_per_frame\twall_ms_per_frame\tquads_per_frame\trenderer_ms_per_frame");
            out.addAll(ROWS);
            Files.write(dir.resolve("terrassic_drawbench_" + label() + ".tsv"), out, StandardCharsets.UTF_8);
            Files.write(dir.resolve("terrassic_drawbench_" + label() + ".txt"), NOTES, StandardCharsets.UTF_8);
        } catch (Exception e) {
            org.slf4j.LoggerFactory.getLogger("terrassic").error("[drawbench] report", e);
        }
        mc.stop();
        return 1;
    }
}
