"""Render the isolated T. rex pilot as a real 3D diorama (Blender/Cycles).

Uses only Terrassic geometry, texture and logo. Reference composition only.
Run after preview_trex.py, using the existing render environment with bpy.
"""
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector
from PIL import Image

import trex_v1 as pilot
from pybench import Rig
from trex_v1 import evaluate as pose_at

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "art/pilotos/trex/v1"
ASSETS = ROOT / "common/src/main/resources/assets/terrassic"


def material(name, color=None, texture=None):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nodes=mat.node_tree.nodes; shader=nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value=.86
    if texture:
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture));tex.interpolation='Closest'
        mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
        mat.node_tree.links.new(tex.outputs['Alpha'],shader.inputs['Alpha'])
    else:
        shader.inputs['Base Color'].default_value=(*color,1)
    return mat


def box(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location)
    obj=bpy.context.object;obj.name=name;obj.scale=scale;obj.data.materials.append(mat)
    return obj


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
    scene.render.resolution_x=1536;scene.render.resolution_y=1536;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world=bpy.data.worlds.new('Basalt studio');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.045,.054,.085,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    m=pilot.build();spec=m.spec();rig=Rig(spec)
    anim=next(a for a in m.animations if a['name'].endswith('.roar'))
    pose=pose_at(anim,.9)
    low=float(pilot.point_cloud(rig,pose)[:,1].min())
    verts=[];faces=[];uvs=[]
    W,H=Image.open(OUT/'tyrannosaurus_male.png').size
    for cube,face,corners,(u0,v0,u1,v1) in rig.cube_faces(pose,pilot.HIDE):
        order=((0,0),(1,0),(1,1),(0,1))
        start=len(verts)
        for s,t in order:
            p=corners[(s,t)][1]
            verts.append((float(p[0])/16,-float(p[2])/16,(float(p[1])-low)/16+.02))
            uvs.append(((u0+s*(u1-u0))/W,1-(v0+t*(v1-v0))/H))
        faces.append((start,start+1,start+2,start+3))
    mesh=bpy.data.meshes.new('Terrassic T rex pilot');mesh.from_pydata(verts,[],faces);mesh.update()
    layer=mesh.uv_layers.new(name='Terrassic UV')
    for poly in mesh.polygons:
        for li in poly.loop_indices:layer.data[li].uv=uvs[mesh.loops[li].vertex_index]
    obj=bpy.data.objects.new('Tyrannosaurus - original pilot',mesh);scene.collection.objects.link(obj)
    obj.data.materials.append(material('T rex pixel skin',texture=OUT/'tyrannosaurus_male.png'))
    # Every terrain cell is a complete unit cube on an integer grid.
    soil=material('Laterite',texture=ASSETS/'textures/block/laterite.png')
    litter=material('Fern litter',texture=ASSETS/'textures/block/fern_litter.png')
    stone=material('Limestone',texture=ASSETS/'textures/block/limestone_flagstone.png')
    rng=random.Random(271026)
    occupied=set()
    for x in range(-3,4):
        for y in range(-7,7):
            if (x/3.8)**2+(y/7.5)**2>1.05:continue
            occupied.add((x,y))
            depth=2+(abs(x)<2 and abs(y)<5)
            for z in range(-depth,0):
                mat=litter if z==-1 else (stone if z==-depth else soil)
                box('Voxel ground', (x+.5,y+.5,z+.5), (1,1,1),mat)
    bark=material('Araucaria bark',texture=ASSETS/'textures/block/araucaria_log.png')
    # A small fallen trunk is deliberately cuboid, not synthesized scenery.
    for i in range(4):box('Fallen trunk',(-2.4,1.8+i,-.0+.3),(.6,1,.6),bark)
    greens=[material('Fern '+str(i),color=c) for i,c in enumerate(((.12,.23,.10),(.18,.32,.12),(.27,.38,.15)))]
    for x,y in sorted(occupied):
        if abs(x)<1.5 or rng.random()>.24:continue
        # Blocky fern fronds, kept sparse so the animal remains the subject.
        for j in range(3):
            fern=box('Fern frond',(x+.5,y+.5,.15+j*.09),(.6-j*.12,.10,.09),greens[j])
            fern.rotation_euler[2]=(j-1)*.65
    floor=material('Basalt backdrop',color=(.016,.020,.038))
    box('Studio ground',(0,0,-3.15),(200,200,.1),floor)
    def light(name,loc,energy,col,size):
        data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=col;data.shape='DISK';data.size=size
        ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc
        ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
    light('Warm key',(2,7,14),2600,(1,.72,.41),7)
    light('Cool rim',(-7,-4,10),3400,(.26,.50,.73),6)
    light('Soft face fill',(9,10,5),1100,(1,.9,.71),6)
    camera=bpy.data.cameras.new('Diorama camera');ob=bpy.data.objects.new('Diorama camera',camera)
    scene.collection.objects.link(ob);ob.location=(14,19,10)
    target=Vector((0,.2,1.0));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    camera.type='ORTHO';camera.ortho_scale=17.8;scene.camera=ob
    scene.render.filepath=str(OUT/'trex_diorama_sem_logo.png')
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'trex_diorama.blend'))
    bpy.ops.render.render(write_still=True)
    # Exact shipped logo; avoid generative reinterpretation of lettering.
    image=Image.open(OUT/'trex_diorama_sem_logo.png').convert('RGBA')
    logo=Image.open(ASSETS/'textures/gui/title/menu/titulo.png').convert('RGBA');logo=logo.crop(logo.getbbox())
    logo.thumbnail((580,170),Image.Resampling.NEAREST)
    image.alpha_composite(logo,(68,58));image.convert('RGB').save(OUT/'trex_diorama.png')
    print(str(OUT/'trex_diorama.png'),flush=True)


if __name__=='__main__':main()
