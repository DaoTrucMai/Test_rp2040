#!/usr/bin/env python3

#
# Copyright (c) 2020 2024 Daniel Gorbea
#
# Copyright (c) 2020 Raspberry Pi (Trading) Ltd. author of https://github.com/raspberrypi/pico-examples/tree/master/usb
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Install dependency:  sudo apt install python3-usb
# Run with:           python3 usb_speed_test.py
# If permission denied: sudo python3 usb_speed_test.py
#                       (or install udev rules: see 99-rp2040-usb.rules)

import usb.core
import usb.util
import datetime
import sys

dev = usb.core.find(idVendor=0x2E8A, idProduct=0x0001)
if dev is None:
    print("Lỗi: Không tìm thấy thiết bị.")
    print("  - Kiểm tra Pico đã được cắm chưa: lsusb | grep 2e8a")
    print("  - Kiểm tra firmware đã nạp đúng chưa (nên thấy ID 2e8a:0001)")
    sys.exit(1)

# Detach kernel driver nếu cần (an toàn hơn với try/except)
try:
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
except (usb.core.USBError, NotImplementedError):
    pass

# KHÔNG gọi dev.set_configuration() ở đây.
# Firmware tự xử lý SET_CONFIGURATION trong quá trình enumeration.
# Gọi lại từ host sẽ khiến pyusb claim interface và không release đúng cách,
# gây lỗi "Device busy" khi chạy lần 2.

EP_DIR_OUT = 0x00
EP_DIR_IN  = 0x80
TYPE_VENDOR = 0x40

REQ_EP0_OUT = 0x00
REQ_EP0_IN  = 0x01
REQ_EP1_OUT = 0x02
REQ_EP2_IN  = 0x03
REQ_EP3_IN  = 0x04
REQ_EP4_OUT = 0x05

EP1_OUT_ADDRESS = EP_DIR_OUT | 0x01
EP2_IN_ADDRESS  = EP_DIR_IN  | 0x02
EP3_IN_ADDRESS  = EP_DIR_IN  | 0x03
EP4_OUT_ADDRESS = EP_DIR_OUT | 0x04

# dev.ctrl_transfer(reqType, bReq, wVal, wIndex, [] or size)

repeat = 3  # Lấy trung bình 3 lần để kết quả ổn định hơn

try:
    # ---------- EP0 OUT ----------
    size = 4096
    kBs_total = 0
    buffer = []
    val = 0
    for i in range(size):
        buffer.append(val)
        val = (val + 1) % 10
    for i in range(repeat):
        a = datetime.datetime.now()
        dev.ctrl_transfer(TYPE_VENDOR | EP_DIR_OUT, REQ_EP0_OUT, 0, 0, buffer)
        b = datetime.datetime.now()
        elapsed = (b - a).total_seconds()
        kBs_total += (size / 1024) / elapsed
    print("Request REQ_EP0_OUT.       Size: %6u bytes.  Speed: %4u kB/s" % (size, kBs_total / repeat))

    # ---------- EP0 IN ----------
    size = 4096
    kBs_total = 0
    for i in range(repeat):
        a = datetime.datetime.now()
        response = dev.ctrl_transfer(TYPE_VENDOR | EP_DIR_IN, REQ_EP0_IN, 0, 0, size)
        b = datetime.datetime.now()
        elapsed = (b - a).total_seconds()
        kBs_total += (size / 1024) / elapsed
    print("Request REQ_EP0_IN.        Size: %6u bytes.  Speed: %4u kB/s" % (size, kBs_total / repeat))

    # ---------- EP1 OUT (bulk) ----------
    size = 40000
    kBs_total = 0
    buffer = []
    size_buffer = [size & 0xFF, size >> 8]
    val = 0
    for i in range(size):
        buffer.append(val)
        val = (val + 1) % 255
    for i in range(repeat):
        dev.ctrl_transfer(TYPE_VENDOR | EP_DIR_OUT, REQ_EP1_OUT, 0, 0, size_buffer)
        a = datetime.datetime.now()
        dev.write(EP1_OUT_ADDRESS, buffer)
        b = datetime.datetime.now()
        elapsed = (b - a).total_seconds()
        kBs_total += (size / 1024) / elapsed
    print("Request REQ_EP1_OUT.       Size: %6u bytes.  Speed: %4u kB/s" % (size, kBs_total / repeat))

    # ---------- EP2 IN (bulk) ----------
    size = 40000
    kBs_total = 0
    size_buffer = [size & 0xFF, size >> 8]
    for i in range(repeat):
        dev.ctrl_transfer(TYPE_VENDOR | EP_DIR_OUT, REQ_EP2_IN, 0, 0, size_buffer)
        a = datetime.datetime.now()
        response = dev.read(EP2_IN_ADDRESS, size)
        b = datetime.datetime.now()
        elapsed = (b - a).total_seconds()
        kBs_total += (size / 1024) / elapsed
    print("Request REQ_EP2_IN.        Size: %6u bytes.  Speed: %4u kB/s" % (size, kBs_total / repeat))

    # ---------- EP3 IN stream ----------
    size = 40000
    kBs_total = 0
    size_buffer = [size & 0xFF, size >> 8]
    for i in range(repeat):
        dev.ctrl_transfer(TYPE_VENDOR | EP_DIR_OUT, REQ_EP3_IN, 0, 0, size_buffer)
        a = datetime.datetime.now()
        response = dev.read(EP3_IN_ADDRESS, size)
        b = datetime.datetime.now()
        elapsed = (b - a).total_seconds()
        kBs_total += (size / 1024) / elapsed
    print("Request REQ_EP3_IN stream.  Size: %6u bytes.  Speed: %4u kB/s" % (size, kBs_total / repeat))

    # ---------- EP4 OUT stream ----------
    size = 40000
    kBs_total = 0
    buffer = []
    size_buffer = [size & 0xFF, size >> 8]
    val = 0
    for i in range(size):
        buffer.append(val)
        val = (val + 1) % 255
    for i in range(repeat):
        dev.ctrl_transfer(TYPE_VENDOR | EP_DIR_OUT, REQ_EP4_OUT, 0, 0, size_buffer)
        a = datetime.datetime.now()
        dev.write(EP4_OUT_ADDRESS, buffer)
        b = datetime.datetime.now()
        elapsed = (b - a).total_seconds()
        kBs_total += (size / 1024) / elapsed
    print("Request REQ_EP4_OUT stream. Size: %6u bytes.  Speed: %4u kB/s" % (size, kBs_total / repeat))

except usb.core.USBError as e:
    print("\nLỗi USB: %s" % e)
    print("Gợi ý: Rút và cắm lại Pico, rồi thử lại.")
    sys.exit(1)

finally:
    # Giải phóng thiết bị đúng cách để lần chạy kế tiếp không bị lỗi "busy"
    usb.util.dispose_resources(dev)
