package com.terrassic.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.terrassic.leap.LeapNetwork;
import com.terrassic.leap.LeapRegistry;
import com.terrassic.research.Objective;
import dev.architectury.event.events.client.ClientGuiEvent;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import dev.architectury.registry.client.level.entity.EntityRendererRegistry;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * Client side of v0.9 "The End" (docs/SALTO.md):
 * <ul>
 *   <li><b>Shooting stars</b> (Katarina's "estrelas que caem cada vez mais"): streaks across the night sky, more of
 *       them with each amber fragment you hold (0.6 a minute with none, about 7 with four). Drawn by LevelRendererMixin
 *       after the vanilla stars.</li>
 *   <li><b>The ritual sky</b>: within 192 blocks of an altar during the ritual the sky and fog turn the red of a
 *       burning sky and the shooting stars become a shower, day or night.</li>
 *   <li><b>The flash of the leap</b>: the screen goes white-gold for a few seconds.</li>
 *   <li>Renderers of the Rift Tyrant (the rex model with the Rift layer) and of the meteors.</li>
 * </ul>
 * config/terrassic-client.json: "shooting_stars" and "ritual_sky" can be turned off.
 */
public final class LeapClient {
    private static final Vec3 RITUAL_SKY = new Vec3(0.62D, 0.2D, 0.1D);
    private static final Vec3 RITUAL_FOG = new Vec3(0.5D, 0.18D, 0.1D);
    private static final int FLASH_IN = 12;
    private static final int FLASH_HOLD = 40;
    private static final int FLASH_OUT = 50;
    private static final RandomSource RANDOM = RandomSource.create();
    private static final List<Streak> STREAKS = new ArrayList<>();

    private static BlockPos ritualAltar;
    private static int ritualSeen = -1000;
    private static float ritual;
    private static float ritualPrevious;
    private static int ticks;
    private static int flash = -1;
    private static boolean flashUnstable;

    /** A shooting star: from {@code start} along {@code dir} (unit vectors on the sky sphere), over {@code life} ticks. */
    private record Streak(Vector3f start, Vector3f dir, int born, int life, float length, float width) {
    }

    private LeapClient() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, LeapNetwork.RITUAL, (buf, context) -> {
            BlockPos pos = buf.readBlockPos();
            boolean on = buf.readBoolean();
            context.queue(() -> {
                if (on) {
                    ritualAltar = pos;
                    ritualSeen = ticks;
                } else if (pos.equals(ritualAltar)) {
                    ritualAltar = null;
                }
            });
        });
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, LeapNetwork.FLASH, (buf, context) -> {
            boolean unstable = buf.readBoolean();
            context.queue(() -> startFlash(unstable));
        });
        ClientTickEvent.CLIENT_POST.register(LeapClient::tick);
        ClientGuiEvent.RENDER_HUD.register(LeapClient::renderFlash);
        EntityRendererRegistry.register(LeapRegistry.RIFT_TYRANT, ctx -> new DinosaurRenderer<>(ctx, "tyrannosaurus",
                com.terrassic.entity.Tyrannosaurus.MODEL_SCALE, com.terrassic.entity.Tyrannosaurus.SHADOW * 1.35F));
        EntityRendererRegistry.register(LeapRegistry.METEOR, MeteorRenderer::new);
    }

    // ------------------------------------------------------------------ ritual sky

    /** 0..1: how much of the ritual sky is over the player (fades with distance from the altar). */
    public static float ritual(float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.level.dimension() != Level.OVERWORLD || !ClientConfig.flag("ritual_sky")) {
            return 0.0F;
        }
        return Mth.lerp(partialTick, ritualPrevious, ritual);
    }

    public static Vec3 tintSky(Vec3 colour, float partialTick) {
        float k = ritual(partialTick) * 0.85F;
        return k <= 0.0F ? colour : colour.lerp(RITUAL_SKY, k);
    }

    public static Vec3 tintFog(Vec3 colour, float partialTick) {
        float k = ritual(partialTick) * 0.7F;
        return k <= 0.0F ? colour : colour.lerp(RITUAL_FOG, k);
    }

    private static void tick(Minecraft mc) {
        ritualPrevious = ritual;
        if (mc.level == null || mc.player == null) {
            ritualAltar = null;
            ritual = 0.0F;
            STREAKS.clear();
            flash = -1;
            return;
        }
        if (mc.isPaused()) {
            return;
        }
        ticks++;
        if (flash >= 0 && ++flash > FLASH_IN + FLASH_HOLD + FLASH_OUT) {
            flash = -1;
        }
        // no word from the server for 5 s: the ritual is over (or we walked away)
        if (ritualAltar != null && ticks - ritualSeen > 100) {
            ritualAltar = null;
        }
        float target = 0.0F;
        if (ritualAltar != null) {
            double d = Math.sqrt(mc.player.blockPosition().distSqr(ritualAltar));
            target = (float) Mth.clamp(1.0D - (d - 64.0D) / (LeapNetwork.RANGE - 64.0D), 0.0D, 1.0D);
        }
        ritual += (target - ritual) * 0.02F;
        if (Math.abs(target - ritual) < 0.002F) {
            ritual = target;
        }
        spawnStreaks(mc.level);
    }

    // ------------------------------------------------------------------ shooting stars

    /** Shooting stars per minute: more with each fragment, a shower during the ritual. */
    private static float rate() {
        int fragments = Objective.fragments(ClientResearch.get());
        return 0.6F + 1.6F * fragments + 50.0F * ritual;
    }

    private static void spawnStreaks(ClientLevel level) {
        STREAKS.removeIf(s -> ticks - s.born() > s.life());
        if (!ClientConfig.flag("shooting_stars") || level.dimension() != Level.OVERWORLD) {
            return;
        }
        if (RANDOM.nextFloat() >= rate() / 1200.0F || STREAKS.size() > 40) {
            return;
        }
        // start somewhere in the upper sky, run along the sky at a slant, mostly downwards
        float az = RANDOM.nextFloat() * Mth.TWO_PI;
        float el = (25.0F + RANDOM.nextFloat() * 50.0F) * Mth.DEG_TO_RAD;
        Vector3f start = new Vector3f(Mth.cos(el) * Mth.cos(az), Mth.sin(el), Mth.cos(el) * Mth.sin(az));
        Vector3f side = new Vector3f(-Mth.sin(az), 0.0F, Mth.cos(az)).mul(RANDOM.nextBoolean() ? 1.0F : -1.0F);
        Vector3f down = new Vector3f(start).cross(side).normalize();
        if (down.y > 0.0F) {
            down.negate();
        }
        Vector3f dir = side.mul(0.6F).add(down.mul(0.8F)).normalize();
        boolean big = RANDOM.nextInt(ritual > 0.3F ? 3 : 8) == 0;
        STREAKS.add(new Streak(start, dir, ticks, 14 + RANDOM.nextInt(16), big ? 0.34F : 0.2F, big ? 0.9F : 0.5F));
    }

    /** Called by LevelRendererMixin at the end of the sky: draws the streaks (additive, behind the terrain). */
    public static void renderStreaks(PoseStack poseStack, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        ClientLevel level = mc.level;
        if (level == null || STREAKS.isEmpty()) {
            return;
        }
        float night = level.getStarBrightness(partialTick) * (1.0F - level.getRainLevel(partialTick));
        float visible = Math.max(night * 2.0F, ritual(partialTick));
        if (visible <= 0.02F) {
            return;
        }
        RenderSystem.enableBlend();
        RenderSystem.blendFunc(com.mojang.blaze3d.platform.GlStateManager.SourceFactor.SRC_ALPHA,
                com.mojang.blaze3d.platform.GlStateManager.DestFactor.ONE);
        RenderSystem.depthMask(false);
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BufferBuilder b = Tesselator.getInstance().getBuilder();
        b.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        Matrix4f m = poseStack.last().pose();
        float now = ticks + partialTick;
        for (Iterator<Streak> it = STREAKS.iterator(); it.hasNext(); ) {
            Streak s = it.next();
            float t = (now - s.born()) / s.life();
            if (t < 0.0F || t > 1.0F) {
                continue;
            }
            float alpha = Mth.clamp(visible, 0.0F, 1.0F) * Mth.sin(t * Mth.PI);
            // the head runs along the sky, the tail follows 'length' behind it
            Vector3f head = new Vector3f(s.dir()).mul(t * 0.5F).add(s.start()).normalize().mul(100.0F);
            Vector3f tail = new Vector3f(s.dir()).mul(t * 0.5F - s.length()).add(s.start()).normalize().mul(100.0F);
            Vector3f across = new Vector3f(head).sub(tail).cross(head).normalize().mul(s.width());
            b.vertex(m, tail.x, tail.y, tail.z).color(1.0F, 0.75F, 0.45F, 0.0F).endVertex();
            b.vertex(m, head.x - across.x, head.y - across.y, head.z - across.z).color(1.0F, 0.95F, 0.85F, alpha).endVertex();
            b.vertex(m, head.x + across.x, head.y + across.y, head.z + across.z).color(1.0F, 0.95F, 0.85F, alpha).endVertex();
            b.vertex(m, tail.x, tail.y, tail.z).color(1.0F, 0.75F, 0.45F, 0.0F).endVertex();
        }
        BufferUploader.drawWithShader(b.end());
        RenderSystem.depthMask(true);
        RenderSystem.defaultBlendFunc();
        RenderSystem.disableBlend();
    }

    // ------------------------------------------------------------------ the flash of the leap

    private static void startFlash(boolean unstable) {
        flash = 0;
        flashUnstable = unstable;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null) {
            mc.player.playNotifySound(SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1.0F, unstable ? 0.5F : 0.7F);
            mc.player.playNotifySound(SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 0.6F, 0.5F);
        }
    }

    private static void renderFlash(GuiGraphics g, float partialTick) {
        if (flash < 0) {
            return;
        }
        float t = flash + partialTick;
        float a;
        if (t < FLASH_IN) {
            a = t / FLASH_IN;
        } else if (t < FLASH_IN + FLASH_HOLD) {
            a = 1.0F;
        } else {
            a = 1.0F - (t - FLASH_IN - FLASH_HOLD) / FLASH_OUT;
        }
        a = Mth.clamp(a, 0.0F, 1.0F);
        int rgb = flashUnstable ? 0xFFD0A0 : 0xFFF4DC;
        g.fill(0, 0, g.guiWidth(), g.guiHeight(), ((int) (a * 255.0F) << 24) | rgb);
    }
}
