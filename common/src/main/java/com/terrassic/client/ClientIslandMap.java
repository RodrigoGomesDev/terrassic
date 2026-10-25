package com.terrassic.client;

import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.math.Axis;
import com.terrassic.Terrassic;
import com.terrassic.world.continent.IslandMap;
import dev.architectury.event.events.client.ClientPlayerEvent;
import dev.architectury.networking.NetworkManager;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;

import static com.terrassic.client.ui.TerrassicPalette.*;

/**
 * The map of the island on the client (docs/MUNDO.md, section 11): receives the survey of the continent
 * (world/continent/IslandMap) and draws it as an old ink map on the notebook paper. Sea in a light wash with
 * ripple lines along the coast, the coastline in ink, land shaded by its relief (light from the north-west) with a
 * small mark per biome (trees, tufts of the swamps, dots of the dry lands), rivers in soft ink. The player is a red
 * arrow; north is up.
 */
public final class ClientIslandMap {
    /** Pixels of the drawn map (2 per surveyed cell). */
    private static final int PX = IslandMap.SIZE * 2;
    /** Under the map, the same texture holds one legend swatch per biome category, SWATCH x LEGEND_H pixels each. */
    private static final int SWATCH = 24;
    private static final int LEGEND_H = 16;
    private static final int TEX_H = PX + LEGEND_H;
    private static final ResourceLocation TEXTURE = Terrassic.id("island_map");

    private static int size;
    private static int extent;
    private static int seaLevel;
    private static byte[] heights;
    private static byte[] kinds;
    private static DynamicTexture texture;

    private ClientIslandMap() {
    }

