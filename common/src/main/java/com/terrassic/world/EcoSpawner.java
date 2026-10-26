package com.terrassic.world;

import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.entity.SwimmingDinosaur;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.event.events.common.TickEvent;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.HitResult;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * The living ecosystem (docs/REGRAS.md, "Ecossistema"). Land and sea augment vanilla populations;
 * wild flyers use this spawner exclusively so chunk generation cannot bypass the sky budget.
 *
 * <p>Every two seconds per player, staggered by UUID, it counts wild creatures within {@link #RADIUS} blocks in three kinds
 * (land and sea) and, where a kind is below its target, spawns one group of it 36 to 80 blocks away.
 * The sky is counted over a 192-block region and the full world height, once every twenty seconds per player,
 * with a default shared regional target of four and insertion 64 to 112 blocks away, outside direct view:
 * <ul>
 *   <li>the species come from the biome's own spawn list (the WORLD table of gen_species.py, the Cretaceous biomes,
 *       config/terrassic.json), weighted the same way, so every biome keeps its fauna;</li>
 *   <li><b>land</b>: a herd, pack or pair on the surface, with babies among them ({@link Rule#BABY_SHARE});</li>
 *   <li><b>flyers</b>: a flock already in the air 16 to 40 blocks over the ground, soaring together (SoarGoal);</li>
 *   <li><b>sea</b>: a pod or school in open water, deep enough for the animal.</li>
 * </ul>
 * Targets scale with the world rules: {@link Rule#SPAWN_DENSITY} times the kind's own multiplier; nothing spawns
 * once the world holds {@link Rule#MAX_CREATURES} wild creatures. Creatures placed here are "roamers": like
 * ARK's wild dinos they despawn once every player is far away (DinosaurEntity.removeWhenFarAway), unless tamed or
 * named, so the population follows the players instead of piling up. Existing persistent animals count toward
 * the target but are never culled by this spawner. The doMobSpawning game rule turns it off.
 */
public final class EcoSpawner {
    /** Ticks between spawn rounds. */
    private static final int PERIOD = 40;
    /** Horizontal radius around a player in which wild creatures are counted. */
    private static final double RADIUS = 80.0D;
    private static final int MIN_DISTANCE = 36;
    private static final int MAX_DISTANCE = 80;
    /** Wild creatures of each kind around a player at density 1. */
    private static final int LAND_TARGET = 18;
    private static final int SEA_TARGET = 12;
    /** Spot searches per kind per round before giving up until the next round. */
    private static final int TRIES = 4;
    /** Share of a group's members after the first that are babies, at baby_share 1. */
    private static final float BABY_CHANCE = 0.18F;

    enum Kind { LAND, FLYER, SEA, OTHER }

    private static final Map<EntityType<?>, Kind> KINDS = new HashMap<>();
    /** Wild creatures in the level, recounted every few rounds (cheap enough, and the cap does not need precision). */
    private static final Map<ServerLevel, Integer> WILD = new HashMap<>();
    private static final Map<ServerLevel, Long> LAST_COUNT = new HashMap<>();

    private EcoSpawner() {
    }

    public static void init() {
        TickEvent.SERVER_LEVEL_POST.register(EcoSpawner::tick);
        LifecycleEvent.SERVER_STOPPED.register(server -> {
            WILD.clear();
            LAST_COUNT.clear();
            KINDS.clear();
        });
    }

    private static void tick(ServerLevel level) {
        long time = level.getGameTime();
        if (!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)) {
            return;
        }
        List<ServerPlayer> players = new ArrayList<>();
        for (ServerPlayer p : level.players()) {
            if (!p.isSpectator() && SpawnBudget.isTurn(time, p.getUUID().hashCode(), PERIOD)) {
                players.add(p);
            }
        }
        if (players.isEmpty()) {
            return;
        }
        Rules rules = Rules.of(level);
        double density = rules.get(Rule.SPAWN_DENSITY);
        if (density <= 0.0D) {
            return;
        }
        // The scheduled slot can be empty, so track recount time instead of requiring an exact modulo tick.
        if (!WILD.containsKey(level) || time - LAST_COUNT.getOrDefault(level, time) >= PERIOD * 5) {
            int wild = 0;
            for (Entity e : level.getAllEntities()) {
                if (e instanceof DinosaurEntity d && !d.isTame()) {
                    wild++;
                }
            }
            WILD.put(level, wild);
            LAST_COUNT.put(level, time);
        }
        int cap = (int) rules.get(Rule.MAX_CREATURES);
        RandomSource random = level.getRandom();
        // Rotate priority among players assigned to the same tick, rather than always favoring login order.
        int first = (int) Math.floorMod(time / PERIOD, players.size());
        for (int index = 0; index < players.size(); index++) {
            ServerPlayer player = players.get((first + index) % players.size());
            if (WILD.get(level) >= cap) {
                return;
            }
            AABB box = new AABB(player.getX() - RADIUS, Math.max(level.getMinBuildHeight(), player.getY() - RADIUS), player.getZ() - RADIUS,
                    player.getX() + RADIUS, Math.min(level.getMaxBuildHeight(), player.getY() + RADIUS), player.getZ() + RADIUS);
            int land = 0;
            int sea = 0;
            for (DinosaurEntity d : level.getEntitiesOfClass(DinosaurEntity.class, box, e -> !e.isTame())) {
                if (d instanceof FlyingDinosaur) {
                    continue;
                } else if (d instanceof SwimmingDinosaur) {
                    sea++;
                } else {
                    land++;
                }
            }
            if (land < target(LAND_TARGET, density, rules.get(Rule.LAND_SPAWNS))) {
                spawnRound(level, player, Kind.LAND, rules, random,
                        SpawnBudget.allowance(target(LAND_TARGET, density, rules.get(Rule.LAND_SPAWNS)), land, cap, WILD.get(level)));
            }
            if (SpawnBudget.isTurn(time, player.getUUID().hashCode(), SpawnBudget.SKY_PERIOD)) {
                // Count the whole visible sky, including birds that left the inner 80-block replenishment zone.
                AABB sky = new AABB(player.getX() - SpawnBudget.SKY_RADIUS, level.getMinBuildHeight(),
                        player.getZ() - SpawnBudget.SKY_RADIUS, player.getX() + SpawnBudget.SKY_RADIUS,
                        level.getMaxBuildHeight(), player.getZ() + SpawnBudget.SKY_RADIUS);
                int regionalFlyers = level.getEntitiesOfClass(FlyingDinosaur.class, sky,
                        e -> e.isAlive() && !e.isTame()).size();
                int skyTarget = target(SpawnBudget.SKY_TARGET, density, rules.get(Rule.FLYER_SPAWNS));
                spawnRound(level, player, Kind.FLYER, rules, random,
                        SpawnBudget.allowance(skyTarget, regionalFlyers, cap, WILD.get(level)));
            }
            if (sea < target(SEA_TARGET, density, rules.get(Rule.SEA_SPAWNS))) {
                spawnRound(level, player, Kind.SEA, rules, random,
                        SpawnBudget.allowance(target(SEA_TARGET, density, rules.get(Rule.SEA_SPAWNS)), sea, cap, WILD.get(level)));
            }
        }
    }

    private static int target(int base, double density, double kind) {
        return (int) Math.round(base * density * kind);
    }

    private static void spawnRound(ServerLevel level, ServerPlayer player, Kind kind, Rules rules, RandomSource random, int budget) {
        if (budget <= 0) {
            return;
        }
        for (int i = 0; i < TRIES; i++) {
            double angle = random.nextDouble() * Math.PI * 2.0D;
            double distance = kind == Kind.FLYER
                    ? SpawnBudget.SKY_MIN_DISTANCE + random.nextDouble() * (SpawnBudget.SKY_MAX_DISTANCE - SpawnBudget.SKY_MIN_DISTANCE)
                    : MIN_DISTANCE + random.nextDouble() * (MAX_DISTANCE - MIN_DISTANCE);
            int x = Mth.floor(player.getX() + Math.cos(angle) * distance);
            int z = Mth.floor(player.getZ() + Math.sin(angle) * distance);
            BlockPos column = new BlockPos(x, player.getBlockY(), z);
            if (!level.isPositionEntityTicking(column)) {
                continue;
            }
            int spawned = switch (kind) {
                case LAND -> spawnLand(level, x, z, rules, random, budget, player.getY());
                case FLYER -> spawnFlock(level, x, z, rules, random, budget, player.getY());
                case SEA -> spawnSea(level, x, z, rules, random, budget, player.getY());
                default -> 0;
            };
            if (spawned > 0) {
                WILD.merge(level, spawned, Integer::sum);
                return;
            }
        }
    }

    // ------------------------------------------------------------------ land

    private static int spawnLand(ServerLevel level, int x, int z, Rules rules, RandomSource random, int budget, double playerY) {
        BlockPos pos = new BlockPos(x, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
        if (Math.abs(pos.getY() - playerY) > RADIUS || !level.getFluidState(pos.below()).isEmpty() || !level.getFluidState(pos).isEmpty()) {
            return 0;
        }
        MobSpawnSettings.SpawnerData data = pick(level, pos, MobCategory.CREATURE, Kind.LAND, random);
        if (data == null || !canStand(level, data.type, pos, random)) {
            return 0;
        }
        int count = Math.min(budget, groupSize(data, random));
        int spawned = 0;
        SpawnGroupData group = null;
        double spacing = Math.max(4.0D, data.type.getWidth() * 1.75D);
        double groupAngle = random.nextDouble() * Math.PI * 2;
        for (int i = 0; i < count; i++) {
            BlockPos at = pos;
            if (i > 0) {
                double angle = groupAngle + i * 2.399963229728653D;
                double radius = spacing * Math.sqrt(i);
                int ax = x + Mth.floor(Math.cos(angle) * radius);
                int az = z + Mth.floor(Math.sin(angle) * radius);
                if (!level.isPositionEntityTicking(new BlockPos(ax, pos.getY(), az))) {
                    continue;
                }
                at = new BlockPos(ax, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ax, az), az);
                if (Math.abs(at.getY() - playerY) > RADIUS || !level.getFluidState(at.below()).isEmpty()
                        || !canStand(level, data.type, at, random)) {
                    continue;
                }
            }
            DinosaurEntity dino = create(level, data.type, at, random);
            if (dino == null) {
                continue;
            }
            group = dino.finalizeSpawn(level, level.getCurrentDifficultyAt(at), MobSpawnType.NATURAL, group, null);
            if (i > 0) {
                maybeBaby(dino, rules, random);
            }
            if (level.addFreshEntity(dino)) {
                spawned++;
            }
        }
        return spawned;
    }

    private static boolean canStand(ServerLevel level, EntityType<?> type, BlockPos pos, RandomSource random) {
        return SpawnPlacements.checkSpawnRules(type, level, MobSpawnType.NATURAL, pos, random)
                && level.noCollision(type.getAABB(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D));
    }

    // ------------------------------------------------------------------ sky

    private static int spawnFlock(ServerLevel level, int x, int z, Rules rules, RandomSource random, int budget, double playerY) {
        if (!level.isDay()) {
            // flocks take to the sky by day (SoarGoal); at night the flyers already around rest on the ground
            return 0;
        }
        int ground = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
        BlockPos surface = new BlockPos(x, ground, z);
        MobSpawnSettings.SpawnerData data = pick(level, surface, MobCategory.CREATURE, Kind.FLYER, random);
        if (data == null) {
            return 0;
        }
        int y = Math.min(ground + 16 + random.nextInt(25), level.getMaxBuildHeight() - 8);
        // Prefer at least two flying the same way, unless the remaining budget only allows one.
        int count = Math.min(budget, Math.max(2, groupSize(data, random)));
        float heading = random.nextFloat() * 360.0F;
        Vec3 dir = Vec3.directionFromRotation(0.0F, heading);
        Vec3 side = new Vec3(dir.z, 0, -dir.x);
        double spacing = Math.max(8.0D, data.type.getWidth() * 2.5D);
        int spawned = 0;
        for (int i = 0; i < count; i++) {
            int row = (i + 1) / 2;
            double lateral = i == 0 ? 0 : (i % 2 == 0 ? -1 : 1) * row * spacing;
            double px = x + 0.5D + side.x * lateral - dir.x * row * spacing * 0.7D;
            double py = y + (i == 0 ? 0.0D : random.nextGaussian() * 1.5D);
            double pz = z + 0.5D + side.z * lateral - dir.z * row * spacing * 0.7D;
            Vec3 position = new Vec3(px, py, pz);
            if (Math.abs(py - playerY) > RADIUS || !level.isPositionEntityTicking(BlockPos.containing(px, py, pz))) {
                continue;
            }
            if (visibleOrTooClose(level, position)) {
                continue;
            }
            if (!level.noCollision(data.type.getAABB(px, py, pz))) {
                continue;
            }
            Entity e = data.type.create(level);
            if (!(e instanceof FlyingDinosaur bird)) {
                return spawned;
            }
            bird.setRoamer(true);
            bird.moveTo(px, py, pz, heading, 0.0F);
            bird.finalizeSpawn(level, level.getCurrentDifficultyAt(BlockPos.containing(px, py, pz)), MobSpawnType.NATURAL, null, null);
            if (bird.isBaby()) {
                bird.setAge(0);
            }
            bird.startSoaring(dir);
            if (level.addFreshEntity(bird)) {
                spawned++;
            }
        }
        return spawned;
    }

    /** Do not materialize a flock beside another player, or in an unobstructed direction they are watching. */
    private static boolean visibleOrTooClose(ServerLevel level, Vec3 position) {
        for (ServerPlayer player : level.players()) {
            if (player.isSpectator()) continue;
            Vec3 relative = position.subtract(player.getEyePosition());
            double distance = relative.lengthSqr();
            if (distance < SpawnBudget.SKY_MIN_DISTANCE * SpawnBudget.SKY_MIN_DISTANCE) return true;
            if (distance < 128 * 128 && relative.normalize().dot(player.getLookAngle()) > 0.35D
                    && level.clip(new ClipContext(player.getEyePosition(), position, ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE, player)).getType() == HitResult.Type.MISS) return true;
        }
        return false;
    }

    // ------------------------------------------------------------------ sea

    private static int spawnSea(ServerLevel level, int x, int z, Rules rules, RandomSource random, int budget, double playerY) {
        int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z) - 1;
        int floor = level.getHeight(Heightmap.Types.OCEAN_FLOOR, x, z);
        BlockPos surface = new BlockPos(x, top, z);
        if (!level.getFluidState(surface).is(FluidTags.WATER) || top - floor < 6) {
            return 0;
        }
        int sea = level.getSeaLevel();
        int low = Math.max(floor + 3, sea - 40);
        int high = Math.min(top - 3, sea - 6);
        if (high < low) {
            return 0;
        }
        BlockPos pos = new BlockPos(x, low + random.nextInt(high - low + 1), z);
        MobSpawnSettings.SpawnerData data = pick(level, pos, MobCategory.WATER_CREATURE, Kind.SEA, random);
        if (data == null || !SpawnPlacements.checkSpawnRules(data.type, level, MobSpawnType.NATURAL, pos, random)) {
            return 0;
        }
        int count = Math.min(budget, groupSize(data, random));
        int spawned = 0;
        SpawnGroupData group = null;
        for (int i = 0; i < count; i++) {
            BlockPos at = i == 0 ? pos : pos.offset(random.nextInt(7) - 3, random.nextInt(3) - 1, random.nextInt(7) - 3);
            if (Math.abs(at.getY() - playerY) > RADIUS || !level.isPositionEntityTicking(at)) {
                continue;
            }
            if (i > 0 && !level.getFluidState(at).is(FluidTags.WATER)) {
                continue;
            }
            if (!level.noCollision(data.type.getAABB(at.getX() + 0.5D, at.getY(), at.getZ() + 0.5D))) {
                continue;
            }
            DinosaurEntity dino = create(level, data.type, at, random);
            if (dino == null) {
                continue;
            }
            group = dino.finalizeSpawn(level, level.getCurrentDifficultyAt(at), MobSpawnType.NATURAL, group, null);
            if (level.addFreshEntity(dino)) {
                spawned++;
            }
        }
        return spawned;
    }

    // ------------------------------------------------------------------ shared

    /** A Terrassic species of that kind from the biome's spawn list, picked by weight (null when there is none). */
    private static MobSpawnSettings.SpawnerData pick(ServerLevel level, BlockPos pos, MobCategory category, Kind kind,
                                                     RandomSource random) {
        Holder<Biome> biome = level.getBiome(pos);
        List<MobSpawnSettings.SpawnerData> options = new ArrayList<>();
        int total = 0;
        for (MobSpawnSettings.SpawnerData data : biome.value().getMobSettings().getMobs(category).unwrap()) {
            if (kindOf(level, data.type) == kind) {
                options.add(data);
                total += data.getWeight().asInt();
            }
        }
        if (total <= 0) {
            return null;
        }
        int roll = random.nextInt(total);
        for (MobSpawnSettings.SpawnerData data : options) {
            roll -= data.getWeight().asInt();
            if (roll < 0) {
                return data;
            }
        }
        return null;
    }

    /** Land, flyer or sea, found once per type by making a throwaway instance (OTHER for anything not ours). */
    private static Kind kindOf(ServerLevel level, EntityType<?> type) {
        Kind kind = KINDS.get(type);
        if (kind == null) {
            kind = Kind.OTHER;
            if (BuiltInRegistries.ENTITY_TYPE.getKey(type).getNamespace().equals("terrassic")) {
                Entity e = type.create(level);
                if (e instanceof FlyingDinosaur) {
                    kind = Kind.FLYER;
                } else if (e instanceof SwimmingDinosaur) {
                    kind = Kind.SEA;
                } else if (e instanceof DinosaurEntity) {
                    kind = Kind.LAND;
                }
                if (e != null) {
                    e.discard();
                }
            }
            KINDS.put(type, kind);
        }
        return kind;
    }

    private static int groupSize(MobSpawnSettings.SpawnerData data, RandomSource random) {
        return data.minCount + random.nextInt(Math.max(1, data.maxCount - data.minCount + 1));
    }

    private static DinosaurEntity create(ServerLevel level, EntityType<?> type, BlockPos pos, RandomSource random) {
        Entity e = type.create(level);
        if (!(e instanceof DinosaurEntity dino)) {
            return null;
        }
        dino.setRoamer(true);
        dino.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, random.nextFloat() * 360.0F, 0.0F);
        return dino;
    }

    /** Some of the herd are babies, of different ages (and so sizes). */
    private static void maybeBaby(DinosaurEntity dino, Rules rules, RandomSource random) {
        if (random.nextFloat() < BABY_CHANCE * rules.get(Rule.BABY_SHARE)) {
            dino.setAge(-6000 - random.nextInt(18001));
        }
    }
}
