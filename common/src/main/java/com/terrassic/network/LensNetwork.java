package com.terrassic.network;

import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.item.FieldLensItem;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;

/**
 * Packets of the Field Lens ({@link FieldLensItem}):
 * <ul>
 *   <li>{@link #ASK} (client to server): the id of the dinosaur the player looks at through the lens.</li>
 *   <li>{@link #INFO} (server to client): that id and {@link DinosaurEntity#lensInfo} as NBT, only for a player holding
 *       the lens within {@link #RANGE} blocks.</li>
 * </ul>
 * The client receiver is registered in client/LensOverlay.
 */
public final class LensNetwork {
    public static final ResourceLocation ASK = Terrassic.id("lens_ask");
    public static final ResourceLocation INFO = Terrassic.id("lens_info");
    public static final double RANGE = 40.0D;

    private LensNetwork() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.C2S, ASK, (buf, context) -> {
            int id = buf.readVarInt();
            context.queue(() -> {
                if (context.getPlayer() instanceof ServerPlayer player && FieldLensItem.holding(player)
                        && player.level().getEntity(id) instanceof DinosaurEntity dino && dino.isAlive()
                        && dino.distanceToSqr(player) < RANGE * RANGE) {
                    FriendlyByteBuf out = new FriendlyByteBuf(Unpooled.buffer());
                    out.writeVarInt(id);
                    out.writeNbt(dino.lensInfo(player));
                    NetworkManager.sendToPlayer(player, INFO, out);
                }
            });
        });
    }
}
