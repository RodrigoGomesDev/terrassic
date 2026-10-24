package com.terrassic.leap;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.Tyrannosaurus;
import com.terrassic.entity.Velociraptor;
import com.terrassic.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

import java.util.List;

/**
 * The Rift Tyrant (Tirano da Fenda), boss of Chapter 1 (HISTORIA.md §3): a Tyrannosaurus that came through the Rift,
 * 35% bigger than the biggest rex, with amber cracks glowing on its hide (client/RiftLayer). It answers the ritual
 * of the meteors at the Leap Altar and only there.
 * <ul>
 *   <li>Hunts every player around, never sleeps or gets full, cannot be tamed, ridden or bred, never despawns.</li>
 *   <li><b>Roar of the Rift</b> (every ~12 s with a target near): pushes back and slows everyone within 10 blocks.</li>
 *   <li><b>Below half health</b>: faster, and it calls raptors of the Rift (up to 4 at a time) and meteors onto its
 *       target, with a ring of sparks on the ground a second and a half before each one lands.</li>
 *   <li>Does not wander more than 48 blocks from the altar; meteors and fire do not hurt it.</li>
 *   <li>Its death opens the altar ({@link LeapAltarBlockEntity#onTyrantDeath}).</li>
 * </ul>
 */
public class RiftTyrant extends Tyrannosaurus {
    public static final float SIZE = 1.35F;
    private static final double LEASH = 48.0D;
    private static final java.util.UUID PLAYERS_HEALTH_ID = java.util.UUID.fromString("6b1f0c52-8a3e-4d7f-b2c4-91e5a7d30f18");
    private static final DustParticleOptions SPARK = new DustParticleOptions(new Vector3f(1.0F, 0.55F, 0.12F), 2.0F);
    private final ServerBossEvent bossBar = new ServerBossEvent(Component.translatable("entity.terrassic.rift_tyrant"),
            BossEvent.BossBarColor.YELLOW, BossEvent.BossBarOverlay.NOTCHED_10);
    private BlockPos altar;
    private int roarCooldown = 200;
    private int callCooldown = 200;
    private int meteorCooldown = 160;
    /** The meteor it called onto its target, and where it will land (marked by a ring of sparks until it does). */
    private Meteor incoming;
    private Vec3 landing;
    private long incomingAt;

    public RiftTyrant(EntityType<? extends RiftTyrant> type, Level level) {
        super(type, level);
        this.xpReward = 500;
        this.setPersistenceRequired();
        if (!level.isClientSide()) {
            this.setAdultSize(SIZE);
            this.setRift(true);
        }
    }

