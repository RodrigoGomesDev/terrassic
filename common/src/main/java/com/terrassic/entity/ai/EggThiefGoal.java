package com.terrassic.entity.ai;

import com.terrassic.block.DinoEggBlock;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;

import java.util.EnumSet;

/**
 * The egg thief (docs/NINHOS.md): a wild, grown {@link DinosaurEntity#eggThief()} that is hungry and has nothing
 * else to do walks to a dinosaur egg block within eight blocks and eats it: the egg breaks without dropping
 * anything and the thief is fed. Respects mobGriefing. The herd around a wild nest defends it like against a
 * player (the thief becomes the enemy of the wild adults of that species nearby).
 */
public class EggThiefGoal extends Goal {
    private final DinosaurEntity dino;
    private BlockPos egg;
    private int timer;

    public EggThiefGoal(DinosaurEntity dino) {
        this.dino = dino;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (this.dino.isTame() || this.dino.isBaby() || this.dino.isSleeping() || this.dino.getTarget() != null
                || this.dino.isSated() || !this.dino.level().getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)
                || this.dino.getRandom().nextInt(reducedTickDelay(120)) != 0) {
            return false;
        }
        this.egg = this.dino.nearestEgg(8);
        return this.egg != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.timer > 0 && this.dino.getTarget() == null
                && this.dino.level().getBlockState(this.egg).getBlock() instanceof DinoEggBlock;
    }

    @Override
    public void start() {
        this.timer = 600;
        this.dino.getNavigation().moveTo(this.egg.getX() + 0.5D, this.egg.getY(), this.egg.getZ() + 0.5D, 1.1D);
    }

    @Override
    public void tick() {
        this.timer--;
        this.dino.getLookControl().setLookAt(this.egg.getX() + 0.5D, this.egg.getY() + 0.3D, this.egg.getZ() + 0.5D);
        if (this.dino.blockPosition().distSqr(this.egg) <= 2.5D) {
            if (this.dino.level() instanceof ServerLevel server && server.getBlockState(this.egg).getBlock() instanceof DinoEggBlock block) {
                block.alertParents(server.getBlockState(this.egg), server, this.egg, this.dino);
                server.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, new ItemStack(Items.EGG)),
                        this.egg.getX() + 0.5D, this.egg.getY() + 0.3D, this.egg.getZ() + 0.5D, 10, 0.2D, 0.2D, 0.2D, 0.05D);
                server.destroyBlock(this.egg, false, this.dino);
                this.dino.playSound(SoundEvents.TURTLE_EGG_BREAK, 0.9F, 1.0F);
                this.dino.playSound(SoundEvents.GENERIC_EAT, 0.8F, 1.2F);
                this.dino.feed(40);
            }
            this.timer = 0;
        } else if (this.dino.getNavigation().isDone()) {
            this.dino.getNavigation().moveTo(this.egg.getX() + 0.5D, this.egg.getY(), this.egg.getZ() + 0.5D, 1.1D);
        }
    }

    @Override
    public void stop() {
        this.timer = 0;
        this.egg = null;
    }
}
