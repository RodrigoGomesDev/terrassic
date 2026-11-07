package com.terrassic.client.dev;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.registry.ModItems;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;

/**
 * Development only (TERRASSIC_BEHAVIOR_TEST=1, with --quickPlaySingleplayer on a superflat world): the remade species of
 * the 1.8 (Styracosaurus, Deinosuchus, Elasmosaurus) are left to live in small arenas built for them and watched:
 * every one-shot animation they trigger by themselves (DinosaurEntity#triggerLog), every movement animation the client
 * draws, the first time each happens photographed; then taming by hand, the saddle, a ride (third person), breeding,
 * the egg and the hatching (or the live birth). Writes terrassic_behavior_report.txt in the game directory and closes
 * the game. Nothing is forced: the arenas only put the animals where their behaviours can happen.
 */
public final class BehaviorTest {
    private static final double Y = -60.0D;
    private static final Deque<Step> STEPS = new ArrayDeque<>();
    private static final List<String> REPORT = new ArrayList<>();
    /** species -> animation -> times triggered by the creatures themselves (server) */
    private static final Map<String, Map<String, Integer>> TRIGGERS = new ConcurrentHashMap<>();
    /** species -> movement animations seen drawn on the client */
    private static final Map<String, Set<String>> MOVES = new ConcurrentHashMap<>();
    private static final ConcurrentLinkedQueue<Object[]> NEW = new ConcurrentLinkedQueue<>();
    private static final Set<String> SHOT = ConcurrentHashMap.newKeySet();
    private static int wait;
    private static int shotCooldown;
    private static long serial;
    private static final long RUN = System.nanoTime() & 0xFFFFFFFL;

    private interface Step {
        int run(Minecraft mc);
    }

    private BehaviorTest() {
    }

