package com.terrassic.entity;

import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import com.terrassic.network.ModNetwork;
import com.terrassic.research.Research;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The hand-made Ankylosaurus rig (tools/modelgen/handmade/ankylosaurus, its own study and 24 animations). Its touch is
 * the TAIL CLUB: the prey that fights back, and fights BACKWARDS. What it adds over a plain herbivore:
 * <ul>
 *   <li>the walk and the trot follow the real speed, so the feet do not slide;</li>
 *   <li>the club defence, in place of the plain melee: it does not chase. A target near it is turned to the side or
 *       the back of the animal (it pivots its body away), and when the target is in the club's arc, from the flank
 *       round to the tail, at shin height and within the reach of the tail, the club swings to that side ("club_l" /
 *       "club_r"). The blow lands at the club's widest point (0.55 s in) on everything in that arc on that side, with
 *       a sideways knock. A target right at its head gets a short hook of the head instead ("attack"). A tame one walks
 *       to its owner's target first; a wild one only defends the ground it stands on and drops a target that keeps
 *       away;</li>
 *   <li>the warning: a wild adult with a player standing close behind it (in the club's arc) lifts its tail and swings
 *       it slowly ("club_warn"); one who stays there gets the club. A wild predator within 10 blocks: it turns its back
 *       to it and warns. One right at its head: it drops flat on its belly ("hunker") and takes less damage while it
 *       holds;</li>
 *   <li>its own taming: a wild adult does not eat from a stranger's hand (its head is under a metre high: it feeds off
 *       the ground). Its food dropped in front of it is walked to and eaten; each one eaten is a chance to tame it for
 *       whoever dropped it, the usual 1 in N, as long as they stand where it can see them and not behind it, in the
 *       arc of the club;</li>
 *   <li>two wild adult males side by side now and then club each other on the flank ("flank_club", no damage: the
 *       healed flank plates of Zuul, Arbour et al. 2022);</li>
 *   <li>idle: it roots with a forefoot ("dig", a small meal), drinks at the water, snorts with its call.</li>
 * </ul>
 * The young had no club yet: the renderer hides "adult_club" on babies and shows them "young_tail", and hides the flank
 * plates (adult_l / adult_r). Babies do not swing. Its own pack deck is the only saddle it takes (gen_species).
 */
public abstract class Ankylosaurid extends HerbivoreDinosaur {
    /** The cycles (ankyloanims.py WALK, TROTP): pixels of ground each covers at 24 px/m and its length in ticks. */
    private static final double WALK_PX = 30.0D;
    private static final double WALK_TICKS = 36.0D;
    private static final double RUN_PX = 40.0D;
    private static final double RUN_TICKS = 18.0D;
    /** Ticks from the start of a swing to the blow (the club's widest point in club_l / club_r). */
    private static final int SWING_HIT = 11;
    private static final int SWING_COOLDOWN = 34;
    /** The reach of the club from the hips, in blocks at size 1.0 (the tail is 3.5 blocks long at scale 0.667). */
    private static final double CLUB_REACH = 4.4D;
    private static final double CLUB_INNER = 1.2D;
    /** The arc of the club: from this many degrees off the nose round to the tail, on each side. */
    private static final double ARC_FROM = 70.0D;
    private int still;
    private int swingCooldown;
    private int swingHitIn = -1;
    private int swingSide;
    private int warnCooldown;
    private int hunkering;
    private int lostTarget;
    private ItemEntity meal;
    /** How long each player has stood in the club's arc since the warning. */
    private final Map<UUID, Integer> behind = new HashMap<>();

    protected Ankylosaurid(EntityType<? extends Ankylosaurid> type, Level level) {
        super(type, level);
    }

    protected abstract float modelScale();

