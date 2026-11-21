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
import net.minecraft.world.entity.Entity;
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
    /** every animal met on the whole tour, per species (UUIDs) */
    private static final Map<String, java.util.Set<java.util.UUID>> SEEN = new ConcurrentHashMap<>();
    /** 1.11.0: the four remade herbivores */
    private static final String[] NEW_HERBIVORES = {"maiasaura", "corythosaurus", "pachyrhinosaurus", "thescelosaurus"};
    private static int wait;
    private static boolean started;
    private static int titleTicks;
    private static int done;
    private static int notReady;
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
        int floatSec;           // seconds in a row off the ground, out of the water, not climbing or falling
        int worstFloat;
        String floatWhy = "";
        double lastVy;
        boolean asleep;
        double sleepNearHunter = 999.0D;
        int huntedPlayerAt = -1;  // distance when it first took the player as its target
        int fled;
        String stuckWhy = "";
        String sleepWho = "";
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
        } catch (Throwable e) {
            REPORT.add("  STEP FAILED: " + e);
            org.slf4j.LoggerFactory.getLogger("terrassic").error("[playtest] step failed", e);
            w = 1;
        }
        if (w < 0) {
            // not ready yet: run it again next tick (logged every 10 s so a step that never gets ready shows in the log)
            if (++notReady % 200 == 0) {
                org.slf4j.LoggerFactory.getLogger("terrassic").info("[playtest] waiting on step {} ({} left)", done, STEPS.size());
            }
            return;
        }
        notReady = 0;
        STEPS.poll();
        done++;
        if (done % 20 == 0) {
            org.slf4j.LoggerFactory.getLogger("terrassic").info("[playtest] step {} done, {} left", done, STEPS.size());
        }
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
        // TERRASSIC_PLAYTEST_ONLY=portraits: only the four habitats and their portraits (a few minutes)
        boolean portraitsOnly = "portraits".equals(System.getenv("TERRASSIC_PLAYTEST_ONLY"));
        for (int i = 0; i < places.length && !portraitsOnly; i++) {
            boolean night = i == 4 || i == 8;
            visit(i, places[i][0], places[i][1], night);
        }
        newHerbivores(portraitsOnly);
        STEPS.add(mc -> {
            int total = 0;
            StringBuilder b = new StringBuilder();
            for (String sp : NEW_HERBIVORES) {
                int n = SEEN.getOrDefault(sp, java.util.Set.of()).size();
                total += n;
                b.append(' ').append(sp).append('=').append(n);
            }
            REPORT.add("");
            REPORT.add("== New herbivores met on the whole tour:" + b + " (total " + total + ")");
            write(mc);
            mc.stop();
            return 1;
        });
    }

    private static void visit(int i, int x, int z, boolean night) {
        visit(i, new int[]{x, z}, night, 0);
    }

    /** {@code xz} may be filled in by an earlier step (a structure or a biome found in the world). */
    private static void visit(int i, int[] xz, boolean night, int stayFor) {
        STEPS.add(mc -> {
            TRACK.clear();
            shots = 0;
            command(mc, "time set " + (night ? 18000 : 1000 + i * 700));
            command(mc, String.format(Locale.ROOT, "tp @s %d 200 %d", xz[0], xz[1]));
            return 60;
        });
        // stand on the ground there once it has loaded
        STEPS.add(mc -> {
            int x = xz[0], z = xz[1];
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
        int stay = stayFor > 0 ? stayFor : night ? 180 : 45;
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

    // ------------------------------------------------------------------ 1.11.0: where the new herbivores live
    /** The Nest Colony (the Maiasaura's nests) and a biome of each new herbivore's habitat, found in this world. */
    private static void newHerbivores(boolean portraitsOnly) {
        int[] colony = {0, 0};
        if (!portraitsOnly) {
        STEPS.add(mc -> {
            ServerLevel lv = mc.getSingleplayerServer().overworld();
            var reg = lv.registryAccess().registryOrThrow(Registries.STRUCTURE);
            var key = ResourceKey.create(Registries.STRUCTURE, new ResourceLocation("terrassic", "nest_colony"));
            var holder = reg.getHolder(key);
            var found = holder.isEmpty() ? null : lv.getChunkSource().getGenerator().findNearestMapStructure(lv,
                    net.minecraft.core.HolderSet.direct(holder.get()), BlockPos.ZERO, 100, false);
            if (found != null) {
                colony[0] = found.getFirst().getX();
                colony[1] = found.getFirst().getZ();
            }
            REPORT.add("");
            REPORT.add("== Nest Colony: " + (found == null ? "NOT FOUND" : colony[0] + " " + colony[1]));
            return 1;
        });
        visit(10, colony, false, 60);
        STEPS.add(mc -> {
            ServerLevel lv = mc.getSingleplayerServer().overworld();
            BlockPos c = new BlockPos(colony[0], lv.getHeight(Heightmap.Types.WORLD_SURFACE, colony[0], colony[1]), colony[1]);
            int eggs = 0, covered = 0;
            for (BlockPos q : BlockPos.betweenClosed(c.offset(-40, -12, -40), c.offset(40, 12, 40))) {
                var st = lv.getBlockState(q);
                if (st.getBlock() instanceof com.terrassic.block.DinoEggBlock
                        && net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(st.getBlock()).getPath().startsWith("maiasaura")) {
                    eggs++;
                    if (st.hasProperty(com.terrassic.block.DinoEggBlock.COVERED) && st.getValue(com.terrassic.block.DinoEggBlock.COVERED)) {
                        covered++;
                    }
                }
            }
            long maia = lv.getEntitiesOfClass(com.terrassic.entity.Maiasaurine.class, new net.minecraft.world.phys.AABB(c).inflate(48.0D)).size();
            REPORT.add(String.format(Locale.ROOT, "  colony: %d maiasaura eggs in the nests (%d covered), %d maiasaura within 48 blocks", eggs, covered, maia));
            return 1;
        });
        }
        // a habitat of each: the Maiasaura's plains, the Corythosaurus' swamp, the Pachyrhinosaurus' taiga, the
        // Thescelosaurus' river bank (its burrow)
        String[][] habitats = {{"plains", "maiasaura"}, {"swamp", "corythosaurus"}, {"taiga", "pachyrhinosaurus"}, {"river", "thescelosaurus"}};
        String onlySp = System.getenv("TERRASSIC_PLAYTEST_SPECIES");    // portraits of these only (comma list)
        for (int h = 0; h < habitats.length; h++) {
            String[] hab = habitats[h];
            if (portraitsOnly && onlySp != null && !onlySp.contains(hab[1])) {
                continue;
            }
            int[] at = {0, 0};
            int[] from = {h % 2 == 0 ? 600 : -600, h < 2 ? 600 : -600};
            STEPS.add(mc -> {
                ServerLevel lv = mc.getSingleplayerServer().overworld();
                var tag = net.minecraft.tags.TagKey.create(Registries.BIOME, new ResourceLocation("terrassic", "habitat/" + hab[0]));
                var found = lv.findClosestBiome3d(b -> b.is(tag), new BlockPos(from[0], 70, from[1]), 1600, 32, 64);
                if (found != null) {
                    at[0] = found.getFirst().getX();
                    at[1] = found.getFirst().getZ();
                }
                REPORT.add("");
                REPORT.add("== Habitat " + hab[0] + " (" + hab[1] + "): " + (found == null ? "NOT FOUND" : at[0] + " " + at[1]));
                return 1;
            });
            visit(11 + h, at, false, portraitsOnly ? 5 : 90);
            STEPS.add(mc -> {
                StringBuilder b = new StringBuilder();
                for (String sp : NEW_HERBIVORES) {
                    long n = TRACK.values().stream().filter(t -> t.species.equals(sp)).count();
                    b.append(' ').append(sp).append('=').append(n);
                }
                REPORT.add("  new herbivores here:" + b);
                return 1;
            });
            portrait(hab[1]);
            if (h == 0 && !portraitsOnly) {
                approach();
            }
        }
    }

    /** Two photos of a grown male of {@code species} where the tour stands (its own habitat): three quarters from the
     *  front and from the side, at noon (screenshots/bateria_<species>_34.png and _lado.png). */
    private static void portrait(String species) {
        java.util.UUID id = java.util.UUID.nameUUIDFromBytes(("bateria-" + species).getBytes(StandardCharsets.UTF_8));
        DinosaurEntity[] dino = new DinosaurEntity[1];
        int[] spotAt = new int[3];
        STEPS.add(mc -> {
            command(mc, "time set 6000");
            command(mc, "gamemode spectator");
            ServerLevel lv = mc.getSingleplayerServer().overworld();
            // on the server thread: the heightmap of chunks not loaded yet, read from the client thread, left the
            // client without those chunks (only the sky in the photo, and the player fell out of the world)
            int px = mc.player.getBlockX(), pz = mc.player.getBlockZ();
            int[] spot = mc.getSingleplayerServer().submit(() -> openGround(lv, px, pz)).join();
            int x = spot[0], y = spot[1], z = spot[2];
            REPORT.add(String.format(Locale.ROOT, "  portrait spot for %s: %d %d %d (%s)", species, x, y, z,
                    lv.getBiome(new BlockPos(x, y, z)).unwrapKey().map(k -> k.location().getPath()).orElse("?")));
            spotAt[0] = x;
            spotAt[1] = y;
            spotAt[2] = z;
            // the camera near first: a spot up to 64 blocks off was past where the client tracks the animal
            command(mc, String.format(Locale.ROOT, "tp @s %d %d %d", x, y + 8, z + 10));
            return 200;     // the chunks round it drawn (after 30 ticks the photo had only the sky)
        });
        STEPS.add(mc -> {
            int x = spotAt[0], y = spotAt[1], z = spotAt[2];
            // the others out of the picture (a portrait, not the tour)
            // (out of the world, not killed: a kill leaves a carcass in the picture)
            command(mc, String.format(Locale.ROOT, "tp @e[type=!player,x=%d,y=%d,z=%d,distance=..40] ~ -200 ~", x, y, z));
            command(mc, String.format(Locale.ROOT, "summon terrassic:%s %d.5 %d %d.5 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Female:0b,"
                    + "Rotation:[%.0ff,0f],UUID:[I;%d,%d,%d,%d]}", species, x, y, z, 30.0F,
                    (int) (id.getMostSignificantBits() >> 32), (int) id.getMostSignificantBits(),
                    (int) (id.getLeastSignificantBits() >> 32), (int) id.getLeastSignificantBits()));
            return 40;
        });
        int[] tries = {0};
        for (String view : new String[]{"34", "lado"}) {
            STEPS.add(mc -> {
                dino[0] = null;
                for (Entity e : mc.level.entitiesForRendering()) {
                    if (e instanceof DinosaurEntity d && id.equals(d.getUUID())) {
                        dino[0] = d;
                    }
                }
                if (dino[0] == null && tries[0]++ < 200) {
                    return -1;      // not on the client yet: again next tick (up to 10 s)
                }
                if (dino[0] == null) {
                    REPORT.add("  portrait " + species + " " + view + ": NOT FOUND");
                    return 1;
                }
                net.minecraft.world.phys.AABB all = dino[0].getBoundingBox().minmax(dino[0].partsBounds());
                Vec3 c = all.getCenter();
                double size = Math.max(all.getXsize(), Math.max(all.getYsize(), all.getZsize()));
                float bodyYaw = dino[0].yBodyRot * Mth.DEG_TO_RAD;
                Vec3 side = new Vec3(-Mth.cos(bodyYaw), 0, -Mth.sin(bodyYaw));
                Vec3 forward = new Vec3(-Mth.sin(bodyYaw), 0, Mth.cos(bodyYaw));
                double dist = size * 0.75D + 2.0D;
                // from either side (the one with a clear view of it), the eye out of the ground and the leaves
                ServerLevel lv = mc.getSingleplayerServer().overworld();
                ServerPlayer viewer = mc.getSingleplayerServer().getPlayerList().getPlayer(mc.player.getUUID());
                Vec3 eye = mc.getSingleplayerServer().submit(() -> {
                    Vec3 first = null;
                    for (float s2 : new float[]{1.0F, -1.0F}) {
                        for (double lift = 0.0D; lift <= 4.0D; lift += 2.0D) {
                            Vec3 e0 = "34".equals(view)
                                    ? c.add(side.scale(s2 * dist * 0.8D)).add(forward.scale(dist * 0.7D)).add(0, size * 0.25D + lift, 0)
                                    : c.add(side.scale(s2 * dist * 1.1D)).add(0, size * 0.1D + lift, 0);
                            for (int up = 0; up < 10; up++) {
                                BlockPos b = BlockPos.containing(e0);
                                if (lv.getBlockState(b).isAir() && lv.getBlockState(b.above()).isAir()) {
                                    break;
                                }
                                e0 = e0.add(0, 1.0D, 0);
                            }
                            if (first == null) {
                                first = e0;
                            }
                            var hit = lv.clip(new net.minecraft.world.level.ClipContext(e0, c,
                                    net.minecraft.world.level.ClipContext.Block.VISUAL, net.minecraft.world.level.ClipContext.Fluid.NONE, viewer));
                            if (hit.getType() == net.minecraft.world.phys.HitResult.Type.MISS) {
                                return e0;
                            }
                        }
                    }
                    return first;
                }).join();
                Vec3 d = c.subtract(eye);
                float yaw = (float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90.0F;
                float pitch = (float) -(Mth.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * Mth.RAD_TO_DEG);
                ServerPlayer sp = mc.getSingleplayerServer().getPlayerList().getPlayer(mc.player.getUUID());
                double eyeH = mc.player.getEyeHeight();
                mc.getSingleplayerServer().execute(() -> sp.teleportTo(sp.serverLevel(), eye.x, eye.y - eyeH, eye.z, yaw, pitch));
                return 60;
            });
            STEPS.add(mc -> {
                if (dino[0] != null) {
                    String name = "bateria_" + species + "_" + view + ".png";
                    Screenshot.grab(mc.gameDirectory, name, mc.getMainRenderTarget(), m -> {
                    });
                    REPORT.add("  portrait " + name);
                }
                return 10;
            });
        }
        STEPS.add(mc -> {
            command(mc, "kill " + id);
            command(mc, "gamemode survival");
            return 10;
        });
    }

    /** A level, open patch near (x0, z0) for a portrait: no leaves over it, dry, the ground within 2 blocks over 17 x 17 (room for the camera)
     *  (searched in rings up to 64 blocks out); {x, y, z}, or the place itself if none. */
    private static int[] openGround(ServerLevel lv, int x0, int z0) {
        for (int r = 6; r <= 64; r += 6) {
            for (int a = 0; a < 16; a++) {
                int x = x0 + (int) Math.round(Math.cos(a * Math.PI / 8.0D) * r), z = z0 + (int) Math.round(Math.sin(a * Math.PI / 8.0D) * r);
                int lo = Integer.MAX_VALUE, hi = Integer.MIN_VALUE;
                boolean ok = true;
                for (int dx = -8; dx <= 8 && ok; dx += 2) {
                    for (int dz = -8; dz <= 8 && ok; dz += 2) {
                        int h = lv.getHeight(Heightmap.Types.MOTION_BLOCKING, x + dx, z + dz);
                        int hn = lv.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x + dx, z + dz);
                        BlockPos g = new BlockPos(x + dx, hn - 1, z + dz);
                        ok = h == hn && lv.getFluidState(g).isEmpty() && lv.getFluidState(g.above()).isEmpty();
                        lo = Math.min(lo, hn);
                        hi = Math.max(hi, hn);
                    }
                }
                if (ok && hi - lo <= 2) {
                    return new int[]{x, lv.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z};
                }
            }
        }
        return new int[]{x0, lv.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x0, z0), z0};
    }

    /** The LOD (client/DinoLod) as the player walks up: the camera glides from 76 to 10 blocks of a grown animal in
     *  16 s while client/dev/LodProbe records how much its bones moved each frame. */
    private static void approach() {
        int[] who = {-1};
        double[][] path = new double[2][3];
        int[] tick = {0};
        String[] sp = {""};
        STEPS.add(mc -> {
            DinosaurEntity d = null;
            double bd = 1e9;
            for (DinosaurEntity e : mc.level.getEntitiesOfClass(DinosaurEntity.class, mc.player.getBoundingBox().inflate(64.0D))) {
                if (!e.isBaby() && e.isAlive() && !(e instanceof com.terrassic.entity.FlyingDinosaur) && e.distanceToSqr(mc.player) < bd) {
                    bd = e.distanceToSqr(mc.player);
                    d = e;
                }
            }
            REPORT.add("");
            if (d == null) {
                REPORT.add("== LOD approach: no animal near");
                return 1;
            }
            who[0] = d.getId();
            sp[0] = d.speciesId();
            DinosaurEntity sd = (DinosaurEntity) mc.getSingleplayerServer().overworld().getEntity(d.getUUID());
            if (sd != null) {
                mc.getSingleplayerServer().execute(() -> sd.setNoAi(true));   // still: only its idle moves
            }
            Vec3 c = d.position().add(0, d.getBbHeight() * 0.5D, 0);
            Vec3 dir = mc.player.position().subtract(d.position()).multiply(1, 0, 1);
            dir = dir.lengthSqr() < 1.0E-3D ? new Vec3(1, 0, 0) : dir.normalize();
            Vec3 a = c.add(dir.scale(76.0D)).add(0, 8.0D, 0), b = c.add(dir.scale(10.0D)).add(0, 3.0D, 0);
            path[0] = new double[]{a.x, a.y, a.z};
            path[1] = new double[]{b.x, b.y, b.z};
            command(mc, "gamemode spectator");
            REPORT.add("== LOD approach: a " + sp[0] + ", from 76 to 10 blocks in 16 s");
            return 20;
        });
        STEPS.add(mc -> {
            if (who[0] < 0) {
                return 1;
            }
            int k = tick[0]++;
            double f = Math.min(1.0D, k / 320.0D);
            double x = path[0][0] + (path[1][0] - path[0][0]) * f, y = path[0][1] + (path[1][1] - path[0][1]) * f,
                    z = path[0][2] + (path[1][2] - path[0][2]) * f;
            mc.player.setPos(x, y, z);
            Entity d = mc.level.getEntity(who[0]);
            if (d != null) {
                face(mc.player, d.position().add(0, d.getBbHeight() * 0.5D, 0));
            }
            if (k == 20) {
                LodProbe.start(who[0]);
            }
            if (k < 330) {
                return -1;
            }
            LodProbe.stop();
            lodVerdict();
            return 1;
        });
        STEPS.add(mc -> {
            if (who[0] >= 0) {
                Entity d = mc.level.getEntity(who[0]);
                DinosaurEntity sd = d == null ? null : (DinosaurEntity) mc.getSingleplayerServer().overworld().getEntity(d.getUUID());
                if (sd != null) {
                    mc.getSingleplayerServer().execute(() -> sd.setNoAi(false));
                }
                command(mc, "gamemode survival");
            }
            return 20;
        });
    }

    /** The largest change of one frame where the camera crosses each LOD distance, against the frames of the same
     *  band away from the crossings (95th percentile and largest). */
    private static void lodVerdict() {
        List<double[]> f = new ArrayList<>(LodProbe.FRAMES);
        int near = com.terrassic.client.DinoLod.near();
        double[] edges = {near, near + com.terrassic.client.DinoLod.LIVELY_FADE, near * 2.0D};
        REPORT.add(String.format(Locale.ROOT, "  lod frames: %d (from %.0f to %.0f blocks)", f.size(),
                f.isEmpty() ? 0.0D : f.get(0)[0], f.isEmpty() ? 0.0D : f.get(f.size() - 1)[0]));
        for (double e : edges) {
            List<Double> at = new ArrayList<>(), round = new ArrayList<>();
            for (double[] fr : f) {
                double off = Math.abs(fr[0] - e);
                if (off <= 1.0D) {
                    at.add(fr[1]);
                } else if (off <= 8.0D) {
                    round.add(fr[1]);
                }
            }
            round.sort(Double::compare);
            double p95 = round.isEmpty() ? 0.0D : round.get((int) Math.min(round.size() - 1, Math.round(round.size() * 0.95D)));
            double maxRound = round.isEmpty() ? 0.0D : round.get(round.size() - 1);
            double maxAt = at.stream().mapToDouble(Double::doubleValue).max().orElse(0.0D);
            REPORT.add(String.format(Locale.ROOT, "  lod crossing %.0f blocks: largest frame change %.4f (%d frames); round it p95 %.4f, largest %.4f (%d frames)",
                    e, maxAt, at.size(), p95, maxRound, round.size()));
        }
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
                // floating (1.11, the physics of an animal standing still is skipped): off the ground, not in water, not
                // a flyer, not moving up or down, with air under it, for seconds in a row
                boolean flyer = d instanceof com.terrassic.entity.FlyingDinosaur || d instanceof com.terrassic.entity.SwimmingDinosaur;
                if (!flyer && t.last != null && !d.onGround() && !d.isInWater() && !d.isPassenger() && !d.isNoGravity()
                        && Math.abs(pos.y - t.last.y) < 0.02D && lv.getBlockState(d.blockPosition().below()).isAir()
                        && lv.getBlockState(d.blockPosition()).getCollisionShape(lv, d.blockPosition()).isEmpty()) {
                    t.floatSec++;
                    if (t.floatSec > t.worstFloat) {
                        t.worstFloat = t.floatSec;
                        t.floatWhy = String.format(Locale.ROOT, "at %s, %.2f over the block below, sleeping %s, still %s",
                                d.blockPosition().toShortString(), pos.y - Math.floor(pos.y), d.isSleeping(),
                                d.getDeltaMovement().horizontalDistanceSqr() < 1.0E-4D);
                    }
                } else {
                    t.floatSec = 0;
                }
                t.last = pos;
                SEEN.computeIfAbsent(d.speciesId(), k -> ConcurrentHashMap.newKeySet()).add(d.getUUID());
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
                        if (o instanceof PredatorDinosaur && !o.isTame() && d.distanceTo(o) < t.sleepNearHunter) {
                            t.sleepNearHunter = d.distanceTo(o);
                            // who, and was the hunter itself asleep, sated, after something (08/11: one at 12 blocks)
                            t.sleepWho = String.format(Locale.ROOT, "%s asleep %.0f from a %s (%s%s%s)", d.speciesId(), d.distanceTo(o),
                                    o.speciesId(), o.isSleeping() ? "asleep" : "awake", o.isSated() ? ", sated" : "",
                                    o.getTarget() != null ? ", hunting " + o.getTarget().getType().toShortString() : "");
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
        int hunters = 0, all = 0, stuck = 0, walls = 0, hops = 0, fled = 0, floating = 0;
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
            if (t.worstFloat >= 3) {
                floating++;
                problems.add(t.species + " floating " + t.worstFloat + " s: " + t.floatWhy);
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
                // the rule (HerbivoreDinosaur.wokenByThreat): a hunter on the move wakes it from 28, an idle one from 18;
                // a check every half second leaves a few blocks of margin
                if (t.sleepNearHunter < (t.sleepWho.contains("hunting") ? 24.0D : 16.0D)) {
                    problems.add("asleep near a hunter: " + t.sleepWho);
                }
                sleepMin = Math.min(sleepMin, t.sleepNearHunter);
            }
            if (t.huntedPlayerAt >= 0) {
                REPORT.add("  took the player as target: " + t.species + " from " + t.huntedPlayerAt + " blocks"
                        + (t.struckPlayer ? ", and STRUCK" : ", never struck"));
            }
        }
        REPORT.add(String.format(Locale.ROOT, "  animals met: %d (%d hunters, %.0f%%) | species %s", all, hunters,
                all == 0 ? 0.0D : 100.0D * hunters / all, seen));
        REPORT.add(String.format(Locale.ROOT, "  stuck %d | inside a block %d | hopping in water %d | ran away %d | closest sleeper to a hunter %s | floating %d",
                stuck, walls, hops, fled, sleepMin > 900 ? "-" : String.format(Locale.ROOT, "%.0f", sleepMin), floating));
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
