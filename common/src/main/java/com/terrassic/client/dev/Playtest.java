package com.terrassic.client.dev;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.HerbivoreDinosaur;
import com.terrassic.entity.PredatorDinosaur;
import com.terrassic.world.EcoSpawner;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPreset;
import net.minecraft.world.phys.Vec3;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Development only (TERRASSIC_PLAYTEST=1, started from the title screen, no world argument): the mod played the way a
 * player meets it, not in a flat arena (Rodrigo, 08/11/2026: "simule um player testando/jogando o mod").
 *
 * <p>It makes a fresh world of the Terrassic type (fixed seed, TERRASSIC_PLAYTEST_SEED), puts a survival player in it
 * (who cannot die: resistance V) and takes them to a string of places from the Arrival Crater out into the dense
 * forest, by day and at night. At each place the ecosystem fills in on its own (EcoSpawner), the player stands, looks
 * around, walks crouched towards the nearest hunter, strikes the nearest herbivore, and photographs what they see.
 * Every animal near is followed every second: stuck while trying to walk, inside a block, hopping in the water,
 * asleep next to a hunter, hunting the player (and from how far). The report goes to terrassic_playtest_report.txt,
 * the photos to screenshots/playtest_*.png; tools/validation/playtest_report.py reads both with the game log.
 */
public final class Playtest {
    private interface Step {
        int run(Minecraft mc);
    }

    private static final Deque<Step> STEPS = new ArrayDeque<>();
    private static final List<String> REPORT = new ArrayList<>();
    /** per animal (entity id) followed at the current place */
    private static final Map<Integer, Track> TRACK = new ConcurrentHashMap<>();
    private static int wait;
    private static boolean started;
    private static int titleTicks;
    private static String place = "";
    private static int shots;
    private static int photoNo;

    /** what one animal did while the player was at a place */
    private static final class Track {
        String species;
        boolean predator;
        Vec3 last;
        int tryingStill;        // seconds with a path in progress and under 0.3 block moved
        int worstStill;
        int inWall;
        int waterHops;
        double lastVy;
        boolean asleep;
        double sleepNearHunter = 999.0D;
        int huntedPlayerAt = -1;  // distance when it first took the player as its target
        int fled;
        String stuckWhy = "";
        boolean struckPlayer;
    }

    private static String goals(DinosaurEntity d) {
        try {
            java.lang.reflect.Field f = net.minecraft.world.entity.Mob.class.getDeclaredField("goalSelector");
            f.setAccessible(true);
            StringBuilder b = new StringBuilder();
            ((net.minecraft.world.entity.ai.goal.GoalSelector) f.get(d)).getRunningGoals()
                    .forEach(g -> b.append(g.getGoal().getClass().getSimpleName()).append(' '));
            return b.toString().trim();
        } catch (ReflectiveOperationException e) {
            return "?";
        }
    }

    private Playtest() {
    }

    public static void init() {
        if (!"1".equals(System.getenv("TERRASSIC_PLAYTEST"))) {
            return;
        }
        ClientTickEvent.CLIENT_POST.register(Playtest::tick);
        plan();
    }

    private static void tick(Minecraft mc) {
        if (!started) {
            // only once the resources have loaded (no reload overlay): a world made earlier crashed the client in
            // ModelManager.requiresRender (08/11)
            if (mc.screen instanceof TitleScreen && mc.getOverlay() == null && ++titleTicks > 40) {
                started = true;
                makeWorld(mc);
            }
            return;
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
        } catch (RuntimeException e) {
            REPORT.add("  STEP FAILED: " + e);
            w = 1;
        }
        if (w < 0) {
            return;     // not ready yet: run it again next tick
        }
        STEPS.poll();
        wait = w;
    }

