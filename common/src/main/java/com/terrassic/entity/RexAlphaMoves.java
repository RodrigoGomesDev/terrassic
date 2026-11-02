package com.terrassic.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The T. rex alpha's own moves (tools/modelgen/handmade/tyrannosaurus/alphaanims.py, docs/ALFAS.md): the owner of the
 * region. It walks unhurried with the head high, surveys its ground, marks trunks with its jaw (the bark comes off),
 * stamps a challenge instead of the common threat, bites and throws, shoulders away what stands beside it, stands
 * over its kill growling at whoever comes near, and tries once to rise when it is about to wake from a knockout.
 */
final class RexAlphaMoves extends AlphaMoves {
    static final String[] ACTIONS = {"alpha_survey", "alpha_jaw_rub", "alpha_challenge", "alpha_bite_toss", "alpha_shove",
            "alpha_shove_left", "alpha_guard", "alpha_ko_struggle"};
    /** Bite and throw: the jaws close at 0.42 s, the neck wrenches at 1.05-1.22 s (the throw), 2.2 s in all. */
    private static final ApexTheropod.Strike TOSS = new ApexTheropod.Strike("alpha_bite_toss", 8, 50, false);
    private static final int TOSS_AFTER_HIT = 14;
    /** The shoulder lands at 0.63 s of 1.4 s; it hits beside and behind (side = true). */
    private static final ApexTheropod.Strike SHOVE = new ApexTheropod.Strike("alpha_shove", 13, 32, false, true);
    /** The same shove with the left shoulder, for what stands on its left. */
    private static final ApexTheropod.Strike SHOVE_LEFT = new ApexTheropod.Strike("alpha_shove_left", 13, 32, false, true);
    /** The challenge's three stamps (ticks into it) and the jaw-rub's three strokes, then the bark comes off. */
    private static final int[] STAMPS = {20, 36, 52};
    private static final int[] STROKES = {25, 47, 69};
    private static final int RUB_STRIP = 80;

    private int busy;
    private int challengeAge = -1;
    private BlockPos rubLog;
    private int rubAge = -1;
    private int rubHold;
    private int tossTarget = -1;
    private int tossIn;
    private int sideCooldown;
    private int guardCooldown = 200;

    RexAlphaMoves(ApexTheropod mob) {
        super(mob);
    }

    @Override
    public String walkAnim() {
        return "alpha_walk";
    }

    @Override
    public double walkCycle() {
        return 86.0D / 16.0D / 48.0D;      // 86 px per 2.4 s cycle
    }

    @Override
    public String threatAnim() {
        this.challengeAge = 0;
        this.busy = 66;
        return "alpha_challenge";
    }

