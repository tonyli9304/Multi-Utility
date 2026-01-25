import bpy

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
