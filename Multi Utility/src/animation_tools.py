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

import bpy

class ANIM_OT_root_alignment_automation(bpy.types.Operator):
    bl_idname = "anim_tools.root_alignment_automation"
    bl_label = "Root Alignment Automation"
    bl_description = "Automatically align root bone movement to a stationary foot controller across keyframes"
    bl_options = {'REGISTER', 'UNDO'}

    stationary_mode: bpy.props.BoolProperty(
        name="Stationary Mode (Invert Delta)",
        description="Invert delta for anti-slide (root counters foot movement to keep foot stationary)",
        default=False  # False for your pseudocode (follow); True for bl_description (stationary)
    )

    def execute(self, context):
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose Mode")
            return {'CANCELLED'}

        selected_bones = context.selected_pose_bones
        if len(selected_bones) != 2:
            self.report({'ERROR'}, "Select exactly 2 bones: foot controller and root bone")
            return {'CANCELLED'}

        # Auto-detect foot based on name (handles order issue)
        foot_candidate1 = selected_bones[0]
        foot_candidate2 = selected_bones[1]
        if "foot" in foot_candidate1.name.lower() or "ik" in foot_candidate1.name.lower():
            foot_controller = foot_candidate1
            root_bone = foot_candidate2
        elif "foot" in foot_candidate2.name.lower() or "ik" in foot_candidate2.name.lower():
            foot_controller = foot_candidate2
            root_bone = foot_candidate1
        else:
            # Fallback to original order with warning
            self.report({'WARNING'}, "No clear foot bone name detected; using selection order")
            foot_controller = selected_bones[0]
            root_bone = selected_bones[1]

        obj = context.object

        if not obj.animation_data or not obj.animation_data.action:
            self.report({'ERROR'}, "No animation data found")
            return {'CANCELLED'}

        action = obj.animation_data.action

        # Collect selected keyframes ONLY from foot's f-curves
        foot_paths = [
            f'pose.bones["{foot_controller.name}"].location',
            f'pose.bones["{foot_controller.name}"].rotation_quaternion',
            f'pose.bones["{foot_controller.name}"].rotation_euler',
            f'pose.bones["{foot_controller.name}"].rotation_axis_angle',
        ]
        selected_keyframes = set()
        for fcurve in action.fcurves:
            if fcurve.data_path in foot_paths:
                for keyframe in fcurve.keyframe_points:
                    if keyframe.select_control_point:
                        selected_keyframes.add(int(keyframe.co[0]))

        if len(selected_keyframes) < 2:
            self.report({'ERROR'}, "Select at least 2 keyframes on the foot controller in Graph Editor/Dopesheet")
            return {'CANCELLED'}

        keyframe_list = sorted(list(selected_keyframes))

        # Cache obj world (handles non-identity armatures)
        obj_world = obj.matrix_world.copy()
        obj_world_inv = obj_world.inverted()

        # Set to first frame
        first_frame = keyframe_list[0]
        context.scene.frame_set(first_frame)
        context.view_layer.update()
        depsgraph = context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        eval_foot = eval_obj.pose.bones[foot_controller.name]
        eval_root = eval_obj.pose.bones[root_bone.name]

        previous_foot_global = obj_world @ eval_foot.matrix.copy()
        previous_root_global = obj_world @ eval_root.matrix.copy()

        # Process subsequent frames
        for i in range(1, len(keyframe_list)):
            current_frame = keyframe_list[i]
            context.scene.frame_set(current_frame)
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            eval_obj = obj.evaluated_get(depsgraph)
            eval_foot = eval_obj.pose.bones[foot_controller.name]

            foot_global_now = obj_world @ eval_foot.matrix.copy()

            # Delta
            if self.stationary_mode:
                delta_transform = previous_foot_global @ foot_global_now.inverted()  # Invert for stationary
            else:
                delta_transform = foot_global_now @ previous_foot_global.inverted()  # Follow

            new_root_global = delta_transform @ previous_root_global

            # Set root matrix (handle parent)
            if root_bone.parent:
                parent_world = obj_world @ root_bone.parent.matrix.copy()
                root_bone.matrix = parent_world.inverted() @ new_root_global
            else:
                root_bone.matrix = obj_world_inv @ new_root_global

            # Force immediate update to prevent snap/lag
            depsgraph.update()
            context.view_layer.update()

            # Keyframe (rotation-mode aware)
            root_bone.keyframe_insert(data_path="location", frame=current_frame)
            if root_bone.rotation_mode == 'QUATERNION':
                root_bone.keyframe_insert(data_path="rotation_quaternion", frame=current_frame)
            elif root_bone.rotation_mode in {'XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'}:
                root_bone.keyframe_insert(data_path="rotation_euler", frame=current_frame)
            elif root_bone.rotation_mode == 'AXIS_ANGLE':
                root_bone.keyframe_insert(data_path="rotation_axis_angle", frame=current_frame)
            # root_bone.keyframe_insert(data_path="scale", frame=current_frame)  # Uncomment if needed

            previous_foot_global = foot_global_now
            previous_root_global = new_root_global

        self.report({'INFO'}, f"Root alignment applied to {len(keyframe_list)} keyframes")
        return {'FINISHED'}