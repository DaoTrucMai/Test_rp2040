# USB Device Library for RP2040 – Hướng dẫn đo tốc độ USB trên Ubuntu

> Repo gốc (upstream): [dgatf/usb_library_rp2040](https://github.com/dgatf/usb_library_rp2040)

Đây là thư viện USB device nhẹ, nhanh cho vi điều khiển RP2040 (Raspberry Pi Pico).
Tài liệu này hướng dẫn **từng bước** cách biên dịch firmware, nạp vào Pico, rồi đo tốc độ USB thực tế từ máy Ubuntu.

---

## Mục lục

1. [Yêu cầu phần cứng](#1-yêu-cầu-phần-cứng)
2. [Cài đặt môi trường build trên Ubuntu](#2-cài-đặt-môi-trường-build-trên-ubuntu)
3. [Cài đặt Pico SDK](#3-cài-đặt-pico-sdk)
4. [Biên dịch firmware](#4-biên-dịch-firmware)
5. [Nạp firmware vào Raspberry Pi Pico](#5-nạp-firmware-vào-raspberry-pi-pico)
6. [Cài đặt công cụ đo tốc độ trên Ubuntu](#6-cài-đặt-công-cụ-đo-tốc-độ-trên-ubuntu)
7. [Cài đặt udev rule để không cần sudo](#7-cài-đặt-udev-rule-để-không-cần-sudo)
8. [Chạy bài đo tốc độ](#8-chạy-bài-đo-tốc-độ)
9. [Hiểu kết quả đầu ra](#9-hiểu-kết-quả-đầu-ra)
10. [Kết quả tham khảo từ tác giả gốc](#10-kết-quả-tham-khảo-từ-tác-giả-gốc)
11. [Xử lý lỗi thường gặp](#11-xử-lý-lỗi-thường-gặp)
12. [So sánh với TinyUSB](#12-so-sánh-với-tinyusb)

---

## 1. Yêu cầu phần cứng

| Thiết bị | Ghi chú |
|---|---|
| Raspberry Pi Pico (hoặc Pico W) | Dùng chip RP2040 |
| Cáp USB Micro-B | Cáp có dây data (không phải cáp chỉ sạc) |
| Máy tính Ubuntu 20.04 / 22.04 / 24.04 | x86_64 hoặc ARM64 đều được |

---

## 2. Cài đặt môi trường build trên Ubuntu

Mở Terminal và chạy lần lượt các lệnh sau:

```bash
sudo apt update
sudo apt install -y \
    cmake \
    gcc-arm-none-eabi \
    libnewlib-arm-none-eabi \
    libstdc++-arm-none-eabi-newlib \
    build-essential \
    git \
    python3 \
    python3-pip
```

Kiểm tra trình biên dịch đã cài đúng chưa:

```bash
arm-none-eabi-gcc --version
# Phải thấy thông tin phiên bản, ví dụ: arm-none-eabi-gcc (15:10.3...) 10.3.1
```

---

## 3. Cài đặt Pico SDK

```bash
# Tạo thư mục làm việc
mkdir -p ~/pico && cd ~/pico

# Clone Pico SDK
git clone https://github.com/raspberrypi/pico-sdk.git
cd pico-sdk
git submodule update --init --recursive
cd ..

# Đặt biến môi trường (thêm vào ~/.bashrc để dùng lại sau)
echo 'export PICO_SDK_PATH=$HOME/pico/pico-sdk' >> ~/.bashrc
source ~/.bashrc
```

Kiểm tra:

```bash
echo $PICO_SDK_PATH
# Phải in ra: /home/<tên-user>/pico/pico-sdk
```

---

## 4. Biên dịch firmware

Clone repo này (nếu chưa có) rồi biên dịch:

```bash
cd ~/pico

# Clone repo
git clone https://github.com/DaoTrucMai/Test_rp2040.git
cd Test_rp2040

# Tạo thư mục build và biên dịch
mkdir -p src/build && cd src/build
cmake ..
make -j$(nproc)
```

Sau khi thành công sẽ xuất hiện file `usb_device.uf2` trong thư mục `src/build/`.

```bash
ls src/build/*.uf2
# usb_device.uf2
```

---

## 5. Nạp firmware vào Raspberry Pi Pico

**Bước 5.1 – Đưa Pico vào chế độ bootloader (BOOTSEL)**

1. **Giữ nút BOOTSEL** trên Pico.
2. **Cắm cáp USB** vào máy Ubuntu (trong khi vẫn giữ nút).
3. **Thả nút BOOTSEL** sau khi đã cắm cáp.

Pico sẽ xuất hiện như một ổ đĩa USB có tên `RPI-RP2`.

**Bước 5.2 – Copy file .uf2 vào Pico**

```bash
# Xem Pico được mount ở đâu
lsblk
# Thường là /media/$USER/RPI-RP2

# Copy firmware (thay <user> bằng tên user của bạn)
cp ~/pico/Test_rp2040/src/build/usb_device.uf2 /media/$USER/RPI-RP2/
```

Hoặc kéo thả file `usb_device.uf2` vào ổ `RPI-RP2` bằng trình quản lý file.

Pico sẽ tự động khởi động lại và chạy firmware. Đèn LED có thể nháy nhẹ.

**Bước 5.3 – Xác nhận Pico đã được nhận**

```bash
lsusb | grep -i "2e8a"
# Phải thấy: Bus ... Device ...: ID 2e8a:0001 ...
```

---

## 6. Cài đặt công cụ đo tốc độ trên Ubuntu

Ubuntu 22.04 / 24.04 dùng Python 3.12+ với PEP 668, **không cho phép `pip install` trực tiếp** vào môi trường hệ thống.
Cách đơn giản nhất là dùng `apt`:

```bash
sudo apt install python3-usb
```

Kiểm tra đã cài thành công:

```bash
python3 -c "import usb.core; print('pyusb OK')"
```

> **Nếu máy bạn không có `python3-usb` trong apt** (Ubuntu cũ hoặc môi trường tùy chỉnh), dùng virtual environment:
>
> ```bash
> sudo apt install python3-venv python3-full
> python3 -m venv ~/pico/venv
> ~/pico/venv/bin/pip install pyusb
> # Sau đó chạy script bằng:
> ~/pico/venv/bin/python3 utils/usb_speed_test.py
> ```

### Cài tất cả trong một lệnh (khuyến nghị)

Thay vì làm bước 6 và 7 riêng lẻ, bạn có thể chạy script tự động:

```bash
bash utils/setup_ubuntu.sh
```

Script này sẽ tự động cài `python3-usb`, cài udev rule, và thêm user vào group `plugdev`.

---

## 7. Cài đặt udev rule để không cần sudo

Theo mặc định, Linux yêu cầu quyền root để truy cập USB. Cài udev rule để chạy script với user thường:

```bash
# Copy file rule vào thư mục udev
sudo cp utils/99-rp2040-usb.rules /etc/udev/rules.d/

# Reload udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Thêm user vào group plugdev
sudo usermod -aG plugdev $USER

# Đăng xuất rồi đăng nhập lại để group có hiệu lực
# Hoặc dùng lệnh tạm thời:
newgrp plugdev
```

Sau bước này **rút và cắm lại** cáp USB của Pico.

---

## 8. Chạy bài đo tốc độ

```bash
cd ~/pico/Test_rp2040
python3 utils/usb_speed_test.py
```

Nếu gặp lỗi quyền truy cập:

```bash
sudo python3 utils/usb_speed_test.py
```

---

## 9. Hiểu kết quả đầu ra

Script sẽ in ra kết quả dạng:

```
Request REQ_EP0_OUT.       Size:   4096 bytes.  Speed:  520 kB/s
Request REQ_EP0_IN.        Size:   4096 bytes.  Speed:  429 kB/s
Request REQ_EP1_OUT.       Size:  40000 bytes.  Speed: 1093 kB/s
Request REQ_EP2_IN.        Size:  40000 bytes.  Speed: 1109 kB/s
Request REQ_EP3_IN stream. Size:  40000 bytes.  Speed: 1091 kB/s
Request REQ_EP4_OUT stream. Size: 40000 bytes.  Speed: 1072 kB/s
```

| Endpoint | Loại | Hướng | Mô tả |
|---|---|---|---|
| EP0 OUT | Control | Host → Pico | Host gửi data qua endpoint điều khiển |
| EP0 IN  | Control | Pico → Host | Pico gửi data qua endpoint điều khiển |
| EP1 OUT | Bulk | Host → Pico | Host gửi khối data lớn |
| EP2 IN  | Bulk | Pico → Host | Pico gửi khối data lớn |
| EP3 IN (stream) | Bulk stream | Pico → Host | Pico stream data liên tục (không có buffer cố định) |
| EP4 OUT (stream) | Bulk stream | Host → Pico | Host stream data liên tục |

**Đơn vị:** `kB/s` = kilobyte/giây (1 kB = 1024 byte).

**Ghi chú về phép đo:** Script hiện tại lấy trung bình **3 lần đo** để cho kết quả ổn định hơn.

---

## 10. Kết quả tham khảo từ tác giả gốc

### Thư viện này (usb_library_rp2040)

```
EP0 OUT:  ~520 kB/s
EP0 IN:   ~429 kB/s
EP1 OUT: ~1093 kB/s
EP2 IN:  ~1109 kB/s
EP3 IN stream:  ~1091 kB/s
EP4 OUT stream: ~1072 kB/s
```

### TinyUSB (để so sánh)

```
EP0 OUT:  ~481 kB/s
EP0 IN:   ~641 kB/s
EP1 OUT:  ~500 kB/s
EP2 IN:   ~631 kB/s
```

### Kết luận

| Endpoint | Thay đổi so với TinyUSB |
|---|---|
| EP0 OUT | +8% |
| EP0 IN  | -33% |
| BULK OUT | +119% |
| BULK IN  | +76% |
| STREAM IN/OUT | Chỉ thư viện này hỗ trợ |

---

## 11. Xử lý lỗi thường gặp

### "Cannot attach USB device" — Bạn đang dùng máy ảo (VirtualBox / VMware)

Thông báo này **không phải lỗi firmware hay script** — đây là Ubuntu đang chạy trong máy ảo và VM chưa được cấp quyền "capture" USB device từ máy host (Windows/macOS).

Khi cắm Pico vào, máy host (Windows/macOS) đang giữ device. VM cần được cấu hình để "cướp" device đó về phía mình.

---

#### Nếu dùng VirtualBox

**Bước 1 – Cài VirtualBox Extension Pack** (chỉ cần làm 1 lần)

Tải tại: https://www.virtualbox.org/wiki/Downloads → chọn đúng phiên bản VirtualBox đang dùng → `Oracle VirtualBox Extension Pack`

Double-click file `.vbox-extpack` vừa tải để cài.

**Bước 2 – Thêm USB filter cho Pico**

1. Tắt máy ảo Ubuntu (Shut down, không phải Pause).
2. Mở VirtualBox → chọn máy ảo Ubuntu → **Settings** → **USB**.
3. Chọn **USB 2.0 (EHCI)** hoặc **USB 3.0 (xHCI)** (cần Extension Pack).
4. Nhấn nút **Add filter from device** (icon USB có dấu +) → chọn **Raspberry Pi Pico**.
5. Nhấn OK.
6. Khởi động lại máy ảo.

**Bước 3 – Capture device thủ công** (nếu vẫn cần)

Khi Pico đã được cắm và máy ảo đang chạy:
- Menu VirtualBox: **Devices** → **USB** → chọn **Raspberry Pi Pico (2E8A:0001)** → tích chọn.

Kiểm tra trong Ubuntu:
```bash
lsusb | grep 2e8a
# Phải thấy: Bus ... ID 2e8a:0001
```

---

#### Nếu dùng VMware Workstation / Fusion

**Bước 1 – Cấu hình auto-connect USB**

- Menu: **VM** → **Settings** → **USB Controller**
- Chọn **USB 3.1** (hoặc 2.0)
- Tích **Automatically connect new USB devices**
- Nhấn OK.

**Bước 2 – Connect thủ công**

Khi Pico đang cắm:
- Menu: **VM** → **Removable Devices** → **Raspberry Pi Pico** → **Connect (Disconnect from Host)**

---

#### Lưu ý đặc biệt: Pico có 2 USB ID khác nhau

Khi cắm Pico, nó có thể xuất hiện với 2 ID khác nhau tùy trạng thái:

| Trạng thái | USB ID | Mô tả |
|---|---|---|
| Đang ở chế độ BOOTSEL (chờ flash) | `2E8A:0003` | Mass storage để nạp firmware |
| Firmware đang chạy bình thường | `2E8A:0001` | Thiết bị USB custom của library này |

Bạn cần tạo filter (hoặc capture) **cả hai ID** trong VM settings, vì:
1. Khi cắm Pico lần đầu (hoặc sau khi reset) nó sẽ xuất hiện là `0003`.
2. Sau khi firmware boot xong, nó chuyển sang `0001`.
3. Nếu chỉ filter `0001`, VM sẽ bỏ lỡ quá trình kết nối ban đầu.

Cách thêm filter cho cả hai trong VirtualBox:
- Thêm filter thứ nhất: Vendor `2E8A`, Product `0003`
- Thêm filter thứ hai: Vendor `2E8A`, Product `0001`

---

### Pico không kết nối được sau khi flash firmware

Đây là vấn đề phổ biến. Dưới đây là các nguyên nhân theo thứ tự khả năng xảy ra:

**Bước chẩn đoán nhanh:**
```bash
lsusb | grep 2e8a
```

| Kết quả `lsusb` | Nguyên nhân | Giải pháp |
|---|---|---|
| Không thấy gì | Firmware crash (panic) hoặc firmware không chạy | Rút cắm lại Pico |
| Thấy `2e8a:0003` (BootROM) | Firmware bị lỗi, Pico reset về bootloader | Flash lại firmware |
| Thấy `2e8a:0001` | Firmware đang chạy tốt, lỗi do phần mềm phía host | Xem bên dưới |

**Nguyên nhân 1 – Firmware crash do Unhandled IRQ (đã sửa trong repo này)**

Firmware gốc có `panic("Unhandled IRQ")` — nếu Ubuntu gửi bất kỳ USB interrupt nào ngoài 3 loại được xử lý, Pico **treo ngay lập tức**. Phiên bản trong repo này đã thay bằng `usb_hw_clear->sie_status` để bỏ qua interrupt lạ thay vì crash.

**Nguyên nhân 2 – `dev.set_configuration()` giữ claim interface (đã sửa)**

Phiên bản cũ của script gọi `dev.set_configuration()`, khiến pyusb claim interface nhưng không release đúng cách. Lần chạy kế tiếp sẽ báo lỗi `Resource busy`. Đã sửa bằng cách xóa lệnh đó và thêm `usb.util.dispose_resources(dev)` ở cuối.

**Nguyên nhân 3 – EP4 buffer_control không được reset (đã sửa)**

Sau khi EP4 OUT stream hoàn thành, `buffer_control` không được xóa, khiến lần transfer tiếp theo bị stuck. Đã uncomment `*ep->buffer_control = 0`.

**Nguyên nhân 4 – Cáp USB chỉ có dây nguồn, không có dây data**

Dấu hiệu: Đèn LED Pico sáng nhưng `lsusb` không thấy. Đổi sang cáp khác.

**Nguyên nhân 5 – Cần rút cắm lại sau khi firmware crash**

Nếu Pico bị treo, chỉ cần rút cáp USB ra và cắm lại (không cần giữ BOOTSEL vì firmware vẫn còn trong flash).

### `ValueError: Device not found`

- Kiểm tra Pico có đang được cắm không: `lsusb | grep 2e8a`
- Kiểm tra firmware đã nạp đúng chưa (nạp lại nếu cần).
- Thử `sudo python3 utils/usb_speed_test.py` để loại trừ lỗi quyền truy cập.

### `usb.core.USBError: [Errno 13] Access denied`

- Chưa cài udev rule. Làm theo [Bước 7](#7-cài-đặt-udev-rule-để-không-cần-sudo).
- Rút và cắm lại Pico sau khi cài rule.

### `error: externally-managed-environment` (Ubuntu 22.04 / 24.04)

Ubuntu mới dùng PEP 668, không cho `pip install` trực tiếp. Dùng `apt` thay thế:

```bash
sudo apt install python3-usb
```

Hoặc nếu muốn dùng pip, tạo virtual environment:

```bash
sudo apt install python3-venv python3-full
python3 -m venv ~/pico/venv
~/pico/venv/bin/pip install pyusb
~/pico/venv/bin/python3 utils/usb_speed_test.py
```

### `arm-none-eabi-gcc: command not found`

```bash
sudo apt install gcc-arm-none-eabi
```

### `CMake Error: PICO_SDK_PATH not set`

```bash
export PICO_SDK_PATH=$HOME/pico/pico-sdk
# Hoặc thêm vào ~/.bashrc
```

### Lỗi khi cmake: `pico_sdk_import.cmake not found`

Đảm bảo biến `PICO_SDK_PATH` trỏ đúng vào thư mục pico-sdk và SDK đã được clone đầy đủ:

```bash
ls $PICO_SDK_PATH/external/pico_sdk_import.cmake
```

### Tốc độ đo được thấp bất thường

- Dùng cáp USB chất lượng tốt (không phải cáp chỉ sạc).
- Cắm trực tiếp vào cổng USB của máy, không qua hub.
- Đóng các chương trình nặng khi đo để tránh tranh chấp CPU.

---

## 12. So sánh với TinyUSB

Thư mục `tinyusb_comparison/` chứa source code ví dụ tương tự dùng TinyUSB để bạn có thể tự build và so sánh.

Biên dịch TinyUSB comparison:

```bash
cd ~/pico/Test_rp2040/tinyusb_comparison
mkdir build && cd build
cmake ..
make -j$(nproc)
```

Nạp file `usb_device.uf2` tương ứng vào Pico rồi chạy lại `usb_speed_test.py`.

---

## Cấu trúc thư mục

```
.
├── src/
│   ├── main.c          # Chương trình chính, xử lý các request USB
│   ├── usb.c           # Core USB driver
│   ├── usb.h           # API public
│   ├── usb_common.h    # Định nghĩa USB chung
│   ├── usb_config.c    # Khởi tạo endpoints và device config
│   ├── usb_config.h    # Khai báo endpoints, descriptors
│   └── CMakeLists.txt
├── tinyusb_comparison/ # Ví dụ tương đương dùng TinyUSB
├── utils/
│   ├── usb_speed_test.py      # Script đo tốc độ (đã sửa lỗi timing)
│   ├── 99-rp2040-usb.rules    # udev rule cho Linux
│   └── comparison.png         # Biểu đồ so sánh tốc độ
├── LICENSE
└── README.md
```

---

## Thay đổi so với repo gốc

- **`utils/usb_speed_test.py`**: Sửa lỗi tính thời gian dùng `c.microseconds` (chỉ lấy phần dưới 1 giây, gây sai số lớn khi transfer chậm) → dùng `c.total_seconds()` cho kết quả chính xác. Thêm `dev.set_configuration()` và auto-detach kernel driver. Tăng số lần lặp lên 3 để lấy trung bình.
- **`utils/99-rp2040-usb.rules`**: File udev rule mới, cho phép truy cập USB không cần sudo.
- **`README.md`**: Thêm hướng dẫn sử dụng chi tiết bằng tiếng Việt.
