import os
import time
import random
import struct
from typing import Dict, Tuple, List

# HID Scancodes (Usage ID)
# Reference: USB HID Usage Tables
SCANCODE_A = 0x04
SCANCODE_Z = 0x1D
SCANCODE_1 = 0x1E
SCANCODE_0 = 0x27
SCANCODE_ENTER = 0x28
SCANCODE_ESCAPE = 0x29
SCANCODE_BACKSPACE = 0x2A
SCANCODE_TAB = 0x2B
SCANCODE_SPACE = 0x2C
SCANCODE_MINUS = 0x2D
SCANCODE_EQUAL = 0x2E
SCANCODE_LEFT_BRACE = 0x2F
SCANCODE_RIGHT_BRACE = 0x30
SCANCODE_BACKSLASH = 0x31
SCANCODE_NON_US_HASH = 0x32 # # and ~ on non-US keyboards
SCANCODE_SEMICOLON = 0x33
SCANCODE_APOSTROPHE = 0x34
SCANCODE_GRAVE = 0x35
SCANCODE_COMMA = 0x36
SCANCODE_DOT = 0x37
SCANCODE_SLASH = 0x38
SCANCODE_F1 = 0x3A
SCANCODE_F12 = 0x45

# Modifiers (Bitmask)
MOD_NONE = 0x00
MOD_LCTRL = 0x01
MOD_LSHIFT = 0x02
MOD_LALT = 0x04
MOD_LGUI = 0x08
MOD_RCTRL = 0x10
MOD_RSHIFT = 0x20
MOD_RALT = 0x40 # AltGr
MOD_RGUI = 0x80

class Layout:
    def __init__(self):
        self.mapping: Dict[str, Tuple[int, int]] = {}

    def get_scancode(self, char: str) -> Tuple[int, int]:
        """Returns (modifier, scancode) for a given character."""
        return self.mapping.get(char, (MOD_NONE, 0x00))

