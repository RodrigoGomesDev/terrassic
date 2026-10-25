package com.terrassic.client;

import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import com.terrassic.client.ui.TerrassicFonts;
import com.terrassic.client.ui.TerrassicUi;
import com.terrassic.network.RulesNetwork;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.narration.NarratedElementType;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import static com.terrassic.client.ui.TerrassicPalette.*;

/**
 * "Terrassic Rules" (docs/REGRAS.md): the world rules, one tab per {@link Rule.Tab}, every rule a row with its name,
 * a number box and a slider; hovering the name explains it.
 *
 * <p>Opened from the pause menu (or {@code /terrassic regras}) it edits the rules of the world being played: an
 * operator, or the owner of a single player world, saves them to the server; anyone else only reads them. Opened
 * with no world (the Forge mods list) it edits the defaults new worlds start from (config/terrassic-world.json).
 * Drawn with the Terrassic look (client/ui/TerrassicUi, docs/IDENTIDADE.md): a basalt slab with an amber inlay,
 * carved stone buttons and amber sliders, no texture.
 */
public class RulesScreen extends Screen {
    private static final int ROW_H = 34;
    private static final int FIELD_W = 44;

    private static Rule.Tab lastTab = Rule.Tab.GENERAL;

    private final Screen parent;
    /** True: the rules of the world being played; false: the defaults for new worlds. */
    private final boolean world;
    private final boolean editable;
    private final Rules edited;
    private final List<Row> rows = new ArrayList<>();
    private Rule.Tab tab;
    private int left;
    private int top;
    private int panelW;
    private int panelH;
    private int listTop;
    private int listBottom;
    private int scroll;

    public RulesScreen(Screen parent, boolean world) {
        super(Component.translatable("rules.terrassic.ui.title"));
        this.parent = parent;
        this.world = world;
        this.editable = !world || ClientRules.canEdit();
        this.edited = world ? ClientRules.get().copy() : Rules.loadDefaults();
        this.tab = lastTab;
    }

    // ------------------------------------------------------------------ layout

    @Override
    protected void init() {
        this.panelW = Math.min(380, this.width - 24);
        this.panelH = this.height - 32;
        this.left = (this.width - this.panelW) / 2;
        this.top = 16;
        this.listTop = this.top + 58;
        this.listBottom = this.top + this.panelH - 34;
        this.rows.clear();

        // tabs (the active one is drawn highlighted and does nothing when clicked)
        Rule.Tab[] tabs = Rule.Tab.values();
        int tabW = (this.panelW - 24) / tabs.length;
        for (int i = 0; i < tabs.length; i++) {
            Rule.Tab t = tabs[i];
            this.addRenderableWidget(new StoneButton(this.left + 12 + i * tabW, this.top + 30, tabW - 4, 18,
                    Component.translatable("rules.terrassic.tab." + t.id()), b -> this.select(t), t == this.tab, true, false));
        }

        int y = this.listTop;
        for (Rule rule : Rule.values()) {
            if (rule.tab != this.tab) {
                continue;
            }
            Row row = new Row(rule, y);
            this.rows.add(row);
            y += ROW_H;
        }
        this.scroll = 0;
        this.layoutRows();

        int bw = (this.panelW - 32) / 3;
        int by = this.top + this.panelH - 26;
        StoneButton reset = new StoneButton(this.left + 12, by, bw, 18, Component.translatable("rules.terrassic.ui.reset"),
                b -> this.resetTab(), false, false, false);
        reset.active = this.editable;
        this.addRenderableWidget(reset);
        this.addRenderableWidget(new StoneButton(this.left + 16 + bw, by, bw, 18, Component.translatable("rules.terrassic.ui.cancel"),
                b -> this.onClose(), false, false, false));
        StoneButton save = new StoneButton(this.left + 20 + bw * 2, by, bw, 18, Component.translatable("rules.terrassic.ui.save"),
                b -> this.save(), false, false, true);
        save.active = this.editable;
        this.addRenderableWidget(save);
    }

    private void select(Rule.Tab t) {
        this.commitBoxes();
        this.tab = t;
        lastTab = t;
        this.rebuildWidgets();
    }

    private void layoutRows() {
        int contentH = this.rows.size() * ROW_H;
        int maxScroll = Math.max(0, contentH - (this.listBottom - this.listTop));
        this.scroll = Mth.clamp(this.scroll, 0, maxScroll);
        for (int i = 0; i < this.rows.size(); i++) {
            this.rows.get(i).place(this.listTop + i * ROW_H - this.scroll);
        }
    }

    private void resetTab() {
        for (Row row : this.rows) {
            this.edited.set(row.rule, row.rule.defaultValue);
            row.refresh();
        }
    }

