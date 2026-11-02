package com.terrassic.entity;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;

/**
 * What only an alpha of a species does (docs/ALFAS.md, Rodrigo 02/11: "animacoes proprias dele"): its own walk, idle
 * acts, threat, blows and the stir before it wakes from a knockout. One subclass per species with alpha animations
 * (the T. rex: {@link RexAlphaMoves}); a species without one keeps the common behaviour on its alpha. Held by the
 * animal ({@link ApexTheropod#alphaMoves()}), so a subclass can keep timers.
 */
public abstract class AlphaMoves {
    protected final ApexTheropod mob;

    protected AlphaMoves(ApexTheropod mob) {
        this.mob = mob;
    }

    /** The moves of an alpha of this animal's species, or null for a species without its own. */
    static AlphaMoves create(ApexTheropod mob) {
        return switch (mob.speciesId()) {
            case "tyrannosaurus" -> new RexAlphaMoves(mob);
            default -> null;
        };
    }

    /** The one-shot animations to register on the action controller for this species (registered on every animal
     *  of the species: the controllers are built before the alpha flag reaches the client). */
    static String[] actions(String species) {
        return switch (species) {
            case "tyrannosaurus" -> RexAlphaMoves.ACTIONS;
            default -> new String[0];
        };
    }

    /** The calm walk loop (null = the species' own), and its cycle in blocks per tick at model scale 1. */
    public String walkAnim() {
        return null;
    }

    public double walkCycle() {
        return 0.0D;
    }

    /** The one-shot in place of the threat (when a player walks up to it while it is not hunting). */
    public String threatAnim() {
        return "threat";
    }

    /** An idle act of its own when it stands with nothing to do; true if it did one (else a common gesture plays). */
    public boolean gesture(ServerLevel level) {
        return false;
    }

    /** A blow of its own for a target in reach of the head, or null for the common bite. */
    public ApexTheropod.Strike bite(LivingEntity target) {
        return null;
    }

    /** A blow for a target beside or behind it (out of the head's reach), or null for none. */
    public ApexTheropod.Strike side(LivingEntity target) {
        return null;
    }

    /** Whether a blow plays to its end on planted feet (its legs do not walk, so it must not move under it). */
    public boolean standsOut(ApexTheropod.Strike strike) {
        return false;
    }

    /** Called right after a blow of its own landed on the target. */
    public void struck(LivingEntity target, ApexTheropod.Strike strike) {
    }

    /** Server, every tick of a living alpha. */
    public void tick(ServerLevel level) {
    }

    /** Whether one of its own acts holds it in place (no walking off in the middle of it). */
    public boolean busy() {
        return false;
    }

    /** The one-shot when, knocked out, it is about to wake (null = none). */
    public String stirAnim() {
        return null;
    }
}
