#!/bin/bash
# Script to verify if the Raspberry Pi is correctly configured as a USB HID Gadget.
# This check is intended to be run on the Raspberry Pi (Interface Unit).

echo "--- Vision-HID-Bridge: Raspberry Pi Setup Verification ---"

# 1. Check Kernel Modules
echo "[1/3] Checking Kernel Modules..."
if lsmod | grep -q "libcomposite"; then
    echo "  [OK] libcomposite module is loaded."
else
    echo "  [FAIL] libcomposite module is NOT loaded."
    echo "         Run: sudo modprobe libcomposite"
    exit 1
fi

if lsmod | grep -q "dwc2"; then
    echo "  [OK] dwc2 module is loaded."
else
    echo "  [FAIL] dwc2 module is NOT loaded."
    echo "         Add 'dtoverlay=dwc2' to /boot/config.txt and reboot."
    exit 1
fi

# 2. Check ConfigFS
echo "[2/3] Checking USB Gadget ConfigFS..."
GADGET_DIR="/sys/kernel/config/usb_gadget/hid_gadget"

if [ -d "$GADGET_DIR" ]; then
    echo "  [OK] HID Gadget ConfigFS directory exists at $GADGET_DIR."
else
    echo "  [FAIL] HID Gadget ConfigFS directory not found."
    echo "         Ensure 'setup_gadget.sh' has been executed."
    exit 1
fi

if [ -L "$GADGET_DIR/configs/c.1/hid.usb0" ]; then
    echo "  [OK] HID Function is linked to configuration."
else
    echo "  [FAIL] HID Function is NOT linked to configuration."
    exit 1
fi

# 3. Check Device Node
echo "[3/3] Checking /dev/hidg0 Device Node..."
if [ -c "/dev/hidg0" ]; then
    echo "  [OK] /dev/hidg0 exists."
else
    echo "  [FAIL] /dev/hidg0 does not exist."
    exit 1
fi

# Check Permissions (Need write access)
if [ -w "/dev/hidg0" ]; then
    echo "  [OK] /dev/hidg0 is writable by current user."
else
    echo "  [WARN] /dev/hidg0 is NOT writable by current user."
    echo "         You may need to run your agent with sudo or change permissions:"
    echo "         sudo chmod 666 /dev/hidg0"
fi

echo "--- Verification Complete: System Ready ---"
exit 0
