package com.terrassic.client;

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
    private static final int PAGE_W = 116;
    private static final int TOP = 12;
    private static final int BOTTOM = H - 28;
    private static final int INK = 0xFF3F2A14;
    private static final int TITLE = 0xFF5C3412;
    private static final int MUTED = 0xFF806240;
    private static final int LINK = 0xFF285078;
    /** The spread open last time, so the book reopens where the player left it (this session). */
    private static int lastSpread;

    private final List<List<Element>> pages = new ArrayList<>();
    private int spread;
    private int left;
    private int top;
    private ItemStack hoveredStack = ItemStack.EMPTY;
    private IndexEntry hoveredEntry;

    public static void open() {
        Minecraft mc = Minecraft.getInstance();
        mc.setScreen(new PocketGuideScreen());
        mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0F));
    }

    public PocketGuideScreen() {
        super(Component.translatable("guide.terrassic.pocket.title"));
    }

    @Override
    protected void init() {
        this.left = (this.width - W) / 2;
        this.top = (this.height - H) / 2;
        this.layout();
        this.spread = Math.min(lastSpread, this.lastSpread());
    }

    // ------------------------------------------------------------------ layout

    private record Topic(String id, ItemStack icon, List<ResourceLocation> recipes) {
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
                ItemStack icon = new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(GsonHelper.getAsString(t, "icon"))));
                List<ResourceLocation> recipes = new ArrayList<>();
                JsonArray rs = GsonHelper.getAsJsonArray(t, "recipes", new JsonArray());
                for (JsonElement r : rs) {
                    recipes.add(new ResourceLocation(r.getAsString()));
                }
                out.add(new Topic(GsonHelper.getAsString(t, "id"), icon, recipes));
            }
        } catch (Exception ex) {
            LogUtils.getLogger().warn("Pocket Guide: could not read {}", CONTENT, ex);
        }
        return out;
    }

    /** Index first, then each topic from a fresh page; an element that does not fit starts the next page. */
    private void layout() {
        this.pages.clear();
        List<Topic> topics = this.topics();
        // index
        List<Element> page = new ArrayList<>();
        page.add(new TitleLine(Component.translatable("guide.terrassic.pocket.title"), ItemStack.EMPTY));
        page.add(new TextLine(Component.translatable("guide.terrassic.pocket.subtitle").getVisualOrderText(), MUTED));
        page.add(new Gap(8));
        List<IndexEntry> entries = new ArrayList<>();
        for (Topic t : topics) {
            IndexEntry entry = new IndexEntry(Component.translatable("guide.terrassic.pocket." + t.id() + ".title"), t.icon());
            entries.add(entry);
            page = this.add(page, entry);
        }
        this.pages.add(page);
        // topics
        for (int i = 0; i < topics.size(); i++) {
            Topic t = topics.get(i);
            entries.get(i).target = this.pages.size();
            page = new ArrayList<>();
            page.add(new TitleLine(Component.translatable("guide.terrassic.pocket." + t.id() + ".title"), t.icon()));
            String body = keys(Component.translatable("guide.terrassic.pocket." + t.id() + ".body").getString());
            String[] paragraphs = body.split("\n");
            for (int p = 0; p < paragraphs.length; p++) {
                if (p > 0) {
                    page = this.add(page, new Gap(5));
                }
                for (FormattedCharSequence line : this.font.split(FormattedText.of(paragraphs[p]), PAGE_W)) {
                    page = this.add(page, new TextLine(line, INK));
                }
            }
            for (ResourceLocation id : t.recipes()) {
                Optional<? extends Recipe<?>> recipe = this.minecraft != null && this.minecraft.level != null
                        ? this.minecraft.level.getRecipeManager().byKey(id) : Optional.empty();
                if (recipe.isPresent()) {
                    page = this.add(page, new Gap(6));
                    page = this.add(page, new RecipeGrid(recipe.get()));
                }
            }
            this.pages.add(page);
        }
        if (this.pages.size() % 2 == 1) {
            this.pages.add(new ArrayList<>());
        }
    }

    /** Adds the element to the page, or closes the page and starts the next one with it. A gap never opens a page. */
    private List<Element> add(List<Element> page, Element e) {
        int used = 0;
        for (Element x : page) {
            used += x.height();
        }
        if (TOP + used + e.height() <= BOTTOM) {
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

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(g);
        g.blit(TEXTURE, this.left, this.top, 0, 0, W, H, TEX_W, TEX_H);
        this.hoveredStack = ItemStack.EMPTY;
        this.hoveredEntry = null;
        for (int side = 0; side < 2; side++) {
            int index = this.spread * 2 + side;
            if (index >= this.pages.size()) {
                continue;
            }
            int x = this.left + (side == 0 ? 14 : W / 2 + 6);
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
            lastSpread = target;
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
    public boolean mouseScrolled(double mx, double my, double delta) {
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
            g.drawString(PocketGuideScreen.this.font, this.text, x, y + (this.icon.isEmpty() ? 2 : 5), TITLE, false);
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
            return 18;
        }

        @Override
        public void render(GuiGraphics g, int x, int y, int mouseX, int mouseY) {
            boolean over = inside(mouseX, mouseY, x, y, PAGE_W, 18);
            if (over) {
                PocketGuideScreen.this.hoveredEntry = this;
            }
            var font = PocketGuideScreen.this.font;
            g.renderItem(this.icon, x, y);
            g.drawString(font, this.name, x + 20, y + 4, over ? LINK : INK, false);
            String number = String.valueOf(this.target + 1);
            int nx = x + PAGE_W - font.width(number);
            g.drawString(font, number, nx, y + 4, MUTED, false);
            for (int dx = x + 22 + font.width(this.name); dx < nx - 3; dx += 3) {
                g.fill(dx, y + 11, dx + 1, y + 12, MUTED);
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
            return 56;
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
                PocketGuideScreen.this.slot(g, x + 2 + col * 18, y + row * 18, stack, mouseX, mouseY);
            }
            g.blit(TEXTURE, x + 60, y + 23, 0, ARROW_V, 8, 7, TEX_W, TEX_H);
            Minecraft mc = Minecraft.getInstance();
            ItemStack result = mc.level != null ? this.recipe.getResultItem(mc.level.registryAccess()) : ItemStack.EMPTY;
            PocketGuideScreen.this.slot(g, x + 74, y + 18, result, mouseX, mouseY);
        }
    }
}
