import csv
import bpy
import bmesh
import statistics


class ForestLine:
    def __init__(self, row_values, radius_of_coefficient, rounding, object_colour):

        # Set the values from the row that was read in via the temp csv
        self.var_name, self.coef, self.coef_plot, self.lb, self.lb_plot, self.ub, self.ub_plot = row_values

        # Set the values required to create the blend objects
        self._radius = radius_of_coefficient
        self._round = rounding
        self._colour = object_colour

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
        create_emission_node(obj, self._colour)
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

    def make_coefficient(self, object_name):
        """
        Create a coefficient blip for this line

        :param object_name: Line object's name
        :type object_name: str

        :return: The mid point of the line
        :rtype: float
        """

        # Get the middle y position of the line via the mean of its y positions
        y_mean_val = statistics.mean([box_cord[1] for box_cord in bpy.data.objects[object_name].bound_box])

        # Create the primitive circle
        bpy.ops.mesh.primitive_circle_add(
            enter_editmode=True, align='WORLD', location=(float(self.coef_plot), y_mean_val, 0.1), radius=self._radius)

        # Circle to default to edit mode, use this to fill the circle in.
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.editmode_toggle()

        # Set the name and material of the circle, then toggle out and deselect.
        bpy.context.object.name = f"{object_name}_var_name"
        obj = bpy.context.object
        create_emission_node(obj, self._colour)
        bpy.ops.object.select_all(action='DESELECT')

        # Return the y mean for positioning the text
        return y_mean_val


def isolate_rows(path_to_csv):
    """
    Isolate the row content from the csv file provided

    :param path_to_csv: The path to the csv file to load
    :type path_to_csv: str

    :return: The row content to use for the construction, removes the first row due to presumed headers
    :rtype: list
    """
    with open(path_to_csv, "r", encoding="utf-8-sig") as csv_file:
        return [r for i, r in enumerate(csv.reader(csv_file)) if i > 0]


def make_text(object_name, bound, y_mean_val, text, height_iter, object_colour):
    """
    Creates a text object starting at x 'bound' and at y 'y_mean_val' displaying 'text'. It is scaled to be equal to the
    objects via the 'height_iter'

    :param object_name: The name of the object
    :type object_name: str

    :param bound: Starting x position
    :type bound: float

    :param y_mean_val: Y position
    :type y_mean_val: float

    :param text: Text to display
    :type text: str

    :param height_iter: Scaling about to make text relative to all other components
    :type height_iter: float

    :param object_colour: RGBA colour of the object
    :type object_colour: (int, int, int, int)

    :return: Nothing, make the text object then stop
    """

    # Create the text object
    bpy.ops.object.text_add(location=(bound, y_mean_val, 0))

    # Set its name
    obj = bpy.context.object
    obj.data.body = text
    create_emission_node(obj, object_colour)
    bpy.context.object.name = f"{object_name}_var_name"

    # Scale it relative to all other elements
    bpy.ops.transform.resize(value=(height_iter, height_iter, height_iter))
    bpy.ops.object.select_all(action='DESELECT')


def set_values(value, rounding_value):
    """
    Rounding may lead to values not being the right length when converted to strings. This formats them

    :param value: Value to turn into a string
    :type value: float | int

    :param rounding_value: Rounding value target
    :type rounding_value: int

    :return: string representation of the rounded 'value', where rounding is set by rounding_value
    :rtype: str
    """
    set_rounding = round(float(value), rounding_value)
    if set_rounding < 0:
        rounding_value += 3
        set_rounding = str(set_rounding)
    else:
        rounding_value += 2
        set_rounding = f" {set_rounding}"

    if len(set_rounding) == rounding_value:
        return set_rounding
    else:
        return set_rounding + "".join(["0" for _ in range(rounding_value - len(set_rounding))])


def create_emission_node(obj, colour, strength=1.0):
    """
    Create an emission node for this object

    Source: https://blender.stackexchange.com/questions/23436/control-cycles-material-nodes-and-material-
            properties-in-python


    :param obj: The current blender object

    :param colour: RGBA colour
    :type colour: (int, int, int, int)

    :param strength: Intensity of the emission node
    :type strength: float

    :return: Nothing, make the emission node then stop
    :rtype: None
    """

    # Test if material exists, If it does not exist, create it:
    mat_name = obj.name
    mat = (bpy.data.materials.get(mat_name) or
           bpy.data.materials.new(mat_name))

    # Enable 'Use nodes':
    mat.use_nodes = True

    # clear all nodes to start clean
    nodes = mat.node_tree.nodes
    nodes.clear()

    # create emission node
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_emission.inputs[0].default_value = colour
    node_emission.inputs[1].default_value = strength
    node_emission.location = 0, 0

    # create output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = 400, 0

    node = nodes.new('ShaderNodeBsdfDiffuse')
    node.location = (100, 100)

    # link nodes
    links = mat.node_tree.links
    links.new(node_emission.outputs[0], node_output.inputs[0])

    obj.data.materials.append(mat)


if __name__ == '__main__':

    csv_path = r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ScarletAverage1_TEMP.csv"
    csv_rows = isolate_rows(csv_path)

    height_max = 0
    height_iterator = 0.04  # Expose

    coefficient_radius = 0.007  # Expose
    var_bound = -0.8  # Defaults to 1, Expose
    numeric_bound = 0.8  # Defaults to 1, expose
    rounder = 3  # Defaults to 3, Expose
    text_colour = (0, 0, 0, 0)

    x_res = 2160
    y_res = 2160

    # For each row represents a line we wish to plot
    variable_names = []
    for row in csv_rows:

        # Create an object to construct the necessary components
        forest_obj = ForestLine(row, coefficient_radius, rounder, text_colour)
        variable_names.append(forest_obj.var_name)

        # Create the line
        current_name = forest_obj.make_line(height_max, height_iterator)
        y_mean = forest_obj.make_coefficient(current_name)

        # Set the variable name
        make_text(forest_obj.var_name, var_bound, y_mean, forest_obj.var_name, height_iterator, text_colour)

        # Create the numeric string
        numeric = f"{set_values(forest_obj.coef, rounder)} ({set_values(forest_obj.ub, rounder)}; " \
                  f"{set_values(forest_obj.lb, rounder)})"
        make_text(forest_obj.var_name, numeric_bound, y_mean, numeric, height_iterator, text_colour)

        height_max -= height_iterator

    # TODO
    # Make y axis from the min and max values of the standardised rows
    # make dividing line
    # make title

    # Set the output resolution
    bpy.context.scene.render.resolution_x = x_res
    bpy.context.scene.render.resolution_y = y_res

    # Render the scene
    bpy.context.scene.render.filepath = r'C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\TTT.png'
    bpy.context.scene.eevee.use_gtao = True
    bpy.context.scene.render.film_transparent = True
    bpy.ops.render.render(write_still=True)
