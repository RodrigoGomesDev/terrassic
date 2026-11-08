package com.terrassic.entity.ai;

import com.terrassic.entity.Albertosaurine;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The drive (docs/estudos/13_PREDADORES_1_10.md, Albertossauro, "No jogo" 1; Currie 1998: the faster juveniles drove
 * the prey toward the adults, a hypothesis the Guide says is one): a juvenile of an {@link Albertosaurine} pack that
 * answered the call runs round the prey in a wide arc ("drive"), first out to its flank, then to its far side, and
 * from there comes at it, so the prey bolts away from it, toward the adults waiting crouched (PackAmbushGoal). It
 * never bites: when the prey is with the adults, or after a while, it is done.
 */
public class PackDriveGoal extends Goal {
    /** How far out of the prey the arc runs (blocks, at size 1), the speed, and how long the whole drive may take. */
    private static final double ARC = 9.0D;
    private static final double SPEED = 1.75D;
    private static final int TIMEOUT = 500;
    /** How close the prey must come to an adult for the drive to be done (blocks). */
    private static final double DELIVERED = 9.0D;

    private enum Phase { FLANK, FAR, PRESS }

    private final Albertosaurine mob;
    private Phase phase;
    private double side;
    private int ticks;
    private int repath;
    private int bolt;

    public PackDriveGoal(Albertosaurine mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private LivingEntity prey() {
        return this.mob.drivePrey;
    }

    @Override
    public boolean canUse() {
        LivingEntity prey = this.prey();
        Albertosaurine lead = this.mob.driveLeader;
        if (prey == null || lead == null || !this.mob.isDriver() || this.mob.isVehicle() || this.mob.isSleeping()
                || this.mob.isKnockedOut() || this.mob.isInSittingPose()) {
            return false;
        }
        if (!prey.isAlive() || !lead.isAlive() || prey instanceof Player p && (p.isCreative() || p.isSpectator())
                || this.mob.distanceToSqr(prey) > 48.0D * 48.0D || this.mob.tickCount - this.mob.driveSince > TIMEOUT) {
            this.mob.drivePrey = null;
            this.mob.driveLeader = null;
            return false;
        }
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity prey = this.prey();
        return prey != null && prey.isAlive() && this.mob.driveLeader != null && this.mob.driveLeader.isAlive()
                && this.ticks < TIMEOUT && !this.mob.isKnockedOut() && !this.mob.isVehicle()
                && this.mob.distanceToSqr(prey) < 56.0D * 56.0D && !(this.phase == Phase.PRESS && this.delivered());
    }

    @Override
    public void start() {
        this.phase = Phase.FLANK;
        this.ticks = 0;
        this.repath = 0;
        this.bolt = 0;
        // run round on the side of the prey it is already on (the shorter way round)
        Vec3 toPrey = this.prey().position().subtract(this.adults());
        Vec3 toMe = this.mob.position().subtract(this.prey().position());
        this.side = toPrey.x * toMe.z - toPrey.z * toMe.x >= 0.0D ? 1.0D : -1.0D;
        this.mob.setMode(Albertosaurine.MODE_DRIVE);
        this.mob.logAct("drive: runs round the " + this.prey().getType().toShortString() + " in an arc");
    }

    @Override
    public void stop() {
        if (this.phase == Phase.PRESS && this.delivered()) {
            this.mob.logAct("drive: the " + (this.prey() == null ? "prey" : this.prey().getType().toShortString())
                    + " is with the adults");
        } else {
            this.mob.logAct("drive: ends (" + this.ticks / 20 + " s)");
        }
        this.mob.drivePrey = null;
        this.mob.driveLeader = null;
        this.mob.setMode(Albertosaurine.MODE_NONE);
        this.mob.getNavigation().stop();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    /** Where the adults are: the middle of the grown packmates near the prey (the leader if none). */
    private Vec3 adults() {
        LivingEntity prey = this.prey();
        double x = 0.0D, z = 0.0D, y = 0.0D;
        int n = 0;
        for (Albertosaurine a : this.mob.level().getEntitiesOfClass(Albertosaurine.class, prey.getBoundingBox().inflate(40.0D),
                e -> e.isAlive() && !e.isBaby() && !e.isTame() && e.getType() == this.mob.getType())) {
            x += a.getX();
            y += a.getY();
            z += a.getZ();
            n++;
        }
        return n == 0 ? this.mob.driveLeader.position() : new Vec3(x / n, y / n, z / n);
    }

    private boolean delivered() {
        LivingEntity prey = this.prey();
        if (prey == null) {
            return false;
        }
        for (Albertosaurine a : this.mob.level().getEntitiesOfClass(Albertosaurine.class, prey.getBoundingBox().inflate(DELIVERED + 6.0D),
                e -> e.isAlive() && !e.isBaby() && !e.isTame() && e.getType() == this.mob.getType())) {
            double gap = Math.sqrt(a.distanceToSqr(prey)) - a.getBbWidth() * 0.5D - prey.getBbWidth() * 0.5D;
            if (gap < DELIVERED) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void tick() {
        this.ticks++;
        LivingEntity prey = this.prey();
        this.mob.getLookControl().setLookAt(prey, 30.0F, 30.0F);
        Vec3 p = prey.position();
        Vec3 away = p.subtract(this.adults()).multiply(1.0D, 0.0D, 1.0D);
        if (away.lengthSqr() < 1.0E-4D) {
            away = p.subtract(this.mob.position()).multiply(1.0D, 0.0D, 1.0D);
        }
        away = away.normalize();
        Vec3 across = new Vec3(-away.z, 0.0D, away.x).scale(this.side);
        double r = ARC * Math.max(0.6D, this.mob.getScale()) + prey.getBbWidth() * 0.5D;
        Vec3 goal = switch (this.phase) {
            case FLANK -> p.add(across.scale(r * 1.1D)).add(away.scale(r * 0.3D));
            case FAR -> p.add(away.scale(r)).add(across.scale(r * 0.35D));
            case PRESS -> p.add(away.scale(2.0D));
        };
        double d2 = this.mob.position().multiply(1.0D, 0.0D, 1.0D).distanceToSqr(goal.multiply(1.0D, 0.0D, 1.0D));
        if (this.phase == Phase.FLANK && d2 < 16.0D) {
            this.phase = Phase.FAR;
            this.repath = 0;
        } else if (this.phase == Phase.FAR && d2 < 16.0D) {
            this.phase = Phase.PRESS;
            this.repath = 0;
            this.mob.logAct("drive: behind the " + prey.getType().toShortString() + ", presses it toward the adults");
        }
        if (--this.repath <= 0) {
            this.repath = 8;
            this.mob.getNavigation().moveTo(goal.x, goal.y, goal.z, this.phase == Phase.PRESS ? SPEED * 0.85D : SPEED);
        }
        // pressed from behind, the prey bolts away from the juvenile: toward the adults
        if (this.phase == Phase.PRESS && --this.bolt <= 0 && prey instanceof PathfinderMob runner
                && !(prey instanceof DinosaurEntity d && d.isTame()) && !(prey instanceof Albertosaurine)
                && this.mob.distanceToSqr(prey) < (r + 6.0D) * (r + 6.0D)) {
            this.bolt = 20;
            Vec3 run = prey.position().subtract(this.mob.position()).multiply(1.0D, 0.0D, 1.0D);
            if (run.lengthSqr() > 1.0E-4D) {
                Vec3 to = prey.position().add(run.normalize().scale(14.0D));
                runner.getNavigation().moveTo(to.x, to.y, to.z, 1.5D);
                if (this.ticks % 60 < 20) {
                    this.mob.logAct("drive: the " + prey.getType().toShortString() + " bolts away from it");
                }
            }
        }
    }
}
