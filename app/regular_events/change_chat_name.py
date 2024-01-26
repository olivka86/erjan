import sys
sys.path.append("/home/me/bots/erjan")

import vk_api
import datetime as dt
import json
from pathlib import Path

import app.config as config

DEFAULT_CHAT_NAME = 'Джанго’22 ⛰🍇'
CHAT_ID = 7

vk_session = vk_api.VkApi(token=config.TOKEN)  # Передаем токен сообщества

with open(Path(__file__).parent.parent.joinpath('data.json'), 'r', encoding="utf8") as f:
    data = json.load(f)
    DATES_OF_BIRTH = data['dates_of_birth']
    del data


def change_chat_name(title, chat_id):
    return vk_session.method('messages.editChat',
                             {'chat_id': chat_id, 'title': title})


if __name__ == '__main__':
    today = dt.datetime.now().strftime("%d %m")
    current_title = vk_session.method("messages.getConversationsById",
                                      {'peer_ids': 2000000000 + CHAT_ID})['items'][0]['chat_settings']['title']

    if today in DATES_OF_BIRTH:
        change_chat_name(DATES_OF_BIRTH[today], CHAT_ID)
    elif current_title != DEFAULT_CHAT_NAME:
        change_chat_name(DEFAULT_CHAT_NAME, CHAT_ID)