    /** Takes whatever was typed into the boxes, even without pressing Enter. */
    private void commitBoxes() {
        for (Row row : this.rows) {
            row.commit();
        }
    }

    private void save() {
        this.commitBoxes();
        if (this.world) {
            FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
            buf.writeNbt(this.edited.save());
            NetworkManager.sendToServer(RulesNetwork.SET, buf);
        } else {
            Rules.saveDefaults(this.edited);
        }
        this.onClose();
    }

    @Override
    public void onClose() {
        if (this.minecraft != null) {
            this.minecraft.setScreen(this.parent);
        }
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        this.scroll -= (int) (delta * ROW_H / 2);
        this.layoutRows();
        return true;
    }

    // ------------------------------------------------------------------ drawing

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(g);
        int right = this.left + this.panelW;
        int bottom = this.top + this.panelH;
        TerrassicUi.slab(g, this.left, this.top, right, bottom);
        g.drawString(this.font, TerrassicFonts.title(this.title), this.left + 14, this.top + 8, rgb(AMBER_500));
        Component sub = TerrassicFonts.ui(this.world ? "rules.terrassic.ui.world" : "rules.terrassic.ui.defaults");
        g.drawString(this.font, sub, right - 14 - this.font.width(sub), this.top + 12, rgb(STONE_400), false);
        TerrassicUi.divider(g, this.left + 12, right - 12, this.listTop - 6);
        TerrassicUi.divider(g, this.left + 12, right - 12, this.listBottom + 3);

        g.enableScissor(this.left + 1, this.listTop - 4, right - 1, this.listBottom + 2);
        for (Row row : this.rows) {
            row.drawLabel(g);
        }
        g.disableScissor();
        // scroll bar
        int contentH = this.rows.size() * ROW_H;
        int viewH = this.listBottom - this.listTop;
        if (contentH > viewH) {
            int barH = Math.max(16, viewH * viewH / contentH);
            int barY = this.listTop + (viewH - barH) * this.scroll / (contentH - viewH);
            TerrassicUi.scrollbar(g, right - 9, this.listTop, this.listBottom, barY, barH);
        }
        if (!this.editable) {
            g.drawCenteredString(this.font, TerrassicFonts.ui("rules.terrassic.ui.read_only"), this.width / 2,
                    this.listBottom - 10, rgb(AMBER_300));
        }
        super.render(g, mouseX, mouseY, partialTick);

