import psutil
import subprocess
import time
import os
import requests

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

    # Tạo thông báo
    message = f"CPU Usage: {cpu_usage}% | RAM Usage: {ram_usage}%"
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
            result = subprocess.run(['pkill', '-9', '-f', process_name], check=True)
            if result.returncode == 0:
                print(f"Đã kill tiến trình: {process_name}")
            else:
                print(f"Không thể kill tiến trình: {process_name} với mã lỗi {result.returncode}")
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi kill tiến trình {process_name}: {e}")
        except Exception as ex:
            print(f"Đã xảy ra lỗi không mong muốn: {ex}")

# Hàm chính để theo dõi hệ thống và thực thi pkill khi cần
def monitor_system():
    last_kill_time = time.time()  # Lưu thời gian thực hiện pkill cuối cùng
    last_telegram_time = time.time()  # Lưu thời gian gửi thông báo Telegram cuối cùng
    last_total_kill_time = time.time()  # Lưu thời gian thực hiện pkill tổng cuối cùng

    while True:
        current_time = time.time()

        # Cập nhật trạng thái hệ thống mỗi 7 giây
        if current_time - last_telegram_time >= 7:
            cpu_usage, ram_usage, system_message = check_system_usage()  # Gọi hàm để lấy cpu_usage và ram_usage
            send_telegram_message(f"Trạng thái hệ thống: {system_message}")
            last_telegram_time = current_time  # Cập nhật thời gian gửi thông báo

        # Kiểm tra tài nguyên hệ thống nếu sử dụng quá 95%
        if cpu_usage > 95 or ram_usage > 95:
            print("Cảnh báo: Tài nguyên hệ thống vượt quá 95%. Đang thực hiện pkill...")
            send_telegram_message("Cảnh báo: Tài nguyên hệ thống vượt quá 95%. Đang thực hiện pkill...")
            kill_processes()
            last_kill_time = current_time  # Cập nhật thời gian pkill

        # Kiểm tra và kill tiến trình sau mỗi 5 phút (300 giây)
        if current_time - last_total_kill_time >= 300:
            print("5 phút đã trôi qua, thực hiện pkill tất cả tiến trình")
            send_telegram_message("Đang thực hiện pkill tất cả tiến trình...")
            kill_processes()
            last_total_kill_time = current_time  # Cập nhật thời gian pkill tổng

        time.sleep(1)  # Chờ 1 giây trước khi kiểm tra lại

if __name__ == "__main__":
    monitor_system()