    // ------------------------------------------------------------------ the world
    private static void makeWorld(Minecraft mc) {
        long seed = Long.parseLong(System.getenv().getOrDefault("TERRASSIC_PLAYTEST_SEED", "20261108"));
        String name = "playtest_" + seed;
        File dir = new File(mc.gameDirectory, "saves/" + name);
        deleteTree(dir);    // always a fresh world: the ecosystem must fill it from nothing, as for a new player
        GameRules rules = new GameRules();
        rules.getRule(GameRules.RULE_DAYLIGHT).set(false, null);
        rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false, null);
        LevelSettings settings = new LevelSettings(name, GameType.SURVIVAL, false, Difficulty.NORMAL, true, rules,
                WorldDataConfiguration.DEFAULT);
        ResourceKey<WorldPreset> preset = ResourceKey.create(Registries.WORLD_PRESET, new ResourceLocation("terrassic", "terrassic"));
        mc.createWorldOpenFlows().createFreshLevel(name, settings, new WorldOptions(seed, true, false),
                access -> access.registryOrThrow(Registries.WORLD_PRESET).getHolderOrThrow(preset).value().createWorldDimensions());
        REPORT.add("Terrassic playtest: a fresh Terrassic world, seed " + seed + ", a survival player who cannot die");
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

    // ------------------------------------------------------------------ the tour
    private static void plan() {
        STEPS.add(mc -> mc.level == null || mc.player == null || mc.getSingleplayerServer() == null ? -1 : 200);
        STEPS.add(mc -> {
            for (String c : new String[]{"effect give @s minecraft:resistance infinite 4 true",
                    "effect give @s minecraft:saturation infinite 0 true", "effect give @s minecraft:water_breathing infinite 0 true",
                    "effect give @s minecraft:fire_resistance infinite 0 true", "time set 1000", "weather clear"}) {
                command(mc, c);
            }
            mc.options.hideGui = true;
            return 20;
        });
        // from the crater outwards, every heading; the continent is about 1200 blocks across (world_preset raio)
        int[][] places = {{0, 60}, {260, 0}, {0, -420}, {-520, 120}, {380, 520}, {760, -200}, {-300, -800}, {-900, -300},
                {150, 950}, {1000, 450}};
        for (int i = 0; i < places.length; i++) {
            boolean night = i == 4 || i == 8;
            visit(i, places[i][0], places[i][1], night);
        }
        STEPS.add(mc -> {
            write(mc);
            mc.stop();
            return 1;
        });
    }

    private static void visit(int i, int x, int z, boolean night) {
        STEPS.add(mc -> {
            TRACK.clear();
            shots = 0;
            command(mc, "time set " + (night ? 18000 : 1000 + i * 700));
            command(mc, String.format(Locale.ROOT, "tp @s %d 200 %d", x, z));
            return 60;
        });
        // stand on the ground there once it has loaded
        STEPS.add(mc -> {
            ServerLevel lv = mc.getSingleplayerServer().overworld();
            if (!lv.hasChunkAt(new BlockPos(x, 64, z))) {
                return -1;
            }
            int y = lv.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            command(mc, String.format(Locale.ROOT, "tp @s %d %d %d", x, y + 1, z));
            BlockPos at = new BlockPos(x, y, z);
            place = String.format(Locale.ROOT, "%d %d (%s, %s%s)", x, z, lv.getBiome(at).unwrapKey().map(k -> k.location().getPath()).orElse("?"),
                    EcoSpawner.zoneOf(lv, at, lv.getBiome(at)), night ? ", night" : "");
            REPORT.add("");
            REPORT.add("== Place " + (i + 1) + ": " + place);
            return 20;
        });
        // the ecosystem fills in around a newcomer: 45 s standing and looking around, followed every second
        int stay = night ? 180 : 45;
        for (int s = 0; s < stay; s++) {
            int sec = s;
            int last = stay - 1;
            STEPS.add(mc -> {
                mc.player.setYRot(mc.player.getYRot() + 8.0F);
                follow(mc);
                if (sec == last) {
                    photos(mc, "arrive");
                }
                return 20;
            });
        }
        // walk crouched towards the nearest hunter for 8 s, as a player sneaking past would
        STEPS.add(mc -> {
            DinosaurEntity h = nearest(mc, true);
            if (h != null) {
                face(mc.player, h.position().add(0, h.getBbHeight() * 0.5D, 0));
                mc.options.keyShift.setDown(true);
                mc.options.keyUp.setDown(true);
                REPORT.add(String.format(Locale.ROOT, "  sneaking towards a %s %.0f blocks away", h.speciesId(), h.distanceTo(mc.player)));
            }
            return 1;
        });
        for (int s = 0; s < 8; s++) {
            STEPS.add(mc -> {
                follow(mc);
                return 20;
            });
        }
        STEPS.add(mc -> {
            mc.options.keyShift.setDown(false);
            mc.options.keyUp.setDown(false);
            photos(mc, "sneak");
            return 1;
        });
        // strike the nearest herbivore once, from where a player would (a spear's reach), and watch the herd for 15 s
        STEPS.add(mc -> {
            DinosaurEntity v = nearest(mc, false);
            if (v != null) {
                ServerPlayer sp = mc.getSingleplayerServer().getPlayerList().getPlayer(mc.player.getUUID());
                mc.getSingleplayerServer().execute(() -> {
                    DinosaurEntity sv = (DinosaurEntity) sp.serverLevel().getEntity(v.getId());
                    if (sv != null) {
                        sp.teleportTo(sv.getX() + 4.0D, sv.getY(), sv.getZ());
                        sv.hurt(sv.damageSources().playerAttack(sp), 6.0F);
                    }
                });
                REPORT.add("  struck a " + v.speciesId());
            }
            return 1;
        });
        for (int s = 0; s < 15; s++) {
            int sec = s;
            STEPS.add(mc -> {
                follow(mc);
                if (sec == 3) {
                    photos(mc, "struck");
                }
                return 20;
            });
        }
        STEPS.add(mc -> {
            summary(mc);
            return 1;
        });
    }

