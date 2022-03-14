from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, Boolean, String, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

import app.config as config

engine = create_engine(f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}'
                       f'@{config.POSTGRES_IP}:5432/{config.POSTGRES_DB}')
Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)  # id чата
    member_id = Column(Integer)  # vk id пользователя
    member_name = Column(String)  # имя пользователя
    current_date = Column(Date, default=datetime.date.today())
    current_time = Column(Time(timezone=True), default=datetime.datetime.now().time().strftime('%H:%M:%S'))
    photo = Column(Integer)  # кол-во фотографий
    audio = Column(Integer)  # кол-во аудиозаписей
    video = Column(Integer)  # кол-во видео
    doc = Column(Integer)  # кол-во докумнтов
    audio_msg = Column(Boolean)  # кол-во аудиосообщений
    sticker = Column(Boolean)  # кол-во стикеров

    def __repr__(self):
        return f"Conversation {self.chat_name}: {self.chat_id}"


Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


# Create
def insert_msg(chat_id, member_id, member_name,
               photo_stat, audio_stat, audio_msg_stat, video_stat, doc_stat, sticker_stat):
    new_data = Conversation(
        chat_id=chat_id,
        member_id=member_id,
        member_name=member_name,
        photo=photo_stat,
        audio=audio_stat,
        audio_msg=audio_msg_stat,
        video=video_stat,
        doc=doc_stat,
        sticker=sticker_stat
    )

    with Session() as session:
        with session.begin():
            session.add(new_data)
            session.commit()


def check_registration(chat_id, user_id):
    with Session() as session:
        is_user_exist = session.query(Conversation).filter_by(chat_id=chat_id, member_id=user_id).all()
    if is_user_exist:
        return True
    return False


def find_top_5_users(chat_id):
    with Session() as session:
        with session.begin():
            top = session.query(Conversation.member_name, Conversation.member_id,
                                func.count().label('top')) \
                .filter_by(chat_id=chat_id).group_by(Conversation.member_name, Conversation.member_id) \
                .order_by(func.count().label('top').desc()).limit(5).all()
    return top


def find_top_5_users_week(chat_id, week_ago):
    with Session() as session:
        with session.begin():
            top = session.query(Conversation.member_name, Conversation.member_id,
                                func.count().label('top')) \
                .filter_by(chat_id=chat_id).filter(Conversation.current_date > week_ago) \
                .group_by(Conversation.member_name, Conversation.member_id) \
                .order_by(func.count().label('top').desc()).limit(5).all()
    return top


def get_chat_statistic(chat_id):
    with Session() as session:
        with session.begin():
            count_msg = session.query(Conversation).filter_by(chat_id=chat_id).count()
            photo = session.query(Conversation).filter_by(chat_id=chat_id).filter(Conversation.photo != 0).count()
            audio = session.query(Conversation).filter_by(chat_id=chat_id).filter(Conversation.audio != 0).count()
            video = session.query(Conversation).filter_by(chat_id=chat_id).filter(Conversation.video != 0).count()
            doc = session.query(Conversation).filter_by(chat_id=chat_id).filter(Conversation.doc != 0).count()
            audio_msg = session.query(Conversation).filter_by(chat_id=chat_id, audio_msg=True).count()
            sticker = session.query(Conversation).filter_by(chat_id=chat_id, sticker=True).count()

    chat_stat = (f'Статистика за весь период\n'
                 f'📧 Сообщений: {count_msg}\n'
                 f'🎵 Голосовых: {audio_msg}\n'
                 f'📷 Фото: {photo}\n'
                 f'🎧 Аудио: {audio}\n'
                 f'📹 Видео: {video}\n'
                 f'📑 Документов: {doc}\n'
                 f'🐱 Стикеров: {sticker}\n').format(count_msg=count_msg, audio_msg=audio_msg,
                                                     photo=photo, audio=audio, video=video,
                                                     doc=doc, sticker=sticker)

    text_top5 = 'Самые активные пользователи:\n'
    top5 = find_top_5_users(chat_id)
    for ind, user in enumerate(top5):
        text = f"{ind + 1}. {user[0]} – {user[2]}\n"
        text_top5 += text

    chat_stat += text_top5

    return chat_stat


