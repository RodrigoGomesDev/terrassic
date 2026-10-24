package com.terrassic.config;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * The world's {@link Rules}, saved with it (data/terrassic_rules.dat of the overworld). A world without the file
 * (a new world, or one made before the rules existed) starts from the defaults in config/terrassic-world.json.
 */
public class RulesData extends SavedData {
    private static final String NAME = "terrassic_rules";

    private final Rules rules;

    private RulesData(Rules rules) {
        this.rules = rules;
    }

    public static RulesData get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(RulesData::load, RulesData::create, NAME);
    }

    private static RulesData create() {
        RulesData data = new RulesData(Rules.loadDefaults());
        data.setDirty();
        return data;
    }

    private static RulesData load(CompoundTag tag) {
        return new RulesData(Rules.load(tag.getCompound("Rules")));
    }

    public Rules rules() {
        return this.rules;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.put("Rules", this.rules.save());
        return tag;
    }
}
