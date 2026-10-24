package com.terrassic.research;

import com.terrassic.network.NbtDelta;
import com.terrassic.network.NetworkRegression;
import io.netty.buffer.Unpooled;
import net.minecraft.SharedConstants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.ConnectionProtocol;
import net.minecraft.network.protocol.PacketFlow;
import net.minecraft.util.datafix.DataFixers;
import net.minecraft.world.level.storage.DimensionDataStorage;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Random;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

/** Executable regressions using the production classes and real NBT files; never runs in a shipped mod. */
public final class ResearchRegression {
    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void main(String[] args) throws Exception {
        SharedConstants.tryDetectVersion();
        if (args.length == 1 && args[0].equals("--protocol-dump")) {
            for (ConnectionProtocol protocol : ConnectionProtocol.values()) {
                for (PacketFlow flow : PacketFlow.values()) {
                    protocol.getPacketsByIds(flow).forEach((id, type) ->
                            System.out.println("PROTOCOL " + protocol.name() + " " + flow.name() + " " + id + " " + type.getSimpleName()));
                }
            }
            return;
        }
        knowledgeRoundTrip();
        individualStorage();
        deltaRoundTrip();
        NetworkRegression.run();
        System.out.println("PASS: knowledge mutation tracking, UUID isolation/migration/reload, 1000 NBT delta round trips");
    }

    private static Knowledge fixture(String species, String page) {
        Knowledge k = new Knowledge();
        k.raiseLevel(species, Knowledge.STUDIED);
        k.addPoints(species, 7);
        k.addPage(page);
        k.completeObjective(Objective.FIRST_FOSSIL);
        k.increment("fossils");
        k.setIntroSeen(true);
        return k;
    }

    private static void knowledgeRoundTrip() {
        Knowledge k = fixture("tyrannosaurus", "page_a");
        k.addPoints("unseen_species", 2);
        require(k.save().equals(Knowledge.load(k.save()).save()), "knowledge NBT must round-trip exactly");
        require(Knowledge.load(k.save()).points("unseen_species") == 2
                        && Knowledge.load(k.save()).level("unseen_species") == Knowledge.UNKNOWN,
                "research points collected before a sighting must survive reload");
        AtomicInteger changes = new AtomicInteger();
        k.onChange(changes::incrementAndGet);
        k.raiseLevel("tyrannosaurus", Knowledge.STUDIED);
        k.addPoints("tyrannosaurus", 0);
        k.addPage("page_a");
        k.completeObjective(Objective.FIRST_FOSSIL);
        k.setIntroSeen(true);
        require(changes.get() == 0, "no-op mutations must not dirty a player's file");
        k.raiseLevel("tyrannosaurus", Knowledge.TAMED);
        k.addPoints("tyrannosaurus", 1);
        k.addPage("page_b");
        k.completeObjective(Objective.FIRST_SPEAR);
        k.increment("fossils");
        k.setIntroSeen(false);
        require(changes.get() == 6, "every mutation path must notify storage");
        try {
            k.pages().add("untracked_page");
            throw new AssertionError("page views must not allow untracked mutations");
        } catch (UnsupportedOperationException expected) {
            // Mutations go through addPage, which marks the owning record dirty.
        }
        k.addPoints("tyrannosaurus", Integer.MAX_VALUE);
        require(k.points("tyrannosaurus") == 99, "point addition must not overflow");
        CompoundTag bad = k.save();
        bad.getCompound("Species").getCompound("tyrannosaurus").putInt("Level", 999);
        bad.getCompound("Species").getCompound("tyrannosaurus").putInt("Points", 999);
        bad.getCompound("Counters").putInt("fossils", Integer.MAX_VALUE);
        Knowledge loaded = Knowledge.load(bad);
        require(loaded.level("tyrannosaurus") == Knowledge.TAMED && loaded.points("tyrannosaurus") == 99,
                "out-of-range loaded values must be bounded");
        require(loaded.increment("fossils") == Integer.MAX_VALUE, "counters must saturate instead of wrapping negative");
    }

    private static DimensionDataStorage storage(Path path) {
        return new DimensionDataStorage(path.toFile(), DataFixers.getDataFixer());
    }

