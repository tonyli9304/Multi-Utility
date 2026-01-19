bl_info = {
    "name": "Multi Utility",
    "author": "Tony Li",
    "version": (1, 5),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > Multi Utility",
    "description": "Various pose, object, and animation utilities",
    "category": "Animation",
}

import bpy
import math

# === GLOBAL STORAGE ===
stored_world_matrix = None

# === PROPERTIES ===
class MultiUtilityProperties(bpy.types.PropertyGroup):
    ui_tabs: bpy.props.EnumProperty(
        name="Tabs",
        description="Choose utility category",
        items=[
            ('POSE', "Pose", "Pose-related tools"),
            ('OBJECT', "Object", "Object-related tools"),
            ('ANIMATION', "Animation", "Animation-related tools"),
        ],
        default='POSE'
    )

    trackchild_influence: bpy.props.FloatProperty(
        name="Influence",
        description="Set influence value for TrackChild constraints",
        default=0.2,
        min=0.0,
        max=1.0
    )

    reset_location: bpy.props.BoolProperty(
        name="Location",
        description="Reset Location",
        default=True
    )
    reset_rotation: bpy.props.BoolProperty(
        name="Rotation",
        description="Reset Rotation",
        default=True
    )
    reset_scale: bpy.props.BoolProperty(
        name="Scale",
        description="Reset Scale",
        default=True
    )

    # === AXIS TOGGLES ===
    loc_x: bpy.props.BoolProperty(name="X", default=True)
    loc_y: bpy.props.BoolProperty(name="Y", default=True)
    loc_z: bpy.props.BoolProperty(name="Z", default=True)
    rot_x: bpy.props.BoolProperty(name="X", default=True)
    rot_y: bpy.props.BoolProperty(name="Y", default=True)
    rot_z: bpy.props.BoolProperty(name="Z", default=True)
    scl_x: bpy.props.BoolProperty(name="X", default=True)
    scl_y: bpy.props.BoolProperty(name="Y", default=True)
    scl_z: bpy.props.BoolProperty(name="Z", default=True)

    # === INTERPOLATION / EXTRAPOLATION ===
    interpolation_mode: bpy.props.EnumProperty(
        name="Interpolation",
        items=[
            ('CONSTANT', "Constant", ""),
            ('LINEAR', "Linear", ""),
            ('BEZIER', "Bezier", ""),
        ],
        default='BEZIER'
    )
    extrapolation_mode: bpy.props.EnumProperty(
        name="Extrapolation",
        items=[
            ('CONSTANT', "Constant", ""),
            ('LINEAR', "Linear", ""),
            ('CYCLIC', "Cyclic", ""),
        ],
        default='CONSTANT'
    )

    # === HANDLE EDITING SHARED ===
    handle_mode: bpy.props.EnumProperty(
        name="Handle Mode",
        items=[
            ('', "None", ""),
            ('AUTO', "Auto", ""),
            ('VECTOR', "Vector", ""),
            ('ALIGNED', "Aligned", ""),
            ('FREE', "Free", ""),
            ('AUTO_CLAMPED', "Auto Clamped", ""),
        ],
        default='',
    )

    # For ALIGNED mode
    handle_scale: bpy.props.FloatProperty(name="Handle Scale", default=1.0, min=0.0)
    handle_rotate: bpy.props.FloatProperty(name="Handle Rotate", default=0.0, subtype='ANGLE')

    # For FREE mode
    handle_left_scale: bpy.props.FloatProperty(name="Left Handle Scale", default=1.0, min=0.0)
    handle_left_rotate: bpy.props.FloatProperty(name="Left Handle Rotate", default=0.0, subtype='ANGLE')
    handle_right_scale: bpy.props.FloatProperty(name="Right Handle Scale", default=1.0, min=0.0)
    handle_right_rotate: bpy.props.FloatProperty(name="Right Handle Rotate", default=0.0, subtype='ANGLE')

    debug_filler_scroll: bpy.props.BoolProperty(
        name="Debug Scroll Filler",
        description="Add extra UI elements to force scrolling",
        default=False
    )

