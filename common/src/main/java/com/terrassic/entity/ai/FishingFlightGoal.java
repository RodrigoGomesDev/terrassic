package com.terrassic.entity.ai;

import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.world.PteroColonies;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.AbstractFish;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;
import java.util.List;

/**
 * A colony's fishing party (world/PteroColonies, docs: Pteranodonte, colônias): by day a colonist leaves now and then
 * for the open sea, 64 to 160 blocks off the coast, calling one to four idle colony mates along. Out there they glide
 * 14 to 30 blocks over the water, dip down to the surface now and then and snatch any fish near it, and after a few
 * minutes (or at dusk) they fly home and drop onto the colony. It drives the cruise flight of {@link FlyingDinosaur}
 * (FlightSteering) through the soar target, like {@link SoarGoal}.
 */
public class FishingFlightGoal extends Goal {
    private static final int OUT = 0;
    private static final int FISH = 1;
    private static final int HOME = 2;

    private final FlyingDinosaur bird;
    private int cooldown;
    private int phase;
    private int timer;
    private int retarget;
    private Vec3 sea;
    private Vec3 target;
    /** Ticks until the beak closes in a scoop under way (0 = none), whether the plunge is under way, and whether the
     *  current target is a dip to the surface. */
    private int strike;
    private boolean diving;
    private boolean dip;

