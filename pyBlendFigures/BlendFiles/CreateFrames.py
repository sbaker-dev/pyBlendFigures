from blendSupports.misc import tuple_convert

from miscSupports import directory_iterator, chunk_list
from csvObject import CsvObject
from pathlib import Path

import bpy


class CreateFrames:
    def __init__(self, args):

        read_path, write_path, start_index, name_index = args

        self._setup_camera()

        self.data_path = Path(read_path)

        self.data = CsvObject(self.data_path, set_columns=True)
        self.write_directory = write_path

        self.start_index = int(start_index)
        self.name_i = int(name_index)

        self.create_frames()

    @staticmethod
    def _setup_camera():
        camera = bpy.data.objects["Camera"]

        camera_position = (387584, 331645, 1218433)
        camera.location = camera_position
        camera.data.clip_end = 1e+18
        camera.data.ortho_scale = 700000

    def create_frames(self):

        for i in range(self.start_index, len(self.data.headers)):

            for row in self.data.row_data:
                self.change_colour(row[self.name_i], tuple_convert(row[i]))

            # Render the scene
            bpy.context.scene.render.filepath = str(
                Path(self.write_directory, f"{self.data.headers[i]}_{self.data_path.stem}.png").absolute())
            bpy.context.scene.eevee.use_gtao = True
            bpy.context.scene.render.film_transparent = True
            bpy.ops.render.render(write_still=True)

    @staticmethod
    def change_colour(place, colour):
        # Select the current Object that has the same name as place
        ob = bpy.context.scene.objects[place]
        bpy.ops.object.select_all(action='DESELECT')

        # Make the District the active object
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

        # Make the District the active object
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

        for mat in ob.material_slots:
            mat.material.node_tree.nodes["Emission"].inputs[0].default_value = colour


root = r"I:\Work\DataBases\Adjacent\Months"
file_list = chunk_list(directory_iterator(root), int(len(directory_iterator(root)) / 5))

for file in file_list[0]:
    print(file)

    CreateFrames([Path(root, file),
                  r"I:\Work\Figures_and_tables\DiseasesOverTime",
                  2, 0])
