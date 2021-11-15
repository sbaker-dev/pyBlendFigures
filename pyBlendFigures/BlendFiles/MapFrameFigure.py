from blendSupports.Nodes.emission_node import create_emission_node
from miscSupports import load_json
import bpy

frame_dict = load_json(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Map2\Test2\UE_Values.txt")

for frame_id, frame_place_values in frame_dict.items():

    for index, (place, colour) in enumerate(frame_place_values.items()):
        print(f"{index}/{len(frame_place_values)}")

        bpy.ops.object.select_all(action='DESELECT')

        obj = bpy.context.scene.objects.get(place)
        obj.select_set(True)
        create_emission_node(obj, colour, 1, f'F{frame_id}-{place}')

        # Isolate the index of that material, set it to active
        material_index = {mat.name: i for i, mat in enumerate(obj.data.materials)}[f'F{frame_id}-{place}']
        bpy.context.object.active_material_index = material_index

        # Assign this material
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.material_slot_assign()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()
        break

    break