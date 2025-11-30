"""
Automated Keyboard Layout Detection Module.

This module detects the active keyboard layout of the target system
by injecting specific test characters and observing the output via OCR.
"""

import time
import logging

class LayoutDetector:
    """
    Automates the detection of the target system's keyboard layout (e.g., US vs DE).

    This works by injecting characters that have different positions on different layouts
    (like 'z' and 'y') and observing what character actually appears on the screen via OCR.
    """
    def __init__(self, injector, capture_func):
        """
        Args:
            injector (KeyInjector): The instance used to type keys.
            capture_func (Callable): A function that captures the screen text (OCR).
        """
        self.injector = injector
        self.capture_func = capture_func

    def detect(self) -> str:
        """
        Runs the layout detection heuristic.

        Heuristic:
        - Type 'z'.
        - If 'z' appears: Likely US or UK (QWERTY).
        - If 'y' appears: Likely German (QWERTZ) because the 'z' key is in the 'y' position on US hardware maps.

        Returns:
            str: The detected layout code ("US", "DE", or "UNKNOWN").
        """
        logging.info("Starting Keyboard Layout Detection...")

        # We need to type characters that vary significantly between layouts.
        # US vs DE:
        # z <-> y

        # Test 1: Check Y/Z (QWERTZ vs QWERTY)
        # We send 'z'.
        # On US: Output 'z'
        # On DE: Output 'y' (because 'z' key is at 'y' position)

        test_char = 'z'
        self.injector.type_text(test_char, delay_mean=0.1)
        time.sleep(1.0)

        text = self.capture_func(mode="ocr_text")
        logging.debug(f"Layout Detect 'z' -> Saw '{text}'")

        if 'y' in text.lower():
            # We sent 'z' (pos Z), but got 'y'.
            # This implies the target interprets that position as 'y'.
            # That matches QWERTZ (DE).
            logging.info("Detected Layout: DE (QWERTZ)")
            return "DE"
        elif 'z' in text.lower():
            logging.info("Detected Layout: US/UK (QWERTY)")
            return "US" # Could be UK too

        # Fallback or inconclusive
        return "UNKNOWN"

    def apply_layout(self, layout_code: str):
        """
        Applies the detected layout to the KeyInjector.

        Args:
            layout_code (str): The code returned by detect() ("US", "DE").
        """
        if layout_code == "DE":
            from .hid import GermanISO
            logging.info("Applying GermanISO Layout")
            self.injector.layout = GermanISO()
        elif layout_code == "US":
             from .hid import USLayout
             logging.info("Applying US Layout")
             self.injector.layout = USLayout()
        else:
            logging.warning(f"Unknown layout code {layout_code}, keeping current.")
