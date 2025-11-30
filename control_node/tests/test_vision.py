import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import numpy as np

# Mock cv2 and pytesseract BEFORE importing vision
# We need to assign them to sys.modules so `import cv2` works inside vision.py
# AND we need to ensure that when `from vision import ...` happens, it sees these mocks.

mock_cv2 = MagicMock()
mock_pytesseract = MagicMock()
sys.modules['cv2'] = mock_cv2
sys.modules['pytesseract'] = mock_pytesseract

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Force reload of vision to ensure it picks up the mocks if it was already imported
import vision
import importlib
importlib.reload(vision)

from vision import VisionPipeline, ScreenCapture

class TestVision(unittest.TestCase):
    def setUp(self):
        self.pipeline = VisionPipeline()
        self.capture = ScreenCapture()

    def test_preprocess(self):
        # Create a dummy image
        img = np.zeros((100, 100, 3), dtype=np.uint8)

        # Access the global mock_cv2 we created
        global mock_cv2

        # Setup cv2 mocks to return something
        mock_cv2.cvtColor.return_value = img
        mock_cv2.bitwise_not.return_value = img
        mock_cv2.resize.return_value = img
        mock_cv2.threshold.return_value = (0.0, img)

        # Mock constants used in preprocess
        mock_cv2.COLOR_BGR2GRAY = 6
        mock_cv2.INTER_CUBIC = 2
        mock_cv2.THRESH_BINARY = 0
        mock_cv2.THRESH_OTSU = 8

        # When mocking modules in sys.modules, sometimes imports in SUT need reload
        # but here we rely on existing import.

        res = self.pipeline.preprocess_for_ocr(img)

        # Check if chain was called
        mock_cv2.cvtColor.assert_called()
        mock_cv2.bitwise_not.assert_called()
        mock_cv2.threshold.assert_called()

    def test_ocr_call(self):
        global mock_pytesseract
        img = np.zeros((100, 100), dtype=np.uint8)
        mock_pytesseract.image_to_string.return_value = "Detected Text"

        text = self.pipeline.extract_text(img)
        self.assertEqual(text, "Detected Text")
        mock_pytesseract.image_to_string.assert_called()

    def test_capture_lifecycle(self):
        global mock_cv2
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True

        # Ensure read always returns (True, frame)
        valid_frame = (True, np.zeros((10,10,3)))
        mock_cap.read.return_value = valid_frame

        # Configure return value of VideoCapture constructor
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.VideoCapture.side_effect = None

        # Mock the constants used in set()
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_BUFFERSIZE = 38

        # Force re-open to pick up the mock
        self.capture.cap = None

        frame = self.capture.capture_frame()
        self.assertIsNotNone(frame)
        self.capture.release()
        mock_cap.release.assert_called()

if __name__ == '__main__':
    unittest.main()
