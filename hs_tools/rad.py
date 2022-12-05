import bpy
import bmesh

class rad_set(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.set_radius"
    bl_label = "Radius Uniform"
    bl_options = {'REGISTER', 'UNDO'}


    radius: bpy.props.FloatProperty(name="Radius", default=0.1, min=0.0)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.mode == 'EDIT'

    def execute(self, context):
        # create bmesh
        bm = bmesh.from_edit_mesh(context.active_object.data)

        # store original selection
        edges_original_edge_selection = [e for e in bm.edges if e.select]
        verts_original_edge_selection = [v for v in bm.verts if v.select]

        for v in verts_original_edge_selection:
            print(v.link_edges)

         

        # cleanup
        bm.select_flush(True)
        bm.free()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(rad_set)
def unregister():
    bpy.utils.unregister_class(rad_set)
if __name__ == "__main__":
    register()
