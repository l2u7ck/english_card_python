import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

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


def create_table(engine):

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
