package com.terrassic.entity.ai;

import com.terrassic.entity.CarcassEntity;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.PredatorDinosaur;
import com.terrassic.entity.Tyrannosaurine;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The carcass thief (docs/estudos/13_PREDADORES_1_10.md, Daspletossauro, "No jogo" 2; a hypothesis from the scavenged
 * bones of Hone &amp; Tanke 2015 and the komodo-like gatherings of Roach &amp; Brinkman 2007): a hungry wild
 * {@link Tyrannosaurine} that sees another predator at a carcass walks in on it, stops a few steps short and roars at
 * it ("steal_roar"). A rival under half its size gives the carcass up (it is put off eating for a while and walks
 * away); an equal or a bigger one does not, and the roar turns into a fight for it (with the duel set, a duel that
 * ends when one gives in). Then the thief eats (EatCarcassGoal) and guards it (Tyrannosaurine).
 */
public class CarcassStealGoal extends Goal {
    private static final double LOOK = 24.0D;
    /** How close to the carcass a rival must stand to count as holding it (blocks past the half widths). */
    private static final double HOLDING = 3.5D;
    /** The roar: where the thief stops (blocks from the rival, past the half widths), the clip and the sound. */
    private static final double STOP = 4.0D;
    private static final int ROAR_TICKS = 60;
    private static final int SOUND_AT = 17;
    private static final int GIVE_UP_AT = 24;
    private static final int TIMEOUT = 400;
    /** How long the frightened one stays away from food. */
    private static final int SCARED_TICKS = 900;

    private final Tyrannosaurine mob;
    private CarcassEntity carcass;
    private DinosaurEntity rival;
    private int roarTick = -1;
    private int ticks;
    private int repath;

    public CarcassStealGoal(Tyrannosaurine mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    /** A meat eater (the predators; the scavenging rule of EatCarcassGoal). */
    public static boolean eatsMeat(DinosaurEntity e) {
        return e instanceof PredatorDinosaur;
    }

    @Override
    public boolean canUse() {
        if (!this.mob.wantsToSteal() || this.mob.getRandom().nextInt(reducedTickDelay(40)) != 0) {
            return false;
        }
        CarcassEntity best = null;
        DinosaurEntity holder = null;
        double bestD = LOOK * LOOK;
        for (CarcassEntity c : this.mob.level().getEntitiesOfClass(CarcassEntity.class, this.mob.getBoundingBox().inflate(LOOK),
                CarcassEntity::hasMeat)) {
            double d = this.mob.distanceToSqr(c);
            if (d >= bestD) {
                continue;
            }
            DinosaurEntity h = this.holder(c);
            if (h != null) {
                best = c;
                holder = h;
                bestD = d;
            }
        }
        this.carcass = best;
        this.rival = holder;
        return best != null;
    }

    /** The predator at the carcass (not its own kind: its mate shares). */
    private DinosaurEntity holder(CarcassEntity c) {
        double r = c.getBbWidth() * 0.5D + HOLDING + 3.0D;
        DinosaurEntity best = null;
        double bestD = Double.MAX_VALUE;
        for (DinosaurEntity e : this.mob.level().getEntitiesOfClass(DinosaurEntity.class, c.getBoundingBox().inflate(r),
                e -> e != this.mob && e.isAlive() && !e.isBaby() && eatsMeat(e) && !(e instanceof Tyrannosaurine)
                        && e.getTarget() == null && !e.isVehicle())) {
            double gap = Math.sqrt(e.distanceToSqr(c)) - e.getBbWidth() * 0.5D - c.getBbWidth() * 0.5D;
            if (gap <= HOLDING && gap < bestD) {
                bestD = gap;
                best = e;
            }
        }
        return best;
    }

    @Override
    public boolean canContinueToUse() {
        return this.carcass != null && this.carcass.isAlive() && this.carcass.hasMeat() && this.rival != null
                && this.rival.isAlive() && this.ticks < TIMEOUT && this.mob.getTarget() == null && !this.mob.isVehicle()
                && !this.mob.isSleeping() && !this.mob.isKnockedOut();
    }

    @Override
    public void start() {
        this.roarTick = -1;
        this.ticks = 0;
        this.repath = 0;
        this.mob.getNavigation().moveTo(this.rival, 1.0D);
        this.mob.logAct("steal carcass: walks in on a " + this.rival.speciesId());
    }

    @Override
    public void stop() {
        this.carcass = null;
        this.rival = null;
        this.roarTick = -1;
        this.mob.carcassActDone(200);
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        this.ticks++;
        this.mob.getLookControl().setLookAt(this.rival, 30.0F, 30.0F);
        if (this.roarTick < 0) {
            double gap = Math.sqrt(this.mob.distanceToSqr(this.rival)) - this.mob.getBbWidth() * 0.5D - this.rival.getBbWidth() * 0.5D;
            if (gap > STOP * this.mob.getScale()) {
                if (--this.repath <= 0) {
                    this.repath = 20;
                    this.mob.getNavigation().moveTo(this.rival, 1.0D);
                }
                return;
            }
            this.mob.getNavigation().stop();
            this.roarTick = 0;
            this.mob.stealRoar(this.rival);
            this.mob.logAct("steal carcass: roars at the " + this.rival.speciesId());
            // the one on the carcass looks up at it
            this.rival.getLookControl().setLookAt(this.mob, 30.0F, 30.0F);
            return;
        }
        int t = this.roarTick++;
        this.mob.getNavigation().stop();
        this.face();
        if (t == SOUND_AT) {
            this.mob.stealRoarSound();
        }
        if (t == GIVE_UP_AT) {
            if (this.mob.frightens(this.rival)) {
                this.mob.logAct("steal carcass: the " + this.rival.speciesId() + " gives it up");
                // it gives the carcass up: put off food for a while, it walks away from the thief
                this.rival.setSated(SCARED_TICKS);
                this.rival.getNavigation().stop();
                Vec3 away = this.rival.position().subtract(this.mob.position()).multiply(1.0D, 0.0D, 1.0D);
                if (away.lengthSqr() < 1.0E-4D) {
                    away = new Vec3(1.0D, 0.0D, 0.0D);
                }
                Vec3 to = this.rival.position().add(away.normalize().scale(16.0D));
                this.rival.getNavigation().moveTo(to.x, to.y, to.z, 1.3D);
            } else {
                // an equal or a bigger one: it has to be fought for
                this.mob.logAct("steal carcass: the " + this.rival.speciesId() + " stands, they fight");
                this.mob.setTarget(this.rival);
                this.rival.setTarget(this.mob);
            }
        }
        if (t >= ROAR_TICKS) {
            this.carcass = null;            // done: EatCarcassGoal takes it from here
        }
    }

    private void face() {
        double dx = this.rival.getX() - this.mob.getX();
        double dz = this.rival.getZ() - this.mob.getZ();
        float yaw = Mth.approachDegrees(this.mob.getYRot(), (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F, 6.0F);
        this.mob.setYRot(yaw);
        this.mob.setYBodyRot(yaw);
    }
}
