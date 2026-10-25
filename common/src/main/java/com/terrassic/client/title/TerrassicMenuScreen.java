package com.terrassic.client.title;

import com.mojang.blaze3d.systems.RenderSystem;
import com.terrassic.Terrassic;
import com.terrassic.client.ClientConfig;
import com.terrassic.client.RulesScreen;
import com.terrassic.client.ui.TerrassicUi;
import dev.architectury.event.CompoundEventResult;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.platform.Platform;
import net.minecraft.Util;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.components.PlainTextButton;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.gui.screens.AccessibilityOptionsScreen;
import net.minecraft.client.gui.screens.LanguageSelectScreen;
import net.minecraft.client.gui.screens.OptionsScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.WinScreen;
import net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen;
import net.minecraft.client.gui.screens.multiplayer.SafetyScreen;
import net.minecraft.client.gui.screens.worldselection.SelectWorldScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static com.terrassic.client.ui.TerrassicPalette.*;

import java.util.List;
import java.util.function.Supplier;

/**
 * The Terrassic main menu (docs/MENU.md), in place of the vanilla title screen on Fabric and Forge.
 *
 * <p>A scene of the Late Cretaceous fills the screen (rendered in Blender from the mod's own blocks and models by
 * tools/menugen; it drifts slowly sideways), with the stone TERRASSIC title of the cover and the slogan at the top
 * left, a column of options with their own icons under it, and a museum placard of the animal in the scene at the
 * bottom right. The highlighted option (mouse or keyboard) lights up in amber with a band and a short hint. Language
 * and accessibility sit as icons at the top right; the Mojang copyright opens the credits, as in vanilla. Realms is
 * left out (it does not run mods); "Mods" opens the Forge mod list, or Mod Menu's on Fabric when it is installed.
 * "Terrassic Rules" opens the defaults for new worlds (the button ClientHooks gives the vanilla title screen).
 * Colours and the divider come from the "Âmbar e Basalto" identity (docs/IDENTIDADE.md).
 *
 * <p>Swapped in for {@link TitleScreen} through Architectury's SET_SCREEN event, so every path that opens the title
 * screen lands here. {@code "title_screen": false} in config/terrassic-client.json brings the vanilla screen back.
 */
public class TerrassicMenuScreen extends Screen {
    private static final Logger LOG = LoggerFactory.getLogger(Terrassic.MOD_ID);
    private static final String TEX = "textures/gui/title/menu/";
    private static final ResourceLocation TITLE = Terrassic.id(TEX + "titulo.png");
    private static final ResourceLocation ICONS = Terrassic.id(TEX + "icones.png");
    private static final int TITLE_W = 950;
    private static final int TITLE_H = 150;
    private static final int BG_W = 1920;
    private static final int BG_H = 1080;

    /** The scenes of the menu; one is picked each time the game starts. */
    private static final List<Scene> SCENES = List.of(new Scene("nevoa"), new Scene("triceratops"), new Scene("espinossauro"),
            new Scene("pteranodonte"));

    private static final int ICON_COLUMNS = 8;
    private static final int LEFT = 24;
    private static final int ROW = 24;
    private static final int BAND = 168;
    /** Seconds of one slow sideways drift of the scene (there and back). */
    private static final float DRIFT_SECONDS = 120.0F;
    private static final float FADE_SECONDS = 1.2F;
    private static final Component COPYRIGHT = Component.literal("Copyright Mojang AB. Do not distribute!");

    private static boolean firstShow = true;
    private static Scene scene;

    private final long openedAt = Util.getMillis();
    private final boolean fadeIn;
    private int titleW;
    private int titleH;
    private int titleY;
    private int divider;
    /** Height of one option: ROW, or a little less when the screen is short (GUI scale 3 or 4). */
    private int row = ROW;

    public TerrassicMenuScreen() {
        super(Component.translatable("narrator.screen.title"));
        this.fadeIn = firstShow;
        firstShow = false;
        if (scene == null) {
            scene = SCENES.get((int) (Math.random() * SCENES.size()));
        }
    }

    /** Puts this screen in place of the vanilla title screen (called from TerrassicClient). */
    public static void register() {
        ClientGuiEvent.SET_SCREEN.register(screen -> screen != null && screen.getClass() == TitleScreen.class
                && ClientConfig.titleScreen()
                ? CompoundEventResult.interruptTrue(new TerrassicMenuScreen())
                : CompoundEventResult.pass());
    }

