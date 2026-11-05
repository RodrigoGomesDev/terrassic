package com.terrassic.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.TranqDart;
import com.terrassic.registry.ModEntities;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import org.joml.Vector3f;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.cache.object.GeoCube;
import software.bernie.geckolib.cache.object.GeoQuad;
import software.bernie.geckolib.cache.object.GeoVertex;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;
import software.bernie.geckolib.util.RenderUtil;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

/**
 * Darts and arrows stuck in a creature's hide (v1.1.4, docs/ARMAS.md), like the arrows a player carries after a
 * fight. The counts come from the entity: {@link DinosaurEntity#getStuckDarts()} and the vanilla arrow count. Each one
 * sits on the face of a real cube of the model, follows its bone through the animations and points into the body,
 * the fletching out. Where it sits is fixed by the creature's id, so it does not jump between frames. Only solid
 * cubes take one (not planes such as teeth, frills or feathers), weighted by their area, so the big body parts get most.
 */
public class StuckProjectilesLayer<T extends DinosaurEntity> extends GeoRenderLayer<T> {
    /** No more than this many of each are drawn, however many are in it. */
    private static final int MAX_DRAWN = 12;
    /** How much further in than the arrow renderer already puts the head (it draws the head about a quarter of a
     *  block ahead of the origin, the shaft and fletching behind it), in blocks. */
    private static final float DEPTH = 0.02F;

    /** Per model: every face, then the faces of the body, of the head and neck, and of the tail (1.7: a dart is drawn
     *  in the part it hit, DinosaurEntity#stuckDartZone). */
    private final Map<BakedGeoModel, Surface[]> surfaces = new WeakHashMap<>();
    private Arrow arrow;
    private TranqDart dart;

    public StuckProjectilesLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    @Override
    public void renderForBone(PoseStack poseStack, T animatable, GeoBone bone, RenderType renderType, MultiBufferSource bufferSource,
                              VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        int darts = Math.min(animatable.getStuckDarts(), MAX_DRAWN);
        int arrows = Math.min(animatable.getArrowCount(), MAX_DRAWN);
        if (darts + arrows == 0 || animatable.isInvisible() || bone.isHidden()) {
            return;
        }
        Surface[] zones = this.surfaces.computeIfAbsent(this.getDefaultBakedModel(animatable), Surface::zones);
        Surface all = zones[0];
        if (all.faces.isEmpty()) {
            return;
        }
        boolean parts = animatable.parts().length > 0;
        boolean drew = false;
        for (int i = 0; i < darts + arrows; i++) {
            RandomSource random = RandomSource.create(animatable.getId() * 341873128712L + i * 132897987541L);
            Surface surface = all;
            if (i < darts && parts) {
                Surface zone = zones[1 + animatable.stuckDartZone(i)];
                if (!zone.faces.isEmpty()) {
                    surface = zone;
                }
            }
            Face face = surface.pick(random.nextFloat());
            if (face.bone != bone) {
                continue;
            }
            AbstractArrow shown = i < darts ? this.dart(animatable.level()) : this.arrow(animatable.level());
            this.renderStuck(poseStack, animatable, face, random, shown, bufferSource, partialTick, packedLight);
            drew = true;
        }
        if (drew) {
            // back to the creature's own buffer, as GeoRenderLayer asks
            bufferSource.getBuffer(renderType);
        }
    }

    private void renderStuck(PoseStack poseStack, T animatable, Face face, RandomSource random, AbstractArrow shown,
                             MultiBufferSource bufferSource, float partialTick, int packedLight) {
        GeoVertex[] v = face.quad.vertices();
        float a = 0.15F + random.nextFloat() * 0.7F;
        float b = 0.15F + random.nextFloat() * 0.7F;
        // a point on the face (bilinear over its four corners), then a little way in along the face's normal
        Vector3f p0 = new Vector3f(v[0].position()).lerp(v[1].position(), a);
        Vector3f p1 = new Vector3f(v[3].position()).lerp(v[2].position(), a);
        Vector3f point = p0.lerp(p1, b);
        Vector3f in = new Vector3f(face.quad.normal()).negate();
        // not square to the hide: a dart comes in at an angle
        in.add((random.nextFloat() - 0.5F) * 0.9F, (random.nextFloat() - 0.5F) * 0.9F, (random.nextFloat() - 0.5F) * 0.9F)
                .normalize();
        poseStack.pushPose();
        RenderUtil.translateToPivotPoint(poseStack, face.cube);
        RenderUtil.rotateMatrixAroundCube(poseStack, face.cube);
        RenderUtil.translateAwayFromPivotPoint(poseStack, face.cube);
        poseStack.translate(point.x(), point.y(), point.z());
        // undo the creature's own size, so a dart is a dart's size on a hatchling and on a T. rex alike
        float scale = this.getRenderer() instanceof DinosaurRenderer<?> dinoRenderer ? dinoRenderer.renderScale(animatable) : 1.0F;
        if (scale > 0.01F) {
            poseStack.scale(1.0F / scale, 1.0F / scale, 1.0F / scale);
        }
        // pointing into the body: the head goes under the hide, the shaft and fletching stay out
        poseStack.translate(in.x() * DEPTH, in.y() * DEPTH, in.z() * DEPTH);
        float horizontal = Mth.sqrt(in.x() * in.x() + in.z() * in.z());
        shown.setYRot((float) (Mth.atan2(in.x(), in.z()) * Mth.RAD_TO_DEG));
        shown.setXRot((float) (Mth.atan2(in.y(), horizontal) * Mth.RAD_TO_DEG));
        shown.yRotO = shown.getYRot();
        shown.xRotO = shown.getXRot();
        EntityRenderer<? super AbstractArrow> renderer = Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(shown);
        renderer.render(shown, 0.0F, partialTick, poseStack, bufferSource, packedLight);
        poseStack.popPose();
    }

