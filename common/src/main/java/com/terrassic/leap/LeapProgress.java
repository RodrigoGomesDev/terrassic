package com.terrassic.leap;

import com.terrassic.config.WorldConfig;
import com.terrassic.research.Knowledge;
import com.terrassic.research.Objective;
import com.terrassic.research.Research;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

/**
 * Who may do what at the Leap Altar (HISTORIA.md §5, CONQUISTAS.md "Como o salto destrava"). Progress is per player:
 * the fragments come from the player's own Field Journal; beating the Rift Tyrant is saved here per player.
 * <pre>
 *   mode     ritual          leap                                   unstable leap
 *   normal   4 fragments     after beating the Rift Tyrant          2 fragments, no boss
 *   rapido   4 fragments*    with 4 fragments (boss optional)       2 fragments*
 *   livre    always          always                                 -
 *   (* in "rapido" one objective per theme already makes its fragment)
 * </pre>
 * The world's mode is saved with the world (data/terrassic_leap.dat); a new world starts with "progression_mode"
 * from config/terrassic-world.json. Operators change it with {@code /terrassic modo}.
 */
public final class LeapProgress {
    public static final int FRAGMENTS = 4;
    public static final int UNSTABLE_FRAGMENTS = 2;

    public enum Mode {
        NORMAL("normal"), FAST("rapido"), FREE("livre");

        public final String id;

        Mode(String id) {
            this.id = id;
        }

        public static Mode byId(String id) {
            String s = id == null ? "" : id.toLowerCase(Locale.ROOT);
            for (Mode m : values()) {
                if (m.id.equals(s) || m.name().toLowerCase(Locale.ROOT).equals(s)) {
                    return m;
                }
            }
            return switch (s) {
                case "rápido", "fast", "quick" -> FAST;
                case "free", "libre" -> FREE;
                default -> null;
            };
        }
    }

    private LeapProgress() {
    }

    public static Mode mode(MinecraftServer server) {
        return Data.get(server).mode();
    }

    public static void setMode(MinecraftServer server, Mode mode) {
        Data d = Data.get(server);
        d.mode = mode;
        d.setDirty();
    }

    /** Amber fragments of the player under the world's mode. */
    public static int fragments(ServerPlayer player) {
        Knowledge k = Research.knowledge(player);
        if (mode(player.server) != Mode.FAST) {
            return Objective.fragments(k);
        }
        int n = 0;
        for (Objective.Theme t : Objective.Theme.values()) {
            if (Objective.done(k, t) >= 1) {
                n++;
            }
        }
        return n;
    }

    public static boolean canStartRitual(ServerPlayer player) {
        return mode(player.server) == Mode.FREE || fragments(player) >= FRAGMENTS;
    }

    public static boolean defeatedTyrant(ServerPlayer player) {
        return Data.get(player.server).tyrant.contains(player.getUUID());
    }

    public static void markTyrant(ServerPlayer player) {
        Data d = Data.get(player.server);
        if (d.tyrant.add(player.getUUID())) {
            d.setDirty();
        }
    }

    public static boolean canLeap(ServerPlayer player) {
        return switch (mode(player.server)) {
            case FREE -> true;
            case FAST -> fragments(player) >= FRAGMENTS;
            case NORMAL -> defeatedTyrant(player);
        };
    }

    public static boolean canLeapUnstable(ServerPlayer player) {
        return !canLeap(player) && fragments(player) >= UNSTABLE_FRAGMENTS;
    }

    /** Leap state of the world, saved with the overworld. */
    static final class Data extends SavedData {
        private static final String NAME = "terrassic_leap";
        Mode mode;
        final Set<UUID> tyrant = new HashSet<>();

        static Data get(MinecraftServer server) {
            return server.overworld().getDataStorage().computeIfAbsent(Data::load, Data::new, NAME);
        }

        Mode mode() {
            if (this.mode == null) {
                Mode m = Mode.byId(WorldConfig.progressionMode());
                this.mode = m == null ? Mode.NORMAL : m;
                this.setDirty();
            }
            return this.mode;
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            if (this.mode != null) {
                tag.putString("Mode", this.mode.id);
            }
            ListTag list = new ListTag();
            for (UUID id : this.tyrant) {
                list.add(NbtUtils.createUUID(id));
            }
            tag.put("TyrantDefeated", list);
            return tag;
        }

        static Data load(CompoundTag tag) {
            Data d = new Data();
            d.mode = tag.contains("Mode") ? Mode.byId(tag.getString("Mode")) : null;
            for (Tag t : tag.getList("TyrantDefeated", Tag.TAG_INT_ARRAY)) {
                d.tyrant.add(NbtUtils.loadUUID(t));
            }
            return d;
        }
    }
}