    // ------------------------------------------------------------------ following the animals
    private static void follow(Minecraft mc) {
        ServerPlayer p = mc.getSingleplayerServer().getPlayerList().getPlayer(mc.player.getUUID());
        if (p == null) {
            return;
        }
        mc.getSingleplayerServer().execute(() -> {
            ServerLevel lv = p.serverLevel();
            List<DinosaurEntity> near = lv.getEntitiesOfClass(DinosaurEntity.class, p.getBoundingBox().inflate(96.0D));
            for (DinosaurEntity d : near) {
                Track t = TRACK.computeIfAbsent(d.getId(), k -> {
                    Track n = new Track();
                    n.species = d.speciesId();
                    n.predator = d instanceof PredatorDinosaur;
                    return n;
                });
                Vec3 pos = d.position();
                boolean trying = d.getNavigation().isInProgress();
                if (t.last != null && trying && pos.distanceTo(t.last) < 0.3D && !d.isSleeping() && !d.isOrderedToSit()) {
                    t.tryingStill++;
                    t.worstStill = Math.max(t.worstStill, t.tryingStill);
                    if (t.tryingStill == 10) {
                        net.minecraft.world.level.pathfinder.Path path = d.getNavigation().getPath();
                        BlockPos ahead = BlockPos.containing(d.position().add(d.getLookAngle().multiply(d.getBbWidth() * 0.5D + 0.6D, 0, d.getBbWidth() * 0.5D + 0.6D)));
                        t.stuckWhy = String.format(Locale.ROOT, "goals [%s] going to %s, at %s on %s, ahead %s, in water %s, sleeping %s, width %.1f",
                                goals(d), path == null || path.getEndNode() == null ? "-" : path.getEndNode().asBlockPos().toShortString(),
                                d.blockPosition().toShortString(), lv.getBlockState(d.blockPosition().below()).getBlock().getName().getString(),
                                lv.getBlockState(ahead.above()).getBlock().getName().getString(), d.isInWater(), d.isSleeping(), d.getBbWidth());
                    }
                } else {
                    t.tryingStill = 0;
                }
                t.last = pos;
                if (d.isInWall()) {
                    t.inWall++;
                }
                if (d.isInWater() && !d.isUnderWater()) {
                    double vy = d.getDeltaMovement().y;
                    if (t.lastVy < -0.02D && vy > 0.06D) {
                        t.waterHops++;
                    }
                    t.lastVy = vy;
                }
                if (d.fleeLeft > 0) {
                    t.fled++;
                }
                if (d.getLastHurtMob() == p) {
                    t.struckPlayer = true;
                }
                if (d.getTarget() instanceof Player && t.huntedPlayerAt < 0) {
                    t.huntedPlayerAt = (int) d.distanceTo(p);
                }
                t.asleep = d.isSleeping();
                if (d.isSleeping() && d instanceof HerbivoreDinosaur) {
                    for (DinosaurEntity o : near) {
                        if (o instanceof PredatorDinosaur && !o.isTame()) {
                            t.sleepNearHunter = Math.min(t.sleepNearHunter, d.distanceTo(o));
                        }
                    }
                }
            }
        });
    }

