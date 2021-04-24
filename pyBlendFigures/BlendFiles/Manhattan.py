from blendSupports.Supports.collection_cleanup import collection_cleanup
from blendSupports.Supports.blend_logging import BlendLogger
from blendSupports.misc import convert_colour

from miscSupports import open_setter, decode_line, terminal_time, normalisation_min_max
from pathlib import Path
import json
import math
import ast
import bpy
import sys


class Manhattan:
    def __init__(self, args):
        write_directory, write_name, summary_path, chromosome_selection, chromosome_headers, snp_header, \
            base_position_header, p_value_header, camera_position, camera_scale, positions = args

        # todo we also need to have some axises produced for the render

        self.write_directory = write_directory

        # Setup the blend file
        self.configure_blend(convert_colour(camera_position), float(camera_scale))

        # Set the summary file, and determine if its zipped or not
        self.summary_file = Path(summary_path)
        self.zipped = self.summary_file.suffix == ".gz"

        # If the file is zipped it will have .txt.gz/zip/something, this isolates the actual name regardless of zips
        self.write_name = write_name
        self.logger = BlendLogger(self.write_directory, f"{self.write_name}.log")
        self.logger.write_to_log(f"Starting {self.summary_file.stem}: {terminal_time()}\n")

        # Set the headers
        self.chr_h, self.snp_h, self.bp_h, self.p_h = self.set_summary_headers(
            chromosome_headers, snp_header, base_position_header, p_value_header)
        self.header_indexes = [self.chr_h, self.snp_h, self.bp_h, self.p_h]

        self.logger.write_to_log(chromosome_selection)

        # Evaluate the lists and, if it has been set, the positions within the file.
        chromosome_selection = json.loads(chromosome_selection)
        if not ast.literal_eval(positions):
            # If positions have not been set, set them
            self.positions = self.create_chromosome_positions()
        else:
            self.positions = ast.literal_eval(positions)

        self.logger.write_to_log(chromosome_selection)

        # For each group, render the frames
        for index, chromosome_group in enumerate(chromosome_selection):
            self.make_manhattan(index, chromosome_group)

    @staticmethod
    def configure_blend(camera_position, camera_scale):
        """Since we are using view port renders we need to disable must viewport features"""
        bpy.context.scene.render.film_transparent = True
        for area in bpy.context.screen.areas:

            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.overlay.show_floor = False
                        space.overlay.show_axis_x = False
                        space.overlay.show_axis_y = False
                        space.overlay.show_axis_z = False
                        space.overlay.show_cursor = False
                        space.overlay.show_object_origins = False

        # Set the camera position
        camera = bpy.data.objects["Camera"]
        camera.location = camera_position
        camera.data.ortho_scale = camera_scale

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

    def create_chromosome_positions(self):
        """
        If chromosome positions have not been set, find the seek positions of the file so we can jump to them when
        required
        :return: dict of {chromosome: file.seek}
        :rtype: dict
        """

        last_position = 0
        self.logger.write_to_log(f"No positions found so creating them: {terminal_time()}")

        chromosome_positions = {1: 0}
        for chromosome in range(1, 23):
            print(chromosome)
            with open_setter(self.summary_file)(self.summary_file) as file:
                self.seek_to_start(chromosome, file, last_position)

                for line_byte in file:
                    line = [v for i, v in enumerate(decode_line(line_byte, self.zipped)) if i in self.header_indexes]

                    if int(line[self.chr_h]) > chromosome:
                        last_position = file.tell() - len(line_byte)
                        chromosome_positions[chromosome + 1] = last_position
                        self.logger.write_to_log(f"Determined log position of {chromosome}: {terminal_time()}")
                        self.logger.write_to_log(chromosome_positions)
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
            self.logger.write_to_log(f"Starting {chromosome}: {terminal_time()}")
            print(chromosome)

            # Isolate the values from the file
            line_array = self.isolate_line_array(chromosome)

            # Bound the base pair positions between 0 and 1
            x_positions = normalisation_min_max([r[2] for r in line_array])

            # Convert the p values to the -log base 10
            y_positions = [-math.log(r[3]) for r in line_array]

            vertexes = [(x + (chromosome - 1), y, 0) for x, y in zip(x_positions, y_positions)]

            # Make the block
            mesh = bpy.data.meshes.new(f"Chromosome_{chromosome}")
            obj = bpy.data.objects.new(mesh.name, mesh)
            col = bpy.data.collections.get("Collection")
            col.objects.link(obj)
            bpy.context.view_layer.objects.active = obj

            mesh.from_pydata(vertexes, [], [])

        # Render and then save the file encase we want to edit it
        bpy.context.scene.render.filepath = str(
            Path(self.write_directory, f"{self.write_name}__{index}").absolute())
        bpy.ops.wm.save_as_mainfile(filepath=f"{self.write_directory}/{self.write_name}__{index}.blend")
        bpy.ops.render.opengl(write_still=True, view_context=True)
        collection_cleanup("Collection")
        self.logger.write_to_log(f"Finished group {index} at {terminal_time()}")

    def isolate_line_array(self, chromosome):
        line_array = []

        with open_setter(self.summary_file)(self.summary_file) as file:

            if chromosome == 1:
                file.readline()
            else:
                file.seek(self.positions[chromosome])

            for line_byte in file:
                line = [v for i, v in enumerate(decode_line(line_byte, self.zipped)) if i in self.header_indexes]

                if int(line[self.chr_h]) > chromosome:
                    file.close()
                    return line_array
                else:
                    line_array.append([str(line[0]), int(line[1]), int(line[2]), float(line[3])])
        return line_array


if __name__ == '__main__':
    Manhattan(sys.argv[len(sys.argv) - 1].split("__"))
