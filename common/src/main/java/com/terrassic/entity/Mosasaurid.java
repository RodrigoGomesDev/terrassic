package com.terrassic.entity;

import com.terrassic.network.ModNetwork;
import java.util.EnumSet;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The hand-made Mosasaurus rig (tools/modelgen/handmade/mosasaurus, its own study and 25 animations), the first animal
 * of the sea remade by hand. Its touch is the AMBUSH FROM BELOW of an air-breathing lizard of the sea. What it adds over
 * a plain {@link SwimmingDinosaur}:
 * <ul>
 *   <li>its own gaits: in the water it hovers ("idle"), cruises on the beat of its tail ("swim"), patrols slowly near
 *       the bottom ("walk") and bursts ("run") when it hunts; out of the water it lies helpless and thrashes
 *       ("stranded");</li>
 *   <li>the ambush: a hunting wild adult whose prey is at the surface (swimming, or in a boat) with deep water under it
 *       does not swim at it: it sinks under it, then rises in a steep burst ("ambush") and bites from below for half
 *       again its bite. A boat it hits from below throws its rower into the water. Without deep water under the prey it
 *       just bites, as before;</li>
 *   <li>it breathes air: every two or three minutes it swims up and lifts the top of its head out of the water, where
 *       the nostrils are, and blows ("breathe": a puff of spray at the snout). That is when you see one;</li>
 *   <li>now and then a wild one, fed and at the surface, throws itself clear of the water ("breach"); a rider makes it
 *       leap with the jump key at the surface;</li>
 *   <li>it swallows small prey in steps (the pterygoid ratchet, "swallow") and shakes what is too big ("shake"); two
 *       wild males spar with their jaws now and then, without harm ("spar");</li>
 *   <li>it warns before it hunts: a wild adult that is not hunting turns its gape on whoever swims or rows within 10
 *       blocks ("gape", the whole double-hinged jaw open, the throat ballooning); and now and then at the surface it
 *       puts its head straight up out of the water and looks round ("spyhop");</li>
 *   <li>live birth, no egg: a calf is born at sea next to its mother's tail ("birth") and goes up for its first breath;
 *       born to tame parents, it is its owner's. Wild calves keep near their mother;</li>
 *   <li>its own taming: only a calf eats from a stranger's hand, and not with its mother near: she comes to defend it.
 *       The calf has to be lured away with fish first (it follows fish in the hand), beyond 20 blocks from her.</li>
 * </ul>
 * Its own diving harness is the only saddle it takes (gen_species); the floats on it are why a rider breathes under
 * water (SwimmingDinosaur gives the rider water breathing).
 */
public abstract class Mosasaurid extends SwimmingDinosaur {
    /** Blocks from the centre to the nostrils (the model: z -118 px at 16 px per block). */
    private static final double SNOUT = 5.2D;
    /** How far a calf may be from its mother before she defends it / before it eats from a stranger. */
    private static final double MOTHER_RANGE = 20.0D;

    private RawAnimation idleA;
    private RawAnimation swimA;
    private RawAnimation walkA;
    private RawAnimation runA;
    private RawAnimation strandedA;
    private RawAnimation sitA;
    private RawAnimation sleepA;

    private int breathTimer;
    private int ambushCooldown;
    private int breachCooldown;
    private int sparCooldown;
    private int gapeCooldown;
    private int spyhopCooldown;
    /** Client of the rider: the leap asked with the jump key, applied in travel. */
    private float breachPower;
    /** Ticks after a breach: the splash when it comes back into the water. */
    private int airborne;

    protected Mosasaurid(EntityType<? extends Mosasaurid> type, Level level) {
        super(type, level);
        // the first breath and the first leap come soon after it appears (seen within a minute), then every 1-2 and
        // 1.5-3 minutes
        this.breathTimer = 200 + level.getRandom().nextInt(400);
        this.breachCooldown = 300;
        this.sparCooldown = 1200;
        this.spyhopCooldown = 1200 + level.getRandom().nextInt(1200);
    }

    // ------------------------------------------------------------------ animations