    private static DinosaurEntity nearest(Minecraft mc, boolean predator) {
        DinosaurEntity best = null;
        double bd = 1e9;
        for (DinosaurEntity d : mc.level.getEntitiesOfClass(DinosaurEntity.class, mc.player.getBoundingBox().inflate(64.0D))) {
            if ((d instanceof PredatorDinosaur) != predator || d.isTame()) {
                continue;
            }
            double dd = d.distanceToSqr(mc.player);
            if (dd < bd) {
                bd = dd;
                best = d;
            }
        }
        return best;
    }

    private static void summary(Minecraft mc) {
        Map<String, Integer> seen = new TreeMap<>();
        int hunters = 0, all = 0, stuck = 0, walls = 0, hops = 0, fled = 0;
        double sleepMin = 999.0D;
        List<String> problems = new ArrayList<>();
        for (Track t : TRACK.values()) {
            all++;
            seen.merge(t.species, 1, Integer::sum);
            if (t.predator) {
                hunters++;
            }
            if (t.worstStill >= 10) {
                stuck++;
                problems.add(t.species + " stuck " + t.worstStill + " s trying to walk: " + t.stuckWhy);
            }
            if (t.inWall > 0) {
                walls++;
                problems.add(t.species + " inside a block " + t.inWall + " s");
            }
            if (t.waterHops >= 3) {
                hops++;
                problems.add(t.species + " hopped " + t.waterHops + " times in the water");
            }
            if (t.fled > 0) {
                fled++;
            }
            if (t.asleep) {
                sleepMin = Math.min(sleepMin, t.sleepNearHunter);
            }
            if (t.huntedPlayerAt >= 0) {
                REPORT.add("  took the player as target: " + t.species + " from " + t.huntedPlayerAt + " blocks"
                        + (t.struckPlayer ? ", and STRUCK" : ", never struck"));
            }
        }
        REPORT.add(String.format(Locale.ROOT, "  animals met: %d (%d hunters, %.0f%%) | species %s", all, hunters,
                all == 0 ? 0.0D : 100.0D * hunters / all, seen));
        REPORT.add(String.format(Locale.ROOT, "  stuck %d | inside a block %d | hopping in water %d | ran away %d | closest sleeper to a hunter %s",
                stuck, walls, hops, fled, sleepMin > 900 ? "-" : String.format(Locale.ROOT, "%.0f", sleepMin)));
        for (String s : problems) {
            REPORT.add("  PROBLEM " + s);
        }
    }

    // ------------------------------------------------------------------ the player's eye
    private static void photos(Minecraft mc, String what) {
        List<DinosaurEntity> near = new ArrayList<>(mc.level.getEntitiesOfClass(DinosaurEntity.class, mc.player.getBoundingBox().inflate(48.0D)));
        near.sort((a, b) -> Double.compare(a.distanceToSqr(mc.player), b.distanceToSqr(mc.player)));
        DinosaurEntity d = near.isEmpty() ? null : near.get(0);
        if (d != null) {
            face(mc.player, d.position().add(0, d.getBbHeight() * 0.5D, 0));
        }
        String name = String.format(Locale.ROOT, "playtest_%03d_%s_%s.png", ++photoNo, what,
                d == null ? "empty" : d.speciesId());
        // the frame is drawn after this tick: take it a moment later from the render thread
        mc.tell(() -> Screenshot.grab(mc.gameDirectory, name, mc.getMainRenderTarget(), m -> {
        }));
        REPORT.add("  photo " + name + (d == null ? "" : String.format(Locale.ROOT, " (%s, %.0f blocks)", d.speciesId(), d.distanceTo(mc.player))));
        shots++;
    }

    private static void face(Player p, Vec3 at) {
        Vec3 eye = p.getEyePosition();
        Vec3 d = at.subtract(eye);
        p.setYRot((float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90.0F);
        p.setXRot((float) -(Mth.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * Mth.RAD_TO_DEG));
    }

    private static void command(Minecraft mc, String c) {
        mc.player.connection.sendCommand(c);
    }

    private static void write(Minecraft mc) {
        try {
            Files.write(new File(mc.gameDirectory, "terrassic_playtest_report.txt").toPath(), REPORT, StandardCharsets.UTF_8);
        } catch (Exception e) {
            org.slf4j.LoggerFactory.getLogger("terrassic").error("playtest report", e);
        }
    }
}