    public static AttributeSupplier.Builder createAttributes() {
        // x SIZE^2 for health and x SIZE for the bite through the size modifiers: ~770 health, ~22 damage
        return Animal.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 420.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.26D)
                .add(Attributes.ATTACK_DAMAGE, 16.0D)
                .add(Attributes.ATTACK_KNOCKBACK, 2.0D)
                .add(Attributes.ARMOR, 12.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 4.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.FOLLOW_RANGE, 64.0D);
    }

    void bindToAltar(BlockPos pos) {
        this.altar = pos;
    }

    /** Multiplayer: +50% health for each player in the fight after the first, up to 8 players (x4.5). Saved with
     *  the attributes, so a reload keeps it. */
    void scaleForPlayers(int players) {
        net.minecraft.world.entity.ai.attributes.AttributeInstance health = this.getAttribute(Attributes.MAX_HEALTH);
        if (health == null) {
            return;
        }
        health.removeModifier(PLAYERS_HEALTH_ID);
        int extra = Math.max(0, Math.min(8, players) - 1);
        if (extra > 0) {
            health.addPermanentModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(PLAYERS_HEALTH_ID,
                    "Rift Tyrant players", 0.5D * extra, net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.MULTIPLY_BASE));
        }
        this.setHealth(this.getMaxHealth());
    }

    // ------------------------------------------------------------------ what a normal rex does and this one does not

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.targetSelector.addGoal(0, new NearestAttackableTargetGoal<>(this, Player.class, 5, false, false,
                e -> !((Player) e).isCreative() && !e.isSpectator() && this.withinLeash(e)));
    }

    /** It only goes after what is within {@link #LEASH} blocks of its altar (a target dragged further is dropped). */
    private boolean withinLeash(LivingEntity e) {
        return this.altar == null || e.distanceToSqr(Vec3.atCenterOf(this.altar)) < LEASH * LEASH;
    }

    /** It came for the players, not for dinner (and never for its own raptors). */
    @Override
    protected boolean isPrey(LivingEntity e) {
        return false;
    }

    @Override
    protected boolean huntsPlayers() {
        return true;
    }

    @Override
    protected boolean canHunt() {
        return this.level().getDifficulty() != net.minecraft.world.Difficulty.PEACEFUL;
    }

    @Override
    public boolean isSleepTime() {
        return false;
    }

    @Override
    protected int hungerInterval() {
        return Integer.MAX_VALUE / 2;
    }

    @Override
    protected float minSize() {
        return SIZE;
    }

    @Override
    protected float maxSize() {
        return SIZE;
    }

    @Override
    public boolean isRideable() {
        return false;
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        return InteractionResult.PASS;
    }

    @Override
    public boolean canMate(Animal other) {
        return false;
    }

    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        return null;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public boolean requiresCustomPersistence() {
        return true;
    }

    @Override
    public boolean canChangeDimensions() {
        return false;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getDirectEntity() instanceof Meteor || source.is(DamageTypeTags.IS_FIRE) || source.is(DamageTypeTags.IS_FALL)
                || source.is(DamageTypeTags.IS_DROWNING)) {
            return false;
        }
        return super.hurt(source, amount);
    }

    // ------------------------------------------------------------------ the fight

    void roarNow() {
        this.roarCooldown = 0;
        triggerAnim(ACTION_CONTROLLER, "roar");
        this.playSound(SoundEvents.RAVAGER_ROAR, 5.0F, 0.5F);
    }

    private boolean enraged() {
        return this.getHealth() < this.getMaxHealth() * 0.5F;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        ServerLevel level = (ServerLevel) this.level();
        this.bossBar.setProgress(this.getHealth() / this.getMaxHealth());
        if (this.enraged() && this.bossBar.getColor() != BossEvent.BossBarColor.RED) {
            this.bossBar.setColor(BossEvent.BossBarColor.RED);
            this.bossBar.setDarkenScreen(true);
            this.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0.31D);
            this.roarNow();
        }
        // a Tyrant whose ritual is over (or another one's) goes back into the Rift
        if (this.altar != null && this.tickCount % 40 == 0 && level.isLoaded(this.altar)
                && !(level.getBlockEntity(this.altar) instanceof LeapAltarBlockEntity be && be.fighting(this.getUUID()))) {
            level.sendParticles(SPARK, this.getX(), this.getY() + this.getBbHeight() / 2, this.getZ(), 200,
                    this.getBbWidth() / 2, this.getBbHeight() / 2, this.getBbWidth() / 2, 0.05D);
            dismissRaptors(level, this.position());
            this.discard();
            return;
        }
        // the leash: it does not chase you to the other side of the map
        if (this.getTarget() != null && !this.withinLeash(this.getTarget())) {
            this.setTarget(null);
        }
        LivingEntity target = this.getTarget();
        if (this.altar != null && target == null && this.tickCount % 20 == 0
                && this.distanceToSqr(Vec3.atCenterOf(this.altar)) > 24.0D * 24.0D) {
            this.getNavigation().moveTo(this.altar.getX() + 0.5D, this.altar.getY(), this.altar.getZ() + 0.5D, 1.1D);
        }
        if (this.roarCooldown > 0) {
            this.roarCooldown--;
        } else if (target != null && this.distanceToSqr(target) < 12.0D * 12.0D) {
            this.roar(level);
        }
        if (this.enraged()) {
            if (--this.callCooldown <= 0) {
                this.callRaptors(level);
            }
            if (this.incoming != null && this.incoming.isAlive() && level.getGameTime() - this.incomingAt < 200L) {
                if (this.tickCount % 5 == 0) {
                    this.markLanding(level);
                }
            } else if (--this.meteorCooldown <= 0 && target != null) {
                this.meteorCooldown = 100 + this.random.nextInt(80);
                this.landing = target.position();
                this.incoming = Meteor.fallAt(level, this.landing, 2.0F);
                this.incomingAt = level.getGameTime();
            }
        }
    }

    private void roar(ServerLevel level) {
        this.roarCooldown = (this.enraged() ? 160 : 240) + this.random.nextInt(60);
        this.roarNow();
        AABB area = this.getBoundingBox().inflate(10.0D);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, area, e -> e != this && !(e instanceof DinosaurEntity d && d.isRift()))) {
            if (e instanceof Player p && (p.isCreative() || p.isSpectator())) {
                continue;
            }
            Vec3 push = e.position().subtract(this.position()).normalize().scale(1.4D);
            e.push(push.x, 0.45D, push.z);
            e.hurtMarked = true;
            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1), this);
        }
        level.sendParticles(SPARK, this.getX(), this.getY() + this.getBbHeight() * 0.8D, this.getZ(), 120, 3.0D, 1.0D, 3.0D, 0.15D);
    }

    private void callRaptors(ServerLevel level) {
        this.callCooldown = 600;
        List<Velociraptor> around = level.getEntitiesOfClass(Velociraptor.class, this.getBoundingBox().inflate(48.0D), DinosaurEntity::isRift);
        for (int i = around.size(); i < 4 && i < around.size() + 2; i++) {
            Velociraptor v = ModEntities.VELOCIRAPTOR.get().create(level);
            if (v == null) {
                return;
            }
            double a = this.random.nextDouble() * Math.PI * 2.0D;
            v.moveTo(this.getX() + Math.cos(a) * 5.0D, this.getY(), this.getZ() + Math.sin(a) * 5.0D, this.random.nextFloat() * 360.0F, 0.0F);
            if (!level.noCollision(v)) {
                v.moveTo(this.getX(), this.getY(), this.getZ());
            }
            v.finalizeSpawn(level, level.getCurrentDifficultyAt(v.blockPosition()), MobSpawnType.EVENT, null, null);
            v.setRift(true);
            v.addTag("terrassic_rift");
            v.setTarget(this.getTarget());
            level.addFreshEntity(v);
            level.sendParticles(SPARK, v.getX(), v.getY() + 0.8D, v.getZ(), 60, 0.5D, 0.8D, 0.5D, 0.05D);
        }
        level.playSound(null, this.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.HOSTILE, 3.0F, 0.5F);
    }

    /** A ring of sparks where the incoming meteor will land (it takes about 3 s to come down). */
    private void markLanding(ServerLevel level) {
        for (int i = 0; i < 24; i++) {
            double a = i / 24.0D * Math.PI * 2.0D;
            level.sendParticles(SPARK, this.landing.x + Math.cos(a) * 2.5D, this.landing.y + 0.2D, this.landing.z + Math.sin(a) * 2.5D,
                    1, 0.05D, 0.05D, 0.05D, 0.0D);
        }
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (this.level() instanceof ServerLevel level && this.altar != null
                && level.getBlockEntity(this.altar) instanceof LeapAltarBlockEntity be) {
            be.onTyrantDeath(this);
        }
        if (this.level() instanceof ServerLevel level) {
            dismissRaptors(level, this.position());  // its raptors go back into the Rift with it
        }
    }

    /** The raptors of the Rift it called, within 64 blocks of {@code around}, go back into the Rift. */
    static void dismissRaptors(ServerLevel level, Vec3 around) {
        for (Velociraptor v : level.getEntitiesOfClass(Velociraptor.class, new AABB(around, around).inflate(64.0D),
                v -> v.isRift() && !v.isTame())) {
            level.sendParticles(SPARK, v.getX(), v.getY() + 0.8D, v.getZ(), 40, 0.5D, 0.8D, 0.5D, 0.05D);
            v.discard();
        }
    }

    // ------------------------------------------------------------------ boss bar and save

    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        this.bossBar.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        this.bossBar.removePlayer(player);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (this.altar != null) {
            tag.put("Altar", NbtUtils.writeBlockPos(this.altar));
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Altar")) {
            this.altar = NbtUtils.readBlockPos(tag.getCompound("Altar"));
        }
        this.bossBar.setProgress(this.getHealth() / this.getMaxHealth());
    }
}
