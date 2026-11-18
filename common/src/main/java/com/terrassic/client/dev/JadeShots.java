package com.terrassic.client.dev;

import com.terrassic.client.ClientConfig;
import com.terrassic.client.HudOptionsScreen;
import dev.architectury.event.events.client.ClientTickEvent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Locale;
import java.util.UUID;

/**
 * Development only (TERRASSIC_JADE_SHOTS=1, a dev client with Jade: ./gradlew :fabric:runClient -Pjade
 * --args="--quickPlaySingleplayer partes"): photographs Jade's tooltip over a Terrassic animal in each state the plugin
 * shows (wild, calf, tame with its owner, knocked out while being tamed, alpha), then the nameplate forced back beside
 * Jade and the HUD options with the new switch. Screenshots jade_*.png in screenshots/; closes the game.
 */
public final class JadeShots {
    private interface Step {
        int run(Minecraft mc);
    }

    private static final Deque<Step> STEPS = new ArrayDeque<>();
    private static int wait;
    private static final double Y = -60.0D;

    private JadeShots() {
    }

    public static void init() {
        if (!"1".equals(System.getenv("TERRASSIC_JADE_SHOTS"))) {
            return;
        }
        ClientTickEvent.CLIENT_POST.register(JadeShots::tick);
        plan();
    }

    private static void tick(Minecraft mc) {
        if (wait > 0) {
            wait--;
            return;
        }
        Step s = STEPS.peek();
        if (s == null) {
            return;
        }
        int w;
        try {
            w = s.run(mc);
        } catch (Throwable e) {
            org.slf4j.LoggerFactory.getLogger("terrassic").error("[jade shots] step failed", e);
            w = 1;
        }
        if (w < 0) {
            return;
        }
        STEPS.poll();
        wait = w;
    }

    /** As the server itself (the test world has no cheats on), like BehaviorTest. */
    private static void command(Minecraft mc, String c) {
        net.minecraft.server.MinecraftServer server = mc.getSingleplayerServer();
        server.execute(() -> server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), c));
    }

    private static String owner(UUID id) {
        long m = id.getMostSignificantBits();
        long l = id.getLeastSignificantBits();
        return String.format(Locale.ROOT, "[I;%d,%d,%d,%d]", (int) (m >> 32), (int) m, (int) (l >> 32), (int) l);
    }

    private static void plan() {
        STEPS.add(mc -> mc.level == null || mc.player == null || mc.getSingleplayerServer() == null ? -1 : 100);
        STEPS.add(mc -> {
            for (String c : new String[]{"gamemode creative @a", "gamerule doDaylightCycle false", "time set 6000", "weather clear",
                    "gamerule doMobSpawning false", "kill @e[type=!player]"}) {
                command(mc, c);
            }
            ClientConfig.set("hud_nameplate_with_jade", false);
            mc.options.hideGui = false;
            mc.player.getAbilities().flying = true;
            return 40;
        });
        shot("wild", "tyrannosaurus", "NoAI:1b,Female:1b", 5.5D, 2.2D);
        shot("baby", "triceratops", "NoAI:1b,Age:-24000", 2.2D, 0.25D);
        shot("tame", "parasaurolophus", "NoAI:1b,Owner:OWNER", 4.0D, 1.4D);
        shot("knocked_out", "carnotaurus", "NoAI:1b,KnockedOut:1b,Torpor:120f,TameProgress:6f", 4.0D, 0.5D);
        shot("alpha", "tyrannosaurus", "NoAI:1b,Alpha:1b", 5.5D, 2.2D);
        // the nameplate forced back beside Jade (hud_nameplate_with_jade)
        STEPS.add(mc -> {
            ClientConfig.set("hud_nameplate_with_jade", true);
            return 1;
        });
        shot("with_nameplate", "styracosaurus", "NoAI:1b", 4.5D, 0.8D);
        STEPS.add(mc -> {
            ClientConfig.set("hud_nameplate_with_jade", false);
            mc.setScreen(new HudOptionsScreen(null));
            return 30;
        });
        STEPS.add(mc -> {
            Screenshot.grab(mc.gameDirectory, "jade_hud_options.png", mc.getMainRenderTarget(), m -> {
            });
            return 20;
        });
        STEPS.add(mc -> {
            mc.setScreen(null);
            mc.stop();
            return 1;
        });
    }

    /** Summons the animal, stands the camera in front of it looking at its middle, and photographs the tooltip. */
    private static int place;

    private static void shot(String name, String species, String nbt, double dist, double eyeAt) {
        double z = 0.5D + 40.0D * place++;     // each one on clean ground (a carcass stays where the last one fell)
        STEPS.add(mc -> {
            command(mc, "kill @e[type=!player]");
            return 30;
        });
        STEPS.add(mc -> {
            command(mc, "kill @e[type=!player]");   // the carcass left by the last one
            return 10;
        });
        STEPS.add(mc -> {
            command(mc, String.format(Locale.ROOT, "summon terrassic:%s 0.5 %.1f %.1f {%s,Rotation:[0f,0f]}", species, Y, z,
                    nbt.replace("OWNER", owner(mc.player.getUUID()))));
            // feet on the ground (never the eye under it), looking at the body's height
            double feet = Math.max(Y, Y + eyeAt - 1.62D);
            float pitch = (float) Math.toDegrees(Math.atan2(feet + 1.62D - (Y + eyeAt), dist));
            command(mc, String.format(Locale.ROOT, "tp @p %.1f %.1f %.1f 90 %.1f", 0.5D + dist, feet, z, pitch));
            return 130;     // the new-species toasts fade first
        });
        STEPS.add(mc -> {
            mc.gui.getChat().clearMessages(false);
            return 10;
        });
        STEPS.add(mc -> {
            Screenshot.grab(mc.gameDirectory, "jade_" + name + ".png", mc.getMainRenderTarget(), m -> {
            });
            return 10;
        });
    }
}
