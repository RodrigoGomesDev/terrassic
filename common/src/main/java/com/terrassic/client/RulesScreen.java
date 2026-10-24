package com.terrassic.client;

import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
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

/**
 * "Terrassic Rules" (docs/REGRAS.md): the world rules in a screen modelled on ARK's server settings, one tab per
 * {@link Rule.Tab}, every rule a row with its name, a number box and a slider; hovering the name explains it.
 *
 * <p>Opened from the pause menu (or {@code /terrassic regras}) it edits the rules of the world being played: an
 * operator, or the owner of a single player world, saves them to the server; anyone else only reads them. Opened
 * with no world (the Forge mods list) it edits the defaults new worlds start from (config/terrassic-world.json).
 * Drawn with plain fills and text, no texture: a dark glass panel with cyan lines.
 */
public class RulesScreen extends Screen {
    private static final int GLASS = 0xE00B1620;
    private static final int GLASS_LIGHT = 0xC0132634;
    private static final int LINE = 0xFF3FB5CF;
    private static final int LINE_SOFT = 0x803FB5CF;
    private static final int TEXT = 0xFFD7F4FA;
    private static final int TEXT_SOFT = 0xFF7FA9B5;
    private static final int ACCENT = 0xFF8FE6F7;
    private static final int ROW_H = 34;

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
            this.addRenderableWidget(new GlassButton(this.left + 12 + i * tabW, this.top + 30, tabW - 4, 18,
                    Component.translatable("rules.terrassic.tab." + t.id()), b -> this.select(t), t == this.tab, true));
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
        GlassButton reset = new GlassButton(this.left + 12, by, bw, 18, Component.translatable("rules.terrassic.ui.reset"),
                b -> this.resetTab(), false, false);
        reset.active = this.editable;
        this.addRenderableWidget(reset);
        this.addRenderableWidget(new GlassButton(this.left + 16 + bw, by, bw, 18, Component.translatable("rules.terrassic.ui.cancel"),
                b -> this.onClose(), false, false));
        GlassButton save = new GlassButton(this.left + 20 + bw * 2, by, bw, 18, Component.translatable("rules.terrassic.ui.save"),
                b -> this.save(), false, false);
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
        g.fill(this.left, this.top, right, bottom, GLASS);
        // frame: full lines with a notch cut into the top left corner, like the ARK panels
        g.fill(this.left + 10, this.top, right, this.top + 1, LINE);
        g.fill(this.left, this.top + 10, this.left + 1, bottom, LINE);
        g.fill(right - 1, this.top, right, bottom, LINE);
        g.fill(this.left, bottom - 1, right, bottom, LINE);
        for (int i = 0; i < 10; i++) {
            g.fill(this.left + i, this.top + 10 - i, this.left + i + 1, this.top + 11 - i, LINE);
        }
        this.drawHexes(g, right, bottom);

