package com.terrassic.compat.jade;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import snownee.jade.api.EntityAccessor;
import snownee.jade.api.IServerDataProvider;
import snownee.jade.api.IWailaClientRegistration;
import snownee.jade.api.IWailaCommonRegistration;
import snownee.jade.api.IWailaPlugin;
import snownee.jade.api.WailaPlugin;

/**
 * Jade (1.11, a player's request: docs/DESEMPENHO_1_11.md): what Jade shows over a Terrassic animal. Loaded only by
 * Jade itself (the "jade" entrypoint in fabric.mod.json, {@link WailaPlugin} on Forge); without Jade this class is never
 * touched, and the mod has no dependency on it (compileOnly).
 *
 * <p>Lines: species, sex, calf or adult and level; tame and its owner; an alpha; knocked out with the torpor and the time
 * until it wakes; the taming progress. Jade's own health line stays. What only the server knows (owner's name, torpor,
 * taming) comes from {@link #appendServerData}, a trimmed copy of the Field Lens card
 * ({@link DinosaurEntity#lensInfo}); on a server without Jade the client's synced data still gives the rest.
 */
@WailaPlugin
public final class TerrassicJadePlugin implements IWailaPlugin {
    static final ResourceLocation UID = new ResourceLocation("terrassic", "dinosaur");

    @Override
    public void register(IWailaCommonRegistration registration) {
        registration.registerEntityDataProvider(ServerData.INSTANCE, DinosaurEntity.class);
    }

    @Override
    public void registerClient(IWailaClientRegistration registration) {
        registration.registerEntityComponent(JadeDinoTooltip.INSTANCE, DinosaurEntity.class);
        // the crosshair on a head, neck or tail (a hit part, entity/parts) shows its creature
        registration.addRayTraceCallback((hit, accessor, original) -> JadeDinoTooltip.owner(registration, accessor));
    }

    /** The server side: what only the server knows (works on a dedicated server, no client class touched). */
    enum ServerData implements IServerDataProvider<EntityAccessor> {
        INSTANCE;

        @Override
        public ResourceLocation getUid() {
            return UID;
        }

        @Override
        public void appendServerData(CompoundTag data, EntityAccessor accessor) {
            if (!(accessor.getEntity() instanceof DinosaurEntity d)) {
                return;
            }
            CompoundTag lens = d.lensInfo(accessor.getPlayer());
            CompoundTag t = new CompoundTag();
            for (String key : new String[]{"Owner", "KnockedOut", "Torpor", "MaxTorpor", "WakeSeconds", "Progress", "Goal"}) {
                if (lens.contains(key)) {
                    t.put(key, lens.get(key));
                }
            }
            data.put("Terrassic", t);
        }

    }
}
