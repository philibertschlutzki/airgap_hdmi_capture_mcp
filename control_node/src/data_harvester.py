import os
import json
import time
import re
from typing import List, Dict, Optional

class DataHarvester:
    """
    Handles persistence and structuring of captured data.

    Responsibilities:
    1. Parse raw text output (e.g., directory listings) into structured JSON.
    2. Save structured data to disk.
    3. Maintain a rolling log of all OCR output for auditing.
    """
    def __init__(self, logs_dir: str = "logs"):
        """
        Args:
            logs_dir (str): Directory where JSON scans and logs will be saved.
        """
        self.logs_dir = logs_dir
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def parse_directory_listing(self, text: str) -> Dict:
        """
        Parses the text output of a 'dir' command (Windows CMD style) into a dictionary.

        This uses heuristics (Regex) to extract filenames, sizes, and directory names.
        It is designed to handle standard Windows output but may be fragile with custom formats.

        Args:
            text (str): The raw text output from OCR.

        Returns:
            Dict: A dictionary containing lists of 'files' and 'directories'.
                  Example: {'files': [{'name': 'foo.txt', 'size': 123, 'type': 'file'}], 'directories': []}
        """
        # Simple parser for Windows 'dir' output
        files = []
        directories = []

        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line: continue

            # Windows 'dir' format example:
            # 01/01/2023  12:00 PM    <DIR>          Foldername
            # 01/01/2023  12:00 PM                10 filename.txt

            # Regex for Windows Line
            # Date Time [AM/PM] [<DIR>|Size] Name
            # We look for <DIR> or digits followed by name

            if "<DIR>" in line:
                parts = line.split("<DIR>")
                if len(parts) > 1:
                    name = parts[1].strip()
                    if name not in ['.', '..']:
                        directories.append({"name": name, "type": "dir"})
            else:
                # Try to find file size and name
                # Matches:  DATE  TIME  SIZE  NAME
                # Example: 01/01/2023  12:00 PM                10 filename with spaces.txt

                # Heuristic: Find the last continuous sequence of digits that is followed by spaces, then the rest is the name.
                # However, filenames can start with digits.
                # Standard DIR output format is fixed width for size usually, but we rely on OCR spacing.

                # Regex Strategy:
                # Look for a number (size) that is NOT at the very end of the line (which would be strange for size unless parsing reversed),
                # but is surrounded by spaces or is clearly the size column.
                # Better: DATE TIME [SIZE] [NAME]

                # Ignore summary lines like "               2 File(s)             30 bytes"
                if "File(s)" in line or "Dir(s)" in line or "Volume" in line:
                    continue

                # Regex: Find a number followed by at least one space, then the filename (rest of line).
                # The filename can contain anything.
                # We assume the date/time is at the start.

                # Match: ... <spaces> <digits> <spaces> <filename>
                match = re.search(r'\s+(\d+)\s+(.+)$', line)
                if match:
                    size = match.group(1)
                    name = match.group(2).strip()

                    # Heuristic validation:
                    # If the name is just "bytes" or "File(s)", we might have matched the summary line partially.
                    # But the explicit check above handles most summaries.

                    if size.isdigit():
                         files.append({"name": name, "size": int(size), "type": "file"})

        return {
            "directories": directories,
            "files": files,
            "raw_text": text
        }

    def save_scan(self, path: str, structure: Dict) -> str:
        """
        Saves the structured scan data to a JSON file.

        The filename is generated based on the scanned path and the current timestamp.

        Args:
            path (str): The original path that was scanned (used for naming).
            structure (Dict): The parsed data structure.

        Returns:
            str: The full filepath of the saved JSON file.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_path = path.replace("/", "_").replace("\\", "_").replace(":", "").strip("_")
        if not safe_path: safe_path = "root"

        filename = f"scan_{safe_path}_{timestamp}.json"
        filepath = os.path.join(self.logs_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(structure, f, indent=2)

        return filepath

    def log_ocr_stream(self, text: str):
        """
        Appends a block of OCR text to a daily log file.

        This serves as a 'black box' recorder, capturing everything the agent sees.

        Args:
            text (str): The text content to log.
        """
        today = time.strftime("%Y-%m-%d")
        filename = f"ocr_stream_{today}.log"
        filepath = os.path.join(self.logs_dir, filename)

        timestamp = time.strftime("%H:%M:%S")
        entry = f"--- {timestamp} ---\n{text}\n\n"

        try:
            with open(filepath, 'a') as f:
                f.write(entry)
        except Exception as e:
            print(f"Failed to write to OCR log: {e}")
