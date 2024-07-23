import sqlalchemy
import random
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from dotenv import dotenv_values
import models as m

# connecting environment variables (env)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(load_dotenv(dotenv_path))

# Database connection
DSN = (f'{dotenv_values()['CONNECTION_DRIVER']}://'
       f'{dotenv_values()['LOGIN']}:'
       f'{dotenv_values()['PASSWORD']}@'
       f'{dotenv_values()['HOST']}:'
       f'{dotenv_values()['PORT']}/'
       f'{dotenv_values()['TITLE_DB']}')

engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()


def create_db():

    m.create_table(engine)

    # Insert initial data
    en_words = ['All', 'How', 'Boy', 'People', 'Air', 'City', 'Room', 'Bad', 'Close', 'Run']
    for word in en_words:
        session.add(m.EnglishWords(word=word))

    ru_words = ['Все', 'Как', 'Мальчик', 'Люди', 'Воздух', 'Город', 'Комната', 'Плохо', 'Закрытый', 'Бежать']
    for word in ru_words:
        session.add(m.RussianWords(word=word))

    for idx in range(1, 11):
        session.add(m.TranslationWords(english_words_id=idx, russian_words_id=idx))

    session.commit()


def new_user_db(chat_id):

    session.add(m.Users(chat_id=chat_id))
    session.commit()

    user_id = session.query(m.Users).filter(m.Users.chat_id == chat_id).first().id

    for index in range(1, 11):
        session.add(m.UserLibrary(user_id=user_id, translation_words_id=index))

    session.commit()


def search_user(chat_id):

    q = session.query(m.Users).filter(m.Users.chat_id == chat_id).first()
    if q is None:
        return True
    else:
        return False


def words(chat_id):

    all_words = (session.query(m.RussianWords, m.EnglishWords).
                 select_from(m.TranslationWords).
                 join(m.EnglishWords).
                 join(m.RussianWords).
                 join(m.UserLibrary).
                 join(m.Users).filter(m.Users.chat_id == chat_id).all())

    val = list()

    while len(val) < 4:

        rand = random.randint(0, len(all_words)-1)
        if rand not in val:
            val.append(rand)

    wt = all_words[val[0]]

    rand_words = list()

    for numb in range(1, 4):
        rand_words.append(all_words[val[numb]][1].word)

    return [wt[0].word, wt[1].word]+rand_words


def delete_word(chat_id, en, ru):

    print(chat_id, en, ru)
    index = (session.query(m.UserLibrary.id).
         select_from(m.UserLibrary).
         join(m.TranslationWords).
         join(m.Users).
         join(m.EnglishWords).
         join(m.RussianWords).
         filter(m.EnglishWords.word == en, m.RussianWords.word == ru, m.Users.chat_id == chat_id)).first()

    session.query(m.UserLibrary).filter(m.UserLibrary.id == index[0]).delete()
    session.commit()


# def insert_db():
if __name__ == '__main__':

    create_db()
    session.close()