    @Override
    protected String[] extraActions() {
        return new String[]{"ambush", "breach", "breathe", "swallow", "shake", "spar", "birth", "gape", "spyhop"};
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
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.idleA == null) {
            this.idleA = RawAnimation.begin().thenLoop(anim("idle"));
            this.swimA = RawAnimation.begin().thenLoop(anim("swim"));
            this.walkA = RawAnimation.begin().thenLoop(anim("walk"));
            this.runA = RawAnimation.begin().thenLoop(anim("run"));
            this.strandedA = RawAnimation.begin().thenLoop(anim("stranded"));
            this.sitA = RawAnimation.begin().thenLoop(anim("sit"));
            this.sleepA = RawAnimation.begin().thenLoop(anim("sleep"));
        }
        if (this.isSleeping()) {
            return state.setAndContinue(this.sleepA);
        }
        if (!this.isInWater()) {
            // on land a sea lizard cannot move its weight: it lies and thrashes
            return state.setAndContinue(this.strandedA);
        }
        if (this.isInSittingPose() && !this.isVehicle()) {
            return state.setAndContinue(this.sitA);
        }
        if (state.isMoving()) {
            double v = this.getDeltaMovement().lengthSqr();
            if (this.isAggressive() || v > 0.09D) {
                return state.setAndContinue(this.runA);
            }
            return state.setAndContinue(v < 0.012D ? this.walkA : this.swimA);
        }
        return state.setAndContinue(this.idleA);
    }

    // ------------------------------------------------------------------ goals

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(1, new AmbushGoal());
        this.goalSelector.addGoal(3, new BreatheGoal());
        this.goalSelector.addGoal(5, new StayByMotherGoal());
        // the sea animals had no BreedGoal (1.5 test: a fed tame couple never bred): two in love swim together
        this.goalSelector.addGoal(2, new com.terrassic.entity.ai.DinoBreedGoal(this, 1.0D));
    }

    /** At the surface: swimming in the top block of water, or in a boat. */
    private static boolean atSurface(LivingEntity e) {
        if (e.getVehicle() instanceof Boat) {
            return true;
        }
        BlockPos above = BlockPos.containing(e.getX(), e.getY() + e.getBbHeight() + 0.5D, e.getZ());
        return e.isInWater() && !e.level().getFluidState(above).is(FluidTags.WATER);
    }

    /** Water at least {@code depth} blocks deep straight under the point. */
    private boolean deepUnder(Vec3 at, int depth) {
        for (int dy = 1; dy <= depth; dy++) {
            if (!this.level().getFluidState(BlockPos.containing(at.x, at.y - dy, at.z)).is(FluidTags.WATER)) {
                return false;
            }
        }
        return true;
    }

    /** The y of the first air over the water above it (40 blocks at most), or NaN under a roof. */
    private double surfaceAbove() {
        BlockPos.MutableBlockPos p = this.blockPosition().mutable();
        for (int dy = 0; dy < 40; dy++) {
            p.setY(this.blockPosition().getY() + dy);
            if (!this.level().getFluidState(p).is(FluidTags.WATER)) {
                return this.level().getBlockState(p).isAir() ? p.getY() : Double.NaN;
            }
        }
        return Double.NaN;
    }

    private Vec3 forward() {
        float yaw = this.getYRot() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(yaw), 0.0D, Mth.cos(yaw));
    }

    /** Spray at the nostrils (the blow, a breach, the strike from below). */
    private void spray(int count) {
        if (this.level() instanceof ServerLevel server) {
            Vec3 n = this.position().add(this.forward().scale(SNOUT * this.getScale())).add(0.0D, this.getBbHeight() * 0.9D, 0.0D);
            server.sendParticles(ParticleTypes.SPLASH, n.x, n.y + 0.4D, n.z, count * 3, 0.5D, 0.3D, 0.5D, 0.2D);
            server.sendParticles(ParticleTypes.CLOUD, n.x, n.y + 0.8D, n.z, count, 0.2D, 0.4D, 0.2D, 0.02D);
            this.level().playSound(null, n.x, n.y, n.z, SoundEvents.GENERIC_SPLASH, SoundSource.NEUTRAL, 1.2F, 0.6F);
        }
    }

    /**
     * The ambush from below: sink under the prey, then rise at it in a burst, the bite landing as the jaws close
     * (1.05 s into "ambush"), half again as hard; a rower is thrown out of the boat.
     */
    class AmbushGoal extends Goal {
        private int phase;
        private int ticks;
        private boolean struck;

        AmbushGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            Mosasaurid m = Mosasaurid.this;
            LivingEntity t = m.getTarget();
            return m.ambushCooldown <= 0 && !m.isTame() && !m.isBaby() && !m.isVehicle() && m.isInWater() && t != null
                    && t.isAlive() && atSurface(t) && m.distanceToSqr(t) < 28.0D * 28.0D && m.deepUnder(t.position(), 8);
        }

        @Override
        public boolean canContinueToUse() {
            LivingEntity t = Mosasaurid.this.getTarget();
            return t != null && t.isAlive() && (this.phase == 0 ? this.ticks < 120 : this.ticks <= 32);
        }

        @Override
        public void start() {
            this.phase = 0;
            this.ticks = 0;
            this.struck = false;
        }

        @Override
        public void stop() {
            Mosasaurid.this.ambushCooldown = 200 + Mosasaurid.this.random.nextInt(200);
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            Mosasaurid m = Mosasaurid.this;
            LivingEntity t = m.getTarget();
            if (t == null) {
                return;
            }
            this.ticks++;
            if (this.phase == 0) {
                // down and under it, out of sight
                if (this.ticks % 10 == 1) {
                    m.getNavigation().moveTo(t.getX(), t.getY() - 7.0D, t.getZ(), 1.1D);
                }
                double dx = t.getX() - m.getX();
                double dz = t.getZ() - m.getZ();
                if ((dx * dx + dz * dz < 16.0D && m.getY() < t.getY() - 4.0D) || this.ticks >= 100) {
                    this.phase = 1;
                    this.ticks = 0;
                    m.getNavigation().stop();
                    m.triggerAnim(ACTION_CONTROLLER, "ambush");
                }
                return;
            }
            // the rise: straight at it, fast
            m.getLookControl().setLookAt(t, 30.0F, 30.0F);
            if (m.getY() < t.getY() + 0.5D) {
                Vec3 d = t.position().add(0.0D, t.getBbHeight() * 0.5D, 0.0D).subtract(m.position()).normalize();
                m.setDeltaMovement(d.scale(0.9D));
                m.hasImpulse = true;
            }
            if (!this.struck && this.ticks >= 18 && m.distanceTo(t) < m.getBbWidth() * 0.5F + t.getBbWidth() * 0.5F + 2.5F) {
                this.struck = true;
                float bite = (float) m.getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.5F;
                Entity boat = t.getVehicle();
                if (t.hurt(m.damageSources().mobAttack(m), bite)) {
                    m.setLastHurtMob(t);
                }
                if (boat instanceof Boat) {
                    t.stopRiding();
                    boat.setDeltaMovement(boat.getDeltaMovement().add(0.0D, 0.6D, 0.0D));
                }
                t.setDeltaMovement(t.getDeltaMovement().add(0.0D, 0.7D, 0.0D));
                t.hurtMarked = true;
                m.spray(6);
            }
        }
    }

    /** Up for air every two or three minutes: the top of the head out, the blow. */
    class BreatheGoal extends Goal {
        private int ticks;
        private int held;
        private double surface;

        BreatheGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            Mosasaurid m = Mosasaurid.this;
            if (m.breathTimer > 0 || !m.isInWater() || m.getTarget() != null || m.isVehicle() || m.isOrderedToSit()
                    || m.isKnockedOut() || m.isSleeping()) {
                return false;
            }
            this.surface = m.surfaceAbove();
            if (Double.isNaN(this.surface)) {
                m.breathTimer = 600;     // under a roof of ice or stone: it tries again later
                return false;
            }
            return true;
        }

        @Override
        public boolean canContinueToUse() {
            Mosasaurid m = Mosasaurid.this;
            return this.ticks < 240 && this.held < 52 && m.getTarget() == null && !m.isVehicle();
        }

        @Override
        public void start() {
            this.ticks = 0;
            this.held = 0;
        }

        @Override
        public void stop() {
            Mosasaurid m = Mosasaurid.this;
            m.breathTimer = 1200 + m.random.nextInt(1200);
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            Mosasaurid m = Mosasaurid.this;
            this.ticks++;
            double top = m.getY() + m.getBbHeight();
            if (this.held == 0 && top < this.surface - 0.3D) {
                Vec3 f = m.forward();
                m.getMoveControl().setWantedPosition(m.getX() + f.x * 3.0D, this.surface - m.getBbHeight() * 0.8D,
                        m.getZ() + f.z * 3.0D, 0.8D);
                return;
            }
            if (this.held == 0) {
                m.getNavigation().stop();
                m.triggerAnim(ACTION_CONTROLLER, "breathe");
            }
            this.held++;
            m.setDeltaMovement(m.getDeltaMovement().multiply(0.5D, 0.0D, 0.5D));
            if (this.held == 18) {
                m.spray(5);   // the blow
            }
        }
    }

    /** A wild calf keeps near its mother (the nearest wild adult female). */
    class StayByMotherGoal extends Goal {
        private Mosasaurid mother;

        StayByMotherGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            Mosasaurid m = Mosasaurid.this;
            if (!m.isBaby() || m.isTame() || !m.isInWater() || m.random.nextInt(10) != 0) {
                return false;
            }
            this.mother = m.nearestWildMother(32.0D);
            return this.mother != null && m.distanceToSqr(this.mother) > 100.0D;
        }

        @Override
        public boolean canContinueToUse() {
            return this.mother != null && this.mother.isAlive() && Mosasaurid.this.distanceToSqr(this.mother) > 36.0D
                    && !Mosasaurid.this.getNavigation().isDone();
        }

        @Override
        public void start() {
            Mosasaurid.this.getNavigation().moveTo(this.mother, 1.2D);
        }

        @Override
        public void stop() {
            this.mother = null;
        }
    }

    /** The nearest wild adult female of its kind within range, or null. */
    protected Mosasaurid nearestWildMother(double range) {
        Mosasaurid best = null;
        double bestD = range * range;
        for (Mosasaurid o : this.level().getEntitiesOfClass(Mosasaurid.class, this.getBoundingBox().inflate(range),
                c -> c != this && c.getType() == this.getType() && !c.isBaby() && !c.isTame() && c.isFemale() && c.isAlive())) {
            double d = this.distanceToSqr(o);
            if (d < bestD) {
                bestD = d;
                best = o;
            }
        }
        return best;
    }

    // ------------------------------------------------------------------ the world around it

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.breathTimer > 0 && !this.isVehicle()) {
            this.breathTimer--;
        }
        if (this.ambushCooldown > 0) {
            this.ambushCooldown--;
        }
        if (this.breachCooldown > 0) {
            this.breachCooldown--;
        }
        if (this.sparCooldown > 0) {
            this.sparCooldown--;
        }
        if (this.gapeCooldown > 0) {
            this.gapeCooldown--;
        }
        if (this.spyhopCooldown > 0) {
            this.spyhopCooldown--;
        }
        if (this.airborne > 0) {
            this.airborne--;
            if (this.isInWater() && this.airborne < 30) {
                this.airborne = 0;
                this.spray(10);        // back in, with a splash
            }
        }
        if (this.tickCount % 20 != 0 || this.isTame() || this.isBaby() || !this.isInWater() || this.isKnockedOut()) {
            return;
        }
        if (this.isFemale()) {
            this.guardCalves();
        }
        if (this.getTarget() == null && this.breachCooldown <= 0 && (this.isSated() || this.getHunger() >= HUNTS_BELOW)
                && this.random.nextInt(15) == 0) {
            this.wildBreach();
        }
        if (!this.isFemale() && this.getTarget() == null && this.sparCooldown <= 0 && this.random.nextInt(45) == 0) {
            this.spar();
        }
        if (this.getTarget() == null && this.gapeCooldown <= 0) {
            this.gapeWarning();
        }
        if (this.getTarget() == null && this.spyhopCooldown <= 0 && this.random.nextInt(90) == 0) {
            this.spyhop();
        }
    }

    /** A wild adult that is not hunting: whoever swims or rows within 10 blocks gets the gape first, broadside on. */
    private void gapeWarning() {
        Player p = this.level().getNearestPlayer(this, 10.0D);
        if (p == null || p.isCreative() || p.isSpectator() || !(p.isInWater() || p.getVehicle() instanceof Boat)) {
            return;
        }
        this.getNavigation().stop();
        this.getLookControl().setLookAt(p, 30.0F, 30.0F);
        this.triggerAnim(ACTION_CONTROLLER, "gape");
        this.playSound(this.getAmbientSound(), this.getSoundVolume(), 0.75F);
        this.gapeCooldown = 600 + this.random.nextInt(600);
    }

    /** At the surface, now and then: the head straight up out of the water, looking round (at a player, if one is near). */
    private void spyhop() {
        double surface = this.surfaceAbove();
        if (Double.isNaN(surface) || this.getY() + this.getBbHeight() < surface - 2.0D) {
            return;
        }
        this.spyhopCooldown = 2400 + this.random.nextInt(2400);
        this.getNavigation().stop();
        Player p = this.level().getNearestPlayer(this, 24.0D);
        if (p != null) {
            this.getLookControl().setLookAt(p, 30.0F, 30.0F);
        }
        this.triggerAnim(ACTION_CONTROLLER, "spyhop");
        this.spray(4);
    }

    /** A wild mother: a player near one of her calves, in the water or in a boat, is driven off. */
    private void guardCalves() {
        List<Mosasaurid> calves = this.level().getEntitiesOfClass(Mosasaurid.class, this.getBoundingBox().inflate(MOTHER_RANGE),
                c -> c.getType() == this.getType() && c.isBaby() && !c.isTame());
        for (Mosasaurid calf : calves) {
            Player p = this.level().getNearestPlayer(calf, 8.0D);
            if (p != null && !p.isCreative() && !p.isSpectator() && (p.isInWater() || p.getVehicle() instanceof Boat)) {
                this.guard(p);
                return;
            }
        }
    }

    protected void guard(Player p) {
        if (this.getTarget() != p) {
            this.setTarget(p);
            p.displayClientMessage(Component.translatable("message.terrassic.mother_guard", this.getDisplayName()), true);
        }
    }

    /** At the surface, fed, open water ahead: it throws itself out of the water. */
    private void wildBreach() {
        double surface = this.surfaceAbove();
        if (Double.isNaN(surface) || this.getY() + this.getBbHeight() < surface - 2.5D) {
            return;
        }
        Vec3 land = this.position().add(this.forward().scale(12.0D));
        if (!this.deepUnder(land.add(0.0D, 1.0D, 0.0D), 5)) {
            return;
        }
        this.breachCooldown = 1800 + this.random.nextInt(1800);
        this.leap(1.0F);
    }

    private void leap(float power) {
        Vec3 f = this.forward();
        this.setDeltaMovement(f.x * 0.9D * power, 1.0D * power, f.z * 0.9D * power);
        this.hasImpulse = true;
        this.airborne = 60;
        this.triggerAnim(ACTION_CONTROLLER, "breach");
        this.spray(6);
    }

    /** Two wild males: they face each other and gape, a bite at the head, no harm. */
    private void spar() {
        for (Mosasaurid o : this.level().getEntitiesOfClass(Mosasaurid.class, this.getBoundingBox().inflate(12.0D),
                c -> c != this && c.getType() == this.getType() && !c.isBaby() && !c.isTame() && !c.isFemale()
                        && c.isInWater() && c.getTarget() == null && c.sparCooldown <= 0)) {
            this.getLookControl().setLookAt(o, 30.0F, 30.0F);
            o.getLookControl().setLookAt(this, 30.0F, 30.0F);
            this.triggerAnim(ACTION_CONTROLLER, "spar");
            o.triggerAnim(ACTION_CONTROLLER, "spar");
            this.sparCooldown = 1800 + this.random.nextInt(1800);
            o.sparCooldown = 1800 + this.random.nextInt(1800);
            return;
        }
    }

    // ------------------------------------------------------------------ the bite

    /** What it kills: the small swallowed in steps, the big shaken. */
    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity l && !l.isAlive()) {
            this.triggerAnim(ACTION_CONTROLLER, l.getBbWidth() < 1.0F ? "swallow" : "shake");
        }
        return hit;
    }

    // ------------------------------------------------------------------ taming

    /** Only a calf eats from a stranger's hand, and not with its mother close: she comes for you. */
    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!this.isTame() && this.isBaby() && this.food().test(stack)) {
            Mosasaurid mother = this.nearestWildMother(MOTHER_RANGE);
            if (mother != null) {
                if (!this.level().isClientSide()) {
                    player.displayClientMessage(Component.translatable("message.terrassic.calf_mother_near", this.getDisplayName()), true);
                    mother.guard(player);
                }
                return InteractionResult.sidedSuccess(this.level().isClientSide());
            }
        }
        return super.mobInteract(player, hand);
    }

    // ------------------------------------------------------------------ live birth

    /** No egg: the calf is born at sea by its mother's tail, goes up for its first breath, and is the owner's if the
     *  mother is tame. */
    @Override
    public void finalizeSpawnChildFromBreeding(ServerLevel level, Animal partner, AgeableMob child) {
        super.finalizeSpawnChildFromBreeding(level, partner, child);
        if (!(child instanceof Mosasaurid calf)) {
            return;
        }
        Mosasaurid mother = partner instanceof Mosasaurid o && o.isFemale() ? o : this;
        Vec3 tail = mother.position().subtract(mother.forward().scale(3.5D * mother.getScale())).add(0.0D, 0.5D, 0.0D);
        calf.moveTo(tail.x, tail.y, tail.z, mother.getYRot(), 0.0F);
        calf.breathTimer = 0;
        mother.triggerAnim(ACTION_CONTROLLER, "birth");
        level.sendParticles(ParticleTypes.BUBBLE, tail.x, tail.y + 0.5D, tail.z, 30, 0.6D, 0.4D, 0.6D, 0.05D);
        if (mother.isTame() && mother.getOwner() instanceof Player owner) {
            calf.tame(owner);
            calf.notice(owner, ModNetwork.NOTICE_FERN, Component.translatable("hud.terrassic.notice.born"),
                    Component.translatable("hud.terrassic.notice.name_sex", calf.getDisplayName(),
                            Component.translatable(calf.isFemale() ? "sex.terrassic.female" : "sex.terrassic.male")));
        }
    }

    // ------------------------------------------------------------------ riding: the leap

    /** At the surface the jump key makes it leap clear of the water (a breach under the rider). */
    @Override
    public boolean canJump() {
        return this.isSaddled() && !this.isBaby() && this.isInWater();
    }

    @Override
    public void onPlayerJump(int power) {
        if (this.canJump() && power > 0) {
            this.breachPower = power >= 90 ? 1.0F : 0.5F + 0.5F * power / 90.0F;
        }
    }

    @Override
    public void handleStartJump(int power) {
        if (this.canJump() && this.nearSurface()) {
            this.airborne = 60;
            this.triggerAnim(ACTION_CONTROLLER, "breach");
            this.spray(4);
        }
    }

    private boolean nearSurface() {
        double s = this.surfaceAbove();
        return !Double.isNaN(s) && this.getY() + this.getBbHeight() > s - 2.0D;
    }

    @Override
    public void travel(Vec3 input) {
        if (this.breachPower > 0.0F && this.isVehicle() && this.isControlledByLocalInstance()) {
            if (this.isInWater() && this.nearSurface()) {
                Vec3 f = this.forward();
                this.setDeltaMovement(f.x * 0.8D * this.breachPower, 0.95D * this.breachPower, f.z * 0.8D * this.breachPower);
                this.hasImpulse = true;
            }
            this.breachPower = 0.0F;
        }
        super.travel(input);
    }
}
