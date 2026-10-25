package com.terrassic.client;

import com.terrassic.client.ui.TerrassicButton;
import com.terrassic.client.ui.TerrassicFonts;

import com.terrassic.Terrassic;
import com.terrassic.research.GuideSpecies;
import com.terrassic.research.Knowledge;
import com.terrassic.research.Lore;
import com.terrassic.research.Objective;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * The Field Notebook (docs/HISTORIA.md, section 9): one screen with five tabs.
 * <ul>
 *   <li><b>Journal</b>: the 12 objectives of the chapter in 4 themes, with a hint on hover, and the amber fragments.</li>
 *   <li><b>Guide</b>: every species, revealed level by level (Knowledge.SILHOUETTE .. TAMED).</li>
 *   <li><b>Map</b>: the map of the island, with its legend and where the player is ({@link ClientIslandMap},
 *       docs/MUNDO.md, section 11).</li>
 *   <li><b>Katarina</b>: the pages of her notebook found so far, in day order.</li>
 *   <li><b>Report</b>: the "Incident Report" the player starts with.</li>
 * </ul>
 * Everything is drawn with plain fills and text on a parchment-coloured page; only the Guide's habitat dioramas and
 * the map are textures. The content comes from
 * {@link ClientResearch}.
 */
public class NotebookScreen extends Screen {
    private static final int W = 320;
    private static final int H = 210;
    // Katarina's notebook colours of the Terrassic palette (client/ui/TerrassicPalette, docs/IDENTIDADE.md)
    private static final int PAPER = com.terrassic.client.ui.TerrassicPalette.PAPER;
    private static final int PAPER_DARK = com.terrassic.client.ui.TerrassicPalette.PAPER_DARK;
    private static final int LEATHER = com.terrassic.client.ui.TerrassicPalette.LEATHER;
    private static final int INK = com.terrassic.client.ui.TerrassicPalette.INK;
    private static final int INK_SOFT = com.terrassic.client.ui.TerrassicPalette.INK_SOFT;
    private static final int DONE = 0xFF3C7A2E;
    private static final int AMBER = 0xFFB86E10;
    private static final int BLOOD = com.terrassic.client.ui.TerrassicPalette.BLOOD_500;
    private static final String[] TABS = {"journal", "guide", "map", "katarina", "report"};
    /** Legend of the map, in the order of IslandMap's biome categories (DEEP_SEA .. DRY). */
    private static final String[] MAP_KINDS = {"deep_sea", "sea", "beach", "river", "swamp", "plains", "forest", "highlands", "dry"};

    /** Remembered between openings. */
    private static String lastTab = "journal";
    private static String lastSpecies = null;
    private static int lastKatarinaPage = 0;
    private static int lastReportPage = 0;
    private static String lastEra = null;
    private static String lastDiet = null;
    private static int lastListPage = 0;
    /** Species buttons per page of the Guide list. */
    private static final int LIST_ROWS = 10;
    /** Width of the Guide's list column on the left page (it ends before the spine at W / 2). */
    private static final int LIST_W = W / 2 - 18;

    private final Map<String, LivingEntity> models = new HashMap<>();
    private String tab;
    private int left;
    private int top;
    private int scroll;
    private int contentHeight;

    public NotebookScreen(String tab) {
        super(Component.translatable("notebook.terrassic.title"));
        this.tab = tab != null ? tab : lastTab;
    }

    // ------------------------------------------------------------------ layout

    @Override
    protected void init() {
        this.left = (this.width - W) / 2;
        this.top = (this.height - H) / 2;
        int tabW = 58; // five tabs: 5 x 58 + 4 x 4 = 306 of the 320 of the book
        for (int i = 0; i < TABS.length; i++) {
            String id = TABS[i];
            // leather tabs; the open one shows the page colour (TerrassicButton, docs/IDENTIDADE.md)
            this.addRenderableWidget(TerrassicButton.notebook(this.left + 8 + i * (tabW + 4), this.top - 20, tabW, 18,
                    Component.translatable("notebook.terrassic.tab." + id), button -> this.select(id), id.equals(this.tab)));
        }
        if (this.tab.equals("katarina") || this.tab.equals("report")) {
            this.addRenderableWidget(TerrassicButton.notebook(this.left + 10, this.top + H - 24, 70, 16,
                    Component.translatable("notebook.terrassic.prev"), b -> this.turn(-1), false));
            this.addRenderableWidget(TerrassicButton.notebook(this.left + W - 80, this.top + H - 24, 70, 16,
                    Component.translatable("notebook.terrassic.next"), b -> this.turn(1), false));
        }
        if (this.tab.equals("guide")) {
            this.guideList();
        }
    }

