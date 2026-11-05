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
        for (String species : SPECIES) {
            for (int yaw : YAWS) {
                planSpecies(species, yaw);
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

    private static void planSpecies(String species, int yaw) {
        DinosaurEntity[] dino = new DinosaurEntity[1];
        java.util.UUID id = new java.util.UUID(0x7E55A51C00000000L, ++serial);
        STEPS.add(mc -> {
            // out of the world rather than killed: a killed creature lies dying (and leaves a carcass) for a while
            command(mc, "tp @e[type=!player] 0 -400 0");
            command(mc, String.format(Locale.ROOT, "summon terrassic:%s 0.5 %s 0.5 {NoAI:1b,PersistenceRequired:1b,Size:1f,BirthSize:1f,"
                    + "UUID:[I;%d,%d,%d,%d],Rotation:[%df,0f],Attributes:[{Name:\"minecraft:generic.armor\",Base:0d}]}", species, Y,
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
        look(mc.player, t.add(side.scale(half + 2.0D)), t);
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
