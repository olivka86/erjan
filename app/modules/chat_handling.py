import random
import re
import requests
import datetime as dt
from time import sleep
from random import randrange
from bs4 import BeautifulSoup
import json
from pathlib import Path

import vk_api

from app.modules.weather import current_weather, time_of_sunrise, time_of_sunset
# from gif_maker import create_gif, shakalize
import app.modules.msg_stat as msg_stat

import app.config as config

SEASON = dt.datetime(2024, 7, 10)
ZHD = dt.datetime(2024, 5, 17)

with open(Path(__file__).parent.parent.joinpath('data.json'), encoding='UTF-8') as f:
    data = json.load(f)
    NUMBER_BASE = data['number_base']
    del data

vk_session = vk_api.VkApi(token=config.TOKEN)
vk = vk_session.get_api()


def send_msg(vk_id, text='', attachment='', disable_mentions=True):
    sleep(0.5)
    return vk_session.method("messages.send",
                             {'chat_id': vk_id,
                              'message': text,
                              'attachment': attachment,
                              'random_id': 0,
                              'disable_mentions': int(disable_mentions)})


def send_photo(vk_id, attachment):
    """отправляем фото в чат"""
    sleep(0.3)
    return vk_session.method("messages.send",
                             {'chat_id': vk_id,
                              'attachment': attachment,
                              "random_id": 0})


def end_of_days_wrapper(date):
    def decorator(func):
        def wrapper(vk_id):
            now = dt.datetime.now()
            days_left = (date - now).days
            if days_left < 0:
                days_left = abs(days_left) - 1
            if days_left % 10 == 1:
                sentence_end = 'день'
            elif days_left % 10 in (2, 3, 4):
                sentence_end = 'дня'
            else:
                sentence_end = 'дней'
            return func(vk_id, days_left, sentence_end=sentence_end)

        return wrapper

    return decorator


@end_of_days_wrapper(SEASON)
def season_left_days(vk_id, days_left, sentence_end):
    """отправляет кол-во дней до сезона"""
    send_msg(vk_id, f"До сезона осталось {days_left} {sentence_end}", attachment='photo-202528897_457239248')


@end_of_days_wrapper(ZHD)
def zhd_left_days(vk_id, days_left, sentence_end):
    """отправляет фото ержана с пивом и кол-во дней до зхд"""

    # pictures_zhd = ['photo-202528897_457239152', 'photo-202528897_457239154',
    #             'photo-202528897_457239153', 'photo-202528897_457239157',
    #             'photo-202528897_457239155', 'photo-202528897_457239156']

    send_msg(vk_id, f"До заходского осталось {days_left} {sentence_end}", attachment='photo-202528897_457239087')


def send_photo_from_folder(vk_id, path):
    """Загрузка фотографий на vk.UploadServer с сервера и дальнейшая
    отправка в личные сообщения или чат"""
    server = vk.photos.getMessagesUploadServer()

    photo = requests.post(server['upload_url'], files={'photo': open(path, 'rb')}).json()
    save_photo = vk.photos.saveMessagesPhoto(photo=photo['photo'], server=photo['server'], hash=photo['hash'])[0]
    upload_ph = "photo{}_{}".format(save_photo['owner_id'], save_photo['vk_id'])
    vk_session.method('messages.send', {'chat_id': vk_id, 'message': ' ', 'attachment': upload_ph, 'random_id': 0})


def send_doc(path, vk_id):
    """отправляем любые доки"""
    # vk - <class 'vk_api.vk_api.VkApiMethod'>
    doc = vk_api.upload.VkUpload(vk).document_message(open(path, 'rb'), peer_id=2_000_000_000 + vk_id)
    upload_doc = 'doc{}_{}'.format(doc['doc']['owner_id'], doc['doc']['vk_id'])
    vk_session.method('messages.send', {'chat_id': vk_id, 'message': ' ', 'attachment': upload_doc, 'random_id': 0})


def download_photo(message):
    """Скачивает все изображения из сообщения"""
    amount_of_photos = len(message['attachments'])
    for i in range(amount_of_photos):
        m = []
        resolutions = message['attachments'][i]['photo']['sizes']
        for link in resolutions:
            m.append(link['height'])

        max_resolution = m.index(max(m))
        url = message['attachments'][i]['photo']['sizes'][max_resolution]['url']

        r = requests.get(url)

        with open('photo/{}.jpg'.format(i), 'wb') as ph:
            ph.write(r.content)

    return amount_of_photos


