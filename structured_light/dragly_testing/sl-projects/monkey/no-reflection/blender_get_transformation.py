import bpy
from mathutils import *
import math

def quat_transl_to_transf(quat, transl):
    rot_mat_4x4 = quat.to_matrix().to_4x4()
    transl_mat_4x4 = Matrix.Translation(transl)
    transf_mat = transl_mat_4x4 @ rot_mat_4x4
    return transf_mat

projector = bpy.data.objects['Light']
box = bpy.data.objects['ZividCamera']

quat_world_box = box.rotation_quaternion
print("Rig quaternion")
print(quat_world_box)

transl_world_box = box.location
transf_world_box = quat_transl_to_transf(quat_world_box, transl_world_box)
print("Transformation matrix world to camera rig")
print(transf_world_box)

quat_box_proj = projector.rotation_quaternion
transl_box_proj = projector.location
transf_box_proj = quat_transl_to_transf(quat_box_proj, transl_box_proj)
print("Transformation matrix rig to projector")
print(transf_box_proj)



transf_world_proj = transf_world_box@transf_box_proj


rot_proj_myproj = Matrix.Rotation(math.radians(180.0), 4, 'Z')

transf_world_myproj = transf_world_proj@rot_proj_myproj
print("Transformation matrix world to projector (TPK4171 Convention axis)")
print(transf_world_myproj)

file1 = open("transf-mat-world-to-proj.csv", "w")

for rows in transf_world_myproj:
    for cols in rows:
        file1.write(str(cols) + ",")
    file1.write("\n")

file1.close() 

