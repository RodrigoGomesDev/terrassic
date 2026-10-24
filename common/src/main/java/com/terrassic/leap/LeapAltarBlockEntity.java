package com.terrassic.leap;

import com.terrassic.config.WorldConfig;
import com.terrassic.registry.ModItems;
import com.terrassic.research.Research;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * State and logic of one Leap Altar: the ring check, what the player can do here, and the ritual of the meteors
 * (HISTORIA.md, Chapter 1 "Final"):
 * <ol>
 *   <li><b>Call</b> ({@link WorldConfig#ritualCallSeconds()}, 30 s): the sky reddens around the altar and meteors fall
 *       all around it.</li>
 *   <li><b>Fight</b>: the Rift Tyrant crashes down 20-28 blocks away. Meteors keep falling, fewer.</li>
 *   <li><b>After</b>: the Tyrant falls, the meteors stop over 10 s, and the altar opens for everyone who was
 *       there (advancement "Rift Tyrant"). If every player leaves (96 blocks) or dies for 30 s, the Tyrant goes back
 *       into the Rift and the ritual can be tried again.</li>
 * </ol>
 * Nothing is destroyed: the meteors only burn and push what they hit (WorldConfig "meteor_damage"), never blocks.
 */
public class LeapAltarBlockEntity extends BlockEntity {
    public static final int IDLE = 0;
    public static final int CALL = 1;
    public static final int FIGHT = 2;
    public static final int AFTER = 3;
    private static final int AFTER_TICKS = 200;
    private static final int ABSENT_LIMIT = 600;
    private static final double PRESENCE = 96.0D;
    private static final long CONFIRM_TICKS = 100L;
    private static final DustParticleOptions SPARK = new DustParticleOptions(new Vector3f(1.0F, 0.55F, 0.12F), 1.6F);

    private int phase = IDLE;
    private int timer;
    private int absent;
    private UUID tyrant;
    private boolean opened;
    private final Set<UUID> participants = new HashSet<>();
    /** Unstable Leap asked once: player -> game time (a second offering within 5 s confirms). Not saved. */
    private final Map<UUID, Long> unstableAsked = new HashMap<>();
    /** Altars with a ritual on, for {@code /terrassic ritual parar} (refilled by the ticks after a restart). */
    private static final Set<LeapAltarBlockEntity> ACTIVE = java.util.Collections.newSetFromMap(new java.util.WeakHashMap<>());

    public LeapAltarBlockEntity(BlockPos pos, BlockState state) {
        super(LeapRegistry.LEAP_ALTAR_ENTITY.get(), pos, state);
    }

    public int phase() {
        return this.phase;
    }

    public boolean ritualActive() {
        return this.phase == CALL || this.phase == FIGHT;
    }

    // ------------------------------------------------------------------ the player at the altar

    void use(Player p) {
        if (!(p instanceof ServerPlayer player) || !(this.level instanceof ServerLevel level)) {
            return;
        }
        if (this.ritualActive()) {
            player.displayClientMessage(Component.translatable("altar.terrassic.ritual_running"), true);
            return;
        }
        List<BlockPos> missing = AltarRing.missing(level, this.worldPosition);
        if (!missing.isEmpty()) {
            player.displayClientMessage(Component.translatable("altar.terrassic.ring_missing", missing.size()), false);
            for (BlockPos m : missing) {
                level.sendParticles(player, SPARK, true, m.getX() + 0.5D, m.getY() + 0.6D, m.getZ() + 0.5D, 24, 0.25D, 0.5D, 0.25D, 0.0D);
            }
            level.playSound(null, this.worldPosition, SoundEvents.STONE_HIT, SoundSource.BLOCKS, 1.0F, 0.7F);
            return;
        }
        ItemStack held = player.getMainHandItem();
        boolean amber = held.is(ModItems.RAW_AMBER.get());
        if (player.isShiftKeyDown() && held.isEmpty()) {
            if (LeapProgress.canLeap(player)) {
                Leap.leap(player, this, false);
            } else {
                this.status(player);
            }
            return;
        }
        if (player.isShiftKeyDown() && amber) {
            if (LeapProgress.canStartRitual(player)) {
                this.offer(player, held);
                this.startRitual(level, player);
            } else if (LeapProgress.canLeapUnstable(player)) {
                long now = level.getGameTime();
                Long asked = this.unstableAsked.get(player.getUUID());
                if (asked != null && now - asked <= CONFIRM_TICKS) {
                    this.unstableAsked.remove(player.getUUID());
                    this.offer(player, held);
                    Leap.leap(player, this, true);
                } else {
                    this.unstableAsked.put(player.getUUID(), now);
                    player.displayClientMessage(Component.translatable("altar.terrassic.unstable_confirm"), false);
                    level.playSound(null, this.worldPosition, SoundEvents.RESPAWN_ANCHOR_CHARGE, SoundSource.BLOCKS, 1.0F, 0.5F);
                }
            } else {
                this.status(player);
            }
            return;
        }
        this.status(player);
    }

    private void offer(ServerPlayer player, ItemStack held) {
        if (!player.getAbilities().instabuild) {
            held.shrink(1);
        }
    }

    /** Fragments, mode and the next thing this player can do here. */
    private void status(ServerPlayer player) {
        LeapProgress.Mode mode = LeapProgress.mode(player.server);
        int fragments = LeapProgress.fragments(player);
        player.displayClientMessage(Component.translatable("altar.terrassic.status", fragments, LeapProgress.FRAGMENTS,
                Component.translatable("altar.terrassic.mode." + mode.id)), false);
        String hint;
        if (LeapProgress.canLeap(player)) {
            hint = mode == LeapProgress.Mode.NORMAL ? "leap" : "leap_or_ritual";
        } else if (LeapProgress.canStartRitual(player)) {
            hint = "ritual";
        } else if (LeapProgress.canLeapUnstable(player)) {
            hint = "unstable";
        } else {
            hint = "need_fragments";
        }
        player.displayClientMessage(Component.translatable("altar.terrassic.hint." + hint, fragments), false);
        this.level.playSound(null, this.worldPosition, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1.0F, 0.8F + fragments * 0.1F);
    }

    // ------------------------------------------------------------------ the ritual

    private void startRitual(ServerLevel level, ServerPlayer starter) {
        this.phase = CALL;
        this.timer = 0;
        this.absent = 0;
        this.tyrant = null;
        this.participants.clear();
        for (ServerPlayer p : level.players()) {
            if (p.distanceToSqr(Vec3.atCenterOf(this.worldPosition)) < 48.0D * 48.0D || p == starter) {
                this.participants.add(p.getUUID());
                Research.award(p, "chapter1/meteor_ritual");
            }
        }
        this.broadcast(level, Component.translatable("altar.terrassic.ritual_start"), 128.0D);
        level.playSound(null, this.worldPosition, SoundEvents.END_PORTAL_SPAWN, SoundSource.HOSTILE, 2.0F, 0.6F);
        level.sendParticles(ParticleTypes.FLASH, this.worldPosition.getX() + 0.5D, this.worldPosition.getY() + 1.5D,
                this.worldPosition.getZ() + 0.5D, 1, 0, 0, 0, 0);
        LeapNetwork.ritual(level, this.worldPosition, true);
        this.refreshStage();
        this.setChanged();
    }

    /** Ends a ritual that was not won: the Tyrant goes back into the Rift. */
    void cancelRitual(boolean broken) {
        if (!this.ritualActive() || !(this.level instanceof ServerLevel level)) {
            return;
        }
        Entity t = this.tyrant == null ? null : level.getEntity(this.tyrant);
        if (t != null) {
            level.sendParticles(SPARK, t.getX(), t.getY() + t.getBbHeight() / 2, t.getZ(), 200,
                    t.getBbWidth() / 2, t.getBbHeight() / 2, t.getBbWidth() / 2, 0.05D);
            level.playSound(null, t.blockPosition(), SoundEvents.ENDERMAN_TELEPORT, SoundSource.HOSTILE, 3.0F, 0.4F);
            t.discard();
        }
        this.broadcast(level, Component.translatable(broken ? "altar.terrassic.broken" : "altar.terrassic.retreat"), 128.0D);
        this.phase = IDLE;
        this.tyrant = null;
        this.participants.clear();
        LeapNetwork.ritual(level, this.worldPosition, false);
        if (!broken) {
            this.refreshStage();
        }
        this.setChanged();
    }

    /** Called by the Rift Tyrant when it dies. */
    void onTyrantDeath(RiftTyrant dead) {
        if (!(this.level instanceof ServerLevel level) || this.phase != FIGHT) {
            return;
        }
        this.phase = AFTER;
        this.timer = 0;
        this.opened = true;
        for (ServerPlayer p : level.players()) {
            boolean near = p.distanceToSqr(dead) < PRESENCE * PRESENCE
                    || p.distanceToSqr(Vec3.atCenterOf(this.worldPosition)) < PRESENCE * PRESENCE;
            if (p.isAlive() && (near || this.participants.contains(p.getUUID()) && p.distanceToSqr(dead) < 160.0D * 160.0D)) {
                LeapProgress.markTyrant(p);
                Research.award(p, "chapter1/rift_tyrant");
                p.displayClientMessage(Component.translatable("altar.terrassic.victory"), false);
            }
        }
        level.playSound(null, this.worldPosition, SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1.0F, 1.0F);
        this.refreshStage();
        this.setChanged();
    }

    public static void serverTick(Level lvl, BlockPos pos, BlockState state, LeapAltarBlockEntity be) {
        if (!(lvl instanceof ServerLevel level)) {
            return;
        }
        long time = level.getGameTime();
        if (time % 20 == 0) {
            be.refreshStage();
        }
        if (be.phase == IDLE) {
            ACTIVE.remove(be);
            return;
        }
        ACTIVE.add(be);
        be.timer++;
        RandomSource r = level.random;
        switch (be.phase) {
            case CALL -> {
                float k = Math.min(1.0F, be.timer / 200.0F);
                if (r.nextFloat() < 0.04F + 0.1F * k) {
                    Meteor.fallNear(level, pos, 10.0D, 40.0D, 2.5F);
                }
                if (be.timer >= WorldConfig.ritualCallSeconds() * 20) {
                    be.spawnTyrant(level);
                }
            }
            case FIGHT -> {
                if (r.nextFloat() < 0.03F) {
                    Meteor.fallNear(level, pos, 12.0D, 44.0D, 2.5F);
                }
                if (be.timer % 20 == 0) {
                    be.checkFight(level);
                }
            }
            case AFTER -> {
                if (r.nextFloat() < 0.03F * (1.0F - be.timer / (float) AFTER_TICKS)) {
                    Meteor.fallNear(level, pos, 20.0D, 60.0D, 1.5F);
                }
                if (be.timer >= AFTER_TICKS) {
                    be.phase = IDLE;
                    LeapNetwork.ritual(level, pos, false);
                    be.refreshStage();
                    be.setChanged();
                }
            }
            default -> be.phase = IDLE;
        }
        if (be.phase != IDLE && time % 40 == 0) {
            LeapNetwork.ritual(level, pos, true);
        }
    }

    private void spawnTyrant(ServerLevel level) {
        RandomSource r = level.random;
        BlockPos spot = null;
        RiftTyrant t = LeapRegistry.RIFT_TYRANT.get().create(level);
        if (t == null) {
            this.cancelRitual(false);
            return;
        }
        for (int attempt = 0; attempt < 16 && spot == null; attempt++) {
            double a = r.nextDouble() * Math.PI * 2.0D;
            double d = 20.0D + r.nextDouble() * 8.0D;
            int x = this.worldPosition.getX() + (int) Math.round(Math.cos(a) * d);
            int z = this.worldPosition.getZ() + (int) Math.round(Math.sin(a) * d);
            BlockPos ground = new BlockPos(x, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
            if (!level.getFluidState(ground).isEmpty() || !level.getFluidState(ground.below()).isEmpty()) {
                continue;
            }
            t.moveTo(x + 0.5D, ground.getY(), z + 0.5D, r.nextFloat() * 360.0F, 0.0F);
            if (level.noCollision(t)) {
                spot = ground;
            }
        }
        if (spot == null) {  // forest or water all around: it comes down right next to the ring
            spot = this.worldPosition.offset(0, 0, 6);
            t.moveTo(spot.getX() + 0.5D, spot.getY(), spot.getZ() + 0.5D, 0.0F, 0.0F);
        }
        t.finalizeSpawn(level, level.getCurrentDifficultyAt(spot), MobSpawnType.EVENT, null, null);
        t.bindToAltar(this.worldPosition);
        level.addFreshEntity(t);
        this.tyrant = t.getUUID();
        this.phase = FIGHT;
        this.timer = 0;
        level.sendParticles(ParticleTypes.EXPLOSION_EMITTER, t.getX(), t.getY() + 1.0D, t.getZ(), 2, 1.0D, 0.5D, 1.0D, 0.0D);
        level.sendParticles(ParticleTypes.LAVA, t.getX(), t.getY() + 1.0D, t.getZ(), 60, 3.0D, 1.0D, 3.0D, 0.0D);
        level.sendParticles(SPARK, t.getX(), t.getY() + 2.0D, t.getZ(), 300, 3.0D, 3.0D, 3.0D, 0.1D);
        level.playSound(null, spot, SoundEvents.GENERIC_EXPLODE, SoundSource.HOSTILE, 6.0F, 0.5F);
        t.roarNow();
        this.broadcast(level, Component.translatable("altar.terrassic.tyrant_arrives"), 160.0D);
        this.setChanged();
    }

    private void checkFight(ServerLevel level) {
        Entity t = this.tyrant == null ? null : level.getEntity(this.tyrant);
        if (t == null || !t.isAlive()) {
            // unloaded or gone without dying through onTyrantDeath (e.g. removed by a command): count as absent
            this.absent += 20;
        } else {
            boolean someone = false;
            for (ServerPlayer p : level.players()) {
                if (p.isAlive() && !p.isSpectator() && p.distanceToSqr(Vec3.atCenterOf(this.worldPosition)) < PRESENCE * PRESENCE) {
                    someone = true;
                    this.participants.add(p.getUUID());
                }
            }
            this.absent = someone ? 0 : this.absent + 20;
        }
        if (this.absent >= ABSENT_LIMIT) {
            this.cancelRitual(false);
        }
    }

    /** Ends the rituals of the altars within {@code range} blocks of {@code pos}; returns how many. */
    static int stopNear(ServerLevel level, BlockPos pos, double range) {
        int n = 0;
        for (LeapAltarBlockEntity be : List.copyOf(ACTIVE)) {
            if (be.level == level && !be.isRemoved() && be.worldPosition.distSqr(pos) < range * range) {
                if (be.ritualActive()) {
                    be.cancelRitual(false);
                } else {
                    be.phase = IDLE;
                    LeapNetwork.ritual(level, be.worldPosition, false);
                    be.refreshStage();
                }
                n++;
            }
        }
        return n;
    }

    /** Block state from the ring and the ritual. */
    void refreshStage() {
        if (this.level == null || this.level.isClientSide()) {
            return;
        }
        int stage;
        if (this.ritualActive() || this.phase == AFTER) {
            stage = LeapAltarBlock.RITUAL;
        } else if (!AltarRing.complete(this.level, this.worldPosition)) {
            stage = LeapAltarBlock.COLD;
        } else {
            stage = this.opened ? LeapAltarBlock.OPEN : LeapAltarBlock.RING;
        }
        BlockState state = this.getBlockState();
        if (state.is(LeapRegistry.LEAP_ALTAR.get()) && state.getValue(LeapAltarBlock.STAGE) != stage) {
            this.level.setBlock(this.worldPosition, state.setValue(LeapAltarBlock.STAGE, stage), 3);
        }
    }

    private void broadcast(ServerLevel level, Component msg, double range) {
        for (ServerPlayer p : level.players()) {
            if (p.distanceToSqr(Vec3.atCenterOf(this.worldPosition)) < range * range) {
                p.displayClientMessage(msg, false);
            }
        }
    }

    // ------------------------------------------------------------------ save

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt("Phase", this.phase);
        tag.putInt("Timer", this.timer);
        tag.putBoolean("Opened", this.opened);
        if (this.tyrant != null) {
            tag.putUUID("Tyrant", this.tyrant);
        }
        ListTag list = new ListTag();
        for (UUID id : this.participants) {
            list.add(NbtUtils.createUUID(id));
        }
        tag.put("Participants", list);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        this.phase = tag.getInt("Phase");
        this.timer = tag.getInt("Timer");
        this.opened = tag.getBoolean("Opened");
        this.tyrant = tag.hasUUID("Tyrant") ? tag.getUUID("Tyrant") : null;
        this.participants.clear();
        for (Tag t : tag.getList("Participants", Tag.TAG_INT_ARRAY)) {
            this.participants.add(NbtUtils.loadUUID(t));
        }
    }
}