class USLayout(Layout):
    """
    US QWERTY Keyboard Layout Mapping.
    """
    def __init__(self):
        super().__init__()
        # Basic lowercase (a-z)
        self.mapping['a'] = (MOD_NONE, 0x04)
        self.mapping['b'] = (MOD_NONE, 0x05)
        self.mapping['c'] = (MOD_NONE, 0x06)
        self.mapping['d'] = (MOD_NONE, 0x07)
        self.mapping['e'] = (MOD_NONE, 0x08)
        self.mapping['f'] = (MOD_NONE, 0x09)
        self.mapping['g'] = (MOD_NONE, 0x0A)
        self.mapping['h'] = (MOD_NONE, 0x0B)
        self.mapping['i'] = (MOD_NONE, 0x0C)
        self.mapping['j'] = (MOD_NONE, 0x0D)
        self.mapping['k'] = (MOD_NONE, 0x0E)
        self.mapping['l'] = (MOD_NONE, 0x0F)
        self.mapping['m'] = (MOD_NONE, 0x10)
        self.mapping['n'] = (MOD_NONE, 0x11)
        self.mapping['o'] = (MOD_NONE, 0x12)
        self.mapping['p'] = (MOD_NONE, 0x13)
        self.mapping['q'] = (MOD_NONE, 0x14)
        self.mapping['r'] = (MOD_NONE, 0x15)
        self.mapping['s'] = (MOD_NONE, 0x16)
        self.mapping['t'] = (MOD_NONE, 0x17)
        self.mapping['u'] = (MOD_NONE, 0x18)
        self.mapping['v'] = (MOD_NONE, 0x19)
        self.mapping['w'] = (MOD_NONE, 0x1A)
        self.mapping['x'] = (MOD_NONE, 0x1B)
        self.mapping['y'] = (MOD_NONE, 0x1C)
        self.mapping['z'] = (MOD_NONE, 0x1D)

        # Numbers
        self.mapping['1'] = (MOD_NONE, 0x1E)
        self.mapping['2'] = (MOD_NONE, 0x1F)
        self.mapping['3'] = (MOD_NONE, 0x20)
        self.mapping['4'] = (MOD_NONE, 0x21)
        self.mapping['5'] = (MOD_NONE, 0x22)
        self.mapping['6'] = (MOD_NONE, 0x23)
        self.mapping['7'] = (MOD_NONE, 0x24)
        self.mapping['8'] = (MOD_NONE, 0x25)
        self.mapping['9'] = (MOD_NONE, 0x26)
        self.mapping['0'] = (MOD_NONE, 0x27)

        # Uppercase (Shift)
        for char, (mod, code) in list(self.mapping.items()):
            if char.isalpha():
                self.mapping[char.upper()] = (MOD_LSHIFT, code)

        # Special Characters US
        self.mapping['!'] = (MOD_LSHIFT, 0x1E)
        self.mapping['@'] = (MOD_LSHIFT, 0x1F)
        self.mapping['#'] = (MOD_LSHIFT, 0x20)
        self.mapping['$'] = (MOD_LSHIFT, 0x21)
        self.mapping['%'] = (MOD_LSHIFT, 0x22)
        self.mapping['^'] = (MOD_LSHIFT, 0x23)
        self.mapping['&'] = (MOD_LSHIFT, 0x24)
        self.mapping['*'] = (MOD_LSHIFT, 0x25)
        self.mapping['('] = (MOD_LSHIFT, 0x26)
        self.mapping[')'] = (MOD_LSHIFT, 0x27)

        self.mapping['-'] = (MOD_NONE, 0x2D)
        self.mapping['_'] = (MOD_LSHIFT, 0x2D)
        self.mapping['='] = (MOD_NONE, 0x2E)
        self.mapping['+'] = (MOD_LSHIFT, 0x2E)
        self.mapping['['] = (MOD_NONE, 0x2F)
        self.mapping['{'] = (MOD_LSHIFT, 0x2F)
        self.mapping[']'] = (MOD_NONE, 0x30)
        self.mapping['}'] = (MOD_LSHIFT, 0x30)
        self.mapping['\\'] = (MOD_NONE, 0x31)
        self.mapping['|'] = (MOD_LSHIFT, 0x31)
        self.mapping[';'] = (MOD_NONE, 0x33)
        self.mapping[':'] = (MOD_LSHIFT, 0x33)
        self.mapping["'"] = (MOD_NONE, 0x34)
        self.mapping['"'] = (MOD_LSHIFT, 0x34)
        self.mapping['`'] = (MOD_NONE, 0x35)
        self.mapping['~'] = (MOD_LSHIFT, 0x35)
        self.mapping[','] = (MOD_NONE, 0x36)
        self.mapping['<'] = (MOD_LSHIFT, 0x36)
        self.mapping['.'] = (MOD_NONE, 0x37)
        self.mapping['>'] = (MOD_LSHIFT, 0x37)
        self.mapping['/'] = (MOD_NONE, 0x38)
        self.mapping['?'] = (MOD_LSHIFT, 0x38)

        # Other symbols
        self.mapping[' '] = (MOD_NONE, SCANCODE_SPACE)
        self.mapping['\n'] = (MOD_NONE, SCANCODE_ENTER)
        self.mapping['\t'] = (MOD_NONE, SCANCODE_TAB)

