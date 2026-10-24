package com.terrassic.research;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Every player's {@link Knowledge}, saved with the world (data/terrassic_research.dat of the overworld). */
public class ResearchData extends SavedData {
    private static final String NAME = "terrassic_research";

    private final Map<UUID, Knowledge> players = new HashMap<>();

    public static ResearchData get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(ResearchData::load, ResearchData::new, NAME);
    }

    public Knowledge of(UUID player) {
        return this.players.computeIfAbsent(player, id -> new Knowledge());
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        CompoundTag players = new CompoundTag();
        for (Map.Entry<UUID, Knowledge> e : this.players.entrySet()) {
            players.put(e.getKey().toString(), e.getValue().save());
        }
        tag.put("Players", players);
        return tag;
    }

    private static ResearchData load(CompoundTag tag) {
        ResearchData data = new ResearchData();
        CompoundTag players = tag.getCompound("Players");
        for (String key : players.getAllKeys()) {
            try {
                data.players.put(UUID.fromString(key), Knowledge.load(players.getCompound(key)));
            } catch (IllegalArgumentException ignored) {
                // not a player uuid: skip
            }
        }
        return data;
    }
}
