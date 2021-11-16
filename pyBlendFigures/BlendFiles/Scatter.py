# from blendSupports.Meshs.graph_axis import make_graph_axis
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text
# from blendSupports.misc import tuple_convert

from miscSupports import load_json
from csvObject import CsvObject
import math
import sys
import bpy


class Scatter:
    def __init__(self):
        self.scatter_groups = load_json(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Scatter\Test\Test.txt")

        self.label_threshold = 10
        self.name_index = 0
        self.x_index = 1
        self.y_index = 2
        self.ico_scale = 0.5

        self._y_max = []

        self._make_point_groups()

        print(math.ceil(max(self._y_max)))

    def _make_point_groups(self):
        [self.make_group(group, points) for group, points in self.scatter_groups.items()]

    def make_group(self, group, points):
        obj, x_mid = self.make_vertex_holder(group, points)

        if x_mid != 0:
            make_text(group, x_mid, -6, group, 5, (0.25, 0.25, 0.25, 1), 'CENTER')

        self.link_ico(obj)

    def make_vertex_holder(self, group, points):
        vertexes = [(p[self.x_index], p[self.y_index], 0) for p in points]

        x_points = [p[self.x_index] for p in points]

        obj, mesh = make_mesh(group)
        mesh.from_pydata(vertexes, [], [])

        if len(vertexes) > 0:
            self._y_max.append(max([p[self.y_index] for p in points]))
            return obj, (min(x_points) + max(x_points)) / 2,
        else:
            self._y_max.append(0)
            return obj, 0

    def link_ico(self, obj):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, enter_editmode=False, align='WORLD',
                                              location=(0, 0, 0))
        ico = bpy.context.view_layer.objects.active
        ico.scale = (self.ico_scale, self.ico_scale, self.ico_scale)
        ico.parent = obj
        obj.instance_type = 'VERTS'
        bpy.ops.object.select_all(action='DESELECT')


if __name__ == '__main__':
    Scatter()