import bpy
import bmesh



class mesh_fillet(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.mesh_fillet"
    bl_label = "Fillet"
    bl_options = {'REGISTER', 'UNDO'}

    width: bpy.props.FloatProperty(name="Width", default=0.1, min=0.0)
    solidify: bpy.props.FloatProperty(name="Solidify", default=0.1, min=0.0)
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

        # duplicate fillet piece, add to new group, and hide
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_faces_bounds:
            f.select = True
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)
        bpy.ops.object.vertex_group_assign_new()
        context.active_object.vertex_groups[-1].name = vg_names[0]
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[0]].index
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.duplicate()
        fillet_object = [f for f in bm.faces if f.select]
        fillet_object_verts = [f for f in bm.verts if f.select]
        bmesh.ops.translate(bm, verts=fillet_object_verts, vec=(2, 2, 2))
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in fillet_object:
            f.hide_set(True)
            f.select=True
            
        # update the mesh and extrude the region along normals
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_faces_bounds:
            f.select = True
        # FIXME: need to save this extrude to a specific selection
        bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_shrink_fatten={"value":self.solidify, "use_even_offset":False, "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "release_confirm":False, "use_accurate":False})
        bpy.ops.mesh.select_linked(delimit=set())
        bm_cutter = [f for f in bm.faces if f.select]
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_faces_bounds:
            f.select = True
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)
        bpy.ops.transform.shrink_fatten(value=self.solidify/2, use_even_offset=False)
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_cutter:
            f.select = True

        # assign the new thing to a vertex group
        bpy.ops.object.vertex_group_assign_new()
        context.active_object.vertex_groups[-1].name = vg_names[1]


    

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        # for f in fillet_object:
            # f.hide_set(True)

        ## select the cutter
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in bm_cutter:
            f.select = True
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)
        # split on intersection
        bpy.ops.mesh.intersect(mode='SELECT_UNSELECT', separate_mode='ALL', solver='EXACT')
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[1]].index
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.delete(type='FACE')

        # select fillet piece
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[0]].index
        bpy.ops.object.vertex_group_select()

        # update bmesh
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)


        # cleanup
        bpy.data.objects.remove(bpy.data.objects[object_names[0]])
        bm.free()
        return {'FINISHED'}


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access)
def register():
    bpy.utils.register_class(mesh_fillet)
def unregister():
    bpy.utils.unregister_class(mesh_fillet)
if __name__ == "__main__":
    register()
