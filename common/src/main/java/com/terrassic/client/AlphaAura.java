package com.terrassic.client;

import com.terrassic.entity.Alphas;
import com.terrassic.entity.DinosaurEntity;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;

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
 *
 * v1.6 (Rodrigo 02/11/2026: "usar as particulas do mine nao ficou tao bom, o bicho tem que ter aura"): the mod's own
 * glowing sprites ({@link AlphaMoteParticle}) in four layers, all at full brightness: a faint haze of heat over the
 * back, small motes off the back and flanks, twinkling glints and flakes of ash or ember, and, while it fights, a ring
 * pulsing out of its chest every 1.5 s like a heartbeat. Fewer layers on the "decreased" and "minimal" particle settings.
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
        ParticleStatus status = mc.options.particles().get();
        RandomSource random = mc.level.getRandom();
        for (DinosaurEntity d : mc.level.getEntitiesOfClass(DinosaurEntity.class, camera.getBoundingBox().inflate(34.0D),
                e -> e.isAlpha() && !e.isBaby() && e.isAlive() && !e.isInvisible() && !e.isKnockedOut())) {
            if (camera.getVehicle() == d) {
                continue;
            }
            Body b = new Body(d);
            boolean fighting = d.isAggressive();
            int[] colors = Alphas.auraColors(d.speciesId(), d.isFemale());
            int bright = colors[0];
            int dark = colors[1];
            boolean warm = Alphas.auraGlowsWarm(bright);
            float big = (float) Math.min(2.0D, 0.6D + b.w * 0.25D);   // a bigger animal, bigger specks
            // 1. haze: wide faint blots of heat over the back, rising slowly (the "presence")
            int haze = status == ParticleStatus.MINIMAL ? 0 : fighting ? 3 : 1 + random.nextInt(2);
            for (int i = 0; i < haze; i++) {
                double[] at = b.overBack(random, 0.9D);
                AlphaMoteParticle.spawn(mc.level, at[0], at[1], at[2], 0.0D, 0.012D + random.nextDouble() * 0.02D, 0.0D,
                        AlphaMoteParticle.HAZE, bright, dark, (0.7F + random.nextFloat() * 0.5F) * big,
                        30 + random.nextInt(16), fighting ? 0.75F : 0.6F);
            }
            // 2. motes: small round glows off the back and the flanks
            int motes = fighting ? 4 : 2;
            if (status == ParticleStatus.MINIMAL) {
                motes = 1;
            }
            for (int i = 0; i < motes; i++) {
                double[] at = random.nextInt(3) == 0 ? b.offFlank(random) : b.overBack(random, 1.0D);
                AlphaMoteParticle.spawn(mc.level, at[0], at[1], at[2], (random.nextDouble() - 0.5D) * 0.03D,
                        0.03D + random.nextDouble() * 0.04D, (random.nextDouble() - 0.5D) * 0.03D,
                        AlphaMoteParticle.MOTE, bright, dark, (0.2F + random.nextFloat() * 0.15F) * big,
                        25 + random.nextInt(16), 1.0F);
            }
            // 3. glints that twinkle (pale light on the ivory male, sparks on the ember female) and flakes of ash or ember
            int glints = fighting ? 1 + random.nextInt(2) : (random.nextBoolean() ? 1 : 0);
            for (int i = 0; i < glints; i++) {
                double[] at = b.overBack(random, 0.82D);
                AlphaMoteParticle.spawn(mc.level, at[0], at[1], at[2], 0.0D, 0.04D + random.nextDouble() * 0.03D, 0.0D,
                        AlphaMoteParticle.GLINT, warm ? 0xFFE2A0 : 0xFFFFFF, bright, (0.25F + random.nextFloat() * 0.13F) * big,
                        18 + random.nextInt(12), 1.0F);
            }
            if (status == ParticleStatus.ALL && (fighting || random.nextBoolean())) {
                double[] at = b.overBack(random, 1.0D);
                AlphaMoteParticle.spawn(mc.level, at[0], at[1], at[2], (random.nextDouble() - 0.5D) * 0.05D,
                        0.05D + random.nextDouble() * 0.03D, (random.nextDouble() - 0.5D) * 0.05D,
                        AlphaMoteParticle.FLAKE, bright, dark, 0.18F * big, 35 + random.nextInt(16), 1.0F);
            }
            // 4. while it fights, a pulse like a heartbeat: a ring of motes rolling out from its chest every 1.5 s
            if (fighting && status != ParticleStatus.MINIMAL && d.tickCount % 30 == 0) {
                int n = 18;
                double ry = d.getY() + b.h * 0.5D;
                for (int i = 0; i < n; i++) {
                    double ang = Mth.TWO_PI * i / n;
                    double cx = Math.cos(ang);
                    double cz = Math.sin(ang);
                    AlphaMoteParticle.spawn(mc.level, d.getX() + cx * b.w * 0.6D, ry, d.getZ() + cz * b.w * 0.6D,
                            cx * 0.16D, 0.01D, cz * 0.16D, AlphaMoteParticle.MOTE, bright, dark, 0.3F * big, 14, 1.0F);
                }
            }
        }
    }

    /** Where on the body a speck is born: along its facing, about three hitbox widths from tail to neck. */
    private static final class Body {
        final DinosaurEntity d;
        final double fx;
        final double fz;
        final double w;
        final double h;

        Body(DinosaurEntity d) {
            this.d = d;
            float yaw = d.yBodyRot * Mth.DEG_TO_RAD;
            this.fx = -Mth.sin(yaw);
            this.fz = Mth.cos(yaw);
            this.w = d.getBbWidth();
            this.h = d.getBbHeight();
        }

        private double[] at(double along, double side, double y) {
            return new double[]{this.d.getX() + this.fx * along - this.fz * side, this.d.getY() + y,
                    this.d.getZ() + this.fz * along + this.fx * side};
        }

        /** Over the back, from the tail to the neck (spread 1 = the whole length, less = short of the ends). */
        double[] overBack(RandomSource random, double spread) {
            double along = (random.nextDouble() * 3.2D - 1.6D) * this.w * spread;
            double side = (random.nextDouble() - 0.5D) * this.w * 0.8D;
            return this.at(along, side, this.h * (0.78D + random.nextDouble() * 0.2D) + 0.2D);
        }

        /** Just off a flank, never under the tail. */
        double[] offFlank(RandomSource random) {
            double along = (random.nextDouble() * 1.6D - 0.8D) * this.w;
            double side = (random.nextBoolean() ? 1.0D : -1.0D) * (this.w * 0.55D + 0.25D);
            return this.at(along, side, this.h * (0.35D + random.nextDouble() * 0.4D));
        }
    }

}
