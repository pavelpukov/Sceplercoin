import telebot
from telebot import types
import time
import os
from datetime import datetime, timedelta

# Токен вашего бота
TOKEN = 'token'
ADMIN_ID = 'id'  # Замените 'YOUR_ADMIN_TELEGRAM_ID' на настоящий ID админа

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Путь к файлу базы данных и логов
DATABASE_FILE = 'baza.txt'
LOGS_FILE = 'logs.txt'

# Функция для записи логов
def log_action(user_id, action):
    with open(LOGS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{user_id} - {action}\n")

# Функция для чтения базы данных
def read_database():
    if not os.path.exists(DATABASE_FILE):
        return {}
    with open(DATABASE_FILE, 'r') as f:
        lines = f.readlines()
    data = {}
    for line in lines:
        parts = line.strip().split(",")
        data[parts[0]] = {
            "number": parts[1],
            "registration_time": parts[2],
            "balance": int(parts[3]),
            "last_mined": parts[4],
        }
    return data

# Функция для записи в базу данных
def write_database(data):
    with open(DATABASE_FILE, 'w') as f:
        for user_id, info in data.items():
            f.write(f"{user_id},{info['number']},{info['registration_time']},{info['balance']},{info['last_mined']}\n")

# Функция для регистрации пользователя
def register_user(user_id, phone_number):
    data = read_database()
    if user_id not in data:
        registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data[user_id] = {
            "number": phone_number,
            "registration_time": registration_time,
            "balance": 0,
            "last_mined": "1970-01-01 00:00:00",
        }
    write_database(data)

# Функция для обновления баланса пользователя
def update_balance(user_id, amount):
    data = read_database()
    if user_id in data:
        data[user_id]["balance"] += amount
    write_database(data)

# Функция для проверки времени последней добычи
def can_mine(user_id):
    data = read_database()
    if user_id in data:
        last_mined = datetime.strptime(data[user_id]["last_mined"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > last_mined + timedelta(hours=2):
            return True
    return False

# Функция для обновления времени последней добычи
def update_last_mined(user_id):
    data = read_database()
    if user_id in data:
        data[user_id]["last_mined"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_database(data)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.chat.id)
    data = read_database()
    if user_id not in data:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button = types.KeyboardButton(text="Зарегистрироваться", request_contact=True)
        markup.add(button)
        bot.send_message(message.chat.id, "Привет! Это бот для майнинга Sceplercoin 🪙 её листинг будет в 2025 году. Для подтверждения того чтобы не бот подтвердите что у вас настоящий номер телефона. Нажмите на кнопку 'Зарегистрироваться'.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы!")

# Обработчик контакта
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact is not None:
        user_id = str(message.chat.id)
        phone_number = message.contact.phone_number
        register_user(user_id, phone_number)
        log_action(user_id, "Регистрация")
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button = types.KeyboardButton("Майнить Sceplercoin 🪙")
        markup.add(button)
        bot.send_message(message.chat.id, "Нажми на кнопку Sceplercoin 🪙 и получишь 2000 тысячи Sceplercoin 🪙.", reply_markup=markup)

# Обработчик кнопки для майнинга
@bot.message_handler(regexp="Майнить Sceplercoin 🪙")
def handle_mining(message):
    user_id = str(message.chat.id)
    if can_mine(user_id):
        update_balance(user_id, 2000)
        update_last_mined(user_id)
        log_action(user_id, "Майнинг 2000 Sceplercoin 🪙")
        bot.send_message(message.chat.id, "Ты получил 2000 Sceplercoin 🪙 на баланс!")
    else:
        bot.send_message(message.chat.id, "Извините, майнить можно только раз в 2 часа.")

# Обработчик команды /profile
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = str(message.chat.id)
    data = read_database()
    if user_id in data:
        user_data = data[user_id]
        response = (f"🆔ID: {user_id}\n"
                    f"📞Номер: {user_data['number']}\n"
                    f"⏳Время регистрации: {user_data['registration_time']}\n"
                    f"🪙Баланс: {user_data['balance']} Sceplercoin 🪙")
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Вы еще не зарегистрированы.")

# Обработчик команды /output
@bot.message_handler(commands=['output'])
def handle_output(message):
    bot.send_message(message.chat.id, "Вывод доступен от 500к Sceplercoin. Также за вывод до листинга будет взнематся комисия от 2 USD.")

# Обработчик команды /help для админов
@bot.message_handler(commands=['help'])
def handle_help(message):
    if str(message.chat.id) == ADMIN_ID:
        response = ("/replenishment (id) (сумма) - Пополнит баланс пользователя с id.\n"
                    "/clear (id) (сумма) - Вычтет с баланса пользователя.\n"
                    "/logs (id) - Выгружает все логи определённого пользователя.")
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Неизвестная команда.")

# Команда /replenishment для пополнения баланса пользователя
@bot.message_handler(commands=['replenishment'])
def handle_replenishment(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            command, user_id, amount = message.text.split()
            update_balance(user_id, int(amount))
            log_action(user_id, f"Пополнение {amount} Sceplercoin 🪙")
            bot.send_message(message.chat.id, f"Баланс пользователя {user_id} пополнен на {amount} Sceplercoin 🪙.")
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат команды. Используйте: /replenishment (id) (сумма)")

# Команда /clear для вычитания баланса пользователя
@bot.message_handler(commands=['clear'])
def handle_clear(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            command, user_id, amount = message.text.split()
            update_balance(user_id, -int(amount))
            log_action(user_id, f"Вычитание {amount} Sceplercoin 🪙")
            bot.send_message(message.chat.id, f"Баланс пользователя {user_id} уменьшен на {amount} Sceplercoin 🪙.")
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат команды. Используйте: /clear (id) (сумма)")

# Команда /logs для выгрузки логов определённого пользователя
@bot.message_handler(commands=['logs'])
def handle_logs(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            command, user_id = message.text.split()
            with open(LOGS_FILE, 'r') as file:
                logs = [line for line in file if line.startswith(user_id)]
            logs_filename = f"logs_{user_id}.txt"
            with open(logs_filename, 'w') as log_file:
                log_file.writelines(logs)
            bot.send_document(message.chat.id, open(logs_filename, 'r'))
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат команды. Используйте: /logs (id)")

# Обработчик всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_unknown_message(message):
    bot.send_message(message.chat.id, "Неизвестная команда.")

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
