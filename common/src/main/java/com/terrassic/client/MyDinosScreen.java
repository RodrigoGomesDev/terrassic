package com.terrassic.client;

import com.terrassic.client.ui.AmberHud;
import com.terrassic.client.ui.TerrassicButton;
import com.terrassic.client.ui.TerrassicPalette;
import com.terrassic.client.ui.TerrassicUi;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;

/**
 * 1.7 (player feedback: "you can't see where your dinos are and the whistle only works for about 50 blocks"): "My
 * dinos", every tamed animal of the player wherever it is (entity/TamedRegistry), nearest first: its egg, name, how far
 * and which way, its coordinates, whether it waits there and when it was last seen. "Track" puts the arrow of
 * {@link DinoTracker} at the top of the screen. Opened by sneaking while pressing the whistle key, by its own key
 * (unbound by default) or from the whistle wheel's hint; {@code /terrassic dinos} prints the same in the chat.
 */
public class MyDinosScreen extends Screen {
    private static final int W = 300;
    private static final int ROW = 34;
    private static final int HEADER = 30;
    private static final int FOOTER = 44;

    private final List<CompoundTag> rows = new ArrayList<>();
    private int left;
    private int top;
    private int panelH;
    private int scroll;
    private int visible;

    public MyDinosScreen() {
        super(Component.translatable("gui.terrassic.dinos.title"));
    }

