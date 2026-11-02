package com.terrassic.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.terrassic.entity.ApexTheropod;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.network.DinoNetwork;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import dev.architectury.registry.client.keymappings.KeyMappingRegistry;
import io.netty.buffer.Unpooled;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.EntityHitResult;
import org.lwjgl.glfw.GLFW;

/**
 * The mod's keys (Options > Controls > "Terrassic") and the mounted controls (v0.12). Few new keys on purpose, so the
 * mod sits well in modpacks; riding your own dinosaur, the keys you already use take its side:
 * <ul>
 *   <li>The inventory key opens the dino screen (client/DinoScreen); the player's own inventory is a button there.</li>
 *   <li>A left click is the mount's attack: it strikes what is in front of it, nearest to where you look
 *       (config/terrassic-client.json "mount_attack": false gives the click back to your hand).</li>
 *   <li>A right click with an empty hand is its special: the roar of the big theropods.</li>
 *   <li>{@link #DESCEND} (Z) dives a flyer; in the air sneak does the same (mixin/PlayerMixin keeps you in the
 *       saddle), on the ground it gets off.</li>
 * </ul>
 * {@link #WHISTLE} (H), held, opens the whistle wheel (1.5, client/WhistleWheelScreen): one order for all your dinos
 * that hear it. H was checked against popular mods (docs/ORDENS.md): only Mekanism uses it, for the MekaSuit HUD.
 * On foot, sneak + use with an empty hand on your dinosaur opens its screen. {@link #DINO_SCREEN} does the same for the
 * one you look at; it has no key by default (bind one in Controls if you like).
 */
public final class DinoControls {
    public static final String CATEGORY = "key.categories.terrassic";
    public static final KeyMapping DINO_SCREEN = new KeyMapping("key.terrassic.dino_screen", InputConstants.Type.KEYSYM,
            InputConstants.UNKNOWN.getValue(), CATEGORY);
    public static final KeyMapping DESCEND = new KeyMapping("key.terrassic.descend", InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_Z, CATEGORY);
    public static final KeyMapping WHISTLE = new KeyMapping("key.terrassic.whistle", InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_H, CATEGORY);

    private DinoControls() {
    }

    public static void init() {
        KeyMappingRegistry.register(DINO_SCREEN);
        KeyMappingRegistry.register(DESCEND);
        KeyMappingRegistry.register(WHISTLE);
        // before vanilla reads the keys of this tick, so the clicks taken here never reach it
        ClientTickEvent.CLIENT_PRE.register(DinoControls::tick);
    }

    private static void tick(Minecraft mc) {
        LocalPlayer player = mc.player;
        if (player == null || mc.level == null) {
            return;
        }
        DinosaurEntity mount = player.getVehicle() instanceof DinosaurEntity d && d.isTame() && d.isOwnedBy(player)
                && d.getControllingPassenger() == player ? d : null;
        if (player.getVehicle() instanceof FlyingDinosaur flyer) {
            flyer.riderDescending = mount == flyer && mc.screen == null && (DESCEND.isDown() || mc.options.keyShift.isDown());
        }
        if (mc.screen != null) {
            // a whistle press under any screen (the wheel's own included) must not open the wheel once it closes
            while (WHISTLE.consumeClick()) {
                wheelClosedAt = mc.level.getGameTime();
            }
            return;
        }
        boolean whistle = false;
        while (WHISTLE.consumeClick()) {
            whistle = true;
        }
        long now = mc.level.getGameTime();
        if (whistle && (now - wheelClosedAt > 2L || now < wheelClosedAt)) {
            // the wheel stays while the key is held and gives the order when it is let go
            mc.setScreen(new WhistleWheelScreen());
            return;
        }
        while (DINO_SCREEN.consumeClick()) {
            if (mount != null) {
                ask(-1);
            } else if (mc.hitResult instanceof EntityHitResult hit && hit.getEntity() instanceof DinosaurEntity d
                    && d.isTame() && d.isOwnedBy(player)) {
                ask(d.getId());
            }
        }
        if (mount == null) {
            return;
        }
        while (mc.options.keyInventory.consumeClick()) {
            ask(-1);
        }
        if (ClientConfig.flag("mount_attack")) {
            while (mc.options.keyAttack.consumeClick()) {
                mount("attack");
            }
        }
        if (mount instanceof ApexTheropod && player.getMainHandItem().isEmpty()) {
            while (mc.options.keyUse.consumeClick()) {
                mount("special");
            }
        }
    }

    /** Asks the server for the screen of a dinosaur (-1 = the one ridden). */
    static void ask(int id) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeVarInt(id);
        NetworkManager.sendToServer(DinoNetwork.ASK, buf);
    }

    /** Blows the whistle with an order of the wheel (network/DinoNetwork, entity/Whistle). */
    /** When the whistle wheel last closed (game time): the press that closed it does not reopen it. */
    private static long wheelClosedAt = Long.MIN_VALUE / 2;

    static void wheelClosed() {
        Minecraft mc = Minecraft.getInstance();
        wheelClosedAt = mc.level != null ? mc.level.getGameTime() : Long.MIN_VALUE / 2;
    }

    static void whistle(String order) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeUtf(order);
        NetworkManager.sendToServer(DinoNetwork.WHISTLE, buf);
    }

    private static void mount(String action) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeUtf(action);
        NetworkManager.sendToServer(DinoNetwork.MOUNT, buf);
    }
}