    @Override
    protected void init() {
        // smooth scaling for the two big images (the icons stay crisp)
        this.minecraft.getTextureManager().getTexture(scene.background()).setFilter(true, false);
        this.minecraft.getTextureManager().getTexture(TITLE).setFilter(true, false);

        this.titleW = Math.min(200, this.width / 2 - LEFT);
        this.titleH = this.titleW * TITLE_H / TITLE_W;
        this.titleY = Math.max(10, (int) (this.height * 0.09F));
        Supplier<Screen> mods = modsScreen(this);
        int count = mods != null ? 6 : 5;
        int top = this.titleY + this.titleH + 32;
        this.row = Mth.clamp((this.height - 22 - top - 6) / count, 20, ROW);
        int y = Math.max(top, (int) (this.height * 0.40F));
        y = Math.min(y, this.height - count * this.row - 6 - 22);

        MenuEntry single = new MenuEntry(LEFT, y, this.row, 0, Component.translatable("menu.singleplayer"),
                "singleplayer", () -> this.minecraft.setScreen(new SelectWorldScreen(this)));
        this.addRenderableWidget(single);
        y += this.row;

        MenuEntry multi = new MenuEntry(LEFT, y, this.row, 1, Component.translatable("menu.multiplayer"), "multiplayer", () -> {
            Screen next = this.minecraft.options.skipMultiplayerWarning ? new JoinMultiplayerScreen(this) : new SafetyScreen(this);
            this.minecraft.setScreen(next);
        });
        if (!this.minecraft.allowsMultiplayer()) {
            multi.active = false;
            multi.setTooltip(Tooltip.create(Component.translatable("title.multiplayer.disabled")));
        }
        this.addRenderableWidget(multi);
        y += this.row;

        this.addRenderableWidget(new MenuEntry(LEFT, y, this.row, 7, Component.translatable("rules.terrassic.ui.button"), "rules",
                () -> this.minecraft.setScreen(new RulesScreen(this, false))));
        y += this.row;

        if (mods != null) {
            this.addRenderableWidget(new MenuEntry(LEFT, y, this.row, 2, Component.translatable("menu.terrassic.mods"), "mods",
                    () -> this.minecraft.setScreen(mods.get())));
            y += this.row;
        }

        this.addRenderableWidget(new MenuEntry(LEFT, y, this.row, 3, Component.translatable("menu.options"), "options",
                () -> this.minecraft.setScreen(new OptionsScreen(this, this.minecraft.options))));
        y += this.row + 6;
        this.divider = y - 4;

        this.addRenderableWidget(new MenuEntry(LEFT, y, this.row, 4, Component.translatable("menu.quit"), "quit",
                () -> this.minecraft.stop()));

        IconButton language = new IconButton(this.width - 42, 8, 5, Component.translatable("options.language"),
                () -> this.minecraft.setScreen(new LanguageSelectScreen(this, this.minecraft.options, this.minecraft.getLanguageManager())));
        IconButton access = new IconButton(this.width - 22, 8, 6, Component.translatable("options.accessibility.title"),
                () -> this.minecraft.setScreen(new AccessibilityOptionsScreen(this, this.minecraft.options)));
        this.addRenderableWidget(language);
        this.addRenderableWidget(access);

        int cw = this.font.width(COPYRIGHT);
        this.addRenderableWidget(new PlainTextButton(this.width - cw - 5, this.height - 10, cw, 10, COPYRIGHT,
                b -> this.minecraft.setScreen(new WinScreen(false, () -> this.minecraft.setScreen(this))), this.font));

        this.setInitialFocus(single);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        float seconds = (Util.getMillis() - this.openedAt) / 1000.0F;
        renderScene(g, seconds);

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        g.blit(TITLE, LEFT - 4, this.titleY, this.titleW, this.titleH, 0.0F, 0.0F, TITLE_W, TITLE_H, TITLE_W, TITLE_H);
        int ruleY = this.titleY + this.titleH + 6;
        g.fill(LEFT - 2, ruleY, LEFT + 38, ruleY + 1, AMBER_500);
        g.drawString(this.font, Component.translatable("menu.terrassic.slogan"), LEFT - 2, ruleY + 7, rgb(STONE_200), true);
        TerrassicUi.divider(g, LEFT, LEFT + 120, this.divider);

        renderPlacard(g);
        String version = "Terrassic " + Platform.getMod(Terrassic.MOD_ID).getVersion();
        g.drawString(this.font, version, 6, this.height - 10, rgb(STONE_400), false);

        super.render(g, mouseX, mouseY, partialTick);

        if (this.fadeIn && seconds < FADE_SECONDS) {
            int a = (int) ((1.0F - seconds / FADE_SECONDS) * 255.0F);
            g.fill(0, 0, this.width, this.height, a << 24);
        }
    }

    /** The scene, cover-fitted to the screen and drifting slowly sideways. */
    private void renderScene(GuiGraphics g, float seconds) {
        float scale = Math.max(this.width / (float) BG_W, this.height / (float) BG_H) * 1.04F;
        int w = Mth.ceil(BG_W * scale);
        int h = Mth.ceil(BG_H * scale);
        float spare = (w - this.width) / 2.0F;
        float x = -spare + spare * 0.8F * Mth.sin(seconds * Mth.TWO_PI / DRIFT_SECONDS);
        float y = -(h - this.height) / 2.0F;
        g.pose().pushPose();
        g.pose().translate(x, y, 0.0F);
        g.blit(scene.background(), 0, 0, w, h, 0.0F, 0.0F, BG_W, BG_H, BG_W, BG_H);
        g.pose().popPose();
    }

