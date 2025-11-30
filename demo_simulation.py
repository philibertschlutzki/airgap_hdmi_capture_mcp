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
# Mock VideoCapture to return dummy frames for flushing
mock_cap = MagicMock()
mock_cap.isOpened.return_value = True
# Must return (True, frame) for our logic which checks isinstance(tuple)
mock_cap.read.return_value = (True, "DUMMY_FRAME")
sys.modules['cv2'].VideoCapture.return_value = mock_cap

# Setup paths
sys.path.append(os.path.abspath('control_node/src'))

# Import after mocks
from server import capture_screen_impl, inject_keystrokes_impl, execute_shortcut_impl, get_ocr_logs_impl, get_latest_screen_impl
import server

# 2. Configure Mock Behaviors
# We will simulate a state machine for the screen content
current_screen_state = "locked"

def mock_get_text(image, config=None):
    global current_screen_state
    if current_screen_state == "locked":
        return "Windows 10\nPress Ctrl+Alt+Del to unlock"
    elif current_screen_state == "login":
        return "Password: _"
    elif current_screen_state == "desktop":
        return "C:\\Users\\Admin>"
    elif current_screen_state == "cmd_open":
        return "C:\\Users\\Admin> ipconfig\nIPv4 Address. . . . : 192.168.1.50"
    return "Unknown State"

server.pipeline.extract_text = mock_get_text
server.pipeline.encode_image = lambda x: f"[IMAGE_DATA_STATE_{current_screen_state}]"

# Mock HID to change state
def mock_type_text(text, delay_mean=0.1, delay_std=0.0):
    global current_screen_state
    print(f"   [HID] Typing: '{text}'")
    if current_screen_state == "login" and "secret" in text:
        print("   [SIM] Password correct. Logging in...")
        current_screen_state = "desktop"
    elif current_screen_state == "desktop" and "ipconfig" in text:
        current_screen_state = "cmd_open"

def mock_press_sequence(mods, key):
    global current_screen_state
    print(f"   [HID] Shortcut: {mods} + {key}")
    if current_screen_state == "locked" and "CTRL" in mods and "ALT" in mods and "DELETE" in key:
        print("   [SIM] Unlock sequence received.")
        current_screen_state = "login"

server.injector.type_text = mock_type_text
server.injector.press_sequence = mock_press_sequence

# 3. Run the Agent Loop Scenario
def run_scenario():
    print("\n--- Starting Agent Scenario ---")

    # Step 1: Observe
    print("\n1. Agent captures screen...")
    text = capture_screen_impl(mode="ocr_text")
    print(f"   [VISION] Saw: {text.replace(chr(10), ' | ')}")

    if "Press Ctrl+Alt+Del" in text:
        # Step 2: Act (Unlock)
        print("\n2. Agent decides to unlock...")
        execute_shortcut_impl(['CTRL', 'ALT'], 'DELETE')

        # Verify
        text = capture_screen_impl(mode="ocr_text")
        print(f"   [VISION] Saw: {text}")

    if "Password" in text:
        # Step 3: Login
        print("\n3. Agent enters credentials...")
        inject_keystrokes_impl("super_secret_password")
        inject_keystrokes_impl("{ENTER}") # Simulating enter (logic handled in mock for simplicity just by text content)

        # Verify
        text = capture_screen_impl(mode="ocr_text")
        print(f"   [VISION] Saw: {text}")

    if "Admin>" in text:
        # Step 4: Run Command
        print("\n4. Agent runs ipconfig...")
        inject_keystrokes_impl("ipconfig")

        # Verify
        text = capture_screen_impl(mode="ocr_text")
        print(f"   [VISION] Saw: {text.replace(chr(10), ' | ')}")

    print("\n--- Scenario Complete ---")
    print(f"Final OCR Logs:\n{get_ocr_logs_impl()}")

if __name__ == "__main__":
    run_scenario()
