package com.terrassic.entity;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.terrassic.Terrassic;
import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import com.terrassic.research.Research;
import dev.architectury.event.events.common.CommandRegistrationEvent;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * The alphas (docs/ALFAS.md, approved by Rodrigo on 01/11/2026): a rare animal of the species, much bigger and
 * stronger, born at 80-100% of the "Max wild level" rule, with its own coat per sex. Same model and animations as
 * the species; only the textures {@code <id>_alpha_male.png} / {@code <id>_alpha_female.png} are its own.
 * <p>
 * Where they come from: a wild adult that spawns naturally far from the world spawn has the "Alpha chance" rule of
 * being one, if its species has an alpha ({@link #SPECIES}), no other alpha of the species lives within
 * {@link #REGION} blocks, the region is not resting after the last one fell, and the world has fewer than the
 * "Alphas in the world" rule. Never from an egg or a mating (the alpha x alpha baby comes with the new breeding).
 * <p>
 * The register ({@link Data}, data/terrassic_alphas.dat) keeps the wild alphas (refreshed while they are loaded),
 * the resting regions and who owns which tamed alpha (the "Tamed alphas per player" rule).
 */
public final class Alphas {
    /** Species that have an alpha: their two alpha coats exist. Add one here when its coats are made and approved. */
    public static final Set<String> SPECIES = Set.of("tyrannosaurus");
    /** No two wild alphas of a species within this many blocks; also the size of a resting region. */
    public static final double REGION = 1024.0D;
    /** A region rests this long (game ticks: 7 days) after its alpha died or was tamed. */
    public static final long REST_TICKS = 7L * 24000L;
    /** A wild alpha not seen loaded for this long (3 days) no longer counts toward the world limit. */
    public static final long STALE_TICKS = 3L * 24000L;
    /** Lowest level of an alpha, as a share of the "Max wild level" rule (Rodrigo: "80 a 100"). */
    public static final double LEVEL_FLOOR = 0.8D;
    /** The wild alpha's own health bonus on top of level and size (lost once tamed). */
    public static final float WILD_HEALTH_BONUS = 0.25F;
    /** Each player beyond the first fighting near a wild alpha adds this much health, up to {@link #MAX_EXTRA_PLAYERS}. */
    public static final float PER_PLAYER_HEALTH = 0.25F;
    public static final int MAX_EXTRA_PLAYERS = 4;
    /** Knockout (Rodrigo: "dificuldade para torpor ... mais difícil"): torpor gauge, narcotics, food. */
    public static final float TORPOR_GAUGE = 4.0F;
    public static final float NARCOTIC_EFFECT = 0.5F;
    public static final float FOOD_GOAL = 3.0F;
    public static final float AWAKE_RECOVERY = 1.0F;
    /** Seconds an alpha stays down from a full gauge (it wakes at a quarter); effectiveness lost per wound. */
    public static final float KO_SECONDS = 60.0F;
    public static final float WAKE_SHARE = 0.25F;
    public static final int WOUND_EFFECTIVENESS = 20;

    private Alphas() {
    }

    public static void init() {
        CommandRegistrationEvent.EVENT.register(Alphas::commands);
    }

    public static boolean hasAlpha(String species) {
        return SPECIES.contains(species);
    }

    /** The alpha's adult size relative to the species' standard: its own band per species. T. rex 1.45-1.55, about
     *  19 m, one and a half times the biggest common one (Rodrigo 02/11 after the first test: "ainda maior"; it was
     *  1.25-1.30). The Rift Tyrant (1.65) stays the biggest T. rex. */
    public static float size(String species, RandomSource random) {
        float lo;
        float hi;
        switch (species) {
            case "tyrannosaurus" -> {
                lo = 1.45F;
                hi = 1.55F;
            }
            default -> {
                lo = 1.25F;
                hi = 1.30F;
            }
        }
        return lo + (hi - lo) * random.nextFloat();
    }

    /** The aura's motes (client/AlphaAura): {colour when it leaves the hide, colour as it fades}, RGB, per sex. */
    public static int[] auraColors(String species, boolean female) {
        return switch (species) {
            // the white male sheds pale ash that greys as it rises; the red female throws embers that cool to soot
            case "tyrannosaurus" -> female ? new int[]{0xFF7A2A, 0x4A1510} : new int[]{0xF2EFE8, 0x8A857C};
            default -> female ? new int[]{0xE0C090, 0x6A5A40} : new int[]{0xE8E4DA, 0x7A766E};
        };
    }

    /** Whether the aura's glowing sparks are flames (a red or orange coat) rather than pale end-rod light. */
    public static boolean auraGlowsWarm(int color) {
        int r = color >> 16 & 255;
        int b = color & 255;
        return r - b > 80;
    }

    /** The level band of a new alpha: 80-100% of the "Max wild level" rule (no "levels by distance" cap). */
    public static int[] levelBand(ServerLevel level) {
        int max = Math.max(1, (int) Math.round(Rules.of(level).get(Rule.MAX_WILD_LEVEL)));
        return new int[]{Math.max(1, (int) Math.round(max * LEVEL_FLOOR)), max};
    }

    // ------------------------------------------------------------------ birth

    /** Called from {@link DinosaurEntity#finalizeSpawn}: rolls whether this new wild adult is an alpha. */
    static boolean rollAtSpawn(DinosaurEntity dino, ServerLevel level, MobSpawnType reason) {
        if ((reason != MobSpawnType.NATURAL && reason != MobSpawnType.CHUNK_GENERATION) || dino.isBaby() || dino.isTame()
                || !hasAlpha(dino.speciesId())) {
            return false;
        }
        Rules rules = Rules.of(level);
        if (dino.getRandom().nextDouble() * 100.0D >= rules.get(Rule.ALPHA_CHANCE)) {
            return false;
        }
        BlockPos spawn = level.getSharedSpawnPos();
        double fromSpawn = Math.sqrt(Mth.square(dino.getX() - spawn.getX()) + Mth.square(dino.getZ() - spawn.getZ()));
        if (fromSpawn < rules.get(Rule.ALPHA_DISTANCE)) {
            return false;
        }
        Data data = Data.get(level.getServer());
        long now = level.getServer().overworld().getGameTime();
        String dim = level.dimension().location().toString();
        return data.liveWild(now) < (int) Math.round(rules.get(Rule.ALPHA_WORLD_CAP))
                && !data.alphaNear(dino.speciesId(), dim, dino.getX(), dino.getZ(), now)
                && !data.resting(dino.speciesId(), dim, dino.getX(), dino.getZ(), now);
    }

    /** A wild alpha is alive here (spawned, or loaded again): refresh its place in the register. */
    static void seen(DinosaurEntity dino) {
        if (dino.level() instanceof ServerLevel level && !dino.isTame()) {
            Data.get(level.getServer()).seen(dino.getUUID(), dino.speciesId(), level.dimension().location().toString(),
                    dino.getX(), dino.getZ(), level.getServer().overworld().getGameTime());
        }
    }

    /** It died or was tamed: the region rests, and its owner's slot is freed if it was tame and died. */
    static void gone(DinosaurEntity dino, boolean wasWild, boolean died) {
        if (!(dino.level() instanceof ServerLevel level)) {
            return;
        }
        Data data = Data.get(level.getServer());
        long now = level.getServer().overworld().getGameTime();
        data.forget(dino.getUUID());
        if (wasWild) {
            data.rest(dino.speciesId(), level.dimension().location().toString(), dino.getX(), dino.getZ(), now + REST_TICKS);
        }
        if (died && dino.getOwnerUUID() != null) {
            data.untame(dino.getOwnerUUID(), dino.getUUID());
        }
    }

    /** Whether the player may own one more alpha of the species (the "Tamed alphas per player" rule). */
    static boolean mayOwnAnother(Player player, String species) {
        if (!(player.level() instanceof ServerLevel level)) {
            return true;
        }
        int limit = (int) Math.round(Rules.of(level).get(Rule.ALPHA_TAMED_LIMIT));
        return limit <= 0 || Data.get(level.getServer()).owned(level.getServer(), player.getUUID(), species) < limit;
    }

    static void tamed(Player player, DinosaurEntity dino) {
        if (player.level() instanceof ServerLevel level) {
            Data.get(level.getServer()).own(player.getUUID(), dino.getUUID(), dino.speciesId());
        }
        if (player instanceof ServerPlayer server) {
            Research.award(server, "journal/borrowed_crown");
        }
    }

    // ------------------------------------------------------------------ the spoils

    /** The coat of each sex of a species with alpha spoils (tools/spritegen/alfa_trofeus.py): Marfim and Brasa. */
    private static final Map<String, String[]> COATS = Map.of("tyrannosaurus", new String[]{"ivory", "ember"});
    /** Rugs of its hide: two, one rug two blocks long. */
    private static final int RUGS = 2;

    /** Server, on death: an alpha leaves rugs of its own hide and, if it died wild, its skull on its hide (the
     *  trophy); the one who brought it down gets "Dethroned". They drop on the ground beside the carcass, out of the
     *  body and out of its loot (a scavenger's bite would eat them with its share), and last 10 minutes. */
    static void spoils(DinosaurEntity dino, DamageSource source) {
        if (!(dino.level() instanceof ServerLevel level)) {
            return;
        }
        String[] coats = COATS.get(dino.speciesId());
        boolean wild = !dino.isTame();
        if (coats != null && level.getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT)) {
            String coat = coats[dino.isFemale() ? 1 : 0];
            Vec3 at = beside(dino);
            drop(dino, at, dino.speciesId() + "_" + coat + "_hide_rug", RUGS);
            if (wild) {
                drop(dino, at, dino.speciesId() + "_" + coat + "_trophy", 1);
            }
        }
        if (wild) {
            Entity by = source.getEntity();
            ServerPlayer player = by instanceof ServerPlayer p ? p
                    : by instanceof DinosaurEntity tame && tame.getOwner() instanceof ServerPlayer owner ? owner
                    : dino.getLastHurtByMob() instanceof ServerPlayer last ? last : null;
            if (player != null) {
                Research.award(player, "journal/dethroned");
            }
        }
    }

    /** A free spot beside the body: off its back (it falls with its back to its left), past its legs if a tree or a
     *  slope is in the way, where it fell if both are. Distances from its height, which grows with it. */
    private static Vec3 beside(DinosaurEntity dino) {
        float yaw = dino.yBodyRot * Mth.DEG_TO_RAD;
        Vec3 left = new Vec3(Mth.cos(yaw), 0.0D, Mth.sin(yaw));
        Vec3 feet = dino.position().add(0.0D, 0.5D, 0.0D);
        for (double off : new double[]{0.7D, -0.85D}) {
            Vec3 at = feet.add(left.scale(off * dino.getBbHeight()));
            if (dino.level().noCollision(new AABB(at, at).inflate(0.5D))) {
                return at;
            }
        }
        return feet;
    }

    private static void drop(DinosaurEntity dino, Vec3 at, String id, int count) {
        Item item = BuiltInRegistries.ITEM.get(Terrassic.id(id));
        if (item == Items.AIR) {
            return;
        }
        ItemEntity entity = new ItemEntity(dino.level(), at.x, at.y, at.z, new ItemStack(item, count));
        entity.setDefaultPickUpDelay();
        entity.setExtendedLifetime();
        dino.level().addFreshEntity(entity);
    }

    /** The "Announce fallen alphas" rule: one line in the server chat. */
    static void announce(DinosaurEntity dino, String what, Entity by) {
        if (dino.level() instanceof ServerLevel level && Rules.of(level).get(Rule.ALPHA_ANNOUNCE) >= 0.5D) {
            Component line = by != null
                    ? Component.translatable("message.terrassic.alpha." + what, dino.getDisplayName(), by.getDisplayName())
                    : Component.translatable("message.terrassic.alpha." + what + "_alone", dino.getDisplayName());
            level.getServer().getPlayerList().broadcastSystemMessage(line, false);
        }
    }

    // ------------------------------------------------------------------ command

    /** {@code /terrassic alfa <species> [macho|femea]} (alpha, male/female; hembra): an alpha where the command runs
     *  (operators only), for tests and server events. It ignores chance, distance and the limits. */
    private static void commands(CommandDispatcher<CommandSourceStack> dispatcher, CommandBuildContext ctx,
                                 Commands.CommandSelection selection) {
        for (String name : List.of("alfa", "alpha")) {
            dispatcher.register(Commands.literal("terrassic").then(Commands.literal(name).requires(s -> s.hasPermission(2))
                    .then(Commands.argument("especie", StringArgumentType.word())
                            .suggests((c, b) -> SharedSuggestionProvider.suggest(SPECIES, b))
                            .executes(c -> summon(c.getSource(), StringArgumentType.getString(c, "especie"), null))
                            .then(Commands.argument("sexo", StringArgumentType.word())
                                    .suggests((c, b) -> SharedSuggestionProvider.suggest(
                                            new String[]{"macho", "femea", "male", "female", "hembra"}, b))
                                    .executes(c -> summon(c.getSource(), StringArgumentType.getString(c, "especie"),
                                            StringArgumentType.getString(c, "sexo")))))));
        }
    }

    private static int summon(CommandSourceStack src, String species, String sex) {
        species = species.toLowerCase(Locale.ROOT);
        if (!hasAlpha(species)) {
            src.sendFailure(Component.translatable("command.terrassic.alpha.unknown", species, String.join(", ", SPECIES)));
            return 0;
        }
        Boolean female = null;
        if (sex != null) {
            switch (sex.toLowerCase(Locale.ROOT)) {
                case "macho", "male" -> female = false;
                case "femea", "fêmea", "female", "hembra" -> female = true;
                default -> {
                    src.sendFailure(Component.translatable("command.terrassic.alpha.sex", sex));
                    return 0;
                }
            }
        }
        EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(Terrassic.id(species));
        ServerLevel level = src.getLevel();
        Entity e = type.create(level);
        if (!(e instanceof DinosaurEntity dino)) {
            src.sendFailure(Component.translatable("command.terrassic.alpha.unknown", species, String.join(", ", SPECIES)));
            return 0;
        }
        Vec3 at = src.getPosition();
        dino.moveTo(at.x, at.y, at.z, src.getRotation().y, 0.0F);
        dino.finalizeSpawn(level, level.getCurrentDifficultyAt(BlockPos.containing(at)), MobSpawnType.COMMAND, null, null);
        dino.becomeAlpha(female);
        level.addFreshEntity(dino);
        src.sendSuccess(() -> Component.translatable("command.terrassic.alpha.summoned", dino.getDisplayName()), true);
        return 1;
    }

    // ------------------------------------------------------------------ the register

    /** data/terrassic_alphas.dat of the overworld: wild alphas, resting regions, owners of tamed alphas. */
    public static final class Data extends SavedData {
        private static final String NAME = "terrassic_alphas";

        private record Wild(String species, String dim, double x, double z, long seen) {
        }

        private record Rest(String species, String dim, double x, double z, long until) {
        }

        private final Map<UUID, Wild> wild = new HashMap<>();
        private final List<Rest> resting = new ArrayList<>();
        /** owner -> (alpha -> species) */
        private final Map<UUID, Map<UUID, String>> owners = new HashMap<>();

        public static Data get(MinecraftServer server) {
            return server.overworld().getDataStorage().computeIfAbsent(Data::load, Data::new, NAME);
        }

        int liveWild(long now) {
            int n = 0;
            for (Wild w : this.wild.values()) {
                if (now - w.seen() < STALE_TICKS) {
                    n++;
                }
            }
            return n;
        }

        boolean alphaNear(String species, String dim, double x, double z, long now) {
            for (Wild w : this.wild.values()) {
                if (w.species().equals(species) && w.dim().equals(dim) && now - w.seen() < STALE_TICKS
                        && Mth.square(w.x() - x) + Mth.square(w.z() - z) < REGION * REGION) {
                    return true;
                }
            }
            return false;
        }

        boolean resting(String species, String dim, double x, double z, long now) {
            boolean changed = this.resting.removeIf(r -> r.until() <= now);
            if (changed) {
                this.setDirty();
            }
            for (Rest r : this.resting) {
                if (r.species().equals(species) && r.dim().equals(dim)
                        && Mth.square(r.x() - x) + Mth.square(r.z() - z) < REGION * REGION) {
                    return true;
                }
            }
            return false;
        }

        void seen(UUID id, String species, String dim, double x, double z, long now) {
            this.wild.put(id, new Wild(species, dim, x, z, now));
            this.setDirty();
        }

        void forget(UUID id) {
            if (this.wild.remove(id) != null) {
                this.setDirty();
            }
        }

        void rest(String species, String dim, double x, double z, long until) {
            this.resting.add(new Rest(species, dim, x, z, until));
            this.setDirty();
        }

        void own(UUID owner, UUID alpha, String species) {
            this.owners.computeIfAbsent(owner, k -> new HashMap<>()).put(alpha, species);
            this.setDirty();
        }

        void untame(UUID owner, UUID alpha) {
            Map<UUID, String> mine = this.owners.get(owner);
            if (mine != null && mine.remove(alpha) != null) {
                this.setDirty();
            }
        }

        /** Alphas of the species the player owns. One that is loaded and no longer theirs (or no longer alive, or no
         *  longer an alpha) frees its slot; one in an unloaded chunk still counts. */
        int owned(MinecraftServer server, UUID owner, String species) {
            Map<UUID, String> mine = this.owners.get(owner);
            if (mine == null) {
                return 0;
            }
            int n = 0;
            for (Iterator<Map.Entry<UUID, String>> it = mine.entrySet().iterator(); it.hasNext(); ) {
                Map.Entry<UUID, String> e = it.next();
                if (!e.getValue().equals(species)) {
                    continue;
                }
                Entity found = null;
                for (ServerLevel level : server.getAllLevels()) {
                    found = level.getEntity(e.getKey());
                    if (found != null) {
                        break;
                    }
                }
                if (found != null && !(found instanceof DinosaurEntity d && d.isAlive() && d.isAlpha() && owner.equals(d.getOwnerUUID()))) {
                    it.remove();
                    this.setDirty();
                    continue;
                }
                n++;
            }
            return n;
        }

        private static Data load(CompoundTag tag) {
            Data data = new Data();
            for (Tag t : tag.getList("Wild", Tag.TAG_COMPOUND)) {
                CompoundTag w = (CompoundTag) t;
                if (w.hasUUID("Id")) {
                    data.wild.put(w.getUUID("Id"), new Wild(w.getString("Species"), w.getString("Dim"), w.getDouble("X"),
                            w.getDouble("Z"), w.getLong("Seen")));
                }
            }
            for (Tag t : tag.getList("Resting", Tag.TAG_COMPOUND)) {
                CompoundTag r = (CompoundTag) t;
                data.resting.add(new Rest(r.getString("Species"), r.getString("Dim"), r.getDouble("X"), r.getDouble("Z"),
                        r.getLong("Until")));
            }
            for (Tag t : tag.getList("Owners", Tag.TAG_COMPOUND)) {
                CompoundTag o = (CompoundTag) t;
                if (o.hasUUID("Owner") && o.hasUUID("Alpha")) {
                    data.owners.computeIfAbsent(o.getUUID("Owner"), k -> new HashMap<>()).put(o.getUUID("Alpha"),
                            o.getString("Species"));
                }
            }
            return data;
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            ListTag wildList = new ListTag();
            this.wild.forEach((id, w) -> {
                CompoundTag t = new CompoundTag();
                t.putUUID("Id", id);
                t.putString("Species", w.species());
                t.putString("Dim", w.dim());
                t.putDouble("X", w.x());
                t.putDouble("Z", w.z());
                t.putLong("Seen", w.seen());
                wildList.add(t);
            });
            tag.put("Wild", wildList);
            ListTag restList = new ListTag();
            for (Rest r : this.resting) {
                CompoundTag t = new CompoundTag();
                t.putString("Species", r.species());
                t.putString("Dim", r.dim());
                t.putDouble("X", r.x());
                t.putDouble("Z", r.z());
                t.putLong("Until", r.until());
                restList.add(t);
            }
            tag.put("Resting", restList);
            ListTag ownerList = new ListTag();
            this.owners.forEach((owner, mine) -> mine.forEach((alpha, species) -> {
                CompoundTag t = new CompoundTag();
                t.putUUID("Owner", owner);
                t.putUUID("Alpha", alpha);
                t.putString("Species", species);
                ownerList.add(t);
            }));
            tag.put("Owners", ownerList);
            return tag;
        }
    }
}
