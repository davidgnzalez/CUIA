import unittest
import pathlib
import trimesh


class TestPorscheGLBTextures(unittest.TestCase):
    def test_porsche_has_textures(self):
        root_dir = pathlib.Path(__file__).resolve().parents[1]
        model_path = (
            root_dir / "assets" / "3d_models" / "porsche-911" / "911.glb"
        )
        loaded = trimesh.load(model_path, process=True)
        if isinstance(loaded, trimesh.Scene):
            meshes = list(loaded.geometry.values())
        else:
            meshes = [loaded]

        found = False
        for mesh in meshes:
            if hasattr(mesh.visual, "material"):
                mat = mesh.visual.material
                if getattr(mat, "baseColorTexture", None) is not None:
                    found = True
                    break
        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
