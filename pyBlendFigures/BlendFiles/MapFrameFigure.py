from miscSupports import load_json
from pathlib import Path
import bpy

frame_dict = load_json(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Map2\Test2\UE_Values.txt")

write_directory = r"I:\Work\Figures_and_tables\Depreivation indexes\UEOverTime"

for frame_id, frame_place_values in frame_dict.items():

    for index, (place, colour) in enumerate(frame_place_values.items()):
        print(f"F{frame_id}: {index}/{len(frame_place_values)}")

        # Deselect any objects
        bpy.ops.object.select_all(action='DESELECT')

        # Isolate the current object
        obj = bpy.context.scene.objects.get(place)
        obj.select_set(True)

        # Isolate the first material emission node, change its colour to the colour required
        for mat in obj.data.materials:
            emission = mat.node_tree.nodes.get('Emission')
            emission.inputs[0].default_value = colour

    bpy.context.scene.render.filepath = str(Path(write_directory, f"{frame_id}.png").absolute())
    bpy.ops.render.render(write_still=True)
