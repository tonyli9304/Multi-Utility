import bpy

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
