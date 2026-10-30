package com.terrassic.research;

import com.terrassic.Terrassic;
import com.terrassic.config.Eras;
import com.terrassic.config.Story;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.entity.HerbivoreDinosaur;
import com.terrassic.entity.SwimmingDinosaur;
import com.terrassic.item.SpearItem;
import com.terrassic.network.ModNetwork;
import com.terrassic.registry.ModBlocks;
import com.terrassic.item.SketchItem;
import com.terrassic.registry.ModItems;
import dev.architectury.event.EventResult;
import dev.architectury.event.events.common.BlockEvent;
import dev.architectury.event.events.common.EntityEvent;
import dev.architectury.event.events.common.PlayerEvent;
import dev.architectury.event.events.common.TickEvent;
import net.minecraft.advancements.Advancement;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayList;
import java.util.List;

/**
 * Server side of the scientist mechanics (docs/HISTORIA.md, sections 4 to 6): fills each player's
 * {@link Knowledge} from what they do, raises Field Guide levels, completes Field Journal objectives and keeps the
 * client copy in sync. Nothing here moves the player or blocks anything (rule 0): it only records.
 *
 * <ul>
 *   <li>Silhouette: study a fossil at the Research Table.</li>
 *   <li>Sighted: be within {@link #SIGHT_RANGE} blocks of one, with line of sight.</li>
 *   <li>Studied: sighted plus {@link Knowledge#POINTS_TO_STUDY} study points (fossil 1, sketch 2, defeating one 3).</li>
 *   <li>Tamed: tame or hatch one.</li>
 * </ul>
 * A studied species is easier to tame and takes more damage from that player (see DinosaurEntity).
 *
 * It also gives the advancements of docs/CONQUISTAS.md ({@link #award}). Those that follow from the Knowledge
 * (counts, objectives, fragments) are checked again on every change and when the player joins, so old worlds
 * catch up.
 * <p>
 * With the story mode off (config/Story, the default since v0.10) the Field Guide keeps working, but there is no
 * intro, no notebook on the first join, no objective and no advancement of the "Echoes of the End" tab.
 */
public final class Research {
    public static final double SIGHT_RANGE = 16.0D;
    public static final int FOSSIL_POINTS = 1;
    public static final int SKETCH_POINTS = 2;
    public static final int DEFEAT_POINTS = 3;
    public static final int SAMPLE_POINTS = 2;
    /** Tamed species for "Mixed herd" and pages for "Close reader". */
    public static final int TAMED_SPECIES = 5;
    public static final int READER_PAGES = 5;
    /** Eras from the oldest to the newest (Field Guide era ids). */
    public static final List<String> ERAS = List.of("triassic", "jurassic", "early_cretaceous", "late_cretaceous", "ice_age");
    /** Knowledge counters: a marine reptile / a pterosaur was sighted (objective "Inland Sea"). */
    private static final String SEEN_SEA = "seen_sea";
    private static final String SEEN_SKY = "seen_sky";
    /** Knowledge counter "era_title_&lt;era&gt;": the era's title was shown to this player (once per player and world). */
    private static final String ERA_TITLE = "era_title_";

    private Research() {
    }

    public static void init() {
        ModNetwork.init();
        PlayerEvent.PLAYER_JOIN.register(Research::onJoin);
        PlayerEvent.CHANGE_DIMENSION.register((player, from, to) -> {
            Knowledge k = knowledge(player);
            if (arrive(player, k, false)) {
                changed(player, k, true);
            }
        });
        TickEvent.PLAYER_POST.register(Research::onPlayerTick);
        EntityEvent.LIVING_DEATH.register((entity, source) -> {
            if (entity instanceof DinosaurEntity dino && source.getEntity() instanceof ServerPlayer player) {
                defeated(player, dino.speciesId());
                fillSample(player, dino.speciesId());
            }
            return EventResult.pass();
        });
        PlayerEvent.CRAFT_ITEM.register((player, stack, inventory) -> {
            if (player instanceof ServerPlayer sp && stack.getItem() instanceof SpearItem) {
                objective(sp, Objective.FIRST_SPEAR);
            }
        });
        BlockEvent.PLACE.register((level, pos, state, placer) -> {
            if (placer instanceof ServerPlayer player && isThatch(state)) {
                Knowledge k = knowledge(player);
                if (k.increment("thatch_placed") >= Objective.SHELTER_BLOCKS) {
                    objective(player, Objective.SHELTER);
                }
                changed(player, k, false);
            }
            return EventResult.pass();
        });
    }

