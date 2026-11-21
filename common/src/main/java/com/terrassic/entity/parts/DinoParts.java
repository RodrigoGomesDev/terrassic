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

    /** How far a creature's parts may move within one tick past the bounds the index took (blocks). */
    private static final double PAD = 4.0D;

    /**
     * 1.11 (docs/DESEMPENHO_1_11.md): every Level#getEntities call (each entity's collisions and pushes, every tick)
     * walked all the creatures with parts and read each one's bounds object; with every species in one place that was
     * 5% of the server tick. Once a tick the bounds go into one flat array, padded by {@link #PAD}, and a query only
     * looks closer at the creatures whose padded bounds touch its box. The exact test stays the same as before.
     */
    public static final class Index {
        final DinosaurEntity[] owners;
        final double[] box;
        final long tick;

        Index(DinosaurEntity[] owners, long tick) {
            this.owners = owners;
            this.tick = tick;
            this.box = new double[owners.length * 6];
            for (int i = 0; i < owners.length; i++) {
                AABB b = owners[i].partsBounds();
                int k = i * 6;
                this.box[k] = b.minX - PAD;
                this.box[k + 1] = b.minY - PAD;
                this.box[k + 2] = b.minZ - PAD;
                this.box[k + 3] = b.maxX + PAD;
                this.box[k + 4] = b.maxY + PAD;
                this.box[k + 5] = b.maxZ + PAD;
            }
        }
    }

    /** Adds to a Level#getEntities result the parts that lie in the box (the owner itself is found by the engine). */
    public static void addParts(Level level, Entity except, AABB box, Predicate<? super Entity> filter, List<Entity> out) {
        PartOwners holder = (PartOwners) level;
        DinosaurEntity[] owners = holder.terrassic$partOwners();
        if (owners.length == 0) {
            return;
        }
        long now = level.getGameTime();
        Index index = holder.terrassic$partIndex();
        if (index == null || index.owners != owners || index.tick != now) {
            index = new Index(owners, now);
            holder.terrassic$setPartIndex(index);
        }
        double[] b = index.box;
        boolean stale = false;
        for (int i = 0, k = 0; i < owners.length; i++, k += 6) {
            if (b[k] >= box.maxX || b[k + 3] <= box.minX || b[k + 1] >= box.maxY || b[k + 4] <= box.minY
                    || b[k + 2] >= box.maxZ || b[k + 5] <= box.minZ) {
                continue;
            }
            DinosaurEntity owner = owners[i];
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
            holder.terrassic$prunePartOwners();
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
