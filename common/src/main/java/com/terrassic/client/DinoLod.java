package com.terrassic.client;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.animation.AnimationProcessor;
import software.bernie.geckolib.model.GeoModel;

import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

/**
 * 1.11, a simpler model far from the camera (docs/DESEMPENHO_1_11.md, approved by Rodrigo). Past "lod_near" blocks
 * (config/terrassic-client.json, 32 by default) the bones are worked out every second frame and past "lod_far" (64)
 * every third; on the frames in between the pose worked out last is put back on the shared model. The live layer
 * (LivelyMotion) fades out over the 8 blocks past "lod_near", and cubes smaller than half a pixel on the screen are not
 * drawn (DinosaurRenderer#renderCubesOfBone). 0 in "lod_near" turns it all off.
 */
public final class DinoLod {
    /** How far past "lod_near" the live layer fades out (blocks). */
    public static final double LIVELY_FADE = 8.0D;
    private static int near = -1;
    private static int far;
    /** GeoModel.lastRenderedInstance: after a pose is put back by hand, GeckoLib must not take the model's bones for
     *  the instance it rendered last (a second pass in the same frame, e.g. a shader's shadow pass). */
    private static final VarHandle LAST_RENDERED = lastRendered();

    private DinoLod() {
    }

    private static VarHandle lastRendered() {
        try {
            return MethodHandles.privateLookupIn(GeoModel.class, MethodHandles.lookup())
                    .findVarHandle(GeoModel.class, "lastRenderedInstance", long.class);
        } catch (Throwable e) {
            return null;
        }
    }

    private static void read() {
        if (near < 0) {
            near = Math.max(0, ClientConfig.intOption("lod_near", 32));
            far = Math.max(near, ClientConfig.intOption("lod_far", 64));
        }
    }

    public static int near() {
        read();
        return near;
    }

    /** Squared distance from the camera, or -1 when the animal is not one in the world (a picture in a screen). */
    public static double distSq(DinosaurEntity e) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || e.level() != mc.level || mc.level.getEntity(e.getId()) != e) {
            return -1.0D;
        }
        Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        return e.distanceToSqr(cam);
    }

    /** 0 = every frame, 1 = every second frame, 2 = every third. */
    public static int level(double d2) {
        read();
        if (near <= 0 || d2 < 0.0D || d2 < (double) near * near) {
            return 0;
        }
        return d2 < (double) far * far ? 1 : 2;
    }

    /** The live layer's weight: 1 up to "lod_near", down to 0 over the next 8 blocks. */
    public static float livelyWeight(double d2) {
        read();
        if (near <= 0 || d2 < 0.0D) {
            return 1.0F;
        }
        double d = Math.sqrt(d2);
        return (float) Math.max(0.0D, Math.min(1.0D, (near + LIVELY_FADE - d) / LIVELY_FADE));
    }

    /** The smallest cube (model px, before the model's scale) that still covers half a screen pixel, or 0 when every
     *  cube is drawn (nearer than "lod_near", or not in the world). */
    public static float cullPx(double d2, float renderScale) {
        read();
        if (near <= 0 || d2 < 0.0D || d2 < (double) near * near || renderScale <= 0.0F) {
            return 0.0F;
        }
        Minecraft mc = Minecraft.getInstance();
        double d = Math.sqrt(d2);
        double fov = Math.toRadians(mc.options.fov().get());
        double pxPerBlock = mc.getWindow().getHeight() / (2.0D * d * Math.tan(fov / 2.0D));
        return (float) (8.0D / (renderScale * pxPerBlock));   // half a pixel, in model px (16 to a block)
    }

    /** One animal's last worked-out pose: every bone's rotation, position, scale and hiding. */
    public static final class Pose {
        private GeoBone[] bones = new GeoBone[0];
        private float[] values = new float[0];
        private boolean[] hidden = new boolean[0];
        private boolean valid;
        private int count;

        /** True on the frames that put the last pose back instead of working one out. */
        public boolean skip(int level, AnimationProcessor<?> processor) {
            if (level <= 0 || LAST_RENDERED == null) {
                this.valid = false;
                return false;
            }
            if (!this.valid || this.bones.length == 0 || processor.getBone(this.bones[0].getName()) != this.bones[0]) {
                return false;
            }
            return ++this.count % (level + 1) != 0;
        }

        public void capture(AnimationProcessor<?> processor) {
            int n = processor.getRegisteredBones().size();
            if (this.bones.length != n) {
                this.bones = new GeoBone[n];
                this.values = new float[n * 9];
                this.hidden = new boolean[n * 2];
            }
            int i = 0;
            for (GeoBone b : processor.getRegisteredBones()) {
                this.bones[i] = b;
                int v = i * 9;
                this.values[v] = b.getRotX();
                this.values[v + 1] = b.getRotY();
                this.values[v + 2] = b.getRotZ();
                this.values[v + 3] = b.getPosX();
                this.values[v + 4] = b.getPosY();
                this.values[v + 5] = b.getPosZ();
                this.values[v + 6] = b.getScaleX();
                this.values[v + 7] = b.getScaleY();
                this.values[v + 8] = b.getScaleZ();
                this.hidden[i * 2] = b.isHidden();
                this.hidden[i * 2 + 1] = b.isHidingChildren();
                i++;
            }
            this.valid = n > 0;
        }

        public void restore(GeoModel<?> model) {
            for (int i = 0; i < this.bones.length; i++) {
                GeoBone b = this.bones[i];
                int v = i * 9;
                b.setRotX(this.values[v]);
                b.setRotY(this.values[v + 1]);
                b.setRotZ(this.values[v + 2]);
                b.setPosX(this.values[v + 3]);
                b.setPosY(this.values[v + 4]);
                b.setPosZ(this.values[v + 5]);
                b.setScaleX(this.values[v + 6]);
                b.setScaleY(this.values[v + 7]);
                b.setScaleZ(this.values[v + 8]);
                b.setHidden(this.hidden[i * 2]);
                b.setChildrenHidden(this.hidden[i * 2 + 1]);
                // the "changed" marks stay clear, as GeckoLib leaves them after its own tick (DinoGeoModel's 1.9.1 hotfix)
                b.resetStateChanges();
            }
            LAST_RENDERED.set(model, Long.MIN_VALUE);
        }
    }
}
