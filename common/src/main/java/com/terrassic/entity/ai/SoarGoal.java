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
 * waypoints 24 to 56 blocks ahead, 14 to 40 blocks over the ground, turning gently and heading back when it strays
 * 72 blocks from where it took off; the others hold a place of their own around the leader's waypoint, so the flock
 * keeps its shape. It steers the move control straight at the waypoint (no path finding up there), climbing over
 * whatever it bumps into, and never pulls an unloaded chunk in.
 */
public class SoarGoal extends Goal {
    private static final double FLOCK_RANGE = 32.0D;
    private static final double STRAY = 72.0D;

    private final FlyingDinosaur bird;
    private int retarget;

    public SoarGoal(FlyingDinosaur bird) {
        this.bird = bird;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean free() {
        return !this.bird.isTame() && !this.bird.isBaby() && !this.bird.isOrderedToSit() && !this.bird.isVehicle()
                && !this.bird.isPassenger() && !this.bird.isSleeping() && !this.bird.isLeashed() && this.bird.getTarget() == null
                && !this.bird.isSleepTime();
    }

    @Override
    public boolean canUse() {
        if (!this.free() || this.bird.isResting()) {
            return false;
        }
        return this.bird.isSoaring() || this.bird.getRandom().nextInt(reducedTickDelay(200)) == 0;
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
        if (this.bird.onGround() || this.bird.isInWater()) {
            Vec3 v = this.bird.getDeltaMovement();
            this.bird.setDeltaMovement(v.x, 0.6D, v.z);
        }
        this.retarget = 0;
    }

    @Override
    public void stop() {
        if (!this.bird.isSoaring()) {
            this.bird.endSoar();
        }
    }

    @Override
    public void tick() {
        Vec3 target = this.bird.getSoarTarget();
        if (this.bird.horizontalCollision && target != null) {
            // climb over the hill or tree in the way
            target = new Vec3(target.x, Math.max(target.y, this.bird.getY()) + 6.0D, target.z);
            this.bird.setSoarTarget(target);
        }
        if (target == null || --this.retarget <= 0 || this.bird.position().distanceToSqr(target) < 16.0D) {
            target = this.pickTarget();
            this.bird.setSoarTarget(target);
        }
        if (target != null) {
            double speed = this.bird.position().distanceToSqr(target) > 400.0D ? 1.15D : 1.0D;
            this.bird.getMoveControl().setWantedPosition(target.x, target.y, target.z, speed);
        }
    }

    /** The leader's next waypoint, or a place around the leader's for a follower. */
    private Vec3 pickTarget() {
        FlyingDinosaur leader = this.leader();
        if (leader != this.bird && leader.getSoarTarget() != null) {
            // a place of its own in the formation, fixed by its uuid
            long seed = this.bird.getUUID().getLeastSignificantBits();
            double ox = ((seed & 15L) - 7.5D) * 0.9D;
            double oy = (((seed >> 4) & 7L) - 3.5D) * 0.6D;
            double oz = (((seed >> 8) & 15L) - 7.5D) * 0.9D;
            this.retarget = 10;
            return leader.getSoarTarget().add(ox, oy, oz);
        }
        this.retarget = 100 + this.bird.getRandom().nextInt(100);
        Vec3 home = this.bird.getSoarHome();
        float yaw = this.bird.getYRot() + (this.bird.getRandom().nextFloat() * 140.0F - 70.0F);
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
        int ground = this.bird.level().getHeight(Heightmap.Types.MOTION_BLOCKING, bx, bz);
        double y = ground + 14 + this.bird.getRandom().nextInt(27);
        y = Math.min(y, this.bird.level().getMaxBuildHeight() - 8);
        return new Vec3(x, y, z);
    }

    /** The soaring wild one of the species with the lowest id within flock range (this bird if none is lower). */
    private FlyingDinosaur leader() {
        FlyingDinosaur best = this.bird;
        AABB box = this.bird.getBoundingBox().inflate(FLOCK_RANGE);
        List<? extends FlyingDinosaur> flock = this.bird.level().getEntitiesOfClass(this.bird.getClass(), box,
                e -> e != this.bird && e.isSoaring() && !e.isTame() && !e.isBaby());
        for (FlyingDinosaur other : flock) {
            if (other.getId() < best.getId()) {
                best = other;
            }
        }
        return best;
    }
}
