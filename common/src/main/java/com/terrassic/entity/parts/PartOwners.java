package com.terrassic.entity.parts;

import com.terrassic.entity.DinosaurEntity;

/**
 * The creatures of a level that have hit parts (1.7), kept on the Level itself by {@code mixin.LevelMixin} so that
 * Level#getEntities can add their parts without searching a wider box every time. Copy on write: the getters read a
 * snapshot, the creature adds itself when it first ticks, and removed ones are dropped the next time they are met.
 */
public interface PartOwners {
    DinosaurEntity[] terrassic$partOwners();

    void terrassic$addPartOwner(DinosaurEntity owner);

    /** Drops the owners that were removed (dead, unloaded, changed dimension). */
    void terrassic$prunePartOwners();
}