    /** Called from TerrassicClient. */
    public static void register() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, IslandMap.SYNC, (buf, context) -> {
            int n = buf.readVarInt();
            int e = buf.readVarInt();
            int sea = buf.readVarInt();
            byte[] h = buf.readByteArray();
            byte[] k = buf.readByteArray();
            context.queue(() -> {
                if (h.length == n * n && k.length == n * n) {
                    size = n;
                    extent = e;
                    seaLevel = sea;
                    heights = h;
                    kinds = k;
                    release();
                }
            });
        });
        ClientPlayerEvent.CLIENT_PLAYER_QUIT.register(player -> {
            heights = null;
            kinds = null;
            release();
        });
    }

    /** True once this world's map has arrived (only continent worlds have one). */
    public static boolean available() {
        return heights != null;
    }

    /** Half the side of the mapped square, in blocks (the map covers -extent..+extent on X and Z). */
    public static int extent() {
        return extent;
    }

    /**
     * Draws the map in the square box (x, y, side) with the player's arrow, a north mark and a scale bar; or a note
     * when this world has no map yet.
     */
    public static void render(GuiGraphics g, Font font, int x, int y, int side) {
        if (!available()) {
            Component note = Component.translatable("map.terrassic.none");
            for (var line : font.split(note, side - 8)) {
                g.drawString(font, line, x + 4, y + side / 2 - 4, INK_SOFT, false);
                y += 10;
            }
            return;
        }
        upload();
        g.blit(TEXTURE, x, y, side, side, 0.0F, 0.0F, PX, PX, PX, TEX_H);
        g.renderOutline(x, y, side, side, INK);

        // north
        g.drawCenteredString(font, "N", x + side - 8, y + 4, rgb(INK));
        g.fill(x + side - 9, y + 13, x + side - 7, y + 19, INK);

        // scale bar: 500 m (1 block = 1 m)
        int bar = Math.round(500.0F * side / (2.0F * extent));
        if (bar >= 12 && bar < side - 20) {
            int bx = x + 6;
            int by = y + side - 8;
            g.fill(bx, by, bx + bar, by + 1, INK);
            g.fill(bx, by - 2, bx + 1, by + 1, INK);
            g.fill(bx + bar - 1, by - 2, bx + bar, by + 1, INK);
            g.drawString(font, "500 m", bx + bar + 3, by - 4, INK_SOFT, false);
        }

        // the player
        Player player = Minecraft.getInstance().player;
        if (player != null) {
            float px = x + (float) ((player.getX() + extent) / (2.0D * extent)) * side;
            float pz = y + (float) ((player.getZ() + extent) / (2.0D * extent)) * side;
            px = Mth.clamp(px, x + 3, x + side - 3);
            pz = Mth.clamp(pz, y + 3, y + side - 3);
            g.pose().pushPose();
            g.pose().translate(px, pz, 0.0F);
            g.pose().mulPose(Axis.ZP.rotationDegrees(player.getYRot() + 180.0F));
            // arrow pointing up before the turn (yaw 180 = north): ink outline, red fill
            g.fill(-2, -4, 3, 4, INK);
            g.fill(-1, -3, 2, 3, BLOOD_500);
            g.fill(0, -5, 1, -3, INK);
            g.pose().popPose();
        }
    }

    /** Draws the legend swatch of a biome category (IslandMap.DEEP_SEA ... DRY) in the box (x, y, w, h). */
    public static void swatch(GuiGraphics g, int kind, int x, int y, int w, int h) {
        if (!available()) {
            return;
        }
        upload();
        g.blit(TEXTURE, x, y, w, h, (float) (kind * SWATCH), (float) PX, SWATCH, LEGEND_H, PX, TEX_H);
        g.renderOutline(x, y, w, h, INK_SOFT);
    }

    private static void upload() {
        if (texture == null) {
            texture = new DynamicTexture(draw());
            Minecraft.getInstance().getTextureManager().register(TEXTURE, texture);
        }
    }

    private static void release() {
        if (texture != null) {
            Minecraft.getInstance().getTextureManager().release(TEXTURE);
            texture = null;
        }
    }

    // ------------------------------------------------------------------ drawing the map image

    private static int kind(int i, int j) {
        return kinds[Mth.clamp(j, 0, size - 1) * size + Mth.clamp(i, 0, size - 1)];
    }

    private static float height(float u, float v) {
        float fu = Mth.clamp(u, 0.0F, size - 1.001F);
        float fv = Mth.clamp(v, 0.0F, size - 1.001F);
        int i = (int) fu;
        int j = (int) fv;
        float a = fu - i;
        float b = fv - j;
        return Mth.lerp(b, Mth.lerp(a, h(i, j), h(i + 1, j)), Mth.lerp(a, h(i, j + 1), h(i + 1, j + 1)));
    }

    private static float h(int i, int j) {
        return heights[Mth.clamp(j, 0, size - 1) * size + Mth.clamp(i, 0, size - 1)] & 0xFF;
    }

    private static boolean water(int k) {
        return k == IslandMap.DEEP_SEA || k == IslandMap.SEA;
    }

    private static NativeImage draw() {
        int scale = PX / size;
        boolean[] wet = new boolean[PX * PX];
        for (int py = 0; py < PX; py++) {
            for (int px = 0; px < PX; px++) {
                float u = (px + 0.5F) / scale - 0.5F;
                float v = (py + 0.5F) / scale - 0.5F;
                wet[py * PX + px] = height(u, v) < seaLevel - 0.5F && water(kind(Math.round(u), Math.round(v)));
            }
        }
        int[] dist = coastDistance(wet);
        NativeImage img = new NativeImage(PX, TEX_H, false);
        for (int py = 0; py < PX; py++) {
            for (int px = 0; px < PX; px++) {
                float u = (px + 0.5F) / scale - 0.5F;
                float v = (py + 0.5F) / scale - 0.5F;
                int k = kind(Math.round(u), Math.round(v));
                int color;
                if (wet[py * PX + px]) {
                    int d = dist[py * PX + px];
                    color = mix(PAPER, PAPER_DARK, k == IslandMap.DEEP_SEA ? 0.9F : 0.6F);
                    if (d == 3 || d == 7 || d == 12) {
                        color = mix(color, INK_SOFT, d == 3 ? 0.55F : d == 7 ? 0.35F : 0.2F); // ripples along the coast
                    }
                } else if (dist[py * PX + px] == 1) {
                    color = INK; // coastline
                } else {
                    // relief: light from the north-west
                    float dx = height(u + 0.5F, v) - height(u - 0.5F, v);
                    float dz = height(u, v + 0.5F) - height(u, v - 0.5F);
                    float shade = Mth.clamp(0.5F + (dx + dz) * 0.06F, 0.0F, 1.0F);
                    color = mix(PAPER, INK_SOFT, shade * 0.7F);
                    color = mark(color, k, px, py);
                }
                img.setPixelRGBA(px, py, abgr(color));
            }
        }
        // the legend swatches, drawn the same way as the map
        for (int k = IslandMap.DEEP_SEA; k <= IslandMap.DRY; k++) {
            for (int py = 0; py < LEGEND_H; py++) {
                for (int px = 0; px < SWATCH; px++) {
                    int color;
                    if (water(k)) {
                        color = mix(PAPER, PAPER_DARK, k == IslandMap.DEEP_SEA ? 0.9F : 0.6F);
                        if (k == IslandMap.SEA && py == LEGEND_H / 2) {
                            color = mix(color, INK_SOFT, 0.55F);
                        }
                    } else {
                        color = mark(mix(PAPER, INK_SOFT, 0.35F), k, px, py);
                    }
                    img.setPixelRGBA(k * SWATCH + px, PX + py, abgr(color));
                }
            }
        }
        return img;
    }

    /** A small repeating mark per biome, so the map reads without a legend. */
    private static int mark(int color, int k, int px, int py) {
        int cx = Math.floorMod(px + (py / 6 % 2) * 3, 6);
        int cy = Math.floorMod(py, 6);
        return switch (k) {
            case IslandMap.FOREST -> (cx == 2 && cy <= 2) || (cy == 1 && cx >= 1 && cx <= 3) ? mix(color, INK, 0.6F) : color;
            case IslandMap.SWAMP -> cy == 3 && cx <= 2 ? mix(color, INK_SOFT, 0.7F) : color;
            case IslandMap.DRY -> cx == 1 && cy == 1 && Math.floorMod(px * 7 + py * 13, 3) == 0 ? mix(color, INK_SOFT, 0.7F) : color;
            case IslandMap.RIVER -> mix(color, INK_SOFT, 0.5F);
            case IslandMap.BEACH -> mix(color, PAPER, 0.5F);
            case IslandMap.HIGHLANDS -> cy == 2 && cx == 3 ? mix(color, INK, 0.5F) : color;
            default -> color;
        };
    }

    /**
     * Distance in pixels (chamfer 3-4, so the ripples come out round) from each pixel to the nearest pixel of the
     * other kind (land or sea); 1 on the coast itself.
     */
    private static int[] coastDistance(boolean[] wet) {
        int[] d = new int[PX * PX];
        int far = PX * 8;
        for (int py = 0; py < PX; py++) {
            for (int px = 0; px < PX; px++) {
                int i = py * PX + px;
                boolean edge = px > 0 && wet[i - 1] != wet[i] || px < PX - 1 && wet[i + 1] != wet[i]
                        || py > 0 && wet[i - PX] != wet[i] || py < PX - 1 && wet[i + PX] != wet[i];
                d[i] = edge ? 3 : far;
            }
        }
        int[][] back = {{-1, 0, 3}, {0, -1, 3}, {-1, -1, 4}, {1, -1, 4}};
        for (int py = 0; py < PX; py++) {
            for (int px = 0; px < PX; px++) {
                relax(d, wet, px, py, back);
            }
        }
        int[][] fwd = {{1, 0, 3}, {0, 1, 3}, {1, 1, 4}, {-1, 1, 4}};
        for (int py = PX - 1; py >= 0; py--) {
            for (int px = PX - 1; px >= 0; px--) {
                relax(d, wet, px, py, fwd);
            }
        }
        for (int i = 0; i < d.length; i++) {
            d[i] = (d[i] + 1) / 3;
        }
        return d;
    }

    private static void relax(int[] d, boolean[] wet, int px, int py, int[][] steps) {
        int i = py * PX + px;
        for (int[] s : steps) {
            int nx = px + s[0];
            int ny = py + s[1];
            if (nx >= 0 && nx < PX && ny >= 0 && ny < PX && wet[ny * PX + nx] == wet[i]) {
                d[i] = Math.min(d[i], d[ny * PX + nx] + s[2]);
            }
        }
    }

    private static int mix(int a, int b, float t) {
        int r = (int) Mth.lerp(t, a >> 16 & 0xFF, b >> 16 & 0xFF);
        int gr = (int) Mth.lerp(t, a >> 8 & 0xFF, b >> 8 & 0xFF);
        int bl = (int) Mth.lerp(t, a & 0xFF, b & 0xFF);
        return 0xFF000000 | r << 16 | gr << 8 | bl;
    }

    /** ARGB to the ABGR order of NativeImage. */
    private static int abgr(int argb) {
        return argb & 0xFF00FF00 | (argb & 0xFF) << 16 | argb >> 16 & 0xFF;
    }
}
