from miscSupports import flatten, load_json
from pathlib import Path
import numpy as np
import bpy
import os


def _isolate(frame_dict, key, attr, d):
    try:
        return frame_dict[key][attr][d]
    except LookupError:
        return 'NA'


def _set_colour(quantiles, colour_list, v):
    if v == 0:
        return colour_list[0]

    for i, q in enumerate(quantiles):
        if i > 0:
            if quantiles[i - 1] < v <= q:
                return colour_list[i - 1]
    return 1.0, 0, 1.0, 1.0


def _create_colour_dict(frame_dict, attr, date, colours):
    # Isolate the values for each key
    value_dict = {key.split("__")[0]: _isolate(frame_dict, key, attr, date) for key in frame_dict.keys()}

    # Isolate the quantiles for each location
    v_list = [v for v in value_dict.values() if v != 'NA']
    if len(v_list) == 0:
        return None, None

    quantiles = [0] + [np.quantile(v_list, i / 10) for i in range(1, 10)] + [max(v_list)]

    # Isolate colours based on quantiles of NA
    colour_dict = {}
    for k, v in value_dict.items():
        if v == 'NA':
            colour_dict[k] = (1.0, 0, 1.0, 1.0)
        else:
            colour_dict[k] = _set_colour(quantiles, colours, v)
    return colour_dict, [f"{round(quantiles[i - 1], 2)} - {round(q - 0.1, 2)}" for i, q in enumerate(quantiles) if
                         i > 0]


def _change_element_colour(name, colour):
    # Isolate the current object
    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.context.scene.objects.get(name)
    obj.select_set(True)

    mat = obj.data.materials[0]
    emission = mat.node_tree.nodes.get('Emission')
    emission.inputs[0].default_value = colour
    bpy.ops.object.select_all(action='DESELECT')


def _change_text(name, text):
    # Isolate the current object
    obj = bpy.context.scene.objects.get(name)
    obj.data.body = text


def _make_directory(write_dir, attr):
    try:
        os.mkdir(Path(write_dir, attr))
    except FileExistsError:
        pass


def main():
    write_directory = r"I:\Work\Figures_and_tables\BIO-HGIS"
    frame_dict = load_json(r"I:\Work\BIO-HGIS\Releases\Json\GBHD.txt")

    attributes = sorted(list(set(flatten([[vv for vv in v.keys()] for v in frame_dict.values()]))))
    attributes = [attr for attr in attributes if attr != 'GID']

    colours = [(0.05, 0.05, 0.05, 1)] + [(0.15 + i / 10, 0.15 + i / 10, 0.15 + i / 10, 1) for i in range(8)] + [
        (1, 1, 1, 1)]
    colours = colours[::-1]

    dates = sorted(list(set(flatten(
        [flatten([v.keys() for k, v in value.items() if k != 'GID']) for value in frame_dict.values()]))))

    obj = bpy.context.scene.objects.get('Districts')
    obj.select_set(True)
    place_dict = {colour.name: colour.node_tree.nodes.get('Emission') for colour in obj.data.materials}

    for attr in attributes:
        print(attr)
        _make_directory(write_directory, attr)

        for d in dates:

            colour_dict, q_values = _create_colour_dict(frame_dict, attr, d, colours)
            if colour_dict:
                bpy.ops.object.select_all(action='DESELECT')

                for i, text in enumerate(q_values, 1):
                    _change_element_colour(f"Q{i}", colours[i - 1])
                    _change_element_colour(f"Q{i}T", colours[i - 1])
                    _change_text(f"Q{i}T", text)

                bpy.ops.object.select_all(action='DESELECT')
                for place, colour in colour_dict.items():
                    place_dict[place].inputs[0].default_value = colour

                bpy.context.scene.render.filepath = str(Path(write_directory, attr, f"{d}.png").absolute())
                bpy.context.scene.eevee.use_gtao = True
                bpy.context.scene.render.film_transparent = True
                bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()


