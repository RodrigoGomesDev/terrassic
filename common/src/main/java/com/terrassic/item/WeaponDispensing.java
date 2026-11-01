package com.terrassic.item;

import com.terrassic.entity.FlintArrow;
import com.terrassic.entity.NarcoticArrow;
import com.terrassic.entity.TranqDart;
import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import dev.architectury.event.events.common.LifecycleEvent;
import net.minecraft.core.Direction;
import net.minecraft.core.dispenser.BlockSource;
import net.minecraft.core.dispenser.DefaultDispenseItemBehavior;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.DispenserBlock;
import net.minecraft.world.phys.Vec3;

import java.util.function.Function;

/**
 * v1.1.4 (docs/ARMAS.md): a dispenser shoots the flint arrow, the narcotic arrow and the blowgun dart like a vanilla
 * arrow, instead of spitting the item out. The dispenser's shot is a weak one (vanilla power 1.1): a narcotic arrow
 * from it carries about a third of a full bow draw, a dart the dose of a quick puff. All of them can be picked up.
 * On 1.21 the vanilla projectile behaviour is tied to ProjectileItem, so this one is written out by hand with the
 * numbers of the 1.20.1 AbstractProjectileDispenseBehavior.
 */
public final class WeaponDispensing {
    private static final float POWER = 1.1F;
    private static final float UNCERTAINTY = 6.0F;

    private WeaponDispensing() {
    }

    public static void init() {
        LifecycleEvent.SETUP.register(() -> {
            register(ModItems.FLINT_ARROW.get(), level -> new FlintArrow(ModEntities.FLINT_ARROW.get(), level));
            register(ModItems.NARCOTIC_ARROW.get(), level -> new NarcoticArrow(ModEntities.NARCOTIC_ARROW.get(), level));
            register(ModItems.TRANQ_DART.get(), level -> new TranqDart(ModEntities.TRANQ_DART.get(), level));
        });
    }

    private static void register(Item item, Function<Level, AbstractArrow> factory) {
        DispenserBlock.registerBehavior(item, new DefaultDispenseItemBehavior() {
            @Override
            protected ItemStack execute(BlockSource source, ItemStack stack) {
                Level level = source.level();
                Direction facing = source.state().getValue(DispenserBlock.FACING);
                Vec3 centre = source.pos().getCenter();
                AbstractArrow arrow = factory.apply(level);
                arrow.setPos(centre.x + 0.7D * facing.getStepX(), centre.y + 0.7D * facing.getStepY(),
                        centre.z + 0.7D * facing.getStepZ());
                arrow.pickup = AbstractArrow.Pickup.ALLOWED;
                arrow.shoot(facing.getStepX(), facing.getStepY() + 0.1F, facing.getStepZ(), POWER, UNCERTAINTY);
                level.addFreshEntity(arrow);
                stack.shrink(1);
                return stack;
            }

            @Override
            protected void playSound(BlockSource source) {
                source.level().levelEvent(1002, source.pos(), 0);   // the dispenser's "launch" click
            }
        });
    }
}