# === POSE OPERATORS ===
class BONE_OT_add_damped_track(bpy.types.Operator):
    bl_idname = "bone_tools.add_damped_track"
    bl_label = "Add Damped Track (TrackChild)"

    def execute(self, context):
        obj = context.object
        if obj.type != 'ARMATURE' or obj.mode != 'POSE':
            self.report({'WARNING'}, "Must be in Pose Mode with an armature selected.")
            return {'CANCELLED'}

        added, skipped = 0, 0
        for bone in context.selected_pose_bones:
            edit_bone = obj.data.bones[bone.name]
            children = [child for child in edit_bone.children]
            if len(children) == 1:
                if any(c.name == "TrackChild" for c in bone.constraints):
                    skipped += 1
                    continue
                c = bone.constraints.new(type='DAMPED_TRACK')
                c.name = "TrackChild"
                c.target = obj
                c.subtarget = children[0].name
                c.influence = 0.4
                added += 1
            else:
                skipped += 1
        self.report({'INFO'}, f"Added: {added}, Skipped: {skipped}")
        return {'FINISHED'}

class BONE_OT_adjust_damped_track_influence(bpy.types.Operator):
    bl_idname = "bone_tools.adjust_damped_track_influence"
    bl_label = "Set TrackChild Influence"

    def execute(self, context):
        obj = context.object
        value = context.scene.multi_utility_settings.trackchild_influence
        if obj.type != 'ARMATURE' or obj.mode != 'POSE':
            self.report({'WARNING'}, "Must be in Pose Mode.")
            return {'CANCELLED'}

        updated = 0
        for bone in context.selected_pose_bones:
            for c in bone.constraints:
                if c.type == 'DAMPED_TRACK' and c.name == "TrackChild":
                    c.influence = value
                    updated += 1
        self.report({'INFO'}, f"Updated {updated} constraint(s).")
        return {'FINISHED'}

class BONE_OT_remove_trackchild_constraints(bpy.types.Operator):
    bl_idname = "bone_tools.remove_trackchild_constraints"
    bl_label = "Remove TrackChild Constraints"

    def execute(self, context):
        obj = context.object
        if obj.type != 'ARMATURE' or obj.mode != 'POSE':
            self.report({'WARNING'}, "Must be in Pose Mode.")
            return {'CANCELLED'}

        removed = 0
        for bone in context.selected_pose_bones:
            for c in list(bone.constraints):
                if c.type == 'DAMPED_TRACK' and c.name == "TrackChild":
                    bone.constraints.remove(c)
                    removed += 1
        self.report({'INFO'}, f"Removed {removed} constraint(s).")
        return {'FINISHED'}

# === OBJECT OPERATORS ===
class OBJECT_OT_copy_global_transform(bpy.types.Operator):
    bl_idname = "object.copy_global_transform"
    bl_label = "Copy Global Transform"

    def execute(self, context):
        global stored_world_matrix
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        depsgraph = context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        stored_world_matrix = eval_obj.matrix_world.copy()

        self.report({'INFO'}, "Global transform copied")
        return {'FINISHED'}

class OBJECT_OT_paste_global_transform(bpy.types.Operator):
    bl_idname = "object.paste_global_transform"
    bl_label = "Paste Global Transform"

    def execute(self, context):
        global stored_world_matrix
        obj = context.active_object
        if not obj or stored_world_matrix is None:
            self.report({'ERROR'}, "Missing object or transform")
            return {'CANCELLED'}

        depsgraph = context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)

        parent_matrix = eval_obj.matrix_world @ obj.matrix_basis.inverted_safe()
        local_matrix = parent_matrix.inverted_safe() @ stored_world_matrix
        obj.matrix_basis = local_matrix

        obj.keyframe_insert(data_path="location")
        obj.keyframe_insert(data_path="rotation_euler")
        obj.keyframe_insert(data_path="scale")

        self.report({'INFO'}, "Global transform pasted")
        return {'FINISHED'}

class OBJECT_OT_reset_transform(bpy.types.Operator):
    bl_idname = "object.reset_global_transform"
    bl_label = "Reset Transform"
    bl_description = "Reset selected transform components of the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        props = context.scene.multi_utility_settings
        reset_count = 0

        if props.reset_location:
            obj.location = (0.0, 0.0, 0.0)
            obj.keyframe_insert(data_path="location")
            reset_count += 1

        if props.reset_rotation:
            obj.rotation_euler = (0.0, 0.0, 0.0)
            obj.keyframe_insert(data_path="rotation_euler")
            reset_count += 1

        if props.reset_scale:
            obj.scale = (1.0, 1.0, 1.0)
            obj.keyframe_insert(data_path="scale")
            reset_count += 1

        self.report({'INFO'}, f"Reset {reset_count} component(s)")
        return {'FINISHED'}

# === ANIMATION OPERATORS ===
class ANIM_OT_test_button(bpy.types.Operator):
    bl_idname = "anim_tools.test_button"
    bl_label = "Test Button"
    bl_description = "A test button to check UI rendering"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({'INFO'}, "Test button clicked")
        return {'FINISHED'}

