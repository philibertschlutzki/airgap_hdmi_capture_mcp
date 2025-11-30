"""
VLM Client Module.

This module provides a client interface to communicate with an Ollama-compatible
Vision Language Model (VLM) API. It handles configuration via environment variables
and formats requests for visual analysis.
"""

import os
import requests
import json
import logging
from typing import Optional

class VLMClient:
    """
    Client for interacting with Ollama VLM API.
    """
    def __init__(self):
        """
        Initializes the VLM Client by reading environment variables.

        Environment Variables:
            OLLAMA_BASE_URL (str): The base URL of the Ollama API (default: http://localhost:11434).
            OLLAMA_MODEL (str): The model name to use (default: llava).
            OLLAMA_API_KEY (str): Optional API Key if the endpoint is protected.
        """
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.environ.get("OLLAMA_MODEL", "llava")
        self.api_key = os.environ.get("OLLAMA_API_KEY", "")

    def analyze_image(self, base64_image: str, prompt: str = "Describe what you see on this screen.") -> str:
        """
        Sends an image to the VLM for analysis.

        Args:
            base64_image (str): The base64 encoded image string (without data URI prefix).
            prompt (str): The text prompt for the model.

        Returns:
            str: The model's response text.

        Raises:
            RuntimeError: If the API call fails or configuration is missing.
        """
        url = f"{self.base_url}/api/generate"

        headers = {
            "Content-Type": "application/json"
        }

        # Add API Key header if configured (Example: standard Bearer, or custom)
        # Assuming standard Bearer for generic proxies, or specific header.
        # Ollama native doesn't use auth, but proxies might.
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False
        }

        try:
            # We use a short timeout because this is an interactive system,
            # but VLMs can be slow. 30s is reasonable.
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data.get("response", "")

        except requests.exceptions.RequestException as e:
            error_msg = f"VLM API Error: {str(e)}"
            logging.error(error_msg)
            # Return error as string so it bubbles up to the MCP tool output
            return f"Error: Failed to contact VLM. {error_msg}"
