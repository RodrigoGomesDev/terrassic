package com.terrassic.research;

import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.HerbivoreDinosaur;
import com.terrassic.item.SpearItem;
import com.terrassic.network.ModNetwork;
import com.terrassic.registry.ModBlocks;
import com.terrassic.registry.ModItems;
import dev.architectury.event.EventResult;
import dev.architectury.event.events.common.BlockEvent;
import dev.architectury.event.events.common.EntityEvent;
import dev.architectury.event.events.common.PlayerEvent;
import dev.architectury.event.events.common.TickEvent;
import net.minecraft.advancements.Advancement;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;

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
 */
public final class Research {
    public static final double SIGHT_RANGE = 16.0D;
    public static final int FOSSIL_POINTS = 1;
    public static final int SKETCH_POINTS = 2;
    public static final int DEFEAT_POINTS = 3;

    private Research() {
    }

    public static void init() {
        PlayerEvent.PLAYER_JOIN.register(Research::onJoin);
        TickEvent.PLAYER_POST.register(Research::onPlayerTick);
        EntityEvent.LIVING_DEATH.register((entity, source) -> {
            if (entity instanceof DinosaurEntity dino && source.getEntity() instanceof ServerPlayer player) {
                defeated(player, dino.speciesId());
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
        ResearchData.get(player.server).setDirty();
        if (sync) {
            ModNetwork.sendKnowledge(player, k);
        }
    }

    // ------------------------------------------------------------------ events

    private static void onJoin(ServerPlayer player) {
        Knowledge k = knowledge(player);
        if (!k.introSeen()) {
            k.setIntroSeen(true);
            ItemStack notebook = new ItemStack(ModItems.FIELD_NOTEBOOK.get());
            if (!player.getInventory().add(notebook)) {
                player.drop(notebook, false);
            }
            changed(player, k, false);
            ModNetwork.sendIntro(player);
        }
        ModNetwork.sendKnowledge(player, k);
    }

    private static void onPlayerTick(Player player) {
        if (!(player instanceof ServerPlayer sp) || sp.tickCount % 20 != 0 || sp.isSpectator()) {
            return;
        }
        Knowledge k = knowledge(sp);
        for (DinosaurEntity dino : sp.level().getEntitiesOfClass(DinosaurEntity.class, sp.getBoundingBox().inflate(SIGHT_RANGE),
                d -> d.distanceToSqr(sp) < SIGHT_RANGE * SIGHT_RANGE)) {
            if (k.level(dino.speciesId()) < Knowledge.SIGHTED && sp.hasLineOfSight(dino)) {
                sighted(sp, dino.speciesId());
            }
        }
    }

    // ------------------------------------------------------------------ what raises knowledge

    public static void sighted(ServerPlayer player, String species) {
        Knowledge k = knowledge(player);
        if (k.raiseLevel(species, Knowledge.SIGHTED)) {
            announce(player, species, Knowledge.SIGHTED);
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
            checkStudyCount(player, k);
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
            checkStudyCount(player, k);
        }
    }

    private static void checkStudyCount(ServerPlayer player, Knowledge k) {
        if (k.countAtLeast(Knowledge.STUDIED) >= Objective.STUDY_SPECIES) {
            objective(player, Objective.STUDY_FIVE);
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
        if (!objective.available() || !k.completeObjective(objective)) {
            return;
        }
        Advancement advancement = player.server.getAdvancements().getAdvancement(Terrassic.id(objective.advancement()));
        if (advancement != null) {
            player.getAdvancements().award(advancement, "done");
        }
        int done = 0;
        for (Objective o : Objective.values()) {
            if (o.theme() == objective.theme() && k.hasObjective(o)) {
                done++;
            }
        }
        if (done == Objective.PER_THEME) {
            player.sendSystemMessage(Component.translatable("message.terrassic.theme_done",
                    Component.translatable("theme.terrassic." + objective.theme().id())));
            player.level().playSound(null, player.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1.0F, 0.8F);
        }
        changed(player, k, true);
    }

    /** Adds a Katarina page to the player's notebook. Returns false if they already had it. */
    public static boolean addPage(ServerPlayer player, String page) {
        Knowledge k = knowledge(player);
        if (!k.pages().add(page)) {
            return false;
        }
        changed(player, k, true);
        return true;
    }
}
