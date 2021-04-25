from pyBlendFigures.figure_logic.manhattan_plot import create_manhattan_plot

from miscSupports import validate_path, directory_iterator
from pathlib import Path
import subprocess


class BlendFigure:
    def __init__(self, blender_path, working_directory):

        self._blend_path = str(validate_path(blender_path).absolute())
        self._base_file = str(Path(Path(__file__).parent, "Base.blend").absolute())
        self._blend_scripts = Path(Path(__file__).parent.parent, "BlendFiles").absolute()
        self._working_dir = str(validate_path(working_directory).absolute())

    def forest_plot(self, csv_path, image_name, height_iteration, coefficient_radius, value_title,
                    variable_bound=1.0, ci_bound=0.1, rounder=3, text_colour="Black", axis_width=0.005,
                    axis_label="X_Axis", axis_colour="Dark_Grey", y_scale=0.1, x_resolution=1080,
                    y_resolution=1080, image_type="png", camera_scale=4):
        """
        Will create a forest plot

        :param csv_path: Path to csv data containing four columns of phenotype, coefficient, lower bound, upper bound
        :type csv_path: str | Path

        :param image_name: Name of output image
        :type image_name: str

        :param height_iteration: Amount of y space to place between each element
        :type height_iteration: float

        :param coefficient_radius: Radius of point estimate circles
        :type coefficient_radius: float

        :param value_title: Title to appear above the values
        :type value_title: str

        :param variable_bound: How much distance to place between the forest plot and the variable names, defaults to 1
        :type variable_bound: float

        :param ci_bound: How much distance to place between the forest plot and the numerical values, defaults to 0.1
        :type ci_bound: float

        :param rounder: How many decimal places to round numbers to for numeric column, defaults to 3
        :type rounder: int

        :param text_colour: The colour of the text, may take str values of "Dark_Grey", "Grey", "Black", "White",
            "Blue", "Red", "Green", or a tuple/list of a rgba value bound between 0 and 1, defaults to "Black".
        :type text_colour: str | list | tuple

        :param axis_width: The width of the axis, defaults to 0.005
        :type axis_width: float

        :param axis_label: Label for the x Axis, defaults to "X_Axis"
        :type axis_colour: str

        :param axis_colour: The colour of the axis (see text_colour for options), defaults to "Dark_Grey"
        :type axis_colour: str | list | tuple

        :param y_scale: Width of the line, defaults to 0.1
        :type y_scale: float

        :param x_resolution: X dimension of image output, defaults to 1080
        :type x_resolution: int

        :param y_resolution: Y dimension of image output, defaults to 1080
        :type y_resolution: int

        :param image_type: Image type, defaults to png
        :type image_type: str

        :param camera_scale: Orthographic camera scale, defaults to 4
        :type camera_scale: float

        :return: Nothing, process then finish
        :rtype: None
        """

        subprocess.Popen([self._blend_path, "-b", self._base_file, "--python",
                          str(Path(self._blend_scripts, "ForestPlot.py")), self._prepare_args(locals())])

    def heat_map_frames(self, points_path, days_length, date_index, point_radius, point_colour, camera_z=10):
        """
        This will generate the frames you need for the heat map

        Note
        -----
        Your points list shapefile must contain dates as day/month/year so that it can be delimited by "/"

        :param camera_z:
        :param date_index:
        :param points_path:
        :param days_length:
        :param point_radius:
        :param point_colour:
        :return:
        """

        subprocess.Popen([self._blend_path, "-b", self._base_file, "--python",
                          str(Path(self._blend_scripts, "HeatMap.py")), self._prepare_args(locals())])

    def manhattan_points(self, write_name, gwas_output_path, chromosome_groups, chromosome_headers="CHR",
                         snp_header="SNP", base_position_header="BP", p_value_header="P", camera_position=(12, 9, 55),
                         camera_scale=40, chromosome_positions=None, x_axis_width=23.5, axis_colour="Dark_Grey",
                         line_density=80, axis_width=0.2, bound=0.2, significance=8, significance_colour=(0, 0, 1, 1),
                         x_resolution=1920, y_resolution=1080):
        """
        This will create the points for a manhattan plot

        Note
        -----
        This can take a while, check the file_name.log in the directory you assigned for details on the progress

        This cannot be done purely in the background via the -b subprocessor as opengl requires the window to be
        initialised. As such this will create a blender instance window.

        Source: https://blender.stackexchange.com/questions/2573/render-with-opengl-from-the-command-line

        :param write_name: The name you want the files to use
        :type write_name: str

        :param gwas_output_path: Path to the gwas summary statistics
        :type gwas_output_path: Path | str

        :param chromosome_groups: Groups of chromosomes for colours, for example [[1, 3, ... 21, 23],
            [2, 4, ... 20, 22]]
        :type chromosome_groups: list[list[int]]

        :param chromosome_headers: The header name of the chromosome column, defaults to CHR
        :type chromosome_headers: str

        :param snp_header: The header name of the snp column, defaults to SNP
        :type snp_header: str

        :param base_position_header: The header name of the base position column, defaults to BP
        :type base_position_header: str

        :param p_value_header: The header name of the p value column, defaults to P
        :type p_value_header: str

        :param camera_scale: scale of the orthographic camera, defaults to 40
        :type camera_scale: float

        :param camera_position: Position of the camera, defaults to (12, 10, 55)
        :type camera_position: (int, int, int)

        :param chromosome_positions: If you have prior knowledge of the poisitions of the chromosomes in the file in
            terms of bytes, provide a dict of type {int(chromosome_number): byte start position}
        :type chromosome_positions: dict

        :param x_axis_width: X axis cut off, defaults to 23.5 for 23 chromosomes + some overhang
        :type x_axis_width: float

        :param axis_colour: The colour of the axis (see text_colour for options), defaults to "Dark_Grey"
        :type axis_colour: str | list | tuple

        :param line_density: How small you want the lines to be, defaults to 80 segments
        :type line_density: int

        :param axis_width: Width of the axis lines, defaults to 0.2
        :type axis_width: float

        :param bound: Padding between the axis and material of the graph, defaults to 0.2
        :type bound: float

        :param significance: Level of significance you want to plot a horizontal line, defaults to 8 for -log base ten
            8.
        :type significance: float

        :param significance_colour: RGBA colour of the significance line
        :type significance_colour: (float, float, float, float)

        :param x_resolution: X dimension of image output, defaults to 1920
        :type x_resolution: int

        :param y_resolution: Y dimension of image output, defaults to 1080
        :type y_resolution: int

        :return: Nothing, process file then stop
        """
        subprocess.Popen([self._blend_path, self._base_file, "--python",
                          str(Path(self._blend_scripts, "Manhattan.py")), self._prepare_args(locals())])

    def manhattan_plot(self, colours, output_directory):
        unique_names = list(set([file.split("__")[0] for file in directory_iterator(self._working_dir)
                                 if ".log" not in file]))

        for name in unique_names:
            create_manhattan_plot(name, self._working_dir, colours, output_directory)




    def _prepare_args(self, local_args):
        """
        When a subprocess is called we need to convert the list of arguments to strings so we can pass them via
        subprocess.Popen. However, not all args can be directly convert to strings so this method will convert them when
        required

        :param local_args: args of a given method from locals()
        :type local_args: dict

        :return: A list of strings, where each string represents an argument. Self is replaced with working directory,
            but otherwise the order is the same as submission
        :rtype: list[str]
        """

        args_list = [self._working_dir]
        for arg, value in local_args.items():
            if "colour" in arg:
                args_list.append(str(self._set_colour(value)))
            elif "path" in arg:
                args_list.append(str(validate_path(value).absolute()))
            elif arg == "self":
                pass
            else:
                args_list.append(str(value))

        return "__".join(args_list)

    @staticmethod
    def _set_colour(colour):
        """
        This will set colours when required based on a string key word or on a tuple/list
        :param colour:
        :return:
        """
        if isinstance(colour, str):
            if colour == "Dark_Grey":
                return 0.025, 0.025, 0.025, 1
            elif colour == "Grey":
                return 0.2, 0.2, 0.2, 1
            elif colour == "Black":
                return 0, 0, 0, 1
            elif colour == "White":
                return 1, 1, 1, 1
            elif colour == "Blue":
                return 0.35, 0.085, 0.04, 1
            elif colour == "Red":
                return 0.35, 0.04, 0.04, 1
            elif colour == "Green":
                return 0.066, 0.35, 0.04, 1
            else:
                raise KeyError("Unrecognised string representation of a colour")

        elif isinstance(colour, (tuple, list)):
            if len(colour) != 4:
                raise KeyError(
                    "Colour must be a length four list or tuple of float values between 0 and 1 for rgba")
            else:
                return tuple(colour)

        else:
            raise TypeError(
                f"Expected a string, tuple, or list for colour yet found {type(colour)} for {colour}")
