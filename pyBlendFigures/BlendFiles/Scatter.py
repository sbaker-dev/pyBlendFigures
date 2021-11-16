# from blendSupports.Meshs.graph_axis import make_graph_axis
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text
# from blendSupports.misc import tuple_convert

from miscSupports import load_json
from csvObject import CsvObject
import sys
import bpy


class Scatter:
    def __init__(self):
        self.scatter_groups = load_json(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Scatter\Test\Test.txt")

        self.label_threshold = 10
        self.name_index = 0
        self.x_index = 1
        self.y_index = 2
        self.ico_scale = 0.05

        for group, points in self.scatter_groups.items():
            vertexes = [(p[self.x_index], p[self.y_index], 0) for p in points]

            obj, mesh = make_mesh(group)
            mesh.from_pydata(vertexes, [], [])

            print(vertexes)

            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, enter_editmode=False, align='WORLD',
                                                  location=(0, 0, 0))
            ico = bpy.context.view_layer.objects.active
            ico.scale = (self.ico_scale, self.ico_scale, self.ico_scale)

            ico.parent = obj
            obj.instance_type = 'VERTS'
            bpy.ops.object.select_all(action='DESELECT')

        # file_path = r"C:\Users\Samuel\PycharmProjects\DeprivationIndex\Code\PheWAS\PheWAS_Results\Python\TS_DS.csv"
        #
        # y_axis_index = 6
        # x_axis_index = 12
        #
        # # Create the coordinates
        # file = CsvObject(file_path, set_columns=True)
        # coordinates = [(float(x), float(y), 0) for x, y in zip(file[x_axis_index], file[y_axis_index])]
        #
        # # Make the points data
        # obj, mesh = make_mesh(f"QQ")
        # mesh.from_pydata(coordinates, [], [])
        #
        # # # Render the QQ points
        # # bpy.context.scene.render.filepath = str(Path(self.write_directory, f"{self.write_name}__POINTS").absolute())
        # # bpy.ops.wm.save_as_mainfile(filepath=f"{self.write_directory}/{self.write_name}__POINTS.blend")
        # # bpy.ops.render.opengl(write_still=True, view_context=True)
        # # self.logger.write(f"Written QQ Points at {terminal_time()}")


if __name__ == '__main__':
    Scatter()