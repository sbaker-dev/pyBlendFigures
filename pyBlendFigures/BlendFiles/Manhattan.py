from blendSupports.Supports.collection_cleanup import collection_cleanup

from miscSupports import open_setter, decode_line, terminal_time, normalisation_min_max
from pathlib import Path
import logging
import json
import math
import ast
import bpy
import sys


class Manhattan:
    def __init__(self, args):
        write_directory, summary_path, chromosome_selection, chromosome_headers, snp_header, \
            base_position_header, p_value_header, positions = args.split("__")

        self.write_directory = write_directory

        # Setup the blend file
        self.configure_blend()

        # Set the summary file, and determine if its zipped or not
        self.summary_file = Path(summary_path)
        self.zipped = self.summary_file.suffix == ".gz"

        # Setup logging
        logging.basicConfig(filename=str(Path(self.write_directory, f"{self.summary_file.stem}.log").absolute()),
                            level=logging.INFO)
        self.logger = logging.getLogger(Path(self.write_directory, f"{self.summary_file.stem}.log"))
        self.logger.info(f"Starting {self.summary_file.stem}: {terminal_time()}\n")

        # Set the headers
        self.chr_h, self.snp_h, self.bp_h, self.p_h = self.set_summary_headers(
            chromosome_headers, snp_header, base_position_header, p_value_header)
        self.header_indexes = [self.chr_h, self.snp_h, self.bp_h, self.p_h]

        # Evaluate the lists and, if it has been set, the positions within the file.
        chromosome_selection = json.loads(chromosome_selection)
        if not ast.literal_eval(positions):
            # If positions have not been set, set them
            self.positions = self.create_chromosome_positions()
        else:
            self.positions = ast.literal_eval(positions)

        # For each group, render the frames
        for index, chromosome_group in enumerate(chromosome_selection):
            self.make_manhattan(index, chromosome_group)

    @staticmethod
    def configure_blend():
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
        self.logger.info(f"No positions found so creating them: {terminal_time()}")

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
                        self.logger.info(chromosome_positions)
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
            self.logger.info(f"Starting {chromosome}")
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

        # Render
        bpy.context.scene.render.filepath = str(
            Path(self.write_directory, f"{self.summary_file.stem}__{index}").absolute())
        bpy.ops.render.opengl(write_still=True, view_context=True)
        collection_cleanup("Collection")

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
    a = r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Manhattan\TestFrames__Y:\data\ukbiobank\software\gwas_pipeline\dev\release_candidate\data\phenotypes\ow18390\output\M_1\789eacc2-c569-41ec-8e1c-5eadb99f05b8\M_1_imputed.txt.gz__[[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23], [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]]__CHR__SNP__BP__P_BOLT_LMM_INF__{1: 0, 2: 103551288, 3: 215398919, 4: 309830049, 5: 406727080, 6: 492859006, 7: 582512400, 8: 660602369, 9: 733966091, 10: 791841203, 11: 860501560, 12: 926965989, 13: 990772456, 14: 1039111338, 15: 1082777792, 16: 1120845458, 17: 1162690859, 18: 1198818737, 19: 1236446323, 20: 1267538928, 21: 1296945622, 22: 1315076297, 23: 1333582626}"
    b = r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\Manhattan\TestFrames__Y:\data\ukbiobank\software\gwas_pipeline\dev\release_candidate\data\phenotypes\ow18390\output\M_1\789eacc2-c569-41ec-8e1c-5eadb99f05b8\M_1_imputed.txt.gz__[[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23], [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]]__CHR__SNP__BP__P_BOLT_LMM_INF__None"
    Manhattan(a)
