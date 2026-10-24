package com.terrassic.client;

import com.terrassic.world.RiftStorm;
import dev.architectury.event.events.client.ClientTickEvent;
import dev.architectury.networking.NetworkManager;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * Client side of the Rift Storms ({@link RiftStorm}): the amber sky, fog and clouds (applied by ClientLevelMixin and
 * FogRendererMixin), amber motes drifting around the player and distorted sounds now and then. The intensity eases in
 * and out over a few seconds when the server says a storm started or ended.
 */
public final class RiftStormClient {
    private static final Vec3 AMBER_SKY = new Vec3(1.0D, 0.6D, 0.26D);
    private static final Vec3 AMBER_FOG = new Vec3(0.86D, 0.5D, 0.24D);
    private static final DustParticleOptions MOTE = new DustParticleOptions(new Vector3f(1.0F, 0.72F, 0.25F), 1.0F);
    private static final RandomSource RANDOM = RandomSource.create();
    private static boolean active;
    private static float intensity;
    private static float previous;

    private RiftStormClient() {
    }

    public static void init() {
        NetworkManager.registerReceiver(NetworkManager.Side.S2C, RiftStorm.SYNC, (buf, context) -> {
            boolean on = buf.readBoolean();
            context.queue(() -> active = on);
        });
        ClientTickEvent.CLIENT_POST.register(RiftStormClient::tick);
    }

    /** 0 (no storm) .. 1 (full storm), only in the overworld. */
    public static float intensity(float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.level.dimension() != Level.OVERWORLD) {
            return 0.0F;
        }
        return Mth.lerp(partialTick, previous, intensity);
    }

    public static Vec3 tintSky(Vec3 colour, float partialTick) {
        float k = intensity(partialTick) * 0.75F;
        return k <= 0.0F ? colour : colour.lerp(AMBER_SKY, k);
    }

    public static Vec3 tintFog(Vec3 colour, float partialTick) {
        float k = intensity(partialTick) * 0.6F;
        return k <= 0.0F ? colour : colour.lerp(AMBER_FOG, k);
    }

    private static void tick(Minecraft mc) {
        previous = intensity;
        if (mc.level == null) {
            active = false;
            intensity = 0.0F;
            return;
        }
        if (mc.isPaused()) {
            return;
        }
        float target = active ? 1.0F : 0.0F;
        intensity += (target - intensity) * 0.012F;
        if (Math.abs(target - intensity) < 0.002F) {
            intensity = target;
        }
        ClientLevel level = mc.level;
        LocalPlayer player = mc.player;
        if (player == null || intensity <= 0.02F || level.dimension() != Level.OVERWORLD) {
            return;
        }
        int motes = Math.round(intensity * 5.0F);
        for (int i = 0; i < motes; i++) {
            double x = player.getX() + (RANDOM.nextDouble() - 0.5D) * 24.0D;
            double y = player.getY() + RANDOM.nextDouble() * 10.0D - 2.0D;
            double z = player.getZ() + (RANDOM.nextDouble() - 0.5D) * 24.0D;
            level.addParticle(MOTE, x, y, z, 0.0D, 0.02D, 0.0D);
        }
        // time "glitches": a distorted sound every so often
        if (RANDOM.nextFloat() < 0.004F * intensity) {
            SoundEvent sound = switch (RANDOM.nextInt(3)) {
                case 0 -> SoundEvents.AMETHYST_BLOCK_RESONATE;
                case 1 -> SoundEvents.BEACON_AMBIENT;
                default -> SoundEvents.AMBIENT_CAVE.value();
            };
            level.playLocalSound(player.getX(), player.getY(), player.getZ(), sound, SoundSource.AMBIENT,
                    0.6F + intensity * 0.4F, 0.45F + RANDOM.nextFloat() * 0.2F, false);
        }
    }
}
