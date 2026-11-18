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

    /** Jade's own owner line for tamable animals (snownee.jade.api.Identifiers.MC_ANIMAL_OWNER). */
    private static final ResourceLocation OWNER_LINE = new ResourceLocation("minecraft", "animal_owner");

    /** A hit part under the crosshair stands for its creature (its head, neck or tail is the animal for Jade too). */
    static snownee.jade.api.Accessor<?> owner(snownee.jade.api.IWailaClientRegistration registration, snownee.jade.api.Accessor<?> accessor) {
        if (accessor instanceof EntityAccessor e && e.getEntity() instanceof com.terrassic.entity.parts.DinoPart part) {
            return registration.entityAccessor().from(e).entity(part.owner).build();
        }
        return accessor;
    }

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
        // sex · calf/adult (Jade's title already says the species and the level, "Tiranossauro · Nv 11"); with a custom
        // name in the title, the species goes first
        MutableComponent line = Component.empty();
        if (d.hasCustomName()) {
            line.append(d.speciesName()).append(" · ");
        }
        line.append(Component.translatable(d.isFemale() ? "sex.terrassic.female" : "sex.terrassic.male"))
                .append(" · ").append(Component.translatable(d.isBaby() ? "jade.terrassic.baby" : "jade.terrassic.adult"));
        tooltip.add(line.withStyle(ChatFormatting.GRAY));
        if (d.isAlpha()) {
            tooltip.add(Component.translatable("jade.terrassic.alpha").withStyle(ChatFormatting.GOLD));
        }
        // tame or wild; the owner's name only when Jade's own owner line is off (it shows "Dono: ..." by default)
        if (d.isTame()) {
            String owner = config.get(OWNER_LINE) ? null
                    : hasServer && server.contains("Owner") ? server.getString("Owner") : ownerOnClient(d.getOwnerUUID());
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
