package com.terrassic.leap;

import com.terrassic.Terrassic;
import com.terrassic.registry.ModItems;
import com.terrassic.registry.ModTabs;
import dev.architectury.registry.level.entity.EntityAttributeRegistry;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;

/**
 * Registries of v0.9 "The End" (docs/SALTO.md), kept apart from ModBlocks/ModItems/ModEntities so this front does not
 * touch the shared registry files: the Leap Altar (block, block entity, item), the Rift Tyrant and the meteors.
 * Registered by {@link Leap#init()} after the main registries.
 */
public final class LeapRegistry {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(Terrassic.MOD_ID, Registries.BLOCK);
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Terrassic.MOD_ID, Registries.BLOCK_ENTITY_TYPE);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(Terrassic.MOD_ID, Registries.ITEM);
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Terrassic.MOD_ID, Registries.ENTITY_TYPE);

    public static final RegistrySupplier<LeapAltarBlock> LEAP_ALTAR = BLOCKS.register("leap_altar",
            () -> new LeapAltarBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE).strength(2.5F, 1200.0F)
                    .sound(SoundType.STONE).noOcclusion().pushReaction(PushReaction.BLOCK)
                    .lightLevel(s -> LeapAltarBlock.LIGHT[s.getValue(LeapAltarBlock.STAGE)])));

    public static final RegistrySupplier<BlockEntityType<LeapAltarBlockEntity>> LEAP_ALTAR_ENTITY =
            BLOCK_ENTITIES.register("leap_altar", () -> BlockEntityType.Builder.of(LeapAltarBlockEntity::new, LEAP_ALTAR.get()).build(null));

    public static final RegistrySupplier<Item> LEAP_ALTAR_ITEM = ITEMS.register("leap_altar",
            () -> new BlockItem(LEAP_ALTAR.get(), ModItems.story(new Item.Properties().rarity(Rarity.RARE), ModTabs.SCIENCE)));

    /** The Rift Tyrant: a T. rex of the Rift, 35% bigger (its size is set in the constructor, the type keeps the rex box). */
    public static final RegistrySupplier<EntityType<RiftTyrant>> RIFT_TYRANT = ENTITIES.register("rift_tyrant",
            () -> EntityType.Builder.of(RiftTyrant::new, MobCategory.MONSTER).sized(2.6F, 4.8F).fireImmune()
                    .clientTrackingRange(12).build("rift_tyrant"));

    public static final RegistrySupplier<EntityType<Meteor>> METEOR = ENTITIES.register("meteor",
            () -> EntityType.Builder.<Meteor>of(Meteor::new, MobCategory.MISC).sized(1.0F, 1.0F).fireImmune()
                    .clientTrackingRange(12).updateInterval(2).build("meteor"));

    private LeapRegistry() {
    }

    static void register() {
        BLOCKS.register();
        BLOCK_ENTITIES.register();
        ITEMS.register();
        ENTITIES.register();
        EntityAttributeRegistry.register(RIFT_TYRANT, RiftTyrant::createAttributes);
    }
}