        g.drawString(this.font, this.title.getString().toUpperCase(Locale.ROOT), this.left + 14, this.top + 8, ACCENT);
        Component sub = Component.translatable(this.world ? "rules.terrassic.ui.world" : "rules.terrassic.ui.defaults");
        g.drawString(this.font, sub, this.left + 14, this.top + 19, TEXT_SOFT, false);
        g.fill(this.left + 12, this.listTop - 6, right - 12, this.listTop - 5, LINE_SOFT);
        g.fill(this.left + 12, this.listBottom + 3, right - 12, this.listBottom + 4, LINE_SOFT);

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
            g.fill(right - 8, this.listTop, right - 6, this.listBottom, LINE_SOFT);
            g.fill(right - 9, barY, right - 5, barY + barH, LINE);
        }
        if (!this.editable) {
            g.drawCenteredString(this.font, Component.translatable("rules.terrassic.ui.read_only"), this.width / 2,
                    this.listBottom - 10, 0xFFF0B060);
        }
        super.render(g, mouseX, mouseY, partialTick);

        for (Row row : this.rows) {
            if (row.labelHovered(mouseX, mouseY)) {
                g.renderTooltip(this.font, this.font.split(Component.translatable(row.rule.tipKey()), 220), mouseX, mouseY);
            }
        }
    }

    /** A faint honeycomb in the panel's corner. */
    private void drawHexes(GuiGraphics g, int right, int bottom) {
        int color = 0x143FB5CF;
        for (int row = 0; row < 6; row++) {
            for (int col = 0; col < 5; col++) {
                int cx = right - 20 - col * 18 - (row % 2) * 9;
                int cy = bottom - 44 - row * 15;
                if (cx < this.left + 10 || cy < this.top + 10) {
                    continue;
                }
                g.fill(cx - 4, cy - 7, cx + 4, cy - 6, color);
                g.fill(cx - 4, cy + 6, cx + 4, cy + 7, color);
                g.fill(cx - 8, cy - 1, cx - 7, cy + 1, color);
                g.fill(cx + 7, cy - 1, cx + 8, cy + 1, color);
                g.fill(cx - 7, cy - 6, cx - 6, cy - 1, color);
                g.fill(cx + 6, cy - 6, cx + 7, cy - 1, color);
                g.fill(cx - 7, cy + 1, cx - 6, cy + 6, color);
                g.fill(cx + 6, cy + 1, cx + 7, cy + 6, color);
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
            this.box = new EditBox(RulesScreen.this.font, x, y + 12, 44, 14, Component.translatable(rule.langKey()));
            this.box.setMaxLength(8);
            this.box.setFilter(s -> s.matches("[0-9.,]*"));
            this.box.setValue(format(rule, RulesScreen.this.edited.get(rule)));
            this.box.setEditable(RulesScreen.this.editable);
            this.box.setTextColor(TEXT);
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
            this.box.setY(y + 12);
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
            String name = Component.translatable(this.rule.langKey()).getString().toUpperCase(Locale.ROOT) + ":";
            g.drawString(font, name, RulesScreen.this.left + 14, this.y + 1, TEXT, false);
            if (this.rule.defaultValue != RulesScreen.this.edited.get(this.rule)) {
                // changed from the default: a small mark after the name
                int w = font.width(name);
                g.fill(RulesScreen.this.left + 17 + w, this.y + 3, RulesScreen.this.left + 20 + w, this.y + 6, ACCENT);
            }
        }

        boolean labelHovered(int mx, int my) {
            int w = RulesScreen.this.font.width(Component.translatable(this.rule.langKey()).getString()) + 8;
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

    /** A slider drawn as a thin cyan rail with a hexagonal knob. */
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
            int x = this.getX();
            int y = this.getY();
            int mid = y + this.height / 2;
            int rail = this.active ? LINE : LINE_SOFT;
            g.fill(x + 4, mid - 1, x + this.width - 4, mid + 1, rail);
            // the default value: a tick under the rail
            Rule r = this.row.rule;
            int def = x + 4 + (int) Math.round((r.defaultValue - r.min) / (r.max - r.min) * (this.width - 8));
            g.fill(def, mid + 2, def + 1, mid + 5, LINE_SOFT);
            int kx = x + 4 + (int) Math.round(this.fraction() * (this.width - 8));
            int knob = this.isHoveredOrFocused() && this.active ? 0xFFFFFFFF : ACCENT;
            g.fill(kx - 2, mid - 5, kx + 3, mid + 6, knob);
            g.fill(kx - 4, mid - 3, kx + 5, mid + 4, knob);
            g.fill(kx - 1, mid - 2, kx + 2, mid + 3, GLASS);
        }

        @Override
        protected void updateWidgetNarration(NarrationElementOutput output) {
            output.add(NarratedElementType.TITLE, Component.translatable(this.row.rule.langKey()).append(": ")
                    .append(format(this.row.rule, RulesScreen.this.edited.get(this.row.rule))));
        }
    }

    /** A flat glass button with a cyan outline (tabs and the bottom row). */
    static final class GlassButton extends Button {
        private final boolean selected;
        private final boolean tab;

        GlassButton(int x, int y, int w, int h, Component message, OnPress onPress, boolean selected, boolean tab) {
            super(x, y, w, h, message, onPress, DEFAULT_NARRATION);
            this.selected = selected;
            this.tab = tab;
        }

        @Override
        public void onPress() {
            if (!this.selected) {
                super.onPress();
            }
        }

        @Override
        protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
            int x = this.getX();
            int y = this.getY();
            boolean hot = this.active && this.isHoveredOrFocused();
            if (this.tab) {
                int color = this.selected ? ACCENT : hot ? TEXT : TEXT_SOFT;
                Font font = net.minecraft.client.Minecraft.getInstance().font;
                g.drawCenteredString(font, this.getMessage().getString().toUpperCase(Locale.ROOT), x + this.width / 2,
                        y + (this.height - 8) / 2, color);
                if (this.selected) {
                    g.fill(x + 4, y + this.height - 2, x + this.width - 4, y + this.height, ACCENT);
                }
                return;
            }
            g.fill(x, y, x + this.width, y + this.height, hot ? GLASS_LIGHT : 0x900B1620);
            g.renderOutline(x, y, this.width, this.height, this.active ? (hot ? ACCENT : LINE) : LINE_SOFT);
            Font font = net.minecraft.client.Minecraft.getInstance().font;
            g.drawCenteredString(font, this.getMessage(), x + this.width / 2, y + (this.height - 8) / 2,
                    this.active ? (hot ? 0xFFFFFFFF : TEXT) : TEXT_SOFT);
        }
    }
}
