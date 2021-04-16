from pathlib import Path
import gzip
import math
import bpy
import bmesh

def open_setter(path):
    """
    Some files may be zipped, opens files according to the zip status

    :param path: File path
    :type path: Path
    :return: gzip.open if the file is gzipped else open
    """
    if path.suffix == ".gz":
        return gzip.open
    else:
        return open


def decode_line(byte_line, zip_status):
    """
    Some files may be zipped, when we open zipped files we will need to decode them

    :param byte_line: Current line from open file, zipped or otherwise
    :param zip_status: If the file is zipped or not
    :return: decoded line from the open file
    """
    if zip_status:
        return byte_line.decode("utf-8").split()
    else:
        return byte_line.split()


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


def normalisation_min_max(list_of_values):
    """
    Will normalise a list to be between 0 and 1

    :param list_of_values: A list of numeric values
    :type list_of_values: list[int] | list[float]

    :return: A list of values between zero and 1
    :rtype: list[float]
    """

    value_min = min(list_of_values)
    value_max = max(list_of_values)
    return [((value - value_min) / (value_max - value_min)) for value in list_of_values]


def construct_line_array(summary_path, chromosome, last_position, zipped, header_indexes, chr_h):
    line_array = []

    with open_setter(summary_path)(summary_path) as file:
        # Skip the header

        seek_to_start(chromosome, file, last_position)

        for line_byte in file:
            line = [v for i, v in enumerate(decode_line(line_byte, zipped)) if i in header_indexes]

            if int(line[chr_h]) > chromosome:
                last_position = file.tell() - len(line_byte)
                break
            else:
                line_array.append([str(line[0]), int(line[1]), int(line[2]), float(line[3])])
        file.close()

    return line_array, last_position


def construct():
    output_path = Path(r"Z:\UKB\GeographicID\Paper Data Extraction\SB_Papers\GWAS\Results\SF_1_imputed.txt.gz")
    zipped = output_path.suffix == ".gz"
    header_indexes = [1, 0, 2, 13]
    chr_h, snp_h, bp_h, p_h = header_indexes

    chromosome_list = [i for i in range(1, 24)]

    last_position = 0
    for index, chromosome in enumerate(chromosome_list):

        line_array, last_position = construct_line_array(output_path, chromosome, last_position, zipped, header_indexes,
                                                         chr_h)
        # Bound the base pair positions between 0 and 1
        x_positions = normalisation_min_max([r[2] for r in line_array])

        # Convert the p values to the -log base 10
        y_positions = [-math.log(r[3]) for r in line_array]

        vertexes = [(x + index, y, 0) for x, y in zip(x_positions, y_positions)]

        # Make the block
        mesh = bpy.data.meshes.new(f"Chromosome_{chromosome}")
        obj = bpy.data.objects.new(mesh.name, mesh)
        col = bpy.data.collections.get("Collection")
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        mesh.from_pydata(vertexes, [], [])
        break

    print("\n\n")


if __name__ == '__main__':
    construct()

