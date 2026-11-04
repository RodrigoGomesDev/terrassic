package com.terrassic.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 1.7 (player feedback, 04/11/2026: "you can't see where your dinos are, and the whistle only works for about 50
 * blocks"): where every tamed dinosaur was last seen, saved with the world (data/terrassic_tamed.dat of the overworld)
 * so the owner can find it after its chunk unloads. A loaded tame animal refreshes its line every five seconds
 * (DinosaurEntity.tick); it leaves the list when it dies or stops being tamed. The "My dinos" list
 * (network/TamedNetwork, client/MyDinosScreen, {@code /terrassic dinos}) and the HUD tracker read it.
 * Server thread only.
 */
public class TamedRegistry extends SavedData {
    private static final String NAME = "terrassic_tamed";
    /** Ticks between two refreshes of a loaded tame animal. */
    public static final int REFRESH_TICKS = 100;

    /** One tamed animal: who owns it, what it is, its name ("" = none), where and when (overworld game time) it was
     *  last seen, and whether it was told to wait there. */
    public record Entry(UUID dino, UUID owner, String species, String name, ResourceLocation dimension, BlockPos pos,
                        long seen, boolean sitting) {
    }

    private final Map<UUID, Entry> entries = new LinkedHashMap<>();

    public static TamedRegistry get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(TamedRegistry::load, TamedRegistry::new, NAME);
    }

    private static TamedRegistry load(CompoundTag tag) {
        TamedRegistry data = new TamedRegistry();
        for (Tag t : tag.getList("Tamed", Tag.TAG_COMPOUND)) {
            CompoundTag c = (CompoundTag) t;
            if (!c.hasUUID("Dino") || !c.hasUUID("Owner")) {
                continue;
            }
            ResourceLocation dim = ResourceLocation.tryParse(c.getString("Dim"));
            if (dim == null) {
                continue;
            }
            Entry e = new Entry(c.getUUID("Dino"), c.getUUID("Owner"), c.getString("Species"), c.getString("Name"), dim,
                    BlockPos.of(c.getLong("Pos")), c.getLong("Seen"), c.getBoolean("Sitting"));
            data.entries.put(e.dino(), e);
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Entry e : this.entries.values()) {
            list.add(write(e));
        }
        tag.put("Tamed", list);
        return tag;
    }

    /** One entry as NBT (also what the client gets, with the seconds since it was seen). */
    public static CompoundTag write(Entry e) {
        CompoundTag c = new CompoundTag();
        c.putUUID("Dino", e.dino());
        c.putUUID("Owner", e.owner());
        c.putString("Species", e.species());
        c.putString("Name", e.name());
        c.putString("Dim", e.dimension().toString());
        c.putLong("Pos", e.pos().asLong());
        c.putLong("Seen", e.seen());
        c.putBoolean("Sitting", e.sitting());
        return c;
    }

    /** Records where this animal is now (or drops it when it is not tamed any more). */
    public static void update(DinosaurEntity dino) {
        MinecraftServer server = dino.getServer();
        if (server == null || dino.level().isClientSide()) {
            return;
        }
        TamedRegistry data = get(server);
        UUID owner = dino.getOwnerUUID();
        if (!dino.isTame() || owner == null || !dino.isAlive()) {
            data.forget(dino.getUUID());
            return;
        }
        String name = dino.hasCustomName() && dino.getCustomName() != null ? dino.getCustomName().getString() : "";
        Entry e = new Entry(dino.getUUID(), owner, dino.speciesId(), name, dino.level().dimension().location(),
                dino.blockPosition(), server.overworld().getGameTime(), dino.isOrderedToSit());
        data.entries.put(e.dino(), e);
        data.setDirty();
    }

    /** Drops the animal from the list (it died or stopped being tamed). */
    public static void remove(DinosaurEntity dino) {
        MinecraftServer server = dino.getServer();
        if (server != null && !dino.level().isClientSide()) {
            get(server).forget(dino.getUUID());
        }
    }

    public void forget(UUID dino) {
        if (this.entries.remove(dino) != null) {
            this.setDirty();
        }
    }

    /** The line of this animal, or null. */
    public Entry entry(UUID dino) {
        return this.entries.get(dino);
    }

    /** The owner's tamed animals, in the order they were first listed. */
    public List<Entry> of(UUID owner) {
        List<Entry> out = new ArrayList<>();
        for (Entry e : this.entries.values()) {
            if (e.owner().equals(owner)) {
                out.add(e);
            }
        }
        return out;
    }
}
