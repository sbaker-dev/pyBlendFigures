from blendSupports.Meshs.mesh_ref import make_mesh
from csvObject import CsvObject
import bpy

isolate = 1

for i, row in enumerate(CsvObject(r"I:\Work\DataBases\Disease Notifications\ErrorLog\ErrorByFileEdit.csv").row_data):
    print(i)

    obj, mesh = make_mesh(row[0], (0.1, 0.1, 0.1, 0.1))

    verts = [
        (i, int(row[isolate]), 0),
        (i, 0, 0),
        (i + 1, 0, 0),
        (i + 1, int(row[isolate]), 0)
    ]

    mesh.from_pydata(verts, [], [[0, 1, 2, 3]])
    bpy.ops.object.select_all(action='DESELECT')

bpy.ops.wm.save_as_mainfile(filepath=r"I:\Work\DataBases\Disease Notifications\ErrorLog\ErrorBlends\Error1.blend")