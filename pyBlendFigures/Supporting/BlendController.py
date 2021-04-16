from miscSupports import validate_path
from pathlib import Path


class BlendController:
    def __init__(self, blender_path, working_directory):
        blender_path = validate_path(blender_path)
        self.blend_path = str(Path(blender_path).absolute())
        self.base_file = str(Path(Path(__file__).parent, "Base.blend").absolute())
        self.working_dir = validate_path(working_directory)

