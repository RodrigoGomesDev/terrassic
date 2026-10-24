package com.terrassic.network;

import com.terrassic.research.Knowledge;
import net.minecraft.nbt.CompoundTag;

import java.util.UUID;

/** Tests protocol decisions without pretending that an in-memory transport is a connected Minecraft client. */
public final class NetworkRegression {
    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void run() {
        KnowledgeSyncState state = new KnowledgeSyncState();
        UUID alice = UUID.fromString("00000000-0000-4000-8000-000000000001");
        UUID bob = UUID.fromString("00000000-0000-4000-8000-000000000002");
        Knowledge knowledge = new Knowledge();
        knowledge.raiseLevel("tyrannosaurus", Knowledge.STUDIED);
        CompoundTag snapshot = knowledge.save();
        KnowledgeSyncState.Update first = state.update(alice, snapshot, true);
        require(first.full() && first.payload().equals(snapshot), "a new connection must receive a full snapshot");
        CompoundTag clientSnapshot = first.payload().copy();
        require(state.update(alice, knowledge.save(), true) == null, "unchanged progress must not produce a packet");
        snapshot.putString("external_mutation", "not part of the stored baseline");
        require(state.update(alice, knowledge.save(), true) == null, "the baseline must not alias the caller's NBT");
        knowledge.addPage("page_a");
        KnowledgeSyncState.Update delta = state.update(alice, knowledge.save(), true);
        require(!delta.full(), "a capable client should receive only changes");
        require(NbtDelta.apply(clientSnapshot, delta.payload()).equals(knowledge.save()), "client reconstruction must match the server");
        require(state.update(bob, knowledge.save(), true).full(), "players must have independent baselines");
        state.forget(alice);
        require(state.update(alice, knowledge.save(), true).full(), "same UUID must receive full state after disconnect");
        require(state.update(bob, knowledge.save(), true) == null, "disconnecting one player must not clear another");
        knowledge.increment("fossils");
        KnowledgeSyncState.Update compatible = state.update(alice, knowledge.save(), false);
        require(compatible.full() && compatible.payload().equals(knowledge.save()), "clients without delta support keep the old full-packet protocol");
        require(state.full(alice, knowledge.save()).full(), "join must force a snapshot even if a stale baseline remains");
        state.clear();
        require(state.update(alice, knowledge.save(), true).full() && state.update(bob, knowledge.save(), true).full(),
                "a server restart must clear all connection state");
        System.out.println("PASS: initial sync, no-op suppression, client reconstruction, UUID isolation, rejoin and legacy fallback");
    }
}
