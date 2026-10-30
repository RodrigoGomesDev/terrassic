package com.terrassic.world;

import com.terrassic.block.DinoEggBlock;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.registry.ModBlocks;
import com.terrassic.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.Random;

/**
 * Pteranodon colonies on the coast (approved by Rodrigo on 30/10/2026: colonies and fishing parties, never inland).
 *
 * <p>Around each player, every twenty seconds, {@value #SAMPLES} random loaded columns 32 to 112 blocks away are
 * looked at for a colony site: the highest natural rock, sand or soil at least {@value #MIN_HEIGHT} blocks over the sea,
 * with open sea (an ocean, beach or inner sea biome, at least four deep) within {@value #SEA_REACH} blocks. A site
 * becomes a colony when no other lies within {@value #SPACING} blocks, which gives about one colony per 600 to 800
 * blocks of coastline. Inland there is never open sea within reach, so never a colony. Saved in {@link ColonyData}.
 *
 * <p>When a player comes within {@value #FILL_RANGE} blocks (but not closer than {@value #UNSEEN}, so nothing pops up
 * in view), the colony is stocked: 4 to 10 adults and 1 to 3 young, persistent and tied to the site
 * ({@link FlyingDinosaur#getColonyHome()}), and on the first stocking a scrape or two of eggs on the rocks. It is
 * restocked at most once a day, and only when fewer than half are left. Colonists roost there (ai/ColonyGoal) and fly
 * out to fish over the sea in small parties by day (ai/FishingFlightGoal); the generic sky flocks of EcoSpawner skip
 * colonial species.
 */
public final class PteroColonies {
    private static final int SAMPLES = 24;
    private static final int MIN_HEIGHT = 5;
    private static final int SEA_REACH = 24;
    private static final double SPACING = 640.0D;
    private static final double FILL_RANGE = 160.0D;
    private static final double UNSEEN = 40.0D;
    private static final long RESTOCK = 24000L;

    private PteroColonies() {
    }

    /** Called by EcoSpawner on each player's sky turn (every twenty seconds per player). */
    static void tick(ServerLevel level, ServerPlayer player) {
        ColonyData data = ColonyData.get(level);
        RandomSource random = level.getRandom();
        BlockPos best = null;
        for (int i = 0; i < SAMPLES; i++) {
            double a = random.nextDouble() * Math.PI * 2.0D;
            double r = 32.0D + random.nextDouble() * 80.0D;
            int x = Mth.floor(player.getX() + Math.cos(a) * r);
            int z = Mth.floor(player.getZ() + Math.sin(a) * r);
            if (!level.hasChunk(x >> 4, z >> 4)) {
                continue;
            }
            BlockPos site = siteAt(level, x, z);
            if (site != null && (best == null || site.getY() > best.getY())) {
                best = site;
            }
        }
        if (best != null && data.nearest(best.getX(), best.getZ(), SPACING) == null) {
            data.add(best);
        }
        for (long packed : data.colonies().keySet().toArray(new Long[0])) {
            BlockPos site = BlockPos.of(packed);
            if (player.distanceToSqr(Vec3.atCenterOf(site)) < FILL_RANGE * FILL_RANGE) {
                fill(level, data, site, player);
            }
        }
    }

    // ------------------------------------------------------------------ finding a site

    /** The standing spot on top of a coastal height at (x, z), or null. */
    private static BlockPos siteAt(ServerLevel level, int x, int z) {
        int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        int sea = level.getSeaLevel();
        if (top - 1 < sea + MIN_HEIGHT) {
            return null;
        }
        BlockPos ground = new BlockPos(x, top - 1, z);
        BlockState below = level.getBlockState(ground);
        if (!below.getFluidState().isEmpty() || below.is(BlockTags.LEAVES) || below.is(BlockTags.LOGS)
                || !below.isFaceSturdy(level, ground, net.minecraft.core.Direction.UP)) {
            return null;
        }
        for (int d = 0; d < 16; d++) {
            double a = d * Math.PI / 8.0D;
            for (int r = 4; r <= SEA_REACH; r += 2) {
                if (openSea(level, x + Mth.floor(Math.cos(a) * r), z + Mth.floor(Math.sin(a) * r), 4)) {
                    return ground.above();
                }
            }
        }
        return null;
    }

