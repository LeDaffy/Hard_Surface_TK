import bpy
import mathutils
import bmesh
import numpy as np
from scipy import interpolate


class SplineInterp(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "edit.mesh_interp"
    bl_label = "Interp"
    bl_options = {'REGISTER', 'UNDO'}


    samples: bpy.props.IntProperty(name="Samples", default=20, min=3)
    degree: bpy.props.IntProperty(name="Degree", default=3, min=0, max=5)
    smoothing: bpy.props.FloatProperty(name="Smoothing", default=0.0, min=0.0)
    cyclic: bpy.props.BoolProperty(name="Cyclic", default=True)
    curve_type : bpy.props.EnumProperty(
        items=[
            ('INTERPOLATE', 'Interpolate', "Interpolate B-Spline between verts", 1),
            ('BSPLINE', 'B-Spline', "Create a B-Spline from verts", 2)],
        name="Curve Type",
        description="Choose a type",
        default=None,
        update=None,
        options={'ANIMATABLE'},
        get=None,
        set=None)



    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'


    def get_next_vert(self, vert, selected, ordered):
        for e in vert.link_edges:
            for v in e.verts:
                if v in selected and v not in ordered:
                    return v

    def bspline(self, context, cyclic):
        return
    def execute(self, context):
        # create bmesh
        bm = bmesh.from_edit_mesh(context.active_object.data)

        # (x, y, z) = f(s)
        bm_verts_selected = [v for v in bm.verts if v.select]
        ordered_verts = []
        ordered_verts.append(bm_verts_selected[0])
        for i in range(0, len(bm_verts_selected)-1):
            ordered_verts.append(self.get_next_vert(ordered_verts[i],  \
                                                    bm_verts_selected, \
                                                    ordered_verts)     )


        x_sample = np.array([e.co[0] for e in ordered_verts])
        y_sample = np.array([e.co[1] for e in ordered_verts])
        z_sample = np.array([e.co[2] for e in ordered_verts])

        x_sample = np.r_[x_sample, x_sample[0]]
        y_sample = np.r_[y_sample, y_sample[0]]
        z_sample = np.r_[z_sample, z_sample[0]]
        
        tck, u = interpolate.splprep([x_sample,y_sample,z_sample], k=self.degree, s=self.smoothing, per=True)

        u_fine = np.linspace(0,1, self.samples+1)
        x_fine, y_fine, z_fine = interpolate.splev(u_fine, tck)

        new_verts = []
        for x, y, z in zip(x_fine, y_fine, z_fine):
            new_verts.append(bmesh.ops.create_vert(bm, co=mathutils.Vector((x, y, z)))["vert"][0])

        for i in range(-1, len(new_verts)-1):
            bm.edges.new([new_verts[i], new_verts[i+1]])

        bmesh.ops.remove_doubles(bm, verts=new_verts, dist=0.0001)
        # update bmesh
        bm.select_flush(True)
        bmesh.update_edit_mesh(context.active_object.data, loop_triangles=True, destructive=True)
        return {'FINISHED'}
