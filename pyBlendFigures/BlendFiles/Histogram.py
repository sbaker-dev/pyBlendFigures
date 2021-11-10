from blendSupports.Meshs.mesh_ref import make_mesh
from csvObject import CsvObject
import bpy

file_path = r"C:\Users\Samuel\PycharmProjects\ScarletExposure\Figures and Tables\SummaryCsvs\S.csv"
name_index = 0
isolate = 1


# TODO: Scaling directly is grim. We need to just standardise the values to be between the min and max by diving all by the max value
y_scale = 0.0025



for i, row in enumerate(CsvObject(file_path).row_data):
    print(i)

    obj, mesh = make_mesh(row[name_index], (0.1, 0.1, 0.1, 0.1))

    verts = [
        (i, float(row[isolate]), 0),
        (i, 0, 0),
        (i + 1, 0, 0),
        (i + 1, float(row[isolate]), 0)
    ]

    mesh.from_pydata(verts, [], [[0, 1, 2, 3]])
    obj.select_set(True)

    bpy.ops.transform.resize(value=(1, y_scale, 1))

    print(obj.name)

    bpy.ops.object.select_all(action='DESELECT')
