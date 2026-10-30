package com.terrassic.config;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonObject;
import com.google.gson.JsonSerializationContext;
import com.terrassic.Terrassic;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;
import net.minecraft.world.level.storage.loot.predicates.LootItemConditionType;

/**
 * Loot condition {@code terrassic:story}: true while the story mode is on ({@link Story#enabled()}). Guards the
 * pools of Katarina's pages in the structure chests, so they stay out of the loot while the story is off.
 */
public final class StoryCondition implements LootItemCondition {
    public static final DeferredRegister<LootItemConditionType> CONDITIONS =
            DeferredRegister.create(Terrassic.MOD_ID, Registries.LOOT_CONDITION_TYPE);
    public static final RegistrySupplier<LootItemConditionType> TYPE =
            CONDITIONS.register("story", () -> new LootItemConditionType(new Serializer()));
    private static final StoryCondition INSTANCE = new StoryCondition();

    private StoryCondition() {
    }

    @Override
    public LootItemConditionType getType() {
        return TYPE.get();
    }

    @Override
    public boolean test(LootContext context) {
        return Story.enabled();
    }

    public static final class Serializer implements net.minecraft.world.level.storage.loot.Serializer<StoryCondition> {
        @Override
        public void serialize(JsonObject json, StoryCondition condition, JsonSerializationContext context) {
        }

        @Override
        public StoryCondition deserialize(JsonObject json, JsonDeserializationContext context) {
            return INSTANCE;
        }
    }
}
