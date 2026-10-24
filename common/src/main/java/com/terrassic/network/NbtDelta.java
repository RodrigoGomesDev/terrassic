package com.terrassic.network;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;

/** Lossless compound patches: lists/arrays are replaced, compounds recurse, and removals are explicit. */
public final class NbtDelta {
    private NbtDelta() {
    }

    public static CompoundTag between(CompoundTag previous, CompoundTag current) {
        CompoundTag values = new CompoundTag();
        CompoundTag compounds = new CompoundTag();
        ListTag removed = new ListTag();
        for (String key : current.getAllKeys()) {
            Tag next = current.get(key);
            Tag before = previous.get(key);
            if (next.equals(before)) {
                continue;
            }
            if (next instanceof CompoundTag nextCompound && before instanceof CompoundTag beforeCompound) {
                compounds.put(key, between(beforeCompound, nextCompound));
            } else {
                values.put(key, next.copy());
            }
        }
        for (String key : previous.getAllKeys()) {
            if (!current.contains(key)) {
                removed.add(StringTag.valueOf(key));
            }
        }
        CompoundTag patch = new CompoundTag();
        if (!values.isEmpty()) {
            patch.put("Values", values);
        }
        if (!compounds.isEmpty()) {
            patch.put("Compounds", compounds);
        }
        if (!removed.isEmpty()) {
            patch.put("Removed", removed);
        }
        return patch;
    }

    /** Returns a copy; neither the input snapshot nor the patch is mutated/aliased. */
    public static CompoundTag apply(CompoundTag snapshot, CompoundTag patch) {
        CompoundTag result = snapshot.copy();
        for (Tag key : patch.getList("Removed", Tag.TAG_STRING)) {
            result.remove(key.getAsString());
        }
        CompoundTag values = patch.getCompound("Values");
        for (String key : values.getAllKeys()) {
            result.put(key, values.get(key).copy());
        }
        CompoundTag compounds = patch.getCompound("Compounds");
        for (String key : compounds.getAllKeys()) {
            result.put(key, apply(result.getCompound(key), compounds.getCompound(key)));
        }
        return result;
    }
}