class GermanISO(Layout):
    """
    German ISO Keyboard Layout Mapping.
    """
    def __init__(self):
        super().__init__()
        # Basic lowercase (a-z)
        # Note: In German layout, Z and Y are swapped compared to US QWERTY
        # But scancodes are positional.
        # QWERTY: q=0x14, w=0x1a, ...
        # QWERTZ: q=0x14, w=0x1a, ... z (pos y)=0x1d, y (pos z)=0x1c

        # We map characters to the USB Usage IDs.
        # The OS maps Usage ID -> Character based on configured layout.
        # If the target OS is set to German, pressing Usage ID 0x1D (Z position on US) produces 'y'.
        # Wait, if target is German:
        # Key labeled 'Z' is at 0x1C (Y position on US).
        # Key labeled 'Y' is at 0x1D (Z position on US).

        # Let's define based on "What key do I press on a German keyboard to get 'x'?"

        # Lowercase
        self.mapping['a'] = (MOD_NONE, 0x04)
        self.mapping['b'] = (MOD_NONE, 0x05)
        self.mapping['c'] = (MOD_NONE, 0x06)
        self.mapping['d'] = (MOD_NONE, 0x07)
        self.mapping['e'] = (MOD_NONE, 0x08)
        self.mapping['f'] = (MOD_NONE, 0x09)
        self.mapping['g'] = (MOD_NONE, 0x0A)
        self.mapping['h'] = (MOD_NONE, 0x0B)
        self.mapping['i'] = (MOD_NONE, 0x0C)
        self.mapping['j'] = (MOD_NONE, 0x0D)
        self.mapping['k'] = (MOD_NONE, 0x0E)
        self.mapping['l'] = (MOD_NONE, 0x0F)
        self.mapping['m'] = (MOD_NONE, 0x10)
        self.mapping['n'] = (MOD_NONE, 0x11)
        self.mapping['o'] = (MOD_NONE, 0x12)
        self.mapping['p'] = (MOD_NONE, 0x13)
        self.mapping['q'] = (MOD_NONE, 0x14)
        self.mapping['r'] = (MOD_NONE, 0x15)
        self.mapping['s'] = (MOD_NONE, 0x16)
        self.mapping['t'] = (MOD_NONE, 0x17)
        self.mapping['u'] = (MOD_NONE, 0x18)
        self.mapping['v'] = (MOD_NONE, 0x19)
        self.mapping['w'] = (MOD_NONE, 0x1A)
        self.mapping['x'] = (MOD_NONE, 0x1B)
        self.mapping['y'] = (MOD_NONE, 0x1D) # Pos Z on US
        self.mapping['z'] = (MOD_NONE, 0x1C) # Pos Y on US

        # Numbers
        self.mapping['1'] = (MOD_NONE, 0x1E)
        self.mapping['2'] = (MOD_NONE, 0x1F)
        self.mapping['3'] = (MOD_NONE, 0x20)
        self.mapping['4'] = (MOD_NONE, 0x21)
        self.mapping['5'] = (MOD_NONE, 0x22)
        self.mapping['6'] = (MOD_NONE, 0x23)
        self.mapping['7'] = (MOD_NONE, 0x24)
        self.mapping['8'] = (MOD_NONE, 0x25)
        self.mapping['9'] = (MOD_NONE, 0x26)
        self.mapping['0'] = (MOD_NONE, 0x27)

        # Uppercase (Shift)
        for char, (mod, code) in list(self.mapping.items()):
            if char.isalpha():
                self.mapping[char.upper()] = (MOD_LSHIFT, code)

        # Special German Characters (Shifted Numbers)
        self.mapping['!'] = (MOD_LSHIFT, 0x1E) # Shift+1
        self.mapping['"'] = (MOD_LSHIFT, 0x1F) # Shift+2
        self.mapping['§'] = (MOD_LSHIFT, 0x20) # Shift+3
        self.mapping['$'] = (MOD_LSHIFT, 0x21) # Shift+4
        self.mapping['%'] = (MOD_LSHIFT, 0x22) # Shift+5
        self.mapping['&'] = (MOD_LSHIFT, 0x23) # Shift+6
        self.mapping['/'] = (MOD_LSHIFT, 0x24) # Shift+7
        self.mapping['('] = (MOD_LSHIFT, 0x25) # Shift+8
        self.mapping[')'] = (MOD_LSHIFT, 0x26) # Shift+9
        self.mapping['='] = (MOD_LSHIFT, 0x27) # Shift+0

        # Other symbols
        self.mapping[' '] = (MOD_NONE, SCANCODE_SPACE)
        self.mapping['\n'] = (MOD_NONE, SCANCODE_ENTER)
        self.mapping['\t'] = (MOD_NONE, SCANCODE_TAB)

        self.mapping['ß'] = (MOD_NONE, 0x2D) # Key right of 0
        self.mapping['?'] = (MOD_LSHIFT, 0x2D)

        self.mapping['+'] = (MOD_NONE, 0x30) # Key right of P (ü/+] in DE, ] in US) wait..
        # DE Layout:
        # Row QWERTYUIOP Ü +
        # Row ASDFGHJKL Ö Ä #
        # Row YXCVBNM , . -
        # Row <

        # Let's approximate common CLI chars for DE layout
        self.mapping['.'] = (MOD_NONE, 0x37)
        self.mapping[':'] = (MOD_LSHIFT, 0x37)
        self.mapping[','] = (MOD_NONE, 0x36)
        self.mapping[';'] = (MOD_LSHIFT, 0x36)
        self.mapping['-'] = (MOD_NONE, 0x38) # Slash key on US is -/_ on DE
        self.mapping['_'] = (MOD_LSHIFT, 0x38)

        # AltGr (Right Alt)
        self.mapping['@'] = (MOD_RALT, 0x14) # AltGr+Q
        self.mapping['\\'] = (MOD_RALT, 0x2D) # AltGr+ß (Key right of 0)
        self.mapping['|'] = (MOD_RALT, 0x35) # AltGr + < (Key right of LShift)
        self.mapping['{'] = (MOD_RALT, 0x24) # AltGr+7
        self.mapping['}'] = (MOD_RALT, 0x27) # AltGr+0
        self.mapping['['] = (MOD_RALT, 0x25) # AltGr+8
        self.mapping[']'] = (MOD_RALT, 0x26) # AltGr+9
        self.mapping['~'] = (MOD_RALT, 0x30) # AltGr + + (Key right of Ü)

