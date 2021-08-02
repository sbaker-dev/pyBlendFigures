from blendSupports.Nodes.emission_node import create_emission_node
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text
from blendSupports.Renders import render_scene
from blendSupports.misc import set_values

from miscSupports import normalisation_min_max, flatten, chunk_list, tuple_convert
from csvObject import CsvObject
import statistics
import logging
import sys
import bpy


class ForestPlot:
    def __init__(self, args):
        write_directory, csv_path, image_name, height_iter, coefficient_radius, value_title, var_bound, ci_bound, \
            rounder, text_colour, axis_width, axis_label, axis_colour, y_scale, x_res, y_res, image_type, \
            camera_scale, camera_position = args

        # Convert and create attributes for values where required
        self.csv_path = csv_path
        self.height_iter = float(height_iter)
        self.coefficient_radius = float(coefficient_radius)
        self.rounder = int(rounder)
        self.text_colour = tuple_convert(text_colour)
        self.y_scale = float(y_scale)
        self.var_bound = float(var_bound)
        self.ci_bound = float(ci_bound)
        self.value_title = value_title
        self.axis_width = float(axis_width)
        self.axis_label = axis_label
        self.axis_colour = tuple_convert(axis_colour)

        # Isolate the row data and create normalised position data so we can construct the elements
        self.line_rows, self.axis_position = self._position_values()

        # Create the lines of the forest plot, logging the total height and the bound values for the axis
        self.height_max = 0
        self.bound_values = []
        self._create_lines()

        # Create the axis and the labels for it
        self._create_axis()

        # Render the scene
        render_scene(camera_position, write_directory, image_name, x_resolution=x_res, y_resolution=y_res,
                     camera_scale=camera_scale)

    def _create_lines(self):

        for row in self.line_rows:
            # Create an object to construct the necessary components
            forest_obj = ForestLine(row, self.coefficient_radius, self.rounder, self.text_colour)

            if forest_obj.var_name == "#Delete":
                self.height_max -= self.height_iter

            else:
                self.bound_values = self.bound_values + [float(forest_obj.lb), float(forest_obj.ub)]

                # Create the line
                current_name = forest_obj.make_line(self.height_max, self.height_iter, self.y_scale)
                y_mean = forest_obj.make_coefficient(current_name)

                # Set the variable name
                make_text(f"{forest_obj.var_name}_var_name", -self.var_bound, y_mean, forest_obj.var_name,
                          self.height_iter, self.text_colour, "LEFT")

                # Create the numeric string
                numeric = f"{set_values(forest_obj.coef, self.rounder)} ({set_values(forest_obj.lb, self.rounder)}; " \
                          f"{set_values(forest_obj.ub, self.rounder)})"
                make_text(f"{forest_obj.var_name}_CI", 1 + self.ci_bound, y_mean, numeric, self.height_iter,
                          self.text_colour)

                self.height_max -= self.height_iter

    def _position_values(self):
        csv_data = CsvObject(self.csv_path, [str, float, float, float])

        if csv_data.row_length != 4:
            msg = f"Csv file should contain phenotype, coefficient, lower bound, upper bound yet found" \
                  f" {csv_data.row_length} rows"
            logging.error(msg)
            raise IndexError(msg)

        # Normalise the values for the table plot with 0 added so we know where to draw the axis
        numerical_values = flatten([row[1:] for row in csv_data.row_data])
        normalised_value_list = normalisation_min_max(numerical_values + [0])

        # Isolate the axis and normal array, then chunk the normal array back into the coefficient, lower bound and
        # upper bound
        x_axis_point = normalised_value_list[-1]
        normal_array = chunk_list(normalised_value_list[:-1], 3)

        # Format the rows so we have actual - positional values for each numeric
        formatted_rows = []
        for row, normalised in zip(csv_data.row_data, normal_array):
            formatted_rows.append(flatten([[row[0]]] + [[row[i+1], normalised[i]] for i in range(3)]))

        # Isolate the maximum phenotype name so we can justify our text accordingly
        # name_length_max = max([len(row[0]) for row in csv_data])
        return formatted_rows, x_axis_point

    def _create_axis(self):
        # Make y axis from the min and max values of the standardised rows
        self._make_axis()
        self.height_max -= self.height_iter

        # Label left an right most columns
        make_text("Phenotype", -self.var_bound, self.height_iter, "Phenotype", self.height_iter, self.text_colour)
        make_text(self.value_title, 1 + self.ci_bound, self.height_iter, self.value_title, self.height_iter,
                  self.text_colour)

        # Add values based on a range between the min and max equally divided
        make_text("Min_Bound", 0, self.height_max, set_values(min(self.bound_values), 2), self.height_iter,
                  self.text_colour)
        make_text("Max_Bound", 1, self.height_max, str(round(max(self.bound_values), 2)), self.height_iter,
                  self.text_colour,
                  "RIGHT")
        make_text("Mid_Point", self.axis_position, self.height_max, str(0.0), self.height_iter, self.text_colour,
                  "CENTER")

        # # Add the x axis label
        make_text("Axis Label", self.axis_position, self.height_max - self.height_iter, self.axis_label,
                  self.height_iter, self.text_colour, align="CENTER")

    def _make_axis(self):

        obj, mesh = make_mesh("Axis", self.axis_colour)

        # 4 verts made with XYZ coords
        verts = [
            # Vertical axis
            (self.axis_width / 2 + self.axis_position, 0, -self.axis_width),
            (self.axis_width / 2 + self.axis_position, self.height_max, -self.axis_width),
            (-self.axis_width / 2 + self.axis_position, self.height_max, -self.axis_width),
            (-self.axis_width / 2 + self.axis_position, 0, -self.axis_width),

            # Horizontal axis
            (1, self.height_max, -self.axis_width),
            (1, self.height_max - self.axis_width, -self.axis_width),
            (0, self.height_max - self.axis_width, -self.axis_width),
            (0, self.height_max, -self.axis_width)
        ]
        edges = []
        faces = [[0, 1, 2, 3], [4, 5, 6, 7]]
        mesh.from_pydata(verts, edges, faces)
        bpy.ops.object.select_all(action='DESELECT')


class ForestLine:
    def __init__(self, row_values, radius_of_coefficient, rounding, object_colour):
        # Set the values from the row that was read in via the temp csv
        self.var_name, self.coef, self.coef_plot, self.lb, self.lb_plot, self.ub, self.ub_plot = row_values

        # Set the values required to create the blend objects
        self._radius = radius_of_coefficient
        self._round = rounding
        self._colour = object_colour

    def make_line(self, height_total, height_iterator, scale=0.1):
        """
        This will make the forest line via the standardised lower and upper bounds.

        :param height_total: Total current height, starts at 0 and is iterated each time a row is added
        :type height_total: float

        :param height_iterator: The iterable amount specified by the user, defaults to 0.5
        :type height_iterator: float

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
                 (float(self.ub_plot), height_total - height_iterator, 0.0),
                 (float(self.lb_plot), height_total - height_iterator, 0.0),
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
        bpy.context.object.name = f"{object_name}_coefficient"
        obj = bpy.context.object
        create_emission_node(obj, self._colour)
        bpy.ops.object.select_all(action='DESELECT')

        # Return the y mean for positioning the text
        return y_mean_val


if __name__ == '__main__':
    ForestPlot(sys.argv[len(sys.argv) - 1].split("__"))