    /**
     * Guide tab, left column: era and diet filters (each button cycles through the values present in the Guide,
     * starting with "all"), one page of species buttons and the page turner. Built for hundreds of species.
     */
    private void guideList() {
        int x = this.left + 8;
        List<String> eras = values(true);
        List<String> diets = values(false);
        Component era = lastEra == null ? Component.translatable("notebook.terrassic.guide.all_eras")
                : Component.translatable("era.terrassic." + lastEra);
        Component diet = lastDiet == null ? Component.translatable("notebook.terrassic.guide.all_diets")
                : Component.translatable("diet.terrassic." + lastDiet);
        this.addRenderableWidget(TerrassicButton.notebook(x, this.top + 18, LIST_W, 12, era, b -> {
            lastEra = next(eras, lastEra);
            lastListPage = 0;
            this.rebuildWidgets();
        }, false));
        this.addRenderableWidget(TerrassicButton.notebook(x, this.top + 31, LIST_W, 12, diet, b -> {
            lastDiet = next(diets, lastDiet);
            lastListPage = 0;
            this.rebuildWidgets();
        }, false));

        List<GuideSpecies> shown = filtered();
        int pages = Math.max(1, (shown.size() + LIST_ROWS - 1) / LIST_ROWS);
        lastListPage = Mth.clamp(lastListPage, 0, pages - 1);
        int y = this.top + 47;
        for (GuideSpecies s : shown.subList(lastListPage * LIST_ROWS, Math.min(shown.size(), (lastListPage + 1) * LIST_ROWS))) {
            int level = ClientResearch.get().level(s.id());
            Component name = level >= Knowledge.SIGHTED ? Component.translatable("entity.terrassic." + s.id())
                    : Component.translatable("notebook.terrassic.guide.unknown");
            this.addRenderableWidget(TerrassicButton.notebook(x, y, LIST_W, 12, name, button -> {
                lastSpecies = s.id();
                this.scroll = 0;
                this.rebuildWidgets();
            }, s.id().equals(this.selectedSpecies())));
            y += 13;
        }
        if (pages > 1) {
            Button prev = TerrassicButton.notebook(x, this.top + H - 20, 18, 12, Component.literal("<"), b -> {
                lastListPage--;
                this.rebuildWidgets();
            }, false);
            Button next = TerrassicButton.notebook(x + LIST_W - 18, this.top + H - 20, 18, 12, Component.literal(">"), b -> {
                lastListPage++;
                this.rebuildWidgets();
            }, false);
            prev.active = lastListPage > 0;
            next.active = lastListPage < pages - 1;
            this.addRenderableWidget(prev);
            this.addRenderableWidget(next);
        }
    }

    /** The eras (or diets) used by the Guide, in Guide order. */
    private static List<String> values(boolean era) {
        List<String> out = new ArrayList<>();
        for (GuideSpecies s : GuideSpecies.ALL) {
            String v = era ? s.era() : s.diet();
            if (!out.contains(v)) {
                out.add(v);
            }
        }
        return out;
    }

    /** Cycles null ("all") -> first value -> ... -> last value -> null. */
    private static String next(List<String> values, String current) {
        int i = current == null ? -1 : values.indexOf(current);
        return i + 1 < values.size() ? values.get(i + 1) : null;
    }

    private static List<GuideSpecies> filtered() {
        List<GuideSpecies> out = new ArrayList<>();
        for (GuideSpecies s : GuideSpecies.ALL) {
            if ((lastEra == null || lastEra.equals(s.era())) && (lastDiet == null || lastDiet.equals(s.diet()))) {
                out.add(s);
            }
        }
        return out;
    }

