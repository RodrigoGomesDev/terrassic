package com.terrassic.client.compat;

import com.terrassic.entity.DinosaurEntity;
import dev.architectury.platform.Platform;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.WeakHashMap;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.cache.object.GeoCube;
import software.bernie.geckolib.cache.object.GeoQuad;
import software.bernie.geckolib.cache.object.GeoVertex;
import software.bernie.geckolib.model.GeoModel;

/**
 * Hats Renewed on the dinosaurs (05/11/2026, Rodrigo: "melhore a parte de hitbox para mods como o de hats renewed").
 * Hats finds a GeckoLib animal's "head" bone and builds its matrix from the bone chain alone: it leaves out the model
 * scale our renderer draws with (a 12 m Deinosuchus is drawn at 0.8, a baby at a fraction of that) and sizes the hat by
 * the hitbox width, so the hat floated far from the head, too big or too small. Here, right after an animal is drawn,
 * the pose of its skull bone gives the real spot: the top of the cranium, the back
 * of its biggest box (over the braincase, not halfway down a long snout), sized to that box. The mixin
 * {@code mixin.client.HatsHeadMixin} hands it to Hats; nothing of this runs without Hats installed.
 */
public final class HatsCompat {
    public static final boolean PRESENT = Platform.isModLoaded("hats");
    /** Hats sizes a hat by the hitbox width over a player's (0.6), clamped; a player's head is half a block wide. */
    private static final float PLAYER_WIDTH = 0.6F;
    private static final float PLAYER_HEAD = 0.5F;
    /** The hat narrower than the cranium (the hats are drawn for a player's head; on a wide skull the big ones looked like boxes). */
    private static final float FIT = 0.75F;

    private static final Map<Entity, Matrix4f> ANCHORS = new WeakHashMap<>();
    /** Per skull bone of a baked model: the crown point (x, y, z, in blocks, model space at rest) and the width. */
    private static final Map<GeoBone, float[]> CROWNS = new IdentityHashMap<>();

    private HatsCompat() {
    }

    /** After drawing an animal: where its hat sits, in the frame Hats multiplies into (already turned by the body
     *  yaw). The bones of a model are shared by every animal of the species and hold the pose of the one drawn last,
     *  this one: the chain from the root to the skull is rebuilt the way GeckoLib draws it (RenderUtils.prepMatrixForBone),
     *  times the renderer's scale. */
    public static void capture(DinosaurEntity entity, GeoModel<?> model, float renderScale) {
        Optional<GeoBone> found = skull(model);
        if (found.isEmpty() || entity.isPerched() || renderScale <= 0.0F) {
            ANCHORS.remove(entity);
            return;
        }
        GeoBone skull = found.get();
        float[] crown = CROWNS.computeIfAbsent(skull, HatsCompat::crownOf);
        if (crown == null) {
            ANCHORS.remove(entity);
            return;
        }
        java.util.ArrayList<GeoBone> chain = new java.util.ArrayList<>();
        for (GeoBone b = skull; b != null; b = b.getParent()) {
            chain.add(0, b);
        }
        Matrix4f m = new Matrix4f().scale(renderScale);
        for (GeoBone b : chain) {
            m.translate(-b.getPosX() / 16.0F, b.getPosY() / 16.0F, b.getPosZ() / 16.0F)
                    .translate(b.getPivotX() / 16.0F, b.getPivotY() / 16.0F, b.getPivotZ() / 16.0F)
                    .rotateZ(b.getRotZ()).rotateY(b.getRotY()).rotateX(b.getRotX())
                    .scale(b.getScaleX(), b.getScaleY(), b.getScaleZ())
                    .translate(-b.getPivotX() / 16.0F, -b.getPivotY() / 16.0F, -b.getPivotZ() / 16.0F);
        }
        float want = Mth.clamp(crown[3] * renderScale * FIT / PLAYER_HEAD, 0.15F, 8.0F);
        float hats = Mth.clamp(entity.getBbWidth() / PLAYER_WIDTH, 0.2F, 3.0F);
        m.translate(crown[0], crown[1], crown[2]).scale(want / hats / renderScale);
        ANCHORS.put(entity, m);
    }

    /** The hat's frame for an animal drawn this frame, or null (Hats then falls back to its own guess). */
    public static Matrix4f anchor(Entity entity) {
        Matrix4f m = ANCHORS.get(entity);
        return m == null ? null : new Matrix4f(m);
    }

    private static Optional<GeoBone> skull(GeoModel<?> model) {
        Optional<GeoBone> skull = model.getBone("skull");
        return skull.isPresent() && !skull.get().getCubes().isEmpty() ? skull : model.getBone("head");
    }

    /** The top of the bone's biggest unturned box, at the back (+z, the model looks to -z) by half its width. */
    private static float[] crownOf(GeoBone bone) {
        GeoCube best = null;
        double bestSize = 0.0D;
        for (boolean turnedToo : new boolean[]{false, true}) {
            for (GeoCube cube : bone.getCubes()) {
                Vec3 r = cube.rotation();
                if (!turnedToo && (Math.abs(r.x) > 1.0E-3D || Math.abs(r.y) > 1.0E-3D || Math.abs(r.z) > 1.0E-3D)) {
                    continue;
                }
                double size = cube.size().x * cube.size().y * cube.size().z;
                if (size > bestSize) {
                    best = cube;
                    bestSize = size;
                }
            }
            if (best != null) {
                break;
            }
        }
        if (best == null) {
            return null;
        }
        Vector3f lo = new Vector3f(Float.MAX_VALUE);
        Vector3f hi = new Vector3f(-Float.MAX_VALUE);
        for (GeoQuad quad : best.quads()) {
            if (quad == null) {
                continue;
            }
            for (GeoVertex v : quad.vertices()) {
                lo.min(v.position());
                hi.max(v.position());
            }
        }
        if (lo.x > hi.x) {
            return null;
        }
        float width = hi.x - lo.x;
        float z = Math.max((lo.z + hi.z) * 0.5F, hi.z - width * 0.5F);
        return new float[]{(lo.x + hi.x) * 0.5F, hi.y, z, width};
    }
}
