package com.terrassic.world;

import com.mojang.brigadier.CommandDispatcher;
import com.terrassic.Terrassic;
import com.terrassic.config.WorldConfig;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.SwimmingDinosaur;
import com.terrassic.registry.ModItems;
import com.terrassic.research.GuideSpecies;
import com.terrassic.research.Objective;
import com.terrassic.research.Research;
import dev.architectury.event.EventResult;
import dev.architectury.event.events.common.CommandRegistrationEvent;
import dev.architectury.event.events.common.EntityEvent;
import dev.architectury.event.events.common.PlayerEvent;
import dev.architectury.event.events.common.TickEvent;
import dev.architectury.networking.NetworkManager;
import io.netty.buffer.Unpooled;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * Rift Storms (Tempestades da Fenda, HISTORIA.md §5; v0.8 phase M4). Now and then, at dusk, the sky turns amber, time
 * "glitches" (amber motes, distorted sounds; client side in client/RiftStormClient) and creatures from other eras
 * step out of the Rift around every player in the overworld for a few minutes: the species of the Field Guide whose
 * era is not the Late Cretaceous (today the four Jurassic "leaks"; any out-of-era species added later joins in).
 * When the storm ends they go back through the Rift, unless someone tamed them. They drop raw amber.
 * A player who is in the overworld when the storm starts and still alive there when it ends completes the Field
 * Journal objective "Survive a Rift Storm".
 *
 * <p>Options in config/terrassic-world.json ({@link WorldConfig}); {@code /terrassic tempestade iniciar|parar} for admins.
 */
public final class RiftStorm {
    public static final ResourceLocation SYNC = Terrassic.id("rift_storm");
    /** Scoreboard tag of the creatures that came through the Rift. */
    public static final String TAG = "terrassic_rift";
    private static final DustParticleOptions AMBER = new DustParticleOptions(new Vector3f(1.0F, 0.68F, 0.22F), 1.6F);
    private static final int DUSK = 12600;
    private static List<EntityType<?>> leaks;

    private RiftStorm() {
    }

    public static void init() {
        TickEvent.SERVER_LEVEL_POST.register(RiftStorm::tick);
        PlayerEvent.PLAYER_JOIN.register(p -> send(p, Data.get(p.server).active));
        PlayerEvent.CHANGE_DIMENSION.register((p, from, to) -> send(p, Data.get(p.server).active));
        EntityEvent.LIVING_DEATH.register(RiftStorm::onDeath);
        CommandRegistrationEvent.EVENT.register(RiftStorm::commands);
    }

    public static boolean active(MinecraftServer server) {
        return Data.get(server).active;
    }

    // ------------------------------------------------------------------ the storm's life

    private static void tick(ServerLevel level) {
        if (level.dimension() != Level.OVERWORLD) {
            return;
        }
        Data d = Data.get(level.getServer());
        long time = level.getGameTime();
        if (!d.active) {
            if (time % 100 == 0) {
                sendBack(level, false);  // stragglers loaded after the last storm ended
            }
            if (WorldConfig.riftStorms() && level.getDayTime() % 24000L == DUSK && !level.players().isEmpty()
                    && time - d.lastEnd >= WorldConfig.stormMinDays() * 24000L
                    && level.random.nextDouble() < WorldConfig.stormChance()) {
                start(level, d);
            }
            return;
        }
        if (--d.left <= 0) {
            stop(level, d);
            return;
        }
        if (time % 200 == 0) {
            for (ServerPlayer p : level.players()) {
                if (!p.isSpectator()) {
                    leakNear(level, p);
                }
            }
        }
        if (time % 20 == 0) {
            d.setDirty();
        }
    }