def send_gif(vk_id, message):
    """отправляет гифку, хранящуюся внутри директориии photo"""
    amount_of_photos = download_photo(message)
    photos = []
    for i in range(amount_of_photos):
        photos.append('photo/{}.jpg'.format(i))
    print(amount_of_photos)
    create_gif(photos)
    send_doc(vk_id, 'photo/erj.gif')


def send_shakal(vk_id, message):
    """Отправляет просто сжатую картинку пользователю"""
    resolutions = message['attachments'][0]['photo']['sizes']
    m = []
    for link in resolutions:
        m.append(link['height'])

    max_resolution = m.index(max(m))
    url = message['attachments'][0]['photo']['sizes'][max_resolution]['url']

    r = requests.get(url)

    with open('photo/shakal/pic.jpg', 'wb') as ph:
        ph.write(r.content)

    shakalize('photo/shakal/pic.jpg')
    send_photo_from_folder(vk_id, 'photo/shakal/shakal.jpg')


def send_joke(vk_id):
    month = random.randint(1, 12)
    year = random.randint(2005, 2023)
    url = f'https://башорг.рф/best/{year}/{month}'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    jokes = soup.findAll('div', class_='quote__body')
    b_joke = repr(jokes[0]).replace('<br/>', '\n')
    print(b_joke)
    first_line = b_joke.find('\n') + 7
    last_line = b_joke.find('          </div>') - 1

    send_msg(vk_id, text=b_joke[first_line:last_line])


def send_ultrashakal(vk_id, message):
    """Отправляет ультра сжатую картинку пользователю"""
    resolutions = message['attachments'][0]['photo']['sizes']
    m = []
    for link in resolutions:
        m.append(link['height'])

    max_resolution = m.index(max(m))
    url = message['attachments'][0]['photo']['sizes'][max_resolution]['url']

    r = requests.get(url)

    with open('photo/shakal/pic.jpg', 'wb') as ph:
        ph.write(r.content)

    shakalize('photo/shakal/pic.jpg', quality=1)
    send_photo_from_folder(vk_id, 'photo/shakal/shakal.jpg')


def get_username(user_id):
    user_get = vk.users.get(user_ids=user_id)
    print(user_id, user_get)
    user_text = user_get[0]
    fullname = user_text['first_name'] + ' ' + user_text['last_name']
    return fullname


def register_msg(message, chat_id):
    def check_media(event):
        attachments = event['attachments']
        photo, video, audio, doc = 0, 0, 0, 0
        audio_msg, sticker = False, False
        for attach in attachments:
            if attach['type'] == 'photo':
                photo += 1
            elif attach['type'] == 'video':
                video += 1
            elif attach['type'] == 'doc':
                doc += 1
            elif attach['type'] == 'audio':
                audio += 1
            elif attach['type'] == 'audio_message':
                audio_msg = True
            elif attach['type'] == 'sticker':
                sticker = True
        return {
            'photo': photo,
            'video': video,
            'doc': doc,
            'audio': audio,
            'audio_msg': audio_msg,
            'sticker': sticker
        }

    media = check_media(message)
    user_id = message['from_id']
    message_id = message['conversation_message_id']
    text = message['text']
    photo_stat = media['photo']
    audio_stat = media['audio']
    audio_msg_stat = media['audio_msg']
    video_stat = media['video']
    doc_stat = media['doc']
    sticker_stat = media['sticker']

    msg_stat.insert_msg(chat_id, user_id, message_id, photo_stat, audio_stat, text,
                        audio_msg_stat, video_stat, doc_stat, sticker_stat)


