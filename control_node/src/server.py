from fastmcp import FastMCP
from typing import List, Optional
import time
import threading
try:
    from .vision import ScreenCapture, VisionPipeline
    from .hid import KeyInjector
except ImportError:
    from vision import ScreenCapture, VisionPipeline
    from hid import KeyInjector

# Initialize Global Components
injector = KeyInjector()
capture = ScreenCapture()
pipeline = VisionPipeline()

# State for resources
latest_ocr_log = []
latest_screen_base64 = ""

# Create MCP Server
mcp = FastMCP("Vision-HID-Bridge")

# --- Implementation Logic (Testable) ---

def capture_screen_impl(mode: str = "ocr_text", region: Optional[List[int]] = None) -> str:
    global latest_screen_base64

    try:
        frame = capture.capture_frame()

        # Crop if requested
        if region and len(region) == 4:
            x, y, w, h = region
            if hasattr(frame, 'shape'):
                h_img, w_img = frame.shape[:2]
            else:
                 h_img, w_img = 1080, 1920 # Default or Mock

            x = max(0, x)
            y = max(0, y)
            w = min(w, w_img - x)
            h = min(h, h_img - y)
            frame = frame[y:y+h, x:x+w]

        # Update latest resource
        latest_screen_base64 = pipeline.encode_image(frame)

        if mode == "raw_base64":
            return latest_screen_base64

        elif mode == "ocr_text":
            processed = pipeline.preprocess_for_ocr(frame)
            text = pipeline.extract_text(processed)

            # Update Log
            if text.strip():
                latest_ocr_log.append(f"[{time.strftime('%H:%M:%S')}] {text[:50]}...")
                if len(latest_ocr_log) > 100:
                    latest_ocr_log.pop(0)

            return text

        else:
            return "Error: Unknown mode"

    except Exception as e:
        return f"Error capturing screen: {str(e)}"

def inject_keystrokes_impl(text: str, delay_ms: int = 20) -> str:
    try:
        delay_sec = float(delay_ms) / 1000.0
        delay_std = delay_sec * 0.3

        injector.type_text(text, delay_mean=delay_sec, delay_std=delay_std)
        return f"Successfully typed {len(text)} characters."
    except Exception as e:
        return f"Error injecting keystrokes: {str(e)}"

def execute_shortcut_impl(modifiers: List[str], key: str) -> str:
    try:
        injector.press_sequence(modifiers, key)
        return f"Executed shortcut: {'+'.join(modifiers)} + {key}"
    except Exception as e:
        return f"Error executing shortcut: {str(e)}"

def get_latest_screen_impl() -> str:
    return latest_screen_base64

def get_ocr_logs_impl() -> str:
    return "\n".join(latest_ocr_log)


# --- MCP Tool Definitions ---

@mcp.tool()
def capture_screen(mode: str = "ocr_text", region: Optional[List[int]] = None) -> str:
    """
    Captures the current screen content from the target system.

    Args:
        mode: Return mode. "raw_base64" for image data, "ocr_text" for extracted text.
        region: Optional [x, y, width, height] to crop.
    """
    return capture_screen_impl(mode, region)

@mcp.tool()
def inject_keystrokes(text: str, delay_ms: int = 20) -> str:
    """
    Types text into the target system.

    Args:
        text: The string to type.
        delay_ms: Average delay between keystrokes in milliseconds.
    """
    return inject_keystrokes_impl(text, delay_ms)

@mcp.tool()
def execute_shortcut(modifiers: List[str], key: str) -> str:
    """
    Executes a keyboard shortcut (e.g., Ctrl+Alt+Del).

    Args:
        modifiers: List of modifiers ['CTRL', 'ALT', 'SHIFT', 'GUI', 'RALT'].
        key: The key to press (e.g., 'DELETE', 'ENTER', 'T').
    """
    return execute_shortcut_impl(modifiers, key)

@mcp.resource("system://screen/latest")
def get_latest_screen() -> str:
    """Returns the most recently captured screen as base64."""
    return get_latest_screen_impl()

@mcp.resource("system://logs/ocr")
def get_ocr_logs() -> str:
    """Returns the last 100 lines of OCR logs."""
    return get_ocr_logs_impl()

def run():
    mcp.run()
