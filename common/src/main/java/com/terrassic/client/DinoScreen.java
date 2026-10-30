package com.terrassic.client;

import com.terrassic.client.ui.TerrassicButton;
import com.terrassic.client.ui.TerrassicFonts;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.client.ui.TerrassicUi;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.network.DinoNetwork;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

/**
 * The dino screen (v0.12): your tamed dinosaur at a glance, and the orders it takes. Opened with sneak + use (empty
 * hand) on it, with the inventory key while riding it, or with the "Dino screen" key (client/DinoControls).
 * <p>
 * A basalt slab (client/ui/TerrassicUi): on the left the animal itself, turning with the mouse; on the right its name
 * and sex, species, age and size, health and fullness, saddle and cargo; at the bottom the orders: follow or wait,
 * open the cargo, hop onto the shoulder, and your own inventory while riding. The values come from the server
 * ({@link DinosaurEntity#screenInfo}) and are sent again after every order. A line at the foot names the mounted
 * controls with the keys the player has bound.
 * <p>
 * Room is left in the layout for the levels and stats of v0.13.
 */
public class DinoScreen extends Screen {
    private static final int W = 252;
    private static final int H = 156;
    private static final int PORTRAIT = 84;

    private final int dinoId;
    private CompoundTag info;
    private int left;
    private int top;

    public DinoScreen(int dinoId, CompoundTag info) {
        super(Component.translatable("gui.terrassic.dino.title"));
        this.dinoId = dinoId;
        this.info = info;
    }