    private static boolean isThatch(BlockState state) {
        return state.is(ModBlocks.THATCH.get()) || state.is(ModBlocks.THATCH_STAIRS.get()) || state.is(ModBlocks.THATCH_SLAB.get());
    }

    // ------------------------------------------------------------------ access

    public static Knowledge knowledge(ServerPlayer player) {
        return ResearchData.get(player.server).of(player.getUUID());
    }

    /** Field Guide level of a species for a player (server side; 0 on the client or for non-players). */
    public static int level(Player player, String species) {
        return player instanceof ServerPlayer sp ? knowledge(sp).level(species) : Knowledge.UNKNOWN;
    }

    public static boolean isStudied(Player player, String species) {
        return level(player, species) >= Knowledge.STUDIED;
    }

    private static void changed(ServerPlayer player, Knowledge k, boolean sync) {
        if (milestones(player, k) || sync) {
            ModNetwork.sendKnowledge(player, k);
        }
    }

    /** Era of the place the player is in: the Overworld is Chapter 1 (other eras will get their own dimensions). */
    public static String eraHere(ServerPlayer player) {
        return player.level().dimension() == Level.OVERWORLD ? "late_cretaceous" : null;
    }

    // ------------------------------------------------------------------ events

    private static void onJoin(ServerPlayer player) {
        Knowledge k = knowledge(player);
        // players from before v0.10 saw the era's title on every join: they are not shown it again
        boolean veteran = k.introSeen();
        ModNetwork.sendStory(player, Story.enabled());
        if (Story.enabled()) {
            if (!k.introSeen()) {
                k.setIntroSeen(true);
                ItemStack notebook = new ItemStack(ModItems.FIELD_NOTEBOOK.get());
                if (!player.getInventory().add(notebook)) {
                    player.drop(notebook, false);
                }
                ModNetwork.sendIntro(player);
            }
            award(player, "chapter1/root");
        }
        milestones(player, k);
        arrive(player, k, veteran);
        ModNetwork.sendFullKnowledge(player, k);
    }

    /**
     * The title of the era the player is in ("Late Cretaceous"), the first time they are in it: once per player and
     * world, kept in their Knowledge. {@code silent} only marks it. Returns true if the Knowledge changed.
     */
    private static boolean arrive(ServerPlayer player, Knowledge k, boolean silent) {
        String era = eraHere(player);
        if (era == null || k.counter(ERA_TITLE + era) > 0) {
            return false;
        }
        k.increment(ERA_TITLE + era);
        if (!silent) {
            ModNetwork.sendEraTitle(player, era);
        }
        return true;
    }

    private static void onPlayerTick(Player player) {
        if (!(player instanceof ServerPlayer sp) || (sp.tickCount + sp.getId()) % 20 != 0 || sp.isSpectator()) {
            return;
        }
        Knowledge k = knowledge(sp);
        for (DinosaurEntity dino : sp.level().getEntitiesOfClass(DinosaurEntity.class, sp.getBoundingBox().inflate(SIGHT_RANGE),
                d -> d.distanceToSqr(sp) < SIGHT_RANGE * SIGHT_RANGE)) {
            if (isNews(k, dino) && sp.hasLineOfSight(dino)) {
                sighted(sp, dino);
            }
        }
        // ridden flight: really in the air, not just a jump
        if (sp.getVehicle() instanceof FlyingDinosaur flyer && flyer.isFlying() && sp.level().isEmptyBlock(flyer.blockPosition().below(3))) {
            award(sp, "journal/ride_flyer");
        }
    }

    /** Whether seeing this animal teaches the player something new. */
    private static boolean isNews(Knowledge k, DinosaurEntity dino) {
        return k.level(dino.speciesId()) < Knowledge.SIGHTED
                || dino instanceof SwimmingDinosaur && k.counter(SEEN_SEA) == 0
                || dino instanceof FlyingDinosaur && k.counter(SEEN_SKY) == 0;
    }

    // ------------------------------------------------------------------ what raises knowledge

    /** A living animal seen up close or through the Amber Lens. */
    public static void sighted(ServerPlayer player, DinosaurEntity dino) {
        Knowledge k = knowledge(player);
        if (dino instanceof SwimmingDinosaur && k.counter(SEEN_SEA) == 0) {
            k.increment(SEEN_SEA);
        }
        if (dino instanceof FlyingDinosaur && k.counter(SEEN_SKY) == 0) {
            k.increment(SEEN_SKY);
        }
        sighted(player, dino.speciesId());
    }

