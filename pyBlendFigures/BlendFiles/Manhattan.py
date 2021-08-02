from blendSupports.Meshs.horizontal_dashed_line import make_horizontal_dashed_line
from blendSupports.Supports.collection_cleanup import collection_cleanup
from blendSupports.Renders.render import open_gl_render, render_scene
from blendSupports.Meshs.graph_axis import make_graph_axis
from blendSupports.Meshs.mesh_ref import make_mesh
from blendSupports.Meshs.text import make_text

from miscSupports import open_setter, decode_line, terminal_time, normalisation_min_max, FileOut, tuple_convert
from pathlib import Path
import json
import math
import sys
import bpy


class Manhattan:
    def __init__(self, args):
        write_directory, write_name, summary_path, chromosome_selection, chr_headers, snp_h, bp_h, p_v, \
            camera_position, camera_scale, x_axis_width, axis_colour, line_density, axis_width, bound, significance, \
            significance_colour, x_resolution, y_resolution = args

        # Setup camera and write location
        self.camera_position = camera_position
        self.camera_scale = camera_scale
        self.x_res = x_resolution
        self.y_res = y_resolution
        self.write_directory = write_directory

        # Set the summary file, and determine if its zipped or not
        self.summary_file = Path(summary_path)
        self.zipped = self.summary_file.suffix == ".gz"

        # If the file is zipped it will have .txt.gz/zip/something, this isolates the actual name regardless of zips
        self.write_name = write_name
        self.logger = FileOut(self.write_directory, f"{self.write_name}", "log", True)
        self.logger.write(f"Starting {self.summary_file.stem}: {terminal_time()}\n")

        # Set the headers
        self.chr_h, self.snp_h, self.bp_h, self.p_h = self.set_summary_headers(chr_headers, snp_h, bp_h, p_v)

        # Evaluate the lists and, if it has been set, the positions within the file.
        chromosome_selection = json.loads(chromosome_selection)

        # If positions have not been set, set them
        self.positions = self.create_chromosome_positions()

        self.axis_y_positions = []
        # For each group, render the frames
        for index, chromosome_group in enumerate(chromosome_selection):
            self.make_manhattan(index, chromosome_group)

        # Make the axis render
        self._make_axis(float(x_axis_width), tuple_convert(axis_colour), int(line_density), float(axis_width),
                        float(bound), float(significance), tuple_convert(significance_colour))

    def set_summary_headers(self, chromosome_header, snp_header, base_position_header, p_value_header):
        """
        Validate which columns are the chromosome, snp, base position and p value.

        To do this, each name provided or the respective default is checked against the first row of the summary file.
        If all are present, the indexes are returned in the order of the header input arguments so they can be assigned
        and used to isolate values later.

        :param chromosome_header: chromosome header name
        :type chromosome_header: str

        :param snp_header: snp header name
        :type snp_header: str

        :param base_position_header: base position header name
        :type base_position_header: str

        :param p_value_header: p value header
        :type p_value_header: str

        :return: A list of [chromosome_header_index, snp_header_index, base_position_index, p_value_index]
        :rtype: list[int, int, int, int]

        :raises KeyError: If a header provided was not found in the decoded headers
        """

        # Decode the headers
        with open_setter(self.summary_file)(self.summary_file) as file:
            decoded_headers = decode_line(file.readline(), self.zipped)
        file.close()

        header_indexes = []
        for header in [chromosome_header, snp_header, base_position_header, p_value_header]:
            if header in decoded_headers:
                header_indexes.append(decoded_headers.index(header))
            else:
                raise KeyError(f"{header} was not found in {decoded_headers}")
        return header_indexes

    def _isolate_from_line(self, line_byte):
        """Decode a line byte then isolate its attributes"""
        line = decode_line(line_byte, self.zipped)
        return [int(line[self.chr_h]), str(line[self.snp_h]), int(line[self.bp_h]), float(line[self.p_h])]

    def create_chromosome_positions(self):
        """
        If chromosome positions have not been set, find the seek positions of the file so we can jump to them when
        required
        :return: dict of {chromosome: file.seek}
        :rtype: dict
        """

        last_position = 0
        chromosome_positions = {1: 0}
        for chromosome in range(1, 23):
            print(chromosome)
            with open_setter(self.summary_file)(self.summary_file) as file:
                self.seek_to_start(chromosome, file, last_position)

                for line_byte in file:
                    current_chrome, _, _, _ = self._isolate_from_line(line_byte)

                    if current_chrome > chromosome:
                        last_position = file.tell() - len(line_byte)
                        chromosome_positions[chromosome + 1] = last_position
                        self.logger.write(f"Determined log position of {chromosome}: {terminal_time()}")
                        self.logger.write(chromosome_positions)
                        break

                file.close()

        return chromosome_positions

    @staticmethod
    def seek_to_start(current_chromosome, file_obj, last_pos):
        """
        If its the first chromosome skip the first line, else seek to the start position of the next chromosome block
        """

        # Then just skip the header
        if current_chromosome == 1:
            file_obj.readline()

        # Else skip to the start of the chromosome section
        else:
            file_obj.seek(last_pos)

    def make_manhattan(self, index, chromosome_group):

        for chromosome in chromosome_group:
            self.logger.write(f"Starting {chromosome}: {terminal_time()}")

            # Isolate the values from the file
            line_array = self.isolate_line_array(chromosome)

            if line_array:
                # Bound the base pair positions between 0 and 1
                x_positions = normalisation_min_max([r[2] for r in line_array])

                # Convert the p values to the -log base 10, append max to the axis so we can create it
                y_positions = [-math.log(r[3]) for r in line_array]
                self.axis_y_positions.append(max(y_positions))

                # Plot the vertexes to the graph
                vertexes = [(x + (chromosome - 1), y, 0) for x, y in zip(x_positions, y_positions)]

                # Make the block
                obj, mesh = make_mesh(f"Chromosome_{chromosome}")
                mesh.from_pydata(vertexes, [], [])

        # Render and then save the file encase we want to edit it
        open_gl_render(self.camera_position, self.write_directory, f"{self.write_name}__{index}", self.x_res,
                       self.y_res, camera_scale=self.camera_scale)
        collection_cleanup("Collection")
        self.logger.write(f"Finished group {index} at {terminal_time()}")

    def isolate_line_array(self, chromosome):
        with open_setter(self.summary_file)(self.summary_file) as file:
            if self._seek_to_position(file, chromosome):
                return self._make_line_array(file, chromosome)
            else:
                return None

    def _seek_to_position(self, file, chromosome):

        # Skip header
        if chromosome == 1:
            file.readline()
            return True
        else:
            # Try to read the position unless the chromosome is not valid in which case return None
            try:
                file.seek(self.positions[chromosome])
                return True

            except KeyError:
                return None

    def _make_line_array(self, file, chromosome):

        line_array = []
        for line_byte in file:
            current_chrome, snp, bp, p = self._isolate_from_line(line_byte)

            if current_chrome > chromosome:
                file.close()
                return line_array
            else:
                line_array.append([current_chrome, snp, bp, p])
        return line_array

    def _make_axis(self, x_axis_width, axis_colour, line_density, axis_width, bound, significance, significance_colour):
        # Set the axis y height as the max of axis_y_positions with ceiling to prevent out of bounds points
        axis_height = math.ceil(max(self.axis_y_positions))

        # Make the graphs axis
        make_graph_axis(axis_colour, x_axis_width, axis_height, axis_width, bound)

        # make the horizontal dashed line to determine the level of significance
        make_horizontal_dashed_line("Line", significance_colour, x_axis_width, 0, significance, line_density)

        # Make a spacer so that elements are relative distances to the axis
        axis_spacer = -(axis_width + (axis_width * 2) + axis_width / 2)

        # Label the x axis
        make_text("Chromosomes", 23.5 / 2, axis_spacer*1.5, "Chromosomes", axis_width * 2, axis_colour, "CENTER")
        for i in range(23):
            make_text(f"Chr{i}", i + 0.5, axis_spacer, f"{i + 1}", axis_width * 2, axis_colour, "CENTER")

        # Label the y axis
        make_text("Log", axis_spacer * 1.5, axis_height / 2, "-log10(pvalue)", axis_width * 2, axis_colour, "CENTER")

        # Y axis needs to be rotated
        obj = bpy.data.objects["Log"]
        obj.select_set(True)
        bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 use_proportional_connected=False, use_proportional_projected=False)

        # Add y axis values
        for i in range(axis_height + 1):
            if i % 2 == 0:
                make_text(f"log{i}", axis_spacer, i, f"{i}", axis_width * 2, axis_colour, "CENTER")

        # Render the scene
        render_scene(self.camera_position, self.write_directory, f"{self.write_name}__AXIS", x_resolution=self.x_res,
                     y_resolution=self.y_res, camera_scale=self.camera_scale)


if __name__ == '__main__':
    Manhattan(sys.argv[len(sys.argv) - 1].split("__"))
