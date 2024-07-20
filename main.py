import telebot
import os
import requests
from dotenv import load_dotenv
from dotenv import dotenv_values


# Connecting environment variables (env)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(load_dotenv(dotenv_path))


bot = telebot.TeleBot(dotenv_values()['TELEGRAM_TOKEN'])


@bot.message_handler(commands=['create_folder'])
def create_folder_handler(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Введите название папки')
    bot.register_next_step_handler(msg, create_folder)


def create_folder(message):
    path = message.text
    headers = {'Authorization': 'OAuth %s' % dotenv_values()['YANDEX_TOKEN']}
    request_url = dotenv_values()['HOST_YANDEX_DISK'] + '/v1/disk/resources?path=%s' % path
    response = requests.put(url=request_url, headers=headers)
    if response.status_code == 201:
        bot.reply_to(message, "Я создал папку %s" % path)
    else:
        bot.reply_to(message, '\n'.join(["Произошла ошибка. Текст ошибки", response.text]))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hellow')
    bot.send_message(message.chat.id, 'hellow')


if __name__ == '__main__':
    bot.polling()


