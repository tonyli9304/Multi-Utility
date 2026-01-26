import bpy
from mathutils import Matrix

# === POSE OPERATORS ===
bone_stored_world_matrix = None

#-----------------------------
#  copy bone global transform
#-----------------------------
import bpy
from mathutils import Matrix

bone_stored_world_matrix = None  # Global storage

import bpy
from mathutils import Matrix

bone_stored_world_matrix = None  # Global storage

class BONE_OT_copy_global_transform(bpy.types.Operator):
    bl_idname = "bone.copy_global_transform"
    bl_label = "Copy Bone Global Transform"

    def execute(self, context):
        global bone_stored_world_matrix
        
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose Mode")
            return {'CANCELLED'}
        
        bone = context.active_pose_bone
        if not bone:
            self.report({'ERROR'}, "No active pose bone")
            return {'CANCELLED'}

        depsgraph = context.evaluated_depsgraph_get()
        obj = context.object
        eval_obj = obj.evaluated_get(depsgraph)
        eval_bone = eval_obj.pose.bones[bone.name]
        
        # Store true world-space matrix
        bone_stored_world_matrix = obj.matrix_world @ eval_bone.matrix
        print(f"copied: {bone_stored_world_matrix}", flush=True)

        self.report({'INFO'}, "Bone global transform copied")
        return {'FINISHED'}

class BONE_OT_paste_global_transform(bpy.types.Operator):
    bl_idname = "bone.paste_global_transform"
    bl_label = "Paste Bone Global Transform"
    
    target_frame: bpy.props.IntProperty(name="Target Frame", default=-1)  # Optional: -1 means current frame

    def execute(self, context):
        global bone_stored_world_matrix
        
        if bone_stored_world_matrix is None:
            self.report({'ERROR'}, "No bone global transform stored")
            return {'CANCELLED'}

        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose Mode")
            return {'CANCELLED'}
        
        bone = context.active_pose_bone
        if not bone:
            self.report({'ERROR'}, "No active pose bone")
            return {'CANCELLED'}
        
        obj = context.object
        
        # Optional: Switch to target frame if specified
        if self.target_frame != -1:
            context.scene.frame_set(self.target_frame)
        
        # Compute required object-space matrix for snap (used if no Child Of)
        target_obj_matrix = obj.matrix_world.inverted() @ bone_stored_world_matrix
        
        # Check for Child Of constraints
        child_of_constraints = [c for c in bone.constraints if c.type == 'CHILD_OF']
        
        if child_of_constraints:
            # Create temp empty at stored world transform
            temp_empty = bpy.data.objects.new(name="Temp_CopyGlobal", object_data=None)
            context.scene.collection.objects.link(temp_empty)
            temp_empty.matrix_world = bone_stored_world_matrix

            # Add temp Copy Transforms (last in stack to override)
            ct = bone.constraints.new(type='COPY_TRANSFORMS')
            ct.target = temp_empty
            ct.target_space = 'WORLD'
            ct.owner_space = 'WORLD'
            ct.influence = 1.0

            # Force update
            depsgraph = context.evaluated_depsgraph_get()
            depsgraph.update()

            # Handle each Child Of: set inverse using operator
            child_of_count = 0
            for c in child_of_constraints:
                # Set as active constraint (required for the operator)
                obj.pose.bones[bone.name].constraints.active = c
                # Call the operator
                bpy.ops.constraint.childof_set_inverse(constraint=c.name, owner='BONE')
                child_of_count += 1

            # Clean up
            bone.constraints.remove(ct)
            bpy.data.objects.remove(temp_empty, do_unlink=True)

            # Report
            self.report({'INFO'}, f"Bone global transform pasted. {child_of_count} Child Of constraint(s) adjusted to maintain the pose.")
        else:
            # No Child Of: just set directly (or add mute logic here if other constraints)
            bone.matrix = target_obj_matrix
            self.report({'INFO'}, "Bone global transform pasted")

        print(f"pasted: {bone.matrix}", flush=True)

        # Optional: Auto-keyframe all channels (adjust for your rotation mode)
        # bone.keyframe_insert(data_path="location")
        # bone.keyframe_insert(data_path="rotation_quaternion" if bone.rotation_mode == 'QUATERNION' else "rotation_euler")
        # bone.keyframe_insert(data_path="scale")

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

