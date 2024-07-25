import os
import sqlalchemy
import sqlalchemy as sq
from dotenv import load_dotenv, dotenv_values
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

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

Base = declarative_base()


class Users(Base):

    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    chat_id = sq.Column(sq.BigInteger, unique=True, nullable=False)


class RussianWords(Base):

    __tablename__ = 'russian_words'

    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=50), unique=True, nullable=False)


class EnglishWords(Base):

    __tablename__ = 'english_words'

    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=50), unique=True, nullable=False)


class TranslationWords(Base):

    __tablename__ = 'translation_words'

    id = sq.Column(sq.Integer, primary_key=True)
    english_words_id = sq.Column(sq.Integer, sq.ForeignKey('english_words.id'), nullable=False)
    russian_words_id = sq.Column(sq.Integer, sq.ForeignKey('russian_words.id'), nullable=False)

    en = relationship('EnglishWords', backref='translation_words')
    ru = relationship('RussianWords', backref='translation_words')


class UserLibrary(Base):

    __tablename__ = 'user_library'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'), nullable=False)
    translation_words_id = sq.Column(sq.Integer, sq.ForeignKey('translation_words.id'), nullable=False)


def create_db():

    create_table(engine)

    # Insert initial data
    en_words = ['All', 'How', 'Boy', 'People', 'Air', 'City', 'Room', 'Bad', 'Close', 'Run']
    for word in en_words:
        session.add(EnglishWords(word=word))

    ru_words = ['Все', 'Как', 'Мальчик', 'Люди', 'Воздух', 'Город', 'Комната', 'Плохо', 'Закрытый', 'Бежать']
    for word in ru_words:
        session.add(RussianWords(word=word))

    for idx in range(1, 11):
        session.add(TranslationWords(english_words_id=idx, russian_words_id=idx))

    session.commit()


def create_table(engine):

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':

    create_db()
    session.close()
