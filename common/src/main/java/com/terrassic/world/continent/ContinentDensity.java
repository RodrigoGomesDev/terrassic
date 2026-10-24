package com.terrassic.world.continent;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.util.KeyDispatchDataCodec;
import net.minecraft.util.Mth;
import net.minecraft.world.level.levelgen.DensityFunction;

import java.util.Objects;

/**
 * The continentalness of the Terrassic continent (docs/MUNDO.md, section 10). It takes the vanilla continentalness
 * ({@code argument}, {@code minecraft:overworld/continents}) and bends it into ONE continent of radius {@code raio}
 * blocks around 0,0, shaped like a "C" (Pangaea): a wide inner sea (the Mar Interior) enters from one coast toward the
 * middle, a ring of islets sits offshore and everything else is deep ocean.
 *
 * <p>Vanilla terrain height, ocean depth and the biome choice all read continentalness, so changing only this value
 * turns the whole overworld into the island; {@link ContinentRouter} puts it in place of the vanilla continentalness
 * everywhere in the noise router. The direction of the inner sea and the coastline detail come from the world seed
 * (sampled once from the seeded vanilla noise), so every world gets a different continent. Registered as the density
 * function type {@code terrassic:continente}, so a data pack can use it too.
 *
 * <p>The math is mirrored in tools/worldgen/ilha_preview.py, which draws a map of it.
 */
public final class ContinentDensity implements DensityFunction {
    public static final int DEFAULT_RADIUS = 1200;

    private static final Codec<ContinentDensity> DATA_CODEC = RecordCodecBuilder.create(i -> i.group(
            DensityFunction.HOLDER_HELPER_CODEC.fieldOf("argument").forGetter(ContinentDensity::input),
            Codec.intRange(64, 30000).optionalFieldOf("raio", DEFAULT_RADIUS).forGetter(ContinentDensity::radius)
    ).apply(i, ContinentDensity::new));
    public static final KeyDispatchDataCodec<ContinentDensity> CODEC = KeyDispatchDataCodec.of(DATA_CODEC);

    private final DensityFunction input;
    private final int radius;
    /** Seed-derived shape, shared by every copy made by mapAll (worldgen threads, chunk caches, biome sampler). */
    private final Shape shape;

    public ContinentDensity(DensityFunction input, int radius) {
        this(input, radius, new Shape());
    }

    private ContinentDensity(DensityFunction input, int radius, Shape shape) {
        this.input = input;
        this.radius = radius;
        this.shape = shape;
    }

    public DensityFunction input() {
        return input;
    }

    public int radius() {
        return radius;
    }

    @Override
    public double compute(FunctionContext ctx) {
        double vanilla = input.compute(ctx);
        if (!shape.ready) {
            shape.init(input);
        }
        return shape.continentalness(ctx.blockX(), ctx.blockZ(), vanilla, radius);
    }

    @Override
    public void fillArray(double[] array, ContextProvider provider) {
        provider.fillAllDirectly(array, this);
    }

    @Override
    public DensityFunction mapAll(Visitor visitor) {
        return visitor.apply(new ContinentDensity(input.mapAll(visitor), radius, shape));
    }

    @Override
    public double minValue() {
        return -1.0D;
    }

    @Override
    public double maxValue() {
        return 1.0D;
    }

    @Override
    public KeyDispatchDataCodec<? extends DensityFunction> codec() {
        return CODEC;
    }

    // equality ignores the lazily filled shape, so the worldgen caches that key on density functions still match
    @Override
    public boolean equals(Object o) {
        return o instanceof ContinentDensity c && c.radius == radius && c.input.equals(input);
    }

    @Override
    public int hashCode() {
        return Objects.hash(input, radius);
    }

    /** The continent outline. Pure math on block coordinates; the only per-world input is the salt. */
    static final class Shape {
        volatile boolean ready;
        private long salt;
        private double cos = 1.0D;
        private double sin;

        /** Reads the seed out of the (seeded) vanilla noise: two samples far apart are different in every world. */
        synchronized void init(DensityFunction seeded) {
            if (ready) {
                return;
            }
            double a = seeded.compute(new SinglePointContext(0, 0, 0));
            double b = seeded.compute(new SinglePointContext(4099, 0, -6151));
            double c = seeded.compute(new SinglePointContext(-7919, 0, 3011));
            long s = Double.doubleToLongBits(a) * 0x9E3779B97F4A7C15L
                    ^ Double.doubleToLongBits(b) * 0xC2B2AE3D27D4EB4FL
                    ^ Double.doubleToLongBits(c);
            setSalt(s);
        }

