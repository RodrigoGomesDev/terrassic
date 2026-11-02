package com.terrassic.entity;

import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The Giganotosaurus rig (tools/modelgen/handmade/giganotosaurus, made for it from its own study: 35 animations of its
 * own, the list Rodrigo approved on 01/11/2026). The life of an {@link ApexTheropod}, with what this animal does
 * differently:
 * <ul>
 *   <li><b>Cut and wait</b>: its main blow is a cut with the blade teeth ("slash"); it lets go at once, steps back
 *       facing the prey ("back_off"), stands and aims at it with one eye ("eye_aim": the eyes look sideways), then
 *       walks sideways round it ("circle") before it comes in again. At big prey it also throws a long low strike at
 *       the legs ("lunge") and holds on and shakes like a shark ("rip").</li>
 *   <li><b>No sprint</b>: its fast gait is a forced march, one foot always on the ground.</li>
 *   <li><b>Its warning</b> is the huge mouth opened in profile ("gape"); the roars go low and forward, never up.</li>
 *   <li><b>Pairs</b>: it keeps company with its mate (not solitary like the T. rex) and gives way only to a bigger
 *       rival of its own sex.</li>
 *   <li><b>Its own idle gestures</b>: it looks to the side with one eye, rubs its mouth on the ground; the male shows
 *       the red lumps of its snout.</li>
 * </ul>
 */
public abstract class Giganotosaurine extends ApexTheropod {
    /** The cycles: pixels of ground each one covers and its length in ticks (gigaanims.py WALK, MARCH, stalk =
     *  the walk at 0.7 of the stride and 1.5 times as long, back_off, circle). */
    private static final double WALK_PX = 84.0D;
    private static final double WALK_TICKS = 40.0D;
    private static final double RUN_PX = 118.0D;
    private static final double RUN_TICKS = 23.0D;
    private static final double STALK_PX = 59.0D;
    private static final double STALK_TICKS = 60.0D;
    private static final double BACK_PX = 44.0D;
    private static final double BACK_TICKS = 32.0D;
    private static final double CIRCLE_PX = 26.0D;
    private static final double CIRCLE_TICKS = 36.0D;
    /** The mouth in the loud roar: head low and forward (blocks at model scale 1). */
    private static final double MOUTH_FORWARD = 9.6D;
    private static final double MOUTH_UP = 4.6D;
    /** Targets at least this wide (blocks) are big prey: the lunge and the rip. */
    private static final float BIG = 2.0F;
    private static final Strike SLASH = new Strike("slash", 10, 28, false);
    private static final Strike LUNGE = new Strike("lunge", 12, 32, false);
    private static final Strike RIP = new Strike("rip", 9, 44, false);
    private static final String[] GESTURES = {"sniff", "look_side", "shake", "yawn", "stretch", "jaw_rub"};
    private static final String[] GESTURES_MALE = {"sniff", "look_side", "shake", "yawn", "stretch", "jaw_rub", "crest_show"};
    private RawAnimation backAnim;
    private RawAnimation circleAnim;

    protected Giganotosaurine(EntityType<? extends Giganotosaurine> type, Level level) {
        super(type, level);
    }

    /** Its own one-shots (no "look_back": its look round is "look_side"), plus an alpha's moves if it ever gets one,
     *  as ApexTheropod adds them. */
    @Override
    protected String[] extraActions() {
        String[] own = {"roar", "roar_loud", "attack_quick", "stomp", "call", "threat", "drink", "sniff", "shake", "yawn",
                "stretch", "look_side", "jaw_rub", "crest_show", "eye_aim", "slash", "lunge", "rip"};
        if (!Alphas.hasAlpha(this.speciesId())) {
            return own;
        }
        String[] alpha = AlphaMoves.actions(this.speciesId());
        String[] all = java.util.Arrays.copyOf(own, own.length + alpha.length);
        System.arraycopy(alpha, 0, all, own.length, alpha.length);
        return all;
    }

    /** "attack" is its cut; "threat" its mouth shown in profile. */
    @Override
    protected String actionAnimation(String trigger) {
        return switch (trigger) {
            case "attack" -> "slash";
            case "threat" -> "gape";
            default -> trigger;
        };
    }

    @Override
    protected String[] gestures() {
        return this.isFemale() ? GESTURES : GESTURES_MALE;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    @Override
    protected double stalkCycleSpeed() {
        return STALK_PX / 16.0D / STALK_TICKS * this.modelScale();
    }

    @Override
    protected double loudMouthForward() {
        return MOUTH_FORWARD;
    }

    @Override
    protected double loudMouthUp() {
        return MOUTH_UP;
    }

    /** Fighting, it steps back and walks sideways (the pause after the cut): its own cycles, picked from the way it
     *  really moved against the way it faces. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving() && this.isAggressive() && !this.isVehicle() && !this.isSleeping() && !this.isSwimmingDeep()) {
            double dx = this.getX() - this.xo;
            double dz = this.getZ() - this.zo;
            double d2 = dx * dx + dz * dz;
            if (d2 > 1.0E-4D) {
                float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
                double ahead = (-Mth.sin(yaw) * dx + Mth.cos(yaw) * dz) / Math.sqrt(d2);
                if (ahead < -0.5D) {
                    if (this.backAnim == null) {
                        this.backAnim = RawAnimation.begin().thenLoop(anim("back_off"));
                    }
                    PlayState play = state.setAndContinue(this.backAnim);
                    this.cycleSpeed = this.gaitSpeed(BACK_PX / 16.0D / BACK_TICKS * this.modelScale());
                    return play;
                }
                if (ahead < 0.5D) {
                    if (this.circleAnim == null) {
                        this.circleAnim = RawAnimation.begin().thenLoop(anim("circle"));
                    }
                    PlayState play = state.setAndContinue(this.circleAnim);
                    this.cycleSpeed = this.gaitSpeed(CIRCLE_PX / 16.0D / CIRCLE_TICKS * this.modelScale());
                    return play;
                }
            }
        }
        return super.movementAnimation(state);
    }

    /** It lives in loose pairs: its mate keeps near it, and only a bigger rival of its own sex makes it give way. */
    @Override
    protected boolean solitary() {
        return false;
    }

    @Override
    protected boolean givesWayTo(ApexTheropod rival) {
        return super.givesWayTo(rival) && rival.isFemale() == this.isFemale();
    }

    @Override
    public Strike biteFor(LivingEntity target) {
        float r = this.getRandom().nextFloat();
        if (target.getBbWidth() >= BIG) {
            return r < 0.4F ? SLASH : (r < 0.7F ? LUNGE : RIP);
        }
        return r < 0.75F ? SLASH : LUNGE;
    }

    /** After the cut: two steps back, a look with one eye, a little circling (1.5 - 2.5 s). After the lunge, a step
     *  back. The rip holds on and needs no pause. */
    @Override
    public Pause pauseAfter(Strike strike) {
        Pause alpha = super.pauseAfter(strike);   // an alpha's own rule first (none today: only the T. rex has alphas)
        if (alpha != null) {
            return alpha;
        }
        if (strike == SLASH) {
            return new Pause(16, "eye_aim", 30, 30 + this.getRandom().nextInt(20));
        }
        if (strike == LUNGE) {
            return new Pause(10, null, 0, 0);
        }
        return null;
    }
}
