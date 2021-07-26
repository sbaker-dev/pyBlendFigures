from blendSupports.Supports.collection_cleanup import collection_cleanup
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text

from miscSupports import load_yaml, chunk_list, flatten
import bpy


class PrismaPlot:
    def __init__(self):
        self._args = load_yaml(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\PRISMA\Test3.yaml")

        self.spacing = 1
        self.line_width = 0.2
        self.padding = 0.4
        self.segments = 5
        self.profile = 0.5
        self.text_colour = (0, 0, 0, 1)
        self.box_colour = (0, 0, 0, 1)

        self.links = self._args["Links"]
        self.positions = self._args["Positions"]
        self.col_count = len(self.links["Columns"])
        self.row_count = len(self.links["Rows"])

        self.widths, self.dimensions = self._set_dimensions()
        self.box_names = []

        # Create the text and text boxes
        self._create_text_boxes()

        # Create the center line and the links to the center line from the sides
        self._create_center_line()
        self._create_links()

    def _set_dimensions(self):

        widths = {"-1": 0}
        dimension_dict = {}
        for i in range(self.col_count):
            dimensions = []

            for name, position in self.positions.items():

                col_id, row_id = name.split("-")
                if col_id == str(i):
                    obj = make_text(name, 0, 0, position["Text"], 1, self.text_colour, align="CENTER")
                    dimensions.append(obj.dimensions)

                    x, y, z = obj.dimensions
                    dimension_dict[name] = [x, y, z]

            widths[str(i)] = max([x for x, y, z in dimensions])

        collection_cleanup("Collection")
        return widths, dimension_dict

    def _create_text_boxes(self):
        previous_height = 0
        for row_i in range(self.row_count):
            for col_i in range(self.col_count):
                try:

                    # Isolate the name and position of this text object
                    name = f"{col_i}-{row_i}"
                    position = self.positions[name]
                    print(name)

                    self._make_text_and_box(name, col_i, position, previous_height)
                    previous_height -= self.dimensions[name][1]

                except KeyError:
                    pass

    def _make_text_and_box(self, name, col_i, position, previous_height):
        # Set the width, which is the x position, relative to other columns of this row
        width = sum([self.widths[str(i - 1)] for i in range(col_i + 1)])
        if col_i != 0:
            width += self.spacing

        # Create the text object and set its origin to geometry
        obj = make_text(name, width, previous_height, position["Text"], 1, self.text_colour,
                        align="CENTER")
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        # Isolate the texts center from location and width and height from dimensions
        x, y, _ = obj.location / 2
        x_d, y_d, _ = obj.dimensions / 2
        obj.select_set(False)

        self._make_bounding_box(x, y, x_d, y_d, name, obj)

    def _make_bounding_box(self, x, y, x_d, y_d, name, obj):
        # Create the bounding box
        vert_list = [((x - x_d) - self.line_width, (y + y_d) + self.line_width, -0.1),
                     ((x - x_d) - self.line_width, (y - y_d) - self.line_width, -0.1),
                     ((x + x_d) + self.line_width, (y - y_d) - self.line_width, -0.1),
                     ((x + x_d) + self.line_width, (y + y_d) + self.line_width, -0.1)]
        box_obj, mesh = make_mesh(f"{name}_box", self.box_colour)
        mesh.from_pydata(vert_list, [], [[0, 1, 2, 3]])
        self.box_names.append(box_obj.name)

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

    def _create_center_line(self):

        # Isolate the center boxes for the center line
        center_line = [box for box in self.box_names if box.split("-")[0] == "0"]

        # Select the center line objects and then duplicate and merge them to create the lines
        for line in center_line:
            obj = bpy.data.objects[line]
            obj.select_set(True)

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
        bpy.ops.object.join()

        # Select the temp object, then chunk the y coords of the verts into 8s due to the inset face
        temp_obj = bpy.context.selected_objects[0]
        cords = chunk_list(sorted([v.co[1] for v in temp_obj.data.vertices]), 8)

        # Create the vert list
        vert_list = []
        for i, v in enumerate(cords):
            if i > 0:
                vert_list.append([(0 - (self.line_width / 2), max(cords[i - 1]), -self.line_width),
                                  (0 - (self.line_width / 2), min(v), -self.line_width),
                                  (0 + (self.line_width / 2), min(v), -self.line_width),
                                  (0 + (self.line_width / 2), max(cords[i - 1]), -self.line_width)])

        # Create the center line object, set the origin to the location of the temp object then delete it
        face_list = chunk_list([i for i in range(len(vert_list) * 4)], len(vert_list))
        box_obj, mesh = make_mesh("TestJoin", self.box_colour)
        mesh.from_pydata(flatten(vert_list), [], face_list)
        box_obj.location = temp_obj.location
        bpy.ops.object.delete()

    def _create_links(self):

        # Select the second column
        join_lines = [box for box in self.box_names if box.split("-")[0] == "1"]

        # For each require line
        for line in join_lines:

            # Create the selection, and set them mid point y to be the locations y.
            # Set x bound to be location x - min of local x from center
            obj = bpy.data.objects[line]
            line_y = obj.location[1]
            line_x = obj.location[0] + min([v.co[0] for v in obj.data.vertices])

            # Create the horizontal lines for this required link
            vert_list = [(0, line_y + (self.line_width / 2), -self.line_width),
                         (0, line_y - (self.line_width / 2), -self.line_width),
                         (line_x, line_y - (self.line_width / 2), -self.line_width),
                         (line_x, line_y + (self.line_width / 2), -self.line_width)]
            box_obj, mesh = make_mesh(f"{obj.name}_link", self.box_colour)
            mesh.from_pydata(vert_list, [], [[0, 1, 2, 3]])


PrismaPlot()
