package com.terrassic.client;

import com.terrassic.client.ui.TerrassicFonts;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.item.FieldLensItem;
import com.terrassic.network.LensNetwork;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.ChatFormatting;
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
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The Field Lens panel (item/FieldLensItem): while the player holds the lens, the dinosaur under the crosshair (up to
 * {@link LensNetwork#RANGE} blocks, not through walls) is asked for every 5 ticks and its card is drawn to the right of
 * the crosshair: name and sex, age and size, wild or whose, health and hunger, and how to tame it. A knocked-out wild
 * animal adds the torpor (with the time until it wakes), the taming progress and the effectiveness; its food is shown
 * as item icons. The card fades a second after the lens leaves it.
 */
public final class LensOverlay {
    private static final int MIN_W = 150;
    private static int W = MIN_W;
    private static final int TORPOR = 0xFF8A6FC8;
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
        ClientGuiEvent.RENDER_HUD.register(LensOverlay::render);
    }

    private static void tick(Minecraft mc) {
        LocalPlayer player = mc.player;
        if (player == null || mc.level == null || !FieldLensItem.holding(player)) {
            target = -1;
            info = null;
            return;
        }
        if (++tick % 5 != 0) {
            return;
        }
        DinosaurEntity seen = look(player);
        if (seen != null) {
            target = seen.getId();
            linger = 4;
            FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
            buf.writeVarInt(target);
            NetworkManager.sendToServer(LensNetwork.ASK, buf);
        } else if (--linger <= 0) {
            target = -1;
        }
    }

    /** The dinosaur under the crosshair, not through blocks. */
    private static DinosaurEntity look(LocalPlayer player) {
        Vec3 eye = player.getEyePosition();
        Vec3 end = eye.add(player.getViewVector(1.0F).scale(LensNetwork.RANGE));
        HitResult block = player.level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        if (block.getType() != HitResult.Type.MISS) {
            end = block.getLocation();
        }
        AABB box = player.getBoundingBox().expandTowards(end.subtract(eye)).inflate(1.0D);
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end, box,
                e -> e instanceof DinosaurEntity && e.isAlive(), eye.distanceToSqr(end));
        return hit != null && hit.getEntity() instanceof DinosaurEntity d ? d : null;
    }

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
        int rows = 5 + (tame ? 1 : 2) + (ko ? 3 : t.getFloat("Torpor") > 0.5F ? 1 : 0) + (t.contains("CargoSize") ? 1 : 0);
        int h = 8 + rows * 11 + 4;
        // as wide as the longest line (the taming hint is the long one)
        String how = ko ? "gui.terrassic.lens.how_feed_now" : "feed".equals(t.getString("Method"))
                ? "gui.terrassic.lens.how_feed" : "gui.terrassic.lens.how_knockout";
        W = Math.max(MIN_W, font.width(TerrassicFonts.ui(how)) + 14);
        int x = g.guiWidth() / 2 + 16;
        int y = Mth.clamp(g.guiHeight() / 2 - h / 2, 4, Math.max(4, g.guiHeight() - h - 30));
        panel(g, x, y, x + W, y + h);
        int cx = x + 6;
        int cy = y + 6;

        // name and sex
        Component sex = Component.literal(t.getBoolean("Female") ? " ♀" : " ♂")
                .withStyle(t.getBoolean("Female") ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.AQUA);
        g.drawString(font, TerrassicFonts.ui(d.getDisplayName().copy()).append(sex), cx, cy, TerrassicPalette.rgb(TerrassicPalette.BONE_100));
        cy += 11;
        Component age = t.getBoolean("Baby")
                ? Component.translatable("gui.terrassic.lens.young", Math.round(t.getFloat("Growth") * 100))
                : Component.translatable("gui.terrassic.lens.adult", Math.round(t.getFloat("Size") * 100));
        g.drawString(font, TerrassicFonts.ui(age), cx, cy, TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        cy += 11;
        Component who = !tame ? Component.translatable("gui.terrassic.lens.wild")
                : t.getBoolean("Mine") ? Component.translatable("gui.terrassic.lens.yours")
                : Component.translatable("gui.terrassic.lens.owner", t.getString("Owner"));
        g.drawString(font, TerrassicFonts.ui(who), cx, cy, tame ? TerrassicPalette.rgb(TerrassicPalette.FERN_400) : TerrassicPalette.rgb(TerrassicPalette.AMBER_500));
        cy += 11;

        // health and hunger
        bar(g, font, cx, cy, Component.translatable("gui.terrassic.lens.health"), t.getFloat("Health") / t.getFloat("MaxHealth"),
                TerrassicPalette.BLOOD_500, Mth.ceil(t.getFloat("Health")) + "/" + Mth.ceil(t.getFloat("MaxHealth")));
        cy += 11;
        bar(g, font, cx, cy, Component.translatable("gui.terrassic.lens.hunger"), t.getInt("Hunger") / (float) DinosaurEntity.MAX_HUNGER,
                TerrassicPalette.AMBER_600, t.getInt("Hunger") + "%");
        cy += 11;

        if (ko) {
            int secs = t.getInt("WakeSeconds");
            bar(g, font, cx, cy, Component.translatable("gui.terrassic.lens.torpor"), t.getFloat("Torpor") / t.getFloat("MaxTorpor"),
                    TORPOR, secs / 60 + ":" + String.format("%02d", secs % 60));
            cy += 11;
            float progress = Math.min(1.0F, t.getFloat("Progress") / t.getFloat("Goal"));
            bar(g, font, cx, cy, Component.translatable("gui.terrassic.lens.taming"), progress, TerrassicPalette.FERN_400,
                    Math.round(progress * 100) + "%");
            cy += 11;
            g.drawString(font, TerrassicFonts.ui("gui.terrassic.lens.effectiveness", t.getInt("Effectiveness")), cx, cy,
                    TerrassicPalette.rgb(TerrassicPalette.STONE_200));
            cy += 11;
        } else if (!tame && t.getFloat("Torpor") > 0.5F) {
            bar(g, font, cx, cy, Component.translatable("gui.terrassic.lens.torpor"), t.getFloat("Torpor") / t.getFloat("MaxTorpor"),
                    TORPOR, Mth.ceil(t.getFloat("Torpor")) + "/" + Mth.ceil(t.getFloat("MaxTorpor")));
            cy += 11;
        }

        if (!tame) {
            g.drawString(font, TerrassicFonts.ui(how), cx, cy, TerrassicPalette.rgb(TerrassicPalette.AMBER_300));
            cy += 11;
            foods(g, font, t, cx, cy);
            cy += 11;
        } else {
            foods(g, font, t, cx, cy);
            cy += 11;
        }
        if (t.contains("CargoSize")) {
            g.drawString(font, TerrassicFonts.ui("gui.terrassic.lens.cargo", t.getInt("CargoUsed"), t.getInt("CargoSize")), cx, cy,
                    TerrassicPalette.rgb(TerrassicPalette.STONE_200));
        }
    }

    private static void panel(GuiGraphics g, int x0, int y0, int x1, int y1) {
        g.fill(x0, y0, x1, y1, TerrassicPalette.alpha(TerrassicPalette.BASALT_900, 0xD8));
        g.fill(x0, y0, x1, y0 + 1, TerrassicPalette.AMBER_700);
        g.fill(x0, y1 - 1, x1, y1, TerrassicPalette.alpha(TerrassicPalette.AMBER_700, 0x90));
        g.fill(x0, y0, x0 + 1, y1, TerrassicPalette.alpha(TerrassicPalette.AMBER_700, 0x90));
        g.fill(x1 - 1, y0, x1, y1, TerrassicPalette.alpha(TerrassicPalette.AMBER_700, 0x90));
    }

    /** A label, then a bar with its value written at the right. */
    private static void bar(GuiGraphics g, Font font, int x, int y, Component label, float fraction, int colour, String value) {
        g.drawString(font, TerrassicFonts.ui(label), x, y, TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        int bx = x + 52;
        int bw = W - 12 - 52;
        g.fill(bx, y + 1, bx + bw, y + 8, TerrassicPalette.BASALT_950);
        int fill = Math.round((bw - 2) * Mth.clamp(fraction, 0.0F, 1.0F));
        g.fill(bx + 1, y + 2, bx + 1 + fill, y + 7, colour);
        g.fill(bx + 1, y + 2, bx + 1 + fill, y + 3, (colour & 0x00FFFFFF) | 0x50FFFFFF);
        g.drawString(font, value, bx + bw - font.width(value) - 2, y + 1, 0xFFFFFFFF, true);
    }

    /** "Eats:" and the accepted foods as item icons (at half size). */
    private static void foods(GuiGraphics g, Font font, CompoundTag t, int x, int y) {
        g.drawString(font, TerrassicFonts.ui("gui.terrassic.lens.eats"), x, y, TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        int ix = x + 52;
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
