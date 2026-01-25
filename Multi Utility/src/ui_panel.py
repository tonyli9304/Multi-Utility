import bpy

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