    private Arrow arrow(Level level) {
        if (this.arrow == null || this.arrow.level() != level) {
            this.arrow = new Arrow(level, 0.0D, 0.0D, 0.0D, new ItemStack(Items.ARROW), null);
        }
        return this.arrow;
    }

    private TranqDart dart(Level level) {
        if (this.dart == null || this.dart.level() != level) {
            this.dart = new TranqDart(ModEntities.TRANQ_DART.get(), level);
        }
        return this.dart;
    }

    /** One face of a solid cube, with the bone it moves with. */
    private record Face(GeoBone bone, GeoCube cube, GeoQuad quad, float area) {
    }

    /** Every face that can take a dart, and the running total of their areas for a weighted pick. */
    private record Surface(List<Face> faces, float[] cumulative) {
        /** All faces, then those of zone 0 (body), 1 (head and neck) and 2 (tail). */
        static Surface[] zones(BakedGeoModel model) {
            Surface[] out = new Surface[4];
            for (int z = -1; z < 3; z++) {
                out[z + 1] = of(model, z);
            }
            return out;
        }

        static Surface of(BakedGeoModel model, int zone) {
            List<Face> faces = new ArrayList<>();
            for (GeoBone bone : model.topLevelBones()) {
                collect(bone, faces, zone, 0);
            }
            float[] cumulative = new float[faces.size()];
            float total = 0.0F;
            for (int i = 0; i < faces.size(); i++) {
                total += faces.get(i).area();
                cumulative[i] = total;
            }
            return new Surface(faces, cumulative);
        }

        private static void collect(GeoBone bone, List<Face> faces, int zone, int inherited) {
            String name = bone.getName().toLowerCase(java.util.Locale.ROOT);
            int own = name.equals("head") || name.startsWith("neck") || name.equals("throat") ? 1
                    : name.startsWith("tail") ? 2 : inherited;
            // the saddle, the eyelids and the parts only one sex shows (male_display) never take one
            boolean skip = name.contains("saddle") || name.contains("display") || name.startsWith("lid")
                    || (zone >= 0 && own != zone);
            if (!skip) {
                for (GeoCube cube : bone.getCubes()) {
                    // a plane (teeth, frill membranes, feathers) has no inside to stick into
                    if (cube.quads() == null || Math.min(cube.size().x, Math.min(cube.size().y, cube.size().z)) < 1.0D) {
                        continue;
                    }
                    for (GeoQuad quad : cube.quads()) {
                        if (quad == null || quad.vertices().length < 4) {
                            continue;
                        }
                        Vector3f e1 = new Vector3f(quad.vertices()[1].position()).sub(quad.vertices()[0].position());
                        Vector3f e2 = new Vector3f(quad.vertices()[3].position()).sub(quad.vertices()[0].position());
                        float area = e1.cross(e2).length();
                        if (area > 1.0E-4F) {
                            faces.add(new Face(bone, cube, quad, area));
                        }
                    }
                }
            }
            for (GeoBone child : bone.getChildBones()) {
                collect(child, faces, zone, own);
            }
        }

        Face pick(float roll) {
            if (this.faces.isEmpty()) {
                return null;
            }
            float target = roll * this.cumulative[this.cumulative.length - 1];
            for (int i = 0; i < this.cumulative.length; i++) {
                if (target <= this.cumulative[i]) {
                    return this.faces.get(i);
                }
            }
            return this.faces.get(this.faces.size() - 1);
        }
    }
}
