package com.terrassic.entity;

import com.terrassic.Terrassic;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.attributes.DefaultAttributes;
import net.minecraft.world.entity.monster.Slime;

import java.util.HashMap;
import java.util.Map;

/**
 * Experience a tame animal earns for a kill (v0.15.3, approved by Rodrigo on 30/10/2026; docs/NIVEIS.md, "XP por
 * abate"). Before, a kill gave the victim's whole health, and six zombies made four levels.
 * <ul>
 *   <li><b>The mod's animals</b>, by size (the species' table health): tiny 2, small 6, medium 15, large 30, giant 50,
 *       colossal 80, times {@code 0.5 + level / 80} (half at level 1, the table at 40, twice at 120).</li>
 *   <li><b>Minecraft's mobs</b>, from {@link #VANILLA}; any other mob 4 if it is a monster, 2 if not.</li>
 *   <li>A tame animal (anyone's) gives nothing, a baby a quarter.</li>
 * </ul>
 */
public final class KillXp {
    private static final Map<EntityType<?>, Float> VANILLA = new HashMap<>();

    static {
        put(0.0F, EntityType.PLAYER, EntityType.VILLAGER, EntityType.WANDERING_TRADER, EntityType.IRON_GOLEM,
                EntityType.SNOW_GOLEM, EntityType.ALLAY, EntityType.BAT, EntityType.ARMOR_STAND);
        put(1.0F, EntityType.CHICKEN, EntityType.RABBIT, EntityType.COD, EntityType.SALMON, EntityType.TROPICAL_FISH,
                EntityType.PUFFERFISH, EntityType.SQUID, EntityType.GLOW_SQUID, EntityType.FROG, EntityType.TADPOLE,
                EntityType.PARROT, EntityType.TURTLE, EntityType.AXOLOTL, EntityType.BEE, EntityType.SILVERFISH,
                EntityType.ENDERMITE);
        put(2.0F, EntityType.COW, EntityType.MOOSHROOM, EntityType.PIG, EntityType.SHEEP, EntityType.GOAT,
                EntityType.HORSE, EntityType.DONKEY, EntityType.MULE, EntityType.LLAMA, EntityType.TRADER_LLAMA,
                EntityType.WOLF, EntityType.FOX, EntityType.DOLPHIN, EntityType.PANDA, EntityType.POLAR_BEAR,
                EntityType.CAT, EntityType.OCELOT, EntityType.CAMEL, EntityType.SNIFFER, EntityType.STRIDER,
                EntityType.SKELETON_HORSE, EntityType.ZOMBIE_HORSE);
        put(4.0F, EntityType.ZOMBIE, EntityType.HUSK, EntityType.DROWNED, EntityType.ZOMBIE_VILLAGER,
                EntityType.ZOMBIFIED_PIGLIN, EntityType.SKELETON, EntityType.STRAY, EntityType.WITHER_SKELETON,
                EntityType.SPIDER, EntityType.CAVE_SPIDER, EntityType.CREEPER, EntityType.SLIME, EntityType.MAGMA_CUBE,
                EntityType.PHANTOM, EntityType.PILLAGER, EntityType.PIGLIN, EntityType.VEX);
        put(8.0F, EntityType.ENDERMAN, EntityType.WITCH, EntityType.VINDICATOR, EntityType.BLAZE, EntityType.GHAST,
                EntityType.GUARDIAN, EntityType.HOGLIN, EntityType.ZOGLIN, EntityType.PIGLIN_BRUTE, EntityType.EVOKER,
                EntityType.SHULKER);
        put(25.0F, EntityType.RAVAGER);
        put(60.0F, EntityType.ELDER_GUARDIAN);
        put(100.0F, EntityType.WARDEN);
        put(150.0F, EntityType.WITHER);
        put(200.0F, EntityType.ENDER_DRAGON);
    }

    private KillXp() {
    }

    private static void put(float xp, EntityType<?>... types) {
        for (EntityType<?> type : types) {
            VANILLA.put(type, xp);
        }
    }

    /** The experience for killing {@code victim}, before the "Tamed XP" rule. */
    public static float of(LivingEntity victim) {
        float xp;
        if (victim instanceof DinosaurEntity d) {
            if (d.isTame()) {
                return 0.0F;
            }
            xp = size(victim.getType()) * (0.5F + d.levels().level() / 80.0F);
        } else if (VANILLA.containsKey(victim.getType())) {
            xp = VANILLA.get(victim.getType());
            // only a big slime is a fight; the small ones it splits into are crumbs
            if (victim instanceof Slime slime && slime.getSize() < 2) {
                xp = 1.0F;
            }
        } else if (Terrassic.MOD_ID.equals(BuiltInRegistries.ENTITY_TYPE.getKey(victim.getType()).getNamespace())) {
            xp = size(victim.getType());
        } else {
            xp = victim.getType().getCategory() == MobCategory.MONSTER ? 4.0F : 2.0F;
        }
        return victim.isBaby() ? xp * 0.25F : xp;
    }

    /** The size class of one of the mod's species, from its table health (docs/NIVEIS.md lists every species). */
    static float size(EntityType<?> type) {
        double health = 20.0D;
        if (DefaultAttributes.hasSupplier(type)) {
            @SuppressWarnings("unchecked")
            EntityType<? extends LivingEntity> living = (EntityType<? extends LivingEntity>) type;
            health = DefaultAttributes.getSupplier(living).getBaseValue(Attributes.MAX_HEALTH);
        }
        if (health <= 12.0D) {
            return 2.0F;
        } else if (health <= 34.0D) {
            return 6.0F;
        } else if (health <= 70.0D) {
            return 15.0F;
        } else if (health <= 120.0D) {
            return 30.0F;
        } else if (health <= 220.0D) {
            return 50.0F;
        }
        return 80.0F;
    }
}
