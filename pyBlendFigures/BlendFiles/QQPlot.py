from blendSupports.Renders.render import open_gl_render, render_scene
from blendSupports.Meshs.graph_axis import make_graph_axis
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text

from miscSupports import open_setter, decode_line, terminal_time, FileOut, tuple_convert
from pathlib import Path
import numpy as np
import math
import sys
import bpy


class QQPlot:
    def __init__(self, args):

        write_directory, summary_file, p_value_index, write_name, log_transform, set_bounds, line_width, axis_colour, \
            camera_position, camera_scale, x_res, y_res = args

        # Camera setup
        self.camera_position = camera_position
        self.camera_scale = camera_scale
        self.x_res = x_res
        self.y_res = y_res

        # Setup the file for the process
        self.write_directory = write_directory
        self.summary_file = Path(summary_file)
        self.zipped = self.summary_file.suffix == ".gz"
        self.write_name = write_name

        # Set the logger
        self.logger = FileOut(self.write_directory, f"{self.write_name}", "log", True)
        self.logger.write(f"Starting {self.summary_file.stem}: {terminal_time()}\n")

        # Draw the QQ plot
        x_values, y_values = self._draw_qq(int(p_value_index), bool(log_transform))

        # Draw the Axis
        self._axis(x_values, y_values, set_bounds, float(line_width), tuple_convert(axis_colour))

    def _draw_qq(self, p_value_index, log_transform):
        # Extract the sorted -log10 values for the y values
        y_values = self._y_values_from_p(p_value_index, log_transform)

        # Create the x values as a vector between -log(1) and -log(1/N) for N values
        x_values = sorted([-math.log10(v) for v in np.linspace(1, 1 / len(y_values), len(y_values))])

        # Create the vertexes from the x and y, hold z as 0
        vertexes = [(x, y, 0) for x, y in zip(x_values, y_values)]

        # Make the points data
        obj, mesh = make_mesh(f"QQ")
        mesh.from_pydata(vertexes, [], [])

        # Render the QQ points
        open_gl_render(self.camera_position, self.write_directory, f"{self.write_name}__POINTS", self.x_res, self.y_res,
                       camera_scale=self.camera_scale)
        self.logger.write(f"Written QQ Points at {terminal_time()}")

        # Return the bounds for the axis
        return x_values, y_values

    def _y_values_from_p(self, p_value_index, log_transform):
        """
        Create the y values from the -log 10 p values.

        :param p_value_index: The index of the p value column in the summary stat file
        :type p_value_index: int

        :param log_transform: If the p value is not in a -log 10 then it needs to be converted, otherwise this can be
            False
        :type log_transform: bool

        :return: The sorted list of -log 10 p values
        :rtype: list
        """

        log_v = []
        with open_setter(self.summary_file)(self.summary_file) as file:

            # Skip the header
            file.readline()

            for index, line_byte in enumerate(file):
                if index % 100000 == 0:
                    self.logger.write(f"Processed {index} Lines")

                # Extract the p value
                p_value = float(decode_line(line_byte, self.zipped)[p_value_index])

                # Log transform the p value if required
                if log_transform:
                    p_value = -math.log10(p_value)
                log_v.append(p_value)

        # Sort the values from smallest to largest
        return sorted(log_v)

    def _axis(self, x_values, y_values, set_bounds, line_width, axis_colour):

        # Make the 45% line from the min of the max
        end_point = min([max(y_values), max(x_values)])
        line, line_mesh = make_mesh("Line", axis_colour)
        line_mesh.from_pydata([(0, 0, 0), (end_point, end_point, 0)], [(0, 1)], [])

        # Turn line to curve, add width equal to line_width
        line.select_set(True)
        bpy.ops.object.convert(target='CURVE')
        bpy.context.object.data.bevel_resolution = 0
        bpy.context.object.data.bevel_depth = line_width

        # Create the bounds
        x_bound = max(x_values)
        y_bound = max(y_values)

        # define the Bound of the axis
        if set_bounds != "None":
            x, y = tuple_convert(set_bounds)
            if (x_bound > x) or (y_bound > y):
                x = max([x_bound, x])
                y = max([y_bound, y])
                self.logger.write(F"WARNING: Set Bound is smaller than p value's, defaulting to native bound")
        else:
            x, y = x_bound, y_bound

        # Make the graphs axis
        make_graph_axis(axis_colour, x, y, line_width, 0.0)

        # TODO see if we can generalise the axis for make graph axis to also include the annotation
        # Label the x axis
        make_text("Theoretical -log10", math.floor(x) / 2, -1, "Theoretical -log10", 0.5, axis_colour, "CENTER")
        for i in range(math.floor(x)):
            make_text(f"{i}", i + 0.5, -0.5, f"{i + 1}", 0.5, axis_colour, "CENTER")

        # Label the y axis
        make_text("Observed -log 10", -1, math.floor(y) / 2, "Observed -log 10", 0.5, axis_colour, "CENTER")

        # Y axis needs to be rotated
        obj = bpy.data.objects["Observed -log 10"]
        obj.select_set(True)
        bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 use_proportional_connected=False, use_proportional_projected=False)

        for i in range(math.floor(y)):
            make_text(f"log{i}", -0.5, i + 0.5, f"{i + 1}", 0.5, axis_colour, "CENTER")

        # Render the scene
        render_scene(self.camera_position, self.write_directory, f"{self.write_name}__AXIS.png", "BLENDER_EEVEE",
                     self.x_res, self.y_res, camera_scale=self.camera_scale)
        self.logger.write(f"Written the AXIS out at {terminal_time()}")


if __name__ == '__main__':
    QQPlot(sys.argv[len(sys.argv) - 1].split("__"))
