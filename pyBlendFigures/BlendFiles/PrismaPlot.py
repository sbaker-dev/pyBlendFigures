from blendSupports.Meshs.text import make_text
from blendSupports.Supports.collection_cleanup import collection_cleanup


from miscSupports import load_yaml


class PrismaPlot:
    def __init__(self):
        self._args = load_yaml(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\TestV2\PRISMA\Test3.yaml")

        self.spacing = 1

        self.links = self._args["Links"]
        self.positions = self._args["Positions"]
        self.col_count = len(self.links["Columns"])
        self.row_count = len(self.links["Rows"])

        self.dimensions = self._set_dimensions()
        print(self.dimensions)

        # TODO: Create each text element, get their dimensions with .dimension and store this rather than via _set_dimensions
        # TODO: Then iterate though row by row placing each element in its place

        # for row_i in range(self.row_count):
        #     for i in range(self.col_count):
        #         for name, position in self.positions.items():
        #             print(name, position)
        #         break
        #     break


        # for i in range(self.col_count):
        #     previous_height = 0
        #     row_adjustment = 0
        #
        #     x_positions = []
        #     y_positions = []
        #     for row_i in range(self.row_count):
        #
        #         for name, position in self.positions.items():
        #             col_id, row_id = name.split("-")
        #             if col_id == str(i) and row_id == str(row_i):
        #                 make_text(name, i + row_adjustment, (-row_i - previous_height), position["Text"], 1,
        #                           (255, 255, 255, 255), align="CENTER")
        #                 previous_height += (len(position["Text"].split("\n")) + self.spacing)
        #
        #                 bpy.ops.object.select_all(action='DESELECT')
        #                 obj = bpy.data.objects[name]
        #                 obj.select_set(True)
        #                 x_positions.append(obj.dimensions[0])
        #                 y_positions.append(obj.dimensions[1])
        #
        #     print(x_positions)
        #     print(y_positions)
        #
        #     print("")

    def _set_dimensions(self):

        widths = {}
        for i in range(self.col_count):
            dimensions = []

            for name, position in self.positions.items():

                col_id, row_id = name.split("-")
                if col_id == str(i):
                    obj = make_text(name, 0, 0, position["Text"], 1, (255, 255, 255, 255), align="CENTER")
                    dimensions.append(obj.dimensions)

            widths[str(i)] = max([x for x, y, z in dimensions])

        collection_cleanup("Collection")
        return widths
# col_heights.append([name, len(text_split)])


#

PrismaPlot()