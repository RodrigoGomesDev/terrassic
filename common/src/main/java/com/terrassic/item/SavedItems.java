package com.terrassic.item;

import com.mojang.serialization.Dynamic;
import net.minecraft.SharedConstants;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.util.datafix.DataFixers;
import net.minecraft.util.datafix.fixes.References;
import net.minecraft.world.item.ItemStack;

/** Items saved by the mod's own fields. Minecraft's data fixers do not know those fields, so a world from the 1.20.1
 *  versions still has them in the old format there (Count, tag): they go through the fixers here, on load. */
public final class SavedItems {
    /** Minecraft 1.20.1. */
    private static final int OLD_DATA_VERSION = 3465;

    private SavedItems() {
    }

    public static ItemStack read(HolderLookup.Provider registries, CompoundTag tag) {
        return ItemStack.parseOptional(registries, upgraded(tag));
    }

    /** The same, for a whole container's item list saved under the given key, before ContainerHelper reads it. */
    public static void upgradeList(CompoundTag owner, String key) {
        ListTag list = owner.getList(key, Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            list.set(i, upgraded(list.getCompound(i)));
        }
    }

    private static CompoundTag upgraded(CompoundTag tag) {
        if (!tag.contains("Count")) {
            return tag;
        }
        int now = SharedConstants.getCurrentVersion().getDataVersion().getVersion();
        Dynamic<Tag> fixed = DataFixers.getDataFixer().update(References.ITEM_STACK, new Dynamic<>(NbtOps.INSTANCE, tag), OLD_DATA_VERSION, now);
        return fixed.getValue() instanceof CompoundTag compound ? compound : tag;
    }
}