class ANIM_OT_apply_curve_settings(bpy.types.Operator):
    bl_idname = "anim_tools.apply_curve_settings"
    bl_label = "Apply to Selected"
    bl_description = "Apply interpolation and extrapolation settings to selected curves"

    @classmethod
    def poll(cls, context):
        print(f"Poll called with context: {context.area.type}, {context.region.type}, {context.space_data.type}")
        return True

    def execute(self, context):
        self.report({'INFO'}, "Operator executed")
        return {'FINISHED'}

class ANIM_OT_set_handle_type(bpy.types.Operator):
    bl_idname = "anim_tools.set_handle_type"
    bl_label = "Set Handle Type"
    bl_description = "Set handle type for selected keyframes"
    handle_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.animation_data or not obj.animation_data.action:
            self.report({'WARNING'}, "No active object with animation data")
            return {'CANCELLED'}

        action = obj.animation_data.action
        for fcurve in action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.handle_left_type = self.handle_type
                kf.handle_right_type = self.handle_type

        context.scene.multi_utility_settings.handle_mode = self.handle_type
        self.report({'INFO'}, f"Handle type set to {self.handle_type}")
        return {'FINISHED'}

class ANIM_OT_edit_handles_aligned(bpy.types.Operator):
    bl_idname = "anim_tools.edit_handles_aligned"
    bl_label = "Apply Aligned Edits"
    bl_description = "Apply scale and rotation to aligned handles"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = context.scene.multi_utility_settings
        obj = context.active_object
        if not obj or not obj.animation_data or not obj.animation_data.action:
            self.report({'WARNING'}, "No active object with animation data")
            return {'CANCELLED'}

        action = obj.animation_data.action
        for fcurve in action.fcurves:
            for kf in fcurve.keyframe_points:
                if kf.handle_left_type == 'ALIGNED' and kf.handle_right_type == 'ALIGNED':
                    handle_left = kf.handle_left - kf.co
                    handle_right = kf.handle_right - kf.co

                    handle_left *= settings.handle_scale
                    handle_right *= settings.handle_scale

                    angle = settings.handle_rotate
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    handle_left_rotated = [
                        handle_left[0] * cos_a - handle_left[1] * sin_a,
                        handle_left[0] * sin_a + handle_left[1] * cos_a
                    ]
                    handle_right_rotated = [
                        handle_right[0] * cos_a - handle_right[1] * sin_a,
                        handle_right[0] * sin_a + handle_right[1] * cos_a
                    ]

                    kf.handle_left = (kf.co[0] + handle_left_rotated[0], kf.co[1] + handle_left_rotated[1])
                    kf.handle_right = (kf.co[0] + handle_right_rotated[0], kf.co[1] + handle_right_rotated[1])

        self.report({'INFO'}, "Aligned handle edits applied")
        return {'FINISHED'}

class ANIM_OT_edit_handles_free(bpy.types.Operator):
    bl_idname = "anim_tools.edit_handles_free"
    bl_label = "Apply Free Edits"
    bl_description = "Apply scale and rotation to free handles"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = context.scene.multi_utility_settings
        obj = context.active_object
        if not obj or not obj.animation_data or not obj.animation_data.action:
            self.report({'WARNING'}, "No active object with animation data")
            return {'CANCELLED'}

        action = obj.animation_data.action
        for fcurve in action.fcurves:
            for kf in fcurve.keyframe_points:
                if kf.handle_left_type == 'FREE' and kf.handle_right_type == 'FREE':
                    handle_left = kf.handle_left - kf.co
                    handle_right = kf.handle_right - kf.co

                    handle_left *= settings.handle_left_scale
                    handle_right *= settings.handle_right_scale

                    angle_left = settings.handle_left_rotate
                    angle_right = settings.handle_right_rotate
                    cos_al = math.cos(angle_left)
                    sin_al = math.sin(angle_left)
                    cos_ar = math.cos(angle_right)
                    sin_ar = math.sin(angle_right)

                    handle_left_rotated = [
                        handle_left[0] * cos_al - handle_left[1] * sin_al,
                        handle_left[0] * sin_al + handle_left[1] * cos_al
                    ]
                    handle_right_rotated = [
                        handle_right[0] * cos_ar - handle_right[1] * sin_ar,
                        handle_right[0] * sin_ar + handle_right[1] * cos_ar
                    ]

                    kf.handle_left = (kf.co[0] + handle_left_rotated[0], kf.co[1] + handle_left_rotated[1])
                    kf.handle_right = (kf.co[0] + handle_right_rotated[0], kf.co[1] + handle_right_rotated[1])

        self.report({'INFO'}, "Free handle edits applied")
        return {'FINISHED'}

