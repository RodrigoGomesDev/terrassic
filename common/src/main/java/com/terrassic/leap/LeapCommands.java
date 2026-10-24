package com.terrassic.leap;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import dev.architectury.event.events.common.CommandRegistrationEvent;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * Commands of v0.9 (operators only, permission level 2), with Portuguese, English and Spanish names:
 * <ul>
 *   <li>{@code /terrassic modo [normal|rapido|livre]} (mode, modo): shows or changes how the chapters open.</li>
 *   <li>{@code /terrassic capitulo <n>} (chapter, capitulo): takes the player to chapter n (HISTORIA.md §5, item 3).
 *       Chapter 1 is the Overworld; the others arrive from v2.0 on.</li>
 *   <li>{@code /terrassic ritual parar} (stop, detener): ends the rituals within 128 blocks; the Tyrant goes back.</li>
 * </ul>
 */
public final class LeapCommands {
    private LeapCommands() {
    }

    static void init() {
        CommandRegistrationEvent.EVENT.register(LeapCommands::register);
    }

    private static void register(CommandDispatcher<CommandSourceStack> dispatcher, CommandBuildContext ctx,
                                 Commands.CommandSelection selection) {
        for (String name : List.of("modo", "mode")) {
            dispatcher.register(Commands.literal("terrassic").then(Commands.literal(name).requires(s -> s.hasPermission(2))
                    .executes(c -> showMode(c.getSource()))
                    .then(Commands.argument("modo", StringArgumentType.word())
                            .suggests((c, b) -> SharedSuggestionProvider.suggest(new String[]{"normal", "rapido", "livre"}, b))
                            .executes(c -> setMode(c.getSource(), StringArgumentType.getString(c, "modo"))))));
        }
        for (String name : List.of("capitulo", "chapter")) {
            dispatcher.register(Commands.literal("terrassic").then(Commands.literal(name).requires(s -> s.hasPermission(2))
                    .then(Commands.argument("n", IntegerArgumentType.integer(1, 5))
                            .executes(c -> chapter(c.getSource(), IntegerArgumentType.getInteger(c, "n"))))));
        }
        for (String[] names : new String[][]{{"ritual", "parar"}, {"ritual", "stop"}, {"ritual", "detener"}}) {
            dispatcher.register(Commands.literal("terrassic").then(Commands.literal(names[0]).requires(s -> s.hasPermission(2))
                    .then(Commands.literal(names[1]).executes(c -> stopRituals(c.getSource())))));
        }
    }

    private static int showMode(CommandSourceStack src) {
        LeapProgress.Mode mode = LeapProgress.mode(src.getServer());
        src.sendSuccess(() -> Component.translatable("command.terrassic.mode.current",
                Component.translatable("altar.terrassic.mode." + mode.id)), false);
        return 1;
    }

    private static int setMode(CommandSourceStack src, String id) {
        LeapProgress.Mode mode = LeapProgress.Mode.byId(id);
        if (mode == null) {
            src.sendFailure(Component.translatable("command.terrassic.mode.unknown", id));
            return 0;
        }
        LeapProgress.setMode(src.getServer(), mode);
        src.sendSuccess(() -> Component.translatable("command.terrassic.mode.set",
                Component.translatable("altar.terrassic.mode." + mode.id)), true);
        return 1;
    }

    private static int chapter(CommandSourceStack src, int n) throws CommandSyntaxException {
        ServerPlayer player = src.getPlayerOrException();
        if (n == 1) {
            ServerLevel overworld = src.getServer().overworld();
            if (player.level().dimension() == Level.OVERWORLD) {
                src.sendSuccess(() -> Component.translatable("command.terrassic.chapter.here", 1), false);
                return 1;
            }
            BlockPos spawn = overworld.getSharedSpawnPos();
            player.teleportTo(overworld, spawn.getX() + 0.5D, spawn.getY(), spawn.getZ() + 0.5D, player.getYRot(), player.getXRot());
            src.sendSuccess(() -> Component.translatable("command.terrassic.chapter.done", 1), true);
            return 1;
        }
        if (!Leap.toChapter(player, n)) {
            src.sendFailure(Component.translatable("command.terrassic.chapter.later", n));
            return 0;
        }
        src.sendSuccess(() -> Component.translatable("command.terrassic.chapter.done", n), true);
        return 1;
    }

    private static int stopRituals(CommandSourceStack src) {
        int n = LeapAltarBlockEntity.stopNear(src.getLevel(), BlockPos.containing(src.getPosition()), 128.0D);
        src.sendSuccess(() -> Component.translatable("command.terrassic.ritual.stopped", n), true);
        return n;
    }
}