    public static void sighted(ServerPlayer player, String species) {
        Knowledge k = knowledge(player);
        if (k.raiseLevel(species, Knowledge.SIGHTED)) {
            announce(player, species, Knowledge.SIGHTED);
        }
        // a Rift leak: an animal of another era in this one (only Chapter 1 has its own tab so far)
        GuideSpecies s = GuideSpecies.byId(species);
        if (s != null && "late_cretaceous".equals(eraHere(player)) && !s.era().equals("late_cretaceous")) {
            award(player, "chapter1/out_of_time");
        }
        checkStudied(player, k, species);
        changed(player, k, true);
    }

    /** A fossil studied at the Research Table. */
    public static void studyFossil(ServerPlayer player, String species) {
        Knowledge k = knowledge(player);
        if (k.raiseLevel(species, Knowledge.SILHOUETTE)) {
            announce(player, species, Knowledge.SILHOUETTE);
        }
        k.addPoints(species, FOSSIL_POINTS);
        checkStudied(player, k, species);
        award(player, "journal/first_silhouette");
        // fossils tell the future: an older era than the one the player is in
        GuideSpecies s = GuideSpecies.byId(species);
        String here = eraHere(player);
        if (s != null && here != null && ERAS.indexOf(s.era()) >= 0 && ERAS.indexOf(s.era()) < ERAS.indexOf(here)) {
            award(player, "journal/deep_time");
        }
        objective(player, Objective.RESEARCH_TABLE);
        changed(player, k, true);
    }

    /** A sketch studied at the Research Table (sketching needs the animal in sight, so it also counts as a sighting). */
    public static void studySketch(ServerPlayer player, String species) {
        Knowledge k = knowledge(player);
        if (k.raiseLevel(species, Knowledge.SIGHTED)) {
            announce(player, species, Knowledge.SIGHTED);
        }
        k.addPoints(species, SKETCH_POINTS);
        checkStudied(player, k, species);
        objective(player, Objective.RESEARCH_TABLE);
        changed(player, k, true);
    }

    /** A Blood Sample studied at the Research Table. */
    public static void studySample(ServerPlayer player, String species) {
        Knowledge k = knowledge(player);
        k.addPoints(species, SAMPLE_POINTS);
        checkStudied(player, k, species);
        objective(player, Objective.RESEARCH_TABLE);
        changed(player, k, true);
    }

