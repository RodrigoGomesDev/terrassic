package com.terrassic.registry;

import com.terrassic.Terrassic;
import com.terrassic.block.DinoEggBlock;
import com.terrassic.block.PrehistoricTreeGrower;
import com.terrassic.block.ResearchTableBlock;
import com.terrassic.entity.DinosaurEntity;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.hooks.item.tool.AxeItemHooks;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CarpetBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.block.state.properties.WoodType;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

/** Dinosaur egg blocks, one per species ("&lt;species&gt;_egg"), and the primitive building blocks. */
public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(Terrassic.MOD_ID, Registries.BLOCK);

    /** species id -> egg block, in registration order (also used for the creative tab). */
    public static final Map<String, RegistrySupplier<Block>> EGGS = new LinkedHashMap<>();

    static {
        // BEGIN GENERATED eggs (tools/javagen/gen_species.py)
        egg("tyrannosaurus", ModEntities.TYRANNOSAURUS, true);
        egg("spinosaurus", ModEntities.SPINOSAURUS, true);
        egg("dilophosaurus", ModEntities.DILOPHOSAURUS, false);
        egg("velociraptor", ModEntities.VELOCIRAPTOR, false);
        egg("compsognathus", ModEntities.COMPSOGNATHUS, false);
        egg("triceratops", ModEntities.TRICERATOPS, true);
        egg("stegosaurus", ModEntities.STEGOSAURUS, true);
        egg("ankylosaurus", ModEntities.ANKYLOSAURUS, true);
        egg("brachiosaurus", ModEntities.BRACHIOSAURUS, true);
        egg("parasaurolophus", ModEntities.PARASAUROLOPHUS, true);
        egg("pachycephalosaurus", ModEntities.PACHYCEPHALOSAURUS, false);
        egg("gallimimus", ModEntities.GALLIMIMUS, false);
        egg("maiasaura", ModEntities.MAIASAURA, false);
        egg("pteranodon", ModEntities.PTERANODON, false);
        // END GENERATED eggs
    }

    // ---- primitive building blocks: the list is GENERATED (BuildingBlocks.java, from tools/javagen/gen_blocks.py),
    // these helpers build each kind of block from a material preset.

    /** building block id -> block, in creative-tab order. */
    public static final Map<String, RegistrySupplier<Block>> BUILDING = new LinkedHashMap<>();

    static {
        BuildingBlocks.register();
        // an axe strips prehistoric logs and wood like the vanilla ones
        LifecycleEvent.SETUP.register(() -> {
            for (String[] pair : BuildingBlocks.STRIPPABLES) {
                AxeItemHooks.addStrippable(BUILDING.get(pair[0]).get(), BUILDING.get(pair[1]).get());
            }
        });
    }

    public static final RegistrySupplier<Block> THATCH = BUILDING.get("thatch");
    public static final RegistrySupplier<Block> THATCH_STAIRS = BUILDING.get("thatch_stairs");
    public static final RegistrySupplier<Block> THATCH_SLAB = BUILDING.get("thatch_slab");

    // ---- science (items registered in ModItems)

    /** Stone with fossil bones in it. Mined with a pickaxe it only gives cobblestone and bones; a Hair Brush or a
     *  Flint Chisel digs the fossil out (ExcavationToolItem). Generated underground by worldgen. */
    public static final RegistrySupplier<Block> FOSSIL_ROCK = BLOCKS.register("fossil_rock",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(2.0F, 6.0F)
                    .requiresCorrectToolForDrops().sound(SoundType.STONE)));
    public static final RegistrySupplier<Block> RESEARCH_TABLE = BLOCKS.register("research_table",
            () -> new ResearchTableBlock(BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(2.0F, 6.0F)
                    .sound(SoundType.STONE).noOcclusion()));

    private ModBlocks() {
    }

    private static void egg(String species, RegistrySupplier<? extends EntityType<? extends DinosaurEntity>> type, boolean large) {
        EGGS.put(species, BLOCKS.register(species + "_egg", () -> new DinoEggBlock(type, large,
                BlockBehaviour.Properties.of().mapColor(MapColor.SAND).strength(0.5F).sound(SoundType.METAL)
                        .randomTicks().noOcclusion())));
    }

    private static void building(String id, Supplier<Block> block) {
        BUILDING.put(id, BLOCKS.register(id, block));
    }

    /** Strength, sound and tool rules of each building material (the "material" column of gen_blocks.py). */
    static BlockBehaviour.Properties material(String material, MapColor color) {
        BlockBehaviour.Properties p = BlockBehaviour.Properties.of().mapColor(color);
        return switch (material) {
            case "stone" -> p.strength(1.5F, 6.0F).requiresCorrectToolForDrops().sound(SoundType.STONE);
            case "soft_stone" -> p.strength(0.9F, 3.0F).requiresCorrectToolForDrops().sound(SoundType.TUFF);
            case "hard_stone" -> p.strength(2.0F, 6.0F).requiresCorrectToolForDrops().sound(SoundType.STONE);
            case "pebbles" -> p.strength(0.3F).sound(SoundType.GRAVEL);
            case "thatch" -> p.strength(0.5F).sound(SoundType.GRASS).ignitedByLava();
            case "mud" -> p.strength(1.2F, 3.0F).sound(SoundType.MUD_BRICKS);
            case "wood" -> p.strength(2.0F, 3.0F).sound(SoundType.WOOD).ignitedByLava();
            case "leaves" -> p.strength(0.2F).randomTicks().sound(SoundType.GRASS).noOcclusion()
                    .isValidSpawn((state, level, pos, type) -> false).isSuffocating((state, level, pos) -> false)
                    .isViewBlocking((state, level, pos) -> false).isRedstoneConductor((state, level, pos) -> false)
                    .ignitedByLava().pushReaction(PushReaction.DESTROY);
            case "sapling" -> p.noCollission().randomTicks().instabreak().sound(SoundType.GRASS)
                    .pushReaction(PushReaction.DESTROY);
            case "bone" -> p.strength(2.0F).requiresCorrectToolForDrops().sound(SoundType.BONE_BLOCK);
            case "hide" -> p.strength(0.8F).sound(SoundType.WOOL).ignitedByLava();
            default -> throw new IllegalArgumentException("unknown building material " + material);
        };
    }

    static void cube(String id, BlockBehaviour.Properties p) {
        building(id, () -> new Block(p));
    }

    /** Several sharpened logs in one block: not a full cube to look at, so no occlusion. */
    static void palisade(String id, BlockBehaviour.Properties p) {
        building(id, () -> new Block(p.noOcclusion()));
    }

    static void stairs(String id, String base, BlockBehaviour.Properties p) {
        building(id, () -> new StairBlock(BUILDING.get(base).get().defaultBlockState(), p) {});
    }

    static void slab(String id, BlockBehaviour.Properties p) {
        building(id, () -> new SlabBlock(p));
    }

    static void wall(String id, BlockBehaviour.Properties p) {
        building(id, () -> new WallBlock(p.forceSolidOn()));
    }

    static void fence(String id, BlockBehaviour.Properties p) {
        building(id, () -> new FenceBlock(p.forceSolidOn()));
    }

    static void pane(String id, BlockBehaviour.Properties p) {
        building(id, () -> new IronBarsBlock(p.noOcclusion()) {});
    }

    static void carpet(String id, BlockBehaviour.Properties p) {
        building(id, () -> new CarpetBlock(p.strength(0.1F)) {});
    }

    static void log(String id, BlockBehaviour.Properties p) {
        building(id, () -> new RotatedPillarBlock(p));
    }

    static void leaves(String id, BlockBehaviour.Properties p) {
        building(id, () -> new LeavesBlock(p));
    }

    /** Sapling that grows into the configured feature terrassic:&lt;tree&gt;. */
    static void sapling(String id, String tree, BlockBehaviour.Properties p) {
        building(id, () -> new SaplingBlock(new PrehistoricTreeGrower(tree), p) {});
    }

    static void fenceGate(String id, BlockBehaviour.Properties p) {
        building(id, () -> new FenceGateBlock(p.forceSolidOn(), WoodType.OAK));
    }

    static void door(String id, BlockBehaviour.Properties p) {
        building(id, () -> new DoorBlock(p.strength(3.0F).noOcclusion().pushReaction(PushReaction.DESTROY), BlockSetType.OAK));
    }

    static void trapdoor(String id, BlockBehaviour.Properties p) {
        building(id, () -> new TrapDoorBlock(p.strength(3.0F).noOcclusion()
                .isValidSpawn((state, level, pos, type) -> false), BlockSetType.OAK));
    }

    /** The egg block of a species, or null if the registry is not ready / unknown species. */
    public static Block eggFor(String species) {
        RegistrySupplier<Block> egg = EGGS.get(species);
        return egg != null && egg.isPresent() ? egg.get() : null;
    }
}
