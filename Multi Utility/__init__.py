bl_info = {
    "name": "Multi Utility",
    "author": "Tony Li",
    "version": (1, 5),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > Multi Utility",
    "description": "Utilities targeted at solo animators for convenience in repetitive tasks",
    "category": "Animation",
}

import bpy
from .src import properties
from .src import pose_tools
from .src import object_tools
from .src import animation_tools
from .src import ui_panel

# === REGISTRATION ===
classes = (
    properties.MultiUtilityProperties,
    #pose
    pose_tools.BONE_OT_add_damped_track,
    pose_tools.BONE_OT_adjust_damped_track_influence,
    pose_tools.BONE_OT_remove_trackchild_constraints,
    #object
    object_tools.OBJECT_OT_copy_global_transform,
    object_tools.OBJECT_OT_paste_global_transform,
    object_tools.OBJECT_OT_reset_transform,
    #animation
    animation_tools.ANIM_OT_test_button,
    animation_tools.ANIM_OT_apply_curve_settings,
    animation_tools.ANIM_OT_set_handle_type,
    animation_tools.ANIM_OT_edit_handles_aligned,
    animation_tools.ANIM_OT_edit_handles_free,
    # ui
    #ui_panel.MULTI_PT_main_panel,
    ui_panel.POSE_PT_panel,
    ui_panel.OBJECT_PT_panel,
    ui_panel.SCULPT_PT_panel,
    ui_panel.ANIMATION_PT_panel,
)

def register():
    for cls in classes:
        print(f"Registering class: {cls.__name__}")
        bpy.utils.register_class(cls)
    bpy.types.Scene.multi_utility_settings = bpy.props.PointerProperty(type=properties.MultiUtilityProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.multi_utility_settings

if __name__ == "__main__":
    register()
