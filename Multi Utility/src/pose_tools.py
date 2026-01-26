import bpy
from mathutils import Matrix

# === POSE OPERATORS ===
bone_stored_world_matrix = None

#-----------------------------
#  copy bone global transform
#-----------------------------
class BONE_OT_copy_global_transform(bpy.types.Operator):
    bl_idname = "bone.copy_global_transform"
    bl_label = "Copy Bone Global Transform"

    def execute(self, context):
        global bone_stored_world_matrix
        
        # Check we're in pose mode
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose Mode")
            return {'CANCELLED'}
        
        # Get the active pose bone
        bone = context.active_pose_bone
        if not bone:
            self.report({'ERROR'}, "No active pose bone")
            return {'CANCELLED'}

        # Get the bone's world matrix (this takes constraints into account)
        depsgraph = context.evaluated_depsgraph_get()
        obj = context.object
        eval_obj = obj.evaluated_get(depsgraph)
        eval_bone = eval_obj.pose.bones[bone.name]
        
        bone_stored_world_matrix = obj.matrix_world @ eval_bone.matrix

        self.report({'INFO'}, "Bone global transform copied")
        return {'FINISHED'}


class BONE_OT_paste_global_transform(bpy.types.Operator):
    bl_idname = "bone.paste_global_transform"
    bl_label = "Paste Bone Global Transform"

    def execute(self, context):
        global bone_stored_world_matrix
        
        if bone_stored_world_matrix is None:
            self.report({'ERROR'}, "No bone global transform stored")
            return {'CANCELLED'}

        # Check we're in pose mode
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose Mode")
            return {'CANCELLED'}
        
        bone = context.active_pose_bone
        if not bone:
            self.report({'ERROR'}, "No active pose bone")
            return {'CANCELLED'}

        # Set the bone's matrix directly
        bone.matrix = bone_stored_world_matrix.copy()

        self.report({'INFO'}, "Bone global transform pasted")
        return {'FINISHED'}

#---------------------------
#  damped track constraints
#---------------------------
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

