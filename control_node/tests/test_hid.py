import unittest
from unittest.mock import MagicMock, patch, mock_open
import time
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from hid import KeyInjector, Layout, GermanISO, MOD_LSHIFT, MOD_NONE, MOD_RALT

class TestHID(unittest.TestCase):
    def setUp(self):
        self.injector = KeyInjector(device_path="/tmp/fake_hidg0")
        # Ensure we are in simulation mode or mock the file write
        self.injector.simulation_mode = True

    def test_german_layout_mapping(self):
        layout = GermanISO()

        # Test basic
        mod, code = layout.get_scancode('a')
        self.assertEqual(code, 0x04)
        self.assertEqual(mod, MOD_NONE)

        # Test Shifted
        mod, code = layout.get_scancode('A')
        self.assertEqual(code, 0x04)
        self.assertEqual(mod, MOD_LSHIFT)

        # Test Special Chars
        mod, code = layout.get_scancode('@')
        self.assertEqual(code, 0x14) # Q key
        self.assertEqual(mod, MOD_RALT) # AltGr

        mod, code = layout.get_scancode('\\')
        self.assertEqual(mod, MOD_RALT)

    @patch('hid.time.sleep')
    def test_jitter_typing(self, mock_sleep):
        # We want to verify that typing calls sleep with varying values
        self.injector.type_text("abc", delay_mean=0.1, delay_std=0.05)

        # Should have called sleep at least 2 times per char (press + release)
        # Actually in my impl: press_key calls sleep once (hold), type_text calls sleep once (interval)
        # So 2 sleeps per char. Total 6 sleeps.
        self.assertGreaterEqual(mock_sleep.call_count, 6)

        # Check variance (rudimentary)
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        self.assertTrue(any(d != 0.1 for d in delays), "Delays should not be exactly constant (jitter expected)")

    def test_sequence_parsing(self):
        with patch.object(self.injector, '_send_report') as mock_send:
            self.injector.press_sequence(['CTRL', 'ALT'], 'DELETE')

            # Check arguments
            # CTRL (1) | ALT (4) = 5
            # DELETE = 0x4C
            mock_send.assert_any_call(5, 0x4C)
            mock_send.assert_any_call(0, 0) # Release

if __name__ == '__main__':
    unittest.main()
