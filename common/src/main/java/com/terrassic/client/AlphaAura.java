package com.terrassic.client;

import com.terrassic.entity.Alphas;
import com.terrassic.entity.DinosaurEntity;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.core.particles.DustColorTransitionOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import org.joml.Vector3f;

/**
 * The alpha's aura (docs/ALFAS.md, Rodrigo 01/11/2026: "seria legal eles ter uma aura"): motes in the colours of its
 * own coat rise off its back and flanks and fade, the white T. rex shedding pale ash, the red one embers, with a few
 * sparks that glow in the dark (end rod for a pale coat, flame for a red one). Twice as dense while it fights,
 * gone while it lies knocked out (beaten). Vanilla particles: they show within the particle range (~32 blocks) and
 * never through walls. Not for its own rider. Client option "alpha_aura" (config/terrassic-client.json) turns it off.
 *
 * Test of 01/11 (round 2): spread over the hitbox, most motes were born inside the model and hidden, and plain dust
 * goes dark at night. So they start on the outside of the body (over the back and just off the flanks, along its
 * length) and the glowing sparks carry the aura at night. Round 3: smaller motes (big ones looked like dead leaves),
 * up to the neck, none under the tail, more sparks; about 5-9% FPS with 6 angry alphas at 200+ FPS.
 */
public final class AlphaAura {
    private AlphaAura() {
    }

    static void init() {
        ClientTickEvent.CLIENT_POST.register(AlphaAura::tick);
    }

    private static void tick(Minecraft mc) {
        Entity camera = mc.getCameraEntity();
        if (mc.level == null || camera == null || mc.isPaused() || !ClientConfig.flag("alpha_aura")) {
            return;
        }
        RandomSource random = mc.level.getRandom();
        for (DinosaurEntity d : mc.level.getEntitiesOfClass(DinosaurEntity.class, camera.getBoundingBox().inflate(34.0D),
                e -> e.isAlpha() && !e.isBaby() && e.isAlive() && !e.isInvisible() && !e.isKnockedOut())) {
            if (camera.getVehicle() == d) {
                continue;
            }
            boolean fighting = d.isAggressive();
            int[] colors = Alphas.auraColors(d.speciesId(), d.isFemale());
            Vector3f from = rgb(colors[0]);
            Vector3f to = rgb(colors[1]);
            // the body runs along its facing, about three hitbox widths from tail to snout; girth about the width
            float yaw = d.yBodyRot * Mth.DEG_TO_RAD;
            double fx = -Mth.sin(yaw);
            double fz = Mth.cos(yaw);
            double w = d.getBbWidth();
            double h = d.getBbHeight();
            int motes = fighting ? 8 : 4;
            for (int i = 0; i < motes; i++) {
                double along = (random.nextDouble() * 3.2D - 1.6D) * w;        // tail (behind) to the neck
                double y;
                double side;
                if (random.nextInt(3) == 0) {                                   // off a flank, not under the tail
                    along = (random.nextDouble() * 1.6D - 0.8D) * w;
                    side = (random.nextBoolean() ? 1.0D : -1.0D) * (w * 0.55D + 0.25D);
                    y = h * (0.35D + random.nextDouble() * 0.4D);
                } else {                                                        // over the back
                    side = (random.nextDouble() - 0.5D) * w * 0.8D;
                    y = h * (0.78D + random.nextDouble() * 0.2D) + 0.2D;
                }
                double x = d.getX() + fx * along - fz * side;
                double z = d.getZ() + fz * along + fx * side;
                float scale = 0.9F + random.nextFloat() * 0.7F;   // bigger ones read as dead leaves up close
                mc.level.addParticle(new DustColorTransitionOptions(from, to, scale), x, d.getY() + y, z,
                        (random.nextDouble() - 0.5D) * 0.04D, 0.04D + random.nextDouble() * 0.05D,
                        (random.nextDouble() - 0.5D) * 0.04D);
            }
            // the glow that carries it at night (dust darkens with the world); a red coat burns: a crown of flames
            boolean warm = Alphas.auraGlowsWarm(colors[0]);
            int sparks = warm ? (fighting ? 2 : 1) : (fighting || random.nextBoolean() ? 1 : 0);
            for (int i = 0; i < sparks; i++) {
                double along = (random.nextDouble() * 2.6D - 1.6D) * w;         // short of the snout: no candle on it
                double side = (random.nextDouble() - 0.5D) * w * 1.2D;
                ParticleOptions spark = warm ? ParticleTypes.FLAME : ParticleTypes.END_ROD;
                mc.level.addParticle(spark, d.getX() + fx * along - fz * side, d.getY() + h * (0.8D + random.nextDouble() * 0.25D),
                        d.getZ() + fz * along + fx * side, 0.0D, 0.02D + random.nextDouble() * 0.03D, 0.0D);
            }
        }
    }

    private static Vector3f rgb(int c) {
        return new Vector3f((c >> 16 & 255) / 255.0F, (c >> 8 & 255) / 255.0F, (c & 255) / 255.0F);
    }
}