    public static void init() {
        if (!"1".equals(System.getenv("TERRASSIC_BEHAVIOR_TEST"))) {
            return;
        }
        ClientTickEvent.CLIENT_POST.register(BehaviorTest::tick);
        DinosaurEntity.triggerLog = (dino, anim) -> {
            String sp = dino.speciesId();
            TRIGGERS.computeIfAbsent(sp, k -> new ConcurrentHashMap<>()).merge(anim, 1, Integer::sum);
            if (SHOT.add(sp + "_" + anim)) {
                NEW.add(new Object[]{dino.getId(), sp + "_" + anim});
            }
        };
        String only = System.getenv().getOrDefault("TERRASSIC_BEHAVIOR_SPECIES", "styracosaurus,deinosuchus,elasmosaurus");
        STEPS.add(mc -> mc.level == null || mc.player == null ? -1 : 100);
        STEPS.add(mc -> {
            for (String c : new String[]{"gamemode creative @a", "gamerule doDaylightCycle false", "gamerule doWeatherCycle false",
                    "time set 6000", "weather clear", "gamerule doMobSpawning false", "difficulty normal", "kill @e[type=!player]"}) {
                command(mc, c);
            }
            mc.options.hideGui = true;
            mc.player.getAbilities().flying = true;
            REPORT.add("Terrassic 1.8: the remade species living in arenas, watched in the real client");
            return 20;
        });
        if (only.contains("styracosaurus")) {
            planStyracosaurus();
        }
        if (only.contains("deinosuchus")) {
            planDeinosuchus();
        }
        if (only.contains("elasmosaurus")) {
            planElasmosaurus();
        }
        if (only.contains("therizinosaurus")) {
            planTherizinosaurus();
        }
        if (only.contains("zones")) {
            planZones();
        }
        if (only.contains("weak")) {
            double x0 = 3800.5D;
            UUID rex = id(), calf = id();
            STEPS.add(mc -> {
                REPORT.add("");
                REPORT.add("== The weak first (1.9.5)");
                clear(mc, x0, 30);
                command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..80]");
                command(mc, "time set 1000");
                summon(mc, "tyrannosaurus", x0, Y, 0.5D, rex, "Hunger:30,Rotation:[0f,0f]");
                for (int i = 0; i < 3; i++) {
                    summon(mc, "edmontosaurus", x0 - 8 + i * 8, Y, 18.5D, id(), "NoAI:1b");
                }
                summon(mc, "edmontosaurus", x0 + 4, Y, 18.5D, calf, "NoAI:1b,Age:-24000");
                return 200;
            });
            STEPS.add(mc -> {
                DinosaurEntity r = server(mc, rex);
                net.minecraft.world.entity.LivingEntity t = r == null ? null : r.getTarget();
                REPORT.add("  hungry T. rex facing 3 adult Edmontosaurus and a calf: its target is "
                        + (t == null ? "none" : t.getUUID().equals(calf) ? "THE CALF" : t.getType().toShortString() + (t.isBaby() ? " (baby)" : " (adult)")));
                return 1;
            });
            UUID rex2 = id();
            STEPS.add(mc -> {
                clear(mc, x0, 40);
                command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..90]");
                summon(mc, "tyrannosaurus", x0, Y, 0.5D, rex2, "Hunger:30,Rotation:[0f,0f]");
                summon(mc, "argentinosaurus", x0, Y, 16.5D, id(), "NoAI:1b");
                summon(mc, "edmontosaurus", x0, Y, -26.5D, id(), "NoAI:1b");
                return 300;
            });
            STEPS.add(mc -> {
                DinosaurEntity r = server(mc, rex2);
                net.minecraft.world.entity.LivingEntity t = r == null ? null : r.getTarget();
                REPORT.add("  hungry T. rex, a grown Argentinosaurus near and an Edmontosaurus far: its target is "
                        + (t == null ? "none" : t.getType().toShortString()));
                return 1;
            });
        }
        if (only.contains("night")) {
            planNight();
        }
        if (only.contains("sleepfish")) {
            planSleepFish();
        }
        if (only.contains("headshot")) {
            planHeadshot(System.getenv().getOrDefault("TERRASSIC_GAIT_ONLY", "deinosuchus"));
        }
        if (only.contains("water")) {
            planWater();
        }
        if (only.contains("jaws")) {
            planJaws();
        }
        if (only.contains("gaits")) {
            planGaits();
        }
        if (only.contains("carcass")) {
            planCarcass();
        }
        if (only.contains("duels")) {
            planAllDuels();
        }
        if (only.contains("moves")) {
            planAllMoves();
        }
        if (only.contains("eco")) {
            planEcosystem();
        }
        if (only.contains("rexduel")) {
            planRexDuel();
        }
        if (only.contains("rexmotion")) {
            planRexMotion();
        }
        if (only.contains("quetzalcoatlus")) {
            planQuetzalcoatlus();
        }
        if (only.contains("edmontosaurus")) {
            planEdmontosaurus();
        }
        if (only.contains("dakotaraptor")) {
            planDakotaraptor();
        }
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== One-shot animations each species triggered by itself (times)");
            for (Map.Entry<String, Map<String, Integer>> e : new TreeMap<>(TRIGGERS).entrySet()) {
                REPORT.add("  " + e.getKey() + ": " + new TreeMap<>(e.getValue()));
            }
            REPORT.add("== Movement animations drawn on the client");
            for (Map.Entry<String, Set<String>> e : new TreeMap<>(MOVES).entrySet()) {
                REPORT.add("  " + e.getKey() + ": " + new TreeSet<>(e.getValue()));
            }
            try {
                Files.write(mc.gameDirectory.toPath().resolve("terrassic_behavior_report.txt"), REPORT, StandardCharsets.UTF_8);
            } catch (IOException ex) {
                throw new RuntimeException(ex);
            }
            return 10;
        });
        STEPS.add(mc -> {
            mc.stop();
            return 1000;
        });
    }

    // ------------------------------------------------------------------ the arenas

    private static void planStyracosaurus() {
        String sp = "styracosaurus";
        double x0 = 0.5D;
        UUID m1 = id(), m2 = id(), f1 = id(), b1 = id(), b2 = id(), raptor = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Styracosaurus: a herd (two males, a female, two calves) on open grass");
            clear(mc, x0, 24);
            summon(mc, sp, x0, Y, 0.5D, m1, "Female:0b");
            summon(mc, sp, x0 + 4, Y, 2.5D, m2, "Female:0b");
            summon(mc, sp, x0 - 3, Y, -3.5D, f1, "Female:1b");
            summon(mc, sp, x0 + 2, Y, -5.5D, b1, "Age:-24000");
            summon(mc, sp, x0 - 2, Y, -6.5D, b2, "Age:-24000");
            watch(mc, new Vec3(x0, Y, 0.0D), 22.0D);
            return 600;
        });
        STEPS.add(mc -> {
            REPORT.add("  a wild Velociraptor (held still) 11 blocks away");
            summon(mc, "velociraptor", x0 + 11, Y, 0.5D, raptor, "NoAI:1b");
            return 160;
        });
        STEPS.add(mc -> {
            command(mc, "tp " + raptor + " 0 -400 0");
            return 2400;
        });
        UUID zombie = id();
        STEPS.add(mc -> {
            REPORT.add("  provoked: a zombie 14 blocks away hits the first male");
            command(mc, String.format(Locale.ROOT, "summon minecraft:husk %.1f %.1f 0.5 {UUID:%s,PersistenceRequired:1b}", x0 - 14, Y, uuidNbt(zombie)));
            return 10;
        });
        STEPS.add(mc -> {
            command(mc, "damage " + m1 + " 2 minecraft:mob_attack by " + zombie);
            return 10;
        });
        for (int i = 0; i < 4; i++) {
            STEPS.add(mc -> {
                DinosaurEntity d = server(mc, m1);
                if (d != null) {
                    REPORT.add(String.format(Locale.ROOT, "    first male: target %s, hurt by %s, aggressive %s, %.1f blocks from the zombie",
                            d.getTarget() == null ? "none" : d.getTarget().getType().toShortString(),
                            d.getLastHurtByMob() == null ? "none" : d.getLastHurtByMob().getType().toShortString(), d.isAggressive(),
                            serverAny(mc, zombie) == null ? -1.0D : d.distanceTo(serverAny(mc, zombie))));
                }
                return 40;
            });
        }
        STEPS.add(mc -> 340);
        STEPS.add(mc -> {
            command(mc, "kill " + zombie);
            return 20;
        });
        planTameRideBreed(sp, f1, m2, new ItemStack(Items.FERN, 64), ModItems.STYRACOSAURUS_SADDLE.get(), x0, false);
    }

    private static void planTherizinosaurus() {
        String sp = "therizinosaurus";
        double x0 = 600.5D;
        UUID m1 = id(), m2 = id(), f1 = id(), b1 = id(), raptor = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Therizinosaurus: two males, a female and a calf in a wood of oaks");
            clear(mc, x0, 26);
            command(mc, "gamerule mobGriefing true");
            for (int[] t : new int[][]{{-8, -6}, {7, -9}, {-4, 9}, {10, 6}, {0, -14}}) {
                command(mc, fill(x0 + t[0], Y, t[1], x0 + t[0], Y + 4, t[1], "minecraft:oak_log"));
                command(mc, fill(x0 + t[0] - 2, Y + 4, t[1] - 2, x0 + t[0] + 2, Y + 6, t[1] + 2, "minecraft:oak_leaves[persistent=true]"));
            }
            summon(mc, sp, x0, Y, 0.5D, m1, "Female:0b");
            summon(mc, sp, x0 + 4, Y, 2.5D, m2, "Female:0b");
            summon(mc, sp, x0 - 3, Y, -3.5D, f1, "Female:1b");
            summon(mc, sp, x0 + 2, Y, -5.5D, b1, "Age:-24000");
            watch(mc, new Vec3(x0, Y + 2, 0.0D), 24.0D);
            return 3000;
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, m1);
            double rx = d == null ? x0 + 11 : d.getX() + 10, rz = d == null ? 0.5D : d.getZ();
            REPORT.add("  a wild Velociraptor (held still) 10 blocks from the first male");
            summon(mc, "velociraptor", rx, Y, rz, raptor, "NoAI:1b");
            return 400;
        });
        STEPS.add(mc -> {
            command(mc, "tp " + raptor + " 0 -400 0");
            REPORT.add("  a player in survival walks up to the first male");
            command(mc, "gamemode survival @a");
            DinosaurEntity d = server(mc, m1);
            ServerPlayer p = player(mc);
            if (d != null && p != null) {
                mc.getSingleplayerServer().execute(() -> p.teleportTo(d.getX() + 6.0D, d.getY() + 0.5D, d.getZ()));
            }
            return 120;
        });
        STEPS.add(mc -> {
            command(mc, "gamemode creative @a");
            mc.player.getAbilities().flying = true;
            watch(mc, new Vec3(x0, Y + 2, 0.0D), 24.0D);
            return 2400;
        });
        planTameRideBreed(sp, f1, m2, null, ModItems.THERIZINOSAURUS_SADDLE.get(), x0, false);
    }

    /** The entity the burst camera follows (client UUID lookup), or null. */
    private static UUID followed;
    /** The duel's second fighter (the camera frames both), and the side it films from (kept steady). */
    private static UUID pairedWith;
    private static Vec3 camSide;

    /** Burst of frames for a GIF: one every 2 ticks for {@code frames} frames, named rexmotion_<tag>_NNN.png. */
    private static void burst(String tag, int frames, java.util.function.IntConsumer each) {
        for (int i = 0; i < frames; i++) {
            int k = i;
            STEPS.add(mc -> {
                each.accept(k);
                if (followed != null && pairedWith != null && mc.level != null) {
                    // a duel: the camera from the side of the line between the two, far enough to frame both
                    Entity e = server(mc, followed), f = server(mc, pairedWith);
                    if (e != null && f != null) {
                        Vec3 mid = e.position().add(f.position()).scale(0.5D);
                        Vec3 line = f.position().subtract(e.position());
                        Vec3 side = new Vec3(-line.z, 0.0D, line.x).normalize();
                        if (camSide == null || camSide.dot(side) < 0.0D) {
                            side = side.scale(-1.0D);
                        }
                        camSide = camSide == null ? side : camSide.scale(0.85D).add(side.scale(0.15D)).normalize();
                        double back = 6.0D + Math.max(e.getBbWidth(), f.getBbWidth()) * 2.2D + line.length() * 0.6D;
                        Vec3 at = mid.add(0.0D, Math.max(e.getBbHeight(), f.getBbHeight()) * 0.45D, 0.0D);
                        look(mc.player, at.add(camSide.scale(back)).add(0.0D, back * 0.3D, 0.0D), at);
                    }
                } else if (followed != null && mc.level != null) {
                    // the camera follows the animal from its side, a little above and behind
                    Entity e = server(mc, followed);
                    if (e != null) {
                        Vec3 at = e.position().add(0.0D, 2.6D, 0.0D);
                        float yaw = e instanceof net.minecraft.world.entity.LivingEntity l ? l.yBodyRot : e.getYRot();
                        double a = Math.toRadians(yaw + 125.0D);
                        look(mc.player, at.add(-Math.sin(a) * 14.0D, 4.5D, Math.cos(a) * 14.0D), at);
                    }
                }
                Screenshot.grab(mc.gameDirectory, String.format(Locale.ROOT, "rexmotion_%s_%03d.png", tag, k), mc.getMainRenderTarget(), msg -> {
                });
                return 2;
            });
        }
    }

    /** 1.9.5, the zones (docs/estudos/12): for each zone a place is found with the server's biome locator, the player
     *  stands there two minutes while the EcoSpawner fills the land, and the hunters' share of the wild within 80 blocks
     *  is counted (TERRASSIC_OLD_ZONES=1: the 1.9.1 picking). Run in a world with terrain ("densidade"). */
    private static void planZones() {
        com.terrassic.world.EcoSpawner.Zone[] zones = com.terrassic.world.EcoSpawner.Zone.values();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Zones" + (com.terrassic.world.EcoSpawner.OLD_ZONES ? " (OLD 1.9.1 picking)" : " (1.9.5)"));
            command(mc, "gamerule doMobSpawning true");
            command(mc, "time set 1000");
            command(mc, "gamerule doDaylightCycle false");
            return 20;
        });
        for (com.terrassic.world.EcoSpawner.Zone z : zones) {
            BlockPos[] at = new BlockPos[1];
            STEPS.add(mc -> {
                net.minecraft.server.level.ServerLevel lvl = mc.getSingleplayerServer().overworld();
                BlockPos spawn = lvl.getSharedSpawnPos();
                BlockPos from = z == com.terrassic.world.EcoSpawner.Zone.MARGIN ? spawn : spawn.offset(700, 0, 700);
                java.util.function.Predicate<net.minecraft.core.Holder<net.minecraft.world.level.biome.Biome>> wet =
                        b -> b.is(net.minecraft.tags.BiomeTags.IS_OCEAN) || b.is(net.minecraft.tags.BiomeTags.IS_DEEP_OCEAN);
                var found = lvl.findClosestBiome3d(b -> z == com.terrassic.world.EcoSpawner.Zone.MARGIN
                                ? b.is(net.minecraft.tags.BiomeTags.IS_BEACH) || b.is(net.minecraft.tags.BiomeTags.IS_RIVER)
                                : !wet.test(b) && com.terrassic.world.EcoSpawner.zoneOf(lvl, from.offset(5000, 0, 5000), b) == z,
                        from, 3000, 32, 64);
                if (found == null) {
                    REPORT.add("  " + z + ": no such biome found");
                    at[0] = null;
                    return 1;
                }
                at[0] = found.getFirst();
                BlockPos ground = lvl.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at[0]);
                double share = com.terrassic.world.EcoSpawner.simulateShare(lvl, ground, 300);
                String biome = found.getSecond().unwrapKey().map(k -> k.location().toString()).orElse("?");
                REPORT.add(String.format(Locale.ROOT, "  %s (%s): 300 picks in a row -> hunters %.0f%% of the animals (target %.0f%%)",
                        z, biome, 100.0D * share, 100.0D * com.terrassic.world.EcoSpawner.huntersTargetOf(z)));
                at[0] = null;      // the measure is the simulation; no need to stand there
                return 1;
            });
            STEPS.add(mc -> {
                if (at[0] != null) {
                    command(mc, String.format(Locale.ROOT, "spreadplayers %d %d 0 1 false @s", at[0].getX(), at[0].getZ()));
                }
                return 2400;
            });
            STEPS.add(mc -> {
                if (at[0] == null) {
                    return 1;
                }
                net.minecraft.server.level.ServerLevel lvl = mc.getSingleplayerServer().overworld();
                Entity p = mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);
                int all = 0, hunt = 0;
                java.util.Map<String, Integer> by = new java.util.TreeMap<>();
                for (DinosaurEntity d : lvl.getEntitiesOfClass(DinosaurEntity.class, p.getBoundingBox().inflate(80.0D),
                        e -> e.isAlive() && !e.isTame() && !(e instanceof com.terrassic.entity.SwimmingDinosaur)
                                && !(e instanceof com.terrassic.entity.FlyingDinosaur))) {
                    all++;
                    boolean h = DinosaurEntity.isHunter(d.getType());
                    hunt += h ? 1 : 0;
                    by.merge(d.speciesId(), 1, Integer::sum);
                }
                String biome = lvl.getBiome(p.blockPosition()).unwrapKey().map(k -> k.location().toString()).orElse("?");
                REPORT.add(String.format(Locale.ROOT, "  %s (%s): %d wild on land within 80, hunters %d = %.0f%% (target %.0f%%)  %s",
                        z, biome, all, hunt, all == 0 ? 0.0D : 100.0D * hunt / all,
                        100.0D * com.terrassic.world.EcoSpawner.huntersTargetOf(z), by));
                return 1;
            });
        }
    }

    /** 1.9.5, the night (docs/estudos/12): herds and hunters mixed in a valley at dusk; after two minutes of night, who
     *  sleeps and how close each sleeping herbivore lies to the nearest predator (TERRASSIC_OLD_SLEEP=1: the 1.9.1 sleep). */
    private static void planNight() {
        double x0 = 3600.5D;
        String[][] cast = {{"edmontosaurus", "6"}, {"triceratops", "3"}, {"parasaurolophus", "2"}, {"tyrannosaurus", "2"},
                {"carnotaurus", "1"}, {"dakotaraptor", "2"}};
        java.util.List<UUID> ids = new java.util.ArrayList<>();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Night" + ("1".equals(System.getenv("TERRASSIC_OLD_SLEEP")) ? " (OLD 1.9.1 sleep)" : " (1.9.5)"));
            clear(mc, x0, 48);
            command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..120]");
            command(mc, "time set 18000");
            look(mc.player, new Vec3(x0, Y + 40.0D, 30.0D), new Vec3(x0, Y, 0.5D));
            java.util.Random rnd = new java.util.Random(7);
            for (String[] c : cast) {
                for (int i = 0; i < Integer.parseInt(c[1]); i++) {
                    UUID u = id();
                    ids.add(u);
                    summon(mc, c[0], x0 - 12 + rnd.nextInt(24), Y, -12 + rnd.nextInt(24), u, "Tags:[\"nightcast\"],Sated:30000");
                }
            }
            return 100;
        });
        for (int k = 0; k < 24; k++) {
            int kk = k;
            STEPS.add(mc -> {
                command(mc, "kill @e[type=!player,tag=!nightcast,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..120]");
                if (kk == 23) {
                    int herb = 0, herbAsleep = 0, close = 0, pred = 0, predAsleep = 0, alive = 0;
                    double minD = Double.MAX_VALUE, sumD = 0;
                    java.util.List<DinosaurEntity> all = new java.util.ArrayList<>();
                    for (UUID u : ids) {
                        DinosaurEntity d = server(mc, u);
                        if (d != null) {
                            all.add(d);
                        }
                    }
                    for (DinosaurEntity d : all) {
                        alive++;
                        if (d instanceof com.terrassic.entity.PredatorDinosaur) {
                            pred++;
                            predAsleep += d.isSleeping() ? 1 : 0;
                            continue;
                        }
                        herb++;
                        if (!d.isSleeping()) {
                            continue;
                        }
                        herbAsleep++;
                        double nd = Double.MAX_VALUE;
                        for (DinosaurEntity o : all) {
                            if (o instanceof com.terrassic.entity.PredatorDinosaur) {
                                nd = Math.min(nd, o.distanceTo(d));
                            }
                        }
                        minD = Math.min(minD, nd);
                        sumD += nd;
                        close += nd < 16.0D ? 1 : 0;
                    }
                    REPORT.add(String.format(Locale.ROOT, "  after 2 min of night: %d of %d alive; herbivores asleep %d of %d, predators asleep %d of %d",
                            alive, ids.size(), herbAsleep, herb, predAsleep, pred));
                    long edAwake = all.stream().filter(d -> d instanceof com.terrassic.entity.Saurolophine && !d.isSleeping()).count();
                    long edAll = all.stream().filter(d -> d instanceof com.terrassic.entity.Saurolophine).count();
                    REPORT.add("  Edmontosaurus awake (the watch): " + edAwake + " of " + edAll);
                    REPORT.add(String.format(Locale.ROOT, "  sleeping herbivores: nearest predator %.1f blocks at the closest, %.1f on average; %d within 16 blocks",
                            herbAsleep == 0 ? 0.0D : minD, herbAsleep == 0 ? 0.0D : sumD / herbAsleep, close));
                }
                return 100;
            });
        }
    }

    /** HOTFIX 1.9.1: Velociraptors slept as soon as they were spawned by day; the sea hunters killed far too many fish.
     *  A Velociraptor spawned in the morning (awake?) and at noon (its nap); a Mosasaurus in a pool with twelve fish for
     *  a minute (how many it kills). */
    private static void planSleepFish() {
        double x0 = 3400.5D;
        UUID r1 = id(), r2 = id(), mosa = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Sleep and fish (HOTFIX 1.9.1)");
            clear(mc, x0, 30);
            command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..80]");
            command(mc, "time set 1000");
            summon(mc, "velociraptor", x0 - 10, Y, 10.5D, r1, "");
            return 100;
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, r1);
            REPORT.add("  Velociraptor spawned at 07:00, 5 s later: " + (d == null ? "gone" : d.isSleeping() ? "ASLEEP" : "awake"));
            return 1300;
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, r1);
            REPORT.add("  the same one a minute later (08:00): " + (d == null ? "gone" : d.isSleeping() ? "ASLEEP" : "awake"));
            command(mc, "time set 6500");
            return 300;
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, r1);
            REPORT.add("  at 12:30 (its nap): " + (d == null ? "gone" : d.isSleeping() ? "asleep" : "awake"));
            summon(mc, "velociraptor", x0 - 14, Y, 10.5D, r2, "");
            return 100;
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, r2);
            REPORT.add("  one spawned at 12:30, 5 s later: " + (d == null ? "gone" : d.isSleeping() ? "ASLEEP" : "awake"));
            command(mc, "time set 1000");
            command(mc, fill(x0 + 4, Y, -14, x0 + 26, Y + 6, 8, "minecraft:glass"));
            command(mc, fill(x0 + 5, Y, -13, x0 + 25, Y + 6, 7, "minecraft:water"));
            return 40;
        });
        STEPS.add(mc -> {
            summon(mc, System.getenv().getOrDefault("TERRASSIC_FISH_HUNTER", "xiphactinus"), x0 + 15, Y + 2, -3.0D, mosa, "");
            for (int i = 0; i < 12; i++) {
                command(mc, String.format(Locale.ROOT, "summon minecraft:%s %.1f %.1f %.1f {PersistenceRequired:1b,Tags:[\"fish\"]}",
                        i % 2 == 0 ? "cod" : "salmon", x0 + 7 + (i % 6) * 3.0D, Y + 2.0D + (i % 3), -11.0D + (i / 6) * 14.0D));
            }
            return 1200;
        });
        STEPS.add(mc -> {
            int left = mc.getSingleplayerServer().overworld().getEntities((Entity) null,
                    new net.minecraft.world.phys.AABB(x0 + 4, Y - 1, -14, x0 + 26, Y + 8, 8), e -> e.getTags().contains("fish")).size();
            DinosaurEntity m = server(mc, mosa);
            REPORT.add("  " + System.getenv().getOrDefault("TERRASSIC_FISH_HUNTER", "xiphactinus") + " with 12 fish for 60 s: " + (12 - left)
                    + " killed" + (m == null ? "" : ", sated " + m.isSated() + ", hunger " + m.getHunger()));
            return 1;
        });
    }

    /** Close still shots of a head (06/11/2026, the Deinosuchus' eyes): the animal still, facing north (-z), the camera
     *  at its left, right, front and above (behavior_head_<species>_<view>.png). */
    private static void planHeadshot(String species) {
        double x0 = 3200.5D;
        for (String sp : species.split(",")) {
            UUID u = id();
            STEPS.add(mc -> {
                clear(mc, x0, 20);
                command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..60]");
                summon(mc, sp, x0, Y, 0.5D, u, "NoAI:1b,Rotation:[180f,0f]");
                look(mc.player, new Vec3(x0 + 12.0D, Y + 6.0D, 0.5D), new Vec3(x0, Y, 0.5D));
                return 60;
            });
            String[] views = {"left", "right", "above", "left_back", "right_back"};
            for (String v : views) {
                STEPS.add(mc -> {
                    DinosaurEntity d = null;
                    for (Entity e : mc.level.entitiesForRendering()) {
                        if (e instanceof DinosaurEntity dd && u.equals(dd.getUUID())) {
                            d = dd;
                        }
                    }
                    if (d == null) {
                        REPORT.add("headshot " + sp + " " + v + ": NOT FOUND");
                        return 1;
                    }
                    net.minecraft.world.phys.AABB head = null;
                    for (com.terrassic.entity.parts.DinoPart part : d.parts()) {
                        if (part.kind() == com.terrassic.entity.parts.DinoPart.Kind.HEAD) {
                            head = head == null ? part.getBoundingBox() : head.minmax(part.getBoundingBox());
                        }
                    }
                    if (head == null) {
                        REPORT.add("headshot " + sp + ": no head part");
                        return 1;
                    }
                    float yaw = d.yBodyRot * net.minecraft.util.Mth.DEG_TO_RAD;
                    Vec3 side = new Vec3(-net.minecraft.util.Mth.cos(yaw), 0, -net.minecraft.util.Mth.sin(yaw));
                    Vec3 fwd = new Vec3(-net.minecraft.util.Mth.sin(yaw), 0, net.minecraft.util.Mth.cos(yaw));
                    Vec3 c = head.getCenter();
                    if (v.endsWith("_back")) {
                        c = c.subtract(fwd.scale(head.getXsize() * 0.5D + head.getZsize() * 0.5D));
                    }
                    double r = 1.2D + Math.max(head.getYsize(), Math.max(head.getXsize(), head.getZsize())) * 1.2D;
                    Vec3 from = switch (v) {
                        case "left", "left_back" -> c.add(side.scale(r)).add(0, 0.3D, 0);
                        case "right", "right_back" -> c.subtract(side.scale(r)).add(0, 0.3D, 0);
                        default -> c.add(0, r, 0).subtract(fwd.scale(0.3D));
                    };
                    look(mc.player, from, c);
                    return 8;
                });
                STEPS.add(mc -> {
                    Screenshot.grab(mc.gameDirectory, "behavior_head_" + sp + "_" + v + ".png", mc.getMainRenderTarget(), msg -> {
                    });
                    return 2;
                });
            }
        }
    }

    /** HOTFIX 1.9.1 (06/11/2026): the water animals bounced in the water ("quicando"), the Deinosuchus worst of all,
     *  attacking in the water. A walled pool five deep: the Deinosuchus set on a prey in the water, a Mosasaurus, an
     *  Elasmosaurus and a Spinosaurus in it; every tick each one's height is read and its hops counted (a rise faster
     *  than 0.15 block/tick). Frames rexmotion_water_NNN. */
    private static void planWater() {
        double x0 = 3000.5D;
        String[] swimmers = {"deinosuchus", "mosasaurus", "elasmosaurus", "spinosaurus"};
        UUID[] ids = new UUID[swimmers.length];
        UUID prey = id();
        for (int i = 0; i < ids.length; i++) {
            ids[i] = id();
        }
        double[][] st = new double[swimmers.length][4];   // last y, min y, max y, hops
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Water: hops in a pool five deep (a hop = rising faster than 0.15 block/tick)");
            clear(mc, x0, 30);
            command(mc, fill(x0 - 16, Y, -16, x0 + 16, Y + 5, 16, "minecraft:glass"));
            command(mc, fill(x0 - 15, Y, -15, x0 + 15, Y + 5, 15, "minecraft:water"));
            look(mc.player, new Vec3(x0, Y + 14.0D, 24.0D), new Vec3(x0, Y + 3.0D, 0.5D));
            return 80;
        });
        STEPS.add(mc -> {
            for (int i = 0; i < swimmers.length; i++) {
                summon(mc, swimmers[i], x0 - 8 + i * 5, Y + 2, -6.0D + (i % 2) * 10.0D, ids[i], "");
                st[i][1] = Double.MAX_VALUE;
                st[i][2] = -Double.MAX_VALUE;
                st[i][0] = Double.NaN;
            }
            summon(mc, "edmontosaurus", x0 + 2, Y + 2, 2.0D, prey, "Age:-24000");
            return 40;
        });
        STEPS.add(mc -> {
            DinosaurEntity croc = server(mc, ids[0]);
            DinosaurEntity p = server(mc, prey);
            if (croc != null && p != null) {
                mc.getSingleplayerServer().execute(() -> croc.setTarget(p));
            }
            followed = ids[0];
            pairedWith = null;
            return 1;
        });
        for (int k = 0; k < 200; k++) {
            int kk = k;
            STEPS.add(mc -> {
                for (int i = 0; i < swimmers.length; i++) {
                    DinosaurEntity d = server(mc, ids[i]);
                    if (d == null) {
                        continue;
                    }
                    double y = d.getY();
                    if (!Double.isNaN(st[i][0]) && y - st[i][0] > 0.15D) {
                        st[i][3]++;
                    }
                    st[i][0] = y;
                    st[i][1] = Math.min(st[i][1], y);
                    st[i][2] = Math.max(st[i][2], y);
                }
                if (kk % 2 == 0) {
                    Entity e = server(mc, ids[0]);
                    if (e != null) {
                        look(mc.player, e.position().add(0.0D, 4.0D, 9.0D), e.position());
                    }
                    Screenshot.grab(mc.gameDirectory, String.format(Locale.ROOT, "rexmotion_water_%03d.png", kk / 2), mc.getMainRenderTarget(), msg -> {
                    });
                }
                if (kk == 199) {
                    for (int i = 0; i < swimmers.length; i++) {
                        REPORT.add(String.format(Locale.ROOT, "  %s: %.0f hops in 10 s, height from %.2f to %.2f (pool floor %.0f, surface %.0f)",
                                swimmers[i], st[i][3], st[i][1], st[i][2], Y, Y + 6));
                    }
                }
                return 1;
            });
        }
        STEPS.add(mc -> {
            followed = null;
            return 1;
        });
    }

    /** HOTFIX 1.9.1 (06/11/2026): jaws and beaks spun round in play. Each species runs hard (it pants), then stands; the
     *  jaw's rotation is read from the model on the client every frame and the head is filmed close
     *  (rexmotion_jaw_<species>_NNN). Reports how far the jaw turned while standing. */
    private static void planJaws() {
        String[] all = {"edmontosaurus", "pteranodon", "quetzalcoatlus", "parasaurolophus", "triceratops", "tyrannosaurus",
                "carnotaurus", "giganotosaurus", "spinosaurus", "styracosaurus", "protoceratops", "pachycephalosaurus",
                "therizinosaurus", "gallimimus", "dakotaraptor", "velociraptor", "ankylosaurus", "deinosuchus"};
        String only = System.getenv("TERRASSIC_GAIT_ONLY");
        double x0 = 2800.5D;
        STEPS.add(mc -> {
            clear(mc, x0, 40);
            look(mc.player, new Vec3(x0, Y + 12.0D, 20.0D), new Vec3(x0, Y, 0.5D));
            return 100;
        });
        for (String sp : all) {
            if (only != null && !only.isBlank() && !java.util.Arrays.asList(only.split(",")).contains(sp)) {
                continue;
            }
            UUID u = id();
            float[] jaw = {Float.NaN, Float.MAX_VALUE, -Float.MAX_VALUE, 0.0F};   // last, min, max, summed change
            STEPS.add(mc -> {
                command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..80]");
                summon(mc, sp, x0 - 30, Y, 0.5D, u, "Rotation:[-90f,0f]");
                return 30;
            });
            for (int i = 0; i < 130; i++) {
                int k = i;
                STEPS.add(mc -> {
                    DinosaurEntity d = server(mc, u);
                    if (d != null) {
                        mc.getSingleplayerServer().execute(() -> {
                            d.setTarget(null);
                            if (k < 50) {
                                d.getNavigation().moveTo(x0 + 40.0D, Y, 0.5D, 2.2D);   // a hard run: it pants after
                            } else {
                                d.getNavigation().stop();
                            }
                        });
                        Entity c = mc.level.getEntity(d.getId());
                        if (c instanceof DinosaurEntity cd && k >= 50) {
                            if (mc.getEntityRenderDispatcher().getRenderer(cd) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> gr) {
                                software.bernie.geckolib.core.animatable.model.CoreGeoBone b = gr.getGeoModel().getAnimationProcessor().getBone("jaw");
                                if (b != null) {
                                    float x = (float) Math.toDegrees(b.getRotX());
                                    if (!Float.isNaN(jaw[0])) {
                                        jaw[3] += Math.abs(x - jaw[0]);
                                    }
                                    jaw[0] = x;
                                    jaw[1] = Math.min(jaw[1], x);
                                    jaw[2] = Math.max(jaw[2], x);
                                }
                            }
                        }
                        Entity e = c != null ? c : d;
                        // close on the head: in front of the body, from the side
                        double yaw = Math.toRadians(e.getYRot());
                        Vec3 head = e.position().add(-Math.sin(yaw) * d.getBbWidth() * 0.9D, d.getBbHeight() * 0.75D, Math.cos(yaw) * d.getBbWidth() * 0.9D);
                        look(mc.player, head.add(0.0D, 0.5D, 2.5D + d.getBbHeight() * 1.2D), head);
                    }
                    Screenshot.grab(mc.gameDirectory, String.format(Locale.ROOT, "rexmotion_jaw_%s_%03d.png", sp, k), mc.getMainRenderTarget(), msg -> {
                    });
                    if (k == 129) {
                        REPORT.add(String.format(Locale.ROOT, "  jaw %s: standing after the run, from %.1f to %.1f deg, total turning %.0f deg%s",
                                sp, jaw[1], jaw[2], jaw[3], Float.isNaN(jaw[0]) ? " (no jaw bone)" : jaw[2] - jaw[1] > 90.0F ? "  <<< SPINS" : ""));
                    }
                    return 2;
                });
            }
        }
    }

    /** Each species walking, then running, on a straight line, filmed side-on and close (06/11/2026: the Triceratops'
     *  legs looked broken in play). Frames rexmotion_gait_<species>_NNN; TERRASSIC_GAIT_ONLY picks species. */
    private static void planGaits() {
        String[] all = {"triceratops", "styracosaurus", "protoceratops", "ankylosaurus", "tyrannosaurus", "carnotaurus",
                "giganotosaurus", "spinosaurus", "therizinosaurus", "pachycephalosaurus", "dakotaraptor", "velociraptor",
                "gallimimus", "parasaurolophus", "edmontosaurus", "deinosuchus", "quetzalcoatlus"};
        String only = System.getenv("TERRASSIC_GAIT_ONLY");
        double x0 = 2600.5D;
        STEPS.add(mc -> {
            clear(mc, x0, 40);
            look(mc.player, new Vec3(x0, Y + 12.0D, 20.0D), new Vec3(x0, Y, 0.5D));
            return 100;
        });
        for (String sp : all) {
            if (only != null && !only.isBlank() && !java.util.Arrays.asList(only.split(",")).contains(sp)) {
                continue;
            }
            UUID u = id();
            STEPS.add(mc -> {
                command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..80]");
                summon(mc, sp, x0 - 30, Y, 0.5D, u, "Rotation:[-90f,0f],Invulnerable:1b,Tags:[\"gaiter\"]");
                REPORT.add("== Gait: " + sp);
                return 30;
            });
            for (int i = 0; i < 120; i++) {
                int k = i;
                STEPS.add(mc -> {
                    if (k % 10 == 0) {
                        command(mc, "kill @e[type=!player,tag=!gaiter,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..90]");
                    }
                    DinosaurEntity d = server(mc, u);
                    if (d == null && k % 20 == 0) {
                        REPORT.add("  frame " + k + ": the animal is gone");
                    }
                    if (d != null) {
                        double speed = k < 60 ? 1.0D : 2.0D;
                        mc.getSingleplayerServer().execute(() -> {
                            d.setTarget(null);
                            d.getNavigation().moveTo(x0 + 40.0D, Y, 0.5D, speed);
                        });
                        Entity c = mc.level.getEntity(d.getId());
                        Entity e = c != null ? c : d;
                        double back = 2.5D + d.getBbWidth() * 1.4D + d.getBbHeight() * 0.6D;
                        Vec3 at = e.position().add(0.0D, d.getBbHeight() * 0.45D, 0.0D);
                        look(mc.player, at.add(0.0D, d.getBbHeight() * 0.2D, back), at);
                    }
                    Screenshot.grab(mc.gameDirectory, String.format(Locale.ROOT, "rexmotion_gait_%s_%03d.png", sp, k), mc.getMainRenderTarget(), msg -> {
                    });
                    return 2;
                });
            }
        }
    }

    /** The death seen in play (06/11/2026): a T. rex killed facing 60 degrees, filmed falling, then its carcass shot from
     *  eight directions near and far (rexmotion_death_*, behavior_carcass_<dist>_<deg>.png). */
    private static void planCarcass() {
        double x0 = 2400.5D;
        UUID u = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Death and carcass");
            clear(mc, x0, 20);
            summon(mc, "tyrannosaurus", x0, Y, 0.5D, u, "NoAI:1b,Rotation:[60f,0f]");
            followed = u;
            return 40;
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, u);
            if (d != null) {
                REPORT.add(String.format(Locale.ROOT, "  body yaw at death %.1f", d.yBodyRot));
                mc.getSingleplayerServer().execute(() -> d.hurt(d.damageSources().generic(), 100000.0F));
            }
            return 1;
        });
        burst("death", 60, k -> {
        });
        STEPS.add(mc -> {
            followed = null;
            java.util.List<com.terrassic.entity.CarcassEntity> cs = mc.level.getEntitiesOfClass(com.terrassic.entity.CarcassEntity.class,
                    new net.minecraft.world.phys.AABB(x0 - 10, Y - 3, -10, x0 + 10, Y + 5, 10));
            REPORT.add("  carcasses on the client: " + cs.size() + (cs.isEmpty() ? "" : String.format(Locale.ROOT, ", yaw %.1f", cs.get(0).getYRot())));
            REPORT.add("  dinosaurs left on the client: " + mc.level.getEntitiesOfClass(DinosaurEntity.class,
                    new net.minecraft.world.phys.AABB(x0 - 10, Y - 3, -10, x0 + 10, Y + 5, 10)).size());
            return 5;
        });
        UUID alive = id();
        STEPS.add(mc -> {
            // a living T. rex standing near, as the killers were in play
            summon(mc, "tyrannosaurus", x0 + 14, Y, 8.5D, alive, "NoAI:1b,Rotation:[200f,0f]");
            return 30;
        });
        // the camera looking past the carcass: up, aside, the carcass at the edge of the screen or just outside it
        for (int off : new int[]{0, 20, 30, 38, 45, 55}) {
            for (int kind = 0; kind < 2; kind++) {
                int oo = off, kk = kind;
                STEPS.add(mc -> {
                    Vec3 at = new Vec3(x0, Y + 1.0D, 0.5D);
                    Vec3 from = at.add(-10.0D, 5.0D, 6.0D);
                    // aside: the aim slid along the body's side; up: the aim raised
                    Vec3 aim = kk == 0 ? at.add(oo * 0.25D, 0.0D, oo * 0.25D) : at.add(0.0D, oo * 0.2D, 0.0D);
                    look(mc.player, from, aim);
                    return 6;
                });
                STEPS.add(mc -> {
                    Screenshot.grab(mc.gameDirectory, String.format(Locale.ROOT, "behavior_carcass_edge_%s_%02d.png", kk == 0 ? "side" : "up", oo),
                            mc.getMainRenderTarget(), msg -> {
                            });
                    return 2;
                });
            }
        }
        for (int dist : new int[]{9, 22}) {
            for (int deg = 0; deg < 360; deg += 45) {
                int dd = dist, gg = deg;
                STEPS.add(mc -> {
                    Vec3 at = new Vec3(x0, Y + 1.0D, 0.5D);
                    double a = Math.toRadians(gg);
                    look(mc.player, at.add(-Math.sin(a) * dd, dd * 0.35D, Math.cos(a) * dd), at);
                    return 6;
                });
                STEPS.add(mc -> {
                    Screenshot.grab(mc.gameDirectory, String.format(Locale.ROOT, "behavior_carcass_%d_%03d.png", dd, gg), mc.getMainRenderTarget(), msg -> {
                    });
                    return 2;
                });
            }
        }
    }

    /** Every species' duel (06/11/2026, the 1.9.0 fluid set): pairs set on each other, filmed (rexmotion_duel_<a>_<b>). */
    private static void planAllDuels() {
        String[][] pairs = {{"tyrannosaurus", "tyrannosaurus"}, {"carnotaurus", "carnotaurus"}, {"giganotosaurus", "giganotosaurus"},
                {"spinosaurus", "triceratops"}, {"triceratops", "triceratops"}, {"pachycephalosaurus", "pachycephalosaurus"},
                {"dakotaraptor", "styracosaurus"}, {"therizinosaurus", "therizinosaurus"}, {"styracosaurus", "styracosaurus"}, {"protoceratops", "protoceratops"},
                {"ankylosaurus", "tyrannosaurus"}};
        double x0 = 2000.5D;
        // the arena's chunks loaded and settled before the first pair (on a fresh world the first pair spawned into
        // terrain still being generated and was thrown about, 06/11)
        STEPS.add(mc -> {
            clear(mc, x0, 24);
            look(mc.player, new Vec3(x0 - 20.0D, Y + 12.0D, 14.0D), new Vec3(x0, Y, 0.5D));
            return 100;
        });
        // TERRASSIC_DUEL_ONLY=tyrannosaurus,carnotaurus: only the pairs whose first fighter is one of these
        String only = System.getenv("TERRASSIC_DUEL_ONLY");
        for (String[] pair : pairs) {
            if (only != null && !only.isBlank() && !java.util.Arrays.asList(only.split(",")).contains(pair[0])) {
                continue;
            }
            UUID a = id(), b = id();
            STEPS.add(mc -> {
                REPORT.add("");
                REPORT.add("== Duel: " + pair[0] + " against " + pair[1]);
                clear(mc, x0, 24);
                command(mc, "kill @e[type=!player,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..60]");
                summon(mc, pair[0], x0 - 6, Y, 0.5D, a, "Female:0b,Tags:[\"duelist\"]");
                summon(mc, pair[1], x0 + 6, Y, 0.5D, b, "Female:0b,Tags:[\"duelist\"]");
                followed = a;
                pairedWith = b;
                camSide = null;
                return 30;
            });
            STEPS.add(mc -> {
                DinosaurEntity da = server(mc, a), db = server(mc, b);
                if (da != null && db != null) {
                    mc.getSingleplayerServer().execute(() -> {
                        da.setTarget(db);
                        db.setTarget(da);
                    });
                }
                return 2;
            });
            double[] m = new double[8];   // last positions a/b (x,z), summed distance, summed motion, samples, clinch frames
            int[] ev = new int[3];          // dodges, counters armed, clinch starts
            burst("duel_" + pair[0] + "_" + pair[1], 200, k -> {
                Minecraft mcm = Minecraft.getInstance();
                if (k % 10 == 0) {
                    // the ecosystem keeps peopling the land round the player: strays out of the arena
                    command(mcm, "kill @e[type=!player,tag=!duelist,x=" + (int) x0 + ",y=" + (int) Y + ",z=0,distance=..70]");
                }
                DinosaurEntity ma = server(mcm, a), mb = server(mcm, b);
                if (ma != null && mb != null) {
                    if (k > 0) {
                        m[5] += Math.hypot(ma.getX() - m[0], ma.getZ() - m[1]) + Math.hypot(mb.getX() - m[2], mb.getZ() - m[3]);
                    }
                    m[0] = ma.getX(); m[1] = ma.getZ(); m[2] = mb.getX(); m[3] = mb.getZ();
                    m[4] += ma.distanceTo(mb);
                    m[6]++;
                    if (ma.clinchLeft > 0) {
                        m[7]++;
                    }
                    if (ma.dodgeLeft > 0 || mb.dodgeLeft > 0) {
                        ev[0]++;
                    }
                    if (ma.counterLeft > 0 || mb.counterLeft > 0) {
                        ev[1]++;
                    }
                }
                if (k == 199) {
                    REPORT.add(String.format(Locale.ROOT, "    mean gap %.1f blocks, both moving %.2f blocks/s, frames grappling %.0f",
                            m[4] / Math.max(1, m[6]), m[5] / Math.max(1, m[6] - 1) * 10.0D, m[7]));
                    for (DinosaurEntity f : new DinosaurEntity[]{ma, mb}) {
                        if (f != null && f.duelBrain() != null) {
                            int[] st = f.duelBrain().stats;
                            REPORT.add(String.format(Locale.ROOT, "    %s: lunges %d, jabs %d, signature %d, feints %d | landed %d, missed %d | parried %d, blocked %d, sidestepped %d, staggered %d",
                                    f.speciesId(), st[0], st[7], st[8], st[9], st[1], st[2], st[3], st[4], st[6], st[5]));
                        }
                    }
                }
                if (k % 50 == 49) {
                    Minecraft mc = Minecraft.getInstance();
                    DinosaurEntity da = server(mc, a), db = server(mc, b);
                    if (da != null && db != null) {
                        REPORT.add(String.format(Locale.ROOT, "    t=%ds: %s %.0f/%.0f dueling %s locked %s | %s %.0f/%.0f dueling %s locked %s | %.1f apart",
                                (k + 1) / 10, pair[0], da.getHealth(), da.getMaxHealth(), da.isDueling(), da.isLocked(),
                                pair[1], db.getHealth(), db.getMaxHealth(), db.isDueling(), db.isLocked(), da.distanceTo(db)));
                    }
                }
            });
            STEPS.add(mc -> {
                command(mc, "kill " + a);
                command(mc, "kill " + b);
                pairedWith = null;
                return 20;
            });
        }
    }

    /** Every species' new one-shots and loops (06/11/2026), triggered one after another and logged. */
    private static void planAllMoves() {
        String[] species = {"carnotaurus", "giganotosaurus", "spinosaurus", "velociraptor", "dakotaraptor", "triceratops",
                "styracosaurus", "protoceratops", "pachycephalosaurus", "parasaurolophus", "edmontosaurus", "gallimimus",
                "ankylosaurus", "therizinosaurus", "deinosuchus", "pteranodon", "quetzalcoatlus"};
        String[] moves = {"feint", "block", "recoil", "submit", "lie_down", "get_up", "ram", "head_clash", "grab_shake", "claw_swipe",
                "sail_display", "leap_back", "nose_jab", "frill_shove", "horn_lock_start", "flank_butt", "kick_back", "body_shove",
                "club_duel", "claw_slash", "gape_threat", "jab", "crest_display"};
        double x0 = 2200.5D;
        for (String sp : species) {
            UUID u = id();
            STEPS.add(mc -> {
                clear(mc, x0, 16);
                summon(mc, sp, x0, Y, 0.5D, u, "NoAI:1b");
                followed = u;
                return 30;
            });
            for (String mv : moves) {
                STEPS.add(mc -> {
                    DinosaurEntity d = server(mc, u);
                    if (d != null) {
                        mc.getSingleplayerServer().execute(() -> d.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, mv));
                    }
                    return 12;
                });
            }
            STEPS.add(mc -> {
                command(mc, "kill " + u);
                return 10;
            });
        }
    }

    /** The ecosystem (06/11/2026): grazing that crops the grass, a herd migrating in file, a T. rex shadowing it, and
     *  the evening at the water. */
    private static void planEcosystem() {
        double x0 = 1800.5D;
        UUID rex = id();
        List<UUID> herd = new ArrayList<>();
        int[] grass = {0};
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Ecosystem: six Edmontosaurus on tall grass, a pool 30 blocks east, a full T. rex 40 blocks south");
            clear(mc, x0, 30);
            command(mc, "gamerule mobGriefing true");
            command(mc, "fill " + (int) (x0 - 30) + " " + (int) Y + " -30 " + (int) (x0 + 30) + " " + (int) Y + " 30 minecraft:grass replace minecraft:air");
            pool(mc, x0 + 30, 0.5D, 4);
            for (int i = 0; i < 6; i++) {
                UUID u = id();
                herd.add(u);
                summon(mc, "edmontosaurus", x0 - 6 + (i % 3) * 5, Y, -4.5D + (i / 3) * 6, u, "Female:" + (i % 2) + "b,Hunger:30");
            }
            summon(mc, "tyrannosaurus", x0, Y, -40.5D, rex, "Female:0b,Hunger:100");
            watch(mc, new Vec3(x0, Y, 0.0D), 40.0D);
            return 40;
        });
        STEPS.add(mc -> {
            grass[0] = countGrass(mc, x0);
            REPORT.add("  tall grass plants round them at the start: " + grass[0]);
            return 2400;
        });
        STEPS.add(mc -> {
            REPORT.add("  after two minutes of grazing: " + countGrass(mc, x0) + " (was " + grass[0] + ")");
            // the season calls: the first one sets off west, the rest should follow in file
            DinosaurEntity lead = server(mc, herd.get(0));
            if (lead != null) {
                BlockPos to = BlockPos.containing(lead.getX() - 90, Y, lead.getZ());
                mc.getSingleplayerServer().execute(() -> {
                    for (UUID u : herd) {
                        DinosaurEntity d = server(mc, u);
                        if (d != null) {
                            d.setMigrationTarget(to);
                        }
                    }
                });
            }
            command(mc, "forceload add " + (int) (x0 - 130) + " -40 " + (int) x0 + " 40");
            return 20;
        });
        for (int i = 0; i < 6; i++) {
            STEPS.add(mc -> {
                StringBuilder b = new StringBuilder("    migrating (x, z): ");
                double minZ = 1e9, maxZ = -1e9, minX = 1e9, maxX = -1e9;
                for (UUID u : herd) {
                    DinosaurEntity d = server(mc, u);
                    if (d != null) {
                        b.append(String.format(Locale.ROOT, "%.0f,%.0f ", d.getX() - x0, d.getZ()));
                        minZ = Math.min(minZ, d.getZ()); maxZ = Math.max(maxZ, d.getZ()); minX = Math.min(minX, d.getX()); maxX = Math.max(maxX, d.getX());
                    }
                }
                DinosaurEntity r = server(mc, rex);
                b.append(String.format(Locale.ROOT, "| spread along %.0f across %.0f | T. rex %.0f,%.0f", maxX - minX, maxZ - minZ,
                        r == null ? 0 : r.getX() - x0, r == null ? 0 : r.getZ()));
                REPORT.add(b.toString());
                return 200;
            });
        }
        STEPS.add(mc -> {
            int path = 0;
            ServerLevel l = mc.getSingleplayerServer().overworld();
            for (BlockPos p : BlockPos.betweenClosed((int) x0 - 130, (int) Y - 1, -20, (int) x0, (int) Y - 1, 20)) {
                if (l.getBlockState(p).is(net.minecraft.world.level.block.Blocks.DIRT_PATH)) {
                    path++;
                }
            }
            REPORT.add("  trail: dirt path blocks left on the way " + path);
            // the evening: a fresh herd by the pool's side, the clock at dusk
            for (UUID u : herd) {
                command(mc, "tp " + u + " " + (x0 - 4) + " " + Y + " 0.5");
            }
            mc.getSingleplayerServer().execute(() -> {
                for (UUID u : herd) {
                    DinosaurEntity d = server(mc, u);
                    if (d != null) {
                        d.setMigrationTarget(null);
                    }
                }
            });
            command(mc, "time set 11200");
            watch(mc, new Vec3(x0 + 12, Y, 0.0D), 40.0D);
            return 1600;
        });
        STEPS.add(mc -> {
            int near = 0;
            for (UUID u : herd) {
                DinosaurEntity d = server(mc, u);
                if (d != null && Math.abs(d.getX() - (x0 + 30)) < 10 && Math.abs(d.getZ()) < 10) {
                    near++;
                }
            }
            REPORT.add("  dusk: Edmontosaurus by the pool after 80 s: " + near + " of " + herd.size());
            command(mc, "time set 6000");
            command(mc, "kill @e[type=!player]");
            return 20;
        });
    }

    private static int countGrass(Minecraft mc, double x0) {
        int n = 0;
        ServerLevel l = mc.getSingleplayerServer().overworld();
        for (BlockPos p : BlockPos.betweenClosed((int) x0 - 30, (int) Y, -30, (int) x0 + 30, (int) Y, 30)) {
            if (l.getBlockState(p).is(net.minecraft.world.level.block.Blocks.GRASS)) {
                n++;
            }
        }
        return n;
    }

    /** Duels (06/11/2026): two grown male T. rex of one size set on each other, then a T. rex against a Triceratops. */
    private static void planRexDuel() {
        double x0 = 1600.5D;
        UUID a = id(), b = id(), trike = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Duels: two male T. rex of one size; then a T. rex against a Triceratops (frames rexmotion_duel*)");
            clear(mc, x0, 30);
            summon(mc, "tyrannosaurus", x0 - 7, Y, 0.5D, a, "Female:0b");
            summon(mc, "tyrannosaurus", x0 + 7, Y, 0.5D, b, "Female:0b");
            followed = a;
            return 40;
        });
        STEPS.add(mc -> {
            DinosaurEntity da = server(mc, a), db = server(mc, b);
            if (da != null && db != null) {
                mc.getSingleplayerServer().execute(() -> {
                    da.setTarget(db);
                    db.setTarget(da);
                });
            }
            return 2;
        });
        burst("duel", 300, k -> {
            if (k % 50 == 0) {
                Minecraft mc = Minecraft.getInstance();
                DinosaurEntity da = server(mc, a), db = server(mc, b);
                if (da != null && db != null) {
                    REPORT.add(String.format(Locale.ROOT, "    t=%ds: A %.0f/%.0f hp dueling %s, B %.0f/%.0f hp dueling %s, %.1f apart",
                            k / 10, da.getHealth(), da.getMaxHealth(), ((com.terrassic.entity.ApexTheropod) da).isDueling(),
                            db.getHealth(), db.getMaxHealth(), ((com.terrassic.entity.ApexTheropod) db).isDueling(), da.distanceTo(db)));
                }
            }
        });
        STEPS.add(mc -> {
            DinosaurEntity da = server(mc, a), db = server(mc, b);
            REPORT.add(String.format(Locale.ROOT, "  after 30 s: A %s, B %s", da == null ? "gone" : String.format(Locale.ROOT, "%.0f hp, target %s", da.getHealth(), da.getTarget() == null ? "none" : "the other"),
                    db == null ? "gone" : String.format(Locale.ROOT, "%.0f hp, target %s", db.getHealth(), db.getTarget() == null ? "none" : "the other")));
            command(mc, "kill " + b);
            summon(mc, "triceratops", x0 + 8, Y, 0.5D, trike, "Female:0b");
            return 20;
        });
        STEPS.add(mc -> {
            DinosaurEntity da = server(mc, a), dt = server(mc, trike);
            if (da != null && dt != null) {
                mc.getSingleplayerServer().execute(() -> {
                    da.heal(400.0F);
                    da.setTarget(dt);
                    dt.setTarget(da);
                });
            }
            return 2;
        });
        burst("duel_trike", 240, k -> {
        });
        STEPS.add(mc -> {
            DinosaurEntity da = server(mc, a), dt = server(mc, trike);
            REPORT.add(String.format(Locale.ROOT, "  T. rex vs Triceratops after 24 s: rex %s, trike %s", da == null ? "gone" : String.format(Locale.ROOT, "%.0f hp", da.getHealth()),
                    dt == null ? "dead/gone" : String.format(Locale.ROOT, "%.0f hp", dt.getHealth())));
            shotCooldown = 0;
            command(mc, "kill @e[type=!player]");
            return 20;
        });
    }

    /**
     * The T. rex's live motion (06/11/2026, the Raxiores study): bursts of frames for GIFs of the walk round a circle
     * (tail spring and bank), turning on the spot (the step-round loops), the run round a circle and the idle.
     */
    private static void planRexMotion() {
        double x0 = 1400.5D;
        UUID rex = id();
        double[] ang = {0.0D};
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== T. rex live motion: walk, turn on the spot, run, idle (frames rexmotion_*)");
            clear(mc, x0, 30);
            summon(mc, "tyrannosaurus", x0, Y, 0.5D, rex, "Female:0b");
            followed = rex;
            watch(mc, new Vec3(x0, Y + 3, 0.0D), 34.0D);
            shotCooldown = 100000;
            return 60;
        });
        java.util.function.BiConsumer<Minecraft, Double> circle = (mc, speed) -> {
            DinosaurEntity d = server(mc, rex);
            if (d != null) {
                ang[0] += 0.045D * speed;
                double tx = x0 + 13.0D * Math.cos(ang[0]), tz = 13.0D * Math.sin(ang[0]);
                // a wanted position straight ahead on the circle (a fresh path every two ticks never got it going)
                mc.getSingleplayerServer().execute(() -> {
                    d.getNavigation().stop();
                    d.getMoveControl().setWantedPosition(tx, Y, tz, speed);
                });
            }
        };
        for (int i = 0; i < 40; i++) {
            STEPS.add(mc -> {
                circle.accept(mc, 1.0D);
                return 2;
            });
        }
        burst("walk", 90, k -> circle.accept(Minecraft.getInstance(), 1.0D));
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, rex);
            if (d != null) {
                mc.getSingleplayerServer().execute(() -> d.getNavigation().stop());
            }
            return 40;
        });
        double[] look = {0.0D};
        burst("turn", 110, k -> {
            Minecraft mc = Minecraft.getInstance();
            DinosaurEntity d = server(mc, rex);
            if (d != null) {
                look[0] += k < 55 ? 0.065D : -0.065D;
                double lx = d.getX() + 10.0D * Math.sin(look[0]), lz = d.getZ() + 10.0D * Math.cos(look[0]);
                mc.getSingleplayerServer().execute(() -> {
                    d.getNavigation().stop();
                    d.getLookControl().setLookAt(lx, d.getEyeY(), lz, 30.0F, 30.0F);
                });
            }
        });
        burst("run", 70, k -> circle.accept(Minecraft.getInstance(), 2.2D));
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, rex);
            if (d != null) {
                mc.getSingleplayerServer().execute(() -> d.getNavigation().stop());
            }
            return 60;
        });
        burst("idle", 90, k -> {
        });
        // the one-shots, each triggered on the server and filmed whole
        String[][] SHOTS = {{"roar", "72"}, {"roar_loud", "92"}, {"attack", "44"}, {"attack_quick", "22"}, {"snort", "36"},
                {"settle", "56"}, {"scan", "104"}, {"stretch", "76"}, {"shake", "44"}, {"bite_low", "26"}, {"bite_side", "28"},
                {"lie_down", "46"}, {"get_up", "46"}, {"fall_asleep", "74"}};
        for (String[] shot : SHOTS) {
            burst(shot[0], Integer.parseInt(shot[1]), k -> {
                if (k == 2) {
                    Minecraft mc = Minecraft.getInstance();
                    DinosaurEntity d = server(mc, rex);
                    if (d != null) {
                        mc.getSingleplayerServer().execute(() -> d.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, shot[0]));
                    }
                }
            });
            STEPS.add(mc -> 20);
        }
        // a hard run, then the stop: the panting layer
        // long enough to tire it (the fatigue of the 06/11 states): then the stop shows the spent stand
        UUID[] preyRun = {id(), id(), id()};
        STEPS.add(mc -> {
            for (int i = 0; i < preyRun.length; i++) {
                command(mc, String.format(Locale.ROOT, "summon terrassic:leptoceratops %.1f %.1f %.1f {UUID:%s}", x0 + 14 + i * 3, Y, -6.5D + i * 6, uuidNbt(preyRun[i])));
            }
            return 5;
        });
        burst("run2", 170, k -> {
            Minecraft mc = Minecraft.getInstance();
            DinosaurEntity hunter = server(mc, rex);
            if (hunter != null && (hunter.getTarget() == null || !hunter.getTarget().isAlive())) {
                for (UUID u : preyRun) {
                    if (serverAny(mc, u) instanceof net.minecraft.world.entity.LivingEntity l && l.isAlive()) {
                        mc.getSingleplayerServer().execute(() -> hunter.setTarget(l));
                        break;
                    }
                }
            }
            if (k % 40 == 0) {
                DinosaurEntity d = server(mc, rex);
                if (d instanceof com.terrassic.entity.ApexTheropod at) {
                    REPORT.add(String.format(Locale.ROOT, "    running: %.3f blocks/tick, fatigue %.2f", Math.sqrt((d.getX() - d.xo) * (d.getX() - d.xo) + (d.getZ() - d.zo) * (d.getZ() - d.zo)), at.fatigue()));
                }
            }
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, rex);
            if (d != null) {
                mc.getSingleplayerServer().execute(() -> d.getNavigation().stop());
            }
            return 1;
        });
        STEPS.add(mc -> {
            DinosaurEntity d = server(mc, rex);
            REPORT.add("  after the long run: tired " + (d instanceof com.terrassic.entity.ApexTheropod at && at.isTired()));
            return 1;
        });
        burst("pant", 100, k -> {
        });
        // feet on uneven ground: it stands with the left foot on a one-block step
        STEPS.add(mc -> {
            command(mc, fill(x0 - 6, Y, -8, x0 + 6, Y, -1, "minecraft:stone"));
            command(mc, "tp " + rex + " " + x0 + " " + (Y + 1) + " -0.3 90 0");
            return 60;
        });
        burst("step", 30, k -> {
            Minecraft mc = Minecraft.getInstance();
            DinosaurEntity d = server(mc, rex);
            if (d != null) {
                mc.getSingleplayerServer().execute(() -> {
                    d.getNavigation().stop();
                    d.setYRot(90.0F);
                    d.setYBodyRot(90.0F);
                    d.setYHeadRot(90.0F);
                });
            }
        });
        STEPS.add(mc -> {
            shotCooldown = 0;
            command(mc, "kill " + rex);
            return 20;
        });
    }

    /** A pool in the middle of the arena, its surface at the ground (for drinking, swimming, wading). */
    private static void pool(Minecraft mc, double x, double z, int r) {
        command(mc, fill(x - r, Y - 2, z - r, x + r, Y - 1, z + r, "minecraft:water"));
    }

    private static void planQuetzalcoatlus() {
        String sp = "quetzalcoatlus";
        double x0 = 800.5D;
        UUID m1 = id(), m2 = id(), f1 = id();
        List<UUID> prey = new ArrayList<>();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Quetzalcoatlus: two males and a female on open ground with a pool; small prey walks among them");
            clear(mc, x0, 30);
            pool(mc, x0 + 9, 6.5D, 3);
            summon(mc, sp, x0, Y, 0.5D, m1, "Female:0b");
            summon(mc, sp, x0 + 5, Y, -4.5D, m2, "Female:0b");
            summon(mc, sp, x0 - 4, Y, 3.5D, f1, "Female:1b");
            watch(mc, new Vec3(x0, Y + 3, 0.0D), 30.0D);
            return 1600;
        });
        STEPS.add(mc -> {
            REPORT.add("  six small prey (Mesodma, chickens) let loose round them");
            for (int i = 0; i < 6; i++) {
                UUID u = id();
                prey.add(u);
                if (i % 2 == 0) {
                    summon(mc, "mesodma", x0 - 8 + i * 3, Y, -8.5D + i, u, "");
                } else {
                    command(mc, String.format(Locale.ROOT, "summon minecraft:chicken %.1f %.1f %.1f {UUID:%s}", x0 - 8 + i * 3, Y, 8.5D - i, uuidNbt(u)));
                }
            }
            return 2400;
        });
        STEPS.add(mc -> {
            int alive = 0;
            for (UUID u : prey) {
                if (serverAny(mc, u) != null && serverAny(mc, u).isAlive()) {
                    alive++;
                }
            }
            REPORT.add("  small prey alive after two minutes: " + alive + " of " + prey.size());
            command(mc, "kill @e[type=minecraft:chicken]");
            return 20;
        });
        planTameRideBreed(sp, f1, m2, null, ModItems.QUETZALCOATLUS_SADDLE.get(), x0, false);
    }

    private static void planEdmontosaurus() {
        String sp = "edmontosaurus";
        double x0 = 1000.5D;
        UUID m1 = id(), m2 = id(), f1 = id(), f2 = id(), b1 = id(), b2 = id(), rex = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Edmontosaurus: a herd (two males, two females, two calves) on grass with a pool and tall oaks");
            clear(mc, x0, 30);
            pool(mc, x0 - 10, -8.5D, 3);
            for (int[] t : new int[][]{{9, -9}, {-9, 9}, {12, 7}}) {
                command(mc, fill(x0 + t[0], Y, t[1], x0 + t[0], Y + 5, t[1], "minecraft:oak_log"));
                command(mc, fill(x0 + t[0] - 2, Y + 4, t[1] - 2, x0 + t[0] + 2, Y + 6, t[1] + 2, "minecraft:oak_leaves[persistent=true]"));
            }
            summon(mc, sp, x0, Y, 0.5D, m1, "Female:0b");
            summon(mc, sp, x0 + 6, Y, 3.5D, m2, "Female:0b");
            summon(mc, sp, x0 - 5, Y, -3.5D, f1, "Female:1b");
            summon(mc, sp, x0 + 3, Y, -6.5D, f2, "Female:1b");
            summon(mc, sp, x0 + 2, Y, 6.5D, b1, "Age:-24000");
            summon(mc, sp, x0 - 2, Y, 8.5D, b2, "Age:-24000");
            watch(mc, new Vec3(x0, Y + 3, 0.0D), 30.0D);
            return 3600;
        });
        STEPS.add(mc -> {
            REPORT.add("  a wild T. rex (held still) 22 blocks away");
            summon(mc, "tyrannosaurus", x0 + 22, Y, 0.5D, rex, "NoAI:1b");
            return 30;
        });
        for (int i = 0; i < 6; i++) {
            STEPS.add(mc -> {
                StringBuilder b = new StringBuilder("    herd: ");
                for (UUID u : new UUID[]{m1, m2, f1, f2, b1, b2}) {
                    DinosaurEntity d = server(mc, u);
                    if (d != null) {
                        b.append(String.format(Locale.ROOT, "%.0f/%s ", d.getX() - x0, d.getNavigation().isDone() ? "still" : "moving"));
                    }
                }
                REPORT.add(b.toString());
                return 40;
            });
        }
        STEPS.add(mc -> {
            command(mc, "tp " + rex + " 0 -400 0");
            return 1200;
        });
        planTameRideBreed(sp, f1, m2, new ItemStack(Items.WHEAT, 64), ModItems.EDMONTOSAURUS_SADDLE.get(), x0, false);
    }

    private static void planDakotaraptor() {
        String sp = "dakotaraptor";
        double x0 = 1200.5D;
        UUID m1 = id(), m2 = id(), f1 = id();
        List<UUID> prey = new ArrayList<>();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Dakotaraptor: a pack (two males, a female) on grass with a pool and a fallen log");
            clear(mc, x0, 30);
            pool(mc, x0 + 10, -7.5D, 3);
            command(mc, fill(x0 - 12, Y, 9, x0 - 4, Y, 9, "minecraft:oak_log[axis=x]"));
            summon(mc, sp, x0, Y, 0.5D, m1, "Female:0b");
            summon(mc, sp, x0 + 3, Y, -2.5D, m2, "Female:0b");
            summon(mc, sp, x0 - 3, Y, 2.5D, f1, "Female:1b");
            watch(mc, new Vec3(x0, Y + 2, 0.0D), 26.0D);
            return 1600;
        });
        STEPS.add(mc -> {
            REPORT.add("  a player in survival walks up to the first male (6 blocks)");
            command(mc, "gamemode survival @a");
            DinosaurEntity d = server(mc, m1);
            ServerPlayer p = player(mc);
            if (d != null && p != null) {
                mc.getSingleplayerServer().execute(() -> p.teleportTo(d.getX() + 5.0D, d.getY() + 0.5D, d.getZ()));
            }
            return 100;
        });
        STEPS.add(mc -> {
            command(mc, "gamemode creative @a");
            mc.player.getAbilities().flying = true;
            watch(mc, new Vec3(x0, Y + 2, 0.0D), 26.0D);
            REPORT.add("  prey let loose 12 blocks away: two Leptoceratops, a pig, two sheep");
            String[][] P = {{"terrassic:leptoceratops", "-12"}, {"terrassic:leptoceratops", "-9"}, {"minecraft:pig", "9"}, {"minecraft:sheep", "12"}, {"minecraft:sheep", "6"}};
            for (String[] e : P) {
                UUID u = id();
                prey.add(u);
                command(mc, String.format(Locale.ROOT, "summon %s %.1f %.1f %s.5 {UUID:%s}", e[0], x0 + 12, Y, e[1], uuidNbt(u)));
            }
            return 2400;
        });
        STEPS.add(mc -> {
            int alive = 0;
            for (UUID u : prey) {
                if (serverAny(mc, u) != null && serverAny(mc, u).isAlive()) {
                    alive++;
                }
            }
            REPORT.add("  prey alive after two minutes: " + alive + " of " + prey.size());
            command(mc, "kill @e[type=!player,type=!terrassic:dakotaraptor]");
            return 600;
        });
        planTameRideBreed(sp, f1, m2, null, ModItems.DAKOTARAPTOR_SADDLE.get(), x0, false);
    }

    private static void planDeinosuchus() {
        String sp = "deinosuchus";
        double x0 = 200.5D;
        UUID male = id(), female = id(), baby = id(), bank = id(), pig = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Deinosuchus: a river pool 4 deep with a sand bank, noon");
            clear(mc, x0, 26);
            command(mc, fill(x0 - 20, Y - 4, -12, x0 + 20, Y - 1, 12, "minecraft:water"));
            command(mc, fill(x0 - 20, Y - 1, 12, x0 + 20, Y - 1, 20, "minecraft:sand"));
            summon(mc, sp, x0, Y - 2, 0.5D, male, "Female:0b,Hunger:100");
            summon(mc, sp, x0 - 8, Y - 2, -4.5D, female, "Female:1b,Hunger:100");
            summon(mc, sp, x0 + 6, Y, 15.5D, bank, "Female:1b,Hunger:100");
            summon(mc, sp, x0 + 3, Y, 17.5D, baby, "Age:-24000");
            watch(mc, new Vec3(x0, Y, 4.0D), 24.0D);
            return 3600;
        });
        STEPS.add(mc -> {
            REPORT.add("  hungry now; a pig swims into the pool");
            command(mc, "data merge entity " + male + " {Hunger:5}");
            command(mc, String.format(Locale.ROOT, "summon minecraft:pig %.1f %.1f 0.5 {UUID:%s}", x0 + 6, Y - 1, uuidNbt(pig)));
            return 20;
        });
        for (int i = 0; i < 12; i++) {
            STEPS.add(mc -> {
                DinosaurEntity d = server(mc, male);
                Entity pg = serverAny(mc, pig);
                if (d != null) {
                    REPORT.add(String.format(Locale.ROOT, "    male: hunger %d, target %s, in water %s, pig %s",
                            d.getHunger(), d.getTarget() == null ? "none" : d.getTarget().getType().toShortString(), d.isInWater(),
                            pg == null || !pg.isAlive() ? "gone" : String.format(Locale.ROOT, "%.1f away, in water %s", d.distanceTo(pg), pg.isInWater())));
                }
                return 100;
            });
        }
        STEPS.add(mc -> {
            command(mc, "kill " + pig);
            return 20;
        });
        planTameRideBreed(sp, female, male, null, null, x0, true);
    }

    private static void planElasmosaurus() {
        String sp = "elasmosaurus";
        double x0 = 400.5D;
        UUID male = id(), female = id(), baby = id();
        STEPS.add(mc -> {
            REPORT.add("");
            REPORT.add("== Elasmosaurus: a glass sea pool 40 x 40, 12 deep");
            clear(mc, x0, 30);
            for (int zz : new int[]{-22, 0}) {
                command(mc, fill(x0 - 22, Y - 4, zz, x0 + 22, Y + 9, zz + 22, "minecraft:glass"));
            }
            for (int zz : new int[]{-21, 0}) {
                command(mc, fill(x0 - 21, Y - 3, zz, x0 + 21, Y + 8, Math.min(21, zz + 21), "minecraft:water"));
            }
            // open to the sky: an air-breather has to reach the air (its BreatheGoal gives up under a roof)
            command(mc, fill(x0 - 21, Y + 9, -21, x0 + 21, Y + 9, 21, "minecraft:air"));
            summon(mc, sp, x0, Y + 2, 0.5D, male, "Female:0b");
            summon(mc, sp, x0 - 8, Y + 4, -6.5D, female, "Female:1b");
            summon(mc, sp, x0 + 5, Y + 3, 8.5D, baby, "Age:-24000");
            watch(mc, new Vec3(x0, Y + 4, 0.0D), 30.0D);
            return 3000;
        });
        planTameRideBreed(sp, female, male, new ItemStack(Items.COD, 64), ModItems.ELASMOSAURUS_SADDLE.get(), x0, true);
        STEPS.add(mc -> {
            command(mc, fill(x0 - 22, Y - 4, -22, x0 + 22, Y + 9, 22, "minecraft:air"));
            return 5;
        });
    }

    /**
     * Taming by hand with the food it takes, the saddle (if it has one), a ride photographed in third person, then the
     * pair tamed and bred: the egg block and its hatching, or a calf born alive.
     */
    private static void planTameRideBreed(String sp, UUID tameMe, UUID mate, ItemStack food, Item saddle, double x0, boolean water) {
        int[] tries = {0};
        if (food == null) {
            // a grown wild predator is not tamed by hand (only an egg, a calf or a knockout): checked, then tamed directly
            STEPS.add(mc -> {
                DinosaurEntity d = server(mc, tameMe);
                ServerPlayer p = player(mc);
                if (d == null || p == null) {
                    return 1;
                }
                mc.getSingleplayerServer().execute(() -> {
                    p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(Items.COD, 64));
                    for (int i = 0; i < 20; i++) {
                        d.mobInteract(p, InteractionHand.MAIN_HAND);
                    }
                    REPORT.add("  a grown wild one offered fish by hand 20 times: " + (d.isTame() ? "TAMED (wrong)" : "not tamed (as designed: egg, calf or knockout)"));
                    d.tame(p);
                });
                return 20;
            });
        }
        if (food != null) STEPS.add(mc -> {
            DinosaurEntity d = server(mc, tameMe);
            ServerPlayer p = player(mc);
            if (d == null || p == null) {
                REPORT.add("  taming: NOT FOUND");
                return 1;
            }
            mc.getSingleplayerServer().execute(() -> {
                p.teleportTo(d.getX() + 2.0D, d.getY() + 1.0D, d.getZ());
                p.setItemInHand(InteractionHand.MAIN_HAND, food.copy());
            });
            return 10;
        });
        for (int i = 0; i < (food == null ? 0 : 260); i++) {
            STEPS.add(mc -> {
                DinosaurEntity d = server(mc, tameMe);
                ServerPlayer p = player(mc);
                if (d == null || p == null || d.isTame()) {
                    return 0;
                }
                tries[0]++;
                if (tries[0] == 1 || tries[0] == 60) {
                    REPORT.add(String.format(Locale.ROOT, "    bite %d: target %s, aggressive %s, ordered to sit %s, %.1f from the player",
                            tries[0], d.getTarget() == null ? "none" : d.getTarget().getType().toShortString() + (d.getTarget().isAlive() ? "" : " (dead)"),
                            d.isAggressive(), d.isOrderedToSit(), d.distanceTo(p)));
                }
                mc.getSingleplayerServer().execute(() -> {
                    if (p.getMainHandItem().isEmpty()) {
                        p.setItemInHand(InteractionHand.MAIN_HAND, food.copy());
                    }
                    d.mobInteract(p, InteractionHand.MAIN_HAND);
                });
                return 6;
            });
        }
        if (food != null) STEPS.add(mc -> {
            DinosaurEntity d = server(mc, tameMe);
            REPORT.add(String.format(Locale.ROOT, "  taming by hand with %s: %s after %d bites", food.getHoverName().getString(),
                    d != null && d.isTame() ? "TAMED" : "not tamed", tries[0]));
            return 20;
        });
        if (saddle != null) {
            STEPS.add(mc -> {
                DinosaurEntity d = server(mc, tameMe);
                ServerPlayer p = player(mc);
                if (d == null || p == null) {
                    return 1;
                }
                mc.getSingleplayerServer().execute(() -> {
                    p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(saddle));
                    d.mobInteract(p, InteractionHand.MAIN_HAND);
                });
                return 10;
            });
            STEPS.add(mc -> {
                DinosaurEntity d = server(mc, tameMe);
                ServerPlayer p = player(mc);
                boolean saddled = d != null && d.isSaddled();
                REPORT.add("  its own saddle put on: " + (saddled ? "SADDLED" : "not saddled"));
                if (saddled && p != null) {
                    mc.getSingleplayerServer().execute(() -> {
                        p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
                        p.startRiding(d, true);
                    });
                }
                return 20;
            });
            STEPS.add(mc -> {
                mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
                mc.options.hideGui = false;
                return 30;
            });
            STEPS.add(mc -> {
                DinosaurEntity d = server(mc, tameMe);
                ServerPlayer p = player(mc);
                if (d != null && p != null && p.getVehicle() == d) {
                    REPORT.add(String.format(Locale.ROOT, "  ridden: the rider's feet %.2f blocks over the animal's, %.2f ahead of its centre",
                            p.getY() - d.getY(), (p.getX() - d.getX()) * -Mth.sin(d.getYRot() * Mth.DEG_TO_RAD)
                                    + (p.getZ() - d.getZ()) * Mth.cos(d.getYRot() * Mth.DEG_TO_RAD)));
                } else {
                    REPORT.add("  ridden: NOT riding");
                }
                Screenshot.grab(mc.gameDirectory, "behavior_" + sp + "_ridden.png", mc.getMainRenderTarget(), msg -> {
                });
                return 10;
            });
            STEPS.add(mc -> {
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                mc.options.hideGui = true;
                ServerPlayer p = player(mc);
                if (p != null) {
                    mc.getSingleplayerServer().execute(p::stopRiding);
                }
                return 20;
            });
        }
        // breeding: both tamed by the player and in love
        int[] eggTicks = {0};
        STEPS.add(mc -> {
            DinosaurEntity a = server(mc, tameMe), b = server(mc, mate);
            ServerPlayer p = player(mc);
            if (a == null || b == null || p == null) {
                REPORT.add("  breeding: NOT FOUND");
                return 1;
            }
            // the owner stays by the pair, as a player feeding them would (tamed animals follow an owner who is far off)
            shotCooldown = 2400;
            mc.getSingleplayerServer().execute(() -> {
                p.teleportTo(a.getX() + 4.0D, a.getY() + 0.5D, a.getZ() + 4.0D);
                b.tame(p);
                a.setAge(0);
                b.setAge(0);
                b.teleportTo(a.getX() + 3.0D, a.getY(), a.getZ());
                a.setInLove(p);
                b.setInLove(p);
            });
            babiesBefore[0] = count(mc, sp, true);
            for (BlockPos old = findEgg(mc, sp, x0); old != null; old = findEgg(mc, sp, x0)) {
                OLD_EGGS.add(old);
                REPORT.add("    (an egg from an earlier run already at " + old.toShortString() + ")");
            }
            return 60;
        });
        STEPS.add(mc -> {
            DinosaurEntity a = server(mc, tameMe), b = server(mc, mate);
            if (a != null && b != null) {
                REPORT.add(String.format(Locale.ROOT, "    pair: in love %s/%s, tame %s/%s, female %s/%s, %.1f apart, in water %s/%s",
                        a.isInLove(), b.isInLove(), a.isTame(), b.isTame(), a.isFemale(), b.isFemale(), a.distanceTo(b), a.isInWater(), b.isInWater()));
            }
            return 1;
        });
        for (int i = 0; i < 60; i++) {
            int step = i;
            STEPS.add(mc -> {
                if (eggTicks[0] > 0 || count(mc, sp, true) > babiesBefore[0]) {
                    return 0;
                }
                if (step % 10 == 5) {
                    DinosaurEntity a = server(mc, tameMe), b = server(mc, mate);
                    if (a != null && b != null) {
                        REPORT.add(String.format(Locale.ROOT, "    after %d s: in love %s/%s, %.1f apart, on ground %s/%s, navigating %s/%s",
                                step, a.isInLove(), b.isInLove(), a.distanceTo(b), a.onGround(), b.onGround(),
                                !a.getNavigation().isDone(), !b.getNavigation().isDone()));
                    }
                }
                BlockPos egg = findEgg(mc, sp, x0);
                if (egg != null && !freshEgg(mc, egg)) {
                    egg = null;
                }
                if (egg != null) {
                    eggTicks[0] = 1;
                    eggAt[0] = egg;
                    REPORT.add("  breeding: an egg block laid at " + egg.toShortString());
                    look(mc.player, Vec3.atCenterOf(egg).add(2.5D, 2.5D, 2.5D), Vec3.atCenterOf(egg));
                    return 20;
                }
                return 20;
            });
        }
        STEPS.add(mc -> {
            shotCooldown = 0;
            if (eggAt[0] != null) {
                Screenshot.grab(mc.gameDirectory, "behavior_" + sp + "_egg.png", mc.getMainRenderTarget(), msg -> {
                });
                command(mc, "gamerule randomTickSpeed 4000");
            }
            return 5;
        });
        for (int i = 0; i < 60; i++) {
            STEPS.add(mc -> {
                if (eggAt[0] != null && !mc.getSingleplayerServer().overworld().getBlockState(eggAt[0]).getBlock().getDescriptionId().contains("_egg")) {
                    return 0;
                }
                return eggAt[0] == null ? 0 : 20;
            });
        }
        STEPS.add(mc -> {
            command(mc, "gamerule randomTickSpeed 3");
            ServerPlayer pl = player(mc);
            if (pl != null && pl.getInventory().items.stream().anyMatch(st -> st.getDescriptionId().contains(sp + "_egg"))) {
                REPORT.add("    an egg in the player's inventory (dropped as an item and picked up)");
            }
            for (Entity e : mc.getSingleplayerServer().overworld().getAllEntities()) {
                if (e instanceof net.minecraft.world.entity.item.ItemEntity it && it.getItem().getDescriptionId().contains(sp + "_egg")) {
                    REPORT.add("    an egg dropped as an item (no place to lay it) at " + it.blockPosition().toShortString());
                }
            }
            int babies = count(mc, sp, true);
            if (eggAt[0] != null) {
                BlockState st = mc.getSingleplayerServer().overworld().getBlockState(eggAt[0]);
                REPORT.add("  hatching: " + (babies > babiesBefore[0] ? "HATCHED, a calf next to the nest" : "not hatched yet (" + st + ")"));
            } else {
                REPORT.add("  breeding: " + (babies > babiesBefore[0] ? "a calf BORN ALIVE" : "no egg and no calf in 60 s"));
            }
            eggAt[0] = null;
            return 20;
        });
    }

    private static final BlockPos[] eggAt = new BlockPos[1];
    private static final int[] babiesBefore = {0};

    // ------------------------------------------------------------------ the loop

    private static void tick(Minecraft mc) {
        if (mc.level != null) {
            for (Entity e : mc.level.entitiesForRendering()) {
                if (e instanceof DinosaurEntity d) {
                    var c = d.getAnimatableInstanceCache().getManagerForId(d.getId()).getAnimationControllers().get("movement");
                    if (c != null && c.getCurrentAnimation() != null) {
                        String n = c.getCurrentAnimation().animation().name();
                        String move = n.substring(n.lastIndexOf('.') + 1);
                        if (MOVES.computeIfAbsent(d.speciesId(), k -> ConcurrentHashMap.newKeySet()).add(move)
                                && SHOT.add(d.speciesId() + "_move_" + move)) {
                            NEW.add(new Object[]{d.getId(), d.speciesId() + "_move_" + move});
                        }
                    }
                }
            }
            if (shotCooldown > 0) {
                shotCooldown--;
            } else if (!NEW.isEmpty() && mc.player != null && mc.player.getVehicle() == null) {
                Object[] ev = NEW.poll();
                Entity e = mc.level.getEntity((Integer) ev[0]);
                if (e instanceof DinosaurEntity d) {
                    double size = Math.max(d.getBbWidth(), d.getBbHeight()) * 2.5D + 6.0D;
                    float yaw = d.yBodyRot * Mth.DEG_TO_RAD;
                    Vec3 c = d.position().add(0, d.getBbHeight() * 0.5D, 0);
                    look(mc.player, c.add(-Mth.cos(yaw) * size * 0.8D, size * 0.45D, -Mth.sin(yaw) * size * 0.8D + Mth.cos(yaw) * size * 0.3D), c);
                    pendingShot = (String) ev[1];
                    pendingIn = 8;
                    shotCooldown = 30;
                }
            }
            if (pendingShot != null && --pendingIn <= 0) {
                Screenshot.grab(mc.gameDirectory, "behavior_" + pendingShot + ".png", mc.getMainRenderTarget(), msg -> {
                });
                pendingShot = null;
                if (watchAt != null) {
                    look(mc.player, watchAt.add(0.0D, watchSize * 0.5D, -watchSize * 0.9D), watchAt);
                }
            }
        }
        if (wait > 0) {
            wait--;
            return;
        }
        Step s = STEPS.poll();
        if (s != null) {
            int w = s.run(mc);
            if (w < 0) {
                STEPS.addFirst(s);
                wait = 20;
            } else {
                wait = w;
            }
        }
    }

    private static String pendingShot;
    private static int pendingIn;
    private static Vec3 watchAt;
    private static double watchSize;

    // ------------------------------------------------------------------ helpers

    private static UUID id() {
        // fresh every run: a creature of an earlier run may still be saved in the world with the same id
        return new UUID(0x7E55B0A100000000L ^ RUN, ++serial);
    }

    private static String uuidNbt(UUID id) {
        return String.format(Locale.ROOT, "[I;%d,%d,%d,%d]", (int) (id.getMostSignificantBits() >> 32), (int) id.getMostSignificantBits(),
                (int) (id.getLeastSignificantBits() >> 32), (int) id.getLeastSignificantBits());
    }

    private static void summon(Minecraft mc, String sp, double x, double y, double z, UUID id, String extra) {
        command(mc, String.format(Locale.ROOT, "summon terrassic:%s %.2f %.2f %.2f {UUID:%s,PersistenceRequired:1b,Size:1f,BirthSize:1f%s}",
                sp, x, y, z, uuidNbt(id), extra.isEmpty() ? "" : "," + extra));
    }

    private static String fill(double x0, double y0, double z0, double x1, double y1, double z1, String block) {
        return String.format(Locale.ROOT, "fill %d %d %d %d %d %d %s", (int) Math.floor(x0), (int) y0, (int) z0, (int) Math.floor(x1), (int) y1, (int) z1, block);
    }

    /** grass from end to end, the air cleared above it */
    private static void clear(Minecraft mc, double x0, int r) {
        command(mc, "forceload add " + (int) (x0 - r) + " " + (-r) + " " + (int) (x0 + r) + " " + r);
        // in slices: a /fill over 32768 blocks fails silently (and left the eggs of earlier runs in the arena)
        for (int z = -r; z <= r; z += 8) {
            command(mc, fill(x0 - r, Y, z, x0 + r, Y + 12, Math.min(r, z + 7), "minecraft:air"));
        }
        command(mc, fill(x0 - r, Y - 1, -r, x0 + r, Y - 1, r, "minecraft:grass_block"));
    }

    private static void watch(Minecraft mc, Vec3 at, double size) {
        watchAt = at;
        watchSize = size;
        look(mc.player, at.add(0.0D, size * 0.5D, -size * 0.9D), at);
        serverTp(mc);
    }

    private static DinosaurEntity server(Minecraft mc, UUID id) {
        MinecraftServer s = mc.getSingleplayerServer();
        return s != null && s.overworld().getEntity(id) instanceof DinosaurEntity d ? d : null;
    }

    private static Entity serverAny(Minecraft mc, UUID id) {
        MinecraftServer s = mc.getSingleplayerServer();
        return s == null ? null : s.overworld().getEntity(id);
    }

    private static ServerPlayer player(Minecraft mc) {
        MinecraftServer s = mc.getSingleplayerServer();
        return s == null || mc.player == null ? null : s.getPlayerList().getPlayer(mc.player.getUUID());
    }

    private static int count(Minecraft mc, String sp, boolean babies) {
        ServerLevel l = mc.getSingleplayerServer().overworld();
        int n = 0;
        for (Entity e : l.getAllEntities()) {
            if (e instanceof DinosaurEntity d && d.speciesId().equals(sp) && d.isAlive() && d.isBaby() == babies) {
                n++;
            }
        }
        return n;
    }

    /** Not an egg left in the world by an earlier run: its block was not there when the pair fell in love. */
    private static boolean freshEgg(Minecraft mc, BlockPos pos) {
        return !OLD_EGGS.contains(pos);
    }

    private static final Set<BlockPos> OLD_EGGS = ConcurrentHashMap.newKeySet();

    private static BlockPos findEgg(Minecraft mc, String sp, double x0) {
        ServerLevel l = mc.getSingleplayerServer().overworld();
        // wide: a pair can wander or flee 30 blocks from the arena centre before it lays
        for (BlockPos p : BlockPos.betweenClosed((int) x0 - 48, (int) Y - 5, -48, (int) x0 + 48, (int) Y + 10, 48)) {
            if (l.getBlockState(p).getBlock().getDescriptionId().equals("block.terrassic." + sp + "_egg") && !OLD_EGGS.contains(p)) {
                return p.immutable();
            }
        }
        return null;
    }

    private static void look(LocalPlayer player, Vec3 eye, Vec3 at) {
        Vec3 d = at.subtract(eye);
        float yRot = (float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90.0F;
        float xRot = (float) -(Mth.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * Mth.RAD_TO_DEG);
        player.getAbilities().flying = true;
        player.moveTo(eye.x, eye.y - player.getEyeHeight(), eye.z, yRot, xRot);
        player.setYHeadRot(yRot);
        player.setDeltaMovement(Vec3.ZERO);
        player.xo = player.getX();
        player.yo = player.getY();
        player.zo = player.getZ();
        player.xRotO = xRot;
        player.yRotO = yRot;
    }

    private static void serverTp(Minecraft mc) {
        LocalPlayer p = mc.player;
        command(mc, String.format(Locale.ROOT, "tp %s %.4f %.4f %.4f %.3f %.3f", p.getGameProfile().getName(),
                p.getX(), p.getY(), p.getZ(), p.getYRot(), p.getXRot()));
    }

    private static void command(Minecraft mc, String command) {
        MinecraftServer server = mc.getSingleplayerServer();
        server.execute(() -> server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), command));
    }
}
