# 3DCC Custom Blender Exporter v0.2a
# Allows for more consistent GLTF export from Blender
# Exported models should have the following rule of three format:
# vec3 position, vec3 normal, vec2 texcoords, vec4 tangent, 16bit indicies
# Run the script in Blender or install it to access the new exporter 
import bpy

def add_uvs_to_meshes(selected_objects):
    # Loop through selected objects
    for obj in selected_objects:
        if obj.type == 'MESH':
            # Check if the mesh has UVs
            if not obj.data.uv_layers:
                # Create a new UV layer
                obj.data.uv_layers.new(name="UVMap")

def triangulate_scene(selected_objects):
    # Triangulate selected objects
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.mode_set(mode='OBJECT')

def export_data(filepath):
    # Ensure the filepath ends with '.gltf'
    if not filepath.lower().endswith('.gltf'):
        filepath += '.gltf'
    
    # Store the current selection and mode
    selected_objects = bpy.context.selected_objects
    if not selected_objects:
        bpy.ops.wm.call_menu(name="ERROR_MT_no_selection")
        return {'CANCELLED'}
    
    current_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add UVs to meshes
    add_uvs_to_meshes(selected_objects)

    # Triangulate the scene
    triangulate_scene(selected_objects)
    
    bpy.ops.export_scene.gltf(filepath=filepath, 
        export_format='GLTF_SEPARATE', # GLB is faster, but GLTF is easier to debug
        use_selection=True,
        export_colors=False,
        export_tangents=True,
        #export_use_gltfpack=True, # Appears to be not ready for prime time yet
        #export_gltfpack_tc=True, # Enable this when export_use_gltfpack is ready (KTX Support)
        export_texture_dir="Textures",
        export_image_format='AUTO' # There is no force PNG yet... also KTX is not supported yet
        #export_cameras=True,
        #export_lights=True,
        #export_extras=True
        )
    
    # Restore the selection and mode to the previous state
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected_objects:
        obj.select_set(True)
    if bpy.context.object:
        bpy.context.view_layer.objects.active = bpy.context.object
    bpy.ops.object.mode_set(mode=current_mode)

    return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ExportOperator.bl_idname)

class ExportOperator(bpy.types.Operator):
    bl_idname = "export.custom_gltf_export"
    bl_label = "3DCC GLTF v0.2a"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        return export_data(self.filepath)

    def invoke(self, context, event):
        # Get the Blender project name as the default file name
        self.filepath = bpy.path.display_name_from_filepath(bpy.data.filepath)
        # Set the default filename with ".gltf" extension
        self.filepath = bpy.path.ensure_ext(self.filepath, ext=".gltf")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ERROR_MT_no_selection(bpy.types.Menu):
    bl_label = "Error"
    bl_idname = "ERROR_MT_no_selection"

    def draw(self, context):
        layout = self.layout
        layout.label(text="No objects selected for export.", icon='ERROR')

def register():
    bpy.utils.register_class(ExportOperator)
    bpy.utils.register_class(ERROR_MT_no_selection)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(ERROR_MT_no_selection)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