    /** Open sea at (x, z): water at sea level, at least {@code depth} deep, in a sea, beach or inner sea biome. */
    static boolean openSea(Level level, int x, int z, int depth) {
        if (!level.hasChunk(x >> 4, z >> 4)) {
            return false;
        }
        int sea = level.getSeaLevel();
        if (level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z) > sea) {
            return false;
        }
        BlockPos water = new BlockPos(x, sea - 1, z);
        if (!level.getFluidState(water).is(net.minecraft.tags.FluidTags.WATER)
                || level.getHeight(Heightmap.Types.OCEAN_FLOOR, x, z) > sea - depth) {
            return false;
        }
        Holder<Biome> biome = level.getBiome(water);
        return biome.is(BiomeTags.IS_OCEAN) || biome.is(BiomeTags.IS_BEACH) || biome.is(CretaceousBiomes.habitat("ocean"))
                || biome.is(CretaceousBiomes.habitat("deep_sea")) || biome.is(CretaceousBiomes.habitat("coast"));
    }

    /** A patch of open sea 64 to 160 blocks off a colony, for a fishing party; null if none is loaded. */
    public static Vec3 seaPoint(Level level, BlockPos home, RandomSource random) {
        if (home == null) {
            return null;
        }
        int start = random.nextInt(12);
        for (int k = 0; k < 12; k++) {
            double a = ((start + k) % 12) * Math.PI / 6.0D;
            int far = 0;
            for (int r = 64; r <= 160; r += 16) {
                int x = home.getX() + Mth.floor(Math.cos(a) * r);
                int z = home.getZ() + Mth.floor(Math.sin(a) * r);
                if (!openSea(level, x, z, 4)) {
                    break;
                }
                far = r;
            }
            if (far >= 64) {
                double r = 64 + random.nextInt(far - 63);
                return new Vec3(home.getX() + Math.cos(a) * r, level.getSeaLevel(), home.getZ() + Math.sin(a) * r);
            }
        }
        return null;
    }

    // ------------------------------------------------------------------ stocking

    private static void fill(ServerLevel level, ColonyData data, BlockPos site, ServerPlayer player) {
        double distance = Math.sqrt(player.distanceToSqr(Vec3.atCenterOf(site)));
        if (distance > FILL_RANGE || distance < UNSEEN || !level.isPositionEntityTicking(site)) {
            return;
        }
        long last = data.lastFilled(site);
        long now = level.getGameTime();
        if (last != ColonyData.NEVER && now - last < RESTOCK) {
            return;
        }
        Random rnd = new Random(site.asLong() * 31L + 7L);
        int adults = 4 + rnd.nextInt(7);
        int young = 1 + rnd.nextInt(3);
        int present = level.getEntitiesOfClass(FlyingDinosaur.class, new AABB(site).inflate(200.0D, 128.0D, 200.0D),
                e -> e.isAlive() && site.equals(e.getColonyHome())).size();
        if (last != ColonyData.NEVER && present * 2 >= adults + young) {
            data.setFilled(site, now);
            return;
        }
        RandomSource random = level.getRandom();
        for (int i = present; i < adults + young; i++) {
            BlockPos at = spot(level, site, random, 6);
            if (at == null) {
                continue;
            }
            FlyingDinosaur bird = ModEntities.PTERANODON.get().create(level);
            if (bird == null) {
                return;
            }
            bird.moveTo(at.getX() + 0.5D, at.getY(), at.getZ() + 0.5D, random.nextFloat() * 360.0F, 0.0F);
            if (!level.noCollision(bird)) {
                continue;
            }
            bird.finalizeSpawn(level, level.getCurrentDifficultyAt(at), MobSpawnType.STRUCTURE, null, null);
            bird.setAge(i >= adults ? -6000 - random.nextInt(14000) : 0);
            bird.setColonyHome(site);
            bird.setPersistenceRequired();
            level.addFreshEntity(bird);
        }
        if (last == ColonyData.NEVER && rnd.nextInt(10) < 6) {
            // a scrape or two of eggs on the rocks
            Block egg = ModBlocks.eggFor("pteranodon");
            for (int n = 0, scrapes = 1 + rnd.nextInt(3); egg != null && n < scrapes; n++) {
                BlockPos at = spot(level, site, random, 5);
                if (at != null && level.getBlockState(at).isAir()) {
                    BlockState state = egg.defaultBlockState();
                    if (state.hasProperty(DinoEggBlock.WILD)) {
                        state = state.setValue(DinoEggBlock.WILD, true);
                    }
                    level.setBlock(at, state, Block.UPDATE_ALL);
                }
            }
        }
        data.setFilled(site, now);
    }

    /** A free standing spot on the ground within {@code radius} of the site, or null. */
    private static BlockPos spot(ServerLevel level, BlockPos site, RandomSource random, int radius) {
        for (int tries = 0; tries < 8; tries++) {
            int x = site.getX() + random.nextInt(radius * 2 + 1) - radius;
            int z = site.getZ() + random.nextInt(radius * 2 + 1) - radius;
            int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            BlockPos at = new BlockPos(x, top, z);
            BlockPos below = at.below();
            if (Math.abs(top - site.getY()) <= 3 && level.getFluidState(below).isEmpty()
                    && level.getBlockState(below).isFaceSturdy(level, below, net.minecraft.core.Direction.UP)) {
                return at;
            }
        }
        return null;
    }
}
