package com.terrassic.client.dev;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.entity.parts.DinoPart;
import com.terrassic.entity.parts.DinoParts;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Deque;
import java.util.List;
import java.util.Locale;

/**
 * Development check of the hit parts in the real client (1.7, docs/PLANO_PARTES.md). Off unless the client is started
 * with the environment variable {@code TERRASSIC_PARTS_SHOWCASE=1} and a world open (e.g. {@code --quickPlaySingleplayer}).
 * For every species with parts, facing straight and turned 45 degrees: F3+B screenshots from the side and from above,
 * the vanilla crosshair pick aimed along the whole body line (part centres and every 10 cm between them, from both
 * sides and from above) to find gaps, and on the straight one a real attack with the same axe on the snout, the body
 * and the tail tip. Writes {@code terrassic_parts_report.txt} in the game directory and closes the game.
 */
public final class PartsShowcase {
    private static final String[] SPECIES = {"tyrannosaurus", "carnotaurus", "giganotosaurus", "spinosaurus", "velociraptor",
            "triceratops", "protoceratops", "ankylosaurus", "pachycephalosaurus", "parasaurolophus", "gallimimus",
            "pteranodon", "mosasaurus"};
    private static final int[] YAWS = {0, 45};
    private static final double Y = -60.0D;

    private static final Deque<Step> STEPS = new ArrayDeque<>();
    private static final List<String> REPORT = new ArrayList<>();
    private static int wait;
    private static boolean started;
    private static int totalMisses;
    private static int totalPicks;

    private PartsShowcase() {
    }

    /** A step runs once its wait is over; it may ask to wait more before the next one. */
    private interface Step {
        int run(Minecraft mc);
    }

    public static void init() {
        if (!"1".equals(System.getenv("TERRASSIC_PARTS_SHOWCASE"))) {
            return;
        }
        ClientTickEvent.CLIENT_POST.register(PartsShowcase::tick);
        // the model in motion is measured once a frame is drawn: the parts were placed for that frame before the
        // crosshair was aimed (mixin.client.PartFrameMixin) and GeckoLib has just drawn the bones
        dev.architectury.event.events.client.ClientGuiEvent.RENDER_HUD.register((graphics, partialTick) -> {
            Measuring m = measuring;
            Minecraft mc = Minecraft.getInstance();
            if (m != null && m.dino != null && !m.dino.isRemoved() && mc.level != null) {
                double before = m.worst[m.slot];
                long farBefore = m.byZone.values().stream().mapToLong(z -> z[2]).sum();
                // GeckoLib places the bones at the tick position, the model is drawn at the frame's position
                Vec3 drawn = new Vec3(Mth.lerp(partialTick, m.dino.xo, m.dino.getX()), Mth.lerp(partialTick, m.dino.yo, m.dino.getY()),
                        Mth.lerp(partialTick, m.dino.zo, m.dino.getZ()));
                Vec3 shift = drawn.subtract(m.dino.position());
                software.bernie.geckolib.cache.object.BakedGeoModel bm = model(mc, m.dino);
                if (bm == null || bm.topLevelBones().isEmpty()
                        || bm.topLevelBones().get(0).getWorldPosition().distanceSquared(m.dino.getX(), m.dino.getY(), m.dino.getZ()) > 9.0D) {
                    return;   // not drawn this frame (out of view): its bones are from another frame
                }
                measure(mc, m.dino, m.counts, m.worst, m.where, m.slot, m.byZone, shift);
                m.frames[0]++;
                if (m.byZone.values().stream().mapToLong(z -> z[2]).sum() > farBefore) {
                    m.frames[1]++;
                    m.playing.merge(playing(m.dino), 1, Integer::sum);
                }
                if (m.worst[m.slot] > before) {
                    m.where[m.slot] += String.format(Locale.ROOT, " @frame%d turning %.0f deg/tick", m.frames[0],
                            Math.abs(Mth.wrapDegrees(m.dino.yBodyRot - m.dino.yBodyRotO)));
                }
            }
        });
    }

