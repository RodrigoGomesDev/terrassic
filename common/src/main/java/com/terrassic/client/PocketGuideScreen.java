package com.terrassic.client;

import net.minecraft.world.item.crafting.RecipeHolder;
import com.google.gson.JsonArray;
import com.mojang.logging.LogUtils;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.terrassic.Terrassic;
import net.minecraft.ChatFormatting;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.ShapedRecipe;

import java.io.Reader;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * The Pocket Guide's book (v1.1.2, docs/AJUDA.md; look approved by Rodrigo on 31/10/2026): two parchment pages in a
 * stitched leather cover, the game's own font, item icons and recipes on a crafting grid. The topics come from
 * assets/terrassic/pocket_guide.json and the lang files (tools/javagen/gen_pocket_guide.py); they are laid out when the
 * screen opens, flowing onto as many pages as they need, so any language and any GUI scale fit. The index entries
 * jump to their topic; arrows, arrow keys, Page Up/Down and the wheel turn the page.
 */
public class PocketGuideScreen extends Screen {
    private static final ResourceLocation TEXTURE = Terrassic.id("textures/gui/pocket_guide.png");
    private static final ResourceLocation CONTENT = Terrassic.id("pocket_guide.json");
    private static final int W = 276;
    private static final int H = 182;
    private static final int TEX_W = 512;
    private static final int TEX_H = 256;
    private static final int ARROW_V = 184;
    /** Text width and the page margins: 8 px from the cover, 9 from the spine, 10 from the top (05/11/2026). */
    private static final int PAGE_W = 110;
    private static final int LEFT_PAGE = 18;
    private static final int RIGHT_PAGE = 148;
    private static final int TOP = 18;
    private static final int BOTTOM = H - 30;
    private static final int LINE = 10;
    private static final int PARAGRAPH = 5;
    /** A topic starts on the same page as the one before when its title and this many lines still fit. */
    private static final int MIN_START_LINES = 4;
    private static final int INK = 0xFF3F2A14;
    private static final int TITLE = 0xFF5C3412;
    private static final int MUTED = 0xFF806240;
    private static final int LINK = 0xFF285078;
    /** The spread open last time in each book, so it reopens where the player left it (this session). */
    private static final java.util.Map<String, Integer> LAST_SPREAD = new java.util.HashMap<>();

    /** Empty for the Pocket Guide, or the Bestiary shown: "carnivores", "herbivores", "flyers", "marine" (1.7.1). */
    private final String volume;

    private final List<List<Element>> pages = new ArrayList<>();
    private int spread;
    private int left;
    private int top;
    private ItemStack hoveredStack = ItemStack.EMPTY;
    private IndexEntry hoveredEntry;

    /** The spread shown (for the development checks in client/dev). */
    public int spreadIndex() {
        return this.spread;
    }

    public static void open() {
        open("");
    }