# === MAIN PANEL ===
class MULTI_PT_main_panel(bpy.types.Panel):
    bl_label = "Multi Utility"
    bl_idname = "MULTI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Multi Utility'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.multi_utility_settings

        row = layout.row(align=True)
        row.prop(settings, "ui_tabs", expand=True)

        if settings.ui_tabs == 'POSE':
            self.draw_pose_tab(layout, settings)
        elif settings.ui_tabs == 'OBJECT':
            self.draw_object_tab(layout)
        elif settings.ui_tabs == 'ANIMATION':
            self.draw_animation_tab(layout, settings)

    def draw_pose_tab(self, layout, settings):
        box = layout.box()
        box.label(text="TrackChild Constraint Tools", icon='CONSTRAINT')

        box.operator("bone_tools.add_damped_track", text="Add TrackChild Constraint", icon='CON_TRACKTO')

        row = box.row(align=True)
        row.prop(settings, "trackchild_influence", text="Influence")
        row.operator("bone_tools.adjust_damped_track_influence", text="Apply Influence", icon='CHECKMARK')

        box.separator()
        box.operator("bone_tools.remove_trackchild_constraints", text="Remove TrackChild", icon='X')

        box.separator()
        box.operator("anim_tools.test_button", text="Test Button in Pose Tab", icon='QUESTION')

    def draw_object_tab(self, layout):
        settings = bpy.context.scene.multi_utility_settings
        box = layout.box()
        box.label(text="Global Transform Tools", icon='OBJECT_DATA')

        row = box.row(align=True)
        row.operator("object.copy_global_transform", text="Copy Transform", icon='COPYDOWN')
        row.operator("object.paste_global_transform", text="Paste Transform", icon='PASTEDOWN')

        box.separator()
        box.label(text="Reset Transform:")
        row = box.row(align=True)
        row.prop(settings, "reset_location", toggle=True)
        row.prop(settings, "reset_rotation", toggle=True)
        row.prop(settings, "reset_scale", toggle=True)

        box.operator("object.reset_global_transform", text="Reset Transform", icon='FILE_REFRESH')

    def draw_animation_tab(self, layout, settings):
        layout.label(text="Graph Editor Simplified", icon='GRAPH')

        # === AXIS TOGGLES ===
        for label, prefix in [("Location", "loc"), ("Rotation", "rot"), ("Scale", "scl")]:
            col = layout.column()
            row = col.row()
            row.label(text=label)
            row.prop(settings, f"{prefix}_x", toggle=True, text="X")
            row.prop(settings, f"{prefix}_y", toggle=True, text="Y")
            row.prop(settings, f"{prefix}_z", toggle=True, text="Z")

        layout.separator()
        layout.label(text="Debug: Before Interpolation", icon='INFO')
        print("Debug: Entering Properties Section")

        col = layout.column()
        col.prop(settings, "interpolation_mode")  # First property
        print("Debug: After First Property")
        col.prop(settings, "extrapolation_mode")  # Second property
        print("Debug: After Second Property")
        col.operator("anim_tools.apply_curve_settings", text="Apply to Selected", icon='CHECKMARK')
        print("Debug: Exited Operator Section")

        layout.separator()
        layout.label(text="Debug: Before Handle Editing", icon='INFO')
        print("Debug: Entering Handle Editing Section")

        # Move handle_mode here to test
        col = layout.column()
        col.prop(settings, "handle_mode", text="Handle Mode Test")
        print("Debug: After Handle Mode Test")

        layout.label(text="Debug: End of Panel", icon='INFO')

# === REGISTRATION ===
classes = (
    MultiUtilityProperties,
    BONE_OT_add_damped_track,
    BONE_OT_adjust_damped_track_influence,
    BONE_OT_remove_trackchild_constraints,
    OBJECT_OT_copy_global_transform,
    OBJECT_OT_paste_global_transform,
    OBJECT_OT_reset_transform,
    ANIM_OT_test_button,
    ANIM_OT_apply_curve_settings,
    ANIM_OT_set_handle_type,
    ANIM_OT_edit_handles_aligned,
    ANIM_OT_edit_handles_free,
    MULTI_PT_main_panel,
)

def register():
    for cls in classes:
        print(f"Registering class: {cls.__name__}")
        bpy.utils.register_class(cls)
    bpy.types.Scene.multi_utility_settings = bpy.props.PointerProperty(type=MultiUtilityProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.multi_utility_settings

if __name__ == "__main__":
    register()