# патерны для поиск в сообщение шаблонов
patterns = {
    'pattern_phone': r'(?i).*(ержан|джа)?.*(какой|киньт?е?)?.*номер.у?.?\[\w\w(\d+)|.+',
    'pattern_days_left_to_season': r'(?i).*(ержан|джа)?.*сколько.+(дней)?.*до.+сезона.*\??',
    'pattern_days_left_to_zhd': r'(?i).*(ержан|джа)?.*сколько.+(дней)?.*(до)?.*(зхд|заходское|заходского).*\??',
    'pattern_erjan': r'(?i).*ержан.*\?$',
    'pattern_understand': r'(?i).*не понял\.?$',
    'pattern_hui': r'(?i).*иди нахуй$',
    'pattern_how_many': r'(?i).* сколько.*',
    'pattern_go': r'(?i).*ержан.* (го|погнали|пойдем|пошли).*',
    'pattern_rso': r'(?i).*труд.*',
    'pattern_weather': r'(?i).*ержан.*погода.*',
    'pattern_veseloe': r'(?i).*(веселое|весёлое).*',
    'pattern_sber': r'(?i).*(карт).*(сбер).*',
    ################################################
    'pattern_5': r'(?i).*(карт).*(пятероч).*',
    'pattern_lenta': r'(?i).*(карт).*(ленты|лента).*',
    'pattern_perek': r'(?i).*(карт).*(перек|перекрест).*',
    'pattern_magnit': r'(?i).*(карт).*(магнит).*',
    'pattern_okey': r'(?i).*(карт).*(оке).*',
    'pattern_prisma': r'(?i).*(карт).*(призм).*',
    'pattern_sportmaster': r'(?i).*(карт).*(спортмастер).*',
    'pattern_trial_sport': r'(?i).*(карт).*(триал спорт).*',
    'pattern_maksidom': r'(?i).*(карт).*(максидом).*',
    'pattern_diksi': r'(?i).*(карт).*(дикси).*',
    'pattern_spar': r'(?i).*(карт).*(спар).*',
    'pattern_auchan': r'(?i).*(карт).*(ашан).*',
    'pattern_letual': r'(?i).*(карт).*(летуал).*',
    'pattern_fix_price': r'(?i).*(карт).*(фикс прайс).*',
    'pattern_riv_gosh': r'(?i).*(карт).*(рив гош).*',
    'pattern_pink_rabbit': r'(?i).*(карт).*(розового кролика).*',
    'pattern_hmel_solod': r'(?i).*(карт).*(хмель и солод).*',
}

loyality_cards = {
    '5': ['photo-202528897_457239258'],
    'lenta': ['photo-202528897_457239249'],
    'perek': ['photo-202528897_457239254'],
    'magnit': ['photo-202528897_457239257'],
    'okey': ['photo-202528897_457239256'],
    'prisma': ['photo-202528897_457239174'],
    'sportmaster': ['photo-202528897_457239176'],
    'trial_sport': ['photo-202528897_457239177'],
    'maksidom': ['photo-202528897_457239194'],
    'diksi': ['photo-202528897_457239255'],
    'spar': ['photo-202528897_457239198'],
    'auchan': ['photo-202528897_457239200'],
    'letual': ['photo-202528897_457239201'],
    'fix_price': ['photo-202528897_457239202'],
    'riv_gosh': ['photo-202528897_457239204'],
    'pink_rabbit': ['photo-202528897_457239207'],
    'hmel_solod': ['photo-202528897_457239206'],
}


def proceed_from_group_message(message: dict):
    pass


def proceed_from_user_message(message: dict):
    send_msg(message['peer_id'], message['text'])


