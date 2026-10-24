package com.terrassic.research;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.storage.DimensionDataStorage;

import java.util.UUID;

/**
 * Individual data/terrassic_research_&lt;uuid&gt;.dat files, using Minecraft's SavedData lifecycle.
 * The original terrassic_research.dat remains a read-only migration archive, never deleted or marked dirty by
 * normal progress. First access imports that UUID if no individual file exists and queues the imported record for save.
 */
public final class ResearchData extends SavedData {
    private static final String NAME = "terrassic_research";
    private final DimensionDataStorage storage;
    private final CompoundTag legacyPlayers;

    private ResearchData(DimensionDataStorage storage, CompoundTag legacyPlayers) {
        this.storage = storage;
        this.legacyPlayers = legacyPlayers;
    }

    public static ResearchData get(MinecraftServer server) {
        return open(server.overworld().getDataStorage());
    }

    /** Package-private for the regression with real DimensionDataStorage and temporary files. */
    static ResearchData open(DimensionDataStorage storage) {
        return storage.computeIfAbsent(tag -> new ResearchData(storage, tag.getCompound("Players")),
                () -> new ResearchData(storage, new CompoundTag()), NAME);
    }

    public Knowledge of(UUID player) {
        String id = player.toString();
        PlayerData data = this.storage.computeIfAbsent(PlayerData::load, () -> {
            boolean migrate = this.legacyPlayers.contains(id, Tag.TAG_COMPOUND);
            return new PlayerData(migrate ? Knowledge.load(this.legacyPlayers.getCompound(id)) : new Knowledge(), migrate);
        }, NAME + "_" + id);
        return data.knowledge;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.put("Players", this.legacyPlayers.copy());
        return tag;
    }

    private static final class PlayerData extends SavedData {
        private final Knowledge knowledge;

        private PlayerData(Knowledge knowledge, boolean dirty) {
            this.knowledge = knowledge;
            this.knowledge.onChange(this::setDirty);
            this.setDirty(dirty);
        }

        private static PlayerData load(CompoundTag tag) {
            return new PlayerData(Knowledge.load(tag.getCompound("Knowledge")), false);
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            tag.putInt("Version", 1);
            tag.put("Knowledge", this.knowledge.save());
            return tag;
        }
    }
}
