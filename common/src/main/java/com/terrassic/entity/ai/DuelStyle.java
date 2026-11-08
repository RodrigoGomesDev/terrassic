package com.terrassic.entity.ai;

import java.util.Map;

/**
 * How each species duels (06/11/2026, the epic duel, docs/estudos/11_LUTA_EPICA.md): the angle it keeps its body at in
 * guard (the theropods side-on, the horned and dome-headed face-on, the Ankylosaurus flank-on), how far its weapon
 * reaches past its body, how far its lunge carries it, its quick blow and its signature blow (animation, hit tick,
 * length), and its temper: how often it parries, blocks and sidesteps, how patient it is, how fast it circles.
 * The lunge (36 ticks, hit at 10), parry (30 ticks, counter at 12) and stagger (32 ticks) animations are the same
 * length in every rig (tools/modelgen/handmade/&lt;species&gt;/&lt;x&gt;fight.py).
 *
 * @param profile    degrees between its body and the line to the rival in guard (0 face-on)
 * @param reach      blocks the weapon reaches past the front of its box, at size 1
 * @param lunge      blocks the lunge carries it, at size 1
 * @param jab        quick blow: animation, hit tick, total ticks
 * @param special    signature blow: animation, hit tick, total ticks (null: none)
 * @param around     the weapon reaches round the body (the Ankylosaurus' tail): no front cone for the hit
 */
public record DuelStyle(float profile, double reach, double lunge, String jab, int jabHit, int jabTotal,
                        String special, int specialHit, int specialTotal, boolean around,
                        float parry, float block, float dodge, int patience, float circle) {

    public static final int LUNGE_HIT = 10;
    public static final int LUNGE_TOTAL = 36;
    public static final int PARRY_COUNTER = 12;
    public static final int PARRY_TOTAL = 30;
    public static final int STAGGER_TOTAL = 32;

    private static final DuelStyle DEFAULT = new DuelStyle(30.0F, 2.5D, 6.0D, "attack", 8, 20, null, 0, 0, false,
            0.15F, 0.25F, 0.10F, 70, 0.55F);

    private static final Map<String, DuelStyle> STYLES = Map.ofEntries(
            // the bone-crushing bite: heavy, patient, blocks with the skull and parries well, a long lunge
            Map.entry("tyrannosaurus", new DuelStyle(45.0F, 4.2D, 7.0D, "attack_quick", 6, 24, "shove", 13, 28, false,
                    0.22F, 0.30F, 0.06F, 80, 0.50F)),
            // the fastest of the big ones: impatient, rams with the horns, the longest lunge, dodges, rarely blocks
            Map.entry("carnotaurus", new DuelStyle(35.0F, 3.4D, 9.0D, "attack_quick", 4, 19, "ram", 15, 32, false,
                    0.12F, 0.15F, 0.22F, 50, 0.75F)),
            // the most patient tyrannosaurid: blocks a lot with the heavy skull, parries into a bite at the rival's face,
            // hardly dodges; a short heavy lunge (docs/estudos/13, Daspletossauro)
            Map.entry("daspletosaurus", new DuelStyle(40.0F, 3.4D, 5.5D, "attack_quick", 6, 18, "face_bite", 11, 28, false,
                    0.30F, 0.40F, 0.03F, 100, 0.40F)),
            // cuts and backs off: slashes from the side, waits, counters
            Map.entry("giganotosaurus", new DuelStyle(45.0F, 4.6D, 7.0D, "slash", 10, 28, "rip", 9, 44, false,
                    0.25F, 0.20F, 0.08F, 90, 0.45F)),
            // the sail shown side-on, the thumb claw, the crocodile snap
            Map.entry("spinosaurus", new DuelStyle(55.0F, 4.6D, 6.0D, "attack_quick", 7, 18, "claw_swipe", 12, 30, false,
                    0.20F, 0.25F, 0.08F, 75, 0.45F)),
            // leaps in with the sickle claws, wings for balance, all speed and sidesteps
            Map.entry("dakotaraptor", new DuelStyle(30.0F, 2.2D, 8.0D, "attack", 7, 18, "pounce", 10, 24, false,
                    0.15F, 0.08F, 0.30F, 40, 0.85F)),
            // arms spread, the claws cut in a cross; short steps, many blocks with the arms
            Map.entry("therizinosaurus", new DuelStyle(20.0F, 3.0D, 4.0D, "attack", 9, 24, "scissor", 11, 28, false,
                    0.20F, 0.40F, 0.05F, 70, 0.45F)),
            // the dome: face-on, a run and a butt, flank butts
            Map.entry("pachycephalosaurus", new DuelStyle(0.0F, 1.6D, 9.0D, "attack", 8, 20, "flank_butt", 8, 20, false,
                    0.10F, 0.10F, 0.25F, 45, 0.80F)),
            // horns always at the rival; the lunge a short heavy charge; the horns take the blows
            Map.entry("triceratops", new DuelStyle(0.0F, 2.8D, 6.0D, "attack", 9, 20, "horn_sweep", 11, 24, false,
                    0.18F, 0.45F, 0.04F, 70, 0.40F)),
            Map.entry("styracosaurus", new DuelStyle(0.0F, 2.6D, 7.0D, "nose_jab", 6, 16, "horn_hook", 9, 20, false,
                    0.20F, 0.35F, 0.06F, 60, 0.50F)),
            // small and stubborn: the beak that holds, the frill shove
            Map.entry("protoceratops", new DuelStyle(0.0F, 1.3D, 4.0D, "attack", 8, 16, "frill_shove", 8, 24, false,
                    0.15F, 0.30F, 0.12F, 45, 0.70F)),
            // the flank to the rival, the club swung round: no front cone
            Map.entry("ankylosaurus", new DuelStyle(70.0F, 3.8D, 2.0D, "club_l", 12, 32, "flank_club", 24, 60, true,
                    0.10F, 0.55F, 0.02F, 80, 0.35F)));

    public static DuelStyle of(String species) {
        return STYLES.getOrDefault(species, DEFAULT);
    }
}
