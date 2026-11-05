package com.terrassic.mixin.parts;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.parts.DinoParts;
import com.terrassic.entity.parts.PartOwners;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Predicate;

/**
 * Hit parts (1.7, entity/parts/DinoPart): the list of entities in a box also gets the creatures' heads and tails, as
 * vanilla does for the Ender Dragon's parts (Forge only does it for its own PartEntity). This is what the crosshair,
 * arrows and thrown spears search, so they can hit a part. The creatures with parts are kept here, on the level.
 */
@Mixin(Level.class)
public abstract class LevelMixin implements PartOwners {
    @Unique
    private static final DinosaurEntity[] terrassic$NONE = new DinosaurEntity[0];
    @Unique
    private volatile DinosaurEntity[] terrassic$owners = terrassic$NONE;

    @Inject(method = "getEntities(Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/phys/AABB;Ljava/util/function/Predicate;)Ljava/util/List;",
            at = @At("RETURN"))
    private void terrassic$addParts(Entity except, AABB box, Predicate<? super Entity> filter, CallbackInfoReturnable<List<Entity>> cir) {
        if (this.terrassic$owners.length > 0) {
            DinoParts.addParts((Level) (Object) this, except, box, filter, cir.getReturnValue());
        }
    }

    @Override
    public DinosaurEntity[] terrassic$partOwners() {
        return this.terrassic$owners;
    }

    @Override
    public synchronized void terrassic$addPartOwner(DinosaurEntity owner) {
        DinosaurEntity[] now = this.terrassic$owners;
        for (DinosaurEntity e : now) {
            if (e == owner) {
                return;
            }
        }
        List<DinosaurEntity> next = new ArrayList<>(now.length + 1);
        for (DinosaurEntity e : now) {
            if (!e.isRemoved()) {
                next.add(e);
            }
        }
        next.add(owner);
        this.terrassic$owners = next.toArray(terrassic$NONE);
    }

    @Override
    public synchronized void terrassic$prunePartOwners() {
        Level self = (Level) (Object) this;
        DinosaurEntity[] next = Arrays.stream(this.terrassic$owners)
                .filter(e -> !e.isRemoved() && e.level() == self)
                .toArray(DinosaurEntity[]::new);
        this.terrassic$owners = next;
    }
}
