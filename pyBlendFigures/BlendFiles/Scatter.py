from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text

from miscSupports import load_json, tuple_convert
import math
import bpy


class Scatter:
    def __init__(self, args):

        load_path, label_threshold, name_index, x_index, y_index, ico_scale, text_scale, label_scale, text_colour = args

        self.scatter_groups = load_json(load_path)

        self.label_threshold = float(label_threshold)
        self.name_index = int(name_index)
        self.x_index = int(x_index)
        self.y_index = int(y_index)
        self.ico_scale = (float(ico_scale))
        self._text_scale = float(text_scale)
        self._label_scale = float(label_scale)
        self._text_colour = tuple_convert(text_colour)

        self._y_max = []
        self._make_point_groups()
        self.make_y_axis()

    def _make_point_groups(self):
        [self.make_group(group, points) for group, points in self.scatter_groups.items()]

    def make_group(self, group, points):
        print(group)
        obj, x_mid = self.make_vertex_holder(group, points)

        if x_mid != 0:
            make_text(group, x_mid, -(self._text_scale + 1), group, self._text_scale, self._text_colour, 'CENTER')

        self.link_ico(obj)

    def make_vertex_holder(self, group, points):
        vertexes = [(p[self.x_index], p[self.y_index], 0) for p in points]

        x_points = [p[self.x_index] for p in points]

        obj, mesh = make_mesh(group)
        mesh.from_pydata(vertexes, [], [])

        if len(vertexes) > 0:
            y_points = [p[self.y_index] for p in points]
            self._y_max.append(max(y_points))
            [self.label_points(points, x_points, i, y) for i, y in enumerate(y_points) if y > self.label_threshold]
            return obj, (min(x_points) + max(x_points)) / 2,
        else:
            self._y_max.append(0)
            return obj, 0

    def label_points(self, points, x_points, i, y):
        name = points[i][self.name_index]
        make_text(name, x_points[i] + (2 * self.ico_scale), y, name, self._label_scale, self._text_colour)

    def link_ico(self, obj):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, enter_editmode=False, align='WORLD',
                                              location=(0, 0, 0))
        ico = bpy.context.view_layer.objects.active
        ico.scale = (self.ico_scale, self.ico_scale, self.ico_scale)
        ico.parent = obj
        obj.instance_type = 'VERTS'
        bpy.ops.object.select_all(action='DESELECT')

    def make_y_axis(self):
        iterator = math.ceil(max(self._y_max)) / 10
        for i in range(1, 11):
            make_text(str(iterator * i), -(self._text_scale + 1), iterator * i, str(round(iterator * i, 2)),
                      self._text_scale, self._text_colour, 'RIGHT')


if __name__ == '__main__':

    arg_list = [r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Scatter\Test\Test.txt",
                15, 0, 1, 2, 0.5, 5, 3, (0.25, 0.25, 0.25, 1)]
    Scatter(arg_list)
