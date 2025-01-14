import psutil
import subprocess
import time
import os
import platform
import requests
from datetime import datetime, timedelta  # Sửa lỗi tại đây

# Danh sách các tiến trình cần kill
tienTrinh = ['flood', 'tlskill', 'bypasscf', 'killercf', 'ctccf', 'floodctc']

# Cấu hình Bot Telegram
TELEGRAM_TOKEN = '8039598203:AAHEmboLSteoEIvu-bSnqFUVn7A6OgDQVr4'
CHAT_ID = '7371969470'

# Hàm gửi thông báo qua Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    params = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Lỗi khi gửi tin nhắn đến Telegram: {response.status_code}")
    except Exception as e:
        print(f"Không thể kết nối đến Telegram: {e}")

# Hàm kiểm tra tình trạng sử dụng RAM và CPU
def check_system_usage():
    # Lấy thông tin sử dụng RAM và CPU
    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)  # Kiểm tra CPU trong 1 giây
    total_cpu = psutil.cpu_count(logical=True)  # Số lượng lõi CPU logic (cả lõi vật lý và ảo)
    total_ram = psutil.virtual_memory().total / (1024 * 1024 * 1024)  # Tổng dung lượng RAM tính bằng GB
    used_ram = psutil.virtual_memory().used / (1024 * 1024 * 1024)  # RAM đã sử dụng tính bằng GB
    free_ram = psutil.virtual_memory().available / (1024 * 1024 * 1024)  # RAM còn trống tính bằng GB
    # Tổng phần trăm CPU còn lại
    cpu_free = 100 - cpu_usage
    # Tổng phần trăm RAM còn lại
    ram_free = 100 - ram_usage

    # Lấy tần số CPU hiện tại (GHz)
    cpu_freq = psutil.cpu_freq().current

    # Kiểm tra GPU
    gpu_info = "Không có GPU"
    try:
        # Kiểm tra xem 'lspci' có tồn tại không
        if subprocess.call(["which", "lspci"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            # Dùng lệnh lspci để tìm GPU
            gpu_output = subprocess.check_output(r"lspci | grep -i 'vga|3d|2d'", shell=True).decode('utf-8').strip()
            if gpu_output:
                gpu_info = gpu_output
            else:
                gpu_info = "Không có GPU trên hệ thống"
        else:
            gpu_info = "Không tìm thấy lspci, không thể xác định GPU"
    except subprocess.CalledProcessError:
        gpu_info = "Không có GPU hoặc không thể xác định GPU"

    # Lấy uptime
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = str(timedelta(seconds=int(uptime_seconds)))  # Sử dụng timedelta đã được import

    # Tạo thông báo với dấu phân cách rõ ràng giữa các thông số và thêm icon
    message = (
        f"🖥️ **Trạng thái hệ thống**:\n"
        f"---------------------------\n"
        f"⚙️ **Tổng số CPU**: {total_cpu} lõi\n"
        f"💻 **Phần trăm sử dụng CPU**: {cpu_usage}%\n"
        f"🌿 **Phần trăm CPU còn trống**: {cpu_free}%\n"
        f"---------------------------\n"
        f"💾 **Tổng dung lượng RAM**: {total_ram:.2f} GB\n"
        f"🗂️ **RAM đã sử dụng**: {used_ram:.2f} GB\n"
        f"🛑 **RAM còn trống**: {free_ram:.2f} GB\n"
        f"🌿 **Phần trăm sử dụng RAM**: {ram_usage}%\n"
        f"🌿 **Phần trăm RAM còn trống**: {ram_free}%\n"
        f"---------------------------\n"
        f"Uptime: {uptime}\n"
        f"CPU: ({total_cpu} cores) @ {cpu_freq:.2f} GHz\n"
        f"GPU: {gpu_info}\n"
    )
    
    return cpu_usage, ram_usage, message

# Hàm thực hiện lệnh pkill với -9 -f (kill mạnh mẽ)
def kill_processes():
    for process_name in tienTrinh:
        print(f"Đang kill tiến trình: {process_name} với pkill -9 -f")
        try:
            # Kiểm tra quyền root trước khi thực hiện pkill
            if os.geteuid() != 0:
                print("Cảnh báo: Cần quyền root để thực hiện lệnh pkill.")
                return

            # Sử dụng pkill với -9 -f để kill các tiến trình
            subprocess.run(['pkill', '-9', '-f', process_name], check=True)
            print(f"Đã kill tiến trình: {process_name}")
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi kill tiến trình {process_name}: {e}")
        except Exception as ex:
            print(f"Đã xảy ra lỗi không mong muốn: {ex}")

# Hàm chính để theo dõi hệ thống và thực thi pkill khi cần
def monitor_system():
    last_kill_time = time.time()  # Lưu thời gian thực hiện pkill cuối cùng
    last_telegram_time = time.time()  # Lưu thời gian gửi thông báo Telegram cuối cùng
    last_message = ""  # Biến lưu thông điệp gần nhất để so sánh và tránh gửi trùng lặp

    while True:
        current_time = time.time()

        # Cập nhật trạng thái hệ thống mỗi 7 giây
        if current_time - last_telegram_time >= 7:
            cpu_usage, ram_usage, system_message = check_system_usage()  # Lấy thông tin tài nguyên

            # Chỉ gửi thông báo nếu thông báo khác với lần trước
            if system_message != last_message:
                send_telegram_message(system_message)  # Gửi thông báo
                last_message = system_message  # Cập nhật thông điệp vừa gửi

            last_telegram_time = current_time  # Cập nhật thời gian gửi thông báo

        # Kiểm tra tài nguyên hệ thống nếu sử dụng quá 95% RAM
        cpu_usage, ram_usage, _ = check_system_usage()  # Cập nhật tài nguyên

        if ram_usage > 95:  # Chỉ pkill khi RAM sử dụng trên 95%
            print("⚠️ Cảnh báo: Tài nguyên RAM vượt quá 95%. Đang thực hiện pkill...")
            send_telegram_message("⚠️ Cảnh báo: Tài nguyên RAM vượt quá 95%. Đang thực hiện pkill...")
            kill_processes()
            last_kill_time = current_time  # Cập nhật thời gian pkill

        # Thực hiện pkill mỗi 5 phút
        if current_time - last_kill_time >= 300:
            print("⏳ 5 phút đã trôi qua, thực hiện pkill tất cả tiến trình")
            send_telegram_message("⏳ Đang thực hiện pkill tất cả tiến trình...")
            kill_processes()
            last_kill_time = current_time  # Cập nhật thời gian pkill tổng

        time.sleep(1)  # Chờ 1 giây trước khi kiểm tra lại

if __name__ == "__main__":
    monitor_system()
