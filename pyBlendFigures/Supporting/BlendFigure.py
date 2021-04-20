from miscSupports import validate_path
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

        print(self._prepare_args(locals()))

        print(Path(self._blend_scripts, "ForestPlot.py").exists())

        subprocess.Popen([self._blend_path, "-b", self._base_file, "--python",
                          str(Path(self._blend_scripts, "ForestPlot.py")), self._prepare_args(locals())])

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





