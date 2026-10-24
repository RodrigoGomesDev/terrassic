package com.terrassic.leap;

import com.terrassic.entity.DinosaurEntity;
import dev.architectury.event.EventResult;
import dev.architectury.event.events.common.InteractionEvent;
import dev.architectury.event.events.common.TickEvent;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.BiFunction;

/**
 * The Leap (O Salto, HISTORIA.md §1 and §5) and the entry point of v0.9 "The End" (docs/SALTO.md).
 * <p>
 * Activating an open altar takes the player, everyone standing inside the ring with them, and the tamed creatures of
 * those players inside the ring, to the next era, while the flash of the impact covers the sky. The Altar always
 * opens onto the same moment of each era, so every era stays open (Rule 0).
 * <p>
 * The next era (Chapter 2, "Penas e Cinzas") arrives in v2.0 with its own dimension, registered here with
 * {@link #registerDestination}. Until then the leap plays the whole scene (the flash, the sound) and the Rift does
 * not open: the player stays where they are, with a message, and loses nothing.
 */
public final class Leap {
    /** Ticks between the start of the flash and the moment the leap happens (the screen is white by then). */
    private static final int FLASH_TICKS = 45;
    private static final Map<Integer, Destination> DESTINATIONS = new HashMap<>();
    private static final List<Pending> PENDING = new ArrayList<>();

    /** Where a chapter's era is: its dimension, where the normal leap lands and where an unstable one lands. */
    public record Destination(ResourceKey<Level> level, BiFunction<ServerLevel, RandomSource, BlockPos> landing,
                              BiFunction<ServerLevel, RandomSource, BlockPos> unstableLanding) {
    }

    private record Pending(UUID player, ResourceKey<Level> from, BlockPos altar, long at, boolean unstable, List<UUID> riders) {
    }

    private Leap() {
    }

    public static void init() {
        LeapRegistry.register();
        LeapNetwork.init();
        LeapCommands.init();
        TickEvent.SERVER_POST.register(Leap::tick);
        InteractionEvent.RIGHT_CLICK_BLOCK.register(Leap::clickAltar);
    }

    /**
     * Every main-hand click on an altar goes here, before vanilla: vanilla never calls Block.use for a sneaking
     * player holding an item (the amber offering) or with anything in the off hand (the empty-hand leap).
     * Sneaking with another block in hand still places it, so the ring can be built around the altar.
     */
    private static EventResult clickAltar(Player player, InteractionHand hand, BlockPos pos, Direction face) {
        if (!player.level().getBlockState(pos).is(LeapRegistry.LEAP_ALTAR.get()) || player.isSpectator()) {
            return EventResult.pass();
        }
        ItemStack held = player.getMainHandItem();
        if (player.isShiftKeyDown() && held.getItem() instanceof BlockItem) {
            return EventResult.pass();
        }
        if (hand != InteractionHand.MAIN_HAND) {
            return EventResult.pass();
        }
        if (!player.level().isClientSide() && player.level().getBlockEntity(pos) instanceof LeapAltarBlockEntity altar) {
            altar.use(player);
        }
        return EventResult.interruptTrue();
    }

    static boolean isLeaping(UUID player) {
        for (Pending p : PENDING) {
            if (p.player().equals(player)) {
                return true;
            }
        }
        return false;
    }

    /** v2.0 and later: the era of {@code chapter} (2 = Early Cretaceous, 3 = Jurassic, ...). */
    public static void registerDestination(int chapter, Destination destination) {
        DESTINATIONS.put(chapter, destination);
    }

    public static boolean hasDestination(int chapter) {
        return DESTINATIONS.containsKey(chapter);
    }

    /** Chapter of the era the level belongs to: the Overworld is Chapter 1. */
    public static int chapterOf(Level level) {
        for (Map.Entry<Integer, Destination> e : DESTINATIONS.entrySet()) {
            if (e.getValue().level().equals(level.dimension())) {
                return e.getKey();
            }
        }
        return 1;
    }

    /** {@code /terrassic capitulo n} for n >= 2: straight to the era's landing; false while the era is not in the game. */
    static boolean toChapter(ServerPlayer player, int chapter) {
        Destination d = DESTINATIONS.get(chapter);
        ServerLevel to = d == null ? null : player.server.getLevel(d.level());
        if (to == null) {
            return false;
        }
        BlockPos land = d.landing().apply(to, to.random);
        player.teleportTo(to, land.getX() + 0.5D, land.getY(), land.getZ() + 0.5D, player.getYRot(), player.getXRot());
        return true;
    }

