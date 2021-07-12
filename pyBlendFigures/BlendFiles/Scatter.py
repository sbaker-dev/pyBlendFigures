from blendSupports.Meshs.graph_axis import make_graph_axis
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text
from blendSupports.misc import tuple_convert

from csvObject import CsvObject
import sys
import bpy


class Scatter:
    def __init__(self):

        file_path = r"C:\Users\Samuel\PycharmProjects\SR-GWAS\Testing\Output\Scatter.csv"

        y_axis_index = 6
        x_axis_index = 12

        # Create the coordinates
        file = CsvObject(file_path, set_columns=True)
        coordinates = [(float(x), float(y), 0) for x, y in zip(file[x_axis_index], file[y_axis_index])]

        # Make the points data
        obj, mesh = make_mesh(f"QQ")
        mesh.from_pydata(coordinates, [], [])

        # # Render the QQ points
        # bpy.context.scene.render.filepath = str(Path(self.write_directory, f"{self.write_name}__POINTS").absolute())
        # bpy.ops.wm.save_as_mainfile(filepath=f"{self.write_directory}/{self.write_name}__POINTS.blend")
        # bpy.ops.render.opengl(write_still=True, view_context=True)
        # self.logger.write(f"Written QQ Points at {terminal_time()}")

    def _draw_plot(self):
        return


if __name__ == '__main__':
    Scatter()