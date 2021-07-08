from miscSupports import directory_iterator
from imageObjects.Support import load_image
from imageObjects import ImageObject


# todo Generalise this and manhattan
def create_qq_plot(plot_name, working_dir, point_colour, output_directory):
    # Isolate the files related to this name
    name_files = []
    for file in directory_iterator(working_dir):
        if (plot_name in file) and (".log" not in file) and (".blend" not in file):
            name_files.append(file)

    # If we find the axis image then we can construct a plot
    if sum([True if "AXIS" in file else False for file in name_files]) == 1:
        # Isolate the axis and the point image file names
        axis = [file for file in name_files if "AXIS" in file][0]
        points = [file for file in name_files if "AXIS" not in file][0]

        # Construct the plot
        _plot_image(working_dir, axis, points, point_colour, output_directory, plot_name)

    else:
        raise IndexError(f"Failed to find {plot_name}__AXIS.png")


def _plot_image(working_dir, axis, point_img, colour, output_directory, plot_name):

    axis = ImageObject(load_image(f"{working_dir}/{axis}", 4))
    blank = axis.blank_like(True)

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
