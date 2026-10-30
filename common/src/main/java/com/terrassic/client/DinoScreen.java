package com.terrassic.client;

import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicButton;
import com.terrassic.client.ui.TerrassicFonts;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.entity.DinoLevels;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.network.DinoNetwork;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Tooltip;
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
 * On the far right, the levels of v0.13 (entity/DinoLevels): the level, the experience to the next one, the points
 * to spend and each stat as a share of the species' usual value, with a "+" beside the ones that take a point.
 * <p>
 * Since v0.14.2 it has the HUD's Âmbar look (docs/HUD.md; study: dirF.py scene_tela_dino): a chipped slab, the animal
 * on a broken rock with an amber vein, the bars cut into the stone, the special's key socket while ridden.
 */
public class DinoScreen extends Screen {
    private static final int W = 372;
    /** Where the levels column starts (the info column ends 10 px before it). */
    private static final int STATS_X = 272;
    /** Where the info column starts. */
    private static final int INFO_X = 132;
    private static final int ROW = 15;
    private static final int H = 196;

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
        this.top = Math.max(2, (this.height - H) / 2 - 8);
        int bx = this.left + INFO_X;
        int by = this.top + H - 26;
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
        // a "+" beside every stat that takes a point, while there are points to spend
        if (this.info.getInt("Points") > 0) {
            int y = this.statsTop();
            for (DinoLevels.Stat stat : DinoLevels.Stat.values()) {
                if (stat.spendable()) {
                    TerrassicButton plus = new TerrassicButton(this.left + STATS_X + 86, y, 12, 12, Component.literal("+"),
                            b -> this.send("up:" + stat.key), TerrassicButton.Kind.PRIMARY, false);
                    plus.setTooltip(Tooltip.create(Component.translatable("gui.terrassic.dino.spend",
                            Component.translatable("gui.terrassic.stat." + stat.key))));
                    this.addRenderableWidget(plus);
                }
                y += ROW;
            }
        }
    }

    /** First stat row of the levels column. */
    private int statsTop() {
        return this.top + 58;
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
        int x0 = this.left;
        int y0 = this.top;
        AmberHud.slab(g, "dino_screen", x0, y0, 6, 0, W - 40, 0, W - 36, 3, W, 3, W, H - 5, W - 5, H, 120, H, 116, H - 2,
                0, H - 2, 0, 6);
        DinosaurEntity d = this.dino();
        CompoundTag t = this.info;

        // the animal on a broken rock with an amber vein, in a dark recess
        int bx = x0 + 10;
        int by = y0 + 12;
        g.fill(bx, by, bx + 112, by + 104, TerrassicPalette.BASALT_900);
        g.fill(bx, by, bx + 112, by + 1, TerrassicPalette.BASALT_950);
        g.fill(bx, by, bx + 1, by + 104, TerrassicPalette.BASALT_950);
        g.fill(bx, by + 103, bx + 112, by + 104, TerrassicPalette.BASALT_600);
        AmberHud.slab(g, "dino_screen_rock", bx, by, 14, 80, 28, 74, 86, 74, 100, 80, 94, 90, 20, 90);
        for (int i = 0; i < 30; i++) {
            g.fill(bx + 40 + i, by + 81 + i / 10, bx + 41 + i, by + 82 + i / 10, i % 5 != 0 ? TerrassicPalette.AMBER_600 : TerrassicPalette.AMBER_300);
        }
        if (d != null) {
            TerrassicHud.portrait(g, d, bx + 2, by + 6, 108, 82);
        }
        if (d != null && d.hasCustomName()) {
            AmberHud.text(g, this.font, d.getType().getDescription(), bx, by + 110, TerrassicPalette.STONE_300);
        }

        // name and sex; age and size; what it is doing; saddle and cargo
        int x = x0 + INFO_X;
        int right = x0 + STATS_X - 10;
        Component name = d == null ? Component.empty() : d.hasCustomName() ? d.getCustomName() : d.getType().getDescription();
        Component title = TerrassicFonts.title(name.copy());
        boolean female = t.getBoolean("Female");
        Component sex = Component.literal(female ? "♀" : "♂");
        // a long name shrinks to stay clear of the levels column
        int room = right - x - AmberHud.width(this.font, sex) - 4;
        float fit = Math.min(1.0F, room / (float) Math.max(1, this.font.width(title)));
        g.pose().pushPose();
        g.pose().translate(x, y0 + 10 + (1.0F - fit) * 4.0F, 0.0F);
        g.pose().scale(fit, fit, 1.0F);
        g.drawString(this.font, title, 0, 0, TerrassicPalette.rgb(TerrassicPalette.AMBER_500), false);
        g.pose().popPose();
        AmberHud.text(g, this.font, sex, x + Math.round(this.font.width(title) * fit) + 4, y0 + 12, female ? 0xFFE58AC0 : 0xFF7FB4E8);
        Component age = t.getBoolean("Baby")
                ? Component.translatable("gui.terrassic.lens.young", Math.round(t.getFloat("Growth") * 100))
                : Component.translatable("gui.terrassic.lens.adult", Math.round(t.getFloat("Size") * 100));
        AmberHud.text(g, this.font, age, x, y0 + 26, TerrassicPalette.STONE_300);
        Component state = Component.translatable(t.getBoolean("Ridden") ? "gui.terrassic.dino.state_ridden"
                : t.getBoolean("Sitting") ? "gui.terrassic.dino.state_waiting" : "gui.terrassic.dino.state_following");
        AmberHud.text(g, this.font, state, x, y0 + 38, TerrassicPalette.FERN_400);
        Component gear = null;
        if (t.getBoolean("Rideable")) {
            gear = Component.translatable(t.getBoolean("Saddled") ? "gui.terrassic.dino.saddled" : "gui.terrassic.dino.no_saddle");
        }
        if (t.contains("CargoSize")) {
            Component cargo = Component.translatable("gui.terrassic.lens.cargo", t.getInt("CargoUsed"), t.getInt("CargoSize"));
            gear = gear == null ? cargo : Component.empty().append(gear).append(" · ").append(cargo);
        }
        if (gear != null) {
            AmberHud.text(g, this.font, gear, x, y0 + 48, TerrassicPalette.STONE_200);
        }

        // health and fullness, cut into the stone
        this.bar(g, x, y0 + 62, Component.translatable("gui.terrassic.lens.health"), t.getFloat("Health") / Math.max(1.0F, t.getFloat("MaxHealth")),
                AmberHud.RED, Mth.ceil(t.getFloat("Health")) + "/" + Mth.ceil(t.getFloat("MaxHealth")));
        this.bar(g, x, y0 + 73, Component.translatable("gui.terrassic.lens.hunger"), t.getInt("Hunger") / (float) DinosaurEntity.MAX_HUNGER,
                AmberHud.AMBER, t.getInt("Hunger") + "%");

        // the special's key socket while you ride it
        if (t.getBoolean("Ridden") && d != null && d.specialName() != null && d.specialCharge() >= 0.0F) {
            AmberHud.text(g, this.font, Component.translatable("gui.terrassic.dino.mount_keys"), x, y0 + 96, TerrassicPalette.STONE_300);
            float charge = d.specialCharge();
            AmberHud.chip(g, this.font, x, y0 + 108, null, charge);
            Component special = Component.translatable("hud.terrassic.special." + d.specialName());
            Component line = charge >= 1.0F ? Component.translatable("hud.terrassic.special.ready", special)
                    : Component.translatable("hud.terrassic.special.wait", special, Mth.ceil(d.specialTicksLeft() / 20.0F));
            AmberHud.text(g, this.font, line, x + 16, y0 + 110, TerrassicPalette.STONE_200);
        }

        this.levels(g, t);
        super.render(g, mouseX, mouseY, partialTick);
        this.statTooltip(g, mouseX, mouseY);
        if (t.getBoolean("Ridden") && d != null) {
            Component hint = d instanceof FlyingDinosaur
                    ? Component.translatable("gui.terrassic.dino.hint_flyer", DinoControls.DESCEND.getTranslatedKeyMessage())
                    : Component.translatable(d instanceof com.terrassic.entity.ApexTheropod ? "gui.terrassic.dino.hint_apex"
                    : "gui.terrassic.dino.hint_ridden");
            g.drawCenteredString(this.font, TerrassicFonts.ui(hint), this.left + W / 2, this.top + H + 4,
                    TerrassicPalette.rgb(TerrassicPalette.STONE_300));
        }
    }

    /** The levels column: level, experience, points, then each stat as a share of the species' usual value. */
    private void levels(GuiGraphics g, CompoundTag t) {
        int x = this.left + STATS_X;
        for (int yy = this.top + 10; yy < this.top + 150; yy++) {
            g.fill(x - 7, yy, x - 6, yy + 1, TerrassicPalette.BASALT_950);
            g.fill(x - 6, yy, x - 5, yy + 1, TerrassicPalette.BASALT_600);
        }
        g.drawString(this.font, TerrassicFonts.title(Component.translatable("gui.terrassic.dino.level", t.getInt("Level"))),
                x, this.top + 8, TerrassicPalette.rgb(TerrassicPalette.AMBER_500), false);
        // experience to the next tame level (full at the top)
        boolean top = t.getInt("TamedLevels") >= DinoLevels.MAX_TAMED_LEVELS;
        float xp = top ? 1.0F : t.getFloat("Xp") / Math.max(1, t.getInt("XpNext"));
        AmberHud.groove(g, x, this.top + 24, 92, xp, AmberHud.AMBER);
        Component next = top ? Component.translatable("gui.terrassic.dino.max_level")
                : Component.translatable("gui.terrassic.dino.xp", Mth.floor(t.getFloat("Xp")), t.getInt("XpNext"));
        AmberHud.text(g, this.font, next, x, this.top + 31, TerrassicPalette.STONE_300);
        int points = t.getInt("Points");
        AmberHud.text(g, this.font, Component.translatable("gui.terrassic.dino.points", points), x, this.top + 43,
                points > 0 ? TerrassicPalette.AMBER_300 : TerrassicPalette.STONE_400);
        int y = this.statsTop();
        CompoundTag stats = t.getCompound("Stats");
        for (DinoLevels.Stat stat : DinoLevels.Stat.values()) {
            AmberHud.text(g, this.font, Component.translatable("gui.terrassic.stat." + stat.key), x, y + 2, TerrassicPalette.STONE_200);
            AmberHud.text(g, this.font, Component.literal(Math.round(stats.getFloat(stat.key) * 100.0F) + "%"), x + 64, y + 2,
                    TerrassicPalette.BONE_100);
            y += ROW;
        }
    }

    /** What a stat does, over its name. */
    private void statTooltip(GuiGraphics g, int mouseX, int mouseY) {
        int x = this.left + STATS_X;
        if (mouseX < x || mouseX >= x + 84) {
            return;
        }
        int y = this.statsTop();
        for (DinoLevels.Stat stat : DinoLevels.Stat.values()) {
            if (mouseY >= y && mouseY < y + 12) {
                g.renderTooltip(this.font, Component.translatable("gui.terrassic.stat." + stat.key + ".tip"), mouseX, mouseY);
                return;
            }
            y += ROW;
        }
    }

    /** A label, a bar cut into the stone and its value at the right (study: 52 px of groove). */
    private void bar(GuiGraphics g, int x, int y, Component label, float fraction, int[] tones, String value) {
        AmberHud.text(g, this.font, label, x, y, TerrassicPalette.STONE_200);
        AmberHud.groove(g, x + 44, y + 1, 52, fraction, tones);
        AmberHud.text(g, this.font, Component.literal(value), x + 100, y, TerrassicPalette.BONE_100);
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
