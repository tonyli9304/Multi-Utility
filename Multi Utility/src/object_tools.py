import bpy

# === GLOBAL STORAGE ===
stored_world_matrix = None

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
        if stored_world_matrix is None:
            self.report({'ERROR'}, "No global transform stored")
            return {'CANCELLED'}

        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        obj.matrix_world = stored_world_matrix.copy()
        self.report({'INFO'}, "Global transform pasted")
        return {'FINISHED'}

class OBJECT_OT_reset_transform(bpy.types.Operator):
    bl_idname = "object.reset_global_transform"
    bl_label = "Reset Global Transform"

    def execute(self, context):
        settings = context.scene.multi_utility_settings
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        if settings.reset_location:
            obj.location = (0, 0, 0)
        if settings.reset_rotation:
            obj.rotation_euler = (0, 0, 0)
        if settings.reset_scale:
            obj.scale = (1, 1, 1)

        self.report({'INFO'}, "Transform reset")
        return {'FINISHED'}
