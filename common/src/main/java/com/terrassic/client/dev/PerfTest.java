package com.terrassic.client.dev;

import com.terrassic.config.Eras;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.SwimmingDinosaur;
import dev.architectury.event.events.client.ClientTickEvent;
import jdk.jfr.Recording;
import jdk.jfr.consumer.RecordedEvent;
import jdk.jfr.consumer.RecordedFrame;
import jdk.jfr.consumer.RecordedStackTrace;
import jdk.jfr.consumer.RecordedThread;
import jdk.jfr.consumer.RecordingFile;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPreset;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Development only (TERRASSIC_PERF=1, started from the title screen with no world argument): the cost of the mod with
 * every active species in one place (1.11, docs/DESEMPENHO_1_11.md; a player measured 3.7% with Spark doing just that).
 *
 * <p>A fresh Terrassic world (fixed seed), a creative player hovering over a patch of ground; TERRASSIC_PERF_COUNT (2)
 * of every active species summoned on a grid in front of them, the swimmers in a pool dug beside it. After the warm-up
 * a JFR recording samples every thread every 10 ms for TERRASSIC_PERF_SECONDS (60); the report says what share of the
 * busy time of the server thread and of the render thread had a Terrassic frame on the stack (the same attribution a
 * sampling profiler such as Spark makes for "a mod"), the mean tick time and frame rate, and where inside the mod the
 * samples fall. Writes perf/terrassic_perf_&lt;label&gt;.txt and .jfr in the game directory, then closes the game.
 */
public final class PerfTest {
    private interface Step {
        int run(Minecraft mc);
    }

    private static final Deque<Step> STEPS = new ArrayDeque<>();
    private static final List<String> REPORT = new ArrayList<>();
    private static final List<Double> MSPT = new ArrayList<>();
    private static final List<Integer> FPS = new ArrayList<>();
    private static int wait;
    private static boolean started;
    private static int titleTicks;
    private static boolean measuring;
    private static int measuredTicks;
    private static Recording recording;
    private static int cx;
    private static int cz;
    private static int gy;

    private PerfTest() {
    }

