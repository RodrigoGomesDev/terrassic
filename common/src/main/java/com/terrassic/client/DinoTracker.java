package com.terrassic.client;

import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.network.TamedNetwork;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientPlayerEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 1.7 (player feedback: "you can't see where your dinos are"): the client side of "My dinos". It keeps the last list
 * the server sent (network/TamedNetwork) and, while one animal is tracked, draws a small slab at the top of the screen
 * with an arrow pointing at it, its name and how far it is. The position is the live one while the animal is loaded
 * here, else the last one the server knows (asked again every five seconds while tracking).
 */
public final class DinoTracker {
    /** Arrows for the eight directions, clockwise from straight ahead. */
    private static final String[] ARROWS = {"↑", "↗", "→", "↘", "↓", "↙", "←", "↖"};
    /** Closer than this it is "here". */
    private static final double HERE = 6.0D;

    private static List<CompoundTag> dinos = new ArrayList<>();
    private static boolean received;
    private static UUID tracked;
    /** The tracked animal when it is loaded on this client (looked up every ten ticks). */
    private static Entity live;
    private static int ticks;

    private DinoTracker() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, TamedNetwork.LIST, (buf, context) -> {
            CompoundTag tag = buf.readNbt();
            context.queue(() -> receive(tag));
        });
        ClientGuiEvent.RENDER_HUD.register(DinoTracker::render);
        ClientTickEvent.CLIENT_POST.register(DinoTracker::tick);
        ClientPlayerEvent.CLIENT_PLAYER_QUIT.register(player -> {
            tracked = null;
            live = null;
            dinos = new ArrayList<>();
            received = false;
        });
    }

    /** Asks the server for the list again. */
    static void ask() {
        NetworkManager.sendToServer(TamedNetwork.ASK, new FriendlyByteBuf(Unpooled.buffer()));
    }

    private static void receive(CompoundTag tag) {
        List<CompoundTag> list = new ArrayList<>();
        if (tag != null) {
            ListTag l = tag.getList("Dinos", Tag.TAG_COMPOUND);
            for (int i = 0; i < l.size(); i++) {
                list.add(l.getCompound(i));
            }
        }
        dinos = list;
        received = true;
        if (tracked != null && entry(tracked) == null) {
            tracked = null;   // it died or is no longer yours
            live = null;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.screen instanceof MyDinosScreen screen) {
            screen.refresh();
        }
    }

    static List<CompoundTag> dinos() {
        return dinos;
    }

    static boolean received() {
        return received;
    }

    static UUID tracked() {
        return tracked;
    }

    /** Tracks this animal, or stops when it is the one tracked already. */
    static void toggle(UUID id) {
        tracked = id.equals(tracked) ? null : id;
        live = null;
        ticks = 0;
    }

    static CompoundTag entry(UUID id) {
        for (CompoundTag t : dinos) {
            if (t.hasUUID("Dino") && t.getUUID("Dino").equals(id)) {
                return t;
            }
        }
        return null;
    }

    private static void tick(Minecraft mc) {
        if (mc.player == null || mc.level == null) {
            return;
        }
        ticks++;
        boolean screen = mc.screen instanceof MyDinosScreen;
        if (tracked != null && ticks % 100 == 0 || screen && ticks % 40 == 0) {
            ask();
        }
        if (tracked != null && ticks % 10 == 0) {
            live = null;
            for (Entity e : mc.level.entitiesForRendering()) {
                if (e instanceof DinosaurEntity && tracked.equals(e.getUUID())) {
                    live = e;
                    break;
                }
            }
        }
    }

    /** Where the entry is now: the live animal if this client sees it, else the last position the server sent. */
    static Vec3 position(CompoundTag t) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level != null && t.hasUUID("Dino")) {
            UUID id = t.getUUID("Dino");
            if (live != null && live.isAlive() && id.equals(live.getUUID())) {
                return live.position();
            }
        }
        return Vec3.atBottomCenterOf(BlockPos.of(t.getLong("Pos")));
    }

    /** Whether the entry is in the dimension the player is in. */
    static boolean sameDimension(CompoundTag t) {
        Minecraft mc = Minecraft.getInstance();
        return mc.level != null && mc.level.dimension().location().toString().equals(t.getString("Dim"));
    }

    /** The arrow from the player's facing to that point. */
    static String arrow(LocalPlayer player, Vec3 to) {
        double dx = to.x - player.getX();
        double dz = to.z - player.getZ();
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        float rel = Mth.wrapDegrees(yaw - player.getYRot());
        int index = Math.floorMod(Math.round(rel / 45.0F), 8);
        return ARROWS[index];
    }

    /** The animal's name: its own, or the species'. */
    static Component name(CompoundTag t) {
        return t.getString("Name").isEmpty() ? Component.translatable("entity.terrassic." + t.getString("Species"))
                : Component.literal(t.getString("Name"));
    }

    private static void render(GuiGraphics g, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (tracked == null || player == null || mc.level == null || mc.options.hideGui) {
            return;
        }
        CompoundTag t = entry(tracked);
        if (t == null) {
            return;
        }
        Component line;
        String arrow = "";
        if (!sameDimension(t)) {
            line = Component.translatable("hud.terrassic.track.dimension", name(t));
        } else {
            Vec3 to = position(t);
            double dist = Math.sqrt(player.distanceToSqr(to.x, player.getY(), to.z));
            if (dist < HERE) {
                line = Component.translatable("hud.terrassic.track.here", name(t));
            } else {
                line = Component.translatable("hud.terrassic.track.distance", name(t), (int) Math.round(dist));
                arrow = arrow(player, to);
            }
        }
        var font = mc.font;
        int arrowW = arrow.isEmpty() ? 0 : font.width(arrow) + 6;
        int w = (AmberHud.width(font, line) + arrowW + 14 + 7) / 8 * 8;   // whole steps of 8: few baked slabs
        int x = (g.guiWidth() - w) / 2;
        int y = 4;
        AmberHud.slab(g, "dino_tracker_" + w, x, y, 3, 0, w - 3, 0, w, 3, w, 13, w - 3, 16, 3, 16, 0, 13, 0, 3);
        int tx = x + 7;
        if (!arrow.isEmpty()) {
            g.drawString(font, arrow, tx, y + 4, TerrassicPalette.AMBER_300, true);
            tx += arrowW;
        }
        AmberHud.text(g, font, line, tx, y + 4, TerrassicPalette.BONE_100);
    }
}
