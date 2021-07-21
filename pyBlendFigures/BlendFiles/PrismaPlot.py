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

        self.widths, self.dimensions = self._set_dimensions()
        print(self.dimensions)

        # TODO: Create each text element, get their dimensions with .dimension and store this rather than via _set_dimensions
        # TODO: Then iterate though row by row placing each element in its place

        previous_height = 0
        for row_i in range(self.row_count):
            for col_i in range(self.col_count):
                try:

                    name = f"{col_i}-{row_i}"
                    position = self.positions[name]

                    print(name)
                    width = sum([self.widths[str(i - 1)] for i in range(col_i + 1)])
                    if col_i != 0:
                        width += self.spacing
                    print(width)

                    make_text(name, width, previous_height, position["Text"], 1, (255, 255, 255, 255), align="CENTER")
                    previous_height += self.dimensions[name][1]
                except KeyError:
                    pass

    def _set_dimensions(self):

        widths = {"-1": 0}
        dimension_dict = {}
        for i in range(self.col_count):
            dimensions = []

            for name, position in self.positions.items():

                col_id, row_id = name.split("-")
                if col_id == str(i):
                    obj = make_text(name, 0, 0, position["Text"], 1, (255, 255, 255, 255), align="CENTER")
                    dimensions.append(obj.dimensions)

                    x, y, z = obj.dimensions
                    dimension_dict[name] = [x, y, z]

            widths[str(i)] = max([x for x, y, z in dimensions])

        collection_cleanup("Collection")
        return widths, dimension_dict


PrismaPlot()
