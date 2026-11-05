package com.terrassic.mixin.parts;

import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.util.concurrent.atomic.AtomicInteger;

/** Hit parts (1.7): a creature reserves a block of entity ids for its parts, as the Ender Dragon does. */
@Mixin(Entity.class)
public interface EntityCounterAccessor {
    @Accessor("ENTITY_COUNTER")
    static AtomicInteger terrassic$counter() {
        throw new AssertionError();
    }
}
