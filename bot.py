import vk_api 
import re
import time
from vk_api.longpoll import VkLongPoll, VkEventType 
from apscheduler.schedulers.background import BackgroundScheduler 
from datetime import datetime, timedelta

# === НАСТРОЙКИ ===
TOKEN = "vk1.a.QDK5NCJ724CtwjKKYNkHBNqRdOREI159MdZcvU_Z1JxCQEYTxFomxJEbPbrnjb5N_7-hN6WpTwfLT0yNOdcKr7CU3Cr60KM6EawCapKDu7u6A9fl4adVYuDQuzmgBbyd4xAFMZQOY6cPPtVTHxNgWrSlOFpiNrzOnfY7Ex0tI1kNJbHRlfdncM0FMrpa_4Hz-n0so28B4d4vKex_KQ8PpA"  # Вставь сюда токен сообщества
GROUP_ID = 229831073   # ID группы без кавычек

# === ИНИЦИАЛИЗАЦИЯ ===
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
scheduler = BackgroundScheduler()
scheduler.start()
reminders = {}

# === ФУНКЦИИ ===
def send_message(peer_id, message):
    vk.messages.send(peer_id=peer_id, message=message, random_id=0)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m")
    except ValueError:
        return None

def schedule_reminder(peer_id, user_tag, date_str):
    date = parse_date(date_str)
    if not date:
        return
    
    # Устанавливаем напоминание на 12:00 следующего дня
    now = datetime.now()
    date = date.replace(year=now.year)
    reminder_time = datetime(date.year, date.month, date.day, 12, 0) + timedelta(days=1)
    
    scheduler.add_job(send_message, 'date', run_date=reminder_time, args=[peer_id, f"{user_tag} - напоминание о подсчёте недели"])
    reminders[user_tag] = reminder_time

def process_message(event):
    global reminders
    text = event.text.strip()
    peer_id = event.peer_id
    
    # Проверяем формат сообщения
    match = re.findall(r"(@\S+) - \d{1,2}\.\d{1,2}", text)
    if match:
        for m in match:
            user_tag, date_str = m.split(" - ")
            schedule_reminder(peer_id, user_tag, date_str)
        send_message(peer_id, "Принято")
        return
    
    # Проверяем команду изменения
    if text.startswith("!изменение!"):
        match = re.findall(r"(@\S+) - \d{1,2}\.\d{1,2}", text)
        if match:
            for m in match:
                user_tag, date_str = m.split(" - ")
                schedule_reminder(peer_id, user_tag, date_str)
            send_message(peer_id, "Принято")
        return

# === ОСНОВНОЙ ЦИКЛ ===
print("Бот запущен...")
while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                process_message(event)
    except Exception as e:
        print("Ошибка:", e)
        time.sleep(5)
