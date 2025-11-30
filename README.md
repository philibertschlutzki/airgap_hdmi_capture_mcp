# Vision-HID-Bridge

**Vision-HID-Bridge** is an autonomous agent capability system designed to bridge the air-gap in hardened environments. It allows an AI agent to see (via HDMI capture) and act (via USB Keyboard emulation) on a physical computer without a network connection.

This project implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) to expose these hardware capabilities to an LLM.

## 🚀 Features

*   **HDMI Screen Capture:** Real-time visual feedback using standard USB HDMI capture cards.
*   **Keystroke Injection:** Emulates a standard USB Keyboard via Raspberry Pi Zero (USB Gadget Mode).
*   **OCR Integration:** Optimised text extraction for CLI environments (PowerShell, CMD).
*   **Human-Like Typing:** Implements Jitter and varying delays to avoid bot detection.
*   **Visual Validation Loop:** Automatically verifies if typed text appears on screen, with retry logic.
*   **Layout Auto-Detection:** Automatically infers the target system's keyboard layout (US/DE) on startup.
*   **Data Harvesting:** Active file system scanning tools and comprehensive OCR logging for audit trails.
*   **Standardized API:** Uses MCP to easily plug into Claude Desktop or other Agent Runtimes.

## 📦 Project Structure

```
/
├── control_node/           # Logic running on the Laptop/Controller
│   ├── src/
│   │   ├── main.py         # Entry point (not used in library mode)
│   │   ├── server.py       # MCP Server Definition
│   │   ├── vision.py       # OpenCV & OCR Pipeline
│   │   ├── hid.py          # USB HID Injection Logic
│   │   ├── layout_detection.py # Auto-detect keyboard layout
│   │   └── data_harvester.py   # OCR Logger and File Scanner
│   └── tests/              # Unit tests
├── interface_unit/         # Configuration for the Raspberry Pi Zero
│   ├── setup_gadget.sh     # Script to enable USB HID Gadget
│   ├── verify_pi_setup.sh  # Script to verify Pi configuration
│   └── usb_gadget.service  # Systemd service for auto-start
└── demo_simulation.py      # Script to demonstrate logic without hardware
```

## 🛠️ Hardware Setup

You need:
1.  **Raspberry Pi Zero W/2W:** Acts as the "keyboard".
2.  **USB HDMI Capture Card:** Acts as the "eyes".
3.  **Target PC:** The computer you want to control.
4.  **Control Node:** A laptop running the Python MCP server.

### 1. Raspberry Pi Zero Setup (Interface Unit)
The Pi Zero converts commands from the Control Node into USB Keystrokes.

1.  Flash Raspberry Pi OS Lite.
2.  Connect to the Pi via SSH.
3.  Copy `interface_unit/setup_gadget.sh` and `interface_unit/usb_gadget.service` to the Pi.
4.  Run setup:
    ```bash
    sudo cp setup_gadget.sh /usr/local/bin/
    sudo chmod +x /usr/local/bin/setup_gadget.sh
    sudo cp usb_gadget.service /etc/systemd/system/
    sudo systemctl enable usb_gadget.service
    sudo systemctl start usb_gadget.service
    ```
5.  **Verify Setup:**
    Use the provided verification script to ensure everything is correct:
    ```bash
    chmod +x interface_unit/verify_pi_setup.sh
    ./interface_unit/verify_pi_setup.sh
    ```
6.  Connect the Pi's **USB Data Port** to the Target PC.

### 2. Control Node Setup
The Control Node runs the intelligence.

1.  Connect the HDMI Capture Card to the Control Node (USB) and Target PC (HDMI).
2.  Connect the Pi Zero to the Control Node (via Serial GPIO or a separate USB-Ethernet adapter for control).
3.  Install dependencies:
    ```bash
    pip install -r control_node/requirements.txt
    ```
    *Note: You need `tesseract-ocr` installed on your system (e.g., `sudo apt install tesseract-ocr`).*

## 💻 Usage

### Running the MCP Server
Start the server to expose tools to your LLM.

```bash
# From the root directory
python3 -m control_node.src.main
```

> **Note:** For detailed instructions on setting up VLM Integration (Ollama) and configuration, please refer to [manual_mcp.md](manual_mcp.md).

### Tools Available
*   `capture_screen(mode="ocr_text")`: Returns the text on screen.
*   `inject_keystrokes(text="echo hello", verify=True)`: Types text with optional visual verification.
*   `execute_shortcut(modifiers=["CTRL", "ALT"], key="DELETE")`: Sends combinations.
*   `scan_directory(path=".")`: Active scanning tool that lists files, parses the output, and saves JSON structure to `logs/`.

### Logging
*   **OCR Logs:** By default, all recognized text is logged to `logs/ocr_stream_YYYY-MM-DD.log`.
*   **Scan Results:** JSON structures from `scan_directory` are saved to `logs/`.

## 🧪 Testing & Simulation

You can run the test suite or a simulation script that mocks the hardware.

```bash
# Run Unit Tests
python3 -m unittest discover control_node/tests

# Run Simulation Demo
python3 demo_simulation.py
```

## 🗺️ Feature Roadmap

### Phase 1: Foundation (Completed)
- [x] Basic USB HID Gadget Setup
- [x] Screen Capture via OpenCV
- [x] Text Extraction (OCR)
- [x] MCP Server Implementation

### Phase 2: Robustness & Reliability (Completed)
- [x] **Visual Validation Loop:** Automatically verify if a typed command appeared on screen.
- [x] **Layout Auto-Detection:** Infer keyboard layout (US/DE/UK) based on trial typing.
- [x] **Data Harvesting:** Structure OCR output into JSON and log streams.

### Phase 3: Advanced Intelligence (Planned)
- [ ] **Stealth Enhancements:** Randomize USB Vendor IDs on every boot.
- [ ] **VLM Integration:** Use Local Vision Models (Llama 3.2 Vision) for understanding GUI elements beyond text.
- [ ] **Recovery Mode:** "Kill Switch" hardware dongle to physically disconnect USB if agent goes rogue.

## ⚠️ Security Warning
This tool interacts with hardware at a low level. Use responsibly. Ensure you have authorization before connecting to air-gapped systems.
