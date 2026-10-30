package com.terrassic.client;

import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.item.FieldLensItem;
import com.terrassic.network.LensNetwork;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientPlayerEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * The Field Lens panel (item/FieldLensItem): while the player holds the lens, the dinosaur under the crosshair (up to
 * {@link LensNetwork#RANGE} blocks, not through walls) is asked for every 5 ticks and its card is drawn to the right of
 * the crosshair: name and sex, age and size, wild or whose, health and hunger, and how to tame it. A knocked-out wild
 * animal adds the torpor (with the time until it wakes), the taming progress and the effectiveness; its food is shown
 * as item icons. The card fades a second after the lens leaves it. Since v0.14.1 it has the HUD's Âmbar look
 * (docs/HUD.md).
 */
public final class LensOverlay {
    private static final int MIN_W = 172;
    private static int W = MIN_W;
    private static int target = -1;
    private static int infoId = -1;
    private static CompoundTag info;
    private static int linger;
    private static int tick;

    private LensOverlay() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, LensNetwork.INFO, (buf, context) -> {
            int id = buf.readVarInt();
            CompoundTag tag = buf.readNbt();
            context.queue(() -> {
                infoId = id;
                info = tag;
            });
        });
        ClientTickEvent.CLIENT_POST.register(LensOverlay::tick);
        ClientPlayerEvent.CLIENT_PLAYER_JOIN.register(player -> info = null);
        ClientGuiEvent.RENDER_HUD.register(LensOverlay::render);
    }

    private static void tick(Minecraft mc) {
        LocalPlayer player = mc.player;
        if (player == null || mc.level == null || !FieldLensItem.holding(player)) {
            target = -1;
            return;
        }
        if (++tick % 5 != 0) {
            return;
        }
        DinosaurEntity seen = look(player, LensNetwork.RANGE);
        if (seen != null) {
            target = seen.getId();
            linger = 4;
            ask(target);
        } else if (--linger <= 0) {
            target = -1;
        }
    }

    /** Asks the server for the animal's card (the answer lands in {@link #infoFor}). */
    static void ask(int id) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeVarInt(id);
        NetworkManager.sendToServer(LensNetwork.ASK, buf);
    }

    /** The Lupa card is on screen (HudNotices waits while it is: both sit in the middle of the right side). */
    static boolean showing() {
        return info != null && target >= 0 && infoId == target;
    }

    /** The last card the server sent for this animal, or null. */
    static CompoundTag infoFor(int id) {
        return infoId == id ? info : null;
    }

    /** The dinosaur under the crosshair within {@code range} blocks, not through blocks. */
    static DinosaurEntity look(LocalPlayer player, double range) {
        Vec3 eye = player.getEyePosition();
        Vec3 end = eye.add(player.getViewVector(1.0F).scale(range));
        HitResult block = player.level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        if (block.getType() != HitResult.Type.MISS) {
            end = block.getLocation();
        }
        AABB box = player.getBoundingBox().expandTowards(end.subtract(eye)).inflate(4.0D);
        DinosaurEntity best = null;
        double bestDistance = Double.MAX_VALUE;
        for (DinosaurEntity d : player.level().getEntitiesOfClass(DinosaurEntity.class, box, Entity::isAlive)) {
            // a flyer's body is small against its wingspan: aim at it with a wider box, a little more for far ones
            double grow = d instanceof com.terrassic.entity.FlyingDinosaur
                    ? Math.max(1.0D, d.getBbWidth() * 0.6D) + eye.distanceTo(d.position()) * 0.03D : 0.3D;
            java.util.Optional<Vec3> at = d.getBoundingBox().inflate(grow).clip(eye, end);
            if (at.isPresent() && eye.distanceToSqr(at.get()) < bestDistance) {
                bestDistance = eye.distanceToSqr(at.get());
                best = d;
            }
        }
        return best;
    }

    /**
     * The card in the Âmbar look (v0.14.1, docs/HUD.md; study: dirF.py lens()): a basalt slab, the animal in a drop of
     * amber, name and level, age and size, wild or whose; then the bars cut into the stone (health, food, and on a
     * knocked-out animal torpor and taming) and the lines under them.
     */
    private static void render(GuiGraphics g, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.options.hideGui || mc.level == null || info == null || target < 0 || infoId != target) {
            return;
        }
        Entity e = mc.level.getEntity(target);
        if (!(e instanceof DinosaurEntity d)) {
            return;
        }
        Font font = mc.font;
        CompoundTag t = info;
        boolean ko = t.getBoolean("KnockedOut");
        boolean tame = t.getBoolean("Tame");
        int points = t.getInt("Points");
        boolean torpor = !ko && !tame && t.getFloat("Torpor") > 0.5F;

        Component name = d.hasCustomName() ? d.getCustomName() : d.getType().getDescription();
        Component dot = Component.literal(name.getString() + " · ");
        Component level = Component.translatable("hud.terrassic.level", Math.max(1, d.getLevel()));
        Component age = t.getBoolean("Baby")
                ? Component.translatable("gui.terrassic.lens.young", Math.round(t.getFloat("Growth") * 100))
                : Component.translatable("gui.terrassic.lens.adult", Math.round(t.getFloat("Size") * 100));
        Component who = !tame ? Component.translatable("gui.terrassic.lens.wild")
                : t.getBoolean("Mine") ? Component.translatable("gui.terrassic.lens.yours")
                : Component.translatable("gui.terrassic.lens.owner", t.getString("Owner"));
        List<Component> lines = new ArrayList<>();
        List<Integer> colours = new ArrayList<>();
        if (ko) {
            lines.add(Component.translatable("gui.terrassic.lens.effectiveness_levels", t.getInt("Effectiveness"), t.getInt("BonusLevels")));
            colours.add(TerrassicPalette.AMBER_500);
        }
        if (!tame) {
            lines.add(howToTame(t, ko));
            colours.add(ko ? 0xFFC2B0EE : TerrassicPalette.AMBER_300);
        }
        if (t.contains("CargoSize")) {
            lines.add(Component.translatable("gui.terrassic.lens.cargo", t.getInt("CargoUsed"), t.getInt("CargoSize")));
            colours.add(TerrassicPalette.STONE_200);
        }
        if (points > 0) {
            lines.add(Component.translatable("gui.terrassic.lens.points", points));
            colours.add(TerrassicPalette.AMBER_300);
        }
        int bars = 2 + (ko ? 2 : torpor ? 1 : 0);
        // as wide as the longest line, 172 at least
        int w = Math.max(MIN_W, 33 + AmberHud.width(font, dot) + AmberHud.width(font, level) + 16);
        w = Math.max(w, 33 + Math.max(AmberHud.width(font, age), AmberHud.width(font, who)) + 6);
        for (Component line : lines) {
            w = Math.max(w, AmberHud.width(font, line) + 12);
        }
        W = w;
        int h = 38 + bars * 10 + 2 + (lines.size() + 1) * 10 + 4;
        // beside the crosshair, but never past the right edge (a long name with its level on a small window)
        int x = Math.max(4, Math.min(g.guiWidth() / 2 + 16, g.guiWidth() - w - 4));
        int y = Mth.clamp(g.guiHeight() / 2 - h / 2, 4, Math.max(4, g.guiHeight() - h - 30));
        AmberHud.slab(g, "lens_" + w + "_" + h, x, y, 0, 4, 4, 0, w, 0, w, h - 4, w - 4, h, 30, h, 26, h - 2, 0, h - 2);
        AmberHud.amberDrop(g, x + 16, y + 18, 13, 13, 4, () -> TerrassicHud.portrait(g, d, x + 4, y + 8, 24, 22));

        // name, level and sex; age and size; wild or whose
        int nx = AmberHud.text(g, font, dot, x + 33, y + 5, TerrassicPalette.BONE_100);
        AmberHud.text(g, font, level, nx, y + 5, TerrassicPalette.AMBER_500);
        boolean female = t.getBoolean("Female");
        AmberHud.text(g, font, Component.literal(female ? "♀" : "♂"), x + w - 12, y + 5, female ? 0xFFE58AC0 : 0xFF7FB4E8);
        AmberHud.text(g, font, age, x + 33, y + 15, TerrassicPalette.STONE_300);
        AmberHud.text(g, font, who, x + 33, y + 24, tame ? TerrassicPalette.FERN_400 : TerrassicPalette.RIFT_500);

        // the bars
        int yy = y + 38;
        bar(g, font, x, yy, w, Component.translatable("gui.terrassic.lens.health"), t.getFloat("Health") / t.getFloat("MaxHealth"),
                AmberHud.RED, Mth.ceil(t.getFloat("Health")) + "/" + Mth.ceil(t.getFloat("MaxHealth")));
        yy += 10;
        bar(g, font, x, yy, w, Component.translatable("gui.terrassic.lens.hunger"), t.getInt("Hunger") / (float) DinosaurEntity.MAX_HUNGER,
                AmberHud.AMBER, t.getInt("Hunger") + "%");
        yy += 10;
        if (ko) {
            int secs = t.getInt("WakeSeconds");
            bar(g, font, x, yy, w, Component.translatable("gui.terrassic.lens.torpor"), t.getFloat("Torpor") / t.getFloat("MaxTorpor"),
                    AmberHud.TORPOR, secs / 60 + ":" + String.format("%02d", secs % 60));
            yy += 10;
            float progress = Math.min(1.0F, t.getFloat("Progress") / t.getFloat("Goal"));
            bar(g, font, x, yy, w, Component.translatable("gui.terrassic.lens.taming"), progress, AmberHud.FERN,
                    Math.round(progress * 100) + "%");
            yy += 10;
        } else if (torpor) {
            bar(g, font, x, yy, w, Component.translatable("gui.terrassic.lens.torpor"), t.getFloat("Torpor") / t.getFloat("MaxTorpor"),
                    AmberHud.TORPOR, Mth.ceil(t.getFloat("Torpor")) + "/" + Mth.ceil(t.getFloat("MaxTorpor")));
            yy += 10;
        }

        // the lines under them, then what it eats
        yy += 2;
        for (int i = 0; i < lines.size(); i++) {
            AmberHud.text(g, font, lines.get(i), x + 6, yy, colours.get(i));
            yy += 10;
        }
        foods(g, font, t, x + 6, yy);
    }

    /** How it is tamed: feeding (with the chance per bite), feeding or knockout, knockout, or "feed it now". */
    private static Component howToTame(CompoundTag t, boolean ko) {
        if (ko) {
            return Component.translatable("gui.terrassic.lens.how_feed_now");
        }
        return switch (t.getString("Method")) {
            case "feed" -> Component.translatable("gui.terrassic.lens.how_feed", t.getInt("Chance"));
            case "feed_or_knockout" -> Component.translatable("gui.terrassic.lens.how_feed_or_ko", t.getInt("Chance"));
            default -> Component.translatable("gui.terrassic.lens.how_knockout");
        };
    }

    /** A label, a bar cut into the stone and its value at the right (study: 80 px of groove on a 172 px card). */
    private static void bar(GuiGraphics g, Font font, int x, int y, int w, Component label, float fraction, int[] tones, String value) {
        AmberHud.text(g, font, label, x + 6, y - 1, TerrassicPalette.STONE_200);
        AmberHud.groove(g, x + 52, y, w - 92, fraction, tones);
        AmberHud.text(g, font, Component.literal(value), x + w - 36, y - 1, TerrassicPalette.BONE_100);
    }

    /** "Eats:" and the accepted foods as item icons (at half size). */
    private static void foods(GuiGraphics g, Font font, CompoundTag t, int x, int y) {
        AmberHud.text(g, font, Component.translatable("gui.terrassic.lens.eats"), x, y, TerrassicPalette.STONE_200);
        int ix = x + 30;
        for (Tag tag : t.getList("Foods", Tag.TAG_STRING)) {
            ItemStack stack = new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(tag.getAsString())));
            g.pose().pushPose();
            g.pose().translate(ix, y - 1, 0.0F);
            g.pose().scale(0.625F, 0.625F, 1.0F);
            g.renderItem(stack, 0, 0);
            g.pose().popPose();
            ix += 11;
        }
    }
}
