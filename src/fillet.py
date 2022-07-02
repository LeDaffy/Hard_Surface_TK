import bpy
import bmesh



class mesh_fillet(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.mesh_fillet"
    bl_label = "Fillet"
    bl_options = {'REGISTER', 'UNDO'}

    width: bpy.props.FloatProperty(name="Width", default=0.0, min=0.0)
    loop_slide_0: bpy.props.BoolProperty(name="Loop Slide 1", default=False)
    loop_slide_1: bpy.props.BoolProperty(name="Loop Slide 2", default=False)
    flip_0: bpy.props.BoolProperty(name="Flip 1", default=False)
    flip_1: bpy.props.BoolProperty(name="Flip 2", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'

    def execute(self, context):
        # add the selection to a vertex group
        vertex_group_names = ["vg_original_selection"]
        object_names = ["o_original_mesh"]
        bpy.ops.object.vertex_group_add()
        context.active_object.vertex_groups[-1].name = vertex_group_names[0]

        # create a backup mesh, with a copy of the current mesh
        og_mesh_backup = bpy.data.objects.new(object_names[0], bpy.context.active_object.data.copy())
        bpy.context.view_layer.active_layer_collection.collection.objects.link(og_mesh_backup)

        # create bmesh
        bm = bmesh.from_edit_mesh(context.active_object.data)

        # store original selection
        bm_edge_original_selection = [e for e in bm.edges if e.select]


        # select region
        bpy.ops.mesh.loop_to_region()
        # create selection group
        bm_faces_offset_0 = [f for f in bm.faces if f.select]
        # outset
        bm_faces_gen_0 = bmesh.ops.inset_region(bm, \
                faces=bm_faces_offset_0, \
                use_boundary=False,\
                use_even_offset=True,\
                use_interpolate=True,\
                use_relative_offset=False,\
                use_edge_rail=self.loop_slide_0,\
                thickness=self.width,\
                depth=0.0,\
                use_outset=self.flip_0)
        bpy.ops.mesh.select_all(action='DESELECT')
        bm_faces_gen_1 = bmesh.ops.inset_region(bm, \
                faces=bm_faces_offset_0, \
                use_boundary=False,\
                use_even_offset=True,\
                use_interpolate=True,\
                use_relative_offset=False,\
                use_edge_rail=self.loop_slide_1,\
                thickness=self.width,\
                depth=0.0,\
                use_outset=self.flip_1)
        bpy.ops.mesh.select_all(action='DESELECT')











        # update bmesh
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)

        # cleanup
        bpy.data.objects.remove(bpy.data.objects[object_names[0]])
        context.active_object.vertex_groups.remove(context.active_object.vertex_groups[vertex_group_names[0]])
        return {'FINISHED'}


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access)
def register():
    bpy.utils.register_class(mesh_fillet)
def unregister():
    bpy.utils.unregister_class(mesh_fillet)
if __name__ == "__main__":
    register()