    public static void register() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, DinoNetwork.SCREEN, (buf, context) -> {
            int id = buf.readVarInt();
            CompoundTag tag = buf.readNbt();
            context.queue(() -> {
                Minecraft mc = Minecraft.getInstance();
                if (mc.screen instanceof DinoScreen open && open.dinoId == id) {
                    open.info = tag;
                    open.rebuildWidgets();
                } else if (mc.screen == null || mc.screen instanceof DinoScreen) {
                    mc.setScreen(new DinoScreen(id, tag));
                }
            });
        });
    }

    private DinosaurEntity dino() {
        return this.minecraft != null && this.minecraft.level != null
                && this.minecraft.level.getEntity(this.dinoId) instanceof DinosaurEntity d && d.isAlive() ? d : null;
    }

    @Override
    protected void init() {
        this.left = (this.width - W) / 2;
        this.top = (this.height - H) / 2;
        int bx = this.left + 10;
        int by = this.top + H - 30;
        int gap = 4;
        boolean sitting = this.info.getBoolean("Sitting");
        // the order it is under shows as the selected one; the other is the action
        bx += this.order(bx, by, 54, "gui.terrassic.dino.follow", "follow", !sitting) + gap;
        bx += this.order(bx, by, 54, "gui.terrassic.dino.wait", "sit", sitting) + gap;
        if (this.info.getBoolean("HasCargo")) {
            bx += this.order(bx, by, 54, "gui.terrassic.dino.cargo", "cargo", false) + gap;
        }
        if (this.info.getBoolean("CanPerch") && !this.info.getBoolean("Ridden")) {
            bx += this.order(bx, by, 54, "gui.terrassic.dino.perch", "perch", false) + gap;
        }
        if (this.info.getBoolean("Ridden") && this.minecraft != null && this.minecraft.player != null) {
            this.addRenderableWidget(TerrassicButton.stone(bx, by, 54, 18, Component.translatable("gui.terrassic.dino.backpack"),
                    b -> this.minecraft.setScreen(new InventoryScreen(this.minecraft.player))));
        }
    }

    /** An order button; returns its width. */
    private int order(int x, int y, int w, String label, String order, boolean selected) {
        this.addRenderableWidget(new TerrassicButton(x, y, w, 18, Component.translatable(label), b -> this.send(order),
                selected ? TerrassicButton.Kind.PRIMARY : TerrassicButton.Kind.STONE, selected));
        return w;
    }

    private void send(String order) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeVarInt(this.dinoId);
        buf.writeUtf(order);
        NetworkManager.sendToServer(DinoNetwork.ORDER, buf);
    }

    @Override
    public void tick() {
        // gone, dead or out of reach: the screen closes
        DinosaurEntity d = this.dino();
        if (d == null || this.minecraft.player == null
                || (!d.hasPassenger(this.minecraft.player) && d.distanceToSqr(this.minecraft.player) > DinoNetwork.RANGE * DinoNetwork.RANGE)) {
            this.onClose();
        }
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(g);
        TerrassicUi.slab(g, this.left, this.top, this.left + W, this.top + H);
        DinosaurEntity d = this.dino();
        CompoundTag t = this.info;

        // the animal, in a recessed frame
        int px = this.left + 10;
        int py = this.top + 12;
        TerrassicUi.well(g, px - 1, py - 1, px + PORTRAIT + 1, py + PORTRAIT + 1, false);
        if (d != null) {
            TerrassicHud.portrait(g, d, px, py, PORTRAIT);
        }

        // name and sex, species
        int x = px + PORTRAIT + 10;
        int y = this.top + 12;
        int right = this.left + W - 10;
        Component name = d != null ? d.getDisplayName() : Component.empty();
        Component sex = Component.literal(t.getBoolean("Female") ? " ♀" : " ♂")
                .withStyle(t.getBoolean("Female") ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.AQUA);
        g.drawString(this.font, TerrassicFonts.title(name.copy()).append(sex), x, y, TerrassicPalette.rgb(TerrassicPalette.BONE_100));
        y += 11;
        if (d != null && d.hasCustomName()) {
            g.drawString(this.font, TerrassicFonts.ui(d.getType().getDescription()), x, y, TerrassicPalette.rgb(TerrassicPalette.STONE_400));
            y += 10;
        }
        Component age = t.getBoolean("Baby")
                ? Component.translatable("gui.terrassic.lens.young", Math.round(t.getFloat("Growth") * 100))
                : Component.translatable("gui.terrassic.lens.adult", Math.round(t.getFloat("Size") * 100));
        g.drawString(this.font, TerrassicFonts.ui(age), x, y, TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        y += 13;
        TerrassicUi.divider(g, x, right, y);
        y += 6;

        // health and fullness
        this.bar(g, x, y, right, Component.translatable("gui.terrassic.lens.health"), t.getFloat("Health") / Math.max(1.0F, t.getFloat("MaxHealth")),
                TerrassicPalette.BLOOD_500, Mth.ceil(t.getFloat("Health")) + "/" + Mth.ceil(t.getFloat("MaxHealth")));
        y += 12;
        this.bar(g, x, y, right, Component.translatable("gui.terrassic.lens.hunger"), t.getInt("Hunger") / (float) DinosaurEntity.MAX_HUNGER,
                TerrassicPalette.AMBER_600, t.getInt("Hunger") + "%");
        y += 15;

        // what it is doing, saddle and cargo
        Component state = Component.translatable(t.getBoolean("Ridden") ? "gui.terrassic.dino.state_ridden"
                : t.getBoolean("Sitting") ? "gui.terrassic.dino.state_waiting" : "gui.terrassic.dino.state_following");
        g.drawString(this.font, TerrassicFonts.ui(state), x, y, TerrassicPalette.rgb(TerrassicPalette.FERN_400));
        y += 11;
        if (t.getBoolean("Rideable")) {
            g.drawString(this.font, TerrassicFonts.ui(t.getBoolean("Saddled") ? "gui.terrassic.dino.saddled" : "gui.terrassic.dino.no_saddle"),
                    x, y, TerrassicPalette.rgb(TerrassicPalette.STONE_300));
            y += 11;
        }
        if (t.contains("CargoSize")) {
            g.drawString(this.font, TerrassicFonts.ui("gui.terrassic.lens.cargo", t.getInt("CargoUsed"), t.getInt("CargoSize")), x, y,
                    TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        }

        // the orders, and at the foot the mounted controls
        TerrassicUi.divider(g, this.left + 10, this.left + W - 10, this.top + H - 36);
        super.render(g, mouseX, mouseY, partialTick);
        if (t.getBoolean("Ridden") && d != null) {
            Component hint = d instanceof FlyingDinosaur
                    ? Component.translatable("gui.terrassic.dino.hint_flyer", DinoControls.DESCEND.getTranslatedKeyMessage())
                    : Component.translatable(d instanceof com.terrassic.entity.ApexTheropod ? "gui.terrassic.dino.hint_apex"
                    : "gui.terrassic.dino.hint_ridden");
            g.drawCenteredString(this.font, TerrassicFonts.ui(hint), this.left + W / 2, this.top + H + 4,
                    TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        }
    }

    /** A label, then a bar with its value written at its right end (as on the Field Lens card). */
    private void bar(GuiGraphics g, int x, int y, int right, Component label, float fraction, int colour, String value) {
        g.drawString(this.font, TerrassicFonts.ui(label), x, y, TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        int bx = x + 54;
        int bw = right - bx;
        g.fill(bx, y, bx + bw, y + 9, TerrassicPalette.BASALT_950);
        int fill = Math.round((bw - 2) * Mth.clamp(fraction, 0.0F, 1.0F));
        g.fill(bx + 1, y + 1, bx + 1 + fill, y + 8, colour);
        g.fill(bx + 1, y + 1, bx + 1 + fill, y + 2, (colour & 0x00FFFFFF) | 0x50FFFFFF);
        g.drawString(this.font, value, bx + bw - this.font.width(value) - 2, y + 1, 0xFFFFFFFF, true);
    }

    @Override
    public boolean keyPressed(int key, int scan, int modifiers) {
        // the key that opened it closes it, like the vanilla inventory
        if (this.minecraft != null && (this.minecraft.options.keyInventory.matches(key, scan) || DinoControls.DINO_SCREEN.matches(key, scan))) {
            this.onClose();
            return true;
        }
        return super.keyPressed(key, scan, modifiers);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
