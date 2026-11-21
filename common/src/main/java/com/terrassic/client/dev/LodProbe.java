package com.terrassic.client.dev;

import com.terrassic.client.DinoLod;
import com.terrassic.entity.DinosaurEntity;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.animation.AnimationProcessor;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * Development only (client/dev/Playtest, the approach): records, frame by frame, how far the bones of ONE animal moved
 * since the frame before, with its distance to the camera. A model that "jumps" when the camera crosses a LOD distance
 * (client/DinoLod: 32 the live layer starts to fade and the bones every second frame, 40 the layer gone, 64 every third
 * frame) shows as one frame with a much larger change than the frames round it. Off (id -1) it costs one int compare.
 */
public final class LodProbe {
    public static volatile int id = -1;
    /** {distance to the camera, sum of |rotation change| in radians + |position change| in blocks} per frame */
    public static final List<double[]> FRAMES = new ArrayList<>();
    private static float[] last;

    private LodProbe() {
    }

    public static void start(int entityId) {
        FRAMES.clear();
        last = null;
        id = entityId;
    }

    public static void stop() {
        id = -1;
        last = null;
    }

    public static void frame(DinosaurEntity e, AnimationProcessor<?> processor) {
        if (e.getId() != id) {
            return;
        }
        Collection<GeoBone> bones = processor.getRegisteredBones();
        float[] now = new float[bones.size() * 6];
        int i = 0;
        for (GeoBone b : bones) {
            now[i++] = b.getRotX();
            now[i++] = b.getRotY();
            now[i++] = b.getRotZ();
            now[i++] = b.getPosX() / 16.0F;
            now[i++] = b.getPosY() / 16.0F;
            now[i++] = b.getPosZ() / 16.0F;
        }
        double d2 = DinoLod.distSq(e);
        if (last != null && last.length == now.length && d2 >= 0.0D) {
            double s = 0.0D;
            for (int k = 0; k < now.length; k++) {
                s += Math.abs(now[k] - last[k]);
            }
            FRAMES.add(new double[]{Math.sqrt(d2), s});
        }
        last = now;
    }
}