    /** Museum placard of the animal in the scene, right-aligned at the bottom right. */
    private void renderPlacard(GuiGraphics g) {
        int right = this.width - 10;
        int y = this.height - 50;
        Component name = Component.translatable(scene.key("name"));
        Component when = Component.translatable(scene.key("when"));
        Component facts = Component.translatable(scene.key("facts"));
        int nameW = this.font.width(name);
        int lineW = Math.max(120, Math.max(nameW, Math.max(this.font.width(when), this.font.width(facts))));
        g.fill(right - lineW, y, right, y + 1, STONE_400);
        g.drawString(this.font, name, right - nameW, y + 4, rgb(BONE_100), true);
        g.drawString(this.font, when, right - this.font.width(when), y + 15, rgb(STONE_300), true);
        g.drawString(this.font, facts, right - this.font.width(facts), y + 25, rgb(STONE_300), true);
    }

    @Override
    public boolean shouldCloseOnEsc() {
        return false;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    /** Forge's mod list, or Mod Menu's on Fabric, or null when neither is there (the entry is then left out). */
    private static Supplier<Screen> modsScreen(Screen parent) {
        for (String name : new String[]{"net.minecraftforge.client.gui.ModListScreen", "com.terraformersmc.modmenu.gui.ModsScreen"}) {
            try {
                var constructor = Class.forName(name).getConstructor(Screen.class);
                return () -> {
                    try {
                        return (Screen) constructor.newInstance(parent);
                    } catch (ReflectiveOperationException e) {
                        LOG.warn("Could not open the mod list {}: {}", name, e.toString());
                        return parent;
                    }
                };
            } catch (ReflectiveOperationException | LinkageError ignored) {
                // not installed: try the next one
            }
        }
        return null;
    }

    private static void icon(GuiGraphics g, int column, int row, int x, int y) {
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        g.blit(ICONS, x, y, column * 16, row * 16, 16, 16, ICON_COLUMNS * 16, 48);
    }

    /** A scene of the menu: its background texture and its placard texts (menu.terrassic.scene.<id>.*). */
    private record Scene(String id) {
        ResourceLocation background() {
            return Terrassic.id(TEX + "fundo_" + this.id + ".png");
        }

        String key(String part) {
            return "menu.terrassic.scene." + this.id + "." + part;
        }
    }

    /** One option of the menu: icon, label and, while highlighted, an amber band and a hint line. */
    private class MenuEntry extends AbstractButton {
        private final int column;
        private final Component hint;
        private final Runnable action;

        MenuEntry(int x, int y, int height, int column, Component label, String id, Runnable action) {
            super(x, y, 160, height, label);
            this.column = column;
            this.hint = Component.translatable("menu.terrassic." + id + ".hint");
            this.action = action;
        }

        @Override
        public void onPress() {
            this.action.run();
        }

        @Override
        protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
            boolean lit = this.active && this.isHoveredOrFocused();
            int x = this.getX();
            int y = this.getY();
            if (lit) {
                // amber band fading to the right, and a bar at its left edge
                for (int i = 0; i < BAND; i += 2) {
                    float k = 1.0F - i / (float) BAND;
                    int a = (int) (34.0F * (float) Math.pow(k, 1.6D));
                    g.fill(x - 8 + i, y - 2, x - 6 + i, y + this.height - 2, alpha(AMBER_500, a));
                }
                g.fill(x - 8, y - 2, x - 6, y + this.height - 2, AMBER_500);
            }
            icon(g, this.column, this.active ? (lit ? 1 : 0) : 2, x + 1, y + (lit ? 0 : 2) - 1);
            Font font = TerrassicMenuScreen.this.font;
            int color = rgb(!this.active ? STONE_400 : lit ? AMBER_300 : STONE_200);
            if (lit) {
                g.drawString(font, this.getMessage(), x + 24, y + 1, color, true);
                g.drawString(font, this.hint, x + 24, y + 12, rgb(STONE_300), false);
            } else {
                g.drawString(font, this.getMessage(), x + 24, y + 5, color, true);
            }
        }

        @Override
        protected void updateWidgetNarration(NarrationElementOutput output) {
            this.defaultButtonNarrationText(output);
        }
    }

    /** A 16x16 icon button (language, accessibility) with a tooltip. */
    private static class IconButton extends AbstractButton {
        private final int column;
        private final Runnable action;

        IconButton(int x, int y, int column, Component label, Runnable action) {
            super(x, y, 16, 16, label);
            this.column = column;
            this.action = action;
            this.setTooltip(Tooltip.create(label));
        }

        @Override
        public void onPress() {
            this.action.run();
        }

        @Override
        protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
            icon(g, this.column, this.isHoveredOrFocused() ? 1 : 2, this.getX(), this.getY());
        }

        @Override
        protected void updateWidgetNarration(NarrationElementOutput output) {
            this.defaultButtonNarrationText(output);
        }
    }
}
