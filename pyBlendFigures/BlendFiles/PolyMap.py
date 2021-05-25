from blendSupports.Meshs.mesh_ref import make_mesh

from shapely.geometry import MultiPolygon, Polygon
from shapeObject import ShapeObject
import sys
import bpy


class PolyMap:
    def __init__(self, args):

        # Set attributes
        write_directory, shape_path, rec_index = args
        self.shape_obj = ShapeObject(shape_path)
        self.rec_index = int(rec_index)

        # Create Map
        self.make_shapefile_places()
        bpy.ops.wm.save_as_mainfile(filepath=f"{write_directory}/MapShp.blend")

    def make_shapefile_places(self):
        """
        For each place in the shapefile make a mesh element of name records[self.rec_index]

        :return: Nothing, make each place then stop
        :rtype: None
        """

        for index, (rec, poly) in enumerate(zip(self.shape_obj.records, self.shape_obj.polygons)):

            if index % 20 == 0:
                print(f"{index} / {len(self.shape_obj.records)}")

            if isinstance(poly, MultiPolygon):

                # Multiple polygons have to have multiple polygons per mesh
                multi_poly = [self._process_location(f"{rec[self.rec_index]}_{i}", p) for i, p in enumerate(poly)]

                # Combine the meshes
                for obj in multi_poly:
                    obj.select_set(True)
                bpy.ops.object.join()

                # Rename the mesh
                for obj in bpy.context.selected_objects:
                    obj.name = str(rec[0])

            elif isinstance(poly, Polygon):
                self._process_location(str(rec[self.rec_index]), poly)

    def _process_location(self, object_name, polygon):
        """
        Polygons have inner rings, and may be made of multiple parts. This will create a mesh of each part within this
        object and cut out holes where required.

        :param object_name: Name of the object
        :type object_name: str

        :param polygon: A shapely polygon
        :type polygon: Polygon

        :return: The mesh object reference data
        """
        obj, mesh = make_mesh(object_name)
        verts = self._isolate_coords(polygon.exterior.coords.xy)

        mesh.from_pydata(verts, [], [[i for i in range(len(verts))]])
        bpy.ops.object.select_all(action='DESELECT')

        for i, hole in enumerate(polygon.interiors):
            self._remove_hole(i, hole, obj, verts)
        return obj

    def _remove_hole(self, hole_index, hole, mesh_obj, mesh_verts):
        """
        Meshes may have holes in them which we need to remove via boolean operations

        :param hole_index: The index of this hole
        :type hole_index: int

        :param hole: Shapely interior loop coordinates

        :param mesh_obj: The mesh object reference we wish to remove holes from

        :param mesh_verts: vertexs of the exterior of the mesh object reference

        :return: Nothing, remove holes then stop
        :rtype: None
        """
        # Create a boolean mesh of the mesh_obj
        bpy.context.view_layer.objects.active = mesh_obj
        mesh_obj.select_set(True)
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.ops.object.select_all(action='DESELECT')

        # Create the hole mesh, if the mesh would be broken by the boolean leaving the array then remove the vert
        hole_coords = [(x, y, z) for x, y, z in self._isolate_coords(hole.xy, 200) if (x, y, 0) not in mesh_verts]
        hole_obj, hole_mesh = make_mesh(f"Hole_{hole_index}")
        hole_mesh.from_pydata(hole_coords, [], [[i for i in range(len(hole_coords))]])

        # Extrude the hole downwards so that we can create a boolean
        hole_obj.select_set(True)
        bpy.context.view_layer.objects.active = hole_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.extrude_region_move(
            MESH_OT_extrude_region={"use_normal_flip": False, "mirror": False},
            TRANSFORM_OT_translate={"value": (0, 0, -400), "orient_type": 'LOCAL',
                                    "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type": 'LOCAL',
                                    "constraint_axis": (False, False, True), "mirror": False,
                                    "use_proportional_edit": False, "proportional_edit_falloff": 'SMOOTH',
                                    "proportional_size": 1, "use_proportional_connected": False,
                                    "use_proportional_projected": False, "snap": False, "snap_target": 'CLOSEST',
                                    "snap_point": (0, 0, 0), "snap_align": False, "snap_normal": (0, 0, 0),
                                    "gpencil_strokes": False, "cursor_transform": False, "texture_space": False,
                                    "remove_on_cancel": False, "release_confirm": False, "use_accurate": False})
        bpy.ops.object.mode_set(mode="OBJECT")

        # Assign the hole as a boolean to the mesh
        mesh_obj.modifiers["Boolean"].object = hole_obj
        bpy.context.view_layer.objects.active = mesh_obj

        # Apply the boolean modifier then remove the mesh and obj reference
        mesh_obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier="Boolean")
        bpy.data.objects.remove(hole_obj)
        bpy.data.meshes.remove(hole_mesh)

    @staticmethod
    def _isolate_coords(polygon, z=0):
        """Isolate the x and y positions of a given polygon then convert into a 3D Vector"""
        x_list = [x for x in polygon[0]]
        y_list = [y for y in polygon[1]]

        return [(x, y, z) for x, y in zip(x_list, y_list)]


if __name__ == '__main__':
    PolyMap(sys.argv[len(sys.argv) - 1].split("__"))
