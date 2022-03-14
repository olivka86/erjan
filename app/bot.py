from flask import Flask, request

from app.modules.chat_handling import proceed_from_group_message, proceed_from_chat_message, proceed_from_user_message
import app.config as config


CHAT_START_ID = int(2E9)

app = Flask(__name__)


@app.route('/e7c5b738db88d164f7e707c5ef85431b', methods=['POST'])
def bot():
    # получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    # ВКонтакте в своих запросах всегда отправляет поле type:
    if not data or 'type' not in data:
        return 'not ok'

    if data['type'] == 'confirmation':
        # если это запрос защитного кода
        # отправляем его
        return config.CONFIRMATION_CODE

    elif data['type'] == 'message_new':
        peer_id = data['object']['peer_id']

        print(peer_id)
        if peer_id < 0:
            proceed_from_group_message(message=data['object']['message'])
        elif peer_id < CHAT_START_ID:
            proceed_from_user_message(message=data['object']['message'])
        else:
            proceed_from_chat_message(message=data['object']['message'])

        return 'ok'

    return 'ok'  # игнорируем другие типы

