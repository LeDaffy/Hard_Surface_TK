import bpy
import bmesh
import mathutils
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# Get the object and its mesh
obj = bpy.context.object
mesh = obj.data


bm = bmesh.from_edit_mesh(bpy.context.active_object.data)


vg_names = ["og", "hstk_side_2_verts"]
# Search for a location
location = Vector( (-0.457528, -4.47243 , 0) )
for v in bm.verts:
    if v.select:
        location = v
        bpy.ops.object.vertex_group_assign_new()
        bpy.context.active_object.vertex_groups[-1].name = vg_names[0]
        break

bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_non_manifold()

sel = [e for e in bm.edges if e.select and e.verts[0] != location and e.verts[1] != location]
    
polygons = [(e.verts[0].index, e.verts[1].index, e.verts[0].index) for e in sel]
vertices = [(v.co.x, v.co.y, v.co.z) for v in bm.verts]
#
#print(vertices)
#print(polygons)
# Create a BVH Tree from it
tree = BVHTree.FromPolygons( vertices, polygons, all_triangles = True )



# Query the tree
found_location, normal, index, distance = tree.find_nearest( location.co )
bpy.ops.mesh.select_all(action='DESELECT')
bm.verts.ensure_lookup_table()
bm.verts[polygons[index][0]].select=True
bm.verts[polygons[index][1]].select=True
bm.select_flush(True)


sub_edges = [e for e in bm.edges if e.select]
geom = bmesh.ops.subdivide_edges(bm, edges=sub_edges, cuts=1)
#

bpy.ops.mesh.select_all(action='DESELECT')
bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups[vg_names[0]].index
bpy.ops.object.vertex_group_select()
location = [v for v in bm.verts if v.select]
for v in geom["geom_inner"]:
    if isinstance(v, bmesh.types.BMVert):
        v.co = location[0].co

bpy.context.active_object.vertex_groups.remove(bpy.context.active_object.vertex_groups[vg_names[0]])
bmesh.update_edit_mesh(bpy.context.active_object.data, loop_triangles=True, destructive=True)

bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles()
bpy.ops.mesh.select_all(action='DESELECT')


#print(found_location)

#print( index )
