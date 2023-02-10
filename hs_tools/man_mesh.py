import bpy
import bmesh


class manifold_mesh(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.manifold_mesh"
    bl_label = "Manifold Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.mode == 'EDIT'

    def is_manifold(self, bm):
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        i = 0
        for v in bm.verts:
            if v.select:
                i += 1
        return i

    def execute(self, context):
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.select_all(action='DESELECT')


        bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
        bpy.ops.mesh.select_non_manifold()

        sel = [v for v in bm.verts if v.select and len(v.link_edges) == 3]
        bpy.ops.mesh.select_all(action='DESELECT')


        n = 0
        while (self.is_manifold(bm) > 0):
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            sel = [v for v in bm.verts if v.select and len(v.link_edges) == 3]
            if len(sel) == 0:
                break
            bpy.ops.mesh.select_all(action='DESELECT')
            sel[0].select = True
            bpy.ops.edit.manifold_edge()
            n+=1





        return {'FINISHED'}

def register():
    bpy.utils.register_class(manifold_mesh)
def unregister():
    bpy.utils.unregister_class(manifold_mesh)

if __name__ == "__main__":
    register()
