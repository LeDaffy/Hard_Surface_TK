import bpy
import math
import mathutils
import bmesh


class mesh_outset(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.mesh_outset"
    bl_label = "Mesh Outset"
    bl_options = {'REGISTER', 'UNDO'}
    
    inset_thickness: bpy.props.FloatProperty(name="Distance", min=0.0)
    inset_flip: bpy.props.BoolProperty(name="Flip", default=False)
    inset_rail: bpy.props.BoolProperty(name="Edge Rail", default=False)
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'

    def execute(self, context):
        print("Hello World")

        # add the selection to a vertex group
        bpy.ops.object.vertex_group_add()
        context.active_object.vertex_groups[-1].name = "Original Selection"

        # create a backup mesh, with a copy of the current mesh
        og_mesh_backup = bpy.data.objects.new("Original Mesh", bpy.context.active_object.data.copy())
        bpy.context.view_layer.active_layer_collection.collection.objects.link(og_mesh_backup)


        # create bmesh
        bm = bmesh.from_edit_mesh(context.active_object.data)

        bm_original_selection = [e for e in bm.edges if e.select]

        # select region
        bpy.ops.mesh.loop_to_region()

        # create selection group
        bm_offset_faces = [f for f in bm.faces if f.select]

        bpy.ops.mesh.select_all(action='DESELECT')


        bm_gen_faces = bmesh.ops.inset_region(bm, \
                faces=bm_offset_faces, \
                use_boundary=False,\
                use_even_offset=True,\
                use_interpolate=True,\
                use_relative_offset=False,\
                use_edge_rail=self.inset_rail,\
                thickness=self.inset_thickness,\
                depth=0.0,\
                use_outset=self.inset_flip)

        for f in bm_gen_faces['faces']:
            f.select_set(True)

        bm.select_flush(True)
        bm_gen_verts = [v for v in bm.verts if v.select]
        
        for v in bm_gen_verts:
            result, coor, normal, index = bpy.data.objects['Original Mesh'].closest_point_on_mesh(v.co)
            v.co = coor


        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_gen_verts:
            f.select_set(True)
        #update bmesh
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)
        bpy.data.objects.remove(og_mesh_backup)
        return {'FINISHED'}




# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access)
def register():

    bpy.utils.register_class(mesh_outset)



def unregister():
    bpy.utils.unregister_class(mesh_outset)



if __name__ == "__main__":
    register()
