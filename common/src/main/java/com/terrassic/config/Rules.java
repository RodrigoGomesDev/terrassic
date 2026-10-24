package com.terrassic.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.platform.Platform;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * The world rules in the style of ARK's server settings (docs/REGRAS.md): one value per {@link Rule}, saved with the
 * world ({@link RulesData}) and edited in the Rules screen. A new world starts from the defaults kept in the
 * "rules" object of config/terrassic-world.json (the Rules screen on the title screen edits that file).
 *
 * <p>Game code asks {@link #of(Level)} for the rules of the world it runs in; on the client (and before a server is
 * up) that is the default set. The static helpers below turn the values into what the creatures need.
 */
public final class Rules {
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final String FILE = Terrassic.MOD_ID + "-world.json";
    private static final Rules DEFAULTS = new Rules();

    /** The rules of the running server's world, loaded on first use (one server at a time). */
    private static MinecraftServer server;
    private static Rules current;

    private final double[] values = new double[Rule.values().length];

    public Rules() {
        for (Rule r : Rule.values()) {
            this.values[r.ordinal()] = r.defaultValue;
        }
    }

    public double get(Rule rule) {
        return this.values[rule.ordinal()];
    }

    public void set(Rule rule, double value) {
        this.values[rule.ordinal()] = rule.clamp(value);
    }

    public Rules copy() {
        Rules r = new Rules();
        System.arraycopy(this.values, 0, r.values, 0, this.values.length);
        return r;
    }

    public void copyFrom(Rules other) {
        System.arraycopy(other.values, 0, this.values, 0, this.values.length);
    }

