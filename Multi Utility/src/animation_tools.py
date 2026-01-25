import bpy
import math

# === ANIMATION OPERATORS ===
class ANIM_OT_test_button(bpy.types.Operator):
    bl_idname = "anim_tools.test_button"
    bl_label = "Test Button"

    def execute(self, context):
        self.report({'INFO'}, "Test button clicked!")
        return {'FINISHED'}

class ANIM_OT_apply_curve_settings(bpy.types.Operator):
    bl_idname = "anim_tools.apply_curve_settings"
    bl_label = "Apply Curve Settings"
    bl_description = "Apply interpolation and extrapolation to selected keyframes"

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
        axis_map = {
            'location': ['loc_x', 'loc_y', 'loc_z'],
            'rotation_euler': ['rot_x', 'rot_y', 'rot_z'],
            'scale': ['scl_x', 'scl_y', 'scl_z']
        }

        for fcurve in action.fcurves:
            path = fcurve.data_path
            index = fcurve.array_index

            apply_curve = False
            for key, axes in axis_map.items():
                if key in path and getattr(settings, axes[index]):
                    apply_curve = True
                    break

            if apply_curve:
                for kf in fcurve.keyframe_points:
                    if kf.select_control_point:
                        kf.interpolation = settings.interpolation_mode
                fcurve.extrapolation = settings.extrapolation_mode

        self.report({'INFO'}, "Curve settings applied")
        return {'FINISHED'}

class ANIM_OT_set_handle_type(bpy.types.Operator):
    bl_idname = "anim_tools.set_handle_type"
    bl_label = "Set Handle Type"
    bl_description = "Set handle type for selected keyframes"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = context.scene.multi_utility_settings
        obj = context.active_object
        if not obj or not obj.animation_data or not obj.animation_data.action:
            self.report({'WARNING'}, "No active object with animation data")
            return {'CANCELLED'}

        if not settings.handle_mode:
            self.report({'WARNING'}, "No handle mode selected")
            return {'CANCELLED'}

        action = obj.animation_data.action
        for fcurve in action.fcurves:
            for kf in fcurve.keyframe_points:
                if kf.select_control_point:
                    kf.handle_left_type = settings.handle_mode
                    kf.handle_right_type = settings.handle_mode

        self.report({'INFO'}, f"Handle type set to {settings.handle_mode}")
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
