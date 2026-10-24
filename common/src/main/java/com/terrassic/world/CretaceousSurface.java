package com.terrassic.world;

import com.google.common.collect.MapMaker;
import com.terrassic.Terrassic;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Noises;
import net.minecraft.world.level.levelgen.SurfaceRules;
import net.minecraft.world.level.levelgen.SurfaceRules.ConditionSource;
import net.minecraft.world.level.levelgen.SurfaceRules.RuleSource;
import net.minecraft.world.level.levelgen.VerticalAnchor;

import java.util.Map;

import static com.terrassic.world.CretaceousBiomes.*;

/**
 * Surface blocks of the Cretaceous biomes, put in front of the overworld surface rule by
 * {@code mixin/NoiseGeneratorSettingsMixin}. Every rule here is guarded by "is a Cretaceous biome", so other biomes
 * and dimensions keep the vanilla rule untouched; where none of these rules applies (deeper layers, bedrock,
 * deepslate) the vanilla rule decides as usual.
 *
 * <pre>
 *  Biome                 Top block
 *  Cretaceous Shore      sand over sandstone, stone on cliffs
 *  Inner Sea             sand with patches of gravel
 *  Deep Inner Sea        gravel with patches of sand
 *  Cretaceous River      gravel and sand bars under the water
 *  River Delta           grass with sand bars, mud and sand under the water, shallow pools
 *  Cypress Swamp         grass with peat, mud under the water, shallow pools (like the vanilla swamp)
 *  Dry Lands             grass, lateritic soil, coarse dirt and cracked mud, laterite rock on steep slopes
 *  Cretaceous Highlands  grass, bare stone on slopes and summits, veins of quartzite
 *  Redwood Forest        grass with needle litter and podzol
 *  Magnolia Forest       grass with fern litter
 *  Hadrosaur Plains      vanilla (grass)
 * </pre>
 */
public final class CretaceousSurface {
    private static final Map<RuleSource, RuleSource> WRAPPED = new MapMaker().weakKeys().makeMap();
    private static volatile RuleSource rules;

    private CretaceousSurface() {
    }

    /** The given surface rule with the Cretaceous rules in front (same instance in, same instance out). */
    public static RuleSource wrap(RuleSource original) {
        if (original == null) {
            return null;
        }
        return WRAPPED.computeIfAbsent(original, o -> SurfaceRules.sequence(rules(), o));
    }

    private static RuleSource rules() {
        RuleSource r = rules;
        if (r == null) {
            r = build();
            rules = r;
        }
        return r;
    }

    private static RuleSource block(Block block) {
        return SurfaceRules.state(block.defaultBlockState());
    }

    private static RuleSource ours(String id) {
        Block b = BuiltInRegistries.BLOCK.get(Terrassic.id(id));
        return block(b == Blocks.AIR ? Blocks.DIRT : b);
    }

    /** Raw surface noise at or above {@code min} (vanilla's surfaceNoiseAbove(x) is min = x / 8.25). */
    private static ConditionSource noiseAbove(double min) {
        return SurfaceRules.noiseCondition(Noises.SURFACE, min, Double.MAX_VALUE);
    }

    private static ConditionSource noiseBetween(double min, double max) {
        return SurfaceRules.noiseCondition(Noises.SURFACE, min, max);
    }

    private static RuleSource build() {
        RuleSource grass = block(Blocks.GRASS_BLOCK);
        RuleSource dirt = block(Blocks.DIRT);
        RuleSource stone = block(Blocks.STONE);
        RuleSource sandBlock = block(Blocks.SAND);
        RuleSource sandstone = block(Blocks.SANDSTONE);
        RuleSource gravelBlock = block(Blocks.GRAVEL);
        RuleSource mud = block(Blocks.MUD);
        RuleSource coarse = block(Blocks.COARSE_DIRT);
        RuleSource podzol = block(Blocks.PODZOL);
        RuleSource water = block(Blocks.WATER);
        RuleSource laterite = ours("laterite");
        RuleSource lateriticSoil = ours("lateritic_soil");
        RuleSource crackedMud = ours("cracked_mud");
        RuleSource quartzite = ours("quartzite");
        RuleSource fernLitter = ours("fern_litter");
        RuleSource needleLitter = ours("needle_litter");
        RuleSource peat = ours("peat");

        ConditionSource dry = SurfaceRules.waterBlockCheck(-1, 0);       // at most one block under the water line
        ConditionSource aboveWater = SurfaceRules.waterBlockCheck(0, 0);
        ConditionSource shallowColumn = SurfaceRules.waterStartCheck(-6, -1);
        ConditionSource floor = SurfaceRules.ON_FLOOR;
        ConditionSource underFloor = SurfaceRules.UNDER_FLOOR;
        RuleSource grassOrDirt = SurfaceRules.sequence(SurfaceRules.ifTrue(aboveWater, grass), dirt);
        RuleSource sand = SurfaceRules.sequence(SurfaceRules.ifTrue(SurfaceRules.ON_CEILING, sandstone), sandBlock);
        RuleSource gravel = SurfaceRules.sequence(SurfaceRules.ifTrue(SurfaceRules.ON_CEILING, stone), gravelBlock);
        // shallow pools in flat wet land (vanilla swamp rule)
        RuleSource pools = SurfaceRules.ifTrue(floor, SurfaceRules.ifTrue(
                SurfaceRules.yBlockCheck(VerticalAnchor.absolute(62), 0),
                SurfaceRules.ifTrue(SurfaceRules.not(SurfaceRules.yBlockCheck(VerticalAnchor.absolute(63), 0)),
                        SurfaceRules.ifTrue(SurfaceRules.noiseCondition(Noises.SWAMP, 0.0D), water))));

        RuleSource beach = SurfaceRules.sequence(
                SurfaceRules.ifTrue(floor, SurfaceRules.sequence(SurfaceRules.ifTrue(SurfaceRules.steep(), stone), sand)),
                SurfaceRules.ifTrue(underFloor, sandBlock),
                SurfaceRules.ifTrue(SurfaceRules.DEEP_UNDER_FLOOR, sandstone));

        ConditionSource gravelPatch = SurfaceRules.noiseCondition(Noises.GRAVEL, -0.08D, 0.08D);
        RuleSource innerSea = SurfaceRules.sequence(
                SurfaceRules.ifTrue(floor, SurfaceRules.sequence(SurfaceRules.ifTrue(gravelPatch, gravel), sand)),
                SurfaceRules.ifTrue(underFloor, SurfaceRules.sequence(SurfaceRules.ifTrue(gravelPatch, gravelBlock), sandBlock)),
                SurfaceRules.ifTrue(SurfaceRules.DEEP_UNDER_FLOOR, sandstone));

        RuleSource deepSea = SurfaceRules.sequence(
                SurfaceRules.ifTrue(floor, SurfaceRules.sequence(SurfaceRules.ifTrue(noiseAbove(0.1D), sand), gravel)),
                SurfaceRules.ifTrue(underFloor, SurfaceRules.sequence(SurfaceRules.ifTrue(noiseAbove(0.1D), sandBlock), gravelBlock)));

        RuleSource river = SurfaceRules.ifTrue(floor, SurfaceRules.ifTrue(SurfaceRules.not(dry),
                SurfaceRules.sequence(SurfaceRules.ifTrue(noiseAbove(0.05D), sand), gravel)));

        RuleSource delta = SurfaceRules.sequence(
                pools,
                SurfaceRules.ifTrue(floor, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(SurfaceRules.not(dry), SurfaceRules.sequence(SurfaceRules.ifTrue(noiseAbove(0.0D), sand), mud)),
                        SurfaceRules.ifTrue(noiseAbove(0.3D), sand),
                        SurfaceRules.ifTrue(SurfaceRules.not(aboveWater), mud),
                        grass)),
                SurfaceRules.ifTrue(shallowColumn, SurfaceRules.ifTrue(underFloor, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(noiseAbove(0.3D), sandBlock),
                        SurfaceRules.ifTrue(SurfaceRules.not(dry), mud),
                        dirt))));

        RuleSource swamp = SurfaceRules.sequence(
                pools,
                SurfaceRules.ifTrue(floor, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(SurfaceRules.not(dry), mud),
                        SurfaceRules.ifTrue(noiseAbove(0.3D), peat),
                        SurfaceRules.ifTrue(SurfaceRules.not(aboveWater), mud),
                        grass)),
                SurfaceRules.ifTrue(shallowColumn, SurfaceRules.ifTrue(underFloor, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(SurfaceRules.not(dry), mud),
                        dirt))));

        RuleSource dryLands = SurfaceRules.sequence(
                SurfaceRules.ifTrue(floor, SurfaceRules.ifTrue(dry, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(SurfaceRules.steep(), laterite),
                        SurfaceRules.ifTrue(noiseAbove(0.2D), lateriticSoil),
                        SurfaceRules.ifTrue(noiseBetween(-0.12D, 0.04D), coarse),
                        SurfaceRules.ifTrue(noiseBetween(-Double.MAX_VALUE, -0.55D), crackedMud),
                        grassOrDirt))),
                SurfaceRules.ifTrue(shallowColumn, SurfaceRules.ifTrue(underFloor, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(SurfaceRules.steep(), laterite),
                        SurfaceRules.ifTrue(noiseAbove(0.2D), lateriticSoil),
                        dirt))));

        ConditionSource bare = noiseAbove(0.12D);
        ConditionSource summit = SurfaceRules.yBlockCheck(VerticalAnchor.absolute(150), 0);
        RuleSource highlands = SurfaceRules.sequence(
                SurfaceRules.ifTrue(floor, SurfaceRules.ifTrue(dry, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(SurfaceRules.steep(), stone),
                        SurfaceRules.ifTrue(summit, stone),
                        SurfaceRules.ifTrue(SurfaceRules.noiseCondition(Noises.CALCITE, -0.03D, 0.03D), quartzite),
                        SurfaceRules.ifTrue(bare, stone),
                        grassOrDirt))),
                SurfaceRules.ifTrue(shallowColumn, SurfaceRules.ifTrue(underFloor, SurfaceRules.sequence(
                        SurfaceRules.ifTrue(SurfaceRules.steep(), stone),
                        SurfaceRules.ifTrue(summit, stone),
                        SurfaceRules.ifTrue(bare, stone),
                        dirt))));

        RuleSource redwood = SurfaceRules.ifTrue(floor, SurfaceRules.ifTrue(dry, SurfaceRules.sequence(
                SurfaceRules.ifTrue(noiseAbove(0.15D), needleLitter),
                SurfaceRules.ifTrue(noiseBetween(-0.45D, -0.3D), podzol),
                grassOrDirt)));

        RuleSource magnolia = SurfaceRules.ifTrue(floor, SurfaceRules.ifTrue(dry, SurfaceRules.sequence(
                SurfaceRules.ifTrue(noiseAbove(0.25D), fernLitter),
                grassOrDirt)));

        RuleSource perBiome = SurfaceRules.sequence(
                SurfaceRules.ifTrue(SurfaceRules.isBiome(BEACH), beach),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(INNER_SEA), innerSea),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(DEEP_INNER_SEA), deepSea),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(RIVER), river),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(RIVER_DELTA), delta),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(CYPRESS_SWAMP), swamp),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(DRY_LANDS), dryLands),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(HIGHLANDS), highlands),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(REDWOOD_FOREST), redwood),
                SurfaceRules.ifTrue(SurfaceRules.isBiome(MAGNOLIA_FOREST), magnolia));
        return SurfaceRules.ifTrue(SurfaceRules.abovePreliminarySurface(), perBiome);
    }
}
