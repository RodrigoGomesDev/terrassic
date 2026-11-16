package com.terrassic.compat.jade;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.PlayerInfo;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import snownee.jade.api.EntityAccessor;
import snownee.jade.api.IEntityComponentProvider;
import snownee.jade.api.ITooltip;
import snownee.jade.api.config.IPluginConfig;

import java.util.UUID;

/** The client side of {@link TerrassicJadePlugin}: the lines Jade draws over a Terrassic animal. */
enum JadeDinoTooltip implements IEntityComponentProvider {
    INSTANCE;

    @Override
    public ResourceLocation getUid() {
        return TerrassicJadePlugin.UID;
    }

    @Override
    public void appendTooltip(ITooltip tooltip, EntityAccessor accessor, IPluginConfig config) {
        if (!(accessor.getEntity() instanceof DinosaurEntity d)) {
            return;
        }
        CompoundTag server = accessor.getServerData().getCompound("Terrassic");
        boolean hasServer = !server.isEmpty();
        // species · sex · calf/adult · level (the title is the custom name when it has one)
        MutableComponent line = d.speciesName().copy()
                .append(" · ").append(Component.translatable(d.isFemale() ? "sex.terrassic.female" : "sex.terrassic.male"))
                .append(" · ").append(Component.translatable(d.isBaby() ? "jade.terrassic.baby" : "jade.terrassic.adult"))
                .append(" · ").append(Component.translatable("hud.terrassic.level", Math.max(1, d.getLevel())));
        tooltip.add(line.withStyle(ChatFormatting.GRAY));
        if (d.isAlpha()) {
            tooltip.add(Component.translatable("jade.terrassic.alpha").withStyle(ChatFormatting.GOLD));
        }
        if (d.isTame()) {
            String owner = hasServer && server.contains("Owner") ? server.getString("Owner") : ownerOnClient(d.getOwnerUUID());
            tooltip.add(owner == null ? Component.translatable("jade.terrassic.tame").withStyle(ChatFormatting.GREEN)
                    : Component.translatable("jade.terrassic.owner", owner).withStyle(ChatFormatting.GREEN));
        } else {
            tooltip.add(Component.translatable("jade.terrassic.wild").withStyle(ChatFormatting.GRAY));
        }
        if (d.isKnockedOut()) {
            MutableComponent ko = Component.translatable("hud.terrassic.knocked_out");
            if (hasServer) {
                int torpor = Mth.floor(100.0F * server.getFloat("Torpor") / Math.max(1.0F, server.getFloat("MaxTorpor")));
                int secs = server.getInt("WakeSeconds");
                ko.append(" · ").append(Component.translatable("jade.terrassic.torpor", torpor))
                        .append(" · ").append(Component.translatable("jade.terrassic.wakes", secs / 60 + ":" + String.format("%02d", secs % 60)));
            }
            tooltip.add(ko.withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        if (!d.isTame() && hasServer && server.getFloat("Progress") > 0.0F) {
            int percent = Mth.floor(100.0F * Math.min(1.0F, server.getFloat("Progress") / Math.max(1.0E-3F, server.getFloat("Goal"))));
            tooltip.add(Component.translatable("jade.terrassic.taming", percent).withStyle(ChatFormatting.DARK_GREEN));
        }
    }

    /** The owner's name when they are on the client's player list (a server without Jade sends no name). */
    private static String ownerOnClient(UUID id) {
        Minecraft mc = Minecraft.getInstance();
        if (id == null || mc.getConnection() == null) {
            return null;
        }
        PlayerInfo info = mc.getConnection().getPlayerInfo(id);
        return info == null ? null : info.getProfile().getName();
    }
}
