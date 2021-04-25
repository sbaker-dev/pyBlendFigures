from blendSupports.Meshs.mesh_ref import make_mesh

from miscSupports import flatten
from shapely.geometry import MultiPolygon, Polygon
from shapeObject import ShapeObject
import bpy


class MapFrames:
    def __init__(self):

        shape_path = r"I:\Work\Shapefiles\Districts\EW1951_lgdistricts\EW1951_lgdistricts.shp"
        rec_index = 0

        self.shape_obj = ShapeObject(shape_path)
        self.rec_index = rec_index

        self.make_shapefile_places()

    def make_shapefile_places(self):

        for index, (rec, poly) in enumerate(zip(self.shape_obj.records, self.shape_obj.polygons)):

            if index % 20 == 0:
                print(f"{index} / {len(self.shape_obj.records)}")

            if isinstance(poly, MultiPolygon):
                verts = []
                faces = []
                total_vert = 0

                holes_list = []

                # Multiple polygons have to have multiple polygons per mesh
                for i, p in enumerate(poly):
                    poly_verts = self._isolate_coords(p.exterior.coords.xy)
                    verts.append(poly_verts)

                    poly_faces = [total_vert + i for i in range(len(poly_verts))]
                    faces.append(poly_faces)

                    holes_list.append(p.interiors)

                    total_vert = len(poly_verts)

                # Make the object from the separate polygons into a single mesh
                obj, mesh = make_mesh(str(rec[self.rec_index]))
                mesh.from_pydata(flatten(verts), [], faces)
                bpy.ops.object.select_all(action='DESELECT')

                # Take the InteriorRingSequence(not the same as poly.interiors)
                for i, hole in enumerate(holes_list):
                    self._remove_hole(i, hole.__p__.exterior.coords, obj)

            elif isinstance(poly, Polygon):
                obj, mesh = make_mesh(str(rec[self.rec_index]))
                verts = self._isolate_coords(poly.exterior.coords.xy)

                mesh.from_pydata(verts, [], [[i for i in range(len(verts))]])
                bpy.ops.object.select_all(action='DESELECT')

                for i, hole in enumerate(poly.interiors):
                    self._remove_hole(i, hole, obj)

    def _remove_hole(self, index, hole, mesh_obj):

        # Create a boolean mesh of the mesh_obj
        bpy.context.view_layer.objects.active = mesh_obj
        mesh_obj.select_set(True)
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.ops.object.select_all(action='DESELECT')

        # Create the hole mesh
        hole_coords = self._isolate_coords(hole.xy, 200)
        hole_obj, hole_mesh = make_mesh(f"Hole_{index}")
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
        x_list = [x for x in polygon[0]]
        y_list = [y for y in polygon[1]]

        return [(x, y, z) for x, y in zip(x_list, y_list)]


MapFrames()