    public static void start(ServerLevel level, Data d) {
        RandomSource r = level.random;
        int minutes = WorldConfig.stormMinutesMin() + r.nextInt(WorldConfig.stormMinutesMax() - WorldConfig.stormMinutesMin() + 1);
        d.active = true;
        d.left = minutes * 1200;
        d.survivors.clear();
        for (ServerPlayer p : level.players()) {
            d.survivors.add(p.getUUID());
            p.displayClientMessage(Component.translatable("message.terrassic.storm_start"), false);
            level.playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.AMBIENT, 1.0F, 0.5F);
        }
        d.setDirty();
        sendAll(level.getServer(), true);
    }

    public static void stop(ServerLevel level, Data d) {
        d.active = false;
        d.left = 0;
        d.lastEnd = level.getGameTime();
        for (ServerPlayer p : level.players()) {
            p.displayClientMessage(Component.translatable("message.terrassic.storm_end"), false);
            if (d.survivors.contains(p.getUUID()) && p.isAlive()) {
                Research.objective(p, Objective.RIFT_STORM);
            }
        }
        d.survivors.clear();
        d.setDirty();
        sendBack(level, true);
        sendAll(level.getServer(), false);
    }

    /** Creatures of the Rift go back where they came from (tamed ones stay and lose the mark). */
    private static void sendBack(ServerLevel level, boolean effects) {
        List<Entity> marked = new ArrayList<>();
        for (Entity e : level.getAllEntities()) {
            if (e.getTags().contains(TAG)) {
                marked.add(e);
            }
        }
        for (Entity e : marked) {
            if (e instanceof DinosaurEntity dino && dino.isTame()) {
                dino.removeTag(TAG);
                continue;
            }
            if (effects) {
                level.sendParticles(AMBER, e.getX(), e.getY() + e.getBbHeight() / 2, e.getZ(), 50,
                        e.getBbWidth() / 2, e.getBbHeight() / 2, e.getBbWidth() / 2, 0.0D);
            }
            e.discard();
        }
    }

    // ------------------------------------------------------------------ creatures from other eras

    private static List<EntityType<?>> leaks(ServerLevel level) {
        if (leaks == null) {
            List<EntityType<?>> out = new ArrayList<>();
            for (GuideSpecies s : GuideSpecies.ALL) {
                if ("late_cretaceous".equals(s.era())) {
                    continue;
                }
                EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(Terrassic.id(s.id()));
                Entity probe = type.create(level);
                if (probe instanceof DinosaurEntity && !(probe instanceof SwimmingDinosaur)) {
                    out.add(type);
                }
                if (probe != null) {
                    probe.discard();
                }
            }
            leaks = out;
        }
        return leaks;
    }

    private static void leakNear(ServerLevel level, ServerPlayer player) {
        List<EntityType<?>> types = leaks(level);
        if (types.isEmpty()) {
            return;
        }
        AABB around = player.getBoundingBox().inflate(64.0D);
        int near = level.getEntitiesOfClass(DinosaurEntity.class, around, e -> e.getTags().contains(TAG)).size();
        if (near >= WorldConfig.stormCreatures()) {
            return;
        }
        RandomSource r = level.random;
        for (int attempt = 0; attempt < 6; attempt++) {
            double angle = r.nextDouble() * Math.PI * 2.0;
            double dist = 20.0D + r.nextDouble() * 14.0D;
            int x = (int) Math.floor(player.getX() + Math.cos(angle) * dist);
            int z = (int) Math.floor(player.getZ() + Math.sin(angle) * dist);
            if (!level.hasChunkAt(new BlockPos(x, 0, z))) {
                continue;
            }
            BlockPos pos = new BlockPos(x, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
            if (!level.getFluidState(pos.below()).isEmpty() || !level.getFluidState(pos).isEmpty()) {
                continue;
            }
            Entity e = types.get(r.nextInt(types.size())).create(level);
            if (!(e instanceof DinosaurEntity dino)) {
                return;
            }
            dino.moveTo(x + 0.5D, pos.getY(), z + 0.5D, r.nextFloat() * 360.0F, 0.0F);
            dino.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.EVENT, null, null);
            dino.addTag(TAG);
            dino.addEffect(new MobEffectInstance(MobEffects.GLOWING, 200, 0, false, false));
            level.addFreshEntity(dino);
            level.sendParticles(AMBER, dino.getX(), dino.getY() + dino.getBbHeight() / 2, dino.getZ(), 80,
                    dino.getBbWidth() / 2, dino.getBbHeight() / 2, dino.getBbWidth() / 2, 0.02D);
            level.playSound(null, pos, SoundEvents.ENDERMAN_TELEPORT, SoundSource.HOSTILE, 1.2F, 0.5F);
            level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.HOSTILE, 1.0F, 0.6F);
            return;
        }
    }

    private static EventResult onDeath(LivingEntity entity, DamageSource source) {
        if (entity.level().isClientSide) {
            return EventResult.pass();
        }
        if (entity instanceof ServerPlayer p) {
            Data.get(p.server).survivors.remove(p.getUUID());
        } else if (entity.getTags().contains(TAG)) {
            entity.spawnAtLocation(new ItemStack(ModItems.RAW_AMBER.get(), 1 + entity.getRandom().nextInt(2)));
        }
        return EventResult.pass();
    }

    // ------------------------------------------------------------------ sync and command

    private static void send(ServerPlayer player, boolean active) {
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        buf.writeBoolean(active);
        NetworkManager.sendToPlayer(player, SYNC, buf);
    }

    private static void sendAll(MinecraftServer server, boolean active) {
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            send(p, active);
        }
    }

    private static void commands(CommandDispatcher<CommandSourceStack> dispatcher, CommandBuildContext ctx,
                                 Commands.CommandSelection selection) {
        dispatcher.register(Commands.literal("terrassic").then(Commands.literal("tempestade")
                .requires(src -> src.hasPermission(2))
                .then(Commands.literal("iniciar").executes(c -> {
                    ServerLevel level = c.getSource().getServer().overworld();
                    Data d = Data.get(c.getSource().getServer());
                    if (!d.active) {
                        start(level, d);
                    }
                    return 1;
                }))
                .then(Commands.literal("parar").executes(c -> {
                    ServerLevel level = c.getSource().getServer().overworld();
                    Data d = Data.get(c.getSource().getServer());
                    if (d.active) {
                        stop(level, d);
                    }
                    return 1;
                }))));
    }

    /** Storm state, saved with the overworld (data/terrassic_rift_storm.dat). */
    public static final class Data extends SavedData {
        private static final String NAME = "terrassic_rift_storm";
        boolean active;
        int left;
        long lastEnd = -1000000L;
        final Set<UUID> survivors = new HashSet<>();

        static Data get(MinecraftServer server) {
            return server.overworld().getDataStorage().computeIfAbsent(Data::load, Data::new, NAME);
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            tag.putBoolean("Active", this.active);
            tag.putInt("Left", this.left);
            tag.putLong("LastEnd", this.lastEnd);
            ListTag list = new ListTag();
            for (UUID id : this.survivors) {
                list.add(NbtUtils.createUUID(id));
            }
            tag.put("Survivors", list);
            return tag;
        }

        static Data load(CompoundTag tag) {
            Data d = new Data();
            d.active = tag.getBoolean("Active");
            d.left = tag.getInt("Left");
            d.lastEnd = tag.contains("LastEnd") ? tag.getLong("LastEnd") : -1000000L;
            for (Tag t : tag.getList("Survivors", Tag.TAG_INT_ARRAY)) {
                d.survivors.add(NbtUtils.loadUUID(t));
            }
            return d;
        }
    }
}