def proceed_from_chat_message(message: dict):
    number = randrange(1, 1000)
    chat_id = int(message['peer_id']) - 2_000_000_000
    user_id = message['from_id']
    msg = message['text']

    msg_stat.check_chat_exist(chat_id)
    msg_stat.check_user_exist(user_id)
    register_msg(message, chat_id)  # registr message in postgresDB

    if re.match(patterns['pattern_go'], msg):  # ержана зовут бухать
        if number < 300:
            send_msg(chat_id, 'выезжаю')
        elif number < 600:
            send_msg(chat_id, 'без деда никуда не пойду')
        elif number < 900:
            send_msg(chat_id, 'погнали')
        elif number > 900:
            send_msg(chat_id, 'с дедом хоть на край света')

    elif msg == '!стата':
        ans = msg_stat.get_user_statistic(chat_id, user_id)
        send_msg(chat_id, ans)

    elif msg == '!статистика':
        ans = msg_stat.get_chat_statistic(chat_id, get_username)
        send_msg(chat_id, ans)

    elif msg == '!статистика неделя':
        ans = msg_stat.get_chat_statistic_week(chat_id, get_username)
        send_msg(chat_id, ans)

    elif (msg == '!погода') or re.match(patterns['pattern_weather'], msg):  # погода
        send_msg(chat_id, current_weather())

    # сколько дней до зхд
    elif (msg == '!зхд') or re.match(patterns['pattern_days_left_to_zhd'], msg) and chat_id != 8:
        zhd_left_days(chat_id)

    # ищет вопрос сколько
    elif re.match(patterns['pattern_how_many'], msg):
        if number > 800:
            send_msg(chat_id, 'дохуя')
        else:
            send_msg(chat_id, str(round(number / 10)))

    # проверка бота работоспособность
    elif msg == 'Ержан, работаешь?':
        send_photo(chat_id, 'photo-202528897_457239027')

    elif msg == 'Ержан, который час?':
        send_msg(chat_id, 'время пива!')

    elif msg == 'Ержан, давно работаешь?' or msg == '!работа':
        how_much_erjan_working(chat_id)

    # поиск запроса на выдачу номера телефона
    # elif re.match(patterns['pattern_phone'], msg).group(3):
    #
    #     user_id_phone = (re.match(patterns['pattern_phone'], msg).group(3))
    #     send_msg(chat_id,
    #              f"Номер *id{user_id_phone}({NUMBER_BASE[user_id_phone][1]}):"
    #              f" {NUMBER_BASE[user_id_phone][0]}")

    elif msg == '!сбер' or re.match(patterns['pattern_sber'], msg):
        ans = f'Да, жду бананы\n\n{config.SBER_CARD_NUMBER}\n{config.SBER_PHONE_NUMBER}'
        send_msg(chat_id, ans)

    elif msg == '!анек':
        send_joke(chat_id)

    # loyalty cards block
    elif msg == '!пятерочка' or msg == '!пятёрочка' or msg == '!5' \
            or re.match(patterns['pattern_5'], msg):
        attachment = random.choice(loyality_cards['5'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!перекресток' or msg == '!перек' or re.match(patterns['pattern_perek'], msg):
        attachment = random.choice(loyality_cards['perek'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!лента' or re.match(patterns['pattern_lenta'], msg):
        attachment = random.choice(loyality_cards['lenta'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!магнит' or re.match(patterns['pattern_magnit'], msg):
        attachment = random.choice(loyality_cards['magnit'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!призма' or re.match(patterns['pattern_prisma'], msg):
        attachment = random.choice(loyality_cards['prisma'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!окей' or re.match(patterns['pattern_okey'], msg):
        attachment = random.choice(loyality_cards['okey'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!триал спорт' or re.match(patterns['pattern_trial_sport'], msg):
        attachment = random.choice(loyality_cards['trial_sport'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!максидом' or re.match(patterns['pattern_maksidom'], msg):
        attachment = random.choice(loyality_cards['maksidom'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!дикси' or re.match(patterns['pattern_diksi'], msg):
        attachment = random.choice(loyality_cards['diksi'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!спортмастер' or re.match(patterns['pattern_sportmaster'], msg):
        attachment = random.choice(loyality_cards['sportmaster'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!спар' or re.match(patterns['pattern_spar'], msg):
        attachment = random.choice(loyality_cards['spar'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!ашан' or re.match(patterns['pattern_auchan'], msg):
        attachment = random.choice(loyality_cards['auchan'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!фикс прайс' or msg == '!фикспрайс' or re.match(patterns['pattern_sportmaster'], msg):
        attachment = random.choice(loyality_cards['fix_price'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!летуаль' or re.match(patterns['pattern_letual'], msg):
        attachment = random.choice(loyality_cards['letual'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!ривгош' or re.match(patterns['pattern_riv_gosh'], msg):
        attachment = random.choice(loyality_cards['riv_gosh'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!розовый кролик' or msg == '!рк' or re.match(patterns['pattern_pink_rabbit'], msg):
        attachment = random.choice(loyality_cards['pink_rabbit'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)
    elif msg == '!хмель и солод' or msg == '!хc' or re.match(patterns['pattern_hmel_solod'], msg):
        attachment = random.choice(loyality_cards['hmel_solod'])
        send_msg(chat_id, text='держи, брат', attachment=attachment)

    ##############################################################################

    elif msg in ('!help', '!хелп', '!памагите') or re.match(r'(?i).*(ержан).*([че|что] умеешь).*', msg):
        cards = '\n'.join(loyality_cards)

        to_return = ('Список команд:\n'
                     '!погода\n'
                     '!рассвет\n'
                     '!закат\n'
                     '!время – текущее время\n'
                     '!анек – рассказываю худшие анеки рунета\n'
                     '!сезон – осталось дней до сезона\n'
                     '!работа – прошло времени с последнего запуска ержана на сервере\n\n'
                     'А также:\n'
                     '· Подскажу номер братка(есть только бойцы Джа)\n'
                     '· Гений математики, способный высчитать что угодно. Cпроси сколько...\n'
                     '· Отвечаю на любые вопросы, заданные мне\n'
                     '· Выезжаю на разборки\n\n'
                     'Список магазинов в базе:\n'
                     f'{cards}')

        send_msg(chat_id, to_return)

    elif re.match(patterns['pattern_erjan'], msg):  # ищет вопрос ержану
        if number < 351:
            send_msg(chat_id, 'да')
        if 350 < number < 701:
            send_msg(chat_id, 'нет')
        if 700 < number < 751:
            send_msg(chat_id, 'мне поебать')
        if 750 < number < 801:
            send_msg(chat_id, 'суета')
        if 800 < number < 821:
            send_msg(chat_id, 'один раз не пидорас')
        if 820 < number < 851:
            send_msg(chat_id, 'узнаешь')
        if 850 < number < 856:
            send_msg(chat_id, 'я больше не работаю')
        if 855 < number < 866:
            send_msg(chat_id, 'Я, блять, в своём познании настолько преисполнился, \
                что я как будто бы уже 100 триллионов миллиардов лет, блять,\
                проживаю на триллионах и триллионах таких же планет, понимаешь?\
                Как эта Земля. Мне уже этот мир абсолютно понятен, и я здесь ищу\
                только одного: покоя, умиротворения и вот этой гармонии от слияния \
                с бесконечно вечным.')
        if 865 < number < 876:
            send_msg(chat_id, 'Как вам сказать… \
                Я прожила довольно долгую жизнь… \
                Ибрагим вам что-нибудь говорит?\
                Прекрасное имя. Аллах акбар. \
                Я прошла афганскую войну. И я желаю всем мужчинам пройти ее.\
                Мужчина определяется делом, а не словом.\
                И если я ношу кандибобер на голове, это не значит,\
                что я женщина или балерина')
        if 875 < number < 901:
            send_msg(chat_id, 'отвечаю')
        if 900 < number < 916:
            send_msg(chat_id, 'Ахахах, насмешил. Гуляй')
        if 915 < number < 941:
            send_msg(chat_id, 'по-любому, езжи')
        if 940 < number < 955:
            send_msg(chat_id, 'встану - ты ляжешь')

    elif re.match(patterns['pattern_days_left_to_season'], msg) or msg == '!сезон':
        season_left_days(chat_id)

    elif re.match(patterns['pattern_understand'], msg) and number < 300:  # не понял
        send_msg(chat_id, 'поймешь')

    elif re.match(patterns['pattern_hui'], msg):  # ержана послали нахуй?
        send_msg(chat_id, 'Сам нахуй иди')

    elif re.match(patterns['pattern_rso'], msg):  # любим рсо
        send_msg(chat_id, 'Я люблю РСО 🏳️‍🌈 🏳️‍🌈 🏳️‍🌈')

    elif re.match(patterns['pattern_veseloe'], msg):  # Веселое? нет блин грустное
        send_msg(chat_id, 'Нет блин грустное')

    elif (msg == 'Да' or msg == 'да' or msg == 'ДА') and number < 150:
        send_msg(chat_id, 'Манда')

    elif (msg == 'Нет' or msg == 'нет' or msg == 'НЕТ') and number < 150:
        send_msg(chat_id, 'Пидора ответ')

    # elif msg == 'Ержан, сделай гифку':
    #     send_gif(chat_id, message)

    # elif msg == 'Ержан, шакализируй' or msg == 'Ержан, шакал':
    #     send_shakal(chat_id, message)

    # elif msg == 'Ержан, ультрашакал':
    #     send_ultrashakal(chat_id, message)

    elif msg == 'Ержан, пиши диплом':
        send_photo(chat_id, 'photo-202528897_457239141')

    elif msg == '!восход' or msg == '!рассвет':
        send_msg(chat_id, time_of_sunrise())

    elif msg == '!заход' or msg == '!закат':
        send_msg(chat_id, time_of_sunset())

    elif msg == '!время':
        if user_id == 174135331 and number <= 50:
            send_msg(chat_id, 'Время учить уроки, Софа!')
        else:
            current_time = dt.datetime.now()
            current_time = current_time.strftime('%H:%M')
            send_msg(chat_id, current_time)

    elif msg == 'один раз':  # no comments
        send_msg(chat_id, 'не пидорас')


if __name__ == '__main__':
    from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
    from app.config import GROUPID, TOKEN

    vk_session = vk_api.VkApi(token=TOKEN)  # Передаем токен сообщества
    vk = vk_session.get_api()
    def longpoll():
        _longpoll = VkBotLongPoll(vk_session, GROUPID)
        try:
            return _longpoll
        except vk_api.exceptions.ApiError:
            pass


    for event in longpoll().listen():
        print('START')
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:

            proceed_from_chat_message(event.message)
            print(event.message['text'])
