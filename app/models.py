import datetime
from sqlalchemy import Column, String, Date, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)  # vk id пользователя
    messages = relationship('Messages', back_populates='user')

    def __repr__(self):
        return f"User: {self.user_id}"


class Chats(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)  # id чата

    def __repr__(self):
        return f"Chat: {self.chat_id}"
    messages = relationship('Messages', back_populates='chat')


class Messages(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, unique=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(Date, default=datetime.datetime.now())
    text = Column(String(4096))
    photo = Column(Integer)  # кол-во фотографий
    audio = Column(Integer)  # кол-во аудиозаписей
    video = Column(Integer)  # кол-во видео
    doc = Column(Integer)  # кол-во докумнтов
    audio_msg = Column(Boolean)  # кол-во аудиосообщений
    sticker = Column(Boolean)  # кол-во стикеров
    user = relationship('Users', back_populates='messages')
    chat = relationship('Chats', back_populates='messages')

    def __repr__(self):
        return f"Message {self.message_id}: {self.text}"