        void setSalt(long s) {
            salt = mix(s);
            double angle = (salt >>> 11) * 0x1.0p-53 * Math.PI * 2.0D;
            cos = Math.cos(angle);
            sin = Math.sin(angle);
            ready = true;
        }

        double continentalness(int x, int z, double vanilla, int radius) {
            double u = (x * cos + z * sin) / radius;   // axis of the inner sea (it opens toward +u)
            double w = (-x * sin + z * cos) / radius;  // long axis of the continent
            double n1 = fbm(x, z, radius * 0.8D, 1L);
            double n2 = fbm(x, z, radius * 0.22D, 2L);
            double d = Math.sqrt(u * u + (w / 1.35D) * (w / 1.35D));
            double e = d + 0.22D * n1 + 0.07D * n2 - 0.06D * vanilla;

            double land = Mth.clamp(Mth.lerp(smooth(0.0D, 0.85D, e), 0.60D, -0.06D) + 0.20D * vanilla, -0.10D, 1.0D);
            double ocean = Mth.lerp(smooth(0.95D, 1.30D, e), -0.25D, -0.95D);
            double c = Mth.lerp(smooth(0.80D, 0.97D, e), land, ocean);

            // Mar Interior: a wide gulf from the coast to near the middle, gently curved
            double along = Mth.clamp(u - 0.30D, 0.0D, 1.0D);
            double halfWidth = 0.12D + 0.30D * along + 0.05D * n2;
            double off = w - 0.18D * Math.sin(Math.PI * along);
            double dist = u < 0.30D ? Math.sqrt((u - 0.30D) * (u - 0.30D) + w * w) : Math.abs(off);
            double gulf = 1.0D - smooth(halfWidth * 0.6D, halfWidth, dist);
            c = Math.min(c, Mth.lerp(gulf, c, -0.38D));

            // islets in a ring of shallow sea around the continent
            double ring = smooth(1.05D, 1.18D, e) * (1.0D - smooth(1.50D, 1.70D, e));
            double islet = smooth(0.50D, 0.64D, n2) * ring;
            if (islet > 0.0D) {
                c = Mth.lerp(islet, c, Math.max(c, -0.02D));
            }
            return c;
        }

        /** 3 octaves of value noise, roughly in [-1, 1]; {@code wavelength} in blocks. */
        private double fbm(int x, int z, double wavelength, long channel) {
            double sum = 0.0D;
            double amp = 1.0D;
            double total = 0.0D;
            double f = 1.0D / wavelength;
            for (int o = 0; o < 3; o++) {
                sum += amp * valueNoise(x * f, z * f, channel * 31L + o);
                total += amp;
                amp *= 0.5D;
                f *= 2.0D;
            }
            return sum / total;
        }

        private double valueNoise(double x, double z, long channel) {
            int x0 = Mth.floor(x);
            int z0 = Mth.floor(z);
            double fx = x - x0;
            double fz = z - z0;
            fx = fx * fx * (3.0D - 2.0D * fx);
            fz = fz * fz * (3.0D - 2.0D * fz);
            double a = lattice(x0, z0, channel);
            double b = lattice(x0 + 1, z0, channel);
            double c = lattice(x0, z0 + 1, channel);
            double d = lattice(x0 + 1, z0 + 1, channel);
            return Mth.lerp(fz, Mth.lerp(fx, a, b), Mth.lerp(fx, c, d));
        }

        private double lattice(int x, int z, long channel) {
            long h = mix(salt ^ (x * 0x632BE59BD9B4E019L) ^ (z * 0x8CB92BA72F3D8DD7L) ^ (channel * 0x9E3779B97F4A7C15L));
            return (h >>> 11) * 0x1.0p-52 - 1.0D;
        }

        private static long mix(long z) {
            z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
            z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;
            return z ^ (z >>> 31);
        }

        private static double smooth(double edge0, double edge1, double x) {
            double t = Mth.clamp((x - edge0) / (edge1 - edge0), 0.0D, 1.0D);
            return t * t * (3.0D - 2.0D * t);
        }
    }
}
