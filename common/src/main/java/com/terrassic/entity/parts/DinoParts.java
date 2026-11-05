package com.terrassic.entity.parts;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

import java.util.List;
import java.util.function.Predicate;

/** Hit parts (1.7): the lookups shared by the mixins and by the code that asks "which creature is this?". */
public final class DinoParts {
    /** No species has more parts than this (tools/javagen/parts.py MAX_TOTAL). */
    public static final int MAX_PARTS = 20;

    private DinoParts() {
    }

    /** The creature a hit part belongs to, or the entity itself. Use it wherever a hit or the crosshair is read. */
    public static Entity owner(Entity entity) {
        return entity instanceof DinoPart part ? part.owner : entity;
    }

    /** Adds to a Level#getEntities result the parts that lie in the box (the owner itself is found by the engine). */
    public static void addParts(Level level, Entity except, AABB box, Predicate<? super Entity> filter, List<Entity> out) {
        DinosaurEntity[] owners = ((PartOwners) level).terrassic$partOwners();
        if (owners.length == 0) {
            return;
        }
        boolean stale = false;
        for (DinosaurEntity owner : owners) {
            if (owner.isRemoved() || owner.level() != level) {
                stale = true;
                continue;
            }
            if (owner == except || !owner.partsActive() || !owner.partsBounds().intersects(box)) {
                continue;
            }
            for (DinoPart part : owner.parts()) {
                if (part != except && part.enabled() && part.getBoundingBox().intersects(box) && filter.test(part)) {
                    out.add(part);
                }
            }
        }
        if (stale) {
            ((PartOwners) level).terrassic$prunePartOwners();
        }
    }

    /** The part with this id, for the server's interaction packets (its id follows its owner's). */
    public static Entity partById(ServerLevel level, int id) {
        for (int k = 1; k <= MAX_PARTS; k++) {
            if (level.getEntity(id - k) instanceof DinosaurEntity owner) {
                return owner.partById(id);
            }
        }
        return null;
    }
}
