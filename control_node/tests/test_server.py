import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock cv2/pytesseract again for server imports
sys.modules['cv2'] = MagicMock()
sys.modules['pytesseract'] = MagicMock()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import server

class TestServer(unittest.TestCase):
    def setUp(self):
        # Reset globals
        server.latest_ocr_log = []
        server.latest_screen_base64 = ""

        # Mock the helper objects
        self.mock_capture = MagicMock()
        self.mock_injector = MagicMock()
        self.mock_pipeline = MagicMock()

        server.capture = self.mock_capture
        server.injector = self.mock_injector
        server.pipeline = self.mock_pipeline

        # Setup returns
        import numpy as np
        self.mock_capture.capture_frame.return_value = np.zeros((10,10,3))
        self.mock_pipeline.encode_image.return_value = "base64data"
        self.mock_pipeline.extract_text.return_value = "C:\\Windows\\system32>"

    def test_tool_capture_screen_ocr(self):
        # Call implementation directly to bypass FastMCP decorators
        result = server.capture_screen_impl(mode="ocr_text")
        self.assertEqual(result, "C:\\Windows\\system32>")
        self.assertIn("C:\\Windows\\system32>", server.latest_ocr_log[0])
        self.assertEqual(server.latest_screen_base64, "base64data")

    def test_tool_inject_keystrokes(self):
        # We need to make sure verify logic passes.
        # It waits for OCR to contain text.
        self.mock_pipeline.extract_text.return_value = "echo hello"

        res = server.inject_keystrokes_impl("echo hello", verify=True)
        self.assertIn("Successfully typed", res)
        self.mock_injector.type_text.assert_called()

    def test_tool_inject_keystrokes_no_verify(self):
        res = server.inject_keystrokes_impl("echo hello", verify=False)
        self.assertIn("Successfully typed", res)
        self.mock_injector.type_text.assert_called()

    def test_tool_execute_shortcut(self):
        res = server.execute_shortcut_impl(['CTRL', 'ALT'], 'DELETE')
        self.assertIn("Executed shortcut", res)
        self.mock_injector.press_sequence.assert_called_with(['CTRL', 'ALT'], 'DELETE')

    def test_resources(self):
        server.latest_screen_base64 = "test_img"
        self.assertEqual(server.get_latest_screen_impl(), "test_img")

        server.latest_ocr_log = ["log1", "log2"]
        self.assertIn("log1\nlog2", server.get_ocr_logs_impl())

if __name__ == '__main__':
    unittest.main()