def get_user_statistic(chat_id, member_id):
    with Session() as session:
        with session.begin():
            count_msg = session.query(Conversation).filter_by(chat_id=chat_id, member_id=member_id).count()
            photo = session.query(Conversation).filter_by(chat_id=chat_id, member_id=member_id) \
                .filter(Conversation.photo != 0).count()
            audio = session.query(Conversation).filter_by(chat_id=chat_id, member_id=member_id) \
                .filter(Conversation.audio != 0).count()
            video = session.query(Conversation).filter_by(chat_id=chat_id, member_id=member_id) \
                .filter(Conversation.video != 0).count()
            doc = session.query(Conversation).filter_by(chat_id=chat_id, member_id=member_id) \
                .filter(Conversation.doc != 0).count()
            audio_msg = session.query(Conversation).filter_by(chat_id=chat_id, member_id=member_id,
                                                              audio_msg=True).count()
            sticker = session.query(Conversation).filter_by(chat_id=chat_id, member_id=member_id, sticker=True).count()

    user_stat = ('Твоя статистика за весь период\n'
                 f'📧 Сообщений: {count_msg}\n'
                 f'🎵 Голосовых: {audio_msg}\n'
                 f'📷 Фото: {photo}\n'
                 f'🎧 Аудио: {audio}\n'
                 f'📹 Видео: {video}\n'
                 f'📑 Документов: {doc}\n'
                 f'🐱 Стикеров: {sticker}\n')

    return user_stat


def get_chat_statistic_week(chat_id):
    with Session() as session:
        with session.begin():
            now = datetime.datetime.now()
            week_ago = now - datetime.timedelta(days=7)
            count_msg = session.query(Conversation) \
                .filter_by(chat_id=chat_id).filter(Conversation.current_date > week_ago).count()
            photo = session.query(Conversation). \
                filter_by(chat_id=chat_id).filter(Conversation.photo != 0,
                                                  Conversation.current_date > week_ago).count()
            audio = session.query(Conversation) \
                .filter_by(chat_id=chat_id).filter(Conversation.audio != 0,
                                                   Conversation.current_date > week_ago).count()
            video = session.query(Conversation) \
                .filter_by(chat_id=chat_id).filter(Conversation.video != 0,
                                                   Conversation.current_date > week_ago).count()
            doc = session.query(Conversation) \
                .filter_by(chat_id=chat_id).filter(Conversation.doc != 0, Conversation.current_date > week_ago).count()
            audio_msg = session.query(Conversation) \
                .filter_by(chat_id=chat_id, audio_msg=True).filter(Conversation.current_date > week_ago).count()
            sticker = session.query(Conversation) \
                .filter_by(chat_id=chat_id, sticker=True).filter(Conversation.current_date > week_ago).count()

    chat_stat_week = (f'Статистика за неделю\n'
                      f'📧 Сообщений: {count_msg}\n'
                      f'🎵 Голосовых: {audio_msg}\n'
                      f'📷 Фото: {photo}\n'
                      f'🎧 Аудио: {audio}\n'
                      f'📹 Видео: {video}\n'
                      f'📑 Документов: {doc}\n'
                      f'🐱 Стикеров: {sticker}\n')

    text_top5 = 'Самые активные пользователи за неделю:\n'
    top5 = find_top_5_users_week(chat_id, week_ago)
    for ind, user in enumerate(top5):
        text = f"{ind + 1}. {user[0]} – {user[2]}\n"
        text_top5 += text

    chat_stat_week += text_top5

    return chat_stat_week


if __name__ == "__main__":
    print(get_chat_statistic_week(2))
