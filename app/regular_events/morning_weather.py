import sys
sys.path.append("/home/me/bots/erjan")

import vk_api

import app.config as config
from app.modules.weather import for_day_weather

vk_session = vk_api.VkApi(token=config.TOKEN)  # Передаем токен сообщества


def send_msg(vk_id, text):
    return vk_session.method("messages.send",
                             {'chat_id': vk_id,
                              'message': text,
                              "random_id": 0})


def send_weather():
    send_msg(7, for_day_weather())


if __name__ == "__main__":
    send_weather()