    public static void open(String volume) {
        Minecraft mc = Minecraft.getInstance();
        mc.setScreen(new PocketGuideScreen(volume));
        mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0F));
    }

    public PocketGuideScreen(String volume) {
        super(Component.translatable(volume.isEmpty() ? "guide.terrassic.pocket.title" : "item.terrassic.bestiary_" + volume));
        this.volume = volume;
    }

    @Override
    protected void init() {
        this.left = (this.width - W) / 2;
        this.top = (this.height - H) / 2;
        this.layout();
        this.spread = Math.min(LAST_SPREAD.getOrDefault(this.volume, 0), this.lastSpread());
    }

    // ------------------------------------------------------------------ layout

    /** {@code list}: a list drawn after the text ("species": every active species, 1.7). */
    private record Topic(String id, ItemStack icon, List<ResourceLocation> recipes, String list) {
    }

    private List<Topic> topics() {
        List<Topic> out = new ArrayList<>();
        Optional<Resource> res = Minecraft.getInstance().getResourceManager().getResource(CONTENT);
        if (res.isEmpty()) {
            return out;
        }
        try (Reader reader = res.get().openAsReader()) {
            JsonObject root = GsonHelper.parse(reader);
            for (JsonElement e : GsonHelper.getAsJsonArray(root, "topics")) {
                JsonObject t = e.getAsJsonObject();
                ItemStack icon = new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(GsonHelper.getAsString(t, "icon"))));
                List<ResourceLocation> recipes = new ArrayList<>();
                JsonArray rs = GsonHelper.getAsJsonArray(t, "recipes", new JsonArray());
                for (JsonElement r : rs) {
                    recipes.add(ResourceLocation.parse(r.getAsString()));
                }
                out.add(new Topic(GsonHelper.getAsString(t, "id"), icon, recipes, GsonHelper.getAsString(t, "list", "")));
            }
        } catch (Exception ex) {
            LogUtils.getLogger().warn("Pocket Guide: could not read {}", CONTENT, ex);
        }
        return out;
    }

    /**
     * Index first, then the topics. A topic starts on a fresh page unless its title and a few lines still fit under the
     * one before (with a rule between them). Paragraphs break between lines, never leaving one line alone at the foot
     * of a page or at the head of the next; recipes, species and titles are kept whole.
     */
    private void layout() {
        this.pages.clear();
        if (!this.volume.isEmpty()) {
            this.layoutVolume();
            return;
        }
        List<Topic> topics = this.topics();
        // index
        List<Element> page = new ArrayList<>();
        page.add(new TitleLine(Component.translatable("guide.terrassic.pocket.title"), ItemStack.EMPTY));
        page.add(new TextLine(Component.translatable("guide.terrassic.pocket.subtitle").getVisualOrderText(), MUTED));
        page.add(new Gap(6));
        List<IndexEntry> entries = new ArrayList<>();
        for (Topic t : topics) {
            IndexEntry entry = new IndexEntry(Component.translatable("guide.terrassic.pocket." + t.id() + ".title"), t.icon());
            entries.add(entry);
            page = this.add(page, entry);
        }
        this.pages.add(page);
        // topics
        page = new ArrayList<>();
        for (int i = 0; i < topics.size(); i++) {
            Topic t = topics.get(i);
            TitleLine title = new TitleLine(Component.translatable("guide.terrassic.pocket." + t.id() + ".title"), t.icon());
            if (!page.isEmpty()) {
                if (used(page) + Rule.HEIGHT + title.height() + MIN_START_LINES * LINE <= BOTTOM - TOP) {
                    page.add(new Rule());
                } else {
                    this.pages.add(page);
                    page = new ArrayList<>();
                }
            }
            entries.get(i).target = this.pages.size();
            page.add(title);
            String body = keys(Component.translatable("guide.terrassic.pocket." + t.id() + ".body").getString());
            String[] paragraphs = body.split("\n");
            for (int p = 0; p < paragraphs.length; p++) {
                page = this.paragraph(page, this.font.split(FormattedText.of(paragraphs[p]), PAGE_W), p > 0 ? PARAGRAPH : 0, INK);
            }
            if ("species".equals(t.list())) {
                List<SpeciesEntry> species = this.species();
                page = this.paragraph(page, this.font.split(count(species.size()), PAGE_W), PARAGRAPH, MUTED);
                for (SpeciesEntry e : species) {
                    page = this.add(page, new Gap(8));
                    page = this.add(page, e);
                }
            }
            for (ResourceLocation id : t.recipes()) {
                Optional<RecipeHolder<?>> recipe = this.minecraft != null && this.minecraft.level != null
                        ? this.minecraft.level.getRecipeManager().byKey(id).map(holder -> (RecipeHolder<?>) holder) : Optional.empty();
                if (recipe.isPresent()) {
                    page = this.add(page, new Gap(8));
                    page = this.add(page, new RecipeGrid(recipe.get().value()));
                }
            }
        }
        if (!page.isEmpty()) {
            this.pages.add(page);
        }
        if (this.pages.size() % 2 == 1) {
            this.pages.add(new ArrayList<>());
        }
    }

    /**
     * A Bestiary (1.7.1): its title, the opening text and an index of its species (each line jumps to the page), then
     * a page for every species. The Pocket Guide grew a page per species; with the eras to come that would be hundreds.
     */
    private void layoutVolume() {
        String key = "guide.terrassic.bestiary." + this.volume;
        List<Element> page = new ArrayList<>();
        page.add(new TitleLine(Component.translatable(key + ".title"), ItemStack.EMPTY));
        page = this.paragraph(page, this.font.split(Component.translatable(key + ".subtitle"), PAGE_W), 0, MUTED);
        page.add(new Gap(6));
        String[] paragraphs = Component.translatable(key + ".body").getString().split("\n");
        for (int p = 0; p < paragraphs.length; p++) {
            page = this.paragraph(page, this.font.split(FormattedText.of(paragraphs[p]), PAGE_W), p > 0 ? PARAGRAPH : 0, INK);
        }
        List<SpeciesEntry> species = this.species();
        page = this.paragraph(page, this.font.split(count(species.size()), PAGE_W), PARAGRAPH, MUTED);
        page = this.add(page, new Gap(4));
        List<IndexEntry> entries = new ArrayList<>();
        for (SpeciesEntry e : species) {
            IndexEntry entry = new IndexEntry(e.name.copy().withStyle(ChatFormatting.RESET), e.egg);
            entries.add(entry);
            page = this.add(page, entry);
        }
        for (int i = 0; i < species.size(); i++) {
            if (!page.isEmpty()) {
                this.pages.add(page);
            }
            page = new ArrayList<>();
            entries.get(i).target = this.pages.size();
            page.add(species.get(i));
        }
        if (!page.isEmpty()) {
            this.pages.add(page);
        }
        if (this.pages.size() % 2 == 1) {
            this.pages.add(new ArrayList<>());
        }
    }

    private static Component count(int species) {
        return species == 1 ? Component.translatable("guide.terrassic.pocket.list.count.one")
                : Component.translatable("guide.terrassic.pocket.list.count", species);
    }

    /** Which Bestiary a species is in: flyers and sea animals by their kind, the rest by diet (omnivores with herbivores). */
    private static String volumeOf(com.terrassic.research.GuideSpecies s, com.terrassic.entity.DinosaurEntity dino) {
        if (dino instanceof com.terrassic.entity.FlyingDinosaur) {
            return "flyers";
        }
        if (dino instanceof com.terrassic.entity.SwimmingDinosaur) {
            return "marine";
        }
        return "carnivore".equals(s.diet()) || "piscivore".equals(s.diet()) ? "carnivores" : "herbivores";
    }

    private static int used(List<Element> page) {
        int used = 0;
        for (Element x : page) {
            used += x.height();
        }
        return used;
    }

    /**
     * A paragraph, after a gap: as many lines as fit, the rest on the next page, but never a single line left behind
     * or carried over (a two-line paragraph moves whole).
     */
    private List<Element> paragraph(List<Element> page, List<FormattedCharSequence> lines, int gap, int colour) {
        int from = 0;
        while (from < lines.size()) {
            int left = lines.size() - from;
            int room = page.isEmpty() ? (BOTTOM - TOP) / LINE : (BOTTOM - TOP - used(page) - gap) / LINE;
            int take = Math.min(left, Math.max(0, room));
            if (take < left) {
                if (left - take < 2) {
                    take = left - 2;
                }
                if (take < 2 && !page.isEmpty()) {
                    take = 0;
                }
            }
            if (take <= 0) {
                this.pages.add(page);
                page = new ArrayList<>();
                continue;
            }
            if (!page.isEmpty() && gap > 0) {
                page.add(new Gap(gap));
            }
            for (int i = 0; i < take; i++) {
                page.add(new TextLine(lines.get(from + i), colour));
            }
            from += take;
            if (from < lines.size()) {
                this.pages.add(page);
                page = new ArrayList<>();
            }
        }
        return page;
    }

    /** Adds the element to the page, or closes the page and starts the next one with it. A gap never opens a page. */
    private List<Element> add(List<Element> page, Element e) {
        if (TOP + used(page) + e.height() <= BOTTOM) {
            page.add(e);
            return page;
        }
        this.pages.add(page);
        List<Element> next = new ArrayList<>();
        if (!(e instanceof Gap)) {
            next.add(e);
        }
        return next;
    }

    /**
     * 1.7 (player feedback: "add a section that shows all the dinos and a taming section to the guidebook"): every
     * species that lives in the world now (config/Eras), in the Field Guide's order, with what the Field Guide and the
     * animal itself say: diet, real size, whether it is ridden, how it is tamed, what it eats and how much.
     */
    private List<SpeciesEntry> species() {
        List<SpeciesEntry> out = new ArrayList<>();
        Minecraft mc = Minecraft.getInstance();
        for (com.terrassic.research.GuideSpecies s : com.terrassic.research.GuideSpecies.ALL) {
            if (!com.terrassic.config.Eras.active(s)) {
                continue;
            }
            net.minecraft.world.entity.EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(Terrassic.id(s.id()));
            com.terrassic.entity.DinosaurEntity dino = null;
            if (mc.level != null && type.create(mc.level) instanceof com.terrassic.entity.DinosaurEntity d) {
                dino = d;
            }
            if (this.volume.isEmpty() || this.volume.equals(volumeOf(s, dino))) {
                out.add(new SpeciesEntry(s, dino));
            }
            if (dino != null) {
                dino.discard();
            }
        }
        return out;
    }

    /** %key:name% -> the key the player has bound for it. */
    private static String keys(String text) {
        Minecraft mc = Minecraft.getInstance();
        for (String name : new String[]{"use", "attack", "jump", "sneak", "inventory", "dino_screen", "descend", "whistle"}) {
            String token = "%key:" + name + "%";
            if (!text.contains(token)) {
                continue;
            }
            KeyMapping key = switch (name) {
                case "use" -> mc.options.keyUse;
                case "attack" -> mc.options.keyAttack;
                case "jump" -> mc.options.keyJump;
                case "sneak" -> mc.options.keyShift;
                case "inventory" -> mc.options.keyInventory;
                case "dino_screen" -> DinoControls.DINO_SCREEN;
                case "whistle" -> DinoControls.WHISTLE;
                default -> DinoControls.DESCEND;
            };
            text = text.replace(token, "[" + key.getTranslatedKeyMessage().getString() + "]");
        }
        return text;
    }

    private int lastSpread() {
        return Math.max(0, (this.pages.size() - 1) / 2);
    }

    // ------------------------------------------------------------------ drawing

    /** 1.21: Screen.render blurs and dims here, over whatever this screen already drew; ours draws its own backdrop. */
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
        g.blit(TEXTURE, this.left, this.top, 0, 0, W, H, TEX_W, TEX_H);
        this.hoveredStack = ItemStack.EMPTY;
        this.hoveredEntry = null;
        for (int side = 0; side < 2; side++) {
            int index = this.spread * 2 + side;
            if (index >= this.pages.size()) {
                continue;
            }
            int x = this.left + (side == 0 ? LEFT_PAGE : RIGHT_PAGE);
            int y = this.top + TOP;
            for (Element e : this.pages.get(index)) {
                e.render(g, x, y, mouseX, mouseY);
                y += e.height();
            }
            String number = String.valueOf(index + 1);
            int cx = this.left + (side == 0 ? W / 4 : 3 * W / 4);
            g.drawString(this.font, number, cx - this.font.width(number) / 2, this.top + H - 22, MUTED, false);
        }
        if (this.spread > 0) {
            boolean lit = this.overBack(mouseX, mouseY);
            g.blit(TEXTURE, this.left + 14, this.top + H - 21, lit ? 24 : 16, ARROW_V, 8, 7, TEX_W, TEX_H);
        }
        if (this.spread < this.lastSpread()) {
            boolean lit = this.overNext(mouseX, mouseY);
            g.blit(TEXTURE, this.left + W - 22, this.top + H - 21, lit ? 8 : 0, ARROW_V, 8, 7, TEX_W, TEX_H);
        }
        super.render(g, mouseX, mouseY, partialTick);
        if (!this.hoveredStack.isEmpty()) {
            g.renderTooltip(this.font, this.hoveredStack, mouseX, mouseY);
        }
    }

    /** Draws a line of text, shrunk to {@code room} when it is wider (a long name or title never runs into the spine). */
    private void fitted(GuiGraphics g, Component text, int x, int y, int room, int colour) {
        int width = this.font.width(text);
        if (width <= room) {
            g.drawString(this.font, text, x, y, colour, false);
            return;
        }
        float scale = room / (float) width;
        g.pose().pushPose();
        g.pose().translate(x, y + (8 - 8 * scale) / 2, 0);
        g.pose().scale(scale, scale, 1);
        g.drawString(this.font, text, 0, 0, colour, false);
        g.pose().popPose();
    }

    private boolean overBack(double mx, double my) {
        return this.spread > 0 && inside(mx, my, this.left + 12, this.top + H - 23, 12, 11);
    }

    private boolean overNext(double mx, double my) {
        return this.spread < this.lastSpread() && inside(mx, my, this.left + W - 24, this.top + H - 23, 12, 11);
    }

    private static boolean inside(double mx, double my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }

    private void slot(GuiGraphics g, int x, int y, ItemStack stack, int mouseX, int mouseY) {
        g.fill(x, y, x + 18, y + 18, 0xFF8B8B8B);
        g.fill(x, y, x + 17, y + 1, 0xFF373737);
        g.fill(x, y, x + 1, y + 17, 0xFF373737);
        g.fill(x + 1, y + 17, x + 18, y + 18, 0xFFFFFFFF);
        g.fill(x + 17, y + 1, x + 18, y + 17, 0xFFFFFFFF);
        if (!stack.isEmpty()) {
            g.renderItem(stack, x + 1, y + 1);
            g.renderItemDecorations(this.font, stack, x + 1, y + 1);
            if (inside(mouseX, mouseY, x, y, 18, 18)) {
                this.hoveredStack = stack;
            }
        }
    }

    // ------------------------------------------------------------------ input

    private void turn(int to) {
        int target = Math.max(0, Math.min(this.lastSpread(), to));
        if (target != this.spread) {
            this.spread = target;
            LAST_SPREAD.put(this.volume, target);
            if (this.minecraft != null) {
                this.minecraft.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0F));
            }
        }
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        if (button == 0) {
            if (this.overBack(mx, my)) {
                this.turn(this.spread - 1);
                return true;
            }
            if (this.overNext(mx, my)) {
                this.turn(this.spread + 1);
                return true;
            }
            if (this.hoveredEntry != null) {
                this.turn(this.hoveredEntry.target / 2);
                return true;
            }
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double scrollX, double delta) {
        this.turn(this.spread + (delta < 0 ? 1 : -1));
        return true;
    }

    @Override
    public boolean keyPressed(int key, int scan, int modifiers) {
        // arrows and Page Up/Down (GLFW 262 right, 263 left, 266 page up, 267 page down)
        if (key == 262 || key == 267) {
            this.turn(this.spread + 1);
            return true;
        }
        if (key == 263 || key == 266) {
            this.turn(this.spread - 1);
            return true;
        }
        return super.keyPressed(key, scan, modifiers);
    }

    // ------------------------------------------------------------------ page elements

    private interface Element {
        int height();

        void render(GuiGraphics g, int x, int y, int mouseX, int mouseY);
    }

    private record Gap(int height) implements Element {
        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
        }
    }

    /** The dotted rule between two topics that share a page. */
    private record Rule() implements Element {
        static final int HEIGHT = 16;

        @Override
        public int height() {
            return HEIGHT;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
            for (int dx = x + 20; dx < x + PAGE_W - 20; dx += 3) {
                g.fill(dx, y + 6, dx + 1, y + 7, MUTED);
            }
        }
    }

    private final class TextLine implements Element {
        private final FormattedCharSequence text;
        private final int colour;

        TextLine(FormattedCharSequence text, int colour) {
            this.text = text;
            this.colour = colour;
        }

        @Override
        public int height() {
            return 10;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
            g.drawString(PocketGuideScreen.this.font, this.text, x, y, this.colour, false);
        }
    }

    /** A topic's title in bold, its item in a slot at the right edge of the page. */
    private final class TitleLine implements Element {
        private final Component text;
        private final ItemStack icon;

        TitleLine(Component text, ItemStack icon) {
            this.text = text.copy().withStyle(ChatFormatting.BOLD);
            this.icon = icon;
        }

        @Override
        public int height() {
            return this.icon.isEmpty() ? 12 : 22;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
            PocketGuideScreen.this.fitted(g, this.text, x, y + (this.icon.isEmpty() ? 2 : 5), this.icon.isEmpty() ? PAGE_W : PAGE_W - 22, TITLE);
            if (!this.icon.isEmpty()) {
                PocketGuideScreen.this.slot(g, x + PAGE_W - 18, y, this.icon, mouseX, mouseY);
            }
        }
    }

    /** One line of the index: icon, name, dotted leader, page number; clicking it opens the topic. */
    private final class IndexEntry implements Element {
        private final Component name;
        private final ItemStack icon;
        private int target;

        IndexEntry(Component name, ItemStack icon) {
            this.name = name;
            this.icon = icon;
        }

        @Override
        public int height() {
            return 15;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
            boolean over = inside(mouseX, mouseY, x, y, PAGE_W, 15);
            if (over) {
                PocketGuideScreen.this.hoveredEntry = this;
            }
            var font = PocketGuideScreen.this.font;
            g.renderItem(this.icon, x, y - 1);
            String number = String.valueOf(this.target + 1);
            int nx = x + PAGE_W - font.width(number);
            PocketGuideScreen.this.fitted(g, this.name, x + 20, y + 3, nx - 4 - x - 20, over ? LINK : INK);
            g.drawString(font, number, nx, y + 3, MUTED, false);
            for (int dx = x + 22 + font.width(this.name); dx < nx - 3; dx += 3) {
                g.fill(dx, y + 10, dx + 1, y + 11, MUTED);
            }
        }
    }

    /** One species of the "The Dinosaurs" topic: its egg and name, then diet and size, how it is tamed, and its food
     *  with the amount taming takes. Kept whole on one page. */
    private final class SpeciesEntry implements Element {
        private final ItemStack egg;
        private final Component name;
        private final List<FormattedCharSequence> lines = new ArrayList<>();
        private final List<ItemStack> foods = new ArrayList<>();

        SpeciesEntry(com.terrassic.research.GuideSpecies s, com.terrassic.entity.DinosaurEntity dino) {
            this.egg = MyDinosScreen.egg(s.id());
            this.name = Component.translatable("entity.terrassic." + s.id()).withStyle(ChatFormatting.BOLD);
            String length = s.length() >= 10.0F ? String.valueOf(Math.round(s.length()))
                    : String.format(java.util.Locale.ROOT, "%.1f", s.length()).replace(".0", "");
            Component about = Component.translatable("guide.terrassic.pocket.list.diet." + s.diet())
                    .append(" · ").append(Component.translatable("guide.terrassic.pocket.list.size", length));
            if (s.rideable()) {
                about = about.copy().append(" · ").append(Component.translatable("guide.terrassic.pocket.list.rideable"));
            }
            var font = PocketGuideScreen.this.font;
            this.lines.addAll(font.split(about, PAGE_W));
            boolean feeding = dino != null && dino.tameMethod() == com.terrassic.entity.DinosaurEntity.TameMethod.FEEDING;
            Component how = Component.translatable(feeding ? "guide.terrassic.pocket.list.tame.feed" : "guide.terrassic.pocket.list.tame.egg");
            this.lines.addAll(font.split(how, PAGE_W));
            if (dino != null) {
                for (String id : dino.acceptedFoods()) {
                    if (this.foods.size() >= 6) {
                        break;
                    }
                    ResourceLocation rl = ResourceLocation.tryParse(id);
                    if (rl != null) {
                        this.foods.add(new ItemStack(BuiltInRegistries.ITEM.get(rl)));
                    }
                }
                int goal = dino.foodGoal();
                Component amount = dino.isHunter() ? (goal == 64 ? Component.translatable("guide.terrassic.pocket.list.food.stack")
                        : Component.translatable("guide.terrassic.pocket.list.food.stacks", goal / 64, goal))
                        : Component.translatable("guide.terrassic.pocket.list.food", goal);
                this.lines.addAll(font.split(amount, PAGE_W));
            }
        }

        @Override
        public int height() {
            return 18 + this.lines.size() * 10 + (this.foods.isEmpty() ? 0 : 18);
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
            var font = PocketGuideScreen.this.font;
            g.renderItem(this.egg, x, y);
            if (inside(mouseX, mouseY, x, y, 16, 16)) {
                PocketGuideScreen.this.hoveredStack = this.egg;
            }
            PocketGuideScreen.this.fitted(g, this.name, x + 20, y + 4, PAGE_W - 20, TITLE);
            int yy = y + 18;
            for (FormattedCharSequence line : this.lines) {
                g.drawString(font, line, x, yy, INK, false);
                yy += 10;
            }
            if (!this.foods.isEmpty()) {
                int fx = x;
                for (ItemStack food : this.foods) {
                    g.renderItem(food, fx, yy);
                    if (inside(mouseX, mouseY, fx, yy, 16, 16)) {
                        PocketGuideScreen.this.hoveredStack = food;
                    }
                    fx += 17;
                }
            }
        }
    }

    /** A crafting recipe on a 3x3 grid, an arrow and the result; ingredients with several items cycle every second. */
    private final class RecipeGrid implements Element {
        private final Recipe<?> recipe;

        RecipeGrid(Recipe<?> recipe) {
            this.recipe = recipe;
        }

        @Override
        public int height() {
            return 54;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
            int width = this.recipe instanceof ShapedRecipe shaped ? shaped.getWidth() : 3;
            List<Ingredient> ingredients = this.recipe.getIngredients();
            long second = System.currentTimeMillis() / 1000L;
            for (int i = 0; i < 9; i++) {
                int col = i % 3;
                int row = i / 3;
                ItemStack stack = ItemStack.EMPTY;
                int index = col < width ? row * width + col : -1;
                if (index >= 0 && index < ingredients.size()) {
                    ItemStack[] options = ingredients.get(index).getItems();
                    if (options.length > 0) {
                        stack = options[(int) (second % options.length)];
                    }
                }
                PocketGuideScreen.this.slot(g, x + 9 + col * 18, y + row * 18, stack, mouseX, mouseY);
            }
            x += 7;
            g.blit(TEXTURE, x + 60, y + 23, 0, ARROW_V, 8, 7, TEX_W, TEX_H);
            Minecraft mc = Minecraft.getInstance();
            ItemStack result = mc.level != null ? this.recipe.getResultItem(mc.level.registryAccess()) : ItemStack.EMPTY;
            PocketGuideScreen.this.slot(g, x + 74, y + 18, result, mouseX, mouseY);
        }
    }
}
