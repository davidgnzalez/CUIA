import unittest
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ar_rendering.scene_renderer import PyrenderModelViewer

class TestPorscheGLBTextures(unittest.TestCase):
    def test_porsche_has_textures(self):
        viewer = PyrenderModelViewer()
        car = {"name": "Porsche 911", "model_path": "porsche-911/911.glb"}
        self.assertTrue(viewer.load_car_model(car))
        meshes = viewer.current_model
        self.assertIsInstance(meshes, list)
        found = False
        for mesh in meshes:
            for prim in getattr(mesh, "primitives", []):
                mat = prim.material
                if getattr(mat, "baseColorTexture", None) is not None:
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)

if __name__ == "__main__":
    unittest.main()
