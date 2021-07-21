from blendSupports.Supports.collection_cleanup import collection_cleanup
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text

from miscSupports import load_yaml
import bpy


class PrismaPlot:
    def __init__(self):
        self._args = load_yaml(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\PRISMA\Test3.yaml")

        self.spacing = 1
        self.line_width = 0.2
        self.padding = 0.4
        self.segments = 5
        self.profile = 0.5

        self.links = self._args["Links"]
        self.positions = self._args["Positions"]
        self.col_count = len(self.links["Columns"])
        self.row_count = len(self.links["Rows"])

        self.widths, self.dimensions = self._set_dimensions()
        print(self.dimensions)

        previous_height = 0
        for row_i in range(self.row_count):
            for col_i in range(self.col_count):
                try:

                    # Isolate the name and position of this text object
                    name = f"{col_i}-{row_i}"
                    position = self.positions[name]
                    print(name)

                    # Set the width, which is the x position, relative to other columns of this row
                    width = sum([self.widths[str(i - 1)] for i in range(col_i + 1)])
                    if col_i != 0:
                        width += self.spacing

                    # Create the text object and set its origin to geometry
                    obj = make_text(name, width, previous_height, position["Text"], 1, (255, 255, 255, 255),
                                    align="CENTER")
                    obj.select_set(True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

                    # Isolate the texts center from location and width and height from dimensions
                    x, y, _ = obj.location / 2
                    x_d, y_d, _ = obj.dimensions / 2
                    obj.select_set(False)

                    # Create the bounding box
                    vert_list = [((x - x_d) - self.line_width, (y + y_d) + self.line_width, -0.1),
                                 ((x - x_d) - self.line_width, (y - y_d) - self.line_width, -0.1),
                                 ((x + x_d) + self.line_width, (y - y_d) - self.line_width, -0.1),
                                 ((x + x_d) + self.line_width, (y + y_d) + self.line_width, -0.1)]
                    box_obj, mesh = make_mesh(name, (255, 255, 255, 255))
                    mesh.from_pydata(vert_list, [], [[0, 1, 2, 3]])

                    # Set the boxes origin to geometry
                    box_obj.select_set(True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                    box_obj.location = obj.location

                    # Set and then remove interior face
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.inset(thickness=self.padding * self.line_width, depth=0)
                    bpy.ops.mesh.delete(type='FACE')
                    bpy.ops.object.editmode_toggle()

                    # Set the profile of the object via a bevel
                    bpy.ops.object.modifier_add(type='BEVEL')
                    bpy.context.object.modifiers["Bevel"].segments = self.segments
                    bpy.context.object.modifiers["Bevel"].profile = self.profile
                    box_obj.select_set(False)

                    previous_height += self.dimensions[name][1]
                except KeyError:
                    pass

    def _set_dimensions(self):

        widths = {"-1": 0}
        dimension_dict = {}
        for i in range(self.col_count):
            dimensions = []

            for name, position in self.positions.items():

                col_id, row_id = name.split("-")
                if col_id == str(i):
                    obj = make_text(name, 0, 0, position["Text"], 1, (255, 255, 255, 255), align="CENTER")
                    dimensions.append(obj.dimensions)

                    x, y, z = obj.dimensions
                    dimension_dict[name] = [x, y, z]

            widths[str(i)] = max([x for x, y, z in dimensions])

        collection_cleanup("Collection")
        return widths, dimension_dict


PrismaPlot()
