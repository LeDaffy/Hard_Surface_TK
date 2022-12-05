import bpy
import bmesh



class fillet_gen(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.fillet_gen"
    bl_label = "Generate Fillet"
    bl_options = {'REGISTER', 'UNDO'}


    width: bpy.props.FloatProperty(name="Width", default=0.1, min=0.0)
    loop_slide_0: bpy.props.BoolProperty(name="Loop Slide 1", default=False)
    loop_slide_1: bpy.props.BoolProperty(name="Loop Slide 2", default=False)
    flip_0: bpy.props.BoolProperty(name="Flip 1", default=True)
    flip_1: bpy.props.BoolProperty(name="Flip 2", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.mode == 'EDIT'

    def outset(self, context, bm, conform_mesh):
        edges_original_edge_selection = [e for e in bm.edges if e.select]
        # select region to loop to prepare for outsetting
        bpy.ops.mesh.loop_to_region()
        # create selection group
        bm_faces_offset_0 = [f for f in bm.faces if f.select]
        # outset
        bm_face_gen_0 = bmesh.ops.inset_region(bm, \
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
        # select original loop and repeat
        for e in edges_original_edge_selection:
            e.select = True
        bm_face_gen_1 = bmesh.ops.inset_region(bm, \
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

        # select the generated faces
        for f in bm_face_gen_0['faces']:
            f.select = True
        for f in bm_face_gen_1['faces']:
            f.select = True

        # conform verts to original mesh
        bm_gen_verts = [v for v in bm.verts if v.select]
        bpy.ops.mesh.select_all(action='DESELECT')
        for v in bm_gen_verts:
            result, coor, normal, index = conform_mesh.closest_point_on_mesh(v.co)
            v.co = coor
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_face_gen_0['faces']:
            f.select = True
        for f in bm_face_gen_1['faces']:
            f.select = True
        bm.select_flush(True)

        return_faces = [f for f in bm.faces if f.select]
        return return_faces


    def execute(self, context):
        object_names = ["o_original_mesh"]
        vg_names = ["hstk_both", "hstk_rm_only"]

        # create a backup mesh, with a copy of the current mesh
        og_mesh_backup = bpy.data.objects.new(object_names[0],
                                              bpy.context.active_object.data.copy())
        bpy.context.view_layer.active_layer_collection \
            .collection.objects.link(og_mesh_backup)

        
        # create bmesh
        bm = bmesh.from_edit_mesh(context.active_object.data)

        # store original selection
        edges_original_edge_selection = [e for e in bm.edges if e.select]

        # duplicate the mesh, hide it
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.duplicate()
        faces_unaltered_mesh = [f for f in bm.faces if f.select]
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in faces_unaltered_mesh:
            f.hide_set(True)
            f.select = False

        # now that the original mesh is hidden restore the original selection
        # state
        for e in edges_original_edge_selection:
            e.select = True


        # assign the new faces to variable
        bm_faces_bounds = self.outset(context=context, bm=bm, 
                conform_mesh=bpy.data.objects[object_names[0]])
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)

        # invert selection and delete the unneeded faces
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_faces_bounds:
            f.select = True
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='INVERT')
        bm_faces_to_delete = [f for f in bm.faces if f.select]
        bmesh.ops.delete(bm, geom=bm_faces_to_delete, context='FACES')

        for f in bm.faces:
            f.hide = False
        bpy.ops.mesh.reveal()

        bpy.ops.mesh.select_mode(type='VERT')

        verts_fillet_outer = [v for v in bm.verts if v.select]
        edges_fillet_outer = [e for e in bm.edges if e.select]

        bpy.ops.mesh.select_all(action='DESELECT')
        for v in verts_fillet_outer:
            v.select=True

        bpy.ops.mesh.select_linked(delimit=set())
        verts_fillet = [v for v in bm.verts if v.select]
        edges_fillet = [e for e in bm.edges if e.select]


        verts_fillet_inner = [v for v in verts_fillet if v not in verts_fillet_outer]
        bpy.ops.mesh.select_all(action='DESELECT')
        for v in verts_fillet_inner:
            v.select=True
        edges_fillet_inner = [e for e in bm.edges if e.select]

        
        #bpy.ops.mesh.select_mode(type='VERT')
        #bm.select_flush(True)

        ## Create outer and inner edge group
        #verts_fillet_outer = [v for v in bm.verts if v.select]
        #bpy.ops.mesh.select_all(action='DESELECT')
        #for f in bm.faces:
        #    f.select = False
        #for e in bm.edges:
        #    e.select = False
        #verts_fillet_outer[0].select=True
        #bpy.ops.mesh.select_linked(delimit=set())
        #for v in verts_fillet_outer:
        #    v.select=False

        # cleanup
        bm.select_flush(True)
        bpy.data.objects.remove(bpy.data.objects[object_names[0]])
        bm.free()
        return {'FINISHED'}
def register():
    bpy.utils.register_class(fillet_gen)
def unregister():
    bpy.utils.unregister_class(fillet_gen)
if __name__ == "__main__":
    register()
