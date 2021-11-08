from blendSupports.Nodes.emission_node import create_emission_node
import bpy

from miscSupports import chunk_list
from csvObject import CsvObject
from dataclasses import dataclass


# Csv contains Coefficient-Scale
# Create Box plots, which is a square for each row, as an object
# Iterate row by box height, set externally (which is just the spawn of the square diameter)
# Each row should be scaled by the scale value, and colour from the coefficient

# Scale values
# Just scale the square, although it will be easier for the dom tree if we check if == 0, then just skip


# Colour values
# We have 0-0.5, which we times by 2
# We Also have 0.5 to 1, which we subtract 0.5 from THEN times by 2
# Lessor values are invest, so that the darkest shade is 0 with the lightest one.
# Greater values are keep as 0-1, with 0 being light and 1 being darkest

# Additional
# To avoid having alpha issues, we might want to create a background for this one
# We may also want to create a border grid of small squares scaled horizontally (or vertically) and colour a set shade
# These should be joined at the end though, otherwise the dom tree will SUCK!

# Link materials of background so that it is all adjustable.


@dataclass
class Element:
    raw_coefficient: float
    scalar: float

    def coefficient_colour(self, scale_adjust=0.85):
        """Coefficients are scaled so that it is """
        if self.raw_coefficient > 0.5:
            scalar = 1 - ((self.raw_coefficient - 0.5) * 2)
            return 1, scalar, (scalar * scale_adjust), 1
        else:
            scalar = self.raw_coefficient * 2
            return scalar * scale_adjust, scalar, 1, 1

    def border_scale(self, border_width):
        scale_size = self.scalar * (1 - border_width)
        return scale_size, scale_size, scale_size


class HeatMap:
    def __init__(self, args):
        self.root = args

        self.x_iterator = 0
        self.y_iterator = 0
        self.background_colour = (0.05, 0.05, 0.05, 1)
        self.scale_adjust = 0.85

        # Border width is 0.1-1
        self.border_width = 0.05
        self.iterator = 2 - self.border_width

        self.construct_grid()

    def construct_grid(self):
        for ri, row in enumerate(CsvObject(self.root, column_types=float).row_data):
            # Construct elements for each row
            elements = [Element(coefficient, scalar) for coefficient, scalar in chunk_list(row, 2)]

            [self.make_row(ri, ci, elem) for ci, elem in enumerate(elements)]

            self.x_iterator = 0
            self.y_iterator -= self.iterator

    def make_row(self, ri, ci, elem):
        # Make the background
        bg = self.make_square(f'Background_{ri}_{ci}', self.background_colour)
        self.make_border(bg)

        # If we need to make a square, as the result is not scaled to zero
        if elem.scalar != 0:
            # Make the grid square with a given border width
            square = self.make_square(f'R{ri}_C{ci}', elem.coefficient_colour(self.scale_adjust))
            square.scale = elem.border_scale(self.border_width)

        self.x_iterator += self.iterator

    def make_square(self, root_name, colour):
        """Make a grid square for the heat map or its background"""
        bpy.ops.mesh.primitive_plane_add(location=(self.x_iterator, self.y_iterator, 0))
        obj = bpy.context.object
        obj.name = root_name
        create_emission_node(obj, colour)
        return obj

    def make_border(self, obj):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.inset(thickness=self.border_width, depth=0)
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.editmode_toggle()
        obj.select_set(False)

    @staticmethod
    def join_borders():
        """Clean up the border individual objects into a single master object"""
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.collections['Collection'].objects:
            if 'Background' in obj.name:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()

        background = bpy.context.object
        background.name = 'Background'


if __name__ == '__main__':
    root = r"C:\Users\Samuel\PycharmProjects\AsthmaDisease\Figures\LogitForest\HeatMap\Actual\MS_Age1.csv"

    HeatMap(root)
