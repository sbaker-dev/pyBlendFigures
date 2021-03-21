from pathlib import Path


class BlendController:
    def __init__(self, blender_path, working_directory):
        self.blend_path = str(Path(blender_path).absolute())
        self.base_file = str(Path(Path(__file__).parent, "Base.blend").absolute())
        self.working_dir = working_directory

