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
            STEPS.add(mc -> {
                if (eggTicks[0] > 0 || count(mc, sp, true) > babiesBefore[0]) {
                    return 0;
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
        for (BlockPos p : BlockPos.betweenClosed((int) x0 - 30, (int) Y - 5, -30, (int) x0 + 30, (int) Y + 10, 30)) {
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
