from fastmcp import FastMCP
from typing import List, Optional
import time
import threading
try:
    from .vision import ScreenCapture, VisionPipeline
    from .hid import KeyInjector
    from .layout_detection import LayoutDetector
    from .data_harvester import DataHarvester
except ImportError:
    from vision import ScreenCapture, VisionPipeline
    from hid import KeyInjector
    from layout_detection import LayoutDetector
    from data_harvester import DataHarvester

# Initialize Global Components
injector = KeyInjector()
capture = ScreenCapture()
pipeline = VisionPipeline()
layout_detector = LayoutDetector(injector, lambda mode: capture_screen_impl(mode=mode))
harvester = DataHarvester()

# Configuration
ENABLE_FULL_LOGGING = True

# State for resources
latest_ocr_log = []
latest_screen_base64 = ""

# Create MCP Server
mcp = FastMCP("Vision-HID-Bridge")

# --- Implementation Logic (Testable) ---

def capture_screen_impl(mode: str = "ocr_text", region: Optional[List[int]] = None) -> str:
    """
    Core implementation for capturing screen content.

    This function interacts with the hardware (OpenCV) to grab a frame, optionally crops it,
    and then processes it based on the requested mode.

    Args:
        mode (str): Determines the output format.
            - "raw_base64": Returns the image frame encoded as a Base64 JPEG string.
            - "ocr_text": Returns the text extracted from the image using Tesseract OCR.
        region (Optional[List[int]]): A list of 4 integers [x, y, width, height] defining
            a sub-region of the screen to capture. Useful for focusing on specific UI elements.

    Returns:
        str: The requested data (text or base64 string) or an error message.
    """
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

                # Global Logging (Feature 3)
                if ENABLE_FULL_LOGGING:
                    harvester.log_ocr_stream(text)

            return text

        else:
            return "Error: Unknown mode"

    except Exception as e:
        return f"Error capturing screen: {str(e)}"

def inject_keystrokes_impl(text: str, delay_ms: int = 20, verify: bool = True) -> str:
    """
    Core implementation for typing text.

    Simulates human-like typing by adding small random delays between keystrokes.
    Can optionally verify if the text appeared on the screen using OCR.

    Args:
        text (str): The string to type.
        delay_ms (int): Mean delay between keystrokes in milliseconds.
        verify (bool): If True, the system will type, wait, capture the screen, and check
                       if the typed text is present. If not, it retries up to 3 times.

    Returns:
        str: Success message or error details.
    """
    try:
        delay_sec = float(delay_ms) / 1000.0
        delay_std = delay_sec * 0.3

        if not verify:
            injector.type_text(text, delay_mean=delay_sec, delay_std=delay_std)
            return f"Successfully typed {len(text)} characters."

        # Verification Loop
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            # Type
            injector.type_text(text, delay_mean=delay_sec, delay_std=delay_std)

            # Wait for text to appear (adjust based on system lag)
            time.sleep(1.0)

            # Check
            screen_text = capture_screen_impl(mode="ocr_text")

            # Simple check: Is the text loosely present?
            # We strip whitespace to avoid issues
            if text.strip() in screen_text:
                return f"Successfully typed and verified {len(text)} characters on attempt {attempt}."

            latest_ocr_log.append(f"[VERIFY-FAIL] Attempt {attempt}: Typed '{text}' but not found in OCR.")

            # Robustness: Try to clear the line before retrying (Ctrl+C)
            # This prevents "echo heecho hello"
            try:
                injector.press_sequence(['CTRL'], 'c')
                time.sleep(0.2)
            except Exception:
                pass # Ignore if shortcut fails

            time.sleep(0.5)

        raise RuntimeError(f"Failed to verify text '{text}' after {max_attempts} attempts.")

    except Exception as e:
        return f"Error injecting keystrokes: {str(e)}"

