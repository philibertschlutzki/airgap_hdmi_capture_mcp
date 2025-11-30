# Vision-HID-Bridge Manual

This manual provides detailed instructions on how to set up, configure, and operate the Vision-HID-Bridge MCP Server, with a specific focus on the Visual Language Model (VLM) integration.

## 1. VLM Integration Setup (Ollama)

To enable the "analysis" mode for screen capture (where the agent can "see" and describe the screen using AI), you need an Ollama-compatible endpoint.

### 1.1 Installation
1.  **Install Ollama:** Follow the instructions at [ollama.com](https://ollama.com).
2.  **Pull a Vision Model:** You must use a model that supports vision (e.g., `llava`, `moondream`, `llama3.2-vision`).
    ```bash
    ollama pull llava
    ```

### 1.2 Running the Endpoint
Run Ollama normally. It defaults to port 11434.
```bash
ollama serve
```

## 2. Configuration (Environment Variables)

The MCP Server uses environment variables to configure the connection to the VLM. This ensures that sensitive information (like API keys) is not hardcoded.

### 2.1 Variables

| Variable | Description | Default |
|---|---|---|
| `OLLAMA_BASE_URL` | The URL of the Ollama API. | `http://localhost:11434` |
| `OLLAMA_MODEL` | The name of the model to use. | `llava` |
| `OLLAMA_API_KEY` | Optional API Key if your endpoint is behind a proxy. | *(Empty)* |

### 2.2 Setting Variables
You can set these before running the server:

**Linux/Mac:**
```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llava"
# export OLLAMA_API_KEY="your-secure-token"  # Only if needed
python -m control_node.src.main
```

**Windows (PowerShell):**
```powershell
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:OLLAMA_MODEL="llava"
python -m control_node.src.main
```

## 3. Usage Guide

### 3.1 Starting the Server
The server is designed to be run as an MCP process.

```bash
python -m control_node.src.main
```

### 3.2 Using the `capture_screen` Tool
The primary tool for vision is `capture_screen`. It supports three modes:

1.  **`ocr_text` (Default):** Returns the text content of the screen using Tesseract. Fast and good for reading CLI output.
2.  **`raw_base64`:** Returns the raw image data. Useful if the client wants to process it elsewhere.
3.  **`analysis`:** Sends the screen image to the configured VLM (Ollama) and returns a natural language description.

**Example Request (Analysis Mode):**
```json
{
  "name": "capture_screen",
  "arguments": {
    "mode": "analysis"
  }
}
```

**Response:**
> "I see a Windows Command Prompt window. The current directory is C:\Users\Admin. There is a file listing visible..."

### 3.3 Authentication Security
When connecting the MCP Server to an external VLM provider (or a secured internal proxy), `OLLAMA_API_KEY` is used as a Bearer token in the HTTP Authorization header (`Authorization: Bearer <key>`). This allows `fastmcp` to identify itself securely to the endpoint.

## 4. Troubleshooting

*   **"Error: Failed to contact VLM":** Ensure Ollama is running (`ollama serve`) and the `OLLAMA_BASE_URL` is reachable from the control node.
*   **"Error: Unknown mode":** Ensure you are passing `mode="analysis"` correctly.
*   **Performance:** Vision models can be slow (seconds). Ensure your timeout logic accounts for this.
