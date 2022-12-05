"""
new idea
instead of merging and fixing holes, keep seperate to split into two sides.

"""
import math
import bpy
import bmesh



class make_manifold(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.make_manifold"
    bl_label = "Make Manifold"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.mode == 'EDIT'

    def select_next(self, vert, side):
        for e in vert.link_edges:
            if e in side:
                if e.verts[0].select == False or e.verts[1].select == False:
                    if e.verts[0] is vert:
                        e.verts[0].select = True
                        e.verts[1].select = True
                        # # print(f"original vert: {vert} \t vert[0]: {e.verts[0]} \t returning vert[1]: {e.verts[1]}")
                        return e.verts[1]
                    else:
                        e.verts[0].select = True
                        e.verts[1].select = True
                        # print(f"original vert: {vert} \t returning: vert[0]: {e.verts[0]} \t vert[1]: {e.verts[1]}")
                        return e.verts[0]
        return vert

    def execute(self, context):
        # create bmesh
        bm = bmesh.from_edit_mesh(context.active_object.data)


        # get selected (non-manifold) edges
        selected_edges = [e for e in bm.edges if e.select]
        selected_verts = [v for v in bm.verts if v.select]

        bpy.ops.mesh.select_all(action='DESELECT')
        selected_verts[0].select = True
        nextvert = self.select_next(selected_verts[0], selected_edges)
        for i in range(0, len(selected_verts)):
            nextvert = self.select_next(nextvert, selected_edges)
            # print(i)

        
        bm.select_flush(True)
        side_1_verts = [v for v in selected_verts if v.select]
        side_1_edges = [e for e in selected_edges if e.select]
        side_2_verts = [v for v in selected_verts if v.select == False]
        side_2_edges = [e for e in selected_edges if e.select == False]

        # split into two sides
        vg_names = ["hstk_side_1_verts", "hstk_side_2_verts"]
        bpy.ops.mesh.select_all(action='DESELECT')
        for v in side_1_verts:
            v.select = True
        bpy.ops.object.vertex_group_assign_new()
        context.active_object.vertex_groups[-1].name = vg_names[0]
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[0]].index
        bpy.ops.mesh.select_all(action='DESELECT')
        for v in side_2_verts:
            v.select = True
        bpy.ops.object.vertex_group_assign_new()
        context.active_object.vertex_groups[-1].name = vg_names[1]
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[1]].index
        #bpy.ops.object.vertex_group_select()

        #each side has a vertex group
        dissolve_group = []
        bpy.ops.mesh.select_all(action='DESELECT')
        for v2 in side_2_verts:
            if len(v2.link_edges) == 2:
                dissolve_group.append(v2)
                v2.select = True
        for v2 in side_1_verts:
            if len(v2.link_edges) == 2:
                dissolve_group.append(v2)
                v2.select = True


        bpy.ops.mesh.select_all(action='DESELECT')
        d = []
        for v in selected_verts:
            if v not in dissolve_group:
                d.append(v)
        for v in dissolve_group:
            valid = False
            for v2 in d:
                if (v.co - v2.co).magnitude < .0001:
                    valid = True
            if valid == False:
                v.select = True
        bm.select_flush(True)
        bpy.ops.mesh.dissolve_mode(use_verts=True)


        bpy.ops.mesh.select_all(action='DESELECT')
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[0]].index
        bpy.ops.object.vertex_group_select()
        bm.select_flush(True)
        side_1_verts = [v for v in bm.verts if v.select]
        side_1_edges = [e for e in bm.edges if e.select]
        bpy.ops.mesh.select_all(action='DESELECT')
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[1]].index
        bpy.ops.object.vertex_group_select()
        bm.select_flush(True)
        side_2_verts = [v for v in bm.verts if v.select]
        side_2_edges = [e for e in bm.edges if e.select]



        #sub divide closest edge
        sub_edges: bmesh.types.BMEdge = []
        merge_threshold = 0.001
        for v in side_1_verts:
            lowest_dist = -1.0
            for i, e in enumerate(side_2_edges):
                if (v.co - e.verts[0].co).magnitude > merge_threshold and (v.co - e.verts[1].co).magnitude > merge_threshold:
                    center = (e.verts[0].co + e.verts[1].co) / 2
                    dist = (v.co - center).magnitude
                    if dist < lowest_dist or i == 0:
                        lowest_dist = dist
                        if e not in sub_edges:
                            sub_edges.append(e)
        geom = bmesh.ops.subdivide_edges(bm, edges=sub_edges, cuts=1)

        bpy.ops.mesh.select_all(action='DESELECT')
        context.active_object.vertex_groups.active_index = context.active_object.vertex_groups[vg_names[0]].index
        bpy.ops.object.vertex_group_select()
        bm.select_flush(True)
        slide_1_verts = [v for v in bm.verts if v.select]

        #
        for v in geom["geom_inner"]:
            if isinstance(v, bmesh.types.BMVert):
                lowest_dist = -1.0
                closest_vert: bmesh.types.BMVert
                for i, v2 in enumerate(slide_1_verts):
                    if (v.co - v2.co).magnitude < lowest_dist or i == 0:
                        lowest_dist = (v.co - v2.co).magnitude
                        closest_vert=v2
                v.co = closest_vert.co


        # bmesh.ops.subdivide_edges(bm, edges=side_1_edges, cuts=1)





        # cleanup
        # update bmesh
        bm.select_flush(True)
        bpy.context.active_object.vertex_groups.remove(bpy.context.active_object.vertex_groups[vg_names[0]])
        bpy.context.active_object.vertex_groups.remove(bpy.context.active_object.vertex_groups[vg_names[1]])
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)
        return {'FINISHED'}


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access)
def register():
    bpy.utils.register_class(make_manifold)
def unregister():
    bpy.utils.unregister_class(make_manifold)
if __name__ == "__main__":
    register()