    public static void init() {
        if (!"1".equals(System.getenv("TERRASSIC_PERF"))) {
            return;
        }
        ClientTickEvent.CLIENT_POST.register(PerfTest::tick);
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
            measuredTicks++;
            if (measuredTicks % 20 == 0) {
                FPS.add(mc.getFps());
            }
            if (measuredTicks % 100 == 0 && mc.getSingleplayerServer() != null) {
                MSPT.add(meanTick(mc.getSingleplayerServer()));
            }
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
            REPORT.add("STEP FAILED: " + e);
            org.slf4j.LoggerFactory.getLogger("terrassic").error("[perf] step failed", e);
            w = 1;
        }
        if (w < 0) {
            return;
        }
        STEPS.poll();
        wait = w;
    }

    /** The mean of the last 100 server ticks (the server's own ring of tick times), in ms. */
    private static double meanTick(MinecraftServer server) {
        long sum = 0;
        for (long t : server.tickTimes) {
            sum += t;
        }
        return sum / (double) server.tickTimes.length / 1.0E6D;
    }

    private static void makeWorld(Minecraft mc) {
        long seed = Long.parseLong(env("TERRASSIC_PERF_SEED", "20261108"));
        String name = "perf_" + seed;
        deleteTree(new File(mc.gameDirectory, "saves/" + name));
        GameRules rules = new GameRules();
        rules.getRule(GameRules.RULE_DAYLIGHT).set(false, null);
        rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false, null);
        LevelSettings settings = new LevelSettings(name, GameType.CREATIVE, false, Difficulty.NORMAL, true, rules,
                WorldDataConfiguration.DEFAULT);
        ResourceKey<WorldPreset> preset = ResourceKey.create(Registries.WORLD_PRESET, new ResourceLocation("terrassic", "terrassic"));
        mc.createWorldOpenFlows().createFreshLevel(name, settings, new WorldOptions(seed, true, false),
                access -> access.registryOrThrow(Registries.WORLD_PRESET).getHolderOrThrow(preset).value().createWorldDimensions());
        REPORT.add("Terrassic performance: every active species in one place, fresh Terrassic world, seed " + seed);
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

    private static void plan() {
        int count = Integer.parseInt(env("TERRASSIC_PERF_COUNT", "2"));
        int seconds = Integer.parseInt(env("TERRASSIC_PERF_SECONDS", "60"));
        int warmup = Integer.parseInt(env("TERRASSIC_PERF_WARMUP", "40"));
        cx = Integer.parseInt(env("TERRASSIC_PERF_X", "260"));
        cz = Integer.parseInt(env("TERRASSIC_PERF_Z", "0"));
        STEPS.add(mc -> mc.level == null || mc.player == null || mc.getSingleplayerServer() == null ? -1 : 200);
        STEPS.add(mc -> {
            for (String c : new String[]{"time set 6000", "weather clear"}) {
                command(mc, c);
            }
            mc.options.hideGui = true;
            mc.player.getAbilities().flying = true;
            command(mc, String.format(Locale.ROOT, "tp @s %d 200 %d", cx, cz));
            return 60;
        });
        STEPS.add(mc -> {
            ServerLevel lv = mc.getSingleplayerServer().overworld();
            if (!lv.hasChunkAt(new BlockPos(cx, 64, cz + 24))) {
                return -1;
            }
            gy = lv.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, cx, cz + 20);
            // a clearing for the herd (trees cut, ground levelled) and a pool for the swimmers beside it
            command(mc, String.format(Locale.ROOT, "fill %d %d %d %d %d %d air", cx - 20, gy, cz + 4, cx + 20, gy + 30, cz + 44));
            command(mc, String.format(Locale.ROOT, "fill %d %d %d %d %d %d grass_block", cx - 20, gy - 1, cz + 4, cx + 20, gy - 1, cz + 44));
            command(mc, String.format(Locale.ROOT, "fill %d %d %d %d %d %d water", cx + 8, gy - 4, cz + 30, cx + 20, gy - 1, cz + 44));
            command(mc, String.format(Locale.ROOT, "tp @s %d %d %d facing %d %d %d", cx, gy + 10, cz - 4, cx, gy, cz + 24));
            BlockPos at = new BlockPos(cx, gy, cz + 20);
            REPORT.add(String.format(Locale.ROOT, "place %d %d %d (%s)", cx, gy, cz + 20,
                    lv.getBiome(at).unwrapKey().map(k -> k.location().getPath()).orElse("?")));
            return 40;
        });
        STEPS.add(mc -> {
            List<String> land = new ArrayList<>();
            List<String> sea = new ArrayList<>();
            ServerLevel lv = mc.getSingleplayerServer().overworld();
            for (EntityType<?> type : BuiltInRegistries.ENTITY_TYPE) {
                ResourceLocation key = BuiltInRegistries.ENTITY_TYPE.getKey(type);
                if (!"terrassic".equals(key.getNamespace()) || !Eras.active(key.getPath())) {
                    continue;
                }
                Entity probe = type.create(lv);
                if (!(probe instanceof DinosaurEntity)) {
                    continue;
                }
                (probe instanceof SwimmingDinosaur || probe.getType().getCategory().getName().contains("water") ? sea : land)
                        .add(key.toString());
                probe.discard();
            }
            int n = 0;
            for (String id : land) {
                for (int c = 0; c < count; c++, n++) {
                    int x = cx - 18 + (n % 12) * 3;
                    int z = cz + 6 + (n / 12) * 4;
                    command(mc, String.format(Locale.ROOT, "summon %s %d %d %d", id, x, gy, z));
                }
            }
            int m = 0;
            for (String id : sea) {
                for (int c = 0; c < count; c++, m++) {
                    command(mc, String.format(Locale.ROOT, "summon %s %d %d %d", id, cx + 10 + (m % 5) * 2, gy - 2, cz + 32 + (m / 5) * 2));
                }
            }
            REPORT.add("species: " + land.size() + " on land " + land + ", " + sea.size() + " in the pool " + sea + "; " + count + " of each");
            return warmup * 20;
        });
        STEPS.add(mc -> {
            REPORT.add("at the start of the recording: " + census(mc));
            Screenshot.grab(mc.gameDirectory, "perf_scene_" + label() + ".png", mc.getMainRenderTarget(), msg -> {
            });
            recording = new Recording();
            recording.enable("jdk.ExecutionSample").withPeriod(Duration.ofMillis(10));
            recording.enable("jdk.GarbageCollection");
            recording.enable("jdk.ObjectAllocationSample").with("throttle", "1000/s");
            recording.start();
            measuring = true;
            return seconds * 20;
        });
        STEPS.add(mc -> {
            measuring = false;
            recording.stop();
            REPORT.add("at the end of the recording: " + census(mc));
            try {
                Path dir = new File(mc.gameDirectory, "perf").toPath();
                Files.createDirectories(dir);
                Path jfr = dir.resolve("terrassic_perf_" + label() + ".jfr");
                recording.dump(jfr);
                recording.close();
                analyse(jfr);
                Files.write(dir.resolve("terrassic_perf_" + label() + ".txt"), REPORT, StandardCharsets.UTF_8);
            } catch (Exception e) {
                org.slf4j.LoggerFactory.getLogger("terrassic").error("[perf] report", e);
            }
            mc.stop();
            return 1;
        });
    }

    private static String label() {
        return env("TERRASSIC_PERF_LABEL", "run");
    }

    private static String census(Minecraft mc) {
        ServerLevel lv = mc.getSingleplayerServer().overworld();
        int dinos = 0;
        int all = 0;
        for (Entity e : lv.getAllEntities()) {
            all++;
            if (e instanceof DinosaurEntity) {
                dinos++;
            }
        }
        return dinos + " Terrassic animals of " + all + " entities on the server, " + mc.level.getEntityCount() + " on the client";
    }

    private static boolean ours(RecordedFrame f) {
        if (!f.isJavaFrame()) {
            return false;
        }
        String type = f.getMethod().getType().getName();
        // mixin handlers are merged into the vanilla class with the mod id in their name
        return type.startsWith("com.terrassic.") || f.getMethod().getName().contains("$terrassic$");
    }

    private static String name(RecordedFrame f) {
        String type = f.getMethod().getType().getName();
        return type.substring(type.lastIndexOf('.') + 1) + "." + f.getMethod().getName();
    }

    /** Reads the recording back: for each thread of interest, its samples, the ones with a Terrassic frame, and where. */
    private static void analyse(Path jfr) throws Exception {
        String[] threads = {"Server thread", "Render thread"};
        Map<String, int[]> totals = new HashMap<>();
        Map<String, Map<String, Integer>> inner = new HashMap<>();
        Map<String, Map<String, Integer>> outer = new HashMap<>();
        Map<String, Map<String, Integer>> leaf = new HashMap<>();
        int gcs = 0;
        double gcMs = 0;
        Map<String, Map<String, Long>> alloc = new HashMap<>();
        Map<String, long[]> allocTotal = new HashMap<>();
        for (RecordedEvent e : RecordingFile.readAllEvents(jfr)) {
            String type = e.getEventType().getName();
            if ("jdk.GarbageCollection".equals(type)) {
                gcs++;
                gcMs += e.getDuration().toNanos() / 1.0E6D;
                continue;
            }
            if ("jdk.ObjectAllocationSample".equals(type)) {
                RecordedThread at = e.getThread("eventThread");
                String an = at == null ? "" : at.getJavaName();
                if (!"Server thread".equals(an) && !"Render thread".equals(an)) {
                    continue;
                }
                long w = e.getLong("weight");
                long[] tw = allocTotal.computeIfAbsent(an, k -> new long[2]);
                tw[0] += w;
                RecordedStackTrace ast = e.getStackTrace();
                if (ast != null) {
                    for (RecordedFrame f : ast.getFrames()) {
                        if (ours(f)) {
                            tw[1] += w;
                            alloc.computeIfAbsent(an, k -> new HashMap<>()).merge(name(f) + " (" + e.getClass("objectClass").getName() + ")", w, Long::sum);
                            break;
                        }
                    }
                }
                continue;
            }
            if (!"jdk.ExecutionSample".equals(type)) {
                continue;
            }
            RecordedThread t = e.getThread("sampledThread");
            String tn = t == null ? "" : t.getJavaName();
            String key = null;
            for (String want : threads) {
                if (want.equals(tn)) {
                    key = want;
                }
            }
            if (key == null) {
                continue;
            }
            int[] tot = totals.computeIfAbsent(key, k -> new int[3]);
            tot[0]++;
            RecordedStackTrace st = e.getStackTrace();
            if (st == null) {
                continue;
            }
            if (st.isTruncated()) {
                tot[2]++;
            }
            List<RecordedFrame> frames = st.getFrames();
            RecordedFrame first = null;
            RecordedFrame last = null;
            for (RecordedFrame f : frames) {
                if (ours(f)) {
                    if (first == null) {
                        first = f;
                    }
                    last = f;
                }
            }
            if (first != null) {
                tot[1]++;
                inner.computeIfAbsent(key, k -> new HashMap<>()).merge(name(first), 1, Integer::sum);
                outer.computeIfAbsent(key, k -> new HashMap<>()).merge(name(last), 1, Integer::sum);
                if (!frames.isEmpty()) {
                    leaf.computeIfAbsent(key, k -> new HashMap<>()).merge(name(frames.get(0)), 1, Integer::sum);
                }
            }
        }
        double mspt = MSPT.stream().mapToDouble(Double::doubleValue).average().orElse(0);
        double fps = FPS.stream().mapToInt(Integer::intValue).average().orElse(0);
        REPORT.add(String.format(Locale.ROOT, "server: mean tick %.2f ms over %d windows of 100 ticks %s", mspt, MSPT.size(), fmt(MSPT)));
        REPORT.add(String.format(Locale.ROOT, "client: mean %.0f fps (%s)", fps, FPS));
        REPORT.add(String.format(Locale.ROOT, "GC: %d collections, %.0f ms", gcs, gcMs));
        for (String key : threads) {
            int[] tot = totals.getOrDefault(key, new int[3]);
            double share = tot[0] == 0 ? 0 : 100.0D * tot[1] / tot[0];
            REPORT.add("");
            REPORT.add(String.format(Locale.ROOT, "== %s: %d samples, %d with a Terrassic frame = %.2f%% (%d truncated stacks)",
                    key, tot[0], tot[1], share, tot[2]));
            if ("Server thread".equals(key)) {
                REPORT.add(String.format(Locale.ROOT, "   mod time per tick ~ %.3f ms = %.2f%% of the 50 ms tick budget",
                        mspt * share / 100.0D, mspt * share / 100.0D / 50.0D * 100.0D));
            }
            top(key, "innermost Terrassic frame", inner.get(key), tot[0]);
            top(key, "outermost Terrassic frame", outer.get(key), tot[0]);
            top(key, "leaf frame of the Terrassic samples", leaf.get(key), tot[0]);
            long[] tw = allocTotal.getOrDefault(key, new long[2]);
            double secs = Double.parseDouble(env("TERRASSIC_PERF_SECONDS", "60"));
            REPORT.add(String.format(Locale.ROOT, "  allocation (sampled weight): %.0f MB/s on this thread, %.0f MB/s with a Terrassic frame",
                    tw[0] / secs / 1.0E6D, tw[1] / secs / 1.0E6D));
            Map<String, Long> am = alloc.get(key);
            if (am != null) {
                am.entrySet().stream().sorted((a, b) -> Long.compare(b.getValue(), a.getValue())).limit(15)
                        .forEach(en -> REPORT.add(String.format(Locale.ROOT, "    %8.1f MB/s  %s", en.getValue() / secs / 1.0E6D, en.getKey())));
            }
        }
    }

    private static String fmt(List<Double> v) {
        StringBuilder b = new StringBuilder("[");
        for (double d : v) {
            b.append(String.format(Locale.ROOT, "%.1f ", d));
        }
        return b.toString().trim() + "]";
    }

    private static void top(String thread, String what, Map<String, Integer> counts, int total) {
        if (counts == null) {
            return;
        }
        REPORT.add("  " + what + ":");
        counts.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(30)
                .forEach(en -> REPORT.add(String.format(Locale.ROOT, "    %6.2f%%  %5d  %s", 100.0D * en.getValue() / Math.max(1, total),
                        en.getValue(), en.getKey())));
    }
}