    /** An empty Clay Jar carried by the player is filled with the blood of the dinosaur they defeated. */
    private static void fillSample(ServerPlayer player, String species) {
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack jar = inv.getItem(i);
            if (jar.is(ModItems.CLAY_JAR.get())) {
                jar.shrink(1);
                ItemStack sample = SketchItem.of(ModItems.BLOOD_SAMPLE.get(), species);
                if (!inv.add(sample)) {
                    player.drop(sample, false);
                }
                player.displayClientMessage(Component.translatable("message.terrassic.sample_taken",
                        Component.translatable("entity.terrassic." + species)), true);
                return;
            }
        }
    }

    public static void defeated(ServerPlayer player, String species) {
        Knowledge k = knowledge(player);
        if (k.raiseLevel(species, Knowledge.SIGHTED)) {
            announce(player, species, Knowledge.SIGHTED);
        }
        k.addPoints(species, DEFEAT_POINTS);
        checkStudied(player, k, species);
        changed(player, k, true);
    }

    public static void tamed(ServerPlayer player, DinosaurEntity dino) {
        Knowledge k = knowledge(player);
        if (k.raiseLevel(dino.speciesId(), Knowledge.TAMED)) {
            announce(player, dino.speciesId(), Knowledge.TAMED);
        }
        if (dino instanceof HerbivoreDinosaur) {
            objective(player, Objective.TAME_HERBIVORE);
        }
        changed(player, k, true);
    }

    private static void checkStudied(ServerPlayer player, Knowledge k, String species) {
        if (k.level(species) == Knowledge.SIGHTED && k.points(species) >= Knowledge.POINTS_TO_STUDY) {
            k.raiseLevel(species, Knowledge.STUDIED);
            announce(player, species, Knowledge.STUDIED);
        }
    }

    private static void announce(ServerPlayer player, String species, int level) {
        player.displayClientMessage(Component.translatable("message.terrassic.guide." + level,
                Component.translatable("entity.terrassic." + species)), true);
        player.level().playSound(null, player.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1.0F, 1.0F);
    }

    // ------------------------------------------------------------------ objectives and pages

    /** Completes a Field Journal objective (and its advancement). Safe to call again. */
    public static void objective(ServerPlayer player, Objective objective) {
        Knowledge k = knowledge(player);
        if (complete(player, k, objective)) {
            changed(player, k, true);
        }
    }

    /** Marks the objective and gives its advancement and, on the theme's 2nd objective, the amber fragment. */
    private static boolean complete(ServerPlayer player, Knowledge k, Objective objective) {
        if (!Story.enabled() || !objective.available() || !k.completeObjective(objective)) {
            return false;
        }
        award(player, objective.advancement());
        if (Objective.done(k, objective.theme()) == Objective.PER_THEME) {
            award(player, objective.theme().advancement());
            player.displayClientMessage(Component.translatable("message.terrassic.theme_done", Objective.fragments(k)), true);
            player.level().playSound(null, player.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1.0F, 0.8F);
        }
        return true;
    }

    // ------------------------------------------------------------------ advancements (docs/CONQUISTAS.md)

    /**
     * Gives the advancement terrassic:&lt;path&gt; (all its criteria). Does nothing if it is done or not in the game, or if
     * it belongs to the story's tab (chapter1/) while the story mode is off.
     */
    public static void award(ServerPlayer player, String path) {
        if (path.startsWith("chapter1/") && !Story.enabled()) {
            return;
        }
        Advancement advancement = player.server.getAdvancements().getAdvancement(Terrassic.id(path));
        if (advancement == null) {
            return;
        }
        AdvancementProgress progress = player.getAdvancements().getOrStartProgress(advancement);
        if (progress.isDone()) {
            return;
        }
        List<String> remaining = new ArrayList<>();
        progress.getRemainingCriteria().forEach(remaining::add);
        for (String criterion : remaining) {
            player.getAdvancements().award(advancement, criterion);
        }
    }

    /**
     * Objectives and advancements that follow from what the player knows: counts, fragments, pages. Cheap and safe to
     * repeat. Returns true if an objective was completed (the client copy needs a sync).
     */
    private static boolean milestones(ServerPlayer player, Knowledge k) {
        boolean changed = false;
        int studied = k.countAtLeast(Knowledge.STUDIED);
        int pages = 0;
        for (Lore.Page p : Lore.ALL) {
            if (k.pages().contains(p.id())) {
                pages++;
            }
        }
        if (studied >= Objective.STUDY_SPECIES) {
            changed |= complete(player, k, Objective.STUDY_FIVE);
        }
        if (pages >= Objective.PAGES) {
            changed |= complete(player, k, Objective.KATARINA_PAGES);
        }
        if (k.counter(SEEN_SEA) > 0 && k.counter(SEEN_SKY) > 0) {
            changed |= complete(player, k, Objective.INLAND_SEA);
        }
        for (Objective o : Objective.values()) {
            if (o.available() && k.hasObjective(o)) {
                award(player, o.advancement());
            }
        }
        for (Objective.Theme t : Objective.Theme.values()) {
            if (Objective.done(k, t) >= Objective.PER_THEME) {
                award(player, t.advancement());
            }
        }
        if (Objective.fragments(k) == Objective.Theme.values().length) {
            award(player, "chapter1/four_fragments");
        }
        if (k.countAtLeast(Knowledge.SIGHTED) > 0) {
            award(player, "journal/first_sighting");
        }
        if (studied > 0) {
            award(player, "journal/first_studied");
        }
        if (allStudied(k, "late_cretaceous")) {
            award(player, "chapter1/all_cretaceous");
        }
        if (allStudied(k, null)) {
            award(player, "journal/guide_complete");
        }
        if (k.countAtLeast(Knowledge.TAMED) >= TAMED_SPECIES) {
            award(player, "journal/five_tamed");
        }
        if (k.level("tyrannosaurus") >= Knowledge.TAMED) {
            award(player, "chapter1/pet_rex");
        }
        if (pages > 0) {
            award(player, "chapter1/first_page");
        }
        if (pages >= READER_PAGES) {
            award(player, "journal/five_pages");
        }
        if (pages == Lore.ALL.size()) {
            award(player, "journal/all_pages");
        }
        return changed;
    }

    /** Every Field Guide species of the era (null = of every active era, config/Eras) is at least studied. */
    private static boolean allStudied(Knowledge k, String era) {
        int count = 0;
        for (GuideSpecies s : GuideSpecies.ALL) {
            if (era == null ? Eras.active(s) : s.era().equals(era)) {
                if (k.level(s.id()) < Knowledge.STUDIED) {
                    return false;
                }
                count++;
            }
        }
        return count > 0;
    }

    /** Adds a Katarina page to the player's notebook. Returns false if they already had it. */
    public static boolean addPage(ServerPlayer player, String page) {
        Knowledge k = knowledge(player);
        if (!k.addPage(page)) {
            return false;
        }
        changed(player, k, true);
        return true;
    }
}