    @Override
    protected String[] extraActions() {
        return new String[]{"graze", "club_l", "club_r", "club_warn", "flank_club", "hunker", "snort", "dig", "drink"};
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
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    /** The club defence replaces the plain melee chase (see {@link ClubDefenceGoal}). */
    @Override
    protected boolean usesMeleeGoal() {
        return false;
    }

    @Override
    protected void addExtraGoals() {
        this.goalSelector.addGoal(4, new ClubDefenceGoal());
    }

    private boolean busy() {
        return this.isVehicle() || this.isInSittingPose() || this.isSleeping() || this.isKnockedOut();
    }

    // ------------------------------------------------------------------ geometry of the club

    /** Angle in degrees of a point off the animal's nose (0 = dead ahead, 180 = behind), and the side: +1 = its left. */
    private double offNose(Vec3 at) {
        Vec3 fwd = Vec3.directionFromRotation(0.0F, this.yBodyRot);
        Vec3 to = new Vec3(at.x - this.getX(), 0.0D, at.z - this.getZ());
        if (to.lengthSqr() < 1.0E-6D) {
            return 0.0D;
        }
        to = to.normalize();
        return Math.toDegrees(Math.acos(Math.max(-1.0D, Math.min(1.0D, fwd.x * to.x + fwd.z * to.z))));
    }

    private int sideOf(Vec3 at) {
        double yaw = Math.toRadians(this.yBodyRot);
        // a mob facing yaw 0 looks south (+z): its left is east (+x)
        double lx = Math.cos(yaw);
        double lz = Math.sin(yaw);
        return (at.x - this.getX()) * lx + (at.z - this.getZ()) * lz >= 0.0D ? 1 : -1;
    }

    private boolean inArc(Entity e) {
        double d = this.distanceTo(e) - e.getBbWidth() * 0.5D;
        double reach = CLUB_REACH * this.getScale();
        return d <= reach && d >= CLUB_INNER * this.getScale() * 0.5D && this.offNose(e.position()) >= ARC_FROM
                && e.getY() < this.getY() + 2.5D * this.getScale();
    }

    /** Turns the body so the target lies off its rear quarter (about 130 degrees off the nose), on the side it is on. */
    private void presentClub(Entity target) {
        int side = this.sideOf(target.position());
        double toTarget = Math.toDegrees(Math.atan2(target.getZ() - this.getZ(), target.getX() - this.getX())) - 90.0D;
        float want = (float) (toTarget - side * 130.0D);
        float now = this.yBodyRot;
        float diff = net.minecraft.util.Mth.wrapDegrees(want - now);
        float step = net.minecraft.util.Mth.clamp(diff, -9.0F, 9.0F);
        this.setYRot(now + step);
        this.yBodyRot = now + step;
        this.yHeadRot = this.yBodyRot;
    }

    private boolean swing(Entity at) {
        if (this.swingCooldown > 0 || this.isBaby() || this.busy() || this.hunkering > 0) {
            return false;
        }
        this.swingSide = this.sideOf(at.position());
        triggerAnim(ACTION_CONTROLLER, this.swingSide > 0 ? "club_l" : "club_r");
        this.swingHitIn = SWING_HIT;
        this.swingCooldown = SWING_COOLDOWN;
        this.getNavigation().stop();
        return true;
    }

    /** Ridden: the rider looking off to the side or behind (past the start of the arc) swings the club to that side;
     *  looking ahead, the head hook as on every mount. */
    @Override
    public void riderAttack(net.minecraft.server.level.ServerPlayer rider) {
        Vec3 look = rider.getViewVector(1.0F);
        Vec3 at = this.position().add(look.x * 3.0D, 0.0D, look.z * 3.0D);
        if (this.offNose(at) < ARC_FROM || this.isBaby()) {
            super.riderAttack(rider);
            return;
        }
        if (this.swingCooldown > 0 || this.isKnockedOut() || this.isSleeping()) {
            return;
        }
        this.swingSide = this.sideOf(at);
        triggerAnim(ACTION_CONTROLLER, this.swingSide > 0 ? "club_l" : "club_r");
        this.swingHitIn = SWING_HIT;
        this.swingCooldown = SWING_COOLDOWN;
    }

    /** The blow: everything in the club's arc on the swing's side takes the club, knocked away sideways. */
    private void clubBlow() {
        double reach = CLUB_REACH * this.getScale() + 1.0D;
        LivingEntity owner = this.getOwner();
        List<LivingEntity> hit = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(reach, 1.0D, reach),
                e -> e != this && e.isAlive() && !e.isSpectator() && e != owner && !this.hasPassenger(e)
                        && !(e instanceof Player p && p.isCreative())
                        && !(e instanceof DinosaurEntity d && d.isTame() && owner != null && d.getOwner() == owner)
                        && this.inArc(e) && this.sideOf(e.position()) == this.swingSide);
        double yaw = Math.toRadians(this.yBodyRot);
        double lx = Math.cos(yaw) * this.swingSide;
        double lz = Math.sin(yaw) * this.swingSide;
        float base = (float) this.getAttributeValue(Attributes.ATTACK_DAMAGE);
        for (LivingEntity e : hit) {
            float dmg = e instanceof DinosaurEntity ? base : (float) (base * Rules.damageDealt(this, e));
            if (e.hurt(this.damageSources().mobAttack(this), dmg)) {
                // knockback(strength, x, z) pushes toward -(x, z): away from the animal, to the swing's side
                e.knockback(1.4D, -lx, -lz);
                this.setLastHurtMob(e);
            }
        }
        if (!hit.isEmpty()) {
            this.playSound(net.minecraft.sounds.SoundEvents.ANVIL_LAND, 0.4F, 0.55F);
        }
    }

