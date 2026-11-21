package com.terrassic.entity;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.BushBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;

/**
 * The hand-made Thescelosaurus rig (tools/modelgen/handmade/thescelosaurus, silhouette A "tipo ave" of the 1.11; its
 * own study: docs/estudos/15_HERBIVOROS_1_11.md, approved by Rodrigo on 10/11/2026). Its touch is the WARY animal of
 * the undergrowth, the commonest middle-sized prey of the forest:
 * <ul>
 *   <li><b>freeze and bolt</b>: a predator or a player noticed within {@link #NOTICE} blocks (a crouching player only
 *       within {@link #NOTICE_SNEAK}) makes it stop dead ("freeze") for 1 to 3 s; if the danger comes within
 *       {@link #BOLT_AT} blocks, or is still there when the freeze ends, it BOLTS ("bolt": a zigzag sprint, the pale
 *       tail flag up) for the thickest cover near (leaves, ferns, bushes, or its burrow), and hides there lying flat
 *       ("hide"), peeking now and then ("peek"), until the danger has gone. The others of its kind that see the flag
 *       bolt too;</li>
 *   <li><b>the nose</b> (Button & Zanno 2023): it smells a predator within {@link #SMELL} blocks without line of sight
 *       ("sniff_air", then the freeze); it sniffs the ground as it browses ("sniff_ground");</li>
 *   <li><b>the burrow</b> (a HYPOTHESIS, Button & Zanno 2023, after Oryctodromeus; the Guide says so): at dusk a wild
 *       adult with no burrow digs one into a bank of earth or sand near ("burrow_dig"), sleeps in it at night curled up
 *       ("burrow_sleep"), runs to it when it bolts, and lays its eggs at its end;</li>
 *   <li>cornered, it bites with the front teeth or kicks forward ("attack", "kick") and kicks back at what bites its
 *       tail ("kick_back"); tame, it follows its owner and digs up roots and tubers ("dig"); not rideable.</li>
 * </ul>
 * One log line per behaviour, "[thesc] ..." (logger "terrassic"), for the playtests (BehaviorTest phase "thesc").
 */
public abstract class Thescelosaurine extends HerbivoreDinosaur {
    /** The cycles (thesanims.py WALK, RUN, BOLT): pixels of ground each covers and its length in ticks. */
    private static final double WALK_PX = 30.0D;
    private static final double WALK_TICKS = 20.0D;
    private static final double RUN_PX = 84.0D;
    private static final double RUN_TICKS = 12.0D;
    private static final double BOLT_PX = 83.0D;
    private static final double BOLT_TICKS = 10.0D;
    /** How far it notices a predator or a standing player it can see; a crouching player only this near. */
    public static final double NOTICE = 16.0D;
    public static final double NOTICE_SNEAK = 6.0D;
    /** How far it smells a predator without seeing it. */
    public static final double SMELL = 24.0D;
    /** The danger this near during the freeze: it bolts. */
    public static final double BOLT_AT = 10.0D;

