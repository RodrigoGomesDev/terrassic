package com.terrassic.network;

import com.mojang.brigadier.CommandDispatcher;
import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.TamedRegistry;
import dev.architectury.event.events.common.CommandRegistrationEvent;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;

import java.util.List;

/**
 * 1.7: the "My dinos" list (entity/TamedRegistry). {@link #ASK} (client to server) asks for it; {@link #LIST} (server
 * to client) carries every tamed animal of the player with where it was last seen, how long ago (seconds) and whether
 * it is loaded now (its position then is live). {@code /terrassic dinos} prints the same list in the chat, for anyone.
 */
public final class TamedNetwork {
    public static final ResourceLocation ASK = Terrassic.id("tamed_ask");
    public static final ResourceLocation LIST = Terrassic.id("tamed_list");
    /** At most this many lines in one answer (a list longer than that is not one anybody scrolls). */
    private static final int MAX = 200;

    private TamedNetwork() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.C2S, ASK, (buf, context) -> context.queue(() -> {
            if (context.getPlayer() instanceof ServerPlayer player) {
                send(player);
            }
        }));
        CommandRegistrationEvent.EVENT.register(TamedNetwork::commands);
    }

    private static void commands(CommandDispatcher<CommandSourceStack> dispatcher, CommandBuildContext ctx,
                                 Commands.CommandSelection selection) {
        dispatcher.register(Commands.literal(Terrassic.MOD_ID).then(Commands.literal("dinos")
                .executes(c -> print(c.getSource().getPlayerOrException()))));
    }

    /** The player's list, with the loaded animals refreshed first (their live position, or dropped when untamed). */
    public static ListTag list(ServerPlayer player) {
        TamedRegistry data = TamedRegistry.get(player.server);
        long now = player.server.overworld().getGameTime();
        ListTag out = new ListTag();
        for (TamedRegistry.Entry e : data.of(player.getUUID())) {
            Entity live = loaded(player, e);
            if (live instanceof DinosaurEntity dino) {
                TamedRegistry.update(dino);
                if (!dino.isTame() || !dino.isOwnedBy(player)) {
                    continue;
                }
            }
            if (out.size() >= MAX) {
                break;
            }
            TamedRegistry.Entry fresh = data.entry(e.dino());
            if (fresh == null) {
                continue;
            }
            CompoundTag t = TamedRegistry.write(fresh);
            t.putLong("Ago", Math.max(0L, (now - fresh.seen()) / 20L));
            t.putBoolean("Loaded", live instanceof DinosaurEntity);
            if (live instanceof DinosaurEntity dino) {
                t.putFloat("Health", dino.getHealth() / Math.max(1.0F, dino.getMaxHealth()));
            }
            out.add(t);
        }
        return out;
    }

    private static Entity loaded(ServerPlayer player, TamedRegistry.Entry e) {
        ServerLevel level = player.server.getLevel(ResourceKey.create(Registries.DIMENSION, e.dimension()));
        return level != null ? level.getEntity(e.dino()) : null;
    }

    private static void send(ServerPlayer player) {
        CompoundTag tag = new CompoundTag();
        tag.put("Dinos", list(player));
        net.minecraft.network.RegistryFriendlyByteBuf out = Net.buf(player.registryAccess());
        out.writeNbt(tag);
        NetworkManager.sendToPlayer(player, LIST, out);
    }

    /** {@code /terrassic dinos}: one chat line per animal, nearest first in the player's dimension. */
    private static int print(ServerPlayer player) {
        ListTag dinos = list(player);
        if (dinos.isEmpty()) {
            player.sendSystemMessage(Component.translatable("message.terrassic.dinos.none"));
            return 0;
        }
        player.sendSystemMessage(Component.translatable("message.terrassic.dinos.header", dinos.size())
                .withStyle(ChatFormatting.GOLD));
        ResourceLocation here = player.level().dimension().location();
        List<CompoundTag> sorted = new java.util.ArrayList<>();
        for (int i = 0; i < dinos.size(); i++) {
            sorted.add(dinos.getCompound(i));
        }
        sorted.sort(java.util.Comparator.comparingDouble(t -> here.toString().equals(t.getString("Dim"))
                ? Math.sqrt(net.minecraft.core.BlockPos.of(t.getLong("Pos")).distSqr(player.blockPosition())) : 1.0E9D));
        for (CompoundTag t : sorted) {
            net.minecraft.core.BlockPos pos = net.minecraft.core.BlockPos.of(t.getLong("Pos"));
            Component name = t.getString("Name").isEmpty()
                    ? Component.translatable("entity.terrassic." + t.getString("Species"))
                    : Component.literal(t.getString("Name"));
            Component where = here.toString().equals(t.getString("Dim"))
                    ? Component.translatable("message.terrassic.dinos.distance",
                    (int) Math.round(Math.sqrt(pos.distSqr(player.blockPosition()))))
                    : Component.translatable("message.terrassic.dinos.dimension", t.getString("Dim"));
            player.sendSystemMessage(Component.translatable("message.terrassic.dinos.line", name, pos.getX(), pos.getY(),
                    pos.getZ(), where));
        }
        return dinos.size();
    }
}
