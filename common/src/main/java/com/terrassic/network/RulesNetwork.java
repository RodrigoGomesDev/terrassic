package com.terrassic.network;

import com.mojang.brigadier.Command;
import com.terrassic.Terrassic;
import com.terrassic.config.Rules;
import dev.architectury.event.events.common.CommandRegistrationEvent;
import dev.architectury.event.events.common.PlayerEvent;
import dev.architectury.event.events.common.TickEvent;
import dev.architectury.networking.NetworkManager;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

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
        PlayerEvent.PLAYER_QUIT.register(p -> TOLD.remove(p.getUUID()));
        TickEvent.SERVER_POST.register(RulesNetwork::watchPermissions);
        CommandRegistrationEvent.EVENT.register((dispatcher, registry, selection) -> {
            for (String name : new String[]{"regras", "rules", "reglas"}) {
                dispatcher.register(Commands.literal(Terrassic.MOD_ID).then(Commands.literal(name).executes(ctx -> {
                    ServerPlayer player = ctx.getSource().getPlayerOrException();
                    // everyone may look; only canEdit saves (the screen opens read-only for the others)
                    sync(player);
                    NetworkManager.sendToPlayer(player, OPEN, Net.buf(player.registryAccess()));
                    return Command.SINGLE_SUCCESS;
                })));
            }
        });
    }

    /**
     * v1.6 (Rodrigo, 02/11/2026): on a server only an operator (level 2, the one of /gamemode); in single player only
     * with cheats on (the owner is then an operator) or in creative mode. Replaces the v0.15.1 lock
     * ("regras_no_jogo"), which kept everyone out.
     */
    public static boolean canEdit(ServerPlayer player) {
        return player.hasPermissions(2)
                || player.isCreative() && player.server.isSingleplayerOwner(player.getGameProfile());
    }

    /** What each player was last told about editing, so the pause button follows /op, /deop and /gamemode. */
    private static final Map<UUID, Boolean> TOLD = new HashMap<>();

    private static void watchPermissions(MinecraftServer server) {
        if (server.getTickCount() % 40 != 0) {
            return;
        }
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            Boolean told = TOLD.get(p.getUUID());
            if (told != null && told != canEdit(p)) {
                sync(p);
            }
        }
    }

    public static void sync(ServerPlayer player) {
        RegistryFriendlyByteBuf buf = Net.buf(player.registryAccess());
        buf.writeNbt(Rules.of(player.server).save());
        boolean edit = canEdit(player);
        TOLD.put(player.getUUID(), edit);
        buf.writeBoolean(edit);
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
