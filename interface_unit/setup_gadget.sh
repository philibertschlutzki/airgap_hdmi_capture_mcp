#!/bin/bash
# Vision-HID-Bridge: USB Gadget Setup Script
# This script configures the Raspberry Pi Zero as a USB HID device (Keyboard)
# using ConfigFS. It must be run as root.

set -e

# Configuration
GADGET_DIR="/sys/kernel/config/usb_gadget/vision_bridge"
VID="0x1d6b" # Linux Foundation (Change to spoof other vendors, e.g., Dell 0x413c)
PID="0x0104" # Multifunction Composite Gadget
SERIAL="deadbeef007"
MANUFACTURER="Vision Systems"
PRODUCT="Vision HID Bridge"

# 1. Load libcomposite module
if ! lsmod | grep -q libcomposite; then
    modprobe libcomposite
fi

# 2. Create Gadget Directory
if [ ! -d "$GADGET_DIR" ]; then
    mkdir "$GADGET_DIR"
else
    echo "Gadget directory already exists. Cleaning up..."
    # Cleanup logic could be added here, but for now we assume a fresh boot or manual cleanup
fi

cd "$GADGET_DIR"

# 3. Configure Device Identity
echo "$VID" > idVendor
echo "$PID" > idProduct
echo "0x0100" > bcdDevice # v1.0.0
echo "0x0200" > bcdUSB    # USB 2.0

# 4. Configure Strings (English)
mkdir -p strings/0x409
echo "$SERIAL" > strings/0x409/serialnumber
echo "$MANUFACTURER" > strings/0x409/manufacturer
echo "$PRODUCT" > strings/0x409/product

# 5. Create Configuration
mkdir -p configs/c.1/strings/0x409
echo "Config 1: HID" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# 6. Define HID Function
mkdir -p functions/hid.usb0

# HID Report Descriptor for a Standard Keyboard (Boot Protocol compatible)
# This is the standard 63-byte report descriptor for a keyboard.
# It defines 8 modifier bits (Ctrl, Shift, etc.) and a byte for reserved,
# followed by an array of 6 key codes.
# This hex string is the binary report descriptor.
REPORT_DESC="05010906a101050719e029e71500250175019508810295017508810395057501050819012905910295017503910395067508150025650507190029658100c0"

echo "1" > functions/hid.usb0/protocol
echo "1" > functions/hid.usb0/subclass # Boot Interface Subclass
echo "8" > functions/hid.usb0/report_length
echo "$REPORT_DESC" | xxd -r -p > functions/hid.usb0/report_desc

# 7. Bind Function to Configuration
ln -s functions/hid.usb0 configs/c.1/

# 8. Enable Gadget
# Find the UDC (USB Device Controller) name (usually ending in .usb)
UDC_NAME=$(ls /sys/class/udc | head -n 1)

if [ -z "$UDC_NAME" ]; then
    echo "Error: No USB Device Controller found. Is this a Raspberry Pi Zero?"
    exit 1
fi

echo "$UDC_NAME" > UDC

chmod 777 /dev/hidg0

echo "Vision-HID-Bridge Gadget enabled on $UDC_NAME"
echo "HID device available at /dev/hidg0"