    // ------------------------------------------------------------------ hurt and hunker

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (this.hunkering > 0 && !source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_ARMOR)) {
            amount *= 0.5F;     // flat on its belly, only armour faces the blow
        }
        return super.hurt(source, amount);
    }

    private void hunker() {
        triggerAnim(ACTION_CONTROLLER, "hunker");
        this.hunkering = 64;
        this.still = 64;
        this.warnCooldown = 120;
    }

    // ------------------------------------------------------------------ taming off the ground

    /** A wild adult does not take food from a stranger's hand: it says to drop it in front of it. */
    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!this.isTame() && !this.isBaby() && !this.isKnockedOut() && this.isFood(stack)) {
            if (!this.level().isClientSide()) {
                player.displayClientMessage(Component.translatable("message.terrassic.eats_from_ground", this.getDisplayName()), true);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide());
        }
        return super.mobInteract(player, hand);
    }

    private Vec3 beak() {
        Vec3 fwd = Vec3.directionFromRotation(0.0F, this.yBodyRot);
        double ahead = 3.4D * this.getScale();
        return new Vec3(this.getX() + fwd.x * ahead, this.getY(), this.getZ() + fwd.z * ahead);
    }

    private void lookForMeal() {
        if (this.meal != null && (!this.meal.isAlive() || this.meal.distanceToSqr(this) > 144.0D)) {
            this.meal = null;
        }
        if (this.meal == null && this.tickCount % 10 == 0) {
            List<ItemEntity> near = this.level().getEntitiesOfClass(ItemEntity.class, this.getBoundingBox().inflate(6.0D, 2.0D, 6.0D),
                    i -> i.isAlive() && i.onGround() && this.isFood(i.getItem()) && i.getOwner() instanceof Player);
            this.meal = near.isEmpty() ? null : near.get(0);
        }
        if (this.meal == null) {
            return;
        }
        Vec3 at = this.meal.position();
        if (this.beak().distanceToSqr(at.x, this.getY(), at.z) < 1.6D * 1.6D) {
            this.getNavigation().stop();
            this.getLookControl().setLookAt(at.x, at.y, at.z);
            this.eatMeal(this.meal);
            this.meal = null;
        } else if (this.getNavigation().isDone() || this.tickCount % 20 == 0) {
            // walk so the beak, not the hips, ends over the food
            Vec3 fwd = at.subtract(this.position()).normalize();
            Vec3 stand = at.subtract(fwd.scale(3.0D * this.getScale()));
            this.getNavigation().moveTo(stand.x, at.y, stand.z, 0.9D);
        }
    }

    private void eatMeal(ItemEntity item) {
        Player thrower = item.getOwner() instanceof Player p ? p : null;
        // whoever dropped it has to be where it can see them, not standing behind it in the arc of the club
        if (thrower != null && this.distanceToSqr(thrower) < 64.0D && this.offNose(thrower.position()) > 110.0D) {
            this.warnCooldown = 0;
            this.warn(thrower);
            return;
        }
        ItemStack stack = item.getItem();
        stack.shrink(1);
        if (stack.isEmpty()) {
            item.discard();
        } else {
            item.setItem(stack);
        }
        triggerAnim(ACTION_CONTROLLER, "eat");
        this.still = 50;
        this.feed(10);
        if (thrower == null || this.isTame() || this.isBaby() || !this.canBeTamedNow() || thrower.distanceToSqr(this) > 24.0D * 24.0D) {
            return;
        }
        int chance = Research.isStudied(thrower, this.speciesId()) ? Math.max(2, this.tameChance() - 1) : this.tameChance();
        if (this.random.nextDouble() < Rules.of(this.level()).get(Rule.TAMING_SPEED) / chance) {
            this.grantTamingBonus(100);      // fed without a fight: full effectiveness
            this.tameBy(thrower);
        } else {
            this.level().broadcastEntityEvent(this, (byte) 6);
            thrower.displayClientMessage(Component.translatable("message.terrassic.tame_try", this.getDisplayName(), chance), true);
        }
    }

    // ------------------------------------------------------------------ the warning

    private void warn(Entity at) {
        if (this.warnCooldown > 0 || this.isBaby()) {
            return;
        }
        this.warnCooldown = 70;
        this.presentClub(at);
        triggerAnim(ACTION_CONTROLLER, "club_warn");
        this.still = Math.max(this.still, 40);
        if (at instanceof Player p) {
            this.notice(p, ModNetwork.NOTICE_BLOOD, Component.translatable("hud.terrassic.notice.club_warn"), this.speciesName());
        }
    }

    /** A player standing close behind a wild adult, in the club's arc: warned once, clubbed if they stay. */
    private void watchBehind() {
        for (Player p : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(CLUB_REACH * this.getScale() + 1.0D),
                p -> p.isAlive() && !p.isCreative() && !p.isSpectator())) {
            if (!this.inArc(p) || this.offNose(p.position()) < 100.0D) {
                this.behind.remove(p.getUUID());
                continue;
            }
            int t = this.behind.merge(p.getUUID(), 10, Integer::sum);
            if (t == 10) {
                this.warnCooldown = 0;
                this.warn(p);
            } else if (t >= 60) {
                this.behind.remove(p.getUUID());
                this.swing(p);
            }
        }
    }

    // ------------------------------------------------------------------ the brain

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!this.level().isClientSide() && !this.busy() && this.getTarget() == null && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "snort");
        }
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.swingCooldown > 0) {
            this.swingCooldown--;
        }
        if (this.warnCooldown > 0) {
            this.warnCooldown--;
        }
        if (this.hunkering > 0) {
            this.hunkering--;
        }
        if (this.swingHitIn >= 0 && --this.swingHitIn < 0) {
            this.clubBlow();
        }
        if (this.still > 0) {
            this.still--;
            this.getNavigation().stop();
            return;
        }
        if (this.busy() || this.getTarget() != null || this.isBaby()) {
            return;
        }
        if (!this.isTame()) {
            if (this.tickCount % 10 == 0) {
                this.watchBehind();
                // a wild predator about: back to it and the club up; one at its head: flat on its belly
                List<PredatorDinosaur> near = this.level().getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(10.0D),
                        p -> p.isAlive() && !p.isTame() && !p.isBaby() && this.hasLineOfSight(p));
                if (!near.isEmpty()) {
                    PredatorDinosaur pr = near.get(0);
                    if (this.distanceTo(pr) < 5.0D * this.getScale() + 2.0D && this.offNose(pr.position()) < 50.0D && this.warnCooldown == 0) {
                        this.hunker();
                    } else {
                        this.warn(pr);
                    }
                    return;
                }
            }
            this.lookForMeal();
            if (this.meal != null) {
                return;
            }
        }
        if (!this.getNavigation().isDone() || this.random.nextInt(700) != 0) {
            return;
        }
        this.idleAct();
    }

    private void idleAct() {
        if (this.isInWater() || this.waterInFront()) {
            triggerAnim(ACTION_CONTROLLER, "drink");
            this.still = 70;
            return;
        }
        if (!this.isTame() && !this.isFemale()) {
            Ankylosaurid rival = this.nearestMale();
            if (rival != null && this.random.nextInt(3) == 0) {
                // side by side, facing the same way: each clubs the other's flank (to its left / right)
                rival.setYRot(this.yBodyRot);
                rival.yBodyRot = this.yBodyRot;
                this.getLookControl().setLookAt(rival, 30.0F, 30.0F);
                triggerAnim(ACTION_CONTROLLER, "flank_club");
                rival.triggerAnim(ACTION_CONTROLLER, "flank_club");
                this.still = 60;
                rival.still = 60;
                return;
            }
        }
        triggerAnim(ACTION_CONTROLLER, "dig");
        this.still = 64;
        this.feed(4);
    }

    private boolean waterInFront() {
        Vec3 b = this.beak();
        BlockPos p = BlockPos.containing(b.x, this.getY() - 0.5D, b.z);
        return this.level().getFluidState(p).is(FluidTags.WATER) || this.level().getFluidState(p.above()).is(FluidTags.WATER);
    }

    private Ankylosaurid nearestMale() {
        Ankylosaurid best = null;
        double bestD = Double.MAX_VALUE;
        for (Ankylosaurid e : this.level().getEntitiesOfClass(Ankylosaurid.class, this.getBoundingBox().inflate(5.0D),
                o -> o != this && o.isAlive() && !o.isFemale() && !o.isBaby() && !o.isTame() && !o.busy() && o.getTarget() == null)) {
            double d = this.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }

    /**
     * The club defence: in place of the melee chase. Close: present the club and swing when the target is in its arc;
     * at the head: the head hook. Farther: a tame one walks to its target, a wild one stands and warns, and drops a
     * target that stays away.
     */
    private class ClubDefenceGoal extends Goal {
        ClubDefenceGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = Ankylosaurid.this.getTarget();
            return t != null && t.isAlive() && !Ankylosaurid.this.isBaby() && !Ankylosaurid.this.busy();
        }

        @Override
        public void start() {
            Ankylosaurid.this.lostTarget = 0;
        }

        @Override
        public void tick() {
            Ankylosaurid a = Ankylosaurid.this;
            LivingEntity t = a.getTarget();
            if (t == null) {
                return;
            }
            double d = a.distanceTo(t);
            double reach = CLUB_REACH * a.getScale();
            if (d > reach + 1.5D) {
                if (a.isTame()) {
                    a.getNavigation().moveTo(t, 1.2D);
                } else {
                    a.getNavigation().stop();
                    a.getLookControl().setLookAt(t, 30.0F, 30.0F);
                    if (d < 12.0D) {
                        a.warn(t);
                    }
                    if (++a.lostTarget > 160) {
                        a.setTarget(null);       // it defends its ground, it does not hunt
                    }
                }
                return;
            }
            a.lostTarget = 0;
            a.getNavigation().stop();
            if (a.inArc(t)) {
                a.swing(t);
            } else if (a.offNose(t.position()) < 45.0D && d < 2.6D * a.getScale() + 1.5D && a.swingCooldown == 0) {
                a.getLookControl().setLookAt(t, 30.0F, 30.0F);
                a.doHurtTarget(t);          // the head hook ("attack")
                a.swingCooldown = 24;
            }
            if (a.swingHitIn < 0) {
                a.presentClub(t);
            }
        }
    }
}
