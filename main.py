import telebot
from pyowm import OWM
import pickle
import os
import datetime as d
import cconverter as cc
import configparser
import googleAPI as gg

config = configparser.ConfigParser()
config.read('settings.ini')
token = config['token']['bot']

# Со
def save_users(type):
    if type == 'admin':
        with open('admins.pickle', 'wb') as f:
            pickle.dump(admins_list, f)

    elif type == 'user':
        with open('users.pickle', 'wb') as f:
            pickle.dump(users_list, f)


def load_users():
    with open('admins.pickle', 'rb') as f:
        try:
            admins_list = pickle.load(f)
        except Exception as e:
            print(f'error: {e}')
            admins_list = []
    with open('users.pickle', 'rb') as f:
        try:
            users_list = pickle.load(f)
        except Exception as e:
            print(f'error: {e}')
            users_list = []
    return admins_list, users_list


def check_auth(id, type):
    if type == 'admin':
        if (id in admins_list) == True:
            return True
        else:
            return False

    elif type == "user":
        if (id in users_list) == True:
            return True
        else:
            return False


admins_list, users_list = load_users()


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, 'Пожалуйста авторизуйтесь')

    @bot.message_handler(content_types=['document'])

    def table(message):
        """
                Обрабатывает документ формата .xlsx
        """
        if (message.chat.id in admins_list) == True or (message.chat.id in users_list) == True:
            try:
                chat_id = message.chat.id
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src = '/Users/maksimpiven/PycharmProjects/tg_bot/' + message.document.file_name
                filename, file_extension = os.path.splitext(src)
                if file_extension == '.xlsx':
                    with open(src, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    bot.reply_to(message, "Пожалуй, я сохраню это")
            except Exception as e:
                bot.reply_to(message, e)
                file_extension = ''
            if file_extension == '.xlsx':
                gg.prog(message.document.file_name)
                with open('result.xlsx', 'rb') as file:
                    bot.send_document(message.chat.id, file)
            else:
                bot.reply_to(message, 'Неправильный формат файла')

    @bot.message_handler(commands=['shutdown'])

    def stop_bot(message, force=False):
        """
                Выключает бота
        """
        if check_auth(message.chat.id, 'admin') == True or force == True:
            bot.send_message(message.chat.id, "Бот наелся и ложится спать")
            print('Бот ложится')
            bot.stop_polling()
            print('Бот умер')
            exit()
        elif check_auth(message.chat.id, 'user') == True:
            bot.send_message(message.chat.id, "НЕ ТРОГАЙ.")
        else:
            bot.send_message(message.chat.id, 'Пожалуйста авторизуйтесь')

    @bot.message_handler(commands=['currencies'])
    def currency(message):
        """
                Показывает актуальный курс валют
        """
        if (message.chat.id in admins_list) == True or (message.chat.id in users_list) == True:
            today = d.datetime.today()
            bot.send_message(message.chat.id, f"Время проверки: {today.strftime('%Y-%m-%d-%H.%M.%S')}\n"
                                              f"Курс доллара: {cc.convert('usd')}\n"
                                              f"Курс евро: {cc.convert('eur')}")
        else:
            bot.send_message(message.chat.id, 'Пожалуйста авторизуйтесь')

    @bot.message_handler(commands=['weather'])
    def weather(message):
        """
                Показывает актуальную погоду
        """
        if (message.chat.id in admins_list) == True or (message.chat.id in users_list) == True:
            appid = config['weather']['id']
            owm = OWM(appid)
            mgr = owm.weather_manager()

            observation = mgr.weather_at_place('Moscow,RU')
            w = observation.weather
            tem = w.temperature('celsius')
            bot.send_message(message.chat.id,f"Температура: {round(tem['temp'])}°С\n"
                                             f"Максимальная: {round(tem['temp_max'])}°С\n"
                                             f"Минимальная: {round(tem['temp_min'])}°С\n"
                                             f"Ощущается как: {round(tem['feels_like'])}°С")
        else:
            bot.send_message(message.chat.id, 'Пожалуйста авторизуйтесь')

    @bot.message_handler(commands=['ops'])
    def ops(message):
        """
                Показывает залогиненных юзеров и админов
        """
        if (message.chat.id in admins_list):
            bot.send_message(message.chat.id, f"Список админов: {admins_list}\n"
                                              f"Список юзеров: {users_list}")
        elif (message.chat.id in users_list):
            bot.send_message(message.chat.id, "Нет доступа")
        else:
            bot.send_message(message.chat.id, 'Пожалуйста авторизуйтесь')

    @bot.message_handler(commands=['help'])
    def helper(message):
        """
                Показывает список доступных комманд
        """
        if (message.chat.id in admins_list):
            bot.send_message(message.chat.id, "Перечень доступных комманд:\n"
                                              "/weather - показывает актуальную погоду в Москве\n"
                                              "/currencies - показывает акутальный курс Евро и Доллара к рублю\n"
                                              "/help - список доступных комманд\n"
                                              "/ops - список всех залогиненных юзеров и админов\n"
                                              "/shutdown - выключить бота")
        elif (message.chat.id in users_list):
            bot.send_message(message.chat.id, "Перечень доступных комманд:\n"
                                              "/weather - показывает актуальную погоду в Москве\n"
                                              "/currencies - показывает акутальный курс Евро и Доллара к рублю\n"
                                              "/help - список доступных комманд\n")
        else:
            bot.send_message(message.chat.id, 'Пожалуйста авторизуйтесь')
    @bot.message_handler(content_types=['text'])
    def send_text(message):
        """
                Обрабатывает сообщения
        """
        if message.text.lower() == "привет":
            bot.send_message(message.chat.id, "Хай буде так хлопчik")

        elif message.text.lower() == config.get('tg', 'admin'):
            if check_auth(message.chat.id, 'admin') == False:
                admins_list.append(message.chat.id)
                save_users('admin')
                bot.send_message(message.chat.id, "Добавлен в список админов.")

                print('Добавлен в список админов.', message.chat.id)
            else:
                bot.send_message(message.chat.id, "Ты уже в списке админов")
        elif message.text.lower() == config.get('tg', 'user'):
            if check_auth(message.chat.id, 'user') == False:
                users_list.append(message.chat.id)
                save_users('user')
                print('Добавлен в список [аб]юзеров', message.chat.id)
                bot.send_message(message.chat.id, "Добавлен в список [аб]юзеров")
            else:
                bot.send_message(message.chat.id, "Ты уже в списке [аб]юзеров")
        else:
            if (message.chat.id in admins_list) == True or (message.chat.id in users_list) == True:
                bot.send_message(message.chat.id, "Не розумiю")
            else:
                start_message(message)
    bot.polling()


if __name__ == "__main__":
    telegram_bot(token)
