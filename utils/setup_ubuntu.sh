#!/usr/bin/env bash
# setup_ubuntu.sh – Cài đặt pyusb và udev rule trên Ubuntu
# Chạy từ thư mục gốc của repo:  bash utils/setup_ubuntu.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Bước 1: Cài python3-usb qua apt ==="
if python3 -c "import usb.core" 2>/dev/null; then
    echo "  pyusb đã được cài sẵn, bỏ qua."
else
    sudo apt-get update -qq
    sudo apt-get install -y python3-usb
    echo "  Đã cài python3-usb."
fi

echo ""
echo "=== Bước 2: Cài udev rule ==="
RULE_SRC="$SCRIPT_DIR/99-rp2040-usb.rules"
RULE_DST="/etc/udev/rules.d/99-rp2040-usb.rules"
if [ -f "$RULE_DST" ]; then
    echo "  udev rule đã tồn tại, bỏ qua."
else
    sudo cp "$RULE_SRC" "$RULE_DST"
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo "  Đã cài udev rule."
fi

echo ""
echo "=== Bước 3: Thêm user vào group plugdev ==="
if groups "$USER" | grep -q plugdev; then
    echo "  User '$USER' đã ở trong group plugdev."
else
    sudo usermod -aG plugdev "$USER"
    echo "  Đã thêm '$USER' vào group plugdev."
    echo "  *** Bạn cần đăng xuất và đăng nhập lại (hoặc chạy: newgrp plugdev) ***"
fi

echo ""
echo "=== Hoàn tất! ==="
echo "Rút và cắm lại Pico, sau đó chạy:"
echo "  python3 utils/usb_speed_test.py"
