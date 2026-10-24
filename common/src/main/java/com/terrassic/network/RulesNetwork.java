package com.terrassic.network;

import com.mojang.brigadier.Command;
import com.terrassic.Terrassic;
import com.terrassic.config.Rules;
import dev.architectury.event.events.common.CommandRegistrationEvent;
import dev.architectury.event.events.common.PlayerEvent;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * Packets of the world rules (docs/REGRAS.md).
 * <ul>
 *   <li>{@link #SYNC} (server to client): the world's rules as NBT and whether this player may edit them; sent on
 *       join and to everyone after a change.</li>
 *   <li>{@link #SET} (client to server): the rules edited in the Rules screen; applied only for an operator (or the
 *       owner of a single player world).</li>
 *   <li>{@link #OPEN} (server to client): open the Rules screen (command {@code /terrassic regras}).</li>
 * </ul>
 * The client receivers are registered in ClientHooks.
 */
public final class RulesNetwork {
    public static final ResourceLocation SYNC = Terrassic.id("rules_sync");
    public static final ResourceLocation SET = Terrassic.id("rules_set");
    public static final ResourceLocation OPEN = Terrassic.id("rules_open");

    private RulesNetwork() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.C2S, SET, (buf, context) -> {
            CompoundTag tag = buf.readNbt();
            context.queue(() -> {
                if (tag != null && context.getPlayer() instanceof ServerPlayer player) {
                    receiveRules(player, Rules.load(tag));
                }
            });
        });
        PlayerEvent.PLAYER_JOIN.register(RulesNetwork::sync);
        CommandRegistrationEvent.EVENT.register((dispatcher, registry, selection) -> {
            for (String name : new String[]{"regras", "rules", "reglas"}) {
                dispatcher.register(Commands.literal(Terrassic.MOD_ID).then(Commands.literal(name).executes(ctx -> {
                    ServerPlayer player = ctx.getSource().getPlayerOrException();
                    sync(player);
                    NetworkManager.sendToPlayer(player, OPEN, new FriendlyByteBuf(Unpooled.buffer()));
                    return Command.SINGLE_SUCCESS;
                })));
            }
        });
    }

    /** Operators, and the owner of a single player world even without cheats. */
    public static boolean canEdit(ServerPlayer player) {
        return player.hasPermissions(2) || player.server.isSingleplayerOwner(player.getGameProfile());
    }

    public static void sync(ServerPlayer player) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeNbt(Rules.of(player.server).save());
        buf.writeBoolean(canEdit(player));
        NetworkManager.sendToPlayer(player, SYNC, buf);
    }

    private static void receiveRules(ServerPlayer player, Rules rules) {
        if (!canEdit(player)) {
            player.displayClientMessage(Component.translatable("rules.terrassic.ui.denied").withStyle(ChatFormatting.RED), false);
            sync(player);
            return;
        }
        MinecraftServer server = player.server;
        Rules.apply(server, rules);
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            sync(p);
            if (canEdit(p)) {
                p.displayClientMessage(Component.translatable("rules.terrassic.ui.saved", player.getDisplayName())
                        .withStyle(ChatFormatting.GRAY), false);
            }
        }
    }
}
