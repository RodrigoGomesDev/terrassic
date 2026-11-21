package com.terrassic.entity.ai;

import com.terrassic.block.DinoEggBlock;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.EnumSet;

/**
 * 1.11.0, the night visitors of a nesting colony (docs/estudos/15, Maiassaura: "a colônia atrai ladrões de ovo à noite",
 * as the Troodon nested at Egg Mountain): a small predator the colony drew in (Maiasaurine.nightRaid) slinks to one egg
 * of the colony, eats it and leaves. It gives up when the colony fights it (it gets a target), after a minute, or when
 * the egg is gone. Added to the raider when it is sent; not saved (the raider is a roamer).
 */
public class NestRaidGoal extends Goal {
    private final DinosaurEntity raider;
    private BlockPos egg;
    private int timer = 1200;
    private boolean done;

    public NestRaidGoal(DinosaurEntity raider, BlockPos egg) {
        this.raider = raider;
        this.egg = egg;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean eggThere() {
        return this.egg != null && this.raider.level().getBlockState(this.egg).getBlock() instanceof DinoEggBlock;
    }

    @Override
    public boolean canUse() {
        if (this.done || this.raider.getTarget() != null || this.raider.isTame() || !this.raider.isAlive()) {
            return false;
        }
        if (!this.eggThere()) {
            BlockPos other = this.egg == null ? null : this.raider.nearestEgg(6);
            if (other == null) {
                this.done = true;
                return false;
            }
            this.egg = other;
        }
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return this.canUse() && this.timer > 0;
    }

    @Override
    public void start() {
        this.raider.setSleeping(false);
        this.raider.getNavigation().moveTo(this.egg.getX() + 0.5D, this.egg.getY(), this.egg.getZ() + 0.5D, 1.15D);
    }

    @Override
    public void tick() {
        if (--this.timer <= 0) {
            this.done = true;
            return;
        }
        this.raider.setSleeping(false);
        this.raider.getLookControl().setLookAt(this.egg.getX() + 0.5D, this.egg.getY() + 0.3D, this.egg.getZ() + 0.5D);
        if (this.raider.blockPosition().distSqr(this.egg) <= 3.0D) {
            if (this.raider.level() instanceof ServerLevel server && server.getBlockState(this.egg).getBlock() instanceof DinoEggBlock block) {
                block.alertParents(server.getBlockState(this.egg), server, this.egg, this.raider);
                server.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, new ItemStack(Items.EGG)),
                        this.egg.getX() + 0.5D, this.egg.getY() + 0.3D, this.egg.getZ() + 0.5D, 10, 0.2D, 0.2D, 0.2D, 0.05D);
                server.destroyBlock(this.egg, false, this.raider);
                this.raider.playSound(ModSounds.SFX_EGG_BREAK.get(), 0.9F, 1.0F);
                this.raider.feed(40);
                com.terrassic.entity.Maiasaurine.logLine("night raid: " + this.raider.speciesId() + " #" + this.raider.getId()
                        + " ate an egg at " + this.egg.toShortString());
            }
            this.done = true;
        } else if (this.raider.getNavigation().isDone()) {
            this.raider.getNavigation().moveTo(this.egg.getX() + 0.5D, this.egg.getY(), this.egg.getZ() + 0.5D, 1.15D);
        }
    }

    @Override
    public void stop() {
        if (this.done) {
            this.egg = null;
        }
    }
}
