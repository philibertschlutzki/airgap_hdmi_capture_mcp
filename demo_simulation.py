#!/usr/bin/env python3
"""
Demo Simulation for Vision-HID-Bridge
This script simulates the MCP Server loop without physical hardware.
It mocks the screen capture and HID injection to demonstrate the logic.
"""

import sys
import time
import os
import random
import logging
from unittest.mock import MagicMock

# 1. Setup Environment Mocks
print("--- Initializing Vision-HID-Bridge Simulation ---")
print("Loading mocks for OpenCV and PyTesseract...")

sys.modules['cv2'] = MagicMock()
sys.modules['pytesseract'] = MagicMock()
mock_cap = MagicMock()
mock_cap.isOpened.return_value = True
mock_cap.read.return_value = (True, "DUMMY_FRAME")
sys.modules['cv2'].VideoCapture.return_value = mock_cap

sys.path.append(os.path.abspath('control_node/src'))

# Import after mocks
from server import capture_screen_impl, inject_keystrokes_impl, execute_shortcut_impl, get_ocr_logs_impl, get_latest_screen_impl, scan_directory_impl
import server
import hid

# 2. Configure Mock Behaviors
# State Machine with specific behaviors
current_screen_state = "cmd_prompt"
screen_text_buffer = "C:\\Users\\Admin>"
layout_simulation_mode = "US" # The 'physical' keyboard layout of the target
# The 'injector' layout is what we THINK we are sending.

def mock_get_text(image, config=None):
    global screen_text_buffer
    return screen_text_buffer

server.pipeline.extract_text = mock_get_text
server.pipeline.encode_image = lambda x: f"[IMAGE_DATA]"

# Mock HID to update the buffer
def mock_type_text(text, delay_mean=0.1, delay_std=0.0):
    global screen_text_buffer, current_screen_state, layout_simulation_mode
    print(f"   [HID] Typing: '{text}'")

    # Simulate Layout Mismatch
    is_server_de = isinstance(server.injector.layout, hid.GermanISO)

    output_text = ""
    for char in text:
        mapped_char = char
        if layout_simulation_mode == "US" and is_server_de:
            if char == 'z': mapped_char = 'y'
            elif char == 'y': mapped_char = 'z'
            elif char == '-': mapped_char = '/'

        output_text += mapped_char

    screen_text_buffer += output_text

server.injector.type_text = mock_type_text

def mock_press_sequence(mods, key):
    global screen_text_buffer
    print(f"   [HID] Shortcut: {mods} + {key}")
    if "ENTER" in key:
        screen_text_buffer += "\nC:\\Users\\Admin>"

    if "c" in key.lower() and "CTRL" in mods:
         print("   [SIM] Ctrl+C received, clearing buffer")
         screen_text_buffer = "C:\\Users\\Admin>" # Clear screen

server.injector.press_sequence = mock_press_sequence

# 3. Run the Agent Loop Scenario
def run_scenario():
    print("\n--- Starting Agent Scenario ---")

    # Step 1: Type with verification (feature 1)
    print("\n1. Testing Visual Verification...")
    try:
        inject_keystrokes_impl("echo test_verification", verify=True)
        print("   [SUCCESS] Verification passed.")
    except Exception as e:
        print(f"   [FAILURE] Verification failed: {e}")

    execute_shortcut_impl([], "ENTER")

    # Step 2: Directory Scan (feature 3)
    print("\n2. Testing Directory Scan...")
    # Mocking the output of a dir command
    global screen_text_buffer
    # Update mock buffer with tricky filenames
    screen_text_buffer += "\nVolume in drive C has no label.\n Directory of C:\\Users\\Admin\n\n01/01/2023  12:00 PM    <DIR>          .\n01/01/2023  12:00 PM    <DIR>          ..\n01/01/2023  12:00 PM                10 file1.txt\n01/01/2023  12:00 PM                20 config with spaces.json\n               2 File(s)             30 bytes\n"

    try:
        result = scan_directory_impl(".")
        print(f"   [SCAN] Result: {result}")

        # Verify parser logic
        import json
        last_log = sorted(os.listdir("logs"))[-1]
        with open(f"logs/{last_log}", 'r') as f:
            data = json.load(f)
            file_names = [f['name'] for f in data['files']]
            print(f"   [DEBUG] Files found: {file_names}")

            if "config with spaces.json" in file_names and "bytes" not in file_names:
                print("   [SUCCESS] Parser handled spaces and summary correctly.")
            else:
                print("   [FAILURE] Parser Logic Error.")

    except Exception as e:
         print(f"   [SCAN] Failed: {e}")

    print("\n--- Scenario Complete ---")

if __name__ == "__main__":
    run_scenario()
