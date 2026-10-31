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
 *       {@link #ecoFactor}: about half of the continent's at the default share (0.35 since v1.0.1).</li>
 * </ul>
 * In the Cretaceous biomes of the Terrassic world type nothing changes: there the dinosaurs are the fauna.
 */
public final class VanillaShare {
    /** Set while EcoSpawner checks a spot: its own targets already hold the share. */
    private static final ThreadLocal<Boolean> ECO = ThreadLocal.withInitial(() -> Boolean.FALSE);

    private VanillaShare() {
    }

    /** v0.16.1: {@code /terrassic fauna} (operators), to measure the share in a real world (Mac test: about 1 in 10
     *  on Fabric and 1 in 4 on Forge). Prints, for the biome under the player, the weights of the mod and of vanilla
     *  in the land and sea lists, the chance a dino is let through, EcoSpawner's factor, and the wild animals
     *  counted within 128 blocks. */
    public static void init() {
        dev.architectury.event.events.common.CommandRegistrationEvent.EVENT.register((dispatcher, registry, selection) ->
                dispatcher.register(net.minecraft.commands.Commands.literal(Terrassic.MOD_ID).then(
                        net.minecraft.commands.Commands.literal("fauna").requires(s -> s.hasPermission(2)).executes(ctx -> {
                            net.minecraft.server.level.ServerPlayer player = ctx.getSource().getPlayerOrException();
                            for (String line : report(player)) {
                                ctx.getSource().sendSuccess(() -> net.minecraft.network.chat.Component.literal(line), false);
                            }
                            return 1;
                        }))));
    }

    private static java.util.List<String> report(net.minecraft.server.level.ServerPlayer player) {
        net.minecraft.server.level.ServerLevel level = player.serverLevel();
        Holder<Biome> biome = level.getBiome(player.blockPosition());
        Rules rules = Rules.of(level);
        double share = rules.get(Rule.DINO_SHARE);
        java.util.List<String> out = new java.util.ArrayList<>();
        out.add("bioma " + biome.unwrapKey().map(k -> k.location().toString()).orElse("?")
                + (biome.is(CretaceousBiomes.CRETACEOUS) ? " (Cretaceo)" : "") + ", dino_share " + share
                + ", fator EcoSpawner " + String.format(java.util.Locale.ROOT, "%.2f", ecoFactor(biome, rules)));
        for (MobCategory category : new MobCategory[]{MobCategory.CREATURE, MobCategory.WATER_CREATURE}) {
            int ours = 0;
            int others = 0;
            for (MobSpawnSettings.SpawnerData data : biome.value().getMobSettings().getMobs(category).unwrap()) {
                if (Terrassic.MOD_ID.equals(BuiltInRegistries.ENTITY_TYPE.getKey(data.type).getNamespace())) {
                    ours += data.getWeight().asInt();
                } else {
                    others += data.getWeight().asInt();
                }
            }
            out.add(category.getName() + ": peso mod " + ours + ", peso vanilla " + others + ", chance "
                    + String.format(java.util.Locale.ROOT, "%.2f", chance(biome.value(), category, share)));
        }
        int dinoLand = 0;
        int dinoSea = 0;
        int vanillaLand = 0;
        int vanillaSea = 0;
        net.minecraft.world.phys.AABB box = player.getBoundingBox().inflate(128.0D, 384.0D, 128.0D);
        for (net.minecraft.world.entity.Mob mob : level.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, box)) {
            boolean ours = Terrassic.MOD_ID.equals(BuiltInRegistries.ENTITY_TYPE.getKey(mob.getType()).getNamespace());
            if (ours && mob instanceof com.terrassic.entity.DinosaurEntity d && d.isTame()) {
                continue;
            }
            MobCategory c = mob.getType().getCategory();
            if (c == MobCategory.CREATURE) {
                if (ours) {
                    dinoLand++;
                } else {
                    vanillaLand++;
                }
            } else if (c == MobCategory.WATER_CREATURE) {
                if (ours) {
                    dinoSea++;
                } else {
                    vanillaSea++;
                }
            }
        }
        out.add("a 128 blocos: terra " + dinoLand + " dinos / " + vanillaLand + " vanilla; mar " + dinoSea
                + " dinos / " + vanillaSea + " vanilla");
        return out;
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