        for (Row row : this.rows) {
            if (row.labelHovered(mouseX, mouseY)) {
                g.renderTooltip(this.font, this.font.split(TerrassicFonts.ui(row.rule.tipKey()), 220), mouseX, mouseY);
            }
        }
    }

    @Override
    public boolean isPauseScreen() {
        return true;
    }

    // ------------------------------------------------------------------ one rule

    /** Name, number box and slider of one rule. */
    private final class Row {
        final Rule rule;
        final EditBox box;
        final Slider slider;
        int y;

        Row(Rule rule, int y) {
            this.rule = rule;
            this.y = y;
            int x = RulesScreen.this.left + 14;
            this.box = new EditBox(RulesScreen.this.font, x + 4, y + 15, FIELD_W - 7, 10, Component.translatable(rule.langKey()));
            this.box.setBordered(false);
            this.box.setMaxLength(8);
            this.box.setFilter(s -> s.matches("[0-9.,]*"));
            this.box.setValue(format(rule, RulesScreen.this.edited.get(rule)));
            this.box.setEditable(RulesScreen.this.editable);
            this.box.setTextColor(rgb(BONE_100));
            this.box.setTextColorUneditable(rgb(STONE_400));
            int sx = x + 56;
            this.slider = new Slider(this, sx, y + 12, RulesScreen.this.left + RulesScreen.this.panelW - 18 - sx, 14);
            this.slider.active = RulesScreen.this.editable;
            // The responder uses the slider, so it is set only after the slider exists.
            this.box.setResponder(s -> {
                Double v = parse(s);
                if (v != null && v >= rule.min && v <= rule.max) {
                    RulesScreen.this.edited.set(rule, v);
                    this.slider.sync();
                }
            });
            RulesScreen.this.addRenderableWidget(this.box);
            RulesScreen.this.addRenderableWidget(this.slider);
        }

        void place(int y) {
            this.y = y;
            this.box.setY(y + 15);
            this.slider.setY(y + 12);
            boolean shown = y >= RulesScreen.this.listTop - 2 && y + ROW_H <= RulesScreen.this.listBottom + 4;
            this.box.visible = shown;
            this.slider.visible = shown;
        }

        void refresh() {
            this.box.setValue(format(this.rule, RulesScreen.this.edited.get(this.rule)));
            this.slider.sync();
        }

        void commit() {
            Double v = parse(this.box.getValue());
            if (v != null) {
                RulesScreen.this.edited.set(this.rule, v);
            }
        }

        void drawLabel(GuiGraphics g) {
            Font font = RulesScreen.this.font;
            int x = RulesScreen.this.left + 14;
            if (!this.box.visible) {
                return;
            }
            Component name = TerrassicFonts.ui(this.rule.langKey());
            g.drawString(font, name, x, this.y + 1, rgb(STONE_200), false);
            if (this.rule.defaultValue != RulesScreen.this.edited.get(this.rule)) {
                // changed from the default: a small amber mark after the name
                TerrassicUi.mark(g, x + font.width(name) + 4, this.y + 3);
            }
            TerrassicUi.well(g, x, this.y + 12, x + FIELD_W, this.y + 26, this.box.isFocused());
        }

        boolean labelHovered(int mx, int my) {
            int w = RulesScreen.this.font.width(TerrassicFonts.ui(this.rule.langKey())) + 8;
            return this.box.visible && mx >= RulesScreen.this.left + 14 && mx <= RulesScreen.this.left + 14 + w
                    && my >= this.y && my <= this.y + 10;
        }
    }

    private static String format(Rule rule, double v) {
        if (rule.whole()) {
            return Integer.toString((int) Math.round(v));
        }
        String s = String.format(Locale.ROOT, "%.2f", v);
        // 1.00 -> 1.0, 0.50 -> 0.5, 0.05 stays
        return s.endsWith("0") ? s.substring(0, s.length() - 1) : s;
    }

    private static Double parse(String s) {
        try {
            return s.isEmpty() ? null : Double.parseDouble(s.replace(',', '.'));
        } catch (NumberFormatException e) {
            return null;
        }
    }

    // ------------------------------------------------------------------ widgets

    /** A slider: an amber-filled groove with an amber shard as the knob (TerrassicUi.slider). */
    private final class Slider extends AbstractWidget {
        private final Row row;

        Slider(Row row, int x, int y, int w, int h) {
            super(x, y, w, h, Component.translatable(row.rule.langKey()));
            this.row = row;
        }

        private double fraction() {
            Rule r = this.row.rule;
            return (RulesScreen.this.edited.get(r) - r.min) / (r.max - r.min);
        }

        void sync() {
            // nothing cached: the knob is drawn from the edited value
        }

        private void setFromMouse(double mouseX) {
            Rule r = this.row.rule;
            double f = Mth.clamp((mouseX - (this.getX() + 4)) / (double) (this.width - 8), 0.0D, 1.0D);
            RulesScreen.this.edited.set(r, r.min + f * (r.max - r.min));
            this.row.box.setValue(format(r, RulesScreen.this.edited.get(r)));
        }

        @Override
        public void onClick(double mouseX, double mouseY) {
            this.setFromMouse(mouseX);
        }

        @Override
        protected void onDrag(double mouseX, double mouseY, double dragX, double dragY) {
            this.setFromMouse(mouseX);
        }

        @Override
        protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
            Rule r = this.row.rule;
            TerrassicUi.slider(g, this.getX(), this.getY(), this.width, this.height, this.fraction(),
                    (r.defaultValue - r.min) / (r.max - r.min), this.active, this.isHoveredOrFocused());
        }

        @Override
        protected void updateWidgetNarration(NarrationElementOutput output) {
            output.add(NarratedElementType.TITLE, Component.translatable(this.row.rule.langKey()).append(": ")
                    .append(format(this.row.rule, RulesScreen.this.edited.get(this.row.rule))));
        }
    }

    /** A carved stone button (tabs and the bottom row); the primary one (save) has an amber face. */
    static final class StoneButton extends Button {
        private final boolean selected;
        private final boolean tab;
        private final boolean primary;

        StoneButton(int x, int y, int w, int h, Component message, OnPress onPress, boolean selected, boolean tab, boolean primary) {
            super(x, y, w, h, message, onPress, DEFAULT_NARRATION);
            this.selected = selected;
            this.tab = tab;
            this.primary = primary;
        }

        @Override
        public void onPress() {
            if (!this.selected) {
                super.onPress();
            }
        }

        @Override
        protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
            Font font = net.minecraft.client.Minecraft.getInstance().font;
            boolean hot = this.active && this.isHoveredOrFocused();
            if (this.tab) {
                TerrassicUi.tab(g, font, this.getX(), this.getY(), this.width, this.height, this.getMessage(), this.selected, hot);
            } else {
                TerrassicUi.button(g, font, this.getX(), this.getY(), this.width, this.height, this.getMessage(), this.active, hot, this.primary);
            }
        }
    }
}