    // ------------------------------------------------------------------ save / load

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        for (Rule r : Rule.values()) {
            tag.putDouble(r.key, this.get(r));
        }
        return tag;
    }

    /** Reads the values present in the tag; missing ones (rules added in a later version) keep their default. */
    public static Rules load(CompoundTag tag) {
        Rules rules = new Rules();
        for (Rule r : Rule.values()) {
            if (tag.contains(r.key)) {
                rules.set(r, tag.getDouble(r.key));
            }
        }
        return rules;
    }

    public JsonObject toJson() {
        JsonObject json = new JsonObject();
        for (Rule r : Rule.values()) {
            json.addProperty(r.key, this.get(r));
        }
        return json;
    }

    public static Rules fromJson(JsonObject json) {
        Rules rules = new Rules();
        if (json != null) {
            for (Rule r : Rule.values()) {
                JsonElement e = json.get(r.key);
                if (e != null && e.isJsonPrimitive() && e.getAsJsonPrimitive().isNumber()) {
                    rules.set(r, e.getAsDouble());
                }
            }
        }
        return rules;
    }

    // ------------------------------------------------------------------ defaults file (config/terrassic-world.json)

    private static Path defaultsFile() {
        return Platform.getConfigFolder().resolve(FILE);
    }

    private static JsonObject readFile() {
        Path file = defaultsFile();
        if (Files.exists(file)) {
            try (Reader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                JsonObject json = GSON.fromJson(r, JsonObject.class);
                return json != null ? json : new JsonObject();
            } catch (Exception e) {
                LOG.error("Could not read {}, using the default rules: {}", file, e.toString());
            }
        }
        return new JsonObject();
    }

    /** The default rules for new worlds; writes the "rules" object back when it is missing or incomplete. */
    public static Rules loadDefaults() {
        JsonObject root = readFile();
        JsonObject json = root.has("rules") && root.get("rules").isJsonObject() ? root.getAsJsonObject("rules") : null;
        Rules rules = fromJson(json);
        if (json == null || json.size() < Rule.values().length) {
            saveDefaults(rules);
        }
        return rules;
    }

    /** Writes the default rules into the "rules" object of the file, keeping everything else in it. */
    public static void saveDefaults(Rules rules) {
        Path file = defaultsFile();
        JsonObject root = readFile();
        root.add("rules", rules.toJson());
        try {
            Files.createDirectories(file.getParent());
            try (Writer w = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
                GSON.toJson(root, w);
            }
        } catch (IOException e) {
            LOG.warn("Could not write {}: {}", file, e.toString());
        }
    }

    // ------------------------------------------------------------------ the running world

    public static void init() {
        // read the world's rules on the main thread as soon as the overworld exists, before chunk generation
        // (which can run on worker threads) spawns its first herds
        LifecycleEvent.SERVER_LEVEL_LOAD.register(level -> {
            if (level.dimension() == Level.OVERWORLD) {
                of(level.getServer());
            }
        });
        LifecycleEvent.SERVER_STOPPED.register(s -> {
            server = null;
            current = null;
        });
    }

    /** The rules of the world this level belongs to (the defaults on the client side). */
    public static Rules of(Level level) {
        if (level instanceof ServerLevel serverLevel) {
            return of(serverLevel.getServer());
        }
        return DEFAULTS;
    }

    public static synchronized Rules of(MinecraftServer s) {
        if (s == null) {
            return DEFAULTS;
        }
        if (s != server || current == null) {
            server = s;
            current = RulesData.get(s).rules();
        }
        return current;
    }

    /** Replaces the rules of the running world and saves them with it. */
    public static synchronized void apply(MinecraftServer s, Rules rules) {
        RulesData data = RulesData.get(s);
        data.rules().copyFrom(rules);
        data.setDirty();
        server = s;
        current = data.rules();
    }

    // ------------------------------------------------------------------ helpers for the creatures

    /** Strength of wild creatures from the difficulty level: 0 -> 0.5, 0.5 -> 1, 1 -> 1.5 (health and damage). */
    public static float wildFactor(Level level) {
        return (float) (0.5D + of(level).get(Rule.DIFFICULTY));
    }

    /**
     * Damage taken by a creature: player damage or creature damage (with the attacker's wild strength), divided by
     * the creature resistance and its own wild strength.
     */
    public static float damageTaken(DinosaurEntity victim, DamageSource source, float amount) {
        Rules rules = of(victim.level());
        Entity attacker = source.getEntity();
        double factor = 1.0D;
        if (attacker instanceof Player) {
            factor *= rules.get(Rule.PLAYER_DAMAGE);
        } else if (attacker instanceof DinosaurEntity dino) {
            factor *= rules.get(Rule.DINO_DAMAGE) * (dino.isTame() ? 1.0D : wildFactor(victim.level()));
        }
        factor /= rules.get(Rule.DINO_RESISTANCE);
        if (!victim.isTame()) {
            factor /= wildFactor(victim.level());
        }
        return (float) (amount * factor);
    }

    /** Damage a creature deals to anything that is not a creature (players, vanilla mobs). */
    public static double damageDealt(DinosaurEntity attacker, Entity target) {
        Rules rules = of(attacker.level());
        double factor = rules.get(Rule.DINO_DAMAGE) * (attacker.isTame() ? 1.0D : wildFactor(attacker.level()));
        if (target instanceof Player) {
            factor /= rules.get(Rule.PLAYER_RESISTANCE);
        }
        return factor;
    }

    /** Whether a creature breaks this block in its way (structure damage over structure resistance; 0 = never). */
    public static boolean breaksBlock(Level level, RandomSource random) {
        Rules rules = of(level);
        double chance = rules.get(Rule.STRUCTURE_DAMAGE) / rules.get(Rule.STRUCTURE_RESISTANCE);
        return chance >= 1.0D || (chance > 0.0D && random.nextDouble() < chance);
    }

    /** A rate scaled by a multiplier rule, rounded at random so fractions keep their average (3.4 -> 3 or 4). */
    public static int scaled(RandomSource random, double base, Rule rule, Level level) {
        double v = base * of(level).get(rule);
        int whole = (int) Math.floor(v);
        return whole + (random.nextDouble() < v - whole ? 1 : 0);
    }

    /** An interval (ticks) divided by a speed rule: faster speed, shorter wait; 0 = never (Integer.MAX_VALUE). */
    public static int interval(int ticks, Rule rule, Level level) {
        double speed = of(level).get(rule);
        if (speed <= 0.0D) {
            return Integer.MAX_VALUE;
        }
        return Math.max(1, (int) Math.round(ticks / speed));
    }
}
