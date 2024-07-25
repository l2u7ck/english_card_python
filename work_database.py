import random
from string import capwords

import models as m
from models import session


# Adding a new user
def new_user_db(chat_id):

    session.add(m.Users(chat_id=chat_id))
    session.commit()

    user_id = session.query(m.Users).filter(m.Users.chat_id == chat_id).first().id

    for index in range(1, 11):
        session.add(m.UserLibrary(user_id=user_id, translation_words_id=index))

    session.commit()


# Checking if a user exists in the database
def search_user(chat_id):

    q = session.query(m.Users).filter(m.Users.chat_id == chat_id).first()
    if q is None:
        return True
    else:
        return False


# Randomly picks up four words and translates one
def words(chat_id):

    all_words = (session.query(m.RussianWords, m.EnglishWords).
                 select_from(m.TranslationWords).
                 join(m.EnglishWords).
                 join(m.RussianWords).
                 join(m.UserLibrary).
                 join(m.Users).filter(m.Users.chat_id == chat_id).all())

    if len(all_words) > 6:
        val = list()
        rand_words = list()

        rand = random.randint(0, len(all_words)-1)
        val.append(rand)
        wt = all_words[val[0]]

        while len(val) < 4:
            rand = random.randint(0, len(all_words) - 1)

            if rand not in val:
                if all_words[rand][0].id != wt[0].id:

                    rand_words.append(all_words[rand][1].word)
                    val.append(rand)

        return [wt[0].word, wt[1].word]+rand_words

    else:
        return []


# Deleting a word from a user
def delete_word(chat_id, en, ru):

    print(chat_id, en, ru)
    index = (session.query(m.UserLibrary.id).
             select_from(m.UserLibrary).
             join(m.TranslationWords).
             join(m.Users).
             join(m.EnglishWords).
             join(m.RussianWords).
             filter(m.EnglishWords.word == en, m.RussianWords.word == ru, m.Users.chat_id == chat_id)).first()

    if index is None:
        return False

    else:
        session.query(m.UserLibrary).filter(m.UserLibrary.id == index[0]).delete()
        session.commit()
        return True


# Adding a word to the database and to the user
def add_word(chat_id, ru, en):

    en = capwords(en.lower())
    ru = capwords(ru.lower())

    en_id = session.query(m.EnglishWords.id).filter(m.EnglishWords.word == en).first()
    ru_id = session.query(m.RussianWords.id).filter(m.RussianWords.word == ru).first()

    if en_id is None:
        session.add(m.EnglishWords(word=en))
        session.commit()
        en_id = session.query(m.EnglishWords.id).filter(m.EnglishWords.word == en).first()

    if ru_id is None:
        session.add(m.RussianWords(word=ru))
        session.commit()
        ru_id = session.query(m.RussianWords.id).filter(m.RussianWords.word == ru).first()

    wt = (session.query(m.TranslationWords.id).
          filter(m.TranslationWords.english_words_id == en_id[0],
                 m.TranslationWords.russian_words_id == ru_id[0]).first())

    if wt is None:
        session.add(m.TranslationWords(english_words_id=en_id[0], russian_words_id=ru_id[0]))
        session.commit()
        wt = (session.query(m.TranslationWords.id).
              filter(m.TranslationWords.english_words_id == en_id[0],
                     m.TranslationWords.russian_words_id == ru_id[0]).first())

    user_id = session.query(m.Users.id).filter(m.Users.chat_id == chat_id).first()[0]

    user_word = (session.query(m.UserLibrary).
                 filter(m.UserLibrary.user_id == user_id,
                        m.UserLibrary.translation_words_id == wt[0]).first())

    if user_word is None:
        session.add(m.UserLibrary(user_id=user_id, translation_words_id=wt[0]))
        session.commit()
        return True

    return False