    public static final byte CALM = 0, FREEZE = 1, BOLT = 2, HIDE = 3;
    private static final EntityDataAccessor<Byte> DATA_WARY =
            SynchedEntityData.defineId(Thescelosaurine.class, EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Boolean> DATA_BURROWED =
            SynchedEntityData.defineId(Thescelosaurine.class, EntityDataSerializers.BOOLEAN);

    private static final RawAnimation FREEZE_A = RawAnimation.begin().thenLoop("animation.thescelosaurus.freeze");
    private static final RawAnimation BOLT_A = RawAnimation.begin().thenLoop("animation.thescelosaurus.bolt");
    private static final RawAnimation HIDE_A = RawAnimation.begin().thenLoop("animation.thescelosaurus.hide");
    private static final RawAnimation BURROW_A = RawAnimation.begin().thenLoop("animation.thescelosaurus.burrow_sleep");

    private LivingEntity danger;
    private int freezeLeft;
    private int boltLeft;
    private int hideTicks;
    private int calmFor;
    private int zig;
    private Vec3 cover;
    private int wariness;            // cooldown after hiding before it freezes at the same thing again
    private int sniffCooldown = 200;
    private LivingEntity blowAt;
    private int blowIn;

    // the burrow
    private BlockPos burrow;         // the inner end (feet level)
    private BlockPos mouth;          // the approach in front of it
    private BlockPos digAt;          // the bank being dug
    private Direction digDir;
    private int digLeft;
    private int digCooldown = 400;

    protected Thescelosaurine(EntityType<? extends Thescelosaurine> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    public static void logLine(String line) {
        Behaviour.LOG.info("[thesc] " + line);
    }

    private void log(String what) {
        logLine(what + " (#" + this.getId() + " " + this.getBlockX() + " " + this.getBlockY() + " " + this.getBlockZ() + ")");
    }

    @Override
    protected void defineSynchedData(net.minecraft.network.syncher.SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(DATA_WARY, CALM);
        builder.define(DATA_BURROWED, false);
    }

    public byte wary() {
        return this.entityData.get(DATA_WARY);
    }

    private void setWary(byte s) {
        this.entityData.set(DATA_WARY, s);
    }

    public boolean inBurrow() {
        return this.entityData.get(DATA_BURROWED);
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "call", "alarm", "sniff_ground", "sniff_air", "dig", "burrow_dig", "peek", "tail_flag",
                "kick", "drink", "hatch"};
    }

    @Override
    protected boolean hasSleepAnim() {
        return true;
    }

    @Override
    protected boolean hasSwimAnim() {
        return true;
    }

    @Override
    protected boolean flinches() {
        return true;
    }

    @Override
    protected int deathAnimTicks() {
        return 60;
    }

    @Override
    public float babyHeadScale() {
        return 1.3F;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        byte w = this.wary();
        if (w == FREEZE && !this.isSleeping()) {
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(FREEZE_A);
        }
        if (w == HIDE && !this.isSleeping() && !state.isMoving()) {
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(HIDE_A);
        }
        if (this.isSleeping() && this.inBurrow()) {
            this.cycleSpeed = 1.0D;
            return state.setAndContinue(BURROW_A);
        }
        if (w == BOLT && state.isMoving() && !this.isSwimmingDeep()) {
            this.cycleSpeed = this.gaitSpeed(BOLT_PX / 16.0D / BOLT_TICKS * this.modelScale());
            return state.setAndContinue(BOLT_A);
        }
        return super.movementAnimation(state);
    }

    // ------------------------------------------------------------------ temperament
    /** Wary: only a tame one fights; the wild one freezes, bolts and hides (its own step, not the shared flight). */
    @Override
    protected boolean fightsBack() {
        return this.isTame();
    }

    @Override
    protected boolean fleesFrom(Player player) {
        return false;
    }

    @Override
    protected void addExtraGoals() {
        // the shared "avoid the player / the predator" goals would run it off before it freezes: it has its own
        this.goalSelector.removeAllGoals(g -> g instanceof AvoidEntityGoal<?>);
    }

    private boolean busy() {
        return this.getTarget() != null || this.isInSittingPose() || this.isKnockedOut() || this.isVehicle();
    }

    private List<Thescelosaurine> kind(double r) {
        return this.level().getEntitiesOfClass(Thescelosaurine.class, this.getBoundingBox().inflate(r, 8.0D, r),
                e -> e != this && e.isAlive() && !e.isTame());
    }

    /** What it notices now: a wild grown predator it sees within NOTICE (or smells within SMELL), a player it sees. */
    private LivingEntity notice() {
        DinosaurEntity p = this.nearestPredator(SMELL, true);
        if (p != null) {
            if (!this.hasLineOfSight(p)) {
                this.smelledBlind = true;          // the nose: within SMELL it needs no line of sight
            }
            return p;
        }
        Player pl = this.level().getNearestPlayer(this, NOTICE);
        if (pl != null && !pl.isCreative() && !pl.isSpectator() && this.hasLineOfSight(pl)
                && (!pl.isCrouching() || pl.distanceTo(this) <= NOTICE_SNEAK)) {
            return pl;
        }
        return null;
    }

    // ------------------------------------------------------------------ freeze, bolt, hide
    private void freeze(LivingEntity threat) {
        this.danger = threat;
        boolean blind = !this.hasLineOfSight(threat);
        if (this.isSleeping()) {
            this.setSleeping(false);
            this.entityData.set(DATA_BURROWED, false);
            this.log("wakes to " + name(threat));
        }
        this.freezeLeft = 20 + this.random.nextInt(41);
        this.setWary(FREEZE);
        this.getNavigation().stop();
        if (blind) {
            triggerAnim(ACTION_CONTROLLER, "sniff_air");
        }
        this.log("freezes: " + name(threat) + " at " + Math.round(threat.distanceTo(this)) + " blocks"
                + (blind ? " (smelled, not seen)" : ""));
    }

    private static String name(LivingEntity e) {
        return e instanceof DinosaurEntity d ? d.speciesId() : e instanceof Player ? "player" : e.getType().toShortString();
    }

    /** Bolts for cover; {@code flag}: set off by another's tail flag. */
    public void bolt(LivingEntity threat, boolean flag) {
        this.danger = threat;
        this.setSleeping(false);
        this.entityData.set(DATA_BURROWED, false);
        this.setWary(BOLT);
        this.boltLeft = 140;
        this.zig = 0;
        this.cover = this.findCover(threat);
        this.boltLeg();
        triggerAnim(ACTION_CONTROLLER, "tail_flag");
        if (!flag) {
            this.boltedAt = threat.distanceTo(this);
        }
        this.log((flag ? "sees the flag and bolts" : "bolts") + " from " + name(threat) + " at "
                + Math.round(threat.distanceTo(this)) + " blocks toward " + (this.cover == null ? "nowhere (open ground)"
                : "cover " + Math.round(this.cover.distanceTo(this.position())) + " blocks off"));
        if (!flag) {
            int n = 0;
            for (Thescelosaurine o : this.kind(NOTICE)) {
                if (o.wary() != BOLT && o.wary() != HIDE && !o.isTame() && o.hasLineOfSight(this)) {
                    o.bolt(threat, true);
                    n++;
                }
            }
            if (n > 0) {
                this.log("the flag: " + n + " others bolt too");
            }
        }
    }

    /** A zigzag leg toward the cover (a waypoint off to one side, the other side next time). */
    private void boltLeg() {
        Vec3 to = this.cover;
        if (to == null && this.danger != null) {
            Vec3 d = this.position().subtract(this.danger.position());
            to = this.position().add(new Vec3(d.x, 0.0D, d.z).normalize().scale(14.0D));
        }
        if (to == null) {
            return;
        }
        Vec3 d = to.subtract(this.position());
        Vec3 flat = new Vec3(d.x, 0.0D, d.z);
        Vec3 wp = to;
        if (flat.length() > 6.0D) {
            Vec3 dir = flat.normalize();
            Vec3 side = new Vec3(-dir.z, 0.0D, dir.x).scale((this.zig++ % 2 == 0 ? 1 : -1) * 3.0D);
            wp = this.position().add(dir.scale(Math.min(6.0D, flat.length()))).add(side);
        }
        this.getNavigation().moveTo(wp.x, to.y, wp.z, 2.0D);
    }

    private static boolean isCover(BlockState s) {
        return s.is(BlockTags.LEAVES) || s.getBlock() instanceof BushBlock || s.is(BlockTags.REPLACEABLE_BY_TREES)
                || s.is(Blocks.SWEET_BERRY_BUSH);
    }

    /** The densest cover within 16 blocks, away from the threat (its burrow first, if it has one near). */
    private Vec3 findCover(LivingEntity threat) {
        if (this.burrow != null && this.mouth != null && this.burrow.distSqr(this.blockPosition()) < 20 * 20
                && Vec3.atCenterOf(this.burrow).distanceTo(threat.position()) > threat.distanceTo(this)) {
            return Vec3.atBottomCenterOf(this.burrow);
        }
        BlockPos here = this.blockPosition();
        Vec3 best = null;
        double bs = -1e9;
        for (int dx = -16; dx <= 16; dx += 2) {
            for (int dz = -16; dz <= 16; dz += 2) {
                for (int dy = -3; dy <= 3; dy++) {
                    BlockPos p = here.offset(dx, dy, dz);
                    if (!this.level().getBlockState(p.below()).isSolid() || this.level().getBlockState(p).isSolid()) {
                        continue;
                    }
                    int c = 0;
                    for (BlockPos q : BlockPos.betweenClosed(p.offset(-1, 0, -1), p.offset(1, 2, 1))) {
                        if (isCover(this.level().getBlockState(q))) {
                            c++;
                        }
                    }
                    double away = Vec3.atBottomCenterOf(p).distanceTo(threat.position()) - threat.distanceTo(this);
                    if (c < 3 || away < 2.0D) {
                        continue;
                    }
                    double score = c * 2.0D + away;
                    if (score > bs) {
                        bs = score;
                        best = Vec3.atBottomCenterOf(p);
                    }
                    break;
                }
            }
        }
        return best;
    }

    private void waryStep() {
        if (this.wariness > 0) {
            this.wariness--;
        }
        byte w = this.wary();
        LivingEntity seen = this.tickCount % 4 == this.getId() % 4 ? this.notice() : null;
        if (w == CALM) {
            if (seen != null && this.wariness == 0 && !this.busy()) {
                this.freeze(seen);
            }
            return;
        }
        if (this.danger != null && !this.danger.isAlive()) {
            this.danger = null;
        }
        if (w == FREEZE) {
            this.getNavigation().stop();
            this.setDeltaMovement(this.getDeltaMovement().multiply(0.0D, 1.0D, 0.0D));
            if (this.danger != null) {
                this.getLookControl().setLookAt(this.danger, 10.0F, 10.0F);
            }
            boolean close = this.danger != null && this.danger.distanceTo(this) <= BOLT_AT;
            if (close || --this.freezeLeft <= 0) {
                double d = this.danger == null ? 1e9 : this.danger.distanceTo(this);
                if (d <= NOTICE + 2.0D) {
                    this.bolt(this.danger, false);
                } else if (d <= SMELL + 2.0D) {
                    // still there but not coming: it slinks off the other way, alert (it does not freeze again at once)
                    this.setWary(CALM);
                    this.wariness = 160;
                    Vec3 away = this.position().subtract(this.danger.position());
                    Vec3 to = this.position().add(new Vec3(away.x, 0.0D, away.z).normalize().scale(6.0D));
                    this.getNavigation().moveTo(to.x, to.y, to.z, 0.6D);
                    this.log("slinks off: " + name(this.danger) + " still at " + Math.round(d) + " blocks, not coming");
                } else {
                    this.setWary(CALM);
                    this.wariness = 60;
                    this.log("relaxes: the danger went off");
                }
            }
            return;
        }
        if (w == BOLT) {
            this.boltLeft--;
            boolean there = this.cover != null && this.cover.distanceToSqr(this.position()) < 2.5D * 2.5D;
            boolean far = this.cover == null && (this.danger == null || this.danger.distanceTo(this) > SMELL + 4.0D);
            if (there || far || this.boltLeft <= 0) {
                this.hide(there);
                return;
            }
            if (this.tickCount % 12 == 0 || this.getNavigation().isDone()) {
                this.boltLeg();
            }
            return;
        }
        if (w == HIDE) {
            this.getNavigation().stop();
            this.hideTicks++;
            LivingEntity d = this.danger;
            if (d != null && d.isAlive() && d.distanceTo(this) < 5.0D && this.hideTicks > 20) {
                this.bolt(d, false);
                return;
            }
            boolean near = d != null && d.isAlive() && d.distanceTo(this) < SMELL;
            this.calmFor = near ? 0 : this.calmFor + 1;
            if (this.hideTicks % 70 == 35) {
                triggerAnim(ACTION_CONTROLLER, "peek");
            }
            if (this.calmFor > 100) {
                this.setWary(CALM);
                this.wariness = 100;
                this.danger = null;
                this.log("comes out of hiding after " + this.hideTicks / 20 + " s");
            }
        }
    }

    private void hide(boolean inCover) {
        this.setWary(HIDE);
        this.getNavigation().stop();
        this.hideTicks = 0;
        this.calmFor = 0;
        BlockPos at = this.blockPosition();
        int c = 0;
        for (BlockPos q : BlockPos.betweenClosed(at.offset(-1, 0, -1), at.offset(1, 2, 1))) {
            if (isCover(this.level().getBlockState(q))) {
                c++;
            }
        }
        boolean burrowed = this.burrow != null && this.burrow.distSqr(at) <= 4;
        this.log("hides " + (burrowed ? "in its burrow" : inCover || c >= 3 ? "in cover (" + c + " cover blocks round it)" : "in the open")
                + (this.danger != null ? ", " + name(this.danger) + " at " + Math.round(this.danger.distanceTo(this)) + " blocks" : ""));
    }

    // ------------------------------------------------------------------ the nose
    private void sniffStep() {
        if (this.sniffCooldown > 0) {
            this.sniffCooldown--;
            return;
        }
        if (this.getNavigation().isDone() && this.random.nextInt(300) == 0) {
            triggerAnim(ACTION_CONTROLLER, this.random.nextInt(3) == 0 ? "sniff_air" : "sniff_ground");
            this.sniffCooldown = 300;
        }
    }

    // ------------------------------------------------------------------ the burrow
    private static boolean diggable(BlockState s) {
        return s.is(BlockTags.DIRT) || s.is(BlockTags.SAND) || s.is(Blocks.GRAVEL) || s.is(Blocks.CLAY)
                || s.is(Blocks.COARSE_DIRT) || s.is(Blocks.MUD) || s.is(Blocks.PACKED_MUD);
    }

    private boolean free(BlockPos p) {
        return this.level().getBlockState(p).getCollisionShape(this.level(), p).isEmpty() && this.level().getFluidState(p).isEmpty();
    }

    /** A bank within r blocks: two diggable blocks deep and two high, with room to stand in front of it. */
    private BlockPos[] findBank(int r) {
        BlockPos here = this.blockPosition();
        BlockPos[] best = null;
        double bd = Double.MAX_VALUE;
        for (BlockPos p : BlockPos.betweenClosed(here.offset(-r, -3, -r), here.offset(r, 3, r))) {
            if (!diggable(this.level().getBlockState(p)) || !diggable(this.level().getBlockState(p.above()))) {
                continue;
            }
            for (Direction d : Direction.Plane.HORIZONTAL) {
                BlockPos front = p.relative(d.getOpposite());
                BlockPos deep = p.relative(d);
                if (free(front) && free(front.above()) && free(front.above(2))
                        && this.level().getBlockState(front.below()).isFaceSturdy(this.level(), front.below(), Direction.UP)
                        && diggable(this.level().getBlockState(deep)) && diggable(this.level().getBlockState(deep.above()))) {
                    double dd = front.distSqr(here);
                    if (dd < bd) {
                        bd = dd;
                        best = new BlockPos[]{p.immutable(), front.immutable(), new BlockPos(d.getStepX(), 0, d.getStepZ())};
                    }
                }
            }
        }
        return best;
    }

    private void burrowStep() {
        if (this.digCooldown > 0) {
            this.digCooldown--;
        }
        if (this.digAt != null) {
            Vec3 front = Vec3.atBottomCenterOf(this.digAt.relative(this.digDir.getOpposite()));
            if (front.distanceToSqr(this.position()) > 1.6D * 1.6D) {
                if (this.getNavigation().isDone()) {
                    if (!this.getNavigation().moveTo(front.x, front.y, front.z, 0.9D) || --this.digLeft < -200) {
                        this.digAt = null;
                        this.digCooldown = 1200;
                    }
                }
                return;
            }
            this.getNavigation().stop();
            this.getLookControl().setLookAt(Vec3.atCenterOf(this.digAt));
            float yaw = this.digDir.toYRot();
            this.setYRot(Mth.approachDegrees(this.getYRot(), yaw, 10.0F));
            this.yBodyRot = this.getYRot();
            if (this.digLeft <= 0) {
                this.digLeft = 240;
            }
            if (this.digLeft % 80 == 0) {
                triggerAnim(ACTION_CONTROLLER, "burrow_dig");
            }
            if (this.digLeft % 10 == 0 && this.level() instanceof ServerLevel server) {
                BlockState s = server.getBlockState(this.digAt);
                server.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, s), this.digAt.getX() + 0.5D, this.digAt.getY() + 0.6D,
                        this.digAt.getZ() + 0.5D, 6, 0.3D, 0.3D, 0.3D, 0.05D);
                this.playSound(s.getSoundType().getHitSound(), 0.7F, 0.9F);
            }
            if (--this.digLeft <= 0) {
                this.finishBurrow();
            }
            return;
        }
        long tod = this.level().getDayTime() % 24000L;
        boolean dusk = tod > 11000L && tod < 23000L;
        if (this.burrow != null || this.isBaby() || this.digCooldown > 0 || !dusk || this.tickCount % 40 != this.getId() % 40) {
            return;
        }
        BlockPos[] b = this.findBank(12);
        this.digCooldown = 1200;
        if (b == null) {
            return;
        }
        this.digAt = b[0];
        this.digDir = Direction.getNearest(b[2].getX(), 0, b[2].getZ());
        this.digLeft = 0;
        this.log("goes to dig a burrow in the bank at " + this.digAt.toShortString());
    }

    private void finishBurrow() {
        BlockPos p = this.digAt;
        Direction d = this.digDir;
        this.digAt = null;
        if (!(this.level() instanceof ServerLevel server)) {
            return;
        }
        String what = server.getBlockState(p).getBlock().getName().getString();
        if (server.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) {
            for (BlockPos q : new BlockPos[]{p, p.above(), p.relative(d), p.relative(d).above()}) {
                if (diggable(server.getBlockState(q))) {
                    server.destroyBlock(q, false, this);
                }
            }
            // the burrow's roof stays (the bank over it), its third block opened only where the animal stands up
            if (diggable(server.getBlockState(p.above(2)))) {
                server.destroyBlock(p.above(2), false, this);
            }
        }
        this.burrow = p.relative(d).immutable();
        this.mouth = p.relative(d.getOpposite()).immutable();
        this.log("digs a burrow in the bank (" + what + ") at " + this.burrow.toShortString());
    }

    public BlockPos burrow() {
        return this.burrow;
    }

    /** At night it goes to its burrow first and sleeps there; without one it sleeps in the open. */
    @Override
    public boolean isSleepTime() {
        if (!super.isSleepTime() || this.wary() != CALM) {
            return false;
        }
        if (this.burrow != null && !this.isTame()) {
            double d = this.burrow.distToCenterSqr(this.position());
            return d < 2.0D * 2.0D || d > 48.0D * 48.0D;
        }
        return true;
    }

    private void nightStep() {
        if (this.burrow == null || this.isTame() || this.isBaby() || this.wary() != CALM || this.digAt != null) {
            return;
        }
        boolean night = !this.level().isDay();
        double d = this.burrow.distToCenterSqr(this.position());
        // "there" is the same 2 blocks as isSleepTime: aiming for 1.5 left one at the mouth of a tight hole walking on
        // the spot for 22 s (the playtest of 20/11: the burrow centre 1.6 blocks off, never closer)
        if (night && !this.isSleeping() && d > 2.0D * 2.0D && d < 48.0D * 48.0D && this.tickCount % 20 == 0) {
            this.getNavigation().moveTo(this.burrow.getX() + 0.5D, this.burrow.getY(), this.burrow.getZ() + 0.5D, 1.0D);
        }
        boolean in = this.isSleeping() && d < 2.0D * 2.0D;
        if (in != this.inBurrow()) {
            this.entityData.set(DATA_BURROWED, in);
            if (in) {
                this.log("sleeps in its burrow");
            }
        }
    }

    /** The eggs at the end of the burrow, when the mother has one near. */
    @Override
    protected BlockPos eggCentre(LevelAccessor level) {
        if (this.burrow != null && this.burrow.distSqr(this.blockPosition()) < 16 * 16) {
            return this.burrow;
        }
        return super.eggCentre(level);
    }

    // ------------------------------------------------------------------ cornered
    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && !this.isTame() && source.getEntity() instanceof LivingEntity attacker
                && !(attacker instanceof Player p && (p.isCreative() || p.isSpectator()))) {
            double dx = attacker.getX() - this.getX(), dz = attacker.getZ() - this.getZ();
            float off = Math.abs(Mth.wrapDegrees((float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F - this.yBodyRot));
            if (attacker.distanceTo(this) < this.getBbWidth() + attacker.getBbWidth() + 1.5F && off < 70.0F && this.blowIn == 0) {
                boolean bite = this.random.nextBoolean();
                triggerAnim(ACTION_CONTROLLER, bite ? "attack" : "kick");
                this.blowAt = attacker;
                this.blowIn = bite ? 9 : 10;
                this.log("cornered: " + (bite ? "bites" : "kicks") + " " + name(attacker));
            }
            if (this.wary() != BOLT) {
                this.bolt(attacker, false);
            }
        }
        return hurt;
    }

    private void blowStep() {
        if (this.blowIn > 0 && --this.blowIn == 0 && this.blowAt != null && this.blowAt.isAlive()
                && this.distanceTo(this.blowAt) < this.getBbWidth() + this.blowAt.getBbWidth() + 2.0F) {
            this.blowAt.hurt(this.damageSources().mobAttack(this), (float) this.getAttributeValue(
                    net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE));
            this.blowAt.knockback(0.6D, this.getX() - this.blowAt.getX(), this.getZ() - this.blowAt.getZ());
            this.blowAt = null;
        }
    }

    // ------------------------------------------------------------------ tame: roots and tubers
    private void rootStep() {
        if (this.isBaby() || this.busy() || !this.getNavigation().isDone() || this.random.nextInt(900) != 0
                || !(this.level() instanceof ServerLevel server)) {
            return;
        }
        BlockPos below = this.blockPosition().below();
        BlockState ground = server.getBlockState(below);
        if (!(ground.is(BlockTags.DIRT) || ground.is(BlockTags.SAND) || ground.is(Blocks.GRAVEL) || ground.is(Blocks.CLAY))) {
            return;
        }
        triggerAnim(ACTION_CONTROLLER, "dig");
        server.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), this.getX(), this.getY() + 0.1D, this.getZ(),
                12, 0.3D, 0.1D, 0.3D, 0.05D);
        this.playSound(ground.getSoundType().getHitSound(), 0.8F, 1.0F);
        if (!this.isTame()) {
            return;
        }
        int roll = this.random.nextInt(100);
        ItemStack found = ItemStack.EMPTY;
        if (roll < 24) {
            found = new ItemStack(Items.HANGING_ROOTS);
        } else if (roll < 58) {
            found = new ItemStack(this.random.nextBoolean() ? Items.CARROT : Items.POTATO);
        } else if (roll < 72) {
            found = new ItemStack(Items.BEETROOT);
        } else if (roll < 78) {
            found = new ItemStack(Items.BONE);
        } else if (roll < 84 && ground.is(Blocks.GRAVEL)) {
            found = new ItemStack(Items.FLINT);
        }
        if (!found.isEmpty()) {
            this.spawnAtLocation(found);
            this.log("digs up " + found.getHoverName().getString());
        }
    }

    /** Test only: digs now, roots guaranteed (the BehaviorTest cannot wait for the 1 in 900). */
    public void testDigRoots() {
        if (this.level() instanceof ServerLevel) {
            triggerAnim(ACTION_CONTROLLER, "dig");
            this.spawnAtLocation(new ItemStack(Items.CARROT));
            this.log("digs up " + new ItemStack(Items.CARROT).getHoverName().getString() + " (test)");
        }
    }

    // ------------------------------------------------------------------ the step
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.blowStep();
        if (this.isTame()) {
            if (this.wary() != CALM) {
                this.setWary(CALM);
            }
            this.rootStep();
            return;
        }
        this.waryStep();
        if (this.wary() != CALM) {
            return;
        }
        this.nightStep();
        if (this.isSleeping() || this.busy()) {
            return;
        }
        this.burrowStep();
        if (this.digAt == null) {
            this.sniffStep();
        }
    }

    // ------------------------------------------------------------------ saving
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (this.burrow != null) {
            tag.putLong("ThescBurrow", this.burrow.asLong());
            tag.putLong("ThescMouth", this.mouth.asLong());
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("ThescBurrow")) {
            this.burrow = BlockPos.of(tag.getLong("ThescBurrow"));
            this.mouth = BlockPos.of(tag.getLong("ThescMouth"));
        }
    }

    // ------------------------------------------------------------------ test hooks (BehaviorTest "thesc")
    /** It smelled a predator it could not see (since the last reset). */
    public boolean smelledBlind;
    /** Test only: the danger's distance when it decided to bolt by itself (not on a mate's flag); -1 if it has not. */
    public double boltedAt = -1.0D;

    public void testDigBurrowNow() {
        this.digCooldown = 0;
        BlockPos[] b = this.findBank(12);
        if (b != null) {
            this.digAt = b[0];
            this.digDir = Direction.getNearest(b[2].getX(), 0, b[2].getZ());
            this.digLeft = 0;
            this.log("goes to dig a burrow in the bank at " + this.digAt.toShortString() + " (test)");
        }
    }

    /** Test only: lays one wild egg now (at the burrow, if it has one near). */
    public void testLayEgg() {
        this.layWildEgg(this.level());
    }

    public void testCalm() {
        this.setWary(CALM);
        this.danger = null;
        this.wariness = 0;
        this.smelledBlind = false;
    }
}
