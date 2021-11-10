from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text
from csvObject import CsvObject
import bpy


class Histogram:
    def __init__(self, args):

        write_directory, file_path, name_index, isolate, y_scale, write_name = args

        self.write_directory = write_directory
        self.csv_obj = CsvObject(file_path)
        self.name_i = int(name_index)
        self.isolate = int(isolate)
        self.y_scale = float(y_scale)
        self.write_name = write_name

        self.make_histogram()

        # TODO: Make the y axis text
        # TODO: apply scale of bars
        # TODO: Inset bars, so that we have a line width
        # TODO: Apply the line area a line colour

    def make_histogram(self):
        for i, row in enumerate(self.csv_obj.row_data):
            self.make_bar(i, row)
            self.make_name(i, row)

        # Save the blend file for manual manipulation later
        bpy.ops.wm.save_as_mainfile(filepath=f"{self.write_directory}/{self.write_name}.blend")

    def make_bar(self, i, row):
        """Make the bar for the histogram"""

        # Initialise the object
        obj, mesh = make_mesh(row[self.name_i], (0.1, 0.1, 0.1, 0.1))

        # Construct the vertexes, using the index position of the row as the x iterator, and row values as the y.
        vertexes = [
            (i, float(row[self.isolate]), 0),
            (i, 0, 0),
            (i + 1, 0, 0),
            (i + 1, float(row[self.isolate]), 0)
        ]
        mesh.from_pydata(vertexes, [], [[0, 1, 2, 3]])

        # Scale the object in y based on assigned value of y_scale
        obj.select_set(True)
        bpy.ops.transform.resize(value=(1, self.y_scale, 1))
        bpy.ops.object.select_all(action='DESELECT')

    def make_name(self, i, row):
        """Make the x axis text"""
        make_text(row[self.name_i], i + 0.5, -1, row[self.name_i], 1, (0, 0, 0, 1), align='CENTER')


if __name__ == '__main__':

    Histogram((r"C:\Users\Samuel\PycharmProjects\ScarletExposure\Figures and Tables\SummaryCsvs",
               r"C:\Users\Samuel\PycharmProjects\ScarletExposure\Figures and Tables\SummaryCsvs\S.csv",
               0, 1, 0.0025, 'Demographics_F'))
