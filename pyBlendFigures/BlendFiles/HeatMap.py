from blendSupports.misc import convert_colour
from blendSupports.Nodes.emission_node import create_emission_node

from datetime import datetime, timedelta
from miscSupports import terminal_time
from shapeObject import ShapeObject
from pathlib import Path

import sys
import bpy


def set_dates(path_to_points, date_index):
    """
    Setup the process by isolating the dates to start and end at and load the shapefile

    :param path_to_points: Path to the shapefile points
    :type path_to_points: str

    :param date_index: Index of the date in the records of the shapefile
    :type date_index: int
    """
    points = ShapeObject(path_to_points)

    dates = [rec[date_index] for rec in points.records]

    start_day, start_month, start_year = dates[0].split("/")
    end_day, end_month, end_year = dates[-1].split("/")

    start_date = datetime(int(start_year), int(start_month), int(start_day))
    end_date = datetime(int(end_year), int(end_month), int(end_day))

    return points, start_date, end_date


def make_point(x, y, name, radius, point_colour):
    # Create the primitive circle
    bpy.ops.mesh.primitive_circle_add(enter_editmode=True, align='WORLD', location=(x, y, 0.1), radius=radius)

    # Circle to default to edit mode, use this to fill the circle in.
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.editmode_toggle()

    # Set the name and material of the circle, then toggle out and deselect.
    bpy.context.object.name = name
    obj = bpy.context.object
    create_emission_node(obj, point_colour)


def iter_heat_map_frames():
    write_directory, points_path, days_length, date_index, point_radius, point_colour, camera_z = \
        sys.argv[len(sys.argv) - 1].split("__")

    days_length = int(days_length)
    date_index = int(date_index)
    point_radius = float(point_radius)
    point_colour = convert_colour(point_colour)

    # Load the ShapeObject and set the dates dimensions
    points, start_date, end_date = set_dates(points_path, date_index)
    date_iter = start_date

    # Set the camera location
    obj_camera = bpy.context.scene.camera
    obj_camera.location = (0, 0, float(camera_z))
    bpy.context.scene.render.film_transparent = True

    # TODO need to find a way to adjust the camera to a set location that best fits the object
    obj_camera = bpy.context.scene.camera
    obj_camera.data.clip_end = 1e+09

    while date_iter < end_date:
        print(date_iter)

        # If the point is between the current date and the current date + extra days make a point
        for point, rec in zip(points.points, points.records):
            day, month, year = rec[date_index].split("/")
            current_date = datetime(int(year), int(month), int(day))

            if date_iter <= current_date < date_iter + timedelta(days=days_length):
                make_point(point.x, point.y, rec[date_index], point_radius, point_colour)

        # Render the image of this date, then iterate the iterator forward by length of days_length
        bpy.context.scene.render.filepath = str(
            Path(write_directory, f"{date_iter.year}_{date_iter.month}_{date_iter.day}.png").absolute())
        bpy.ops.render.render(write_still=True)
        date_iter += timedelta(days=days_length)

        bpy.ops.wm.save_as_mainfile(filepath=f"{write_directory}/Test.blend")

        # Cleanup the collection
        collection = bpy.data.collections["Collection 3"]

        meshes = set()
        for obj in collection.objects:
            meshes.add(obj.data)
            if obj.name != "Camera":
                bpy.data.objects.remove(obj)

        # Look at meshes that are orphean after objects removal
        for mesh in [m for m in meshes if m.users == 0]:
            # Delete the meshes
            bpy.data.meshes.remove(mesh)

        print(f"Finished at {terminal_time()}\n\n")


if __name__ == '__main__':
    iter_heat_map_frames()