    public FishingFlightGoal(FlyingDinosaur bird) {
        this.bird = bird;
        this.cooldown = 200 + bird.getRandom().nextInt(1200);
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean free() {
        return this.bird.isColonist() && !this.bird.isBaby() && !this.bird.isKnockedOut() && !this.bird.isVehicle()
                && !this.bird.isPassenger() && !this.bird.isLeashed() && this.bird.getTarget() == null;
    }

    @Override
    public boolean canUse() {
        if (!this.free() || !this.bird.level().isDay()) {
            return false;
        }
        if (this.bird.hasSortieCall()) {
            this.sea = this.bird.takeSortieCall();
            return true;
        }
        if (--this.cooldown > 0) {
            return false;
        }
        this.cooldown = 1200 + this.bird.getRandom().nextInt(2400);   // one to three minutes between sorties
        this.sea = PteroColonies.seaPoint(this.bird.level(), this.bird.getColonyHome(), this.bird.getRandom());
        if (this.sea == null) {
            return false;
        }
        this.callMates();
        return true;
    }

    /** One to four idle colony mates come along, each to a spot near the same patch of sea. */
    private void callMates() {
        BlockPos home = this.bird.getColonyHome();
        List<FlyingDinosaur> mates = this.bird.level().getEntitiesOfClass(FlyingDinosaur.class, this.bird.getBoundingBox().inflate(24.0D),
                e -> e != this.bird && e.getType() == this.bird.getType() && e.isColonist() && home.equals(e.getColonyHome())
                        && !e.isBaby() && !e.isCruising() && !e.hasSortieCall());
        int want = 1 + this.bird.getRandom().nextInt(4);
        for (int i = 0; i < Math.min(want, mates.size()); i++) {
            double a = this.bird.getRandom().nextDouble() * Math.PI * 2.0D;
            mates.get(i).callToSortie(this.sea.add(Math.cos(a) * 10.0D, 0.0D, Math.sin(a) * 10.0D));
        }
    }

    @Override
    public boolean canContinueToUse() {
        return this.free() && this.phase >= 0;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        this.phase = OUT;
        this.timer = 0;
        this.strike = 0;
        this.diving = false;
        this.dip = false;
        this.retarget = 0;
        this.bird.getNavigation().stop();
        this.bird.setCruising(true);
        if (this.bird.onGround()) {
            Vec3 v = this.bird.getDeltaMovement();
            this.bird.setDeltaMovement(v.x, 0.6D, v.z);   // take off
        }
        this.target = this.cruise(this.sea);
    }

    @Override
    public void stop() {
        this.bird.setCruising(false);
        this.bird.setSoarTarget(null);
        this.target = null;
    }

    @Override
    public void tick() {
        int seaLevel = this.bird.level().getSeaLevel();
        if (this.phase != HOME && !this.bird.level().isDay()) {
            this.phase = HOME;   // dusk: everyone flies home to roost
        }
        switch (this.phase) {
            case OUT -> {
                if (horizontal(this.bird.position(), this.sea) < 16.0D) {
                    this.phase = FISH;
                    this.timer = 1200 + this.bird.getRandom().nextInt(1800);   // one to two and a half minutes out there
                }
            }
            case FISH -> {
                if (this.strike > 0 && --this.strike == 0) {
                    // the beak snaps shut about 1.1 s into the scoop: any fish still within reach is caught
                    AbstractFish caught = this.fishNearby(3.5D, 3.5D);
                    if (caught != null) {
                        caught.hurt(this.bird.damageSources().mobAttack(this.bird), 6.0F);
                    }
                    this.target = this.bird.position().add(0.0D, 8.0D, 0.0D);
                    this.retarget = 40;
                    this.diving = false;
                }
                AbstractFish fish = this.strike > 0 ? null : this.fishNearby(16.0D, 24.0D);
                if (fish != null) {
                    // swoop on it: a dive from high up, then skim the surface and scoop it up
                    this.target = fish.position().add(0.0D, 0.6D, 0.0D);
                    this.approach(fish.getY());
                    if (horizontal(this.bird.position(), fish.position()) < 6.0D && this.bird.getY() - fish.getY() < 4.0D) {
                        this.bird.flightAction("scoop");
                        this.strike = 22;
                    }
                } else if (this.strike == 0 && --this.retarget <= 0) {
                    this.retarget = 60 + this.bird.getRandom().nextInt(60);
                    this.diving = false;
                    double a = this.bird.getRandom().nextDouble() * Math.PI * 2.0D;
                    double r = 6.0D + this.bird.getRandom().nextDouble() * 24.0D;
                    this.dip = this.bird.getRandom().nextInt(4) == 0;   // dip to the surface now and then
                    this.target = new Vec3(this.sea.x + Math.cos(a) * r,
                            this.dip ? seaLevel + 1.5D : seaLevel + 14 + this.bird.getRandom().nextInt(12), this.sea.z + Math.sin(a) * r);
                } else if (this.dip && this.strike == 0) {
                    this.approach(seaLevel);
                    if (this.bird.getY() - seaLevel < 3.0D) {
                        this.bird.flightAction("scoop");   // a skim with nothing in it
                        this.strike = 22;
                        this.dip = false;
                    }
                }
                if (--this.timer <= 0) {
                    this.phase = HOME;
                }
            }
            default -> {
                BlockPos home = this.bird.getColonyHome();
                Vec3 roost = Vec3.atBottomCenterOf(home);
                double flat = horizontal(this.bird.position(), roost);
                this.target = roost.add(0.0D, flat > 24.0D ? 18.0D : Math.max(2.0D, flat * 0.5D), 0.0D);
                if (flat < 4.0D && this.bird.getY() - roost.y < 7.0D) {
                    // over the colony: stop flying and settle down onto it
                    this.bird.setCruising(false);
                    this.bird.setDeltaMovement(0.0D, -0.1D, 0.0D);
                    this.phase = -1;
                    return;
                }
            }
        }
        if (this.phase == OUT) {
            this.target = this.cruise(this.sea);
        }
        this.bird.setSoarTarget(this.target);
    }

    /** The sea patch at cruising height over the water. */
    private Vec3 cruise(Vec3 sea) {
        return new Vec3(sea.x, this.bird.level().getSeaLevel() + 20 + (this.bird.getId() % 8), sea.z);
    }

    /** From high over the water the way down starts with a plunge ("dive"), once per approach. */
    private void approach(double surface) {
        if (!this.diving && this.bird.getY() - surface > 8.0D && this.bird.getDeltaMovement().y < -0.05D) {
            this.bird.flightAction("dive");
            this.diving = true;
        }
    }

    private AbstractFish fishNearby(double reach, double below) {
        List<AbstractFish> fish = this.bird.level().getEntitiesOfClass(AbstractFish.class, this.bird.getBoundingBox().inflate(reach, below, reach),
                f -> f.isAlive() && f.getY() > this.bird.level().getSeaLevel() - 4);
        return fish.isEmpty() ? null : fish.get(0);
    }

    private static double horizontal(Vec3 a, Vec3 b) {
        return Math.sqrt(Mth.square(a.x - b.x) + Mth.square(a.z - b.z));
    }
}
