import bpy

class POSE_PT_panel(bpy.types.Panel):
    bl_label = "Pose"
    bl_idname = "POSE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Multi Utility'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.multi_utility_settings

        # Global Transform Tools
        box = layout.box()
        box.label(text="Global Transform Tools", icon='OBJECT_DATA')
        row = box.row(align=True)
        row.operator("BONE_OT_copy_global_transform", text="Copy Transform", icon='COPYDOWN')
        row.operator("BONE_OT_paste_global_transform", text="Paste Transform", icon='PASTEDOWN')
        
        # TrackChild Constraint Tools
        box = layout.box()
        box.label(text="TrackChild Constraint Tools", icon='CONSTRAINT')
        box.operator("bone_tools.add_damped_track", text="Add TrackChild Constraint", icon='CON_TRACKTO')

        row = box.row(align=True)
        row.prop(settings, "trackchild_influence", text="Influence")
        row.operator("bone_tools.adjust_damped_track_influence", text="Apply Influence", icon='CHECKMARK')

        box.separator()
        box.operator("bone_tools.remove_trackchild_constraints", text="Remove TrackChild", icon='X')

class OBJECT_PT_panel(bpy.types.Panel):
    bl_label = "Object"
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Multi Utility'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.multi_utility_settings
        
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


class SCULPT_PT_panel(bpy.types.Panel):
    bl_label = "Sculpt"
    bl_idname = "SCULPT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Multi Utility'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Work in Progress")


class ANIMATION_PT_panel(bpy.types.Panel):
    bl_label = "Animation"
    bl_idname = "ANIMATION_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Multi Utility'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.multi_utility_settings
        
        # Graph Editor Tools
        box = layout.box()
        box.label(text="Graph Editor Simplified", icon='GRAPH')

        # === AXIS TOGGLES ===
        for label, prefix in [("Location", "loc"), ("Rotation", "rot"), ("Scale", "scl")]:
            row = box.row()
            row.label(text=label)
            row.prop(settings, f"{prefix}_x", toggle=True, text="X")
            row.prop(settings, f"{prefix}_y", toggle=True, text="Y")
            row.prop(settings, f"{prefix}_z", toggle=True, text="Z")

        box.separator()
        
        box.prop(settings, "interpolation_mode")
        box.prop(settings, "extrapolation_mode")
        box.operator("anim_tools.apply_curve_settings", text="Apply to Selected", icon='CHECKMARK')

        box.separator()
        
        box.prop(settings, "handle_mode", text="Handle Mode")

        # Root Alignment Automation
        box = layout.box()
        box.label(text="Root Alignment Automation", icon='ARMATURE_DATA')
        box.operator("anim_tools.root_alignment_automation", text="Align Root to Foot", icon='CON_LOCLIKE')