    @Override
    public boolean gesture(ServerLevel level) {
        float r = this.mob.getRandom().nextFloat();
        if (r < 0.35F) {
            BlockPos log = this.trunkNearby(level);
            if (log != null) {
                this.face(log.getX() + 0.5D, log.getZ() + 0.5D);
                this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "alpha_jaw_rub");
                this.rubLog = log;
                this.rubAge = 0;
                this.rubHold = 100;
                this.busy = 100;
                return true;
            }
        }
        if (r < 0.7F) {
            this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "alpha_survey");
            this.busy = 120;
            return true;
        }
        return false;
    }

    @Override
    public ApexTheropod.Strike bite(LivingEntity target) {
        // a throw only for what its jaws can lift
        return target.getBbWidth() < 2.0F && this.mob.getRandom().nextFloat() < 0.3F ? TOSS : null;
    }

    @Override
    public ApexTheropod.Strike side(LivingEntity target) {
        if (this.sideCooldown > 0) {
            return null;
        }
        this.sideCooldown = 80;
        // its right side: facing yaw 0 is +z (south), the right hand is -x (west)
        float yaw = this.mob.yBodyRot * Mth.DEG_TO_RAD;
        double right = (target.getX() - this.mob.getX()) * -Mth.cos(yaw) + (target.getZ() - this.mob.getZ()) * -Mth.sin(yaw);
        return right >= 0.0D ? SHOVE : SHOVE_LEFT;
    }

    @Override
    public boolean standsOut(ApexTheropod.Strike strike) {
        return strike == TOSS || strike == SHOVE || strike == SHOVE_LEFT;
    }

    @Override
    public void struck(LivingEntity target, ApexTheropod.Strike strike) {
        if (strike == TOSS) {
            // held in the jaws until the neck's wrench: the bite's knockback would take it out of reach of the throw
            target.setDeltaMovement(Vec3.ZERO);
            target.hurtMarked = true;
            this.tossTarget = target.getId();
            this.tossIn = TOSS_AFTER_HIT;
        } else if (strike == SHOVE || strike == SHOVE_LEFT) {
            double dx = target.getX() - this.mob.getX();
            double dz = target.getZ() - this.mob.getZ();
            double d = Math.max(0.1D, Math.sqrt(dx * dx + dz * dz));
            this.fling(target, dx / d * 1.3D, 0.35D, dz / d * 1.3D);
        }
    }

    @Override
    public boolean busy() {
        return this.busy > 0;
    }

    @Override
    public String stirAnim() {
        return "alpha_ko_struggle";
    }

    @Override
    public void tick(ServerLevel level) {
        if (this.busy > 0) {
            this.busy--;
        }
        if (this.sideCooldown > 0) {
            this.sideCooldown--;
        }
        if (this.guardCooldown > 0) {
            this.guardCooldown--;
        }
        if (this.challengeAge >= 0) {
            this.challengeAge++;
            for (int at : STAMPS) {
                if (this.challengeAge == at) {
                    this.mob.dust(level);
                    this.mob.playSound(SoundEvents.GENERIC_EXPLODE, 0.35F, 0.45F);
                }
            }
            if (this.challengeAge > STAMPS[STAMPS.length - 1]) {
                this.challengeAge = -1;
            }
        }
        if (this.rubAge >= 0) {
            this.rubTick(level);
        }
        if (this.rubHold > 0) {
            // held every tick: an idle mob's body follows its head, not its yaw, and would swing off the trunk
            if (--this.rubHold == 0 || this.rubLog == null || this.mob.getTarget() != null) {
                this.rubHold = 0;
            } else {
                this.face(this.rubLog.getX() + 0.5D, this.rubLog.getZ() + 0.5D);
            }
        }
        if (this.tossIn > 0 && --this.tossIn == 0) {
            this.toss(level);
        }
        if ((this.mob.tickCount + this.mob.getId()) % 20 == 0) {
            this.guardTick(level);
        }
    }

    // ------------------------------------------------------------------ marking a trunk

    /** A log about a neck's length away, the block nearest the height of its jaw (the jaw meets the bark there). */
    private BlockPos trunkNearby(ServerLevel level) {
        double k = this.mob.modelScale() * this.mob.getScale();
        int r = Mth.ceil(4.5D * k);
        BlockPos at = this.mob.blockPosition();
        BlockPos best = null;
        double bestD = Double.MAX_VALUE;
        double jawY = this.mob.getY() + 3.9D * k;
        for (BlockPos p : BlockPos.betweenClosed(at.offset(-r, Mth.floor(2.5D * k), -r), at.offset(r, Mth.ceil(4.5D * k), r))) {
            double dx = p.getX() + 0.5D - this.mob.getX();
            double dz = p.getZ() + 0.5D - this.mob.getZ();
            double d = Math.sqrt(dx * dx + dz * dz);
            double score = d + Math.abs(p.getY() + 0.5D - jawY);
            if (d >= 3.5D * k && d <= 4.5D * k && score < bestD && level.getBlockState(p).is(BlockTags.LOGS)) {
                best = p.immutable();
                bestD = score;
            }
        }
        return best;
    }

    private void rubTick(ServerLevel level) {
        this.rubAge++;
        BlockState log = this.rubLog == null ? null : level.getBlockState(this.rubLog);
        if (log == null || !log.is(BlockTags.LOGS) || this.mob.getTarget() != null) {
            this.rubAge = -1;
            return;
        }
        for (int at : STROKES) {
            if (this.rubAge == at) {
                level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, log), this.rubLog.getX() + 0.5D,
                        this.rubLog.getY() + 0.5D, this.rubLog.getZ() + 0.5D, 10, 0.4D, 0.5D, 0.4D, 0.1D);
                level.playSound(null, this.rubLog, log.getSoundType().getHitSound(), SoundSource.HOSTILE, 1.0F, 0.6F);
            }
        }
        if (this.rubAge == RUB_STRIP) {
            // the bark comes off where it rubbed: a stripped log is the mark it leaves (only with mob griefing on)
            if (level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) {
                BlockState stripped = stripped(log);
                if (stripped != null) {
                    level.setBlock(this.rubLog, stripped, Block.UPDATE_ALL);
                    level.playSound(null, this.rubLog, SoundEvents.AXE_STRIP, SoundSource.HOSTILE, 1.0F, 0.7F);
                }
            }
            this.rubAge = -1;
        }
    }

    /** "x_log" -> "stripped_x_log" (and "_wood", "_stem" alike) in the same namespace, keeping the axis. */
    private static BlockState stripped(BlockState log) {
        ResourceLocation id = BuiltInRegistries.BLOCK.getKey(log.getBlock());
        if (id == null || id.getPath().startsWith("stripped_")) {
            return null;
        }
        ResourceLocation to = ResourceLocation.tryBuild(id.getNamespace(), "stripped_" + id.getPath());
        Block block = to == null ? null : BuiltInRegistries.BLOCK.getOptional(to).orElse(null);
        if (block == null) {
            return null;
        }
        BlockState state = block.defaultBlockState();
        if (log.hasProperty(RotatedPillarBlock.AXIS) && state.hasProperty(RotatedPillarBlock.AXIS)) {
            state = state.setValue(RotatedPillarBlock.AXIS, log.getValue(RotatedPillarBlock.AXIS));
        }
        return state;
    }

    // ------------------------------------------------------------------ the throw and the shove

    /** The neck's wrench: what it holds flies to its side. */
    private void toss(ServerLevel level) {
        if (!(level.getEntity(this.tossTarget) instanceof LivingEntity target) || !target.isAlive()
                || target.distanceToSqr(this.mob) > Mth.square(9.0D * this.mob.getScale())) {
            this.tossTarget = -1;
            return;
        }
        float yaw = this.mob.yBodyRot * Mth.DEG_TO_RAD;
        double sx = Mth.cos(yaw);       // its left: the way the neck wrenches (alpha_bite_toss)
        double sz = Mth.sin(yaw);
        this.fling(target, sx * 1.4D, 0.6D, sz * 1.4D);
        this.mob.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.4F, 0.5F);
        this.tossTarget = -1;
    }

    private void fling(LivingEntity target, double x, double y, double z) {
        double keep = 1.0D - Mth.clamp(target.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.KNOCKBACK_RESISTANCE), 0.0D, 1.0D) * 0.6D;
        target.push(x * keep, y * keep, z * keep);
        target.hurtMarked = true;
    }

    // ------------------------------------------------------------------ over its kill

    private void guardTick(ServerLevel level) {
        if (this.guardCooldown > 0 || this.busy > 0 || this.mob.isTame() || this.mob.getTarget() != null || this.mob.isVehicle()
                || this.mob.isSleeping() || this.mob.isKnockedOut() || !this.mob.onGround()) {
            return;
        }
        double s = this.mob.getScale();
        // a kill with meat on it close by, and someone coming: it goes and stands over it first
        CarcassEntity kill = level.getEntitiesOfClass(CarcassEntity.class, this.mob.getBoundingBox().inflate(12.0D * s),
                CarcassEntity::hasMeat).stream().min(java.util.Comparator.comparingDouble(c -> c.distanceToSqr(this.mob))).orElse(null);
        if (kill == null) {
            return;
        }
        Player near = level.getNearestPlayer(this.mob, 16.0D * s);
        if (near == null || near.isCreative() || near.isSpectator()) {
            return;
        }
        double reach = kill.getBbWidth() * 0.5D + 1.5D * s;
        double dx = kill.getX() - this.mob.getX(), dz = kill.getZ() - this.mob.getZ();
        if (dx * dx + dz * dz > reach * reach) {
            this.mob.getNavigation().moveTo(kill, 0.9D);     // checked again in a second, until it is there
            return;
        }
        this.mob.getNavigation().stop();
        this.guardCooldown = 200;
        this.busy = 120;
        this.mob.getLookControl().setLookAt(near, 30.0F, 30.0F);
        this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "alpha_guard");
        this.mob.playSound(this.mob.roarSound(), 1.2F, 0.6F * this.mob.getVoicePitch());
    }

    private void face(double x, double z) {
        float yaw = (float) (Mth.atan2(z - this.mob.getZ(), x - this.mob.getX()) * Mth.RAD_TO_DEG) - 90.0F;
        this.mob.setYRot(yaw);
        this.mob.setYBodyRot(yaw);
        this.mob.setYHeadRot(yaw);
        this.mob.getLookControl().setLookAt(x, this.mob.getEyeY(), z, 30.0F, 30.0F);
        this.mob.getNavigation().stop();
    }
}