class KeyInjector:
    """
    Handles the low-level injection of keystrokes into the USB HID gadget.

    This class manages the connection to the OS HID device file (e.g., /dev/hidg0),
    formats the USB reports, and handles the timing of key presses.
    """
    def __init__(self, device_path="/dev/hidg0", layout: Layout = GermanISO()):
        """
        Args:
            device_path (str): Path to the HID gadget character device.
            layout (Layout): The keyboard layout object (USLayout or GermanISO).
        """
        self.device_path = device_path
        self.layout = layout
        self._check_device()

    def _check_device(self):
        """Checks if the HID device file exists; enables simulation mode if not."""
        if not os.path.exists(self.device_path):
            print(f"Warning: HID device {self.device_path} not found. Running in simulation mode.")
            self.simulation_mode = True
        else:
            self.simulation_mode = False

    def _send_report(self, modifiers: int, key_code: int):
        """
        Sends an 8-byte HID report to the kernel.

        Report Format:
        [Modifier, Reserved, Key1, Key2, Key3, Key4, Key5, Key6]

        Args:
            modifiers (int): Bitmask for modifier keys (Ctrl, Shift, etc.).
            key_code (int): The USB HID usage ID for the key.
        """
        # We only use Key1 for simplicity (typing one char at a time)
        report = struct.pack('BBBBBBBB', modifiers, 0, key_code, 0, 0, 0, 0, 0)

        if self.simulation_mode:
            # print(f"[SIM] Sending Report: Mod={modifiers:02x} Key={key_code:02x}")
            pass
        else:
            try:
                with open(self.device_path, 'wb') as f:
                    f.write(report)
                    f.flush()
            except IOError as e:
                print(f"Error writing to HID device: {e}")

    def release_all(self):
        """Sends an empty report to release all keys."""
        self._send_report(0, 0)

    def press_key(self, char: str):
        """
        Presses and releases a single character key.

        This method looks up the scancode for the character in the current layout,
        sends the press report, waits a random small duration, and then sends the release report.

        Args:
            char (str): The character to type.
        """
        modifier, code = self.layout.get_scancode(char)
        if code == 0:
            print(f"Warning: No mapping for character '{char}'")
            return

        # Press
        self._send_report(modifier, code)

        # Hold briefly (simulating physical press)
        time.sleep(random.uniform(0.01, 0.03))

        # Release
        self.release_all()

    def press_sequence(self, modifiers_list: List[str], key_name: str):
        """
        Presses a special sequence like Ctrl+Alt+Del.
        modifiers_list: ['CTRL', 'ALT', 'SHIFT', 'GUI']
        key_name: 'DELETE', 'F1', 'ENTER', 'A', etc.
        """
        mod_mask = 0
        for m in modifiers_list:
            m = m.upper()
            if m == 'CTRL': mod_mask |= MOD_LCTRL
            if m == 'ALT': mod_mask |= MOD_LALT
            if m == 'SHIFT': mod_mask |= MOD_LSHIFT
            if m == 'GUI' or m == 'WIN': mod_mask |= MOD_LGUI
            if m == 'RALT': mod_mask |= MOD_RALT

        # Find key code (naive lookup)
        key_code = 0
        # Check explicit mappings first
        if key_name == 'DELETE': key_code = 0x4C
        elif key_name == 'ENTER': key_code = SCANCODE_ENTER
        elif key_name == 'ESC': key_code = SCANCODE_ESCAPE
        elif key_name == 'TAB': key_code = SCANCODE_TAB
        elif key_name.startswith('F'):
            try:
                f_num = int(key_name[1:])
                if 1 <= f_num <= 12:
                    key_code = 0x39 + f_num
            except ValueError:
                pass

        if key_code == 0 and len(key_name) == 1:
             # Try to find character code
             _, key_code = self.layout.get_scancode(key_name.lower())

        if key_code == 0:
             print(f"Warning: Unknown key name '{key_name}'")
             return

        self._send_report(mod_mask, key_code)
        time.sleep(0.1)
        self.release_all()


    def type_text(self, text: str, delay_mean: float = 0.05, delay_std: float = 0.02):
        """Types a string with humanized timing."""
        for char in text:
            self.press_key(char)

            # Calculate delay
            delay = random.gauss(delay_mean, delay_std)
            if delay < 0.01: delay = 0.01
            time.sleep(delay)
