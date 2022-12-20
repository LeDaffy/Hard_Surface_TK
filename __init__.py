bl_info = {
    "name": "Hard Surface TK",
    "blender": (3, 20, 0),
    "category": "Mesh",
}

import bpy
from . hs_tools import interp 

classes = interp.SplineInterp

# register, unregister = bpy.utils.register_classes_factory(classes)
def register():
    bpy.utils.register_class(interp.SplineInterp)


def unregister():
    bpy.utils.unregister_class(interp.SplineInterp)
