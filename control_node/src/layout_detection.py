import time
import logging

class LayoutDetector:
    def __init__(self, injector, capture_func):
        self.injector = injector
        self.capture_func = capture_func

    def detect(self) -> str:
        """
        Attempts to detect the keyboard layout by typing specific characters
        and checking the OCR output.
        """
        print("Starting Keyboard Layout Detection...")

        # We need to type characters that vary significantly between layouts.
        # US vs DE:
        # z <-> y
        # - <-> / (slash key)
        # @ (Shift+2 on US, AltGr+Q on DE)

        # Test 1: Check Y/Z (QWERTZ vs QWERTY)
        # We send 'z'.
        # On US: Output 'z'
        # On DE: Output 'y' (because 'z' key is at 'y' position)

        test_char = 'z'
        self.injector.type_text(test_char, delay_mean=0.1)
        time.sleep(1.0)

        text = self.capture_func(mode="ocr_text")
        print(f"DEBUG: Layout Detect 'z' -> Saw '{text}'")

        if 'y' in text.lower():
            # We sent 'z' (pos Z), but got 'y'.
            # This implies the target interprets that position as 'y'.
            # That matches QWERTZ (DE).
            print("Detected Layout: DE (QWERTZ)")
            return "DE"
        elif 'z' in text.lower():
            print("Detected Layout: US/UK (QWERTY)")
            return "US" # Could be UK too

        # Fallback or inconclusive
        return "UNKNOWN"

    def apply_layout(self, layout_code: str):
        if layout_code == "DE":
            from .hid import GermanISO
            print("Applying GermanISO Layout")
            self.injector.layout = GermanISO()
        elif layout_code == "US":
             # We need a US Layout class. For now, assuming default mapping in hid.py needs adjustment
             # if we only have GermanISO implemented.
             # Wait, `hid.py` has a base `Layout` class. We should implement `USLayout`.
             from .hid import USLayout
             print("Applying US Layout")
             self.injector.layout = USLayout()
        else:
            print(f"Unknown layout code {layout_code}, keeping current.")