    private void select(String id) {
        this.tab = id;
        lastTab = id;
        this.scroll = 0;
        this.rebuildWidgets();
    }

    private void turn(int delta) {
        if (this.tab.equals("katarina")) {
            int pages = this.foundPages().size();
            lastKatarinaPage = pages == 0 ? 0 : Mth.clamp(lastKatarinaPage + delta, 0, pages - 1);
        } else {
            lastReportPage = Mth.clamp(lastReportPage + delta, 0, Lore.REPORT_PAGES - 1);
        }
        this.scroll = 0;
    }

    private String selectedSpecies() {
        if (lastSpecies == null || GuideSpecies.byId(lastSpecies) == null) {
            lastSpecies = GuideSpecies.ALL.get(0).id();
        }
        return lastSpecies;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        this.scroll = Mth.clamp(this.scroll - (int) (delta * 12), 0, Math.max(0, this.contentHeight));
        return true;
    }

    // ------------------------------------------------------------------ drawing

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(g);
        g.fill(this.left - 4, this.top - 4, this.left + W + 4, this.top + H + 4, LEATHER);
        g.fill(this.left, this.top, this.left + W, this.top + H, PAPER);
        g.fill(this.left + W / 2 - 1, this.top + 4, this.left + W / 2 + 1, this.top + H - 4, PAPER_DARK);
        switch (this.tab) {
            case "guide" -> this.renderGuide(g, mouseX, mouseY);
            case "map" -> this.renderMap(g, mouseX, mouseY);
            case "katarina" -> this.renderKatarina(g);
            case "report" -> this.renderReport(g);
            default -> this.renderJournal(g, mouseX, mouseY);
        }
        super.render(g, mouseX, mouseY, partialTick);
    }

    private void heading(GuiGraphics g, Component text, int x, int y) {
        // titles in "Entalhe"; a title too long for the half page falls back to bold "Sedimento"
        Component t = TerrassicFonts.title(text);
        if (this.font.width(t) > W / 2 - 24) {
            t = TerrassicFonts.ui(text.copy().withStyle(ChatFormatting.BOLD));
            g.drawString(this.font, t, x, y, INK, false);
            return;
        }
        g.drawString(this.font, t, x, y - 2, INK, false);
    }

    /** Draws wrapped text and returns the y below it. */
    private int text(GuiGraphics g, Component text, int x, int y, int width, int color) {
        for (FormattedCharSequence line : this.font.split(TerrassicFonts.ui(text), width)) {
            g.drawString(this.font, line, x, y, color, false);
            y += 10;
        }
        return y;
    }

    // ---- Journal

    private void renderJournal(GuiGraphics g, int mouseX, int mouseY) {
        Knowledge k = ClientResearch.get();
        int x = this.left + 10;
        int y = this.top + 8;
        this.heading(g, Component.translatable("notebook.terrassic.journal.header"), x, y);
        this.text(g, Component.translatable("notebook.terrassic.journal.intro", Objective.fragments(k)), x, y + 12, W - 20, INK_SOFT);
        List<FormattedCharSequence> tooltip = null;
        Objective.Theme[] themes = Objective.Theme.values();
        for (int t = 0; t < themes.length; t++) {
            int bx = this.left + 10 + (t % 2) * (W / 2);
            int by = this.top + 46 + (t / 2) * 78;
            int done = 0;
            for (Objective o : Objective.values()) {
                if (o.theme() == themes[t] && k.hasObjective(o)) {
                    done++;
                }
            }
            boolean complete = done >= Objective.PER_THEME;
            g.drawString(this.font, TerrassicFonts.ui(Component.translatable("notebook.terrassic.journal.theme",
                    Component.translatable("theme.terrassic." + themes[t].id()), Math.min(done, Objective.PER_THEME))
                    .withStyle(ChatFormatting.BOLD)), bx, by, complete ? DONE : INK, false);
            int oy = by + 14;
            for (Objective o : Objective.values()) {
                if (o.theme() != themes[t]) {
                    continue;
                }
                boolean has = k.hasObjective(o);
                int color = has ? DONE : o.available() ? INK : INK_SOFT;
                MutableComponent line = Component.literal(has ? "✔ " : "○ ")
                        .append(Component.translatable("objective.terrassic." + o.id()));
                g.drawString(this.font, TerrassicFonts.ui(line), bx + 4, oy, color, false);
                if (mouseX >= bx && mouseX < bx + W / 2 - 16 && mouseY >= oy - 1 && mouseY < oy + 10) {
                    tooltip = this.font.split(TerrassicFonts.ui("objective.terrassic." + o.id() + ".hint"), 180);
                }
                oy += 16;
            }
        }
        if (tooltip != null) {
            g.renderTooltip(this.font, tooltip, mouseX, mouseY);
        }
    }

    // ---- Guide

    private void renderGuide(GuiGraphics g, int mouseX, int mouseY) {
        Knowledge k = ClientResearch.get();
        int recorded = 0;
        for (GuideSpecies s : GuideSpecies.ALL) {
            if (k.level(s.id()) > Knowledge.UNKNOWN) {
                recorded++;
            }
        }
        g.drawString(this.font, TerrassicFonts.ui("notebook.terrassic.guide.count", recorded, GuideSpecies.ALL.size()),
                this.left + 10, this.top + 8, INK_SOFT, false);
        int shown = filtered().size();
        int pages = Math.max(1, (shown + LIST_ROWS - 1) / LIST_ROWS);
        if (shown == 0) {
            this.text(g, Component.translatable("notebook.terrassic.guide.empty"), this.left + 10, this.top + 49, 100, INK_SOFT);
        } else if (pages > 1) {
            Component label = TerrassicFonts.ui("notebook.terrassic.guide.page", lastListPage + 1, pages);
            g.drawString(this.font, label, this.left + 8 + LIST_W / 2 - this.font.width(label) / 2, this.top + H - 18, INK_SOFT, false);
        }

        GuideSpecies s = GuideSpecies.byId(this.selectedSpecies());
        int level = k.level(s.id());
        // the species page is the right page: from past the spine to the right margin
        int x = this.left + W / 2 + 8;
        int width = W / 2 - 18;
        int y0 = this.top + 8;
        if (level == Knowledge.UNKNOWN) {
            this.heading(g, Component.translatable("notebook.terrassic.guide.unknown"), x, y0);
            this.text(g, Component.translatable("notebook.terrassic.guide.unknown_hint"), x, y0 + 14, width, INK_SOFT);
            return;
        }

        // picture (sighted and up) or a question mark over the silhouette level
        int picBottom = y0 + 70;
        if (level >= Knowledge.SIGHTED) {
            GuideHabitats.render(g, s.id(), x, y0, width, picBottom + 2 - y0); // habitat diorama behind the model
            LivingEntity model = this.model(s.id());
            if (model != null) {
                int scale = Math.max(4, Math.round(s.guiScale() * 0.6F));
                g.enableScissor(x, y0, x + width, picBottom + 2);
                InventoryScreen.renderEntityInInventoryFollowsMouse(g, x + width / 2, picBottom - 4, scale,
                        x + width / 2 - mouseX, picBottom - 30 - mouseY, model);
                g.disableScissor();
            }
        } else {
            g.pose().pushPose();
            g.pose().translate(x + width / 2.0F, y0 + 20, 0);
            g.pose().scale(4.0F, 4.0F, 1.0F);
            g.drawCenteredString(this.font, "?", 0, 0, 0xFF8A7A60);
            g.pose().popPose();
        }

        // scrollable text below the picture
        List<Line> lines = new ArrayList<>();
        Component name = level >= Knowledge.SIGHTED ? Component.translatable("entity.terrassic." + s.id())
                : Component.translatable("notebook.terrassic.guide.unknown");
        this.add(lines, name.copy().withStyle(ChatFormatting.BOLD), INK, width);
        this.add(lines, Component.translatable("notebook.terrassic.guide.level." + level), AMBER, width);
        this.add(lines, Component.translatable("notebook.terrassic.guide.era", Component.translatable("era.terrassic." + s.era())), INK, width);
        if (level == Knowledge.SILHOUETTE) {
            this.add(lines, Component.translatable("notebook.terrassic.guide.silhouette_hint"), INK_SOFT, width);
        }
        if (level >= Knowledge.SIGHTED) {
            this.add(lines, Component.translatable("notebook.terrassic.guide.diet", Component.translatable("diet.terrassic." + s.diet())), INK, width);
            this.add(lines, Component.translatable("notebook.terrassic.guide.length", String.valueOf(s.length())), INK, width);
            lines.add(Line.GAP);
            this.add(lines, Component.translatable("guide.terrassic." + s.id() + ".sci"), INK, width);
            lines.add(Line.GAP);
        }
        if (level == Knowledge.SIGHTED) {
            this.add(lines, Component.translatable("notebook.terrassic.guide.points", k.points(s.id()), Knowledge.POINTS_TO_STUDY), INK_SOFT, width);
            this.add(lines, Component.translatable("notebook.terrassic.guide.study_hint"), INK_SOFT, width);
        }
        if (level >= Knowledge.STUDIED) {
            this.section(lines, "behavior", s.id(), width);
            this.section(lines, "taming", s.id(), width);
            if (s.rideable()) {
                this.add(lines, Component.translatable("notebook.terrassic.guide.rideable"), INK_SOFT, width);
            }
            if (s.eggOnly()) {
                this.add(lines, Component.translatable("notebook.terrassic.guide.egg_only"), INK_SOFT, width);
            }
            this.add(lines, Component.translatable("notebook.terrassic.guide.bonus"), DONE, width);
            lines.add(Line.GAP);
        }
        if (level == Knowledge.STUDIED) {
            this.add(lines, Component.translatable("notebook.terrassic.guide.tame_hint"), INK_SOFT, width);
        }
        if (level >= Knowledge.TAMED) {
            this.section(lines, "utility", s.id(), width);
            this.add(lines, Component.translatable("notebook.terrassic.guide.note").withStyle(ChatFormatting.BOLD), INK, width);
            // Katarina's own note, in her handwriting
            for (FormattedCharSequence seq : this.font.split(TerrassicFonts.hand(Component.translatable("guide.terrassic." + s.id() + ".note")), width)) {
                lines.add(new Line(seq, AMBER));
            }
        }

        int textTop = picBottom + 6;
        int textBottom = this.top + H - 8;
        this.contentHeight = Math.max(0, lines.size() * 10 - (textBottom - textTop));
        this.scroll = Math.min(this.scroll, this.contentHeight);
        g.enableScissor(x, textTop, x + width, textBottom);
        int y = textTop - this.scroll;
        for (Line line : lines) {
            if (line.text != null) {
                g.drawString(this.font, line.text, x, y, line.color, false);
            }
            y += 10;
        }
        g.disableScissor();
    }

    private record Line(FormattedCharSequence text, int color) {
        static final Line GAP = new Line(null, 0);
    }

    private void add(List<Line> lines, Component text, int color, int width) {
        for (FormattedCharSequence seq : this.font.split(TerrassicFonts.ui(text), width)) {
            lines.add(new Line(seq, color));
        }
    }

    private void section(List<Line> lines, String field, String species, int width) {
        this.add(lines, Component.translatable("notebook.terrassic.guide." + field).withStyle(ChatFormatting.BOLD), INK, width);
        this.add(lines, Component.translatable("guide.terrassic." + species + "." + field), INK, width);
        lines.add(Line.GAP);
    }

    /** A client-side copy of the species, used only to draw it in the Guide. */
    private LivingEntity model(String species) {
        return this.models.computeIfAbsent(species, id -> {
            if (this.minecraft == null || this.minecraft.level == null) {
                return null;
            }
            EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(Terrassic.id(id));
            Entity e = type.create(this.minecraft.level);
            return e instanceof LivingEntity living ? living : null;
        });
    }

    // ---- Map

    /** The map on the left page; its legend, the player's position and the point under the mouse on the right one. */
    private void renderMap(GuiGraphics g, int mouseX, int mouseY) {
        int side = W / 2 - 20;
        int mx = this.left + 10;
        int my = this.top + 22;
        this.heading(g, Component.translatable("map.terrassic.title"), mx, this.top + 8);
        ClientIslandMap.render(g, this.font, mx, my, side);
        if (!ClientIslandMap.available()) {
            return;
        }
        this.text(g, Component.translatable("map.terrassic.note"), mx, my + side + 6, side, INK_SOFT);

        int x = this.left + W / 2 + 10;
        int width = W / 2 - 20;
        int y = this.top + 8;
        this.heading(g, Component.translatable("map.terrassic.legend"), x, y);
        y += 14;
        for (int k = 0; k < MAP_KINDS.length; k++) {
            ClientIslandMap.swatch(g, k, x, y, 12, 8);
            g.drawString(this.font, Component.translatable("map.terrassic.kind." + MAP_KINDS[k]), x + 16, y, INK, false);
            y += 11;
        }
        g.fill(x + 3, y, x + 9, y + 8, INK);
        g.fill(x + 4, y + 1, x + 8, y + 7, BLOOD);
        g.drawString(this.font, Component.translatable("map.terrassic.you"), x + 16, y, INK, false);
        y += 16;

        int extent = ClientIslandMap.extent();
        if (this.minecraft != null && this.minecraft.player != null) {
            y = this.text(g, Component.translatable("map.terrassic.position", Mth.floor(this.minecraft.player.getX()),
                    Mth.floor(this.minecraft.player.getZ())), x, y, width, INK);
        }
        if (mouseX >= mx && mouseX < mx + side && mouseY >= my && mouseY < my + side) {
            int wx = Math.round(((mouseX - mx + 0.5F) / side * 2.0F - 1.0F) * extent);
            int wz = Math.round(((mouseY - my + 0.5F) / side * 2.0F - 1.0F) * extent);
            this.text(g, Component.translatable("map.terrassic.cursor", wx, wz), x, y + 2, width, INK_SOFT);
        }
    }

    // ---- Katarina and Report: one page at a time

    private List<Lore.Page> foundPages() {
        List<Lore.Page> pages = new ArrayList<>();
        for (Lore.Page p : Lore.ALL) {  // Lore.ALL is in day order
            if (ClientResearch.get().pages().contains(p.id())) {
                pages.add(p);
            }
        }
        return pages;
    }

    private void renderKatarina(GuiGraphics g) {
        List<Lore.Page> pages = this.foundPages();
        int x = this.left + 12;
        if (pages.isEmpty()) {
            this.text(g, Component.translatable("notebook.terrassic.katarina.empty"), x, this.top + 12, W / 2 - 24, INK_SOFT);
            return;
        }
        int index = Mth.clamp(lastKatarinaPage, 0, pages.size() - 1);
        Lore.Page page = pages.get(index);
        g.drawString(this.font, TerrassicFonts.ui("notebook.terrassic.katarina.count", pages.size(), Lore.ALL.size()),
                x, this.top + 8, INK_SOFT, false);
        // her pages are in her handwriting
        this.renderPage(g, Component.translatable("page.terrassic." + page.id() + ".title"),
                TerrassicFonts.hand(Component.translatable("page.terrassic." + page.id() + ".text")), index, pages.size());
    }

    private void renderReport(GuiGraphics g) {
        int index = Mth.clamp(lastReportPage, 0, Lore.REPORT_PAGES - 1);
        // the lab report is typed
        this.renderPage(g, Component.translatable("report.terrassic." + index + ".title"),
                TerrassicFonts.ui(Component.translatable("report.terrassic." + index + ".text")), index, Lore.REPORT_PAGES);
    }

    /** Title on the left page, text flowing from the left page to the right one. */
    private void renderPage(GuiGraphics g, Component title, Component body, int index, int count) {
        int colW = W / 2 - 24;
        int x1 = this.left + 12;
        int x2 = this.left + W / 2 + 12;
        int y = this.top + 24;
        this.heading(g, title, x1, y);
        y += 16;
        int bottom = this.top + H - 30;
        int x = x1;
        for (FormattedCharSequence line : this.font.split(body, colW)) {
            if (y > bottom) {
                if (x == x2) {
                    break;
                }
                x = x2;
                y = this.top + 12;
            }
            g.drawString(this.font, line, x, y, INK, false);
            y += 10;
        }
        Component number = TerrassicFonts.ui("notebook.terrassic.page", index + 1, count);
        g.drawString(this.font, number, this.left + W / 2 - this.font.width(number) / 2, this.top + H - 20, INK_SOFT, false);
    }
}
