package com.terrassic.registry;

import com.terrassic.Terrassic;
import com.terrassic.block.BasketBlockEntity;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;

/**
 * Block entities of Terrassic (registered after the blocks they belong to).
 */
public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITY_TYPES =
            DeferredRegister.create(Terrassic.MOD_ID, Registries.BLOCK_ENTITY_TYPE);

    public static final RegistrySupplier<BlockEntityType<BasketBlockEntity>> WICKER_BASKET =
            BLOCK_ENTITY_TYPES.register("wicker_basket", () -> BlockEntityType.Builder.of(BasketBlockEntity::new,
                    ModBlocks.BUILDING.get("wicker_basket").get()).build(null));

    private ModBlockEntities() {
    }
}