    private static void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null || mc.getSingleplayerServer() == null) {
            return;
        }
        if (!started) {
            started = true;
            plan();
            wait = 60;
        }
        if (wait > 0) {
            wait--;
            return;
        }
        Step step = STEPS.poll();
        if (step == null) {
            return;
        }
        try {
            wait = step.run(mc);
        } catch (RuntimeException e) {
            REPORT.add("ERROR " + e);
            wait = 1;
        }
    }

    private static void plan() {
        STEPS.add(mc -> {
            for (String c : new String[]{"gamerule doMobSpawning false", "gamerule doDaylightCycle false", "time set noon",
                    "weather clear", "gamemode creative @a", "tp @e[type=!player] 0 -400 0", "difficulty peaceful",
                    "item replace entity @a weapon.mainhand with minecraft:stone_axe"}) {
                command(mc, c);
            }
            mc.options.hideGui = true;
            mc.getEntityRenderDispatcher().setRenderHitBoxes(true);
            mc.player.getAbilities().flying = true;
            REPORT.add("Terrassic hit parts in the real client: picks aimed along the body line, attacks with a stone axe");
            return 20;
        });
        // TERRASSIC_PARTS_PHASES: any of "still", "flight", "moving" (default all); TERRASSIC_PARTS_SPECIES: a comma list
        String phases = System.getenv().getOrDefault("TERRASSIC_PARTS_PHASES", "still,flight,moving");
        String only = System.getenv("TERRASSIC_PARTS_SPECIES");
        List<String> species = only == null ? List.of(SPECIES) : List.of(only.split(","));
        if (phases.contains("still")) {
            for (String sp : species) {
                for (int yaw : YAWS) {
                    planSpecies(sp, yaw);
                }
            }
        }
        if (phases.contains("flight")) {
            planFlight();
        }
        if (phases.contains("feedback")) {
            planFeedback();
        }
        if (phases.contains("bettercombat")) {
            planBetterCombat();
        }
        if (phases.contains("moving")) {
            for (String sp : species) {
                planAnimated(sp);
            }
        }
        STEPS.add(mc -> {
            REPORT.add(String.format(Locale.ROOT, "TOTAL picks %d, misses %d", totalPicks, totalMisses));
            try {
                Files.write(mc.gameDirectory.toPath().resolve("terrassic_parts_report.txt"), REPORT, StandardCharsets.UTF_8);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
            return 10;
        });
        STEPS.add(mc -> {
            mc.stop();
            return 1000;
        });
    }

    private static int serial;
    private static volatile Measuring measuring;

    /** What the frame measurement adds up for one creature in motion. */
    private static final class Measuring {
        DinosaurEntity dino;
        int slot;
        final long[] counts = new long[4];
        final java.util.Map<String, long[]> byZone = new java.util.TreeMap<>();
        final int[] frames = new int[2];
        final double[] worst = new double[2];
        final String[] where = {"", ""};
        final java.util.Map<String, Integer> playing = new java.util.TreeMap<>();
    }

    /** The animations GeckoLib is playing on the creature now, one per controller. */
    private static String playing(DinosaurEntity dino) {
        StringBuilder out = new StringBuilder();
        dino.getAnimatableInstanceCache().getManagerForId(dino.getId()).getAnimationControllers().forEach((name, c) -> {
            if (c.getCurrentAnimation() != null) {
                String a = c.getCurrentAnimation().animation().name();
                out.append(a.substring(a.lastIndexOf('.') + 1)).append(' ');
            }
        });
        return out.toString().trim();
    }

    private static void planSpecies(String species, int yaw) {
        DinosaurEntity[] dino = new DinosaurEntity[1];
        java.util.UUID id = new java.util.UUID(0x7E55A51C00000000L, ++serial);
        STEPS.add(mc -> {
            // out of the world rather than killed: a killed creature lies dying (and leaves a carcass) for a while
            command(mc, "tp @e[type=!player] 0 -400 0");
            command(mc, String.format(Locale.ROOT, "summon terrassic:%s 0.5 %s 0.5 {NoAI:1b,PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                    + "UUID:[I;%d,%d,%d,%d],Rotation:[%df,0f],attributes:[{id:\"minecraft:generic.armor\",base:0d}]}", species, Y,
                    (int) (id.getMostSignificantBits() >> 32), (int) id.getMostSignificantBits(),
                    (int) (id.getLeastSignificantBits() >> 32), (int) id.getLeastSignificantBits(), yaw));
            park(mc.player);
            return 30;
        });
        STEPS.add(mc -> {
            dino[0] = null;
            for (Entity e : mc.level.entitiesForRendering()) {
                if (e instanceof DinosaurEntity d && id.equals(d.getUUID())) {
                    dino[0] = d;
                }
            }
            if (dino[0] == null) {
                REPORT.add(species + " yaw " + yaw + ": NOT FOUND on the client");
                return 1;
            }
            frame(mc, dino[0], false);
            return 15;
        });
        STEPS.add(mc -> shot(mc, dino[0], species + "_" + yaw + "_side"));
        STEPS.add(mc -> {
            if (dino[0] != null) {
                frame(mc, dino[0], true);
            }
            return 15;
        });
        STEPS.add(mc -> shot(mc, dino[0], species + "_" + yaw + "_top"));
        STEPS.add(mc -> {
            if (dino[0] != null) {
                picks(mc, dino[0], species, yaw);
            }
            return 1;
        });
        if (yaw == 0) {
            for (DinoPart.Kind kind : new DinoPart.Kind[]{null, DinoPart.Kind.BODY, DinoPart.Kind.HEAD, DinoPart.Kind.TAIL}) {
                float[] before = new float[1];
                Entity[] aimed = new Entity[1];
                Entity[] hitOf = new Entity[1];
                String[] note = {""};
                STEPS.add(mc -> {
                    if (dino[0] == null) {
                        return 1;
                    }
                    aimed[0] = aimAt(mc, dino[0], kind);
                    serverTp(mc);
                    return 8;
                });
                STEPS.add(mc -> {
                    if (dino[0] == null || aimed[0] == null) {
                        return 1;
                    }
                    aimed[0] = aimAt(mc, dino[0], kind);   // the same place again, in case the player drifted
                    Entity hit = pick(mc);
                    Entity server = serverDino(mc, dino[0]);
                    before[0] = server instanceof DinosaurEntity d ? d.getHealth() : 0.0F;
                    // the creature's own box sits inside the body piece: aiming at it, the body piece is hit first
                    boolean right = kind == null ? hit != null && DinoParts.owner(hit) == dino[0] : hit == aimed[0];
                    if (!right) {
                        REPORT.add(String.format(Locale.ROOT, "  attack %s: crosshair on %s, not on the aimed part", label(kind), describe(hit)));
                        return 1;
                    }
                    hitOf[0] = hit;
                    MinecraftServer srv = mc.getSingleplayerServer();
                    net.minecraft.server.level.ServerPlayer sp = srv.getPlayerList().getPlayer(mc.player.getUUID());
                    Entity onServer = srv.overworld().getEntityOrPart(hit.getId());
                    note[0] = String.format(Locale.ROOT, " [server: player eye %.1f blocks from the client's, target %s at %.2f from the eye, invulnerable %d, strength %.2f]",
                            sp.getEyePosition().distanceTo(mc.player.getEyePosition()), onServer == null ? "missing" : describe(onServer),
                            onServer == null ? -1.0D : Math.sqrt(onServer.getBoundingBox().distanceToSqr(sp.getEyePosition())),
                            server instanceof DinosaurEntity d0 ? d0.invulnerableTime : -1, sp.getAttackStrengthScale(0.5F));
                    mc.gameMode.attack(mc.player, hit);
                    mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                    return 30;
                });
                STEPS.add(mc -> {
                    if (dino[0] == null || aimed[0] == null || hitOf[0] == null) {
                        return 1;
                    }
                    Entity server = serverDino(mc, dino[0]);
                    float after = server instanceof DinosaurEntity d ? d.getHealth() : 0.0F;
                    REPORT.add(String.format(Locale.ROOT, "  attack %-9s -> %s: %.3f damage%s", label(kind), describe(hitOf[0]), before[0] - after, note[0]));
                    return 5;
                });
            }
        }
    }

    // ------------------------------------------------------------------ the model in motion

    /** The creature with its AI on for 10 s (it idles, strolls, turns its head), then provoked by the player for 10 s
     *  (it runs, flees or fights). Every tick every vertex of the model as GeckoLib drew it (bones and cubes in the real
     *  pose of the animation) is checked against the part boxes and the collision box. */
    private static void planAnimated(String species) {
        DinosaurEntity[] dino = new DinosaurEntity[1];
        java.util.UUID id = new java.util.UUID(0x7E55A51D00000000L, ++serial);
        Measuring m = new Measuring();
        STEPS.add(mc -> {
            command(mc, "tp @e[type=!player] 0 -400 0");
            command(mc, String.format(Locale.ROOT, "summon terrassic:%s 0.5 %s 0.5 {PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                    + "UUID:[I;%d,%d,%d,%d]}", species, Y, (int) (id.getMostSignificantBits() >> 32), (int) id.getMostSignificantBits(),
                    (int) (id.getLeastSignificantBits() >> 32), (int) id.getLeastSignificantBits()));
            mc.options.hideGui = false;   // the HUD event is where the frame is measured
            return 20;
        });
        STEPS.add(mc -> {
            dino[0] = byId(mc, id);
            if (dino[0] != null) {
                track(mc, dino[0]);
                m.dino = dino[0];
                measuring = m;
            }
            return 2;
        });
        for (int t = 0; t < 400; t++) {
            int tick = t;
            STEPS.add(mc -> {
                if (dino[0] == null || dino[0].isRemoved()) {
                    return 0;
                }
                if (tick == 200) {
                    command(mc, "damage @e[type=terrassic:" + species + ",limit=1] 1 minecraft:player_attack by "
                            + mc.player.getGameProfile().getName());
                }
                // watch it from 12 blocks plus its size, a little above, so it is drawn every frame
                AABB all = dino[0].getBoundingBox().minmax(dino[0].partsBounds());
                double size = Math.max(all.getXsize(), Math.max(all.getYsize(), all.getZsize()));
                Vec3 c = all.getCenter();
                look(mc.player, c.add(new Vec3(0.0D, 0.6D, 1.0D).normalize().scale(size + 12.0D)), c);
                if (tick % 20 == 0) {
                    serverTp(mc);
                }
                Entity server = serverDino(mc, dino[0]);
                m.slot = tick >= 200 && server instanceof net.minecraft.world.entity.Mob mob && mob.getTarget() != null ? 1 : 0;
                return 0;
            });
        }
        STEPS.add(mc -> {
            measuring = null;
            mc.options.hideGui = true;
            REPORT.add(String.format(Locale.ROOT, "%s moving, %d frames measured: %.2f%% of vertices outside the boxes; a vertex more than 0.5 m out in %d frames (%.1f%%)",
                    species, m.frames[0], 100.0D * (m.counts[1] + m.counts[3]) / Math.max(1, m.counts[0] + m.counts[2]), m.frames[1],
                    100.0D * m.frames[1] / Math.max(1, m.frames[0])));
            for (java.util.Map.Entry<String, long[]> e : m.byZone.entrySet()) {
                long[] z = e.getValue();
                REPORT.add(String.format(Locale.ROOT, "    %-5s more than 0.25 m out %.2f%%, more than 0.5 m %.2f%%", e.getKey(),
                        100.0D * z[1] / Math.max(1, z[0]), 100.0D * z[2] / Math.max(1, z[0])));
            }
            REPORT.add(String.format(Locale.ROOT, "    worst calm %.2f m (%s); worst fighting %.2f m (%s)", m.worst[0], m.where[0],
                    m.worst[1], m.where[1]));
            if (!m.playing.isEmpty()) {
                REPORT.add("    playing in the frames with a vertex more than 0.5 m out: " + m.playing);
            }
            return 1;
        });
    }

    /** head (and neck), tail, wing or body, from the bone and its parents' names (as tools/javagen/parts.py). */
    private static String zone(software.bernie.geckolib.cache.object.GeoBone bone) {
        for (software.bernie.geckolib.cache.object.GeoBone b = bone; b != null; b = b.getParent()) {
            String n = b.getName();
            if (n.equals("head") || n.startsWith("neck") || n.equals("throat")) {
                return "head";
            }
            if (n.startsWith("tail")) {
                return "tail";
            }
            if (n.startsWith("mem_")) {
                return "wing";
            }
        }
        return "body";
    }

    private static DinosaurEntity byId(Minecraft mc, java.util.UUID id) {
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof DinosaurEntity d && id.equals(d.getUUID())) {
                return d;
            }
        }
        return null;
    }

    private static software.bernie.geckolib.cache.object.BakedGeoModel model(Minecraft mc, DinosaurEntity dino) {
        if (mc.getEntityRenderDispatcher().getRenderer(dino) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> r) {
            @SuppressWarnings("unchecked")
            software.bernie.geckolib.model.GeoModel<DinosaurEntity> m = (software.bernie.geckolib.model.GeoModel<DinosaurEntity>) r.getGeoModel();
            return m.getBakedModel(m.getModelResource(dino));
        }
        return null;
    }

    private static void track(Minecraft mc, DinosaurEntity dino) {
        software.bernie.geckolib.cache.object.BakedGeoModel model = model(mc, dino);
        if (model != null) {
            Deque<software.bernie.geckolib.cache.object.GeoBone> todo = new ArrayDeque<>(model.topLevelBones());
            while (!todo.isEmpty()) {
                software.bernie.geckolib.cache.object.GeoBone b = todo.poll();
                b.setTrackingMatrices(true);
                todo.addAll(b.getChildBones());
            }
        }
    }

    /** Every vertex of every shown cube where it was last drawn, against the parts and the collision box. */
    private static void measure(Minecraft mc, DinosaurEntity dino, long[] counts, double[] worst, String[] where, int slot,
                                java.util.Map<String, long[]> byZone, Vec3 shift) {
        software.bernie.geckolib.cache.object.BakedGeoModel model = model(mc, dino);
        if (model == null) {
            return;
        }
        List<AABB> boxes = new ArrayList<>();
        boxes.add(dino.getBoundingBox().inflate(0.05D));
        for (DinoPart p : dino.parts()) {
            if (p.enabled()) {
                boxes.add(p.getBoundingBox().inflate(0.05D));
            }
        }
        Deque<software.bernie.geckolib.cache.object.GeoBone> todo = new ArrayDeque<>(model.topLevelBones());
        org.joml.Vector4f v = new org.joml.Vector4f();
        while (!todo.isEmpty()) {
            software.bernie.geckolib.cache.object.GeoBone b = todo.poll();
            if (b.isHidden()) {
                continue;
            }
            todo.addAll(b.getChildBones());
            long[] zc = byZone.computeIfAbsent(zone(b), k -> new long[3]);
            // GeckoLib 4 builds the world matrix by adding translation matrices (RenderUtils.translateMatrix uses add): the
            // translation is right, the diagonal carries 2 too many (scale 3.02 and w 3 for a creature of scale 1.02)
            org.joml.Matrix4f world = new org.joml.Matrix4f(b.getWorldSpaceMatrix());
            world.m00(world.m00() - 2.0F).m11(world.m11() - 2.0F).m22(world.m22() - 2.0F).m33(world.m33() - 2.0F);
            for (software.bernie.geckolib.cache.object.GeoCube cube : b.getCubes()) {
                com.mojang.blaze3d.vertex.PoseStack ps = new com.mojang.blaze3d.vertex.PoseStack();
                ps.last().pose().set(world);
                // GeckoLib keeps the bone's matrix before its last step (back from the pivot); the cubes are drawn after it
                software.bernie.geckolib.util.RenderUtils.translateAwayFromPivotPoint(ps, b);
                software.bernie.geckolib.util.RenderUtils.translateToPivotPoint(ps, cube);
                software.bernie.geckolib.util.RenderUtils.rotateMatrixAroundCube(ps, cube);
                software.bernie.geckolib.util.RenderUtils.translateAwayFromPivotPoint(ps, cube);
                org.joml.Matrix4f m = ps.last().pose();
                for (software.bernie.geckolib.cache.object.GeoQuad q : cube.quads()) {
                    if (q == null) {
                        continue;
                    }
                    for (software.bernie.geckolib.cache.object.GeoVertex vx : q.vertices()) {
                        m.transform(v.set(vx.position().x(), vx.position().y(), vx.position().z(), 1.0F));
                        double x = v.x() + shift.x, y = v.y() + shift.y, z = v.z() + shift.z;
                        counts[slot * 2]++;
                        zc[0]++;
                        double best = Double.MAX_VALUE;
                        for (AABB box : boxes) {
                            double dx = Math.max(Math.max(box.minX - x, x - box.maxX), 0.0D);
                            double dy = Math.max(Math.max(box.minY - y, y - box.maxY), 0.0D);
                            double dz = Math.max(Math.max(box.minZ - z, z - box.maxZ), 0.0D);
                            best = Math.min(best, Math.sqrt(dx * dx + dy * dy + dz * dz));
                            if (best == 0.0D) {
                                break;
                            }
                        }
                        if (best > 0.25D) {
                            zc[1]++;
                        }
                        if (best > 0.5D) {
                            zc[2]++;
                        }
                        if (best > 0.0D) {
                            counts[slot * 2 + 1]++;
                            if (best > worst[slot]) {
                                worst[slot] = best;
                                where[slot] = b.getName() + " " + zone(b);
                            }
                        }
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------ the player feedback of 1.7 (docs/FEEDBACK_1_7.md)

    /** The whistle heard at 96 blocks (not 100), the "My dinos" list, the tracking arrow, every spread of the Pocket
     *  Guide, and how much food each remade species takes to tame. */
    private static void planFeedback() {
        java.util.UUID near = new java.util.UUID(0x7E55A52200000000L, ++serial);
        java.util.UUID far = new java.util.UUID(0x7E55A52300000000L, ++serial);
        STEPS.add(mc -> {
            command(mc, "tp @e[type=!player] 0 -400 0");
            int[] o = uuidInts(mc.player.getUUID());
            for (Object[] d : new Object[][]{{near, 90}, {far, 100}}) {
                int[] u = uuidInts((java.util.UUID) d[0]);
                command(mc, String.format(Locale.ROOT, "summon terrassic:velociraptor %d %s 0.5 {PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                        + "UUID:[I;%d,%d,%d,%d],Owner:[I;%d,%d,%d,%d],Sitting:1b,CustomName:'\"%s\"'}", (Integer) d[1], Y,
                        u[0], u[1], u[2], u[3], o[0], o[1], o[2], o[3], d[0] == near ? "Perto" : "Longe"));
            }
            look(mc.player, new Vec3(0.5D, Y + 1.62D, 0.5D), new Vec3(10.0D, Y + 1.0D, 0.5D));
            serverTp(mc);
            return 60;
        });
        double[] start = new double[1];
        STEPS.add(mc -> {
            MinecraftServer srv = mc.getSingleplayerServer();
            net.minecraft.server.level.ServerPlayer sp = srv.getPlayerList().getPlayer(mc.player.getUUID());
            List<DinosaurEntity> hearing = com.terrassic.entity.Whistle.hearing(sp);
            boolean hearsNear = hearing.stream().anyMatch(d -> d.getUUID().equals(near));
            boolean hearsFar = hearing.stream().anyMatch(d -> d.getUUID().equals(far));
            Entity n = srv.overworld().getEntity(near);
            start[0] = n == null ? -1.0D : n.distanceTo(sp);
            REPORT.add(String.format(Locale.ROOT, "feedback whistle: the tamed raptor at %.0f blocks %s, the one at %.0f blocks %s (range %.0f)",
                    start[0], hearsNear ? "hears it" : "does NOT hear it",
                    srv.overworld().getEntity(far) == null ? -1.0D : srv.overworld().getEntity(far).distanceTo(sp),
                    hearsFar ? "HEARS it" : "does not", com.terrassic.entity.Whistle.RANGE));
            command(mc, "execute as " + mc.player.getGameProfile().getName() + " run terrassic apito follow");
            return 400;
        });
        STEPS.add(mc -> {
            MinecraftServer srv = mc.getSingleplayerServer();
            Entity n = srv.overworld().getEntity(near);
            Entity f = srv.overworld().getEntity(far);
            net.minecraft.server.level.ServerPlayer sp = srv.getPlayerList().getPlayer(mc.player.getUUID());
            REPORT.add(String.format(Locale.ROOT, "feedback whistle \"follow\": after 20 s the near one is %.0f blocks away (was %.0f); the far one %.0f",
                    n == null ? -1.0D : n.distanceTo(sp), start[0], f == null ? -1.0D : f.distanceTo(sp)));
            mc.options.hideGui = true;
            com.terrassic.client.MyDinosScreen.open();
            return 60;
        });
        STEPS.add(mc -> {
            Screenshot.grab(mc.gameDirectory, "feedback_my_dinos.png", mc.getMainRenderTarget(), msg -> {
            });
            return 5;
        });
        STEPS.add(mc -> {
            mc.setScreen(null);
            try {
                java.lang.reflect.Method toggle = Class.forName("com.terrassic.client.DinoTracker").getDeclaredMethod("toggle", java.util.UUID.class);
                toggle.setAccessible(true);
                toggle.invoke(null, far);
            } catch (ReflectiveOperationException e) {
                REPORT.add("feedback tracker: " + e);
            }
            mc.options.hideGui = false;
            look(mc.player, mc.player.getEyePosition(), mc.player.getEyePosition().add(-1.0D, 0.0D, 0.0D));   // facing away
            return 120;
        });
        STEPS.add(mc -> {
            Screenshot.grab(mc.gameDirectory, "feedback_tracker.png", mc.getMainRenderTarget(), msg -> {
            });
            return 5;
        });
        STEPS.add(mc -> {
            mc.options.hideGui = true;
            com.terrassic.client.PocketGuideScreen.open();
            return 20;
        });
        for (int i = 0; i < 40; i++) {
            int page = i;
            STEPS.add(mc -> {
                Screenshot.grab(mc.gameDirectory, String.format(Locale.ROOT, "feedback_guide_%02d.png", page), mc.getMainRenderTarget(), msg -> {
                });
                return 3;
            });
            STEPS.add(mc -> {
                if (mc.screen != null) {
                    mc.screen.keyPressed(org.lwjgl.glfw.GLFW.GLFW_KEY_RIGHT, 0, 0);
                }
                return 6;
            });
        }
        STEPS.add(mc -> {
            mc.setScreen(null);
            StringBuilder goals = new StringBuilder("feedback taming goal (portions of food; carnivores in meat):");
            for (String sp : SPECIES) {
                Entity e = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.get(new net.minecraft.resources.ResourceLocation("terrassic", sp))
                        .create(mc.getSingleplayerServer().overworld());
                if (e instanceof DinosaurEntity d) {
                    goals.append(String.format(Locale.ROOT, " %s %d (%s, base health %.0f)", sp, d.foodGoal(), d.isHunter() ? "carnivore" : "other",
                            d.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).getBaseValue()));
                    e.discard();
                }
            }
            REPORT.add(goals.toString());
            return 5;
        });
    }

    // ------------------------------------------------------------------ Better Combat

    /** With Better Combat installed (./gradlew :fabric:runClient -PbetterCombat): the mod's weapons have its attributes
     *  (the clubs were the player's request), and its own attack (the click it takes over) lands on the head, the body
     *  and the tail with the parts' multipliers; a sweep spares the player's own tamed creature. */
    private static void planBetterCombat() {
        STEPS.add(mc -> {
            Class<?> registry;
            try {
                registry = Class.forName("net.bettercombat.logic.WeaponRegistry");
            } catch (ClassNotFoundException e) {
                REPORT.add("better combat: NOT INSTALLED (run with -PbetterCombat)");
                return 1;
            }
            for (String id : new String[]{"bone_club", "tail_club", "flint_spear", "horn_spear", "flint_knife", "rex_tooth_dagger",
                    "flint_hatchet"}) {
                net.minecraft.world.item.Item item = net.minecraft.core.registries.BuiltInRegistries.ITEM.get(
                        new net.minecraft.resources.ResourceLocation("terrassic", id));
                try {
                    Object a = registry.getMethod("getAttributes", net.minecraft.world.item.ItemStack.class)
                            .invoke(null, new net.minecraft.world.item.ItemStack(item));
                    REPORT.add(a == null ? "  better combat " + id + ": NO ATTRIBUTES"
                            : String.format(Locale.ROOT, "  better combat %s: %s, range %.1f, two-handed %s, %d attacks", id,
                            a.getClass().getMethod("category").invoke(a), (Double) a.getClass().getMethod("attackRange").invoke(a),
                            a.getClass().getMethod("isTwoHanded").invoke(a),
                            ((Object[]) a.getClass().getMethod("attacks").invoke(a)).length));
                } catch (ReflectiveOperationException e) {
                    REPORT.add("  better combat " + id + ": " + e);
                }
            }
            return 1;
        });
        for (String weapon : new String[]{"tail_club", "bone_club"}) {
            DinosaurEntity[] dino = new DinosaurEntity[1];
            java.util.UUID id = new java.util.UUID(0x7E55A51F00000000L, ++serial);
            STEPS.add(mc -> {
                command(mc, "tp @e[type=!player] 0 -400 0");
                command(mc, "item replace entity @a weapon.mainhand with terrassic:" + weapon);
                command(mc, String.format(Locale.ROOT, "summon terrassic:tyrannosaurus 0.5 %s 0.5 {NoAI:1b,PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                        + "UUID:[I;%d,%d,%d,%d],Rotation:[0f,0f],Attributes:[{Name:\"minecraft:generic.armor\",Base:0d}]}", Y,
                        (int) (id.getMostSignificantBits() >> 32), (int) id.getMostSignificantBits(),
                        (int) (id.getLeastSignificantBits() >> 32), (int) id.getLeastSignificantBits()));
                return 30;
            });
            STEPS.add(mc -> {
                dino[0] = byId(mc, id);
                return 1;
            });
            for (DinoPart.Kind kind : new DinoPart.Kind[]{DinoPart.Kind.HEAD, DinoPart.Kind.BODY, DinoPart.Kind.TAIL}) {
                float[] before = new float[1];
                Entity[] aimed = new Entity[1];
                STEPS.add(mc -> {
                    if (dino[0] == null) {
                        return 1;
                    }
                    aimed[0] = aimAt(mc, dino[0], kind, 0.8D);
                    serverTp(mc);
                    return 110;   // a club swings at most every 4-5 s (0.2-0.25 attacks a second): Better Combat waits for it
                });
                STEPS.add(mc -> {
                    if (dino[0] == null || aimed[0] == null) {
                        return 1;
                    }
                    aimed[0] = aimAt(mc, dino[0], kind, 0.8D);
                    Entity server = serverDino(mc, dino[0]);
                    before[0] = server instanceof DinosaurEntity d ? d.getHealth() : 0.0F;
                    try {
                        java.lang.reflect.Method start = Minecraft.class.getDeclaredMethod("startAttack");
                        start.setAccessible(true);
                        start.invoke(mc);
                    } catch (ReflectiveOperationException e) {
                        REPORT.add("  better combat attack: " + e);
                    }
                    return 1;
                });
                // Better Combat swings over several ticks and hits partway: hold the aim until the blow has landed
                for (int t = 0; t < 40; t++) {
                    STEPS.add(mc -> {
                        if (dino[0] != null && aimed[0] != null) {
                            aimAt(mc, dino[0], kind, 0.8D);
                        }
                        return 0;
                    });
                }
                STEPS.add(mc -> {
                    if (dino[0] == null || aimed[0] == null) {
                        return 1;
                    }
                    Entity server = serverDino(mc, dino[0]);
                    float after = server instanceof DinosaurEntity d ? d.getHealth() : 0.0F;
                    REPORT.add(String.format(Locale.ROOT, "  better combat %s on the %s (aimed at %s): %.3f damage", weapon, label(kind),
                            describe(aimed[0]), before[0] - after));
                    return 30;
                });
            }
        }
        // the player's own tamed creature right beside a wild one: a sweep at the wild one must not hurt the pet
        java.util.UUID wild = new java.util.UUID(0x7E55A52000000000L, ++serial);
        java.util.UUID pet = new java.util.UUID(0x7E55A52100000000L, ++serial);
        float[] petBefore = new float[1];
        DinosaurEntity[] target = new DinosaurEntity[1];
        STEPS.add(mc -> {
            command(mc, "tp @e[type=!player] 0 -400 0");
            command(mc, "item replace entity @a weapon.mainhand with terrassic:tail_club");
            int[] o = uuidInts(mc.player.getUUID());
            command(mc, String.format(Locale.ROOT, "summon terrassic:gallimimus 0.5 %s 0.5 {NoAI:1b,PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                    + "UUID:[I;%d,%d,%d,%d],Rotation:[90f,0f]}", Y, uuidInts(wild)[0], uuidInts(wild)[1], uuidInts(wild)[2], uuidInts(wild)[3]));
            command(mc, String.format(Locale.ROOT, "summon terrassic:gallimimus 0.5 %s 2.0 {NoAI:1b,PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                    + "UUID:[I;%d,%d,%d,%d],Rotation:[-90f,0f],Owner:[I;%d,%d,%d,%d],Sitting:1b}", Y, uuidInts(pet)[0], uuidInts(pet)[1],
                    uuidInts(pet)[2], uuidInts(pet)[3], o[0], o[1], o[2], o[3]));
            return 30;
        });
        STEPS.add(mc -> {
            target[0] = byId(mc, wild);
            DinosaurEntity p = byId(mc, pet);
            if (target[0] == null || p == null) {
                REPORT.add("  better combat sweep: creatures NOT FOUND");
                return 1;
            }
            Vec3 t = target[0].getBoundingBox().getCenter();
            look(mc.player, t.add(-2.2D, 0.3D, -0.4D), t);
            serverTp(mc);
            Entity server = mc.getSingleplayerServer().overworld().getEntity(pet);
            petBefore[0] = server instanceof DinosaurEntity d ? d.getHealth() : -1.0F;
            return 110;
        });
        STEPS.add(mc -> {
            if (target[0] == null) {
                return 1;
            }
            Vec3 t = target[0].getBoundingBox().getCenter();
            look(mc.player, t.add(-2.2D, 0.3D, -0.4D), t);
            Entity onCrosshair = pick(mc);
            REPORT.add("  better combat sweep: crosshair on " + (onCrosshair == null ? "nothing"
                    : DinoParts.owner(onCrosshair) == target[0] ? "the wild one (" + describe(onCrosshair) + ")" : "something else: " + describe(onCrosshair)));
            try {
                java.lang.reflect.Method start = Minecraft.class.getDeclaredMethod("startAttack");
                start.setAccessible(true);
                start.invoke(mc);
            } catch (ReflectiveOperationException e) {
                REPORT.add("  better combat attack: " + e);
            }
            return 40;
        });
        STEPS.add(mc -> {
            if (target[0] == null) {
                return 1;
            }
            Entity w = mc.getSingleplayerServer().overworld().getEntity(wild);
            Entity server = mc.getSingleplayerServer().overworld().getEntity(pet);
            float petAfter = server instanceof DinosaurEntity d ? d.getHealth() : -1.0F;
            REPORT.add(String.format(Locale.ROOT, "  better combat sweep: wild Gallimimus %s; your tamed one beside it lost %.3f health",
                    w instanceof DinosaurEntity d && d.getHealth() < d.getMaxHealth() ? "hit" : "NOT hit", petBefore[0] - petAfter));
            try {
                java.lang.reflect.Method rel = Class.forName("net.bettercombat.logic.TargetHelper").getMethod("getRelation",
                        net.minecraft.world.entity.player.Player.class, Entity.class);
                DinosaurEntity p = byId(mc, pet);
                StringBuilder r = new StringBuilder("  better combat relation to your tamed one: " + rel.invoke(null, mc.player, p)
                        + " (owner " + (p == null ? null : p.getOwnerUUID()) + ", you " + mc.player.getUUID() + "); its parts:");
                if (p != null) {
                    for (DinoPart part : p.parts()) {
                        r.append(' ').append(part.kind()).append('=').append(rel.invoke(null, mc.player, part));
                    }
                }
                REPORT.add(r.toString());
                REPORT.add("  better combat relation to the wild one: " + rel.invoke(null, mc.player, target[0]));
            } catch (ReflectiveOperationException e) {
                REPORT.add("  better combat relation: " + e);
            }
            return 5;
        });
    }

    private static int[] uuidInts(java.util.UUID id) {
        return new int[]{(int) (id.getMostSignificantBits() >> 32), (int) id.getMostSignificantBits(),
                (int) (id.getLeastSignificantBits() >> 32), (int) id.getLeastSignificantBits()};
    }

    // ------------------------------------------------------------------ flight

    /** The Pteranodon in the air (wings out, parts on): the crosshair along both wings, and a blow on a wing. */
    private static void planFlight() {
        DinosaurEntity[] dino = new DinosaurEntity[1];
        java.util.UUID id = new java.util.UUID(0x7E55A51E00000000L, ++serial);
        STEPS.add(mc -> {
            command(mc, "tp @e[type=!player] 0 -400 0");
            command(mc, String.format(Locale.ROOT, "summon terrassic:pteranodon 0.5 %s 0.5 {NoAI:1b,PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                    + "UUID:[I;%d,%d,%d,%d],Rotation:[0f,0f],Attributes:[{Name:\"minecraft:generic.armor\",Base:0d}]}", Y + 8.0D,
                    (int) (id.getMostSignificantBits() >> 32), (int) id.getMostSignificantBits(),
                    (int) (id.getLeastSignificantBits() >> 32), (int) id.getLeastSignificantBits()));
            return 30;
        });
        STEPS.add(mc -> {
            dino[0] = byId(mc, id);
            if (dino[0] == null) {
                REPORT.add("pteranodon in flight: NOT FOUND");
                return 1;
            }
            frame(mc, dino[0], true);
            return 20;
        });
        STEPS.add(mc -> shot(mc, dino[0], "pteranodon_flight_top"));
        STEPS.add(mc -> {
            if (dino[0] == null) {
                return 1;
            }
            List<DinoPart> wings = new ArrayList<>();
            for (DinoPart p : dino[0].parts()) {
                if (p.kind() == DinoPart.Kind.WING) {
                    wings.add(p);
                }
            }
            long on = wings.stream().filter(DinoPart::enabled).count();
            float bodyYaw = dino[0].yBodyRot * Mth.DEG_TO_RAD;
            Vec3 side = new Vec3(-Mth.cos(bodyYaw), 0, -Mth.sin(bodyYaw));
            wings.sort(Comparator.comparingDouble(p -> p.getBoundingBox().getCenter().subtract(dino[0].position()).dot(side)));
            List<Vec3> targets = new ArrayList<>();
            Vec3 body = dino[0].getBoundingBox().getCenter();
            List<Vec3> line = new ArrayList<>();
            for (DinoPart w : wings) {
                line.add(w.getBoundingBox().getCenter());
            }
            // tip to tip through the body: left wing, body, right wing
            List<Vec3> chain = new ArrayList<>();
            for (Vec3 p : line) {
                if (p.subtract(dino[0].position()).dot(side) < 0) {
                    chain.add(p);
                }
            }
            chain.add(body);
            for (Vec3 p : line) {
                if (p.subtract(dino[0].position()).dot(side) >= 0) {
                    chain.add(p);
                }
            }
            for (int i = 0; i < chain.size(); i++) {
                targets.add(chain.get(i));
                if (i + 1 < chain.size()) {
                    int n = (int) Math.ceil(chain.get(i).distanceTo(chain.get(i + 1)) / 0.1D);
                    for (int k = 1; k < n; k++) {
                        targets.add(chain.get(i).lerp(chain.get(i + 1), k / (double) n));
                    }
                }
            }
            int misses = 0;
            int picks = 0;
            int wingHits = 0;
            for (Vec3 t : targets) {
                for (Vec3 from : new Vec3[]{new Vec3(0, 3.0D, 0.4D), new Vec3(0, -3.0D, 0.4D)}) {
                    look(mc.player, t.add(from), t);
                    Entity hit = pick(mc);
                    picks++;
                    if (hit == null || DinoParts.owner(hit) != dino[0]) {
                        misses++;
                    } else if (hit instanceof DinoPart p && p.kind() == DinoPart.Kind.WING) {
                        wingHits++;
                    }
                }
            }
            totalPicks += picks;
            totalMisses += misses;
            REPORT.add(String.format(Locale.ROOT, "pteranodon in flight (airborne %s): %d of %d wing parts on, %d picks tip to tip from above and below, %d misses, %d on a wing",
                    ((FlyingDinosaur) dino[0]).isAirborne(), on, wings.size(), picks, misses, wingHits));
            return 1;
        });
        float[] before = new float[1];
        Entity[] aimed = new Entity[1];
        STEPS.add(mc -> {
            if (dino[0] == null) {
                return 1;
            }
            DinoPart tip = null;
            for (DinoPart p : dino[0].parts()) {
                if (p.kind() == DinoPart.Kind.WING && p.enabled()) {
                    tip = p;
                    break;
                }
            }
            aimed[0] = tip;
            if (tip != null) {
                Vec3 t = tip.getBoundingBox().getCenter();
                look(mc.player, t.add(0, 2.5D, 0.3D), t);
                serverTp(mc);
            }
            return 8;
        });
        STEPS.add(mc -> {
            if (aimed[0] == null) {
                REPORT.add("  attack wing: no wing part on");
                return 1;
            }
            Vec3 t = aimed[0].getBoundingBox().getCenter();
            look(mc.player, t.add(0, 2.5D, 0.3D), t);
            Entity hit = pick(mc);
            Entity server = serverDino(mc, dino[0]);
            before[0] = server instanceof DinosaurEntity d ? d.getHealth() : 0.0F;
            if (hit != aimed[0]) {
                REPORT.add("  attack wing: crosshair on " + describe(hit));
                aimed[0] = null;
                return 1;
            }
            mc.gameMode.attack(mc.player, hit);
            return 30;
        });
        STEPS.add(mc -> {
            if (aimed[0] != null) {
                Entity server = serverDino(mc, dino[0]);
                float after = server instanceof DinosaurEntity d ? d.getHealth() : 0.0F;
                REPORT.add(String.format(Locale.ROOT, "  attack wing      -> %s: %.3f damage", describe(aimed[0]), before[0] - after));
            }
            return 5;
        });
    }

    // ------------------------------------------------------------------ picking

    /** Aims the crosshair along the body line from both sides and from above; any ray that misses is a gap. */
    private static void picks(Minecraft mc, DinosaurEntity dino, String species, int yaw) {
        LocalPlayer player = mc.player;
        List<DinoPart> line = new ArrayList<>();
        for (DinoPart p : dino.parts()) {
            if (p.enabled() && p.kind() != DinoPart.Kind.WING) {
                line.add(p);
            }
        }
        float bodyYaw = dino.yBodyRot * Mth.DEG_TO_RAD;
        Vec3 forward = new Vec3(-Mth.sin(bodyYaw), 0, Mth.cos(bodyYaw));
        Vec3 side = new Vec3(-Mth.cos(bodyYaw), 0, -Mth.sin(bodyYaw));
        line.sort(Comparator.comparingDouble(p -> p.getBoundingBox().getCenter().subtract(dino.position()).dot(forward)));
        List<Vec3> targets = new ArrayList<>();
        for (int i = 0; i < line.size(); i++) {
            Vec3 a = line.get(i).getBoundingBox().getCenter();
            targets.add(a);
            if (i + 1 < line.size()) {
                Vec3 b = line.get(i + 1).getBoundingBox().getCenter();
                int n = (int) Math.ceil(a.distanceTo(b) / 0.1D);
                for (int k = 1; k < n; k++) {
                    targets.add(a.lerp(b, k / (double) n));
                }
            }
        }
        int misses = 0;
        int picks = 0;
        List<String> examples = new ArrayList<>();
        int[] kinds = new int[DinoPart.Kind.values().length + 1];
        for (Vec3 t : targets) {
            for (Vec3 from : new Vec3[]{side.scale(3.0D), side.scale(-3.0D), new Vec3(0, 3.0D, 0).add(side.scale(0.5D))}) {
                look(player, t.add(from), t);
                Entity hit = pick(mc);
                picks++;
                Entity owner = hit == null ? null : DinoParts.owner(hit);
                if (owner != dino) {
                    misses++;
                    if (examples.size() < 6) {
                        Vec3 rel = t.subtract(dino.position());
                        examples.add(String.format(Locale.ROOT, "fwd %.2f up %.2f from %s -> %s", rel.dot(forward), rel.y,
                                from.y > 1 ? "above" : from.dot(side) > 0 ? "side+" : "side-", describe(hit)));
                    }
                } else {
                    kinds[hit instanceof DinoPart part ? part.kind().ordinal() : kinds.length - 1]++;
                }
            }
        }
        totalPicks += picks;
        totalMisses += misses;
        StringBuilder found = new StringBuilder();
        for (DinoPart.Kind k : DinoPart.Kind.values()) {
            if (kinds[k.ordinal()] > 0) {
                found.append(k.name().toLowerCase(Locale.ROOT)).append('=').append(kinds[k.ordinal()]).append(' ');
            }
        }
        found.append("collisionbox=").append(kinds[kinds.length - 1]);
        boolean flyer = dino instanceof FlyingDinosaur;
        REPORT.add(String.format(Locale.ROOT, "%s yaw %d: %d parts (%s), %d picks along %d points, %d misses; hits: %s",
                species, yaw, dino.parts().length, flyer ? "wings only in flight" : "no wings", picks, targets.size(), misses, found));
        for (String e : examples) {
            REPORT.add("    miss " + e);
        }
        park(player);
    }

    /** Puts the player 2.5 blocks to the side of the part to strike (null = the creature's own box) looking at it. */
    private static Entity aimAt(Minecraft mc, DinosaurEntity dino, DinoPart.Kind kind) {
        return aimAt(mc, dino, kind, 2.0D);
    }

    private static Entity aimAt(Minecraft mc, DinosaurEntity dino, DinoPart.Kind kind, double gap) {
        Entity target = dino;
        if (kind != null) {
            DinoPart best = null;
            for (DinoPart p : dino.parts()) {
                if (p.kind() == kind && p.enabled()) {
                    double f = p.spec.forward();
                    // the snout piece for the head, the tip for the tail
                    if (best == null || (kind == DinoPart.Kind.TAIL ? f < best.spec.forward() : f > best.spec.forward())) {
                        best = p;
                    }
                }
            }
            if (best == null) {
                return null;
            }
            target = best;
        }
        Vec3 t = kind == null ? dino.position().add(0, dino.getBbHeight() * 0.5D, 0) : target.getBoundingBox().getCenter();
        float bodyYaw = dino.yBodyRot * Mth.DEG_TO_RAD;
        Vec3 side = new Vec3(-Mth.cos(bodyYaw), 0, -Mth.sin(bodyYaw));
        double half = kind == null ? dino.getBbWidth() * 0.5D : Math.max(target.getBoundingBox().getXsize(), target.getBoundingBox().getZsize()) * 0.5D;
        look(mc.player, t.add(side.scale(half + gap)), t);
        return target;
    }

    private static Entity pick(Minecraft mc) {
        mc.gameRenderer.pick(1.0F);
        HitResult r = mc.hitResult;
        return r instanceof EntityHitResult e ? e.getEntity() : null;
    }

    /** Places the player's eyes at {@code eye}, looking at {@code at}. */
    private static void look(LocalPlayer player, Vec3 eye, Vec3 at) {
        Vec3 d = at.subtract(eye);
        float yRot = (float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90.0F;
        float xRot = (float) -(Mth.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * Mth.RAD_TO_DEG);
        // the /gamemode sent at the start turns flying off on its way back: kept on, or the player falls between steps
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

    /** Frames the whole animal and its boxes: from the side, or from above at three quarters. */
    private static void frame(Minecraft mc, DinosaurEntity dino, boolean top) {
        AABB all = dino.getBoundingBox().minmax(dino.partsBounds());
        Vec3 c = all.getCenter();
        double size = Math.max(all.getXsize(), Math.max(all.getYsize(), all.getZsize()));
        float bodyYaw = dino.yBodyRot * Mth.DEG_TO_RAD;
        Vec3 side = new Vec3(-Mth.cos(bodyYaw), 0, -Mth.sin(bodyYaw));
        Vec3 forward = new Vec3(-Mth.sin(bodyYaw), 0, Mth.cos(bodyYaw));
        double distance = size * 1.25D + 2.0D;
        Vec3 eye = top ? c.add(side.scale(distance * 0.45D)).add(forward.scale(distance * 0.3D)).add(0, distance * 0.75D, 0)
                : c.add(side.scale(distance)).add(0, size * 0.1D, 0);
        look(mc.player, eye, c);
        serverTp(mc);
    }

    /** Moves the player on the server to where the client put it (a client-side jump is not always taken). */
    private static void serverTp(Minecraft mc) {
        LocalPlayer p = mc.player;
        command(mc, String.format(Locale.ROOT, "tp %s %.4f %.4f %.4f %.3f %.3f", p.getGameProfile().getName(),
                p.getX(), p.getY(), p.getZ(), p.getYRot(), p.getXRot()));
    }

    private static int shot(Minecraft mc, DinosaurEntity dino, String name) {
        if (dino != null) {
            Screenshot.grab(mc.gameDirectory, "parts_" + name + ".png", mc.getMainRenderTarget(), msg -> {
            });
        }
        return 5;
    }

    private static void park(LocalPlayer player) {
        look(player, new Vec3(0.5D, Y + 30.0D, -40.0D), new Vec3(0.5D, Y, 0.5D));
    }

    private static Entity serverDino(Minecraft mc, DinosaurEntity dino) {
        MinecraftServer server = mc.getSingleplayerServer();
        return server == null ? null : server.overworld().getEntity(dino.getUUID());
    }

    private static void command(Minecraft mc, String command) {
        MinecraftServer server = mc.getSingleplayerServer();
        server.execute(() -> server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), command));
    }

    private static String label(DinoPart.Kind kind) {
        return kind == null ? "collision" : kind.name().toLowerCase(Locale.ROOT);
    }

    private static String describe(Entity e) {
        if (e == null) {
            return "nothing";
        }
        if (e instanceof DinoPart p) {
            return "part " + p.kind().name().toLowerCase(Locale.ROOT) + String.format(Locale.ROOT, " (%.2f)", p.spec.forward());
        }
        return e instanceof DinosaurEntity ? "collision box" : e.getType().toShortString();
    }
}
