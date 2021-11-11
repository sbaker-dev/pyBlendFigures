from blendSupports.Nodes.emission_node import create_emission_node

from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text
from csvObject import CsvObject
from miscSupports import tuple_convert
import bpy


class Histogram:
    def __init__(self, args):
        write_directory, file_path, name_index, isolate, y_scale, border_width, colour, border_colour, write_name = args

        self.write_directory = write_directory
        self.csv_obj = CsvObject(file_path)
        self.name_i = int(name_index)
        self.isolate = int(isolate)
        self.y_scale = float(y_scale)
        self.border_width = float(border_width)
        self.colour = tuple_convert(colour)
        self.border_colour = tuple_convert(border_colour)
        self.write_name = write_name

        bpy.context.tool_settings.mesh_select_mode = (False, False, True)
        self.make_histogram()

        # TODO: Make the y axis text from a list rather than the standardisations that max it messy
        # todo: add some standardise rows so that we can put in the x axis

    def make_histogram(self):
        for i, row in enumerate(self.csv_obj.row_data):
            self.make_bar(i, row)
            self.make_name(i, row)

        # Save the blend file for manual manipulation later
        bpy.ops.wm.save_as_mainfile(filepath=f"{self.write_directory}/{self.write_name}.blend")

    def make_bar(self, i, row):
        """Make the bar for the histogram"""

        obj = self.make_bar_mesh(i, row)
        self.scale_bar(obj)
        self.bar_border(obj)

    def make_bar_mesh(self, i, row):
        # Initialise the object
        obj, mesh = make_mesh(row[self.name_i], self.colour)
        create_emission_node(obj, self.border_colour, 1, 'BorderColour')

        # Construct the vertexes, using the index position of the row as the x iterator, and row values as the y.
        vertexes = [
            (i, float(row[self.isolate]), 0),
            (i, 0, 0),
            (i + 1, 0, 0),
            (i + 1, float(row[self.isolate]), 0)
        ]
        mesh.from_pydata(vertexes, [], [[0, 1, 2, 3]])
        return obj

    def scale_bar(self, obj):
        """Scale the object in y based on assigned value of y_scale"""
        obj.select_set(True)
        bpy.ops.transform.resize(value=(1, self.y_scale, 1))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    def bar_border(self, obj):
        """Create the border for the object"""
        # Inset the border
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.inset(thickness=self.border_width, depth=0)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()

        # Isolate the polygons that are not the interior
        mesh = obj.data
        inner_poly_area = max([face.area for face in mesh.polygons])
        for index, face in enumerate(mesh.polygons):
            if face.area != inner_poly_area:
                face.select = True

        # Assign the second material (the border) to this mesh
        # TODO: ideally we access it by name not index to future proof it
        bpy.ops.object.editmode_toggle()
        bpy.context.object.active_material_index = 1
        bpy.ops.object.material_slot_assign()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()

    def make_name(self, i, row):
        """Make the x axis text"""
        make_text(row[self.name_i], i + 0.5, -1, row[self.name_i], 1, (0, 0, 0, 1), align='CENTER')


if __name__ == '__main__':
    Histogram((r"C:\Users\Samuel\PycharmProjects\ScarletExposure\Figures and Tables\SummaryCsvs",
               r"C:\Users\Samuel\PycharmProjects\ScarletExposure\Figures and Tables\SummaryCsvs\S.csv",
               0, 1, 0.0025, 0.05, (1, 0.058, 0.027, 1), (0.1, 0.1, 0.1, 1), 'Demographics_F'))