    private static void individualStorage() throws Exception {
        Path directory = Files.createTempDirectory("terrassic-research-");
        try {
            UUID alice = UUID.fromString("00000000-0000-4000-8000-000000000001");
            UUID bob = UUID.fromString("00000000-0000-4000-8000-000000000002");
            UUID newcomer = UUID.fromString("00000000-0000-4000-8000-000000000003");
            Knowledge oldAlice = fixture("tyrannosaurus", "page_a");
            Knowledge oldBob = fixture("triceratops", "page_b");
            CompoundTag players = new CompoundTag();
            players.put(alice.toString(), oldAlice.save());
            players.put(bob.toString(), oldBob.save());
            CompoundTag archive = new CompoundTag();
            CompoundTag data = new CompoundTag();
            data.put("Players", players);
            archive.put("data", data);
            archive.putInt("DataVersion", SharedConstants.getCurrentVersion().getDataVersion().getVersion());
            Path legacy = directory.resolve("terrassic_research.dat");
            NbtIo.writeCompressed(archive, legacy.toFile());
            byte[] legacyBytes = Files.readAllBytes(legacy);

            DimensionDataStorage first = storage(directory);
            ResearchData research = ResearchData.open(first);
            Knowledge aliceData = research.of(alice);
            require(aliceData.save().equals(oldAlice.save()), "Alice's legacy state must migrate");
            first.save();
            Path aliceFile = directory.resolve("terrassic_research_" + alice + ".dat");
            Path bobFile = directory.resolve("terrassic_research_" + bob + ".dat");
            require(Files.exists(aliceFile) && !Files.exists(bobFile), "migration must be lazy per UUID");
            Knowledge bobData = research.of(bob);
            require(bobData.save().equals(oldBob.save()), "Bob must import his own record");
            require(research.of(newcomer).countAtLeast(Knowledge.SILHOUETTE) == 0, "new UUID must not inherit another notebook");
            first.save();
            byte[] bobBytes = Files.readAllBytes(bobFile);
            FileTime untouched = FileTime.fromMillis(946684800000L);
            Files.setLastModifiedTime(bobFile, untouched);
            aliceData.raiseLevel("tyrannosaurus", Knowledge.TAMED);
            aliceData.increment("fossils");
            first.save();
            require(Files.getLastModifiedTime(bobFile).equals(untouched), "Alice's progress must not rewrite Bob's file");
            require(Arrays.equals(bobBytes, Files.readAllBytes(bobFile)), "Bob's saved data must be unchanged");
            require(Arrays.equals(legacyBytes, Files.readAllBytes(legacy)), "migration must preserve the original archive byte for byte");

            DimensionDataStorage reopened = storage(directory);
            ResearchData reloaded = ResearchData.open(reopened);
            require(reloaded.of(alice).save().equals(aliceData.save()), "individual file must win over stale legacy data on restart");
            require(reloaded.of(bob).save().equals(oldBob.save()), "Bob must survive reopening independently");
            reloaded.of(bob).addPage("page_c");
            reopened.save();
            require(ResearchData.open(storage(directory)).of(bob).pages().contains("page_c"), "loaded records must keep dirty tracking");
        } finally {
            try (var paths = Files.walk(directory)) {
                for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) {
                    Files.deleteIfExists(path);
                }
            }
        }
    }

    private static int wireSize(CompoundTag tag) {
        FriendlyByteBuf buffer = new FriendlyByteBuf(Unpooled.buffer());
        try {
            buffer.writeNbt(tag);
            return buffer.readableBytes();
        } finally {
            buffer.release();
        }
    }

    private static CompoundTag randomTag(Random random, int depth) {
        CompoundTag tag = new CompoundTag();
        for (int i = 0; i < random.nextInt(8); i++) {
            String key = "key_" + random.nextInt(10);
            switch (random.nextInt(depth > 0 ? 6 : 5)) {
                case 0 -> tag.putInt(key, random.nextInt());
                case 1 -> tag.putString(key, "value_" + random.nextInt(100));
                case 2 -> tag.putIntArray(key, new int[]{random.nextInt(), random.nextInt()});
                case 3 -> {
                    ListTag list = new ListTag();
                    list.add(StringTag.valueOf("page_" + random.nextInt(10)));
                    tag.put(key, list);
                }
                case 4 -> tag.putBoolean(key, random.nextBoolean());
                case 5 -> tag.put(key, randomTag(random, depth - 1));
            }
        }
        return tag;
    }

    private static void deltaRoundTrip() {
        Random random = new Random(20261024L);
        for (int i = 0; i < 1000; i++) {
            CompoundTag before = randomTag(random, 3);
            CompoundTag after = randomTag(random, 3);
            CompoundTag backup = before.copy();
            CompoundTag patch = NbtDelta.between(before, after);
            if (i < 100) {
                FriendlyByteBuf wire = new FriendlyByteBuf(Unpooled.buffer());
                try {
                    wire.writeNbt(patch);
                    CompoundTag decoded = wire.readNbt();
                    require(decoded != null && NbtDelta.apply(before, decoded).equals(after) && wire.readableBytes() == 0,
                            "patches must survive the actual FriendlyByteBuf NBT codec");
                } finally {
                    wire.release();
                }
            }
            CompoundTag restored = NbtDelta.apply(before, patch);
            require(after.equals(restored), "delta must handle nested edits, removals, lists, arrays and type changes");
            require(before.equals(backup), "applying a patch must not mutate the old snapshot");
            require(NbtDelta.between(after, after).isEmpty(), "unchanged snapshots must produce no packet");
            restored.putString("mutated_copy", "independent");
            require(!after.contains("mutated_copy") && !before.contains("mutated_copy"), "patch results must not alias snapshots");
        }
        Knowledge full = new Knowledge();
        for (int i = 0; i < 53; i++) {
            full.raiseLevel("species_" + i, Knowledge.STUDIED);
            full.addPoints("species_" + i, 10);
        }
        CompoundTag before = full.save();
        full.increment("thatch_placed");
        CompoundTag patch = NbtDelta.between(before, full.save());
        int deltaBytes = wireSize(patch);
        int fullBytes = wireSize(full.save());
        require(deltaBytes * 10 < fullBytes, "a counter update must be substantially smaller than the full notebook");
        System.out.println("NBT wire fixture (53 species, one counter change): full=" + fullBytes + " B, delta=" + deltaBytes + " B");
    }
}
