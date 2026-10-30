package com.terrassic.entity.ai;

import com.terrassic.entity.FlyingDinosaur;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;
import java.util.List;

/**
 * Wild pterosaurs and birds soaring high over the land in flocks (docs/REGRAS.md, "Ecossistema").
 *
 * <p>A soaring flight lasts one to three minutes ({@link FlyingDinosaur#isSoaring()}); then the animal glides down and
 * rests for a while before taking off again. It flies by daylight only (by night for nocturnal species). The flock
 * is every soaring wild one of the species within 32 blocks: the one with the lowest entity id leads, picking
 * waypoints 24 to 56 blocks ahead, 18 to 30 blocks over the ground, heading home after straying 72 blocks.
 * Followers trail the leader's movement with separation rather than converge on its waypoint. FlightSteering
 * maintains forward speed and limits yaw changes; terrain targets only query chunks already loaded.
 */
public class SoarGoal extends Goal {
    private static final double FLOCK_RANGE = 32.0D;
    private static final double STRAY = 72.0D;

    private final FlyingDinosaur bird;
    private int retarget;
    private int flockRefresh;
    private FlyingDinosaur cachedLeader;
    private List<? extends FlyingDinosaur> neighbours = List.of();
    private Vec3 waypoint;

    public SoarGoal(FlyingDinosaur bird) {
        this.bird = bird;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean free() {
        return !this.bird.isTame() && !this.bird.isBaby() && !this.bird.isKnockedOut() && !this.bird.isColonist() && !this.bird.isOrderedToSit() && !this.bird.isVehicle()
                && !this.bird.isPassenger() && !this.bird.isSleeping() && !this.bird.isLeashed() && this.bird.getTarget() == null
                && !this.bird.isSleepTime();
    }

    @Override
    public boolean canUse() {
        if (!this.free() || this.bird.isResting()) {
            return false;
        }
        // A wild adult already airborne must recover flight immediately, including after loading an old world.
        return this.bird.isSoaring() || this.bird.isFlying()
                || this.bird.getRandom().nextInt(reducedTickDelay(200)) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return this.free() && this.bird.isSoaring();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        if (!this.bird.isSoaring()) {
            this.bird.beginSoar();
        }
        this.bird.getNavigation().stop();
        this.bird.setCruising(true);
        if (this.bird.onGround() || this.bird.isInWater()) {
            Vec3 v = this.bird.getDeltaMovement();
            this.bird.setDeltaMovement(v.x, 0.6D, v.z);
        }
        this.retarget = 0;
        this.flockRefresh = 0;
        this.waypoint = null;
    }

    @Override
    public void stop() {
        this.bird.setCruising(false);
        this.bird.setSoarTarget(null);
        this.neighbours = List.of();
        this.cachedLeader = null;
        this.waypoint = null;
        if (!this.bird.isSoaring() || this.bird.isSleepTime()) {
            this.bird.endSoar();
        }
    }

    @Override
    public void tick() {
        if (--this.flockRefresh <= 0) {
            this.flockRefresh = 10;
            this.refreshFlock();
        }
        Vec3 target = this.waypoint;
        if (this.bird.onGround() && this.bird.soarTicksLeft() < 200) {
            this.bird.endSoar();
            return;
        }
        if (this.bird.horizontalCollision && target != null) {
            // climb over the hill or tree in the way
            target = new Vec3(target.x, Math.min(this.bird.level().getMaxBuildHeight() - 4,
                    Math.max(target.y, this.bird.getY() + 6.0D)), target.z);
        }
        if (target == null || --this.retarget <= 0 || this.bird.position().distanceToSqr(target) < 144.0D) {
            target = this.pickTarget();
        }
        if (target != null) {
            // A close neighbour changes the heading gradually, rather than pushing everyone into one waypoint.
            Vec3 separation = Vec3.ZERO;
            for (FlyingDinosaur other : this.neighbours) {
                if (!other.isAlive()) continue;
                double gap = Math.max(5.0D, (this.bird.getBbWidth() + other.getBbWidth()) * 1.5D);
                Vec3 away = this.bird.position().subtract(other.position());
                double distance = away.length();
                if (distance < gap) {
                    if (distance < 0.01D) {
                        away = Vec3.directionFromRotation(0, this.bird.getId() < other.getId() ? 90 : -90);
                    } else {
                        away = away.scale(1.0D / distance);
                    }
                    separation = separation.add(away.scale((gap - distance) / gap));
                }
            }
            if (separation.lengthSqr() > 1.0D) separation = separation.normalize();
            Vec3 steering = target.add(separation.scale(18.0D));
            this.bird.setSoarTarget(steering);
            // Keep the unmodified waypoint separately: separation must not accumulate every tick.
            this.waypoint = target;
        }
    }

    /** The leader's next waypoint, or a place around the leader's for a follower. */
    private Vec3 pickTarget() {
        FlyingDinosaur leader = this.leader();
        if (leader != this.bird && leader.isCruising() && this.bird.soarTicksLeft() >= 200) {
            // Follow the leader's motion with a loose trailing formation, not its destination.
            long seed = this.bird.getUUID().getLeastSignificantBits();
            Vec3 forward = Vec3.directionFromRotation(0, leader.getYRot());
            Vec3 side = new Vec3(forward.z, 0, -forward.x);
            double gap = Math.max(7.0D, this.bird.getBbWidth() * 2.0D);
            double lateral = ((seed & 1) == 0 ? -1 : 1) * gap * (1.0D + ((seed >>> 1) & 3) * 0.5D);
            double behind = gap * (1.0D + ((seed >>> 3) & 3));
            this.retarget = 10;
            Vec3 formation = leader.position().add(forward.scale(28.0D - behind)).add(side.scale(lateral))
                    .add(0, (((seed >>> 5) & 3) - 1.5D) * 1.5D, 0);
            if (this.bird.level().hasChunk(Mth.floor(formation.x) >> 4, Mth.floor(formation.z) >> 4)) {
                return formation;
            }
        }
        this.retarget = 100 + this.bird.getRandom().nextInt(100);
        Vec3 home = this.bird.getSoarHome();
        float yaw = this.bird.getYRot() + (this.bird.getRandom().nextFloat() * 70.0F - 35.0F);
        boolean strayed = home != null && Math.hypot(home.x - this.bird.getX(), home.z - this.bird.getZ()) > STRAY;
        boolean ending = this.bird.soarTicksLeft() < 200;
        if (home != null && (strayed || ending)) {
            // turn for home (the angle Minecraft uses: x = -sin(yaw), z = cos(yaw))
            yaw = (float) (Mth.atan2(home.z - this.bird.getZ(), home.x - this.bird.getX()) * Mth.RAD_TO_DEG) - 90.0F
                    + (this.bird.getRandom().nextFloat() * 40.0F - 20.0F);
        }
        double distance = 24.0D + this.bird.getRandom().nextDouble() * 32.0D;
        double x = this.bird.getX() - Mth.sin(yaw * Mth.DEG_TO_RAD) * distance;
        double z = this.bird.getZ() + Mth.cos(yaw * Mth.DEG_TO_RAD) * distance;
        int bx = Mth.floor(x);
        int bz = Mth.floor(z);
        if (!this.bird.level().hasChunk(bx >> 4, bz >> 4)) {
            // the edge of the loaded world: circle back over known ground
            if (home == null) {
                return null;
            }
            x = home.x;
            z = home.z;
            bx = Mth.floor(x);
            bz = Mth.floor(z);
            if (!this.bird.level().hasChunk(bx >> 4, bz >> 4)) {
                return null;
            }
        }
        if (!ending && !strayed && !this.habitat(bx, bz)) {
            // keep over its own country (a hill and forest flyer does not go out over the beach and the sea):
            // try the other side, else turn for home
            double back = yaw + 180.0F + (this.bird.getRandom().nextFloat() * 60.0F - 30.0F);
            int ox = Mth.floor(this.bird.getX() - Mth.sin((float) back * Mth.DEG_TO_RAD) * distance);
            int oz = Mth.floor(this.bird.getZ() + Mth.cos((float) back * Mth.DEG_TO_RAD) * distance);
            if (this.bird.level().hasChunk(ox >> 4, oz >> 4) && this.habitat(ox, oz)) {
                x = ox + 0.5D;
                z = oz + 0.5D;
            } else if (home != null && this.bird.level().hasChunk(Mth.floor(home.x) >> 4, Mth.floor(home.z) >> 4)) {
                x = home.x;
                z = home.z;
            }
            bx = Mth.floor(x);
            bz = Mth.floor(z);
        }
        int ground = this.bird.level().getHeight(Heightmap.Types.MOTION_BLOCKING, bx, bz);
        double y = ending ? ground + 0.5D : ground + 18 + this.bird.getRandom().nextInt(13);
        y = Math.min(y, this.bird.level().getMaxBuildHeight() - 8);
        return new Vec3(x, y, z);
    }

    /** Whether the species lives in the biome under (x, z): it is in that biome's spawn list. */
    private boolean habitat(int x, int z) {
        int ground = this.bird.level().getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
        for (net.minecraft.world.level.biome.MobSpawnSettings.SpawnerData data : this.bird.level().getBiome(new net.minecraft.core.BlockPos(x, ground, z))
                .value().getMobSettings().getMobs(net.minecraft.world.entity.MobCategory.CREATURE).unwrap()) {
            if (data.type == this.bird.getType()) {
                return true;
            }
        }
        return false;
    }

    /** The soaring wild one of the species with the lowest id within flock range (this bird if none is lower). */
    private FlyingDinosaur leader() {
        return this.cachedLeader != null && this.cachedLeader.isAlive() ? this.cachedLeader : this.bird;
    }

    private void refreshFlock() {
        FlyingDinosaur best = this.bird;
        AABB box = this.bird.getBoundingBox().inflate(FLOCK_RANGE);
        this.neighbours = this.bird.level().getEntitiesOfClass(this.bird.getClass(), box,
                e -> e != this.bird && e.isCruising() && !e.isTame() && !e.isBaby());
        for (FlyingDinosaur other : this.neighbours) {
            if (other.getId() < best.getId()) {
                best = other;
            }
        }
        this.cachedLeader = best;
    }
}
