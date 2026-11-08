package com.terrassic.world;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.entity.SwimmingDinosaur;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;

import java.util.HashMap;
import java.util.Map;

/**
 * 1.10.1, the stable population (docs/estudos/12, section 4.3): the land is cut in cells of 128 x 128 blocks and each
 * cell remembers how many of its wild land animals died (hunted, killed in a fight, starved). The EcoSpawner fills a
 * cell only up to its share of the target less what it lost, and the loss heals at {@link #REFILL_PER_DAY} animals per
 * in-game day: a valley hunted empty stays empty for a while and comes back over days, not the moment a player walks
 * in. Roamers that despawn when the players leave are not losses: the cell gets the same number back, never more than its
 * share however often the players come and go. Saved per dimension (terrassic_population.dat).
 */
public final class RegionPopulation extends SavedData {
    private static final String NAME = "terrassic_population";
    public static final int CELL = 128;
    /** Wild land animals in a cell at density 1 (the 18 round a player in 80 blocks, over a cell's area). */
    public static final int CELL_TARGET = 15;
    /** Animals a day a cell gets back of what it lost. */
    public static final float REFILL_PER_DAY = 5.0F;
    private static final float MAX_LOST = 32.0F;

    private static final class Cell {
        float lost;
        long at;
    }

    private final Map<Long, Cell> cells = new HashMap<>();

    public static RegionPopulation of(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(RegionPopulation::load, RegionPopulation::new, NAME);
    }

    public static long key(BlockPos pos) {
        return ((long) Math.floorDiv(pos.getX(), CELL) << 32) | (Math.floorDiv(pos.getZ(), CELL) & 0xFFFFFFFFL);
    }

    /** The cell's box (the whole height round {@code y}). */
    public static AABB box(BlockPos pos) {
        int cx = Math.floorDiv(pos.getX(), CELL) * CELL;
        int cz = Math.floorDiv(pos.getZ(), CELL) * CELL;
        return new AABB(cx, pos.getY() - 96, cz, cx + CELL, pos.getY() + 96, cz + CELL);
    }

    /** What the cell has still lost now, the days since healed. */
    public float lost(ServerLevel level, BlockPos pos) {
        Cell c = this.cells.get(key(pos));
        if (c == null) {
            return 0.0F;
        }
        long now = level.getDayTime();
        if (now < c.at) {
            c.at = now;          // the time was set back: no healing for that
        }
        float healed = REFILL_PER_DAY * (now - c.at) / 24000.0F;
        if (healed > 0.0F) {
            c.lost = Math.max(0.0F, c.lost - healed);
            c.at = now;
            this.setDirty();
        }
        if (c.lost <= 0.0F) {
            this.cells.remove(key(pos));
        }
        return c.lost;
    }

    public void died(ServerLevel level, BlockPos pos) {
        this.lost(level, pos);
        Cell c = this.cells.computeIfAbsent(key(pos), k -> new Cell());
        c.at = level.getDayTime();
        c.lost = Math.min(MAX_LOST, c.lost + 1.0F);
        this.setDirty();
    }

    /** Test only: the cell has lost {@code n} (BehaviorTest "stable"). */
    public void setLost(ServerLevel level, BlockPos pos, float n) {
        Cell c = this.cells.computeIfAbsent(key(pos), k -> new Cell());
        c.at = level.getDayTime();
        c.lost = n;
        this.setDirty();
    }

    /** Wild land animals in the cell of {@code pos} now. */
    public static int count(ServerLevel level, BlockPos pos) {
        return level.getEntitiesOfClass(DinosaurEntity.class, box(pos),
                e -> e.isAlive() && !e.isTame() && !(e instanceof FlyingDinosaur) && !(e instanceof SwimmingDinosaur)).size();
    }

    /** How many more the spawner may put in the cell of {@code pos} with a share of {@code cap}. */
    public int room(ServerLevel level, BlockPos pos, int cap) {
        return cap - (int) Math.ceil(this.lost(level, pos)) - count(level, pos);
    }

    private static RegionPopulation load(CompoundTag tag) {
        RegionPopulation p = new RegionPopulation();
        ListTag list = tag.getList("Cells", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag t = list.getCompound(i);
            Cell c = new Cell();
            c.lost = t.getFloat("Lost");
            c.at = t.getLong("At");
            p.cells.put(t.getLong("Key"), c);
        }
        return p;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Map.Entry<Long, Cell> e : this.cells.entrySet()) {
            CompoundTag t = new CompoundTag();
            t.putLong("Key", e.getKey());
            t.putFloat("Lost", e.getValue().lost);
            t.putLong("At", e.getValue().at);
            list.add(t);
        }
        tag.put("Cells", list);
        return tag;
    }
}
