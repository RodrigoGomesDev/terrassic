package com.terrassic.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * The whistle (1.5, docs/ORDENS.md): one order for every tamed dinosaur of the player that hears it, given from the
 * whistle wheel (client/WhistleWheelScreen, hold the whistle key). The six orders are the ones of the approved HUD
 * preview: follow, wait here, wander nearby, attack my target, gather and passive. The dino screen still gives the
 * same orders to one animal.
 * <ul>
 *   <li>Who hears: the player's own living tamed dinosaurs within {@link #RANGE} blocks, except the one they ride and
 *       one on their shoulder. Animals ridden by someone else or knocked out do not obey.</li>
 *   <li>Attack my target: the creature the player looks at, up to {@link #TARGET_RANGE} blocks and not behind a wall,
 *       or else the last one the player hit in the last ten seconds. It overrides the neutral stance's rule (players and
 *       tamed animals are attacked only on this order) and a "Stop", but not the passive stance, a waiting animal, a
 *       young one, a species that flees instead of fighting, the player's own animals or a player PvP protects.</li>
 *   <li>Passive: all of them take the passive stance; whistled again when all already are, they go back to neutral.</li>
 * </ul>
 * Every animal that obeys shows a note over its head. No whistle sound yet: the mod's sounds are on hold (docs/SONS.md).
 */
public final class Whistle {
    /** How far the whistle carries (blocks). */
    public static final double RANGE = 24.0D;
    /** How far "attack my target" looks for the target (blocks). */
    public static final double TARGET_RANGE = 32.0D;
    /** The wheel's orders, clockwise from the top (lang: gui.terrassic.whistle.&lt;order&gt;). */
    public static final String[] ORDERS = {"follow", "sit", "wander", "attack", "gather", "passive"};
    /** At most one whistle every half second per player. */
    private static final long COOLDOWN = 10L;
    private static final Map<UUID, Long> LAST = new HashMap<>();

    private Whistle() {
    }

    /** Whether this dinosaur hears the player's whistle (both sides: the wheel counts them on the client). */
    public static boolean hears(DinosaurEntity dino, Player player) {
        return dino.isAlive() && dino.isTame() && dino.isOwnedBy(player) && dino != player.getVehicle()
                && dino.getVehicle() != player && dino.distanceToSqr(player) <= RANGE * RANGE;
    }

    /** The player's dinosaurs that hear the whistle now. */
    public static List<DinosaurEntity> hearing(Player player) {
        return player.level().getEntitiesOfClass(DinosaurEntity.class, player.getBoundingBox().inflate(RANGE),
                dino -> hears(dino, player));
    }

    /** The player blew the whistle with this order (server; network/DinoNetwork). */
    public static void blow(ServerPlayer player, String order) {
        if (!List.of(ORDERS).contains(order)) {
            return;
        }
        long now = player.level().getGameTime();
        Long last = LAST.get(player.getUUID());
        if (last != null && now - last < COOLDOWN && now >= last) {
            return;
        }
        LAST.put(player.getUUID(), now);
        List<DinosaurEntity> dinos = hearing(player);
        if (dinos.isEmpty()) {
            tell(player, Component.translatable("message.terrassic.whistle.nobody"));
            return;
        }
        LivingEntity target = null;
        if (order.equals("attack")) {
            target = aimed(player);
            if (target == null) {
                tell(player, Component.translatable("message.terrassic.whistle.no_target"));
                return;
            }
            if (target instanceof Player victim && !player.canHarmPlayer(victim)) {
                tell(player, Component.translatable("message.terrassic.whistle.protected", target.getDisplayName()));
                return;
            }
        }
        boolean backToNeutral = order.equals("passive") && dinos.stream().allMatch(d -> d.getStance() == DinoStance.PASSIVE);
        List<DinosaurEntity> obeyed = new ArrayList<>();
        for (DinosaurEntity dino : dinos) {
            if (obey(dino, player, order, target, backToNeutral)) {
                obeyed.add(dino);
                if (player.level() instanceof ServerLevel server) {
                    // count 0: the first offset is the note's colour
                    server.sendParticles(ParticleTypes.NOTE, dino.getX(), dino.getY() + dino.getBbHeight() + 0.5D, dino.getZ(),
                            0, 0.45D, 0.0D, 0.0D, 1.0D);
                }
            }
        }
        if (obeyed.isEmpty()) {
            tell(player, target != null
                    ? Component.translatable("message.terrassic.whistle.attack.none", target.getDisplayName())
                    : Component.translatable("message.terrassic.whistle.nobody"));
            return;
        }
        String key = "message.terrassic.whistle." + (backToNeutral ? "neutral" : order) + (obeyed.size() == 1 ? ".one" : ".many");
        Component who = obeyed.size() == 1 ? obeyed.get(0).getDisplayName() : Component.literal(String.valueOf(obeyed.size()));
        tell(player, target != null ? Component.translatable(key, who, target.getDisplayName()) : Component.translatable(key, who));
    }

    /** One animal takes the order; false when it cannot (ridden, knocked out, or not one to fight this target). */
    private static boolean obey(DinosaurEntity dino, ServerPlayer player, String order, LivingEntity target, boolean backToNeutral) {
        if (dino.isVehicle() || dino.isKnockedOut()) {
            return false;
        }
        switch (order) {
            case "follow", "sit" -> {
                dino.setOrderedToSit(order.equals("sit"));
                dino.stopWandering();
                dino.getNavigation().stop();
                dino.setTarget(null);
                return true;
            }
            case "wander" -> {
                dino.wanderHere();
                return true;
            }
            case "gather" -> {
                dino.setOrderedToSit(false);
                dino.stopWandering();
                dino.setTarget(null);
                dino.getNavigation().moveTo(player, 1.25D);
                return true;
            }
            case "attack" -> {
                return dino.orderAttack(target);
            }
            case "passive" -> {
                dino.setStance(backToNeutral ? DinoStance.NEUTRAL : DinoStance.PASSIVE);
                return true;
            }
            default -> {
                return false;
            }
        }
    }

    /** What the player aims at: a living creature in their line of sight, else the last one they hit (10 s). */
    private static LivingEntity aimed(ServerPlayer player) {
        Vec3 eye = player.getEyePosition();
        Vec3 look = player.getViewVector(1.0F);
        Vec3 end = eye.add(look.scale(TARGET_RANGE));
        BlockHitResult wall = player.level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        if (wall.getType() != HitResult.Type.MISS) {
            end = wall.getLocation();
        }
        Entity mount = player.getVehicle();
        AABB box = player.getBoundingBox().expandTowards(look.scale(TARGET_RANGE)).inflate(1.0D);
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end, box,
                e -> e instanceof LivingEntity && e.isAlive() && !e.isSpectator() && e.isPickable() && e != mount
                        && !(e instanceof DinosaurEntity d && d.getVehicle() == player),
                eye.distanceToSqr(end));
        if (hit != null && hit.getEntity() instanceof LivingEntity living) {
            return living;
        }
        LivingEntity last = player.getLastHurtMob();
        if (last != null && last.isAlive() && player.tickCount - player.getLastHurtMobTimestamp() < 200
                && last.distanceToSqr(player) < TARGET_RANGE * TARGET_RANGE) {
            return last;
        }
        return null;
    }

    private static void tell(ServerPlayer player, Component message) {
        player.displayClientMessage(message, true);
    }
}