def execute_shortcut_impl(modifiers: List[str], key: str) -> str:
    """
    Core implementation for keyboard shortcuts.

    Args:
        modifiers (List[str]): Keys to hold down (e.g., ['CTRL', 'ALT']).
        key (str): The main key to press (e.g., 'DELETE').

    Returns:
        str: Status message.
    """
    try:
        injector.press_sequence(modifiers, key)
        return f"Executed shortcut: {'+'.join(modifiers)} + {key}"
    except Exception as e:
        return f"Error executing shortcut: {str(e)}"

def get_latest_screen_impl() -> str:
    return latest_screen_base64

def get_ocr_logs_impl() -> str:
    return "\n".join(latest_ocr_log)

def scan_directory_impl(path: str) -> str:
    """
    Active tool to scan a directory and save structure to JSON.

    This function:
    1. Injects the `dir` command into the target system.
    2. Waits for the command to finish.
    3. Captures the screen output via OCR.
    4. Parses the text to identify files and directories.
    5. Saves the structure as a JSON file in the `logs/` directory.

    Args:
        path (str): The directory to scan.

    Returns:
        str: Status message indicating success and the path to the saved JSON file.
    """
    try:
        # 1. Inject Command
        # Detect OS style? Assuming Windows CMD for now based on prompt context ("dir")
        # To be safe, we could try to detect or use both?
        # User prompt mentioned "dir usw".

        cmd = f"dir \"{path}\""
        injector.type_text(cmd, delay_mean=0.05)
        injector.press_key("\n")

        # 2. Wait for output
        time.sleep(2.0) # Wait for valid output

        # 3. Capture
        text = capture_screen_impl(mode="ocr_text")

        # 4. Parse & Save
        structure = harvester.parse_directory_listing(text)
        saved_path = harvester.save_scan(path, structure)

        return f"Scan complete. Structure saved to {saved_path}. Found {len(structure.get('files', []))} files."

    except Exception as e:
        return f"Error scanning directory: {e}"


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
def inject_keystrokes(text: str, delay_ms: int = 20, verify: bool = True) -> str:
    """
    Types text into the target system with optional visual verification.

    Args:
        text: The string to type.
        delay_ms: Average delay between keystrokes in milliseconds.
        verify: If True, attempts to verify the text appeared on screen (retries 3 times).
    """
    return inject_keystrokes_impl(text, delay_ms, verify)

@mcp.tool()
def execute_shortcut(modifiers: List[str], key: str) -> str:
    """
    Executes a keyboard shortcut (e.g., Ctrl+Alt+Del).

    Args:
        modifiers: List of modifiers ['CTRL', 'ALT', 'SHIFT', 'GUI', 'RALT'].
        key: The key to press (e.g., 'DELETE', 'ENTER', 'T').
    """
    return execute_shortcut_impl(modifiers, key)

@mcp.tool()
def scan_directory(path: str) -> str:
    """
    Scans a directory on the target system using OCR and saves the structure as JSON.
    Currently assumes Windows CMD ('dir' command).

    Args:
        path: The directory path to scan (e.g., "C:\\Users").
    """
    return scan_directory_impl(path)

@mcp.resource("system://screen/latest")
def get_latest_screen() -> str:
    """Returns the most recently captured screen as base64."""
    return get_latest_screen_impl()

@mcp.resource("system://logs/ocr")
def get_ocr_logs() -> str:
    """Returns the last 100 lines of OCR logs."""
    return get_ocr_logs_impl()

def detect_layout_at_startup():
    """
    Attempts to detect the layout at server startup.
    This is best-effort. If the screen is not interactive (e.g. lock screen),
    it might fail or produce odd results.
    """
    try:
        # Give some time for system to settle or user to prep
        # time.sleep(2)

        # We should check if we can type.
        # But for now, we just run the detection logic.
        print("Running startup layout detection...")
        layout_code = layout_detector.detect()
        layout_detector.apply_layout(layout_code)
    except Exception as e:
        print(f"Startup layout detection failed: {e}")

def run():
    detect_layout_at_startup()
    mcp.run()
