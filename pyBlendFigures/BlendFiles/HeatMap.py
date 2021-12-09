import bpy

from miscSupports import load_json, deep_get, terminal_time


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

        self.data = load_json(args)
        self.bg_material = self._make_material('Background', self.background_colour)

        self._load_materials()
        [self.construct_grid(key) for key in self.data["Process"]]

    # TODO Make this part of blendExternals
    @staticmethod
    def _load_materials():
        mat_file = "C:/Users/Samuel/PycharmProjects/pyBlendFigures/pyBlendFigures/Controller/Materials/CoolToWarm.blend"
        with bpy.data.libraries.load(mat_file, link=False) as (data_from, data_to):
            data_to.materials = data_from.materials

    def construct_grid(self, data_key):
        """Construct the grid for this current key"""
        # Create the collection for this data_key
        collection = bpy.data.collections.new("".join(data_key))
        collection_name = collection.name
        bpy.context.scene.collection.children.link(collection)

        # For each row, make each column entry, then iterate down on y
        for row_name, row_values in deep_get(self.data, data_key).items():
            [self.make_row(row_name, column_name, collection_name, column_values)
             for column_name, column_values in row_values.items()]

            self.x_iterator = 0
            self.y_iterator -= self.iterator

        # Join border meshes within this collection
        self.join_borders(collection_name)
        self.y_iterator -= self.iterator
        print(f"Finished {collection_name} at {terminal_time()}")

    def _make_row_entry(self, row_type, row_name, column_name, collection_name, colour_mat):
        """Make the row as a square, append a material to it, then move it to relevant collection"""
        # Make the background, add an emission node for background colour
        row = self.make_square(f'{row_type}_{row_name}_{column_name}')
        row.data.materials.append(colour_mat)

        # Move the object to the relevant collection
        bpy.data.collections[collection_name].objects.link(row)
        bpy.context.scene.collection.objects.unlink(row)
        return row

    def _make_background(self, row_name, column_name, collection_name):
        """Make the background by cutting out an inset in a square"""
        self.make_border(self._make_row_entry("Background", row_name, column_name, collection_name, self.bg_material))

    def _make_coefficient_square(self, row_name, column_name, collection_name, column_values):
        """Make and scale the coefficient squares"""

        colour = bpy.data.materials.get(str(column_values['colour']))
        square = self._make_row_entry("R", row_name, column_name, collection_name, colour)
        square.scale = self._square_border_scale(column_values['scale'])

    def _square_border_scale(self, scale):
        """Scale the square, adjusted on bordered width, returned as tuple as is required for blender"""
        scale_size = scale * (1 - self.border_width)
        return scale_size, scale_size, scale_size

    def make_row(self, row_name, column_name, collection_name, column_values):

        # Make the background
        self._make_background(row_name, column_name, collection_name)

        # If the scale is not zero we therefore need to make a square for the coefficient value
        if column_values['scale'] != 0:
            self._make_coefficient_square(row_name, column_name, collection_name, column_values)

        self.x_iterator += self.iterator

    def make_square(self, root_name):
        """Make a grid square for the heat map or its background"""
        bpy.ops.mesh.primitive_plane_add(location=(self.x_iterator, self.y_iterator, 0))
        obj = bpy.context.object
        obj.name = root_name
        return obj

    def make_border(self, obj):
        """Inset a face of with 'border_width' then delete it"""
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.inset(thickness=self.border_width, depth=0)
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.editmode_toggle()
        obj.select_set(False)

    @staticmethod
    def join_borders(collection_name):
        """Clean up the border individual objects into a single master object"""
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.collections[collection_name].objects:
            if 'Background' in obj.name:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()

        background = bpy.context.object
        background.name = 'Background'

    # TODO: move to blendSupports
    @staticmethod
    def _make_material(mat_name, colour, strength=1):

        mat = (bpy.data.materials.get(mat_name) or
               bpy.data.materials.new(mat_name))

        # Enable 'Use nodes':
        mat.use_nodes = True

        # clear all nodes to start clean
        nodes = mat.node_tree.nodes
        nodes.clear()

        # create emission node
        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs[0].default_value = colour
        node_emission.inputs[1].default_value = strength
        node_emission.location = 0, 0

        # create output node
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        node_output.location = 400, 0

        node = nodes.new('ShaderNodeBsdfDiffuse')
        node.location = (100, 100)

        # link nodes
        links = mat.node_tree.links
        links.new(node_emission.outputs[0], node_output.inputs[0])

        return mat


if __name__ == '__main__':
    HeatMap(r"C:\Users\Samuel\PycharmProjects\AsthmaDisease\Figures\HeatMaps\HeatMapDictLogit.txt")


