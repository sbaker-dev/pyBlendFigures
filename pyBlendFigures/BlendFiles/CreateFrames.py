from miscSupports import parse_as_numeric
from csvObject import CsvObject
from pathlib import Path

import bpy


class CreateFrames:
    def __init__(self, start_date):

        self._setup_camera()

        self.colours = [(i / 10, i / 10, i / 10, 1.0) for i in range(1, 11)]
        self.missing = (0.0, 0.0, 0.0, 1.0)
        self.date_i = 2

        self.data = CsvObject(r"I:\Work\DataBases\Adjacent\Rates.csv", set_columns=True)
        self.write_directory = r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Map2\Test\Frames"

        self.unique_dates = [int(date) for date in sorted(list(set(self.data[self.date_i])))]

        if not start_date:
            self.start_date = min(self.unique_dates)
        else:
            self.start_date = start_date

        self.name_i = 0
        self.start_index = 3

        self.create_frames()

    @staticmethod
    def _setup_camera():
        camera = bpy.data.objects["Camera"]

        camera_position = (387584, 331645, 1218433)
        camera.location = camera_position
        camera.data.clip_end = 1e+18
        camera.data.ortho_scale = 700000

    def create_frames(self):
        for value_i in range(self.start_index, len(self.data.headers)):
            print(value_i)

            for date_frame in self.unique_dates:
                if date_frame >= self.start_date:
                    print(date_frame)

                    # Isolate the value for this phenotype for this date_frame
                    place_values, value_bands = self.isolate_place_values(date_frame, value_i)

                    for place, value in place_values.items():
                        if value == -1:
                            self.change_colour(place, self.missing)
                        else:
                            self.change_colour(place, self.band_colour(value_bands, value))

                        break

                    # Render the scene
                    bpy.context.scene.render.filepath = str(
                        Path(self.write_directory, f"{self.data.headers[value_i]}_{date_frame}.png").absolute())
                    bpy.context.scene.eevee.use_gtao = True
                    bpy.context.scene.render.film_transparent = True
                    bpy.ops.render.render(write_still=True)

                    break

            break

    def isolate_place_values(self, date_frame, value_i):
        place_values = {}
        for row in self.data.row_data:
            if int(row[self.date_i]) == date_frame:
                # Try to isolate the value
                try:
                    value = float(row[value_i])
                except ValueError:
                    value = -1

                place_values[row[self.name_i]] = value

        value_bands = [parse_as_numeric(v, float) for v in place_values.values()]
        return place_values, [(i / 10) * max(value_bands) for i in range(10)] + [max(value_bands)]

    def band_colour(self, value_bands, value):
        for ci, band in enumerate(value_bands):
            if ci > 0:
                if value_bands[ci - 1] <= value < value_bands[ci]:
                    return self.colours[ci - 1]

        return self.missing

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


CreateFrames(19610125)
