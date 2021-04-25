from imageObjects import ImageObject
from imageObjects.Support import load_image
from miscSupports import directory_iterator

from pathlib import Path


def create_heat_map_frames(working_directory, point_colour, point_out, gradient_out, gradient_scalar, gradient_divider):
    dates = {"".join([n.replace(".png", "").zfill(2) for n in name.split("_")]): name
             for name in directory_iterator(working_directory)}

    # Format dates to be sorted
    dates = {date: name for date, name in sorted(dates.items(), key=lambda kv: kv[0])}

    # Create the bound to mask on, the isolate the first frame
    base = _base_image(dates, working_directory)
    bound_min = (max(point_colour[0]-5, 0), max(point_colour[1]-5, 0), max(point_colour[2]-5, 0))
    base.mask_on_colour_range(bound_min, point_colour)

    # Point frames
    for index, (date, name) in enumerate(dates.items()):
        if index % 10 == 0:
            print(f"Frame {index}: {len(dates.items())}")

        if index > 0:
            current_date = ImageObject(load_image(str(Path(working_directory, name).absolute())))
            current_date.mask_on_colour_range(bound_min, point_colour)

            current_date.write_to_file(point_out, index)

    # Gradient frames
    for index, (date, name) in enumerate(dates.items()):
        if index % 10 == 0:
            print(f"Frame {index}: {len(dates.items())}")

        if index > 0:
            difference = _create_difference(working_directory, name, bound_min, point_colour, base,
                                            gradient_scalar, gradient_divider)
            difference.write_to_file(gradient_out, index)
            base = difference


def _base_image(dates_dict, read_directory):
    for date, name in dates_dict.items():
        return ImageObject(load_image(str(Path(read_directory, name).absolute())))


def _create_difference(working_directory, name, bound_min, point_colour, base, gradient_scalar, gradient_divider):
    current_date = ImageObject(load_image(str(Path(working_directory, name).absolute())))
    current_date.mask_on_colour_range(bound_min, point_colour)

    return ImageObject(((base.image * gradient_scalar) + current_date.image) / gradient_divider)
