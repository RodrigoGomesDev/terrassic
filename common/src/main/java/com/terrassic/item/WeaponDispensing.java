package com.terrassic.item;

import com.terrassic.entity.FlintArrow;
import com.terrassic.entity.NarcoticArrow;
import com.terrassic.entity.TranqDart;
import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import dev.architectury.event.events.common.LifecycleEvent;
import net.minecraft.core.Position;
import net.minecraft.core.dispenser.AbstractProjectileDispenseBehavior;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.DispenserBlock;

import java.util.function.Function;

/**
 * v1.1.4 (docs/ARMAS.md): a dispenser shoots the flint arrow, the narcotic arrow and the blowgun dart like a vanilla
 * arrow, instead of spitting the item out. The dispenser's shot is a weak one (vanilla power 1.1): a narcotic arrow
 * from it carries about a third of a full bow draw, a dart the dose of a quick puff. All of them can be picked up.
 */
public final class WeaponDispensing {
    private WeaponDispensing() {
    }

    public static void init() {
        LifecycleEvent.SETUP.register(() -> {
            register(ModItems.FLINT_ARROW.get(), level -> new FlintArrow(ModEntities.FLINT_ARROW.get(), level));
            register(ModItems.NARCOTIC_ARROW.get(), level -> new NarcoticArrow(ModEntities.NARCOTIC_ARROW.get(), level));
            register(ModItems.TRANQ_DART.get(), level -> new TranqDart(ModEntities.TRANQ_DART.get(), level));
        });
    }

    private static void register(net.minecraft.world.item.Item item, Function<Level, AbstractArrow> factory) {
        DispenserBlock.registerBehavior(item, new AbstractProjectileDispenseBehavior() {
            @Override
            protected Projectile getProjectile(Level level, Position position, ItemStack stack) {
                AbstractArrow arrow = factory.apply(level);
                arrow.setPos(position.x(), position.y(), position.z());
                arrow.pickup = AbstractArrow.Pickup.ALLOWED;
                return arrow;
            }
        });
    }
}
