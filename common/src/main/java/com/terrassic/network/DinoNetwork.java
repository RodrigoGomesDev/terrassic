package com.terrassic.network;

import com.terrassic.Terrassic;
import com.terrassic.entity.ApexTheropod;
import com.terrassic.entity.DinosaurEntity;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;

/**
 * Packets of the dino screen and of the mounted controls (v0.12, client/DinoScreen and client/DinoControls):
 * <ul>
 *   <li>{@link #ASK} (client to server): open the screen of this dinosaur (-1 = the one the player rides).</li>
 *   <li>{@link #SCREEN} (server to client): its id and {@link DinosaurEntity#screenInfo} as NBT; opens or refreshes the
 *       screen. Also sent when the owner sneaks and uses an empty hand on it.</li>
 *   <li>{@link #ORDER} (client to server): an order from the screen ({@link DinosaurEntity#screenOrder}).</li>
 *   <li>{@link #MOUNT} (client to server): the rider's attack ("attack") or the mount's special ("special").</li>
 * </ul>
 * Only the owner gets the screen and gives orders, within {@link #RANGE} blocks or riding it.
 */
public final class DinoNetwork {
    public static final ResourceLocation ASK = Terrassic.id("dino_ask");
    public static final ResourceLocation SCREEN = Terrassic.id("dino_screen");
    public static final ResourceLocation ORDER = Terrassic.id("dino_order");
    public static final ResourceLocation MOUNT = Terrassic.id("dino_mount");
    public static final double RANGE = 12.0D;

    private DinoNetwork() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.C2S, ASK, (buf, context) -> {
            int id = buf.readVarInt();
            context.queue(() -> {
                if (context.getPlayer() instanceof ServerPlayer player) {
                    DinosaurEntity dino = id < 0 ? (player.getVehicle() instanceof DinosaurEntity d ? d : null) : owned(player, id);
                    if (dino != null && dino.isTame() && dino.isOwnedBy(player)) {
                        sendScreen(player, dino);
                    }
                }
            });
        });
        NetworkManager.registerReceiver(NetworkManager.Side.C2S, ORDER, (buf, context) -> {
            int id = buf.readVarInt();
            String order = buf.readUtf(32);
            context.queue(() -> {
                if (context.getPlayer() instanceof ServerPlayer player) {
                    DinosaurEntity dino = owned(player, id);
                    if (dino != null && dino.screenOrder(player, order)) {
                        sendScreen(player, dino);
                    }
                }
            });
        });
        NetworkManager.registerReceiver(NetworkManager.Side.C2S, MOUNT, (buf, context) -> {
            String action = buf.readUtf(32);
            context.queue(() -> {
                if (context.getPlayer() instanceof ServerPlayer player && player.getVehicle() instanceof DinosaurEntity dino
                        && dino.isTame() && dino.isOwnedBy(player) && dino.getControllingPassenger() == player) {
                    if (action.equals("attack")) {
                        dino.riderAttack(player);
                    } else if (action.equals("special") && dino instanceof ApexTheropod apex) {
                        apex.riderRoar();
                    }
                }
            });
        });
    }

    /** The player's own living tame with that id, within reach (or ridden by them); null otherwise. */
    private static DinosaurEntity owned(ServerPlayer player, int id) {
        if (player.level().getEntity(id) instanceof DinosaurEntity dino && dino.isAlive() && dino.isTame() && dino.isOwnedBy(player)
                && (dino.hasPassenger(player) || dino.distanceToSqr(player) < RANGE * RANGE)) {
            return dino;
        }
        return null;
    }

    public static void sendScreen(ServerPlayer player, DinosaurEntity dino) {
        FriendlyByteBuf out = new FriendlyByteBuf(Unpooled.buffer());
        out.writeVarInt(dino.getId());
        out.writeNbt(dino.screenInfo(player));
        NetworkManager.sendToPlayer(player, SCREEN, out);
    }
}
