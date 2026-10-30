package com.terrassic.world;

import com.terrassic.Terrassic;
import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.MobSpawnSettings;

/**
 * v0.15, "Minecraft normal com dinossauros" (Rodrigo, 30/10/2026; docs/MUNDO.md, section 11): outside the Cretaceous
 * biomes the dinosaurs are an extra on top of Minecraft's own fauna, about one animal in four by default
 * ({@link Rule#DINO_SHARE}). The cows, sheep, pigs, horses, squids and dolphins keep spawning exactly as in vanilla;
 * only the dinosaurs are thinned.
 *
 * <ul>
 *   <li><b>Natural and world-generation spawns</b> (Minecraft's own spawner, through the spawn rules of
 *       DinosaurEntity and SwimmingDinosaur): a dinosaur picked from the biome's list is let through with the chance
 *       that leaves it at the chosen share of that list, {@code share / (1 - share) * vanilla weight / dino weight}.
 *       The roll is the same for every member of one group (chunk and tick), so a herd spawns whole or not at all.</li>
 *   <li><b>EcoSpawner</b> (the replenishment around each player): its targets are multiplied by
 *       {@link #ecoFactor}: a third of the continent's at the default share.</li>
 * </ul>
 * In the Cretaceous biomes of the Terrassic world type nothing changes: there the dinosaurs are the fauna.
 */
public final class VanillaShare {
    /** Set while EcoSpawner checks a spot: its own targets already hold the share. */
    private static final ThreadLocal<Boolean> ECO = ThreadLocal.withInitial(() -> Boolean.FALSE);

    private VanillaShare() {
    }

    /** Runs EcoSpawner's spawn-rule check without the thinning below. */
    static boolean ecoCheck(java.util.function.BooleanSupplier check) {
        ECO.set(Boolean.TRUE);
        try {
            return check.getAsBoolean();
        } finally {
            ECO.set(Boolean.FALSE);
        }
    }

    /** Whether a natural or world-generation spawn of this dinosaur may go ahead here (always true elsewhere). */
    public static boolean allows(EntityType<?> type, LevelAccessor level, MobSpawnType reason, BlockPos pos) {
        if (reason != MobSpawnType.NATURAL && reason != MobSpawnType.CHUNK_GENERATION || ECO.get()
                || !(level instanceof ServerLevelAccessor server)) {
            return true;
        }
        Holder<Biome> biome = level.getBiome(pos);
        if (biome.is(CretaceousBiomes.CRETACEOUS)) {
            return true;
        }
        double chance = chance(biome.value(), type.getCategory(), Rules.of(server.getLevel()).get(Rule.DINO_SHARE));
        return chance >= 1.0D || chance > 0.0D && roll(pos, server.getLevel().getGameTime(), type) < chance;
    }

    /** The chance of letting a dinosaur of that category through in this biome. */
    static double chance(Biome biome, MobCategory category, double share) {
        if (share >= 1.0D) {
            return 1.0D;
        }
        int ours = 0;
        int others = 0;
        for (MobSpawnSettings.SpawnerData data : biome.getMobSettings().getMobs(category).unwrap()) {
            if (Terrassic.MOD_ID.equals(BuiltInRegistries.ENTITY_TYPE.getKey(data.type).getNamespace())) {
                ours += data.getWeight().asInt();
            } else {
                others += data.getWeight().asInt();
            }
        }
        if (ours == 0) {
            return 1.0D;
        }
        // a biome with no vanilla animals of that kind (badlands): a quarter of what it would have
        if (others == 0) {
            return share;
        }
        return Math.min(1.0D, share / (1.0D - share) * others / ours);
    }

    /** EcoSpawner's targets around a player standing in this biome: full in the Cretaceous, scaled elsewhere. */
    static double ecoFactor(Holder<Biome> biome, Rules rules) {
        if (biome.is(CretaceousBiomes.CRETACEOUS)) {
            return 1.0D;
        }
        double share = rules.get(Rule.DINO_SHARE);
        return share >= 0.5D ? 1.0D : share / (1.0D - share);
    }

    /** A number in [0, 1) that is the same for one chunk, tick and species: one roll per group. */
    private static double roll(BlockPos pos, long time, EntityType<?> type) {
        long h = (pos.getX() >> 4) * 0x9E3779B97F4A7C15L ^ (pos.getZ() >> 4) * 0xC2B2AE3D27D4EB4FL
                ^ time * 0x165667B19E3779F9L ^ BuiltInRegistries.ENTITY_TYPE.getKey(type).hashCode();
        h ^= h >>> 33;
        h *= 0xFF51AFD7ED558CCDL;
        h ^= h >>> 33;
        h *= 0xC4CEB9FE1A85EC53L;
        h ^= h >>> 33;
        return (h >>> 11) * 0x1.0p-53;
    }
}
