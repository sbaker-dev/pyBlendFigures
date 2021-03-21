import csv
import bpy
import bmesh
import statistics


class ForestLine:
    def __init__(self, row):
        self.var_name, self.coef, self.coef_plot, self.lb, self.lb_plot, self.ub, self.ub_plot = row

        print(self.var_name, self.coef, self.coef_plot, self.lb, self.lb_plot, self.ub, self.ub_plot)

    def make_line(self, height_total, height_iter, scale=0.2):
        """
        This will make the forest line via the standardised lower and upper bounds.

        :param height_total: Total current height, starts at 0 and is iterated each time a row is added
        :type height_total: float

        :param height_iter: The iterable amount specified by the user, defaults to 0.5
        :type height_iter: float

        :param scale: How much to scale on y, defaults to 0.2
        :type scale: float

        :return: The object name of the created element
        :rtype: str
        """
        # Make the block
        mesh = bpy.data.meshes.new(self.var_name)  # add the new mesh
        obj = bpy.data.objects.new(mesh.name, mesh)
        col = bpy.data.collections.get("Collection")
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        # 4 verts made with XYZ coords
        verts = [(float(self.ub_plot), height_total, 0.0),
                 (float(self.ub_plot), height_total - height_iter, 0.0),
                 (float(self.lb_plot), height_total - height_iter, 0.0),
                 (float(self.lb_plot), height_total, 0.0)]
        edges = []
        faces = [[0, 1, 2, 3]]
        mesh.from_pydata(verts, edges, faces)

        # Scale it, by default 80%, on y to get a line centered in the block
        bpy.data.objects[obj.name].select_set(True)
        bpy.ops.object.editmode_toggle()
        bpy.ops.transform.resize(value=(1, scale, 1), orient_type='GLOBAL')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        return obj.name

    def make_coefficient(self, object_name, radius):
        """
        Create a coefficient blip for this line

        :param object_name: Line object's name
        :type object_name: str

        :param radius: Radius of the circle
        :type radius: float

        :return: Nothing, create circle then stop.
        :rtype: None
        """

        # Get the middle y position of the line via the mean of its y positions
        y_mean = statistics.mean([box_cord[1] for box_cord in bpy.data.objects[object_name].bound_box])

        # Create the primitive circle
        bpy.ops.mesh.primitive_circle_add(
            enter_editmode=True, align='WORLD', location=(float(self.coef_plot), y_mean, 0.1), radius=radius)
        bpy.context.object.name = f"{object_name}_coef"

        # Circle to default to edit mode, use this to fill the circle in, then toggle out and deselect.
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')


def isolate_rows():
    with open(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ScarletAverage1_TEMP.csv", "r",
              encoding="utf-8-sig") as csv_file:
        # Isolate the rows from the file
        return [row for i, row in enumerate(csv.reader(csv_file)) if i > 0]


def set_bound(row_info):
    min_bound = max([abs(float(row[-1])) for i, row in enumerate(row_info) if i > 0])
    max_bound = max([abs(float(row[-2])) for i, row in enumerate(row_info) if i > 0])
    return max([min_bound, max_bound]) * 2


def set_values(value, rounding_value):
    set_rounding = round(float(value), rounding_value)
    if set_rounding < 0:
        rounding_value += 3
    else:
        rounding_value += 2

    set_rounding = str(set_rounding)
    if len(set_rounding) == rounding_value:
        return set_rounding
    else:
        return set_rounding + "".join(["0" for _ in range(rounding_value - len(set_rounding))])


if __name__ == '__main__':

    csv_rows = isolate_rows()

    # bound = set_bound(csv_rows)
    height_iterator = 0.04  # Expose
    height_max = 0
    # spacing = height_iter * 2
    coefficient_radius = 0.007
    # rounder = 3
    # cat_spacing = 0.75
    # var_spacing = 1
    # numeric_spacing = 0.8

    # For each row represents a line we wish to plot
    for row in csv_rows:

        # Create an object to construct the necessary components
        forest_obj = ForestLine(row)

        # Create the line
        current_name = forest_obj.make_line(height_max, height_iterator)
        forest_obj.make_coefficient(current_name, coefficient_radius)
        height_max -= height_iterator

    print("")

    # # Group rows
    # groupings = {row[0]: [] for row in csv_rows}
    # for category in groupings.keys():
    #     for row in csv_rows:
    #         if row[0] == category:
    #             groupings[category].append(row[1:])
    #
    # #todo we need ot make the axis
    #
    # # For each category
    # for index, (cat, cat_row) in enumerate(groupings.items()):
    #
    #     category_y = []
    #
    #     for i, row in enumerate(cat_row, 1):
    #         var_name, coef, se, lb, ub = row
    #
    #
    #

    #
    #         # Set the confident / numeric output
    #         bpy.ops.object.text_add(location=(bound * numeric_spacing, y_mean, 0))
    #         ob = bpy.context.object
    #         ob.data.body = f"{set_values(coef, rounder)} ({set_values(lb, rounder)}; {set_values(ub, rounder)})"
    #         bpy.ops.transform.resize(value=(height_iter, height_iter, height_iter))
    #         bpy.ops.object.select_all(action='DESELECT')
    #
    #         # Set the variable name
    #         bpy.ops.object.text_add(location=(-bound * var_spacing, y_mean, 0))
    #         ob = bpy.context.object
    #         ob.data.body = var_name
    #         bpy.ops.transform.resize(value=(height_iter, height_iter, height_iter))
    #         bpy.ops.object.select_all(action='DESELECT')
    #
    #         category_y.append(y_mean)
    #         height_total -= height_iter
    #
    #     # Add the category
    #     bpy.ops.object.text_add(location=((-bound * 2) * cat_spacing, min(category_y), 0))
    #     ob = bpy.context.object
    #     ob.data.body = cat
    #     bpy.ops.transform.resize(value=(height_iter * 2, height_iter * 2, height_iter * 2))
    #     bpy.ops.object.select_all(action='DESELECT')
    #     height_total -= spacing
    #todo set dimensions
    # todo create a base forest blend
print("")