    public static void open() {
        Minecraft.getInstance().setScreen(new MyDinosScreen());
        DinoTracker.ask();
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    protected void init() {
        this.sortRows();
        this.panelH = Math.min(this.height - 8, HEADER + FOOTER + ROW * Math.max(3, Math.min(6, this.rows.size())));
        this.left = (this.width - W) / 2;
        this.top = Math.max(4, (this.height - this.panelH) / 2);
        this.visible = Math.max(1, (this.panelH - HEADER - FOOTER) / ROW);
        this.scroll = Math.max(0, Math.min(this.scroll, this.rows.size() - this.visible));
        for (int i = 0; i < this.visible && this.scroll + i < this.rows.size(); i++) {
            CompoundTag t = this.rows.get(this.scroll + i);
            if (!t.hasUUID("Dino")) {
                continue;
            }
            UUID id = t.getUUID("Dino");
            boolean on = id.equals(DinoTracker.tracked());
            int y = this.top + HEADER + i * ROW + (ROW - 18) / 2;
            this.addRenderableWidget(new TerrassicButton(this.left + W - 72, y, 62, 18,
                    Component.translatable(on ? "gui.terrassic.dinos.untrack" : "gui.terrassic.dinos.track"),
                    b -> {
                        DinoTracker.toggle(id);
                        this.rebuildWidgets();
                    }, on ? TerrassicButton.Kind.PRIMARY : TerrassicButton.Kind.STONE, on));
        }
        this.addRenderableWidget(TerrassicButton.stone(this.left + W - 92, this.top + this.panelH - 24, 80, 18,
                Component.translatable("gui.terrassic.dinos.close"), b -> this.onClose()));
    }

    /** A new list arrived (DinoTracker). */
    void refresh() {
        this.rebuildWidgets();
    }

    private void sortRows() {
        this.rows.clear();
        this.rows.addAll(DinoTracker.dinos());
        LocalPlayer player = Minecraft.getInstance().player;
        if (player != null) {
            this.rows.sort(Comparator.comparingDouble(t -> DinoTracker.sameDimension(t)
                    ? DinoTracker.position(t).distanceToSqr(player.position()) : Double.MAX_VALUE));
        }
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double scrollX, double delta) {
        int max = Math.max(0, this.rows.size() - this.visible);
        int next = Math.max(0, Math.min(max, this.scroll + (delta < 0 ? 1 : -1)));
        if (next != this.scroll) {
            this.scroll = next;
            this.rebuildWidgets();
        }
        return true;
    }

    /** 1.21: Screen#render would draw the background over the panel; it is drawn first, here. */
    @Override
    public void renderBackground(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        if (this.minecraft != null && this.minecraft.level != null) {
            this.renderTransparentBackground(g);
        } else {
            super.renderBackground(g, mouseX, mouseY, partialTick);
        }
        int x0 = this.left;
        int y0 = this.top;
        TerrassicUi.slab(g, x0, y0, x0 + W, y0 + this.panelH);
        Component title = Component.translatable("gui.terrassic.dinos.title");
        AmberHud.text(g, this.font, title, x0 + 12, y0 + 12, TerrassicPalette.AMBER_300);
        if (!this.rows.isEmpty()) {
            Component count = Component.translatable("gui.terrassic.dinos.count", this.rows.size());
            AmberHud.text(g, this.font, count, x0 + W - 12 - AmberHud.width(this.font, count), y0 + 12, TerrassicPalette.STONE_300);
        }
        TerrassicUi.well(g, x0 + 8, y0 + HEADER - 4, x0 + W - 8, y0 + this.panelH - FOOTER + 2, false);
        LocalPlayer player = Minecraft.getInstance().player;
        if (this.rows.isEmpty()) {
            Component empty = Component.translatable(DinoTracker.received() ? "gui.terrassic.dinos.none" : "gui.terrassic.dinos.loading");
            AmberHud.text(g, this.font, empty, x0 + W / 2 - AmberHud.width(this.font, empty) / 2, y0 + HEADER + 12,
                    TerrassicPalette.STONE_300);
        }
        for (int i = 0; i < this.visible && this.scroll + i < this.rows.size() && player != null; i++) {
            this.row(g, player, this.rows.get(this.scroll + i), x0 + 12, y0 + HEADER + i * ROW);
        }
        if (this.rows.size() > this.visible) {
            String more = (this.scroll + 1) + "-" + Math.min(this.rows.size(), this.scroll + this.visible) + " / " + this.rows.size();
            g.drawString(this.font, more, x0 + W - 12 - this.font.width(more), y0 + this.panelH - FOOTER + 6, TerrassicPalette.STONE_400, false);
        }
        Component hint = Component.translatable("gui.terrassic.dinos.hint");
        int hy = y0 + this.panelH - FOOTER + 6;
        for (var line : this.font.split(hint, W - 112)) {
            g.drawString(this.font, line, x0 + 12, hy, TerrassicPalette.STONE_300, false);
            hy += 9;
        }
        super.render(g, mouseX, mouseY, partialTick);
    }

    /** One animal: egg, name, where it is and how it is. */
    private void row(GuiGraphics g, LocalPlayer player, CompoundTag t, int x, int y) {
        g.renderItem(egg(t.getString("Species")), x, y + 8);
        int tx = x + 22;
        Component name = DinoTracker.name(t);
        AmberHud.text(g, this.font, name, tx, y + 3, TerrassicPalette.BONE_100);
        if (!t.getString("Name").isEmpty()) {
            Component species = Component.translatable("entity.terrassic." + t.getString("Species"));
            g.drawString(this.font, species, tx + AmberHud.width(this.font, name) + 6, y + 3, TerrassicPalette.STONE_400, false);
        }
        Component where;
        if (!DinoTracker.sameDimension(t)) {
            where = Component.translatable("gui.terrassic.dinos.dimension", dimensionName(t.getString("Dim")));
        } else {
            Vec3 pos = DinoTracker.position(t);
            double dist = Math.sqrt(player.distanceToSqr(pos.x, player.getY(), pos.z));
            where = dist < 6.0D ? Component.translatable("gui.terrassic.dinos.here")
                    : Component.translatable("gui.terrassic.dinos.distance", (int) Math.round(dist), DinoTracker.arrow(player, pos));
        }
        g.drawString(this.font, where, tx, y + 13, TerrassicPalette.AMBER_500, false);
        net.minecraft.core.BlockPos p = net.minecraft.core.BlockPos.of(t.getLong("Pos"));
        Component coords = Component.translatable("gui.terrassic.dinos.coords", p.getX(), p.getY(), p.getZ());
        g.drawString(this.font, coords, tx + 110, y + 13, TerrassicPalette.STONE_300, false);
        Component state = Component.translatable(t.getBoolean("Sitting") ? "gui.terrassic.dinos.waiting" : "gui.terrassic.dinos.free")
                .append(" · ").append(seen(t));
        g.drawString(this.font, state, tx, y + 23, TerrassicPalette.STONE_400, false);
    }

    private static Component seen(CompoundTag t) {
        if (t.getBoolean("Loaded")) {
            return Component.translatable("gui.terrassic.dinos.live");
        }
        long s = t.getLong("Ago");
        if (s < 60) {
            return Component.translatable("gui.terrassic.dinos.ago_s", s);
        }
        if (s < 3600) {
            return Component.translatable("gui.terrassic.dinos.ago_m", s / 60);
        }
        return Component.translatable("gui.terrassic.dinos.ago_h", s / 3600);
    }

    private static String dimensionName(String id) {
        ResourceLocation rl = ResourceLocation.tryParse(id);
        return rl == null ? id : rl.getPath().replace('_', ' ');
    }

    /** The species' spawn egg, for its picture in the row (a bone when it has none). */
    static ItemStack egg(String species) {
        Item item = BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath("terrassic", species + "_spawn_egg"));
        return new ItemStack(item == Items.AIR ? Items.BONE : item);
    }
}
