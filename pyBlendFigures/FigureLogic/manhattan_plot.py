from miscSupports import directory_iterator
from imageObjects.Support import load_image
from imageObjects import ImageObject


def create_manhattan_plot(plot_name, working_dir, colours, output_directory):
    # Isolate the files related to this name
    name_files = []
    for file in directory_iterator(working_dir):
        if (plot_name in file) and (".log" not in file) and (".blend" not in file):
            name_files.append(file)

    # If we find the axis image then we can construct a plot
    if sum([True if "AXIS" in file else False for file in name_files]) == 1:

        # Isolate the axis and the point image file names
        axis = [file for file in name_files if "AXIS" in file][0]
        points = [file for file in name_files if "AXIS" not in file]
        assert len(points) == len(colours), f"Found {len(points)} but was only provided {len(colours)} colours"

        # Construct the plot
        _construct_plot_image(working_dir, axis, points, colours, output_directory, plot_name)

    else:
        raise IndexError(f"Failed to find {plot_name}_AXIS.png")


def _construct_plot_image(working_dir, axis, points, colours, output_directory, plot_name):

    axis = ImageObject(load_image(f"{working_dir}/{axis}", 4))
    blank = axis.blank_like(True)

    for point_img, colour in zip(points, colours):
        print(f"Processing {plot_name} -> {point_img}: {colour}")

        # Load the point image
        point_img = ImageObject(load_image(f"{working_dir}/{point_img}", 4))

        # Create the overlay colour
        overlay_colour = point_img.blank_like(True)
        overlay_colour.change_bgra_to_bgr()
        overlay_colour.change_a_colour((0, 0, 0), colour)

        # Set the point mask
        point_mask = point_img.mask_alpha(True)
        point_mask.change_bgra_to_bgr()
        point_mask.change_to_mono()

        # Mask the colour on the point mask then assign it the point masks alpha channel
        overlay_colour.mask_on_image(point_mask)
        overlay_colour.change_bgr_to_bgra()
        overlay_colour.assign_alpha_channel(point_mask)
        blank.overlay_additive(overlay_colour)

    blank.overlay_additive(axis)
    blank.write_to_file(output_directory, plot_name)




# a = ImageObject(load_image(r"/Tests/ManhattanTests/untitled.png", 4))
# print(a)
#
#
# c = a.blank_like(True)
# c.change_bgra_to_bgr()
#
#
# b = a.mask_alpha(True)
#
# b.change_bgra_to_bgr()
# b.change_to_mono()
#
# c.change_a_colour((0, 0, 0), (160, 80, 0))
#
# c.mask_on_image(b)
#
#
# a.change_bgra_to_bgr()
#
# a.overlay_image(c, 0, 0)
#
# a.change_bgr_to_bgra()
#
# a.assign_alpha_channel(b)
#
# # print(type(rgba))
# #
# # b.show()
# #
# # cv2.imwrite(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ManhattanTests\Name2.png", rgba)
#
# a.write_to_file(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ManhattanTests", "Plot2")