    /** Starts the leap from this altar: the flash now, the jump {@link #FLASH_TICKS} later. */
    static void leap(ServerPlayer player, LeapAltarBlockEntity altar, boolean unstable) {
        ServerLevel level = player.serverLevel();
        BlockPos pos = altar.getBlockPos();
        List<UUID> riders = new ArrayList<>();
        for (ServerPlayer p : level.players()) {
            if (p == player || AltarRing.inside(pos, p.getX(), p.getY(), p.getZ())) {
                riders.add(p.getUUID());
                LeapNetwork.flash(p, unstable);
            }
        }
        Vec3 c = Vec3.atCenterOf(pos);
        level.sendParticles(ParticleTypes.FLASH, c.x, c.y + 1.0D, c.z, 3, 1.0D, 1.0D, 1.0D, 0.0D);
        level.sendParticles(ParticleTypes.END_ROD, c.x, c.y + 1.0D, c.z, 200, 2.5D, 2.0D, 2.5D, 0.2D);
        level.playSound(null, pos, SoundEvents.END_PORTAL_SPAWN, SoundSource.PLAYERS, 3.0F, unstable ? 0.5F : 0.8F);
        level.playSound(null, pos, SoundEvents.LIGHTNING_BOLT_THUNDER, SoundSource.WEATHER, 6.0F, 0.6F);
        PENDING.add(new Pending(player.getUUID(), level.dimension(), pos, level.getGameTime() + FLASH_TICKS, unstable, riders));
    }

    private static void tick(MinecraftServer server) {
        if (PENDING.isEmpty()) {
            return;
        }
        for (Iterator<Pending> it = PENDING.iterator(); it.hasNext(); ) {
            Pending p = it.next();
            ServerLevel from = server.getLevel(p.from());
            if (from == null) {
                it.remove();
                continue;
            }
            if (from.getGameTime() < p.at()) {
                continue;
            }
            it.remove();
            jump(server, from, p);
        }
    }

    private static void jump(MinecraftServer server, ServerLevel from, Pending p) {
        int chapter = chapterOf(from);
        Destination d = DESTINATIONS.get(chapter + 1);
        List<ServerPlayer> riders = new ArrayList<>();
        for (UUID id : p.riders()) {
            ServerPlayer sp = server.getPlayerList().getPlayer(id);
            if (sp != null && sp.isAlive() && sp.level() == from) {
                riders.add(sp);
            }
        }
        if (d == null || server.getLevel(d.level()) == null) {
            for (ServerPlayer sp : riders) {
                sp.displayClientMessage(Component.translatable("leap.terrassic.no_destination", chapter + 1), false);
            }
            return;
        }
        ServerLevel to = server.getLevel(d.level());
        BlockPos land = (p.unstable() ? d.unstableLanding() : d.landing()).apply(to, to.random);
        // the tamed creatures of the riders that stand inside the ring go along
        List<Entity> animals = new ArrayList<>();
        AABB ring = new AABB(p.altar()).inflate(AltarRing.RADIUS + 1.0D, 4.0D, AltarRing.RADIUS + 1.0D);
        for (TamableAnimal a : from.getEntitiesOfClass(TamableAnimal.class, ring, a -> a.isTame() && a.isAlive()
                && AltarRing.inside(p.altar(), a.getX(), a.getY(), a.getZ()))) {
            for (ServerPlayer sp : riders) {
                if (sp.getUUID().equals(a.getOwnerUUID())) {
                    animals.add(a);
                    break;
                }
            }
        }
        int i = 0;
        for (ServerPlayer sp : riders) {
            double ox = (i % 3 - 1) * 1.5D;
            double oz = (i / 3 - 1) * 1.5D;
            sp.teleportTo(to, land.getX() + 0.5D + ox, land.getY(), land.getZ() + 0.5D + oz, sp.getYRot(), sp.getXRot());
            com.terrassic.research.Research.award(sp, "chapter" + chapter + (p.unstable() ? "/unstable_jump" : "/leap"));
            i++;
        }
        for (Entity a : animals) {
            if (a instanceof DinosaurEntity d2 && d2.isInSittingPose()) {
                d2.setOrderedToSit(false);
            }
            a.teleportTo(to, land.getX() + 0.5D + (from.random.nextDouble() - 0.5D) * 6.0D, land.getY(),
                    land.getZ() + 0.5D + (from.random.nextDouble() - 0.5D) * 6.0D, java.util.Set.of(), a.getYRot(), a.getXRot());
        }
    }
}
