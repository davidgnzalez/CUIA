import sys
import pathlib
import types
import json

# Ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Stub heavy rendering modules before importing AppManager
ar_rendering_pkg = types.ModuleType('ar_rendering')
sys.modules['ar_rendering'] = ar_rendering_pkg
sys.modules['ar_rendering.scene_renderer'] = types.ModuleType('scene_renderer')
sys.modules['ar_rendering.ar_menu'] = types.ModuleType('ar_menu')
# Provide minimal classes referenced by AppManager
sys.modules['ar_rendering.ar_menu'].ARMenu = type('ARMenu', (), {})
sys.modules['ar_rendering.scene_renderer'].PyrenderModelViewer = type(
    'PyrenderModelViewer', (), {}
)

from core.app_manager import AppManager  # noqa: E402


def test_load_user_id_map(tmp_path):
    file_path = tmp_path / "user_id_map.json"
    data = {"alice": "1", "bob": 2}
    file_path.write_text(json.dumps(data))

    am = object.__new__(AppManager)
    am.user_id_map_path = str(file_path)

    result = AppManager._load_user_id_map(am)

    assert result == {"alice": 1, "bob": 2}
    assert all(isinstance(v, int) for v in result.values())
