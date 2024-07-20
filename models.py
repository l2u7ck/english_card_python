import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True)
    telegram_id = sq.Column(sq.Integer, unique=True, nullable=False)


user_library = sq.Table('user_library', Base.metadata,
                        sq.Column('user_id', sq.Integer(), sq.ForeignKey("users.id")),
                        sq.Column('russian_words_id', sq.Integer(), sq.ForeignKey("russian_words.id"))
                        )


class RussianWords(Base):
    __tablename__ = "russian_words"

    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=50), unique=True, nullable=False)
    english_words_id = sq.Column(sq.Integer, sq.ForeignKey("english_words.id"), nullable=False, unique=True)

class EnglishWords(Base):
    __tablename__ = "english_words"

    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=50), unique=True, nullable=False)

    english = relationship('RussianWords', backref='english', uselist=False)


def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
