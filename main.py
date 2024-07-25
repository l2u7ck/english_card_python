import os
import random

from dotenv import load_dotenv
from dotenv import dotenv_values
from telebot.storage import StateMemoryStorage
from telebot import types, TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
import work_database as db

# Connecting environment variables (env)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(load_dotenv(dotenv_path))

print('Start telegram bot...')
state_storage = StateMemoryStorage()
bot = TeleBot(dotenv_values()['TOKEN_BOT'], state_storage=state_storage)


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['translate_word']} - {data['target_word']}"


class Command:

    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):

    target_word = State()
    translate_word = State()
    another_words = State()


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):

    cid = message.chat.id

    if db.search_user(cid):
        db.new_user_db(cid)
        bot.send_message(cid, "Привет, давай подтянем твои знания по английскому ☝☝☝\n"
                              "Ты можешь использовать этот тренажер, как конструктор добавляя или удаляя слова.\n"
                              "Ну что, начнём ⬇️")

    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    words = db.words(cid)

    if words:

        target_word = words[1]
        translate = words[0]
        target_word_btn = types.KeyboardButton(target_word)
        buttons.append(target_word_btn)

        others = [words[2], words[3], words[4]]
        other_words_btns = [types.KeyboardButton(word) for word in others]
        buttons.extend(other_words_btns)

        random.shuffle(buttons)

        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)

        buttons.extend([add_word_btn, next_btn, delete_word_btn])

        markup.add(*buttons)

        greeting = f"Выбери перевод слова:\n👉 {translate}"

        bot.send_message(message.chat.id, greeting, reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['target_word'] = target_word
            data['translate_word'] = translate
            data['other_words'] = others

    else:
        greeting = (f'В словаре меньше 6 слов 👐\n'
                    f'Добавьте больше слов 👋')
        bot.send_message(message.chat.id, greeting)
        add_word_info(message)


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        result = db.delete_word(message.chat.id, data['target_word'], data['translate_word'])  # удалить из БД

        if result:
            greeting = f'Удалено слово: \n 👉 {data['translate_word']} - {data['target_word']} 👈'

        else:
            greeting = f'Слово уже удалено: \n 👉 {data['translate_word']} - {data['target_word']} 👈'
        bot.send_message(message.chat.id, greeting)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word_info(message):

    greeting = (f'Добавить слово можно по форме ниже: \n'
                f'👉 Add слово - перевод\n'
                f'⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇\n'
                f'Например: Add машина - car')
    bot.send_message(message.chat.id, greeting)


@bot.message_handler(func=lambda message: message.text.lower().startswith('add'))
def add_word(message):

    wt = message.text.lower().replace('add', '').replace(' ', '').split('-')
    result = db.add_word(message.chat.id, wt[0], wt[1])

    if result:
        bot.send_message(message.chat.id, f'Добавлено слово: \n 👉 {wt[0]} - {wt[1]}  👌')

    else:
        bot.send_message(message.chat.id, f'Это слово уже добавлено: \n 👉 {wt[0]} - {wt[1]} 👊')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):

    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

        target_word = data['target_word']

        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            hint = show_hint(*hint_text)

        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово: \n 👉{data['translate_word']}")

    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)


if __name__ == '__main__':
    bot.polling()
