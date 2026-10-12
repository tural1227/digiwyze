import bpy
import mathutils
import math
import os
import sys

print("=== STARTING OPTIMIZED MARNEULI GLB GENERATION ===")
bpy.ops.wm.read_factory_settings(use_empty=True)

obj_file = r"C:\Users\lenovo\Downloads\tikinti\wetransfer_marneuli-residental-complex_phase-1-obj_2026-10-12_0739\MARNEULI RESIDENTAL COMPLEX_PHASE 1.obj"
output_glb = r"c:\Users\lenovo\Downloads\ev\ev\marneuli_building.glb"

print("1. Importing OBJ with up_axis='Z', forward_axis='NEGATIVE_Y'...")
bpy.ops.wm.obj_import(
    filepath=obj_file,
    forward_axis='NEGATIVE_Y',
    up_axis='Z',
    use_split_objects=False,
    use_split_groups=False,
    global_scale=0.001
)

imported_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if not imported_objs:
    raise Exception("No mesh imported!")

main_obj = imported_objs[0]
main_obj.name = "Marneuli_Complex"
bpy.context.view_layer.objects.active = main_obj
main_obj.select_set(True)

print(f"2. Raw imported vertices: {len(main_obj.data.vertices)}")
print("   Dimensions:", main_obj.dimensions)

# In the raw OBJ, Z is the elevation height (45.95m).
# Align rotation so the main facade faces directly forward along the X-axis
print("3. Aligning facade angle (-33 deg)...")
main_obj.rotation_euler.z = math.radians(-33.0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Center horizontal X and Y at (0, 0), and place bottom base at Z = 0
bbox = [main_obj.matrix_world @ mathutils.Vector(corner) for corner in main_obj.bound_box]
min_x = min(v.x for v in bbox)
max_x = max(v.x for v in bbox)
min_y = min(v.y for v in bbox)
max_y = max(v.y for v in bbox)
min_z = min(v.z for v in bbox)
max_z = max(v.z for v in bbox)

print(f"   Bounds: X=[{min_x:.1f}, {max_x:.1f}] Y=[{min_y:.1f}, {max_y:.1f}] Z=[{min_z:.1f}, {max_z:.1f}]")
print(f"   Dimensions: W={max_x - min_x:.1f}m, D={max_y - min_y:.1f}m, H={max_z - min_z:.1f}m")

main_obj.location.x = -(min_x + max_x) / 2.0
main_obj.location.y = -(min_y + max_y) / 2.0
main_obj.location.z = -min_z
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 4. Decimate / Optimize polygon count for instant WebGL loading
print("4. Optimizing mesh with Decimate modifier (ratio 0.07)...")
mod = main_obj.modifiers.new(name="Decimate", type='DECIMATE')
mod.ratio = 0.07  # ~320k triangles, lightweight & super fast in WebGL
bpy.ops.object.modifier_apply(modifier="Decimate")
print(f"   Optimized vertex count: {len(main_obj.data.vertices)}")

# 5. PBR Architectural Materials
print("5. Setting up PBR architectural materials...")
for mat in main_obj.data.materials:
    if not mat:
        continue
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    if not bsdf:
        continue
    
    mat_name = mat.name.lower()
    if 'glass' in mat_name:
        bsdf.inputs['Base Color'].default_value = (0.60, 0.78, 0.92, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['Metallic'].default_value = 0.85
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.75
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.75
    elif 'alumin' in mat_name or 'black' in mat_name:
        bsdf.inputs['Base Color'].default_value = (0.16, 0.16, 0.18, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.35
        bsdf.inputs['Metallic'].default_value = 0.65
    elif 'steel' in mat_name or 'metal' in mat_name or 'galvan' in mat_name:
        bsdf.inputs['Base Color'].default_value = (0.75, 0.76, 0.78, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.25
        bsdf.inputs['Metallic'].default_value = 0.80
    elif 'cmu' in mat_name or 'plaster' in mat_name or 'wall' in mat_name:
        bsdf.inputs['Base Color'].default_value = (0.91, 0.90, 0.87, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.70
        bsdf.inputs['Metallic'].default_value = 0.05
    elif 'concrete' in mat_name:
        bsdf.inputs['Base Color'].default_value = (0.78, 0.77, 0.75, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.80
        bsdf.inputs['Metallic'].default_value = 0.05
    else:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.84, 0.82, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.65
        bsdf.inputs['Metallic'].default_value = 0.10

print("6. Exporting optimized GLB (standard compression, fast loading)...")
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    use_selection=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_materials='EXPORT',
    export_apply=True
)

file_size_mb = os.path.getsize(output_glb) / (1024 * 1024)
print(f"=== COMPLETED! Exported size: {file_size_mb:.2f} MB ===")
