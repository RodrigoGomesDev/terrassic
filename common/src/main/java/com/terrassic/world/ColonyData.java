package com.terrassic.world;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * The coastal colonies of a world (world/PteroColonies), saved with it (data/terrassic_colonies.dat of the
 * dimension): each colony site and the game time it was last stocked (so it is restocked at most once a day).
 */
public class ColonyData extends SavedData {
    private static final String NAME = "terrassic_colonies";
    /** Not stocked yet. */
    public static final long NEVER = Long.MIN_VALUE;

    private final Map<Long, Long> colonies = new LinkedHashMap<>();

    public static ColonyData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(ColonyData::load, ColonyData::new, NAME);
    }

    private static ColonyData load(CompoundTag tag) {
        ColonyData data = new ColonyData();
        for (Tag t : tag.getList("Colonies", Tag.TAG_COMPOUND)) {
            CompoundTag c = (CompoundTag) t;
            data.colonies.put(c.getLong("Site"), c.contains("Filled") ? c.getLong("Filled") : NEVER);
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Map.Entry<Long, Long> e : this.colonies.entrySet()) {
            CompoundTag c = new CompoundTag();
            c.putLong("Site", e.getKey());
            if (e.getValue() != NEVER) {
                c.putLong("Filled", e.getValue());
            }
            list.add(c);
        }
        tag.put("Colonies", list);
        return tag;
    }

    /** Every colony site, packed BlockPos -> last stocked (or {@link #NEVER}). */
    public Map<Long, Long> colonies() {
        return this.colonies;
    }

    public void add(BlockPos site) {
        this.colonies.put(site.asLong(), NEVER);
        this.setDirty();
    }

    public long lastFilled(BlockPos site) {
        return this.colonies.getOrDefault(site.asLong(), NEVER);
    }

    public void setFilled(BlockPos site, long time) {
        this.colonies.put(site.asLong(), time);
        this.setDirty();
    }

    /** The nearest colony site to (x, z) within {@code range}, or null. */
    public BlockPos nearest(double x, double z, double range) {
        BlockPos best = null;
        double bestSq = range * range;
        for (long packed : this.colonies.keySet()) {
            BlockPos p = BlockPos.of(packed);
            double d = (p.getX() - x) * (p.getX() - x) + (p.getZ() - z) * (p.getZ() - z);
            if (d < bestSq) {
                bestSq = d;
                best = p;
            }
        }
        return best;
    }
}
