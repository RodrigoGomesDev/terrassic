package com.terrassic.world.continent;

import com.terrassic.Terrassic;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.event.events.common.PlayerEvent;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.Util;
import net.minecraft.core.Holder;
import net.minecraft.core.QuartPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BiomeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.saveddata.SavedData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The map of the island (docs/MUNDO.md, section 11): a coarse survey of the continent world, computed once per world
 * on a background thread from the world generator itself (no chunk is generated) and saved with the world
 * (data/terrassic_island_map.dat). Every player gets it on joining, and everyone online when the survey finishes.
 *
 * <p>The survey is {@link #SIZE} x {@link #SIZE} cells over the square from -2R to +2R (R = the continent radius):
 * for each cell the ground height and a {@link #category} of its biome. The client draws it in ink on paper
 * (client/ClientIslandMap).
 */
public final class IslandMap {
    private static final Logger LOG = LoggerFactory.getLogger(Terrassic.MOD_ID);
    public static final ResourceLocation SYNC = Terrassic.id("island_map");
    public static final int SIZE = 128;

    /** Biome categories of a cell, the same on the client. */
    public static final byte DEEP_SEA = 0;
    public static final byte SEA = 1;
    public static final byte BEACH = 2;
    public static final byte RIVER = 3;
    public static final byte SWAMP = 4;
    public static final byte PLAINS = 5;
    public static final byte FOREST = 6;
    public static final byte HIGHLANDS = 7;
    public static final byte DRY = 8;

    private static volatile boolean surveying;

    private IslandMap() {
    }

    public static void init() {
        LifecycleEvent.SERVER_STARTED.register(IslandMap::survey);
        LifecycleEvent.SERVER_STOPPING.register(server -> surveying = false);
        PlayerEvent.PLAYER_JOIN.register(player -> {
            Data data = Data.find(player.server);
            if (data != null) {
                send(player, data);
            }
        });
    }

    /** Starts the survey of a continent world that has none yet. */
    private static void survey(MinecraftServer server) {
        ServerLevel level = server.overworld();
        int radius = ModContinent.radius(level);
        if (radius <= 0 || Data.find(server) != null) {
            return;
        }
        surveying = true;
        ChunkGenerator generator = level.getChunkSource().getGenerator();
        RandomState random = level.getChunkSource().randomState();
        int extent = 2 * radius;
        long started = Util.getMillis();
        Util.backgroundExecutor().execute(() -> {
            byte[] heights = new byte[SIZE * SIZE];
            byte[] kinds = new byte[SIZE * SIZE];
            try {
                for (int j = 0; j < SIZE && surveying; j++) {
                    for (int i = 0; i < SIZE; i++) {
                        int x = Mth.floor(-extent + (i + 0.5D) * 2.0D * extent / SIZE);
                        int z = Mth.floor(-extent + (j + 0.5D) * 2.0D * extent / SIZE);
                        int y = generator.getBaseHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, level, random);
                        Holder<Biome> biome = generator.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(x),
                                QuartPos.fromBlock(Math.max(y, generator.getSeaLevel())), QuartPos.fromBlock(z),
                                random.sampler());
                        heights[j * SIZE + i] = (byte) Mth.clamp(y, 0, 255);
                        kinds[j * SIZE + i] = category(biome, y, generator.getSeaLevel());
                    }
                }
            } catch (RuntimeException e) {
                LOG.warn("Terrassic island map survey failed: {}", e.toString());
                return;
            }
            if (!surveying) {
                return;
            }
            server.execute(() -> {
                Data data = Data.create(server, extent, heights, kinds);
                LOG.info("Terrassic island map surveyed in {} ms", Util.getMillis() - started);
                for (ServerPlayer player : server.getPlayerList().getPlayers()) {
                    send(player, data);
                }
            });
        });
    }

    /** A biome sorted into what the map draws: the mod's own biomes by name, any other by the vanilla tags. */
    private static byte category(Holder<Biome> biome, int y, int seaLevel) {
        String id = biome.unwrapKey().map(k -> k.location().getPath()).orElse("");
        return switch (id) {
            case "deep_inner_sea" -> DEEP_SEA;
            case "inner_sea" -> SEA;
            case "cretaceous_beach" -> BEACH;
            case "cretaceous_river" -> RIVER;
            case "cypress_swamp", "river_delta" -> SWAMP;
            case "hadrosaur_plains" -> PLAINS;
            case "magnolia_forest", "redwood_forest" -> FOREST;
            case "cretaceous_highlands" -> HIGHLANDS;
            case "dry_lands" -> DRY;
            default -> biome.is(BiomeTags.IS_DEEP_OCEAN) ? DEEP_SEA
                    : biome.is(BiomeTags.IS_OCEAN) || y < seaLevel ? SEA
                    : biome.is(BiomeTags.IS_BEACH) ? BEACH
                    : biome.is(BiomeTags.IS_RIVER) ? RIVER
                    : biome.is(BiomeTags.IS_MOUNTAIN) || biome.is(BiomeTags.IS_HILL) ? HIGHLANDS
                    : biome.is(BiomeTags.IS_FOREST) || biome.is(BiomeTags.IS_TAIGA) || biome.is(BiomeTags.IS_JUNGLE) ? FOREST
                    : biome.is(BiomeTags.IS_BADLANDS) || biome.is(BiomeTags.HAS_DESERT_PYRAMID) ? DRY
                    : PLAINS;
        };
    }

    private static void send(ServerPlayer player, Data data) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeVarInt(SIZE);
        buf.writeVarInt(data.extent);
        buf.writeVarInt(data.seaLevel);
        buf.writeByteArray(data.heights);
        buf.writeByteArray(data.kinds);
        NetworkManager.sendToPlayer(player, SYNC, buf);
    }

    /** The survey saved with the world. */
    static final class Data extends SavedData {
        private static final String NAME = "terrassic_island_map";

        private final int extent;
        private final int seaLevel;
        private final byte[] heights;
        private final byte[] kinds;

        private Data(int extent, int seaLevel, byte[] heights, byte[] kinds) {
            this.extent = extent;
            this.seaLevel = seaLevel;
            this.heights = heights;
            this.kinds = kinds;
        }

        /** The saved survey, or null while there is none. */
        static Data find(MinecraftServer server) {
            Data data = server.overworld().getDataStorage().get(Data::load, NAME);
            return data != null && data.heights.length == SIZE * SIZE ? data : null;
        }

        static Data create(MinecraftServer server, int extent, byte[] heights, byte[] kinds) {
            Data data = new Data(extent, server.overworld().getChunkSource().getGenerator().getSeaLevel(), heights, kinds);
            data.setDirty();
            server.overworld().getDataStorage().set(NAME, data);
            return data;
        }

        private static Data load(CompoundTag tag) {
            return new Data(tag.getInt("Extent"), tag.getInt("SeaLevel"), tag.getByteArray("Heights"), tag.getByteArray("Kinds"));
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            tag.putInt("Extent", this.extent);
            tag.putInt("SeaLevel", this.seaLevel);
            tag.putByteArray("Heights", this.heights);
            tag.putByteArray("Kinds", this.kinds);
            return tag;
        }
    }
}
