import psutil
import subprocess
import time
import os
import requests
from datetime import timedelta

tienTrinh = ['flood', 'tlskill', 'bypasscf', 'killercf', 'ctccf', 'floodctc']
TELEGRAM_TOKEN = '8039598203:AAHEmboLSteoEIvu-bSnqFUVn7A6OgDQVr4'
CHAT_ID = '7371969470'

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    params = {'chat_id': CHAT_ID, 'text': message}
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Lỗi khi gửi tin nhắn đến Telegram: {response.status_code}")
    except Exception as e:
        print(f"Không thể kết nối đến Telegram: {e}")

def check_system_usage():
    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)
    total_cpu = psutil.cpu_count(logical=True)
    total_ram = psutil.virtual_memory().total / (1024 * 1024 * 1024)
    used_ram = psutil.virtual_memory().used / (1024 * 1024 * 1024)
    free_ram = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    cpu_free = 100 - cpu_usage
    ram_free = 100 - ram_usage
    cpu_freq = psutil.cpu_freq().current
    gpu_info = "Không có GPU"

    if os.path.exists("/dev/nvidia0"): gpu_info = "NVIDIA GPU Detected"
    elif os.path.exists("/dev/dri/card0"): gpu_info = "GPU tích hợp (AMD hoặc Intel)"
    
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = str(timedelta(seconds=int(uptime_seconds)))

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

def kill_processes():
    for process_name in tienTrinh:
        print(f"Đang kill tiến trình: {process_name} với pkill -9 -f")
        try:
            if os.geteuid() != 0:
                print("Cảnh báo: Cần quyền root để thực hiện lệnh pkill.")
                return
            subprocess.run(['pkill', '-9', '-f', process_name], check=True)
            print(f"Đã kill tiến trình: {process_name}")
        except Exception as e:
            print(f"Lỗi khi kill tiến trình {process_name}: {e}")

def monitor_system():
    last_kill_time = time.time()
    last_telegram_time = time.time()
    last_message = ""

    while True:
        current_time = time.time()

        if current_time - last_telegram_time >= 7:
            cpu_usage, ram_usage, system_message = check_system_usage()
            if system_message != last_message:
                send_telegram_message(system_message)
                last_message = system_message
            last_telegram_time = current_time

        cpu_usage, ram_usage, _ = check_system_usage()

        if ram_usage > 95:
            print("⚠️ RAM > 95%. Đang pkill...")
            send_telegram_message("⚠️ RAM > 95%. Đang pkill...")
            kill_processes()
            last_kill_time = current_time

        if current_time - last_kill_time >= 300:
            print("⏳ 5 phút đã trôi qua, thực hiện pkill tất cả tiến trình")
            send_telegram_message("⏳ Đang thực hiện pkill tất cả tiến trình...")
            kill_processes()
            last_kill_time = current_time

        time.sleep(1)

if __name__ == "__main__":
    monitor_system()
