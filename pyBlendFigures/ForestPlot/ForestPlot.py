from pyBlendFigures import BlendController

from miscSupports import flatten, chunk_list
from csvObject import CsvObject, write_csv
from pathlib import Path
import numpy as np
import subprocess


class ForestPlot(BlendController):
    def __init__(self, blender_path, working_directory, csv_path):
        super().__init__(blender_path, working_directory)

        # Set the raw path to the file
        self._raw_data = csv_path
        assert Path(self._raw_data).exists(), f"Failed to find {csv_path}"

        # Load the blend script via its relative install location and set headers
        self._forest_path = str(Path(Path(__file__).parent, "blend_forest.py").absolute())
        self._forest_header = ["Phenotype", "Coefficient", "Coefficient Plot", "Lower Bound", "Lower Bound Plot",
                               "Upper Bound", "Upper Bound Plot"]

        # Create a temp csv file based on the input that contains the row information needed for the program
        self._load_path = self._create_temp_file()

    def _create_temp_file(self):
        """
        Create the normalised values for plotting

        The graph will want to plot between set dimensions, so that we can have graphs with different raw values be
        comparable. To do this we normalise all the values and then create a temp csv with both the actual values to
        be written, and the normalised values to be plotted.

        :return: The path of the temp csv to load from
        :rtype: Path
        """

        csv_data = CsvObject(self._raw_data, [str, float, float, float])
        assert csv_data.row_length == 4, "Csv file should contain phenotype, coefficient, lower bound, upper bound " \
                                         f"yet found {csv_data.row_length} rows"

        # Normalise the values for the table plot
        numerical_values = flatten([row[1:] for row in csv_data.row_data])
        norm = np.linalg.norm(numerical_values)
        normal_array = (numerical_values / norm).tolist()

        # Restore the values into the same dimension, then combine into a single file to write
        normal_array = chunk_list(normal_array, 3)
        temp_csv = []
        for row, normalised in zip(csv_data.row_data, normal_array):
            temp_csv.append(flatten([[row[0]]] + [[row[i+1], normalised[i]] for i in range(3)]))

        # Write a temp csv file and return its path to to be used for the blend script
        write_csv(self.working_dir, f"{csv_data.file_path.stem}_TEMP", self._forest_header, temp_csv)
        return Path(self.working_dir, f"{csv_data.file_path.stem}_TEMP.csv")

    def write_forest_blend(self, image_name, height_iteration, coefficient_radius, value_title, variable_bound=-1,
                           ci_bound=1, rounder=3, text_colour="Black", axis_width=0.005, axis_label="X_Axis",
                           axis_colour="Dark_Grey", y_scale=0.1, x_resolution=1080, y_resolution=1080, image_type="png",
                           camera_scale=4):

        # TODO allow for colours to actually mean something
        # todo allow rgb and convert to hex. See:
        #  https://stackoverflow.com/questions/3380726/converting-a-rgb-color-tuple-to-a-six-digit-code-in-python
        # todo also allow for hex directly
        # allow a few str key words such as Black and Dark_Grey
        text_colour = (0, 0, 0, 0)
        axis_colour = (0.2, 0.2, 0.2, 0)

        args = [self._load_path, image_name, height_iteration, coefficient_radius, value_title, variable_bound,
                ci_bound, rounder, text_colour, axis_width, axis_label, axis_colour, y_scale, x_resolution,
                y_resolution, image_type, self.working_dir, camera_scale]
        args = [str(arg) for arg in args]

        subprocess.Popen(
            [self.blend_path, "-b", self.base_file, "--python", self._forest_path, "__".join(args)])




