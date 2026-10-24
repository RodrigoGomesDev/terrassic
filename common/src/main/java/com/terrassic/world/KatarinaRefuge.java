package com.terrassic.world;

import com.terrassic.Terrassic;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.registry.ModItems;
import dev.architectury.event.CompoundEventResult;
import dev.architectury.event.EventResult;
import dev.architectury.event.events.common.InteractionEvent;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.structure.Structure;

import java.util.UUID;

/**
 * Katarina's Refuge, the River House (Casa do Rio, HISTORIA.md §8), placed once per world by the structure set
 * data/terrassic/worldgen/structure_set/river_house.json (tools/javagen/gen_structures.py).
 * <ul>
 *   <li><b>Mate</b>, her Parasaurolophus, waits on the deck: the template spawns him tamed to Katarina (who is never
 *       online, so he stays sitting). The first player who touches him with an empty hand becomes his owner.</li>
 *   <li><b>The Amber Lens points to the Refuge:</b> sneak and use the lens to get the distance and the direction.</li>
 * </ul>
 */
public final class KatarinaRefuge {
    /** Katarina's UUID, as written in the River House template (KATARINA_UUID in gen_structures.py). */
    public static final UUID KATARINA = new UUID(0x4B61746172696E61L, 0x2055736861000001L);
    public static final TagKey<Structure> REFUGE = TagKey.create(Registries.STRUCTURE, Terrassic.id("katarina_refuge"));
    private static final String[] DIRECTIONS = {"n", "ne", "e", "se", "s", "sw", "w", "nw"};

    private KatarinaRefuge() {
    }

    public static void init() {
        InteractionEvent.INTERACT_ENTITY.register(KatarinaRefuge::touchMate);
        InteractionEvent.RIGHT_CLICK_ITEM.register(KatarinaRefuge::useLens);
    }

    private static EventResult touchMate(Player player, Entity entity, InteractionHand hand) {
        if (!(entity instanceof DinosaurEntity dino) || !dino.isTame() || !KATARINA.equals(dino.getOwnerUUID())
                || !player.getItemInHand(hand).isEmpty()) {
            return EventResult.pass();
        }
        if (!player.level().isClientSide) {
            dino.removeTag("terrassic_mate");
            dino.tameBy(player);
            player.displayClientMessage(Component.translatable("message.terrassic.mate_greets", dino.getDisplayName()), false);
        }
        return EventResult.interruptTrue();
    }

    private static CompoundEventResult<ItemStack> useLens(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!player.isShiftKeyDown() || !stack.is(ModItems.AMBER_LENS.get())) {
            return CompoundEventResult.pass();
        }
        if (player instanceof ServerPlayer sp && sp.level() instanceof ServerLevel level) {
            BlockPos here = sp.blockPosition();
            BlockPos refuge = level.findNearestMapStructure(REFUGE, here, 100, false);
            Component msg;
            if (refuge == null) {
                msg = Component.translatable("message.terrassic.refuge_unknown");
            } else {
                int dx = refuge.getX() - here.getX();
                int dz = refuge.getZ() - here.getZ();
                int dist = (int) Math.round(Math.sqrt((double) dx * dx + (double) dz * dz));
                if (dist < 24) {
                    msg = Component.translatable("message.terrassic.refuge_here");
                } else {
                    double angle = Math.toDegrees(Math.atan2(dx, -dz));  // 0 = north (-z), 90 = east (+x)
                    int sector = Math.floorMod((int) Math.round(angle / 45.0), 8);
                    msg = Component.translatable("message.terrassic.refuge_direction", (dist / 10) * 10,
                            Component.translatable("direction.terrassic." + DIRECTIONS[sector]));
                }
            }
            sp.displayClientMessage(msg, true);
            level.playSound(null, here, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 0.8F, 1.2F);
            sp.getCooldowns().addCooldown(stack.getItem(), 40);
        }
        return CompoundEventResult.interruptTrue(stack);
    }
}
