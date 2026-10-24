package com.terrassic.registry;

import com.terrassic.Terrassic;
import dev.architectury.registry.CreativeTabRegistry;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;

public final class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Terrassic.MOD_ID, Registries.CREATIVE_MODE_TAB);

    public static final RegistrySupplier<CreativeModeTab> MAIN = TABS.register("main",
            () -> CreativeTabRegistry.create(Component.translatable("itemGroup.terrassic.main"),
                    () -> new ItemStack(ModItems.TYRANNOSAURUS_SPAWN_EGG.get())));

    public static final RegistrySupplier<CreativeModeTab> BUILDING = TABS.register("building",
            () -> CreativeTabRegistry.create(Component.translatable("itemGroup.terrassic.building"),
                    () -> new ItemStack(ModBlocks.THATCH.get())));

    public static final RegistrySupplier<CreativeModeTab> SCIENCE = TABS.register("science",
            () -> CreativeTabRegistry.create(Component.translatable("itemGroup.terrassic.science"),
                    () -> new ItemStack(ModItems.FIELD_NOTEBOOK.get())));

    private ModTabs() {
    }
}
