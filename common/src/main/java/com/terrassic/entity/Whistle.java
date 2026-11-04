package com.terrassic.entity;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import dev.architectury.event.EventResult;
import dev.architectury.event.events.common.CommandRegistrationEvent;
import dev.architectury.event.events.common.EntityEvent;
import dev.architectury.event.events.common.PlayerEvent;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
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
 *       one on their shoulder (it stays there whatever the order). Animals ridden by someone else or knocked out do not obey.</li>
 *   <li>Attack my target: the creature the player looks at, up to {@link #TARGET_RANGE} blocks and not behind a wall,
 *       or else the last one the player hit in the last ten seconds, by hand, arrow or dart (kept here from the hurt event,
 *       not from vanilla's last-hurt-mob, which forgets after five seconds and only counts blows by hand). It overrides the neutral stance's rule (players and
 *       tamed animals are attacked only on this order) and a "Stop", but not the passive stance, a waiting animal, a
 *       young one, a species that flees instead of fighting, the player's own animals or a player PvP protects.</li>
 *   <li>Passive: all of them take the passive stance; whistled again when all already are, they go back to neutral.</li>
 * </ul>
 * Every animal that obeys shows a note over its head. No whistle sound yet: the mod's sounds are on hold (docs/SONS.md).
 */
public final class Whistle {
    /** How far the whistle carries (blocks). 1.7 (player feedback: "the whistle only works for about 50 blocks"):
     *  24 -> 96, within the entity tracking range of the dinosaurs (8 to 10 chunks), so the wheel counts them all.
     *  Farther than that, the "My dinos" list (TamedRegistry, client/MyDinosScreen) shows where each one is. */
    public static final double RANGE = 96.0D;
    /** How far "attack my target" looks for the target (blocks). */
    public static final double TARGET_RANGE = 32.0D;
    /** The wheel's orders, clockwise from the top (lang: gui.terrassic.whistle.&lt;order&gt;). */
    public static final String[] ORDERS = {"follow", "sit", "wander", "attack", "gather", "passive"};
    /** At most one whistle every half second per player. */
    private static final long COOLDOWN = 10L;
    private static final Map<UUID, Long> LAST = new HashMap<>();
    /** How long the last creature a player hit stays "my target" (ticks). */
    private static final long LAST_HIT_TICKS = 200L;
    /** The last creature each player hurt, and when (game time). */
    private static final Map<UUID, LastHit> LAST_HIT = new HashMap<>();

    private record LastHit(UUID target, long time) {
    }

    private Whistle() {
    }

    /** Remembers whom each player hurts, for "attack my target" (Terrassic.init). */
    public static void init() {
        EntityEvent.LIVING_HURT.register((victim, source, amount) -> {
            if (!victim.level().isClientSide && source.getEntity() instanceof ServerPlayer player && victim != player
                    && worthChasing(victim, player)) {
                LAST_HIT.put(player.getUUID(), new LastHit(victim.getUUID(), player.level().getGameTime()));
            }
            return EventResult.pass();
        });
        PlayerEvent.PLAYER_QUIT.register(player -> {
            LAST_HIT.remove(player.getUUID());
            LAST.remove(player.getUUID());
        });
        CommandRegistrationEvent.EVENT.register(Whistle::commands);
    }

    /**
     * Operators only, for tests and servers, like {@code /terrassic alfa}: {@code /terrassic apito <order>} (whistle)
     * blows the whistle as the player running it, the same as the wheel; {@code /terrassic ombro} (perch) puts their
     * nearest shoulder animal (8 blocks) on their shoulder, the same as the dino screen's button.
     */
    private static void commands(CommandDispatcher<CommandSourceStack> dispatcher, CommandBuildContext ctx,
                                 Commands.CommandSelection selection) {
        for (String name : List.of("apito", "whistle", "silbato")) {
            dispatcher.register(Commands.literal("terrassic").then(Commands.literal(name).requires(s -> s.hasPermission(2))
                    .then(Commands.argument("ordem", StringArgumentType.word())
                            .suggests((c, b) -> SharedSuggestionProvider.suggest(ORDERS, b))
                            .executes(c -> {
                                blow(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "ordem"));
                                return 1;
                            }))));
        }
        for (String name : List.of("ombro", "perch", "hombro")) {
            dispatcher.register(Commands.literal("terrassic").then(Commands.literal(name).requires(s -> s.hasPermission(2))
                    .executes(c -> perchNearest(c.getSource().getPlayerOrException()))));
        }
    }

    private static int perchNearest(ServerPlayer player) {
        if (player.isVehicle() || player.isPassenger()) {
            return 0;
        }
        DinosaurEntity bird = player.level().getEntitiesOfClass(DinosaurEntity.class, player.getBoundingBox().inflate(8.0D),
                        d -> d.isAlive() && d.isTame() && d.isOwnedBy(player) && d.canPerch() && !d.isBaby() && !d.isPassenger())
                .stream().min(java.util.Comparator.comparingDouble(d -> d.distanceToSqr(player))).orElse(null);
        if (bird == null) {
            tell(player, Component.translatable("message.terrassic.whistle.no_perch"));
            return 0;
        }
        bird.perchOn(player);
        return 1;
    }

    /** Not the player's own animals, nor what they ride or carry (a mount, a bird on the shoulder). */
    private static boolean worthChasing(Entity e, Player player) {
        return !(e instanceof OwnableEntity own && player.getUUID().equals(own.getOwnerUUID()))
                && e.getRootVehicle() != player.getRootVehicle();
    }

    /** Whether this dinosaur hears the player's whistle (both sides: the wheel counts them on the client). */
    public static boolean hears(DinosaurEntity dino, Player player) {
        return dino.isAlive() && dino.isTame() && dino.isOwnedBy(player) && !dino.isPerched()
                && dino.getRootVehicle() != player.getRootVehicle() && dino.distanceToSqr(player) <= RANGE * RANGE;
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
            // only the bird on the shoulder heard it: say so, rather than "nobody"
            DinosaurEntity perched = player.getPassengers().stream().filter(e -> e instanceof DinosaurEntity)
                    .map(e -> (DinosaurEntity) e).findFirst().orElse(null);
            tell(player, perched != null ? Component.translatable("message.terrassic.whistle.perched", perched.getDisplayName())
                    : Component.translatable("message.terrassic.whistle.nobody"));
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
        AABB box = player.getBoundingBox().expandTowards(look.scale(TARGET_RANGE)).inflate(1.0D);
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end, box,
                e -> e instanceof LivingEntity && e.isAlive() && !e.isSpectator() && e.isPickable() && worthChasing(e, player),
                eye.distanceToSqr(end));
        if (hit != null && hit.getEntity() instanceof LivingEntity living) {
            return living;
        }
        LastHit last = LAST_HIT.get(player.getUUID());
        if (last == null || player.level().getGameTime() - last.time() > LAST_HIT_TICKS
                || player.level().getGameTime() < last.time()) {
            return null;
        }
        Entity e = player.serverLevel().getEntity(last.target());
        if (e instanceof LivingEntity living && living.isAlive() && living.distanceToSqr(player) < TARGET_RANGE * TARGET_RANGE
                && worthChasing(living, player)) {
            return living;
        }
        return null;
    }

    private static void tell(ServerPlayer player, Component message) {
        player.displayClientMessage(message, true);
    }
}
