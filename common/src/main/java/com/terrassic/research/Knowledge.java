package com.terrassic.research;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;

import java.util.HashMap;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

/**
 * What one player has learned: Field Guide level and study points per species, the Katarina pages found, the
 * Field Journal objectives done and a few counters and flags. Saved per player in {@link ResearchData} (not in
 * the notebook item, so a lost notebook keeps its content) and copied to the client for the notebook screen.
 */
public class Knowledge {
    /** Field Guide levels. A species with no entry is unknown. */
    public static final int UNKNOWN = 0;
    /** A fossil of it was studied: silhouette and era. */
    public static final int SILHOUETTE = 1;
    /** Seen alive up close: name, picture, diet, size. */
    public static final int SIGHTED = 2;
    /** Enough study points: behaviour, how to tame, favourite food, weak spots. */
    public static final int STUDIED = 3;
    /** Tamed one: utility, riding and Katarina's note. */
    public static final int TAMED = 4;

    /** Study points needed (on top of a sighting) to reach {@link #STUDIED}. */
    public static final int POINTS_TO_STUDY = 3;

    private final Map<String, Integer> levels = new HashMap<>();
    private final Map<String, Integer> points = new HashMap<>();
    private final Set<String> pages = new LinkedHashSet<>();
    private final Set<String> pagesView = Collections.unmodifiableSet(this.pages);
    private final Set<String> objectives = new LinkedHashSet<>();
    private final Map<String, Integer> counters = new HashMap<>();
    private boolean introSeen;
    private Runnable onChange = () -> { };

    /** Storage attaches a dirty listener; client copies and newly loaded values have no side effects. */
    void onChange(Runnable listener) {
        this.onChange = listener;
    }

    public int level(String species) {
        return this.levels.getOrDefault(species, UNKNOWN);
    }

    public int points(String species) {
        return this.points.getOrDefault(species, 0);
    }

    /** Raises the level (never lowers it). Returns true if it changed. */
    public boolean raiseLevel(String species, int level) {
        level = Math.max(UNKNOWN, Math.min(TAMED, level));
        if (level <= this.level(species)) {
            return false;
        }
        this.levels.put(species, level);
        this.onChange.run();
        return true;
    }

    public void addPoints(String species, int amount) {
        int points = (int) Math.max(0L, Math.min(99L, (long) this.points(species) + amount));
        if (points != this.points(species)) {
            this.points.put(species, points);
            this.onChange.run();
        }
    }

    /** Number of species at or above a level. */
    public int countAtLeast(int level) {
        int n = 0;
        for (int l : this.levels.values()) {
            if (l >= level) {
                n++;
            }
        }
        return n;
    }

    public Set<String> pages() {
        return this.pagesView;
    }

    public boolean addPage(String page) {
        boolean changed = this.pages.add(page);
        if (changed) {
            this.onChange.run();
        }
        return changed;
    }

    public boolean hasObjective(Objective objective) {
        return this.objectives.contains(objective.id());
    }

    public boolean completeObjective(Objective objective) {
        boolean changed = this.objectives.add(objective.id());
        if (changed) {
            this.onChange.run();
        }
        return changed;
    }

    public int counter(String name) {
        return this.counters.getOrDefault(name, 0);
    }

    public int increment(String name) {
        int value = (int) Math.min(Integer.MAX_VALUE, (long) this.counter(name) + 1);
        if (value != this.counter(name)) {
            this.counters.put(name, value);
            this.onChange.run();
        }
        return value;
    }

    public boolean introSeen() {
        return this.introSeen;
    }

    public void setIntroSeen(boolean seen) {
        if (this.introSeen != seen) {
            this.introSeen = seen;
            this.onChange.run();
        }
    }

    // ------------------------------------------------------------------ NBT

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        CompoundTag species = new CompoundTag();
        for (Map.Entry<String, Integer> e : this.levels.entrySet()) {
            CompoundTag s = new CompoundTag();
            s.putInt("Level", e.getValue());
            s.putInt("Points", this.points(e.getKey()));
            species.put(e.getKey(), s);
        }
        for (Map.Entry<String, Integer> e : this.points.entrySet()) {
            if (!species.contains(e.getKey())) {
                CompoundTag s = new CompoundTag();
                s.putInt("Level", UNKNOWN);
                s.putInt("Points", e.getValue());
                species.put(e.getKey(), s);
            }
        }
        tag.put("Species", species);
        tag.put("Pages", strings(this.pages));
        tag.put("Objectives", strings(this.objectives));
        CompoundTag counters = new CompoundTag();
        this.counters.forEach(counters::putInt);
        tag.put("Counters", counters);
        tag.putBoolean("IntroSeen", this.introSeen);
        return tag;
    }

    public static Knowledge load(CompoundTag tag) {
        Knowledge k = new Knowledge();
        CompoundTag species = tag.getCompound("Species");
        for (String id : species.getAllKeys()) {
            CompoundTag s = species.getCompound(id);
            if (s.getInt("Level") > UNKNOWN) {
                k.levels.put(id, Math.min(TAMED, s.getInt("Level")));
            }
            if (s.getInt("Points") > 0) {
                k.points.put(id, Math.min(99, s.getInt("Points")));
            }
        }
        for (Tag t : tag.getList("Pages", Tag.TAG_STRING)) {
            k.pages.add(t.getAsString());
        }
        for (Tag t : tag.getList("Objectives", Tag.TAG_STRING)) {
            k.objectives.add(t.getAsString());
        }
        CompoundTag counters = tag.getCompound("Counters");
        for (String name : counters.getAllKeys()) {
            k.counters.put(name, Math.max(0, counters.getInt(name)));
        }
        k.introSeen = tag.getBoolean("IntroSeen");
        return k;
    }

    private static ListTag strings(Set<String> values) {
        ListTag list = new ListTag();
        for (String v : values) {
            list.add(StringTag.valueOf(v));
        }
        return list;
    }
}
