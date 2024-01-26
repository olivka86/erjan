from sqlalchemy import create_engine, func, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

import app.config as config
from app.models import Messages, Chats, Users

engine = create_engine(f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}'
                       f'@{config.POSTGRES_IP}:5432/{config.POSTGRES_DB}')
Base = declarative_base()
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


def check_user_exist(user_id):
    with Session() as session:
        with session.begin():
            user_in_db = session.query(Users).filter_by(user_id=user_id).first()
            if not user_in_db:
                user = Users(
                    user_id=user_id
                )
                session.add(user)


def check_chat_exist(chat_id):
    with Session() as session:
        with session.begin():
            chat_in_db = session.query(Chats).filter_by(chat_id=chat_id).first()
            if not chat_in_db:
                chat = Chats(
                    chat_id=chat_id
                )
                session.add(chat)


def insert_msg(chat_id, user_id, message_id, photo_stat, audio_stat, text,
               audio_msg_stat, video_stat, doc_stat, sticker_stat):

    message = Messages(
        message_id=message_id,
        chat_id=chat_id,
        user_id=user_id,
        text=text,
        photo=photo_stat,
        audio=audio_stat,
        video=video_stat,
        doc=doc_stat,
        audio_msg=audio_msg_stat,
        sticker=sticker_stat,
    )

    with Session() as session:
        with session.begin():
            session.add(message)


def get_chat_statistic(chat_id, get_username):
    with Session() as session:
        with session.begin():
            query = session.query(
                func.count().label('total_messages'),
                func.sum(case([(Messages.photo > 0, 1)], else_=0)).label('total_photo'),
                func.sum(case([(Messages.audio > 0, 1)], else_=0)).label('total_audio'),
                func.sum(case([(Messages.video > 0, 1)], else_=0)).label('total_video'),
                func.sum(case([(Messages.doc > 0, 1)], else_=0)).label('total_doc'),
                func.sum(case([(Messages.audio_msg.is_(True), 1)], else_=0)).label('total_audio_msg'),
                func.sum(case([(Messages.sticker.is_(True), 1)], else_=0)).label('total_sticker'),
            ).filter(Messages.chat_id == chat_id).first()

            # Получаем список из пяти самых активных пользователей
            users_count = (
                session.query(Messages.user_id, func.count(Messages.id).label('user_count'))
                .filter_by(chat_id=chat_id)
                .group_by(Messages.user_id)
                .order_by(func.count(Messages.id).desc())
                .limit(5)
                .all()
            )

    # return to_string(messages, photo, audio, video, doc, audio_msg, sticker, users_count)
    return to_string(query, users_count, get_username)


def to_string(query, top_5, get_username):
    result = f"Статистика за весь период\n\n" \
             f"📧 Сообщений: {query.total_messages}\n" \
             f"🎵 Голосовых: {query.total_audio_msg}\n" \
             f"📷 Фото: {query.total_photo}\n" \
             f"🎧 Аудио: {query.total_audio}\n" \
             f"📹 Видео: {query.total_video}\n" \
             f"📑 Документов: {query.total_doc}\n" \
             f"🐱 Стикеров: {query.total_sticker}\n\n" \
             f"Самые активные пользователи:\n"
    for i, user in enumerate(top_5):
        if user.user_id > 0:
            username = get_username(user.user_id)
            result += f"{i + 1}. {username} – {user.user_count}\n"
        else:
            result += f"{i + 1}. {user.user_id} – {user.user_count}\n"
    return result


def get_user_statistic(chat_id, user_id):
    with Session() as session:
        query = session.query(
            func.count().label('total_messages'),
            func.sum(case([(Messages.photo > 0, 1)], else_=0)).label('total_photo'),
            func.sum(case([(Messages.audio > 0, 1)], else_=0)).label('total_audio'),
            func.sum(case([(Messages.video > 0, 1)], else_=0)).label('total_video'),
            func.sum(case([(Messages.doc > 0, 1)], else_=0)).label('total_doc'),
            func.sum(case([(Messages.audio_msg.is_(True), 1)], else_=0)).label('total_audio_msg'),
            func.sum(case([(Messages.sticker.is_(True), 1)], else_=0)).label('total_sticker'),
        ).filter(Messages.chat_id == chat_id, Messages.user_id == user_id).first()

        user_stat = ('Твоя статистика за весь период\n'
                     f'📧 Сообщений: {query.total_messages}\n'
                     f'🎵 Голосовых: {query.total_audio_msg}\n'
                     f'📷 Фото: {query.total_photo}\n'
                     f'🎧 Аудио: {query.total_audio}\n'
                     f'📹 Видео: {query.total_video}\n'
                     f'📑 Документов: {query.total_doc}\n'
                     f'🐱 Стикеров: {query.total_sticker}\n')

    return user_stat


def get_chat_statistic_week(chat_id, get_username):
    with Session() as session:
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        query = session.query(
            func.count().label('total_messages'),
            func.sum(case([(Messages.photo > 0, 1)], else_=0)).label('total_photo'),
            func.sum(case([(Messages.audio > 0, 1)], else_=0)).label('total_audio'),
            func.sum(case([(Messages.video > 0, 1)], else_=0)).label('total_video'),
            func.sum(case([(Messages.doc > 0, 1)], else_=0)).label('total_doc'),
            func.sum(case([(Messages.audio_msg.is_(True), 1)], else_=0)).label('total_audio_msg'),
            func.sum(case([(Messages.sticker.is_(True), 1)], else_=0)).label('total_sticker'),
        ).filter(Messages.chat_id == chat_id, Messages.created_at >= week_ago).first()


    # Получаем список из пяти самых активных пользователей
    users_count = (
        session.query(Messages.user_id, func.count(Messages.id).label('user_count'))
        .filter(Messages.chat_id == chat_id, Messages.created_at >= week_ago)
        .group_by(Messages.user_id)
        .order_by(func.count(Messages.id).desc())
        .limit(5)
        .all()
    )

    # return to_string(messages, photo, audio, video, doc, audio_msg, sticker, users_count)
    return to_string_week(query, users_count, get_username)


def to_string_week(query, top_5, get_username):
    result = f"Статистика за неделю\n\n" \
             f"📧 Сообщений: {query.total_messages}\n" \
             f"🎵 Голосовых: {query.total_audio_msg}\n" \
             f"📷 Фото: {query.total_photo}\n" \
             f"🎧 Аудио: {query.total_audio}\n" \
             f"📹 Видео: {query.total_video}\n" \
             f"📑 Документов: {query.total_doc}\n" \
             f"🐱 Стикеров: {query.total_sticker}\n\n" \
             f"Самые активные пользователи за неделю:\n"
    for i, user in enumerate(top_5):
        if user.user_id > 0:
            username = get_username(user.user_id)
            result += f"{i + 1}. {username} – {user.user_count}\n"
        else:
            result += f"{i + 1}. {user.user_id} – {user.user_count}\n"
    return result
