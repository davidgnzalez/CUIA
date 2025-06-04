import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ar_rendering.ar_menu import ARMenu  # noqa: E402


class TestARMenuEmpty(unittest.TestCase):
    def test_handle_selection_empty_menu(self):
        menu = ARMenu()
        menu.menu_items = []
        # Should not raise and should return None
        result = menu.handle_selection(ord("1"))
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
