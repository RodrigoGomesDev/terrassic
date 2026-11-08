package com.terrassic.entity.ai;

import com.terrassic.entity.CarcassEntity;
import com.terrassic.entity.Carcharodontosaurine;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The Carcharodontosaurus drags its kill (docs/estudos/13, "No jogo" 3; Henderson &amp; Nicholls 2015 measured the load
 * it could lift: a hypothesis of behaviour). Right after a kill, a small or middling carcass is hauled a few blocks
 * backwards, the jaws on it ("drag"), into the shade under the leaves when there is shade near, else away from the
 * water, else straight back; then the ordinary scavenging (EatCarcassGoal) eats it there. Its own goal, ahead of the
 * eating one (a higher priority), so the shared goal stays as it is.
 */
public class CarcassDragGoal extends Goal {
    private static final int MAX_TICKS = 240;

    private final Carcharodontosaurine mob;
    private CarcassEntity carcass;
    private Vec3 dest;
    private Vec3 from;
    private int ticks;
    private int still;
    private double lastD;

    public CarcassDragGoal(Carcharodontosaurine mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if ((this.mob.tickCount + this.mob.getId()) % 5 != 0) {
            return false;
        }
        this.carcass = this.mob.carcassToDrag();
        return this.carcass != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.carcass != null && this.carcass.isAlive() && this.carcass.hasMeat() && this.mob.getTarget() == null
                && !this.mob.isVehicle() && !this.mob.isInSittingPose() && !this.mob.isKnockedOut() && this.ticks < MAX_TICKS
                && this.dest != null && this.flat(this.mob.position(), this.dest) > 0.8D && this.still < 40;
    }

    private double flat(Vec3 a, Vec3 b) {
        double dx = a.x - b.x;
        double dz = a.z - b.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

    @Override
    public void start() {
        this.ticks = 0;
        this.still = 0;
        this.from = this.mob.position();
        this.dest = this.mob.dragDestination();
        this.lastD = this.flat(this.from, this.dest);
        this.mob.getNavigation().stop();
        this.mob.dragStarted(this.carcass);
        this.mob.logAct(String.format("drags the %s carcass toward %s, %.0f blocks", this.carcass.speciesId(),
                this.mob.shadeAt(this.dest) ? "the shade" : "away", this.lastD));
    }

    @Override
    public void stop() {
        if (this.carcass != null && this.from != null) {
            this.mob.logAct(String.format("drag ends: the %s carcass hauled %.1f blocks%s", this.carcass.speciesId(),
                    this.flat(this.from, this.mob.position()), this.mob.shadeAt(this.mob.position()) ? ", in the shade" : ""));
        }
        this.mob.dragEnded();
        this.mob.getNavigation().stop();
        this.carcass = null;
        this.dest = null;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        this.ticks++;
        Vec3 pos = this.mob.position();
        Vec3 way = new Vec3(this.dest.x - pos.x, 0.0D, this.dest.z - pos.z);
        double d = way.length();
        if (d < 1.0E-3D) {
            return;
        }
        Vec3 dir = way.scale(1.0D / d);
        // it walks backwards, facing the carcass it pulls (the carcass trails in front of its jaws)
        float face = (float) (Mth.atan2(-dir.z, -dir.x) * Mth.RAD_TO_DEG) - 90.0F;
        float y = Mth.approachDegrees(this.mob.getYRot(), face, 8.0F);
        this.mob.setYRot(y);
        this.mob.setYBodyRot(y);
        this.mob.setYHeadRot(y);
        this.mob.getNavigation().stop();
        double pace = this.mob.getAttributeValue(Attributes.MOVEMENT_SPEED) * 0.45D;
        Vec3 v = this.mob.getDeltaMovement();
        this.mob.setDeltaMovement(v.x + (dir.x * pace - v.x) * 0.35D, v.y, v.z + (dir.z * pace - v.z) * 0.35D);
        if (this.mob.horizontalCollision && this.mob.onGround()) {
            this.mob.getJumpControl().jump();
        }
        // the carcass at its jaws: a head's length in front of the body, on the ground under it
        double hold = this.mob.getBbWidth() * 0.5D + this.carcass.getBbWidth() * 0.35D + 1.6D * this.mob.getScale();
        double r = Math.toRadians(y);
        Vec3 jaws = new Vec3(pos.x - Math.sin(r) * hold, pos.y, pos.z + Math.cos(r) * hold);
        this.carcass.setPos(jaws.x, pos.y, jaws.z);
        this.carcass.setYRot(y);
        this.mob.getLookControl().setLookAt(this.carcass, 30.0F, 30.0F);
        if (d > this.lastD - 0.01D) {
            this.still++;
        } else {
            this.still = 0;
        }
        this.lastD = d;
    }
}
