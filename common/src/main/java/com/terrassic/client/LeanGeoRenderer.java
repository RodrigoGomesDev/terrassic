package com.terrassic.client;

import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.architectury.platform.Platform;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix3f;
import org.joml.Matrix4d;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.joml.Vector4d;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.cache.object.GeoCube;
import software.bernie.geckolib.cache.object.GeoQuad;
import software.bernie.geckolib.cache.object.GeoVertex;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * GeckoLib's entity renderer with a leaner way of writing the cubes (1.11, docs/DESEMPENHO_1_11.md, "Modelos"). The
 * picture is the same; what changes is how much the CPU does per frame for it:
 * <ul>
 *   <li>no allocation per vertex, per quad or per cube (GeckoLib makes a Vector4f per vertex, a Vector3f per quad and
 *   a Matrix4f and three Quaternionf per cube: 640 MB/s with the 120 animals of the PerfTest);</li>
 *   <li>a cube with no rotation of its own is written straight with its bone's matrix (GeckoLib pushes the stack and
 *   turns it by three zero angles for every cube); a rotated cube's own turn is worked out once per model;</li>
 *   <li>a bone hidden together with its children (sexes, saddle, adult/young parts) is skipped whole, not walked;</li>
 *   <li>the back faces of a closed, fully opaque cube are not written: the model is drawn with no face culling
 *   (entityCutoutNoCull), so the GPU would draw them and hide them behind the cube's own front faces. The eye is taken
 *   from the projection and model-view matrices of the moment, so it holds in the world and on screens alike. A cube
 *   with any see-through texel on its faces (in the texture being drawn), a flat cube, a mirrored cube, an invisible
 *   or faded animal, and any game with a shader mod (Iris/Oculus: the shadow pass has its own eye) keep every face.</li>
 * </ul>
 * {@link #setLean} and {@link #setBackfaces} switch the two halves for the per-species benchmark (dev/DrawBench).
 */
public abstract class LeanGeoRenderer<T extends Entity & GeoAnimatable> extends GeoEntityRenderer<T> {
    private static final boolean SHADERS = Platform.isModLoaded("iris") || Platform.isModLoaded("oculus");
    private static volatile boolean lean = !"0".equals(System.getenv("TERRASSIC_LEAN_RENDER"));
    private static volatile boolean backfaces = !SHADERS && !"0".equals(System.getenv("TERRASSIC_BACKFACE_CULL"));
    /** Quads written since the last {@link #takeQuads} (for the benchmark; one add per quad). */
    private static long quads;

    /** Per model: the cubes prepared once, and which of them are opaque in each texture. */
    private final Map<BakedGeoModel, ModelPrep> preps = new IdentityHashMap<>();

    // state of the animal being drawn (render thread only)
    private ResourceLocation texture;
    private ModelPrep current;
    private boolean cull;
    private boolean eyeIsPoint;
    private final Vector4d eyeView = new Vector4d();
    private final Matrix4d viewInv = new Matrix4d();
    private final Matrix4d modelView = new Matrix4d();
    // scratch
    private final Matrix4f cubePose = new Matrix4f();
    private final Matrix3f cubeNormal = new Matrix3f();
    private final Matrix4f inverse = new Matrix4f();
    private final Vector3f normal = new Vector3f();
    private final Vector3f eyeLocal = new Vector3f();

    protected LeanGeoRenderer(EntityRendererProvider.Context context, GeoModel<T> model) {
        super(context, model);
    }

    public static void setLean(boolean on) {
        lean = on;
    }

    public static void setBackfaces(boolean on) {
        backfaces = on && !SHADERS;
    }

    public static boolean lean() {
        return lean;
    }

    public static boolean backfaces() {
        return backfaces;
    }

    public static long takeQuads() {
        long q = quads;
        quads = 0;
        return q;
    }

    /** Time spent inside {@link #render} of these renderers since the last call (for the benchmark). */
    private static long renderNanos;

    public static long takeRenderNanos() {
        long n = renderNanos;
        renderNanos = 0;
        return n;
    }

    @Override
    public void render(T entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        long t = System.nanoTime();
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
        renderNanos += System.nanoTime() - t;
    }

    @Override
    public void actuallyRender(PoseStack poseStack, T animatable, BakedGeoModel model, RenderType renderType, MultiBufferSource bufferSource,
                               VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay,
                               float red, float green, float blue, float alpha) {
        if (!isReRender) {
            this.texture = this.getTextureLocation(animatable);
            this.current = lean ? this.prep(model, animatable) : null;
            this.cull = lean && backfaces && alpha >= 1.0F && !animatable.isInvisible() && this.eye();
        }
        super.actuallyRender(poseStack, animatable, model, renderType, bufferSource, buffer, isReRender, partialTick, packedLight,
                packedOverlay, red, green, blue, alpha);
    }

    /** Where the eye is in the space the vertices are written in: the point (or, for an orthographic projection, the
     *  direction of sight) that the projection sends to (0, 0, 1, 0). */
    private boolean eye() {
        this.viewInv.set(RenderSystem.getProjectionMatrix()).mul(this.modelView.set(RenderSystem.getModelViewMatrix()));
        if (Math.abs(this.viewInv.determinant()) < 1.0E-30D) {
            return false;
        }
        this.viewInv.invert();
        this.eyeView.set(0.0D, 0.0D, 1.0D, 0.0D);
        this.viewInv.transform(this.eyeView);
        double len = Math.abs(this.eyeView.x) + Math.abs(this.eyeView.y) + Math.abs(this.eyeView.z);
        if (!Double.isFinite(len) || !Double.isFinite(this.eyeView.w)) {
            return false;
        }
        this.eyeIsPoint = Math.abs(this.eyeView.w) > 1.0E-9D * Math.max(len, 1.0E-30D);
        if (this.eyeIsPoint) {
            this.eyeView.div(this.eyeView.w);
        } else if (len < 1.0E-30D) {
            return false;
        }
        return true;
    }

    @Override
    public void renderRecursively(PoseStack poseStack, T animatable, GeoBone bone, RenderType renderType, MultiBufferSource bufferSource,
                                  VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay,
                                  float red, float green, float blue, float alpha) {
        if (lean && bone.isHidden() && bone.isHidingChildren() && !bone.isTrackingMatrices()) {
            return;    // nothing of it or under it is drawn (GeckoLib would still walk it and turn the stack)
        }
        super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender, partialTick, packedLight,
                packedOverlay, red, green, blue, alpha);
    }

    @Override
    public void renderCubesOfBone(PoseStack poseStack, GeoBone bone, VertexConsumer buffer, int packedLight, int packedOverlay,
                                  float red, float green, float blue, float alpha) {
        if (!lean || this.current == null) {
            super.renderCubesOfBone(poseStack, bone, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            return;
        }
        if (bone.isHidden()) {
            return;
        }
        PoseStack.Pose last = poseStack.last();
        boolean haveEye = false;
        float ex = 0, ey = 0, ez = 0;
        for (GeoCube cube : bone.getCubes()) {
            CubePrep p = this.current.cube(cube);
            if (p.local == null) {
                if (this.cull && p.closed && !haveEye) {
                    this.eyeIn(last.pose());
                    ex = this.eyeLocal.x;
                    ey = this.eyeLocal.y;
                    ez = this.eyeLocal.z;
                    haveEye = true;
                }
                this.eyeLocal.set(ex, ey, ez);
                this.draw(p, last.pose(), last.normal(), buffer, packedLight, packedOverlay, red, green, blue, alpha);
            } else {
                this.drawRotated(p, last, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
        }
    }

    /** One cube on its own (a subclass that filters the cubes of a bone calls this with the stack pushed). */
    @Override
    public void renderCube(PoseStack poseStack, GeoCube cube, VertexConsumer buffer, int packedLight, int packedOverlay,
                           float red, float green, float blue, float alpha) {
        if (!lean || this.current == null) {
            super.renderCube(poseStack, cube, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            return;
        }
        CubePrep p = this.current.cube(cube);
        PoseStack.Pose last = poseStack.last();
        if (p.local == null) {
            if (this.cull && p.closed) {
                this.eyeIn(last.pose());
            }
            this.draw(p, last.pose(), last.normal(), buffer, packedLight, packedOverlay, red, green, blue, alpha);
        } else {
            this.drawRotated(p, last, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        }
    }

    private void drawRotated(CubePrep p, PoseStack.Pose last, VertexConsumer buffer, int packedLight, int packedOverlay,
                             float red, float green, float blue, float alpha) {
        Matrix4f pose = this.cubePose.set(last.pose()).mul(p.local);
        Matrix3f nrm = this.cubeNormal.set(last.normal()).mul(p.localNormal);
        if (this.cull && p.closed) {
            this.eyeIn(pose);
        }
        this.draw(p, pose, nrm, buffer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    /** The eye in the space of the given matrix (into eyeLocal: a point, or the direction of sight). */
    private void eyeIn(Matrix4f pose) {
        Matrix4f inv = this.inverse.set(pose).invertAffine();
        if (this.eyeIsPoint) {
            inv.transformPosition((float) this.eyeView.x, (float) this.eyeView.y, (float) this.eyeView.z, this.eyeLocal);
        } else {
            inv.transformDirection((float) this.eyeView.x, (float) this.eyeView.y, (float) this.eyeView.z, this.eyeLocal);
        }
    }

    private void draw(CubePrep p, Matrix4f pose, Matrix3f nrm, VertexConsumer buffer, int packedLight, int packedOverlay,
                      float red, float green, float blue, float alpha) {
        boolean cull = this.cull && p.closed && this.current.opaque(this.texture, p);
        float m00 = pose.m00(), m01 = pose.m01(), m02 = pose.m02();
        float m10 = pose.m10(), m11 = pose.m11(), m12 = pose.m12();
        float m20 = pose.m20(), m21 = pose.m21(), m22 = pose.m22();
        float m30 = pose.m30(), m31 = pose.m31(), m32 = pose.m32();
        GeoQuad[] qs = p.quads;
        for (int i = 0; i < qs.length; i++) {
            if (cull) {
                int a = p.axis[i];
                float e = a == 0 ? this.eyeLocal.x : a == 1 ? this.eyeLocal.y : this.eyeLocal.z;
                boolean front = this.eyeIsPoint ? (p.positive[i] ? e > p.plane[i] : e < p.plane[i])
                        : (p.positive[i] ? e < 0.0F : e > 0.0F);
                if (!front) {
                    continue;
                }
            }
            GeoQuad quad = qs[i];
            Vector3f n = nrm.transform(this.normal.set(quad.normal()));
            if (p.flat) {
                fixInvertedFlat(p.size, n);
            }
            quads++;
            for (GeoVertex vertex : quad.vertices()) {
                Vector3f v = vertex.position();
                float x = v.x(), y = v.y(), z = v.z();
                buffer.vertex(m00 * x + m10 * y + m20 * z + m30, m01 * x + m11 * y + m21 * z + m31, m02 * x + m12 * y + m22 * z + m32,
                        red, green, blue, alpha, vertex.texU(), vertex.texV(), packedOverlay, packedLight, n.x(), n.y(), n.z());
            }
        }
    }

    /** RenderUtils#fixInvertedFlatCube, without its allocation. */
    private static void fixInvertedFlat(Vec3 size, Vector3f n) {
        if (n.x() < 0 && (size.y == 0 || size.z == 0)) {
            n.mul(-1, 1, 1);
        }
        if (n.y() < 0 && (size.x == 0 || size.z == 0)) {
            n.mul(1, -1, 1);
        }
        if (n.z() < 0 && (size.x == 0 || size.y == 0)) {
            n.mul(1, 1, -1);
        }
    }

    @Override
    public void createVerticesOfQuad(GeoQuad quad, Matrix4f poseState, Vector3f normal, VertexConsumer buffer, int packedLight,
                                     int packedOverlay, float red, float green, float blue, float alpha) {
        quads++;
        super.createVerticesOfQuad(quad, poseState, normal, buffer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    private ModelPrep prep(BakedGeoModel model, T animatable) {
        ModelPrep m = this.preps.get(model);
        if (m == null) {
            if (this.preps.size() > 96) {
                this.preps.clear();    // a resource reload baked new models; the old ones are gone
            }
            m = new ModelPrep(model, this.getGeoModel().getModelResource(animatable));
            this.preps.put(model, m);
        }
        return m;
    }

    /** One cube, worked out once: its drawn quads, the plane of each, and its own turn as a matrix. */
    private static final class CubePrep {
        final int index;
        final GeoQuad[] quads;
        final int[] axis;
        final float[] plane;
        final boolean[] positive;
        final Matrix4f local;
        final Matrix3f localNormal;
        final boolean closed;
        final boolean flat;
        final Vec3 size;

        CubePrep(int index, GeoCube cube, boolean wasWhole) {
            this.index = index;
            this.size = cube.size();
            List<GeoQuad> list = new ArrayList<>(6);
            for (GeoQuad q : cube.quads()) {
                if (q != null) {
                    list.add(q);
                }
            }
            this.quads = list.toArray(new GeoQuad[0]);
            this.axis = new int[this.quads.length];
            this.plane = new float[this.quads.length];
            this.positive = new boolean[this.quads.length];
            for (int i = 0; i < this.quads.length; i++) {
                Direction d = this.quads[i].direction();
                int a = d.getAxis().ordinal();
                this.axis[i] = a;
                this.positive[i] = d.getAxisDirection() == Direction.AxisDirection.POSITIVE;
                Vector3f v0 = this.quads[i].vertices()[0].position();
                this.plane[i] = a == 0 ? v0.x() : a == 1 ? v0.y() : v0.z();
            }
            this.flat = this.size.x == 0 || this.size.y == 0 || this.size.z == 0;
            // a box: six faces, or fewer only where tools/modelgen/geo_cull.py took out faces inside the model (a cube
            // left open by design, a shell, shows its inside through the gap and keeps its back faces)
            this.closed = !this.flat && !cube.mirror() && cube.inflate() >= 0 && (this.quads.length == 6 || wasWhole)
                    && planesHold(this);
            Vec3 r = cube.rotation();
            if (r.x != 0 || r.y != 0 || r.z != 0) {
                Vec3 pv = cube.pivot();
                // RenderUtils#translateToPivotPoint, #rotateMatrixAroundCube, #translateAwayFromPivotPoint
                this.local = new Matrix4f().translate((float) (pv.x / 16f), (float) (pv.y / 16f), (float) (pv.z / 16f))
                        .rotate(new Quaternionf().rotationXYZ(0, 0, (float) r.z))
                        .rotate(new Quaternionf().rotationXYZ(0, (float) r.y, 0))
                        .rotate(new Quaternionf().rotationXYZ((float) r.x, 0, 0))
                        .translate((float) (-pv.x / 16f), (float) (-pv.y / 16f), (float) (-pv.z / 16f));
                this.localNormal = new Matrix3f().rotate(new Quaternionf().rotationXYZ(0, 0, (float) r.z))
                        .rotate(new Quaternionf().rotationXYZ(0, (float) r.y, 0))
                        .rotate(new Quaternionf().rotationXYZ((float) r.x, 0, 0));
            } else {
                this.local = null;
                this.localNormal = null;
            }
        }

        /** Each quad really lies on its plane, on the side its direction says (a box built the usual way). */
        private static boolean planesHold(CubePrep p) {
            float[] lo = {Float.MAX_VALUE, Float.MAX_VALUE, Float.MAX_VALUE};
            float[] hi = {-Float.MAX_VALUE, -Float.MAX_VALUE, -Float.MAX_VALUE};
            for (GeoQuad q : p.quads) {
                for (GeoVertex v : q.vertices()) {
                    float[] c = {v.position().x(), v.position().y(), v.position().z()};
                    for (int k = 0; k < 3; k++) {
                        lo[k] = Math.min(lo[k], c[k]);
                        hi[k] = Math.max(hi[k], c[k]);
                    }
                }
            }
            for (int i = 0; i < p.quads.length; i++) {
                int a = p.axis[i];
                for (GeoVertex v : p.quads[i].vertices()) {
                    float c = a == 0 ? v.position().x() : a == 1 ? v.position().y() : v.position().z();
                    if (c != p.plane[i]) {
                        return false;
                    }
                }
                // with fewer than six faces the other side may be missing; the side is still told by the direction
                float other = p.positive[i] ? lo[a] : hi[a];
                if (p.quads.length == 6 && (p.positive[i] ? p.plane[i] <= other : p.plane[i] >= other)) {
                    return false;
                }
            }
            return true;
        }
    }

    private static final class ModelPrep {
        private final Map<GeoCube, CubePrep> cubes = new IdentityHashMap<>();
        private final Map<ResourceLocation, boolean[]> opaque = new HashMap<>();

        /** bone -> cube index -> faces left, for the cubes geo_cull took hidden faces out of (assets/&lt;ns&gt;/geo_cull/&lt;id&gt;.json). */
        private final Map<String, Map<Integer, Integer>> whole;

        ModelPrep(BakedGeoModel model, ResourceLocation geo) {
            this.whole = readWhole(geo);
            for (GeoBone b : model.topLevelBones()) {
                this.add(b);
            }
        }

        /** The record geo_cull.py left beside the model, if it was made for this very geo.json (same SHA-1). */
        private static Map<String, Map<Integer, Integer>> readWhole(ResourceLocation geo) {
            Map<String, Map<Integer, Integer>> out = new HashMap<>();
            String path = geo == null ? "" : geo.getPath();
            if (!path.startsWith("geo/") || !path.endsWith(".geo.json")) {
                return out;
            }
            String id = path.substring(path.lastIndexOf('/') + 1, path.length() - ".geo.json".length());
            var manager = Minecraft.getInstance().getResourceManager();
            Optional<Resource> side = manager.getResource(new ResourceLocation(geo.getNamespace(), "geo_cull/" + id + ".json"));
            Optional<Resource> model = manager.getResource(geo);
            if (side.isEmpty() || model.isEmpty()) {
                return out;
            }
            try (InputStream in = model.get().open(); java.io.Reader reader = side.get().openAsReader()) {
                byte[] digest = java.security.MessageDigest.getInstance("SHA-1").digest(in.readAllBytes());
                StringBuilder hex = new StringBuilder();
                for (byte b : digest) {
                    hex.append(String.format(java.util.Locale.ROOT, "%02x", b));
                }
                com.google.gson.JsonObject json = com.google.gson.JsonParser.parseReader(reader).getAsJsonObject();
                if (!hex.toString().equals(json.get("geo_sha1").getAsString())) {
                    return out;    // the model was changed after the tool ran: trust only whole boxes
                }
                for (Map.Entry<String, com.google.gson.JsonElement> bone : json.getAsJsonObject("closed").entrySet()) {
                    Map<Integer, Integer> cubes = new HashMap<>();
                    for (Map.Entry<String, com.google.gson.JsonElement> c : bone.getValue().getAsJsonObject().entrySet()) {
                        cubes.put(Integer.parseInt(c.getKey()), c.getValue().getAsInt());
                    }
                    out.put(bone.getKey(), cubes);
                }
            } catch (Exception e) {
                out.clear();
            }
            return out;
        }

        private void add(GeoBone bone) {
            Map<Integer, Integer> listed = this.whole.getOrDefault(bone.getName(), Map.of());
            int i = 0;
            for (GeoCube c : bone.getCubes()) {
                int left = 0;
                for (GeoQuad q : c.quads()) {
                    left += q == null ? 0 : 1;
                }
                Integer n = listed.get(i++);
                this.cubes.put(c, new CubePrep(this.cubes.size(), c, n != null && n == left));
            }
            for (GeoBone child : bone.getChildBones()) {
                this.add(child);
            }
        }

        CubePrep cube(GeoCube cube) {
            CubePrep p = this.cubes.get(cube);
            if (p == null) {
                p = new CubePrep(this.cubes.size(), cube, false);
                this.cubes.put(cube, p);
            }
            return p;
        }

        boolean opaque(ResourceLocation texture, CubePrep p) {
            if (texture == null) {
                return false;
            }
            boolean[] flags = this.opaque.get(texture);
            if (flags == null || flags.length < this.cubes.size()) {
                flags = this.measure(texture);
                this.opaque.put(texture, flags);
            }
            return p.index < flags.length && flags[p.index];
        }

        /** Every texel of every drawn face of each cube fully opaque in this texture (read once from the resource). */
        private boolean[] measure(ResourceLocation texture) {
            boolean[] out = new boolean[this.cubes.size()];
            Optional<Resource> res = Minecraft.getInstance().getResourceManager().getResource(texture);
            if (res.isEmpty()) {
                return out;
            }
            try (InputStream in = res.get().open(); NativeImage img = NativeImage.read(in)) {
                int w = img.getWidth();
                int h = img.getHeight();
                for (CubePrep p : this.cubes.values()) {
                    boolean all = p.quads.length > 0;
                    for (GeoQuad q : p.quads) {
                        float u0 = Float.MAX_VALUE, u1 = -Float.MAX_VALUE, v0 = Float.MAX_VALUE, v1 = -Float.MAX_VALUE;
                        for (GeoVertex v : q.vertices()) {
                            u0 = Math.min(u0, v.texU());
                            u1 = Math.max(u1, v.texU());
                            v0 = Math.min(v0, v.texV());
                            v1 = Math.max(v1, v.texV());
                        }
                        int x0 = (int) Math.floor(u0 * w + 1.0E-3F), x1 = (int) Math.ceil(u1 * w - 1.0E-3F);
                        int y0 = (int) Math.floor(v0 * h + 1.0E-3F), y1 = (int) Math.ceil(v1 * h - 1.0E-3F);
                        if (x0 < 0 || y0 < 0 || x1 > w || y1 > h || x1 <= x0 || y1 <= y0) {
                            all = false;
                            break;
                        }
                        for (int y = y0; y < y1 && all; y++) {
                            for (int x = x0; x < x1; x++) {
                                if ((img.getPixelRGBA(x, y) >>> 24) != 0xFF) {
                                    all = false;
                                    break;
                                }
                            }
                        }
                        if (!all) {
                            break;
                        }
                    }
                    out[p.index] = all;
                }
            } catch (Exception e) {
                return new boolean[this.cubes.size()];
            }
            return out;
        }
    }
}
