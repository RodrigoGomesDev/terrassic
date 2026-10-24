package com.terrassic.network;

import net.minecraft.nbt.CompoundTag;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Connection-scoped protocol state, separated from transport so rejoin and compatibility can be regressed. */
final class KnowledgeSyncState {
    record Update(boolean full, CompoundTag payload) {
    }

    private final Map<UUID, CompoundTag> sent = new HashMap<>();

    Update full(UUID player, CompoundTag snapshot) {
        this.sent.put(player, snapshot.copy());
        return new Update(true, snapshot);
    }

    Update update(UUID player, CompoundTag snapshot, boolean supportsDelta) {
        CompoundTag previous = this.sent.get(player);
        if (snapshot.equals(previous)) {
            return null;
        }
        if (previous == null || !supportsDelta) {
            return this.full(player, snapshot);
        }
        CompoundTag patch = NbtDelta.between(previous, snapshot);
        this.sent.put(player, snapshot.copy());
        return new Update(false, patch);
    }

    void forget(UUID player) {
        this.sent.remove(player);
    }

    void clear() {
        this.sent.clear();
    }
}
