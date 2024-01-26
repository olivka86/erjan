"""create conversation table

Revision ID: 194f4a4e9b44
Revises: 16f0d7552f19
Create Date: 2023-12-13 19:23:26.993292

"""
from typing import Sequence, Union

from datetime import datetime
from sqlalchemy import Column, String, Date, Integer, Boolean, ForeignKey
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '194f4a4e9b44'
down_revision: Union[str, None] = '16f0d7552f19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
                    Column('id', Integer, primary_key=True),
                    Column('user_id', Integer, unique=True))  # vk id пользователя

    op.create_table('chats',
                    Column('id', Integer, primary_key=True),
                    Column('chat_id', Integer, unique=True))  # id чата

    op.create_table('messages',
                    Column('id', Integer, primary_key=True),
                    Column('message_id', Integer, unique=True),  # id чата
                    Column('chat_id', Integer, ForeignKey('chats.chat_id')),
                    Column('user_id', Integer, ForeignKey('users.user_id')),
                    Column('created_at', Date, default=datetime.now()),
                    Column('text', String(4096)),
                    Column('photo', Integer),  # кол-во фотографий
                    Column('audio', Integer),  # кол-во аудиозаписей
                    Column('video', Integer),  # кол-во видео
                    Column('doc', Integer),  # кол-во докумнтов
                    Column('audio_msg', Boolean),  # кол-во аудиосообщений
                    Column('sticker', Boolean))  # кол-во стикеров

    # Создаем внешние ключи
    op.create_foreign_key('fk_messages_user_id', 'messages', 'users', ['user_id'], ['user_id'])
    op.create_foreign_key('fk_messages_chat_id', 'messages', 'chats', ['chat_id'], ['chat_id'])

    # Создаем индексы для внешних ключей
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])
    op.create_index('idx_messages_chat_id', 'messages', ['chat_id'])


def downgrade() -> None:
    op.drop_index('idx_messages_chat_id', 'messages')
    op.drop_index('idx_messages_user_id', 'messages')
    op.drop_constraint('fk_messages_chat_id', 'messages', type_='foreignkey')
    op.drop_constraint('fk_messages_user_id', 'messages', type_='foreignkey')

    op.drop_table('messages')
    op.drop_table('chats')
    op.drop_table('users')
