import vk_api
import requests
from db import DB, Users
from vk_api import VkUpload
from random import randint
from vk_api.longpoll import VkLongPoll, VkEventType
import json
import os
import random
import youtube_dl
import datetime
import time

fin = open("Cookies.txt", "r", encoding="utf-8")
accounts = fin.readlines()  # блок получения лимита
limit = int(accounts[0][:1])
fin.close()

user_token = "88a036252b1e9df51aca4f3c27fc97b17b2fc3a3bf70cd7f1a23fada71690a610ab7210ca55edf6815005"
community_token = "519b455618498f3d0a1ed56407bc84fa7db6f3cb382ec19a734678a65861aa8afab2cc75a18e6cdefd093"

session = requests.Session()
vk_session = vk_api.VkApi(token=community_token)
upload = VkUpload(vk_session)

taboo = {"UC7f5bVxWsm3jlZIPDzOMcAg": "Я презираю автора этого канала, поэтому я не буду это загружать",
         "UCdKuE7a2QZeHPhDntXVZ91w": "Автор этого канала запретил загружать его ролики((",
         "UCdmauIL-k-djcct-yMrf82A": "Автор этого канала запретил загружать его ролики",
         "UCyxifPm6ErHW08oXMpzqATw": "Автор этого канала запретил загружать его ролики",
         "UCRpjHHu8ivVWs73uxHlWwFA": "Автор этого канала запретил загружать его ролики",
         "UCiV4ED9tyQUwsn27WTdVsPg": "Автор этого канала запретил загружать его ролики",
         "UCmM6pO5qYhhmYz-qq-fOTRw": "Автор этого канала запретил загружать его ролики",
         "UCOxeDBrR9XuZcI9NR9a8zfQ": "Автор этого канала запретил загружать его ролики",
         "UCHtvgXPPVX5X5BXP8cu7riQ": "Автор этого канала запретил загружать его ролики",
         "UCEnefm2JNYP3dhLULMWBOVA": "Автор этого канала запретил загружать его ролики",
         "UCpJ75-WA0P3EsEgGfhzkZrQ": "Автор этого канала запретил загружать его ролики",
         "UClZkHt2kNIgyrTTPnSQV3SA": "Автор этого канала запретил загружать его ролики",
         "UC3QnkztzojU232SysU-f-wA": "Автор этого канала запретил загружать его ролики",
         "UCRv76wLBC73jiP7LX4C3l8Q": "Автор этого канала запретил загружать его ролики",
         "UCWsJG8ibALRIB6OIon0yWhg": "Автор этого канала запретил загружать его ролики",
         "UCFTq_8SXc-SByisJqDZp9ZQ": "Автор этого канала запретил загружать его ролики",
         "UCsk9ntn2afzIqInnx2jB8gw": "Автор этого канала запретил загружать его ролики"}

db = DB()
users = Users(db.get_connection())  # блок получения БД
users.init_table()


def wr():
    global accounts, limit
    accounts[0] = str(limit) + "\n"
    fout = open("Cookies.txt", "w", encoding="utf-8")
    for i in accounts:
        fout.write(i)
    fout.close()


def agitation(id):
    vk.messages.send(
        user_id=id,
        message="Тестовое видео потрачено\n"
                "Для безлимитной загрузки видео зарегистрируйтесь по данной ссылке"
                " https://stvkr.com/click-HQRAA3UO-NLJQB8OF?bt=25&tl=1&sa=rjandael , после чего пришлите"
                " сюда сообщение с текстом '1' и"
                " прикрепленным скриншотом, подтверждающим регистрацию\n"
                "\n"
                "Это требуется для оплаты серверов, для вас все абсолютно бесплатно",
        random_id=randint(0, 19999),
    )


def try_repeat(func):
    def wrapper(*args, **kwargs):
        count = 3
        while count:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                E = e
                count -= 1
        print('Error:', E)
        vk.messages.send(
            user_id=253830804,
            message=E,
            random_id=randint(0, 19999)
        )

    return wrapper


try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)

longpoll = VkLongPoll(vk_session, mode=2)
vk = vk_session.get_api()


@try_repeat
def send_video(id, reciever):
    if id:
        message = "Дождитесь обработки видео ВК и наслаждайтесь просмотром"
        params = (
            ("user_id", reciever),
            ("random_id", random.randint(0, 19999)),
            ("message", message),
            ("attachment", "video-193181102_" + str(id)),
            ('access_token', community_token),
            ("v", "5.103")
        )
        requests.post('https://api.vk.com/method/messages.send', params=params)
    elif id == 0:
        pass
    else:
        message = "Извините, неполадки со стороны ютуба, пришлите другое видео))"
        params = (
            ("user_id", reciever),
            ("random_id", random.randint(0, 19999)),
            ("message", message),
            ("attachment", "video-193181102_" + str(id)),
            ('access_token', community_token),
            ("v", "5.103")
        )
        requests.post('https://api.vk.com/method/messages.send', params=params)


@try_repeat
def edit_desciption(args):
    id = args[0]
    name = args[1]
    if id == 0:
        return 0
    else:
        params = (
            ("owner_id", 193181102 * -1),
            ("video_id", id),
            ("name", name),
            ("desc",
             "основное сообщество - https://vk.com/youtubeupload"),
            ('access_token', user_token),
            ("v", "5.103")
        )
        requests.post('https://api.vk.com/method/video.edit', params=params)
        return id


@try_repeat
def upload_1(name, f, wallpost):
    params = (
        ("name", name),
        ("description", ""),
        ("wallpost", wallpost),
        ('group_id', 193181102),
        ('access_token', user_token),
        ("v", "5.103")
    )
    response = requests.get('https://api.vk.com/method/video.save', params=params)
    upload_server = json.loads(response.text)['response']['upload_url']
    id = json.loads(response.text)['response']['video_id']
    files = {'video_file': open(f, 'rb')}
    requests.post(upload_server, files=files)
    return id, name


@try_repeat
def autoposter(url, userid):
    global limit
    ydl_opts = {'outtmpl': "./video_PM/%(title)s.%(ext)s", 'quiet': True,
                'merge_output_format': 'mp4'}

    ydl = youtube_dl.YoutubeDL(ydl_opts)
    result = ydl.extract_info(url, download=False)
    views = result.get('view_count')
    channel = result.get('channel_id')
    n = ydl.prepare_filename(result)
    if views >= 500000 and limit < 50:
        wallpost = 1
        limit += 1
        wr()
    else:
        wallpost = 0

    if channel in taboo:
        vk.messages.send(
            user_id=userid,
            message=taboo[channel],
            random_id=randint(0, 19999)
        )
        return 0, 0
    else:
        ydl.download([url])
        id_vk, name_vk = upload_1(n[11:len(n) - 4], n, wallpost)
        os.remove(n)
        return id_vk, name_vk


def inspektor(id):
    global accounts
    accounts.append(str(id) + "\n")
    wr()


def main():
    global limit, accounts
    day = int(datetime.datetime.now().day)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if users.exists(event.user_id)[0]:
                sub = int(users.exists(event.user_id)[1])
                if sub > day or sub == 0:
                    if event.text[:8] == "https://":
                        if event.from_user:
                            vk.messages.send(
                                user_id=event.user_id,
                                message="Загрузка видео начата, ожидайте",
                                random_id=randint(0, 19999)
                            )
                            send_video(edit_desciption(autoposter(event.text, event.user_id)), event.user_id)
                        if sub == 0:
                            users.non_subscribe(event.user_id)
                            agitation(event.user_id)
                    elif event.user_id == 253830804:
                        if event.text.lower() == 'валид':
                            users.subscribe(event.user_id)
                            if event.from_user:
                                vk.messages.send(
                                    user_id=int(accounts[1]),
                                    message="Скриншот проверен, огромное спасибо за "
                                            "регистарцию, бот в твоем распоряжении))",
                                    random_id=randint(0, 19999),
                                )

                                vk.messages.send(
                                    user_id=253830804,
                                    message="Аккаунт " + "https://vk.com/id" + accounts[0] + " - валид",
                                    random_id=randint(0, 19999),
                                )
                                accounts = accounts[1:]
                                wr()
                        elif event.text.lower() == 'нет':
                            if event.from_user:
                                vk.messages.send(
                                    user_id=int(accounts[1]),
                                    message="Скриншот проверен, пришлите пожалуйста "
                                            "настоящий скрин успешной регистрации",
                                    random_id=randint(0, 19999),
                                )

                                vk.messages.send(
                                    user_id=253830804,
                                    message="Аккаунт " + "https://vk.com/id" + accounts[0] + " - не валид",
                                    random_id=randint(0, 19999),
                                )

                                accounts = accounts[1:]
                                wr()
                    else:
                        if event.from_user:
                            vk.messages.send(
                                user_id=event.user_id,
                                message="Я распознаю лишь ссылки",
                                random_id=randint(0, 19999),
                            )

                elif event.attachments:
                    if event.attachments['attach1_type'] == 'photo':
                        if event.from_user:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Ваш скриншот отправлен на проверку\n'
                                        'Максимальное время ожидания: 3 часа',
                                random_id=randint(0, 19999),
                            )
                            vk.messages.send(
                                user_id=253830804,
                                message="Валид? " + "https://vk.com/id" + str(event.user_id),
                                random_id=randint(0, 19999),
                                forward_messages=event.message_id,
                                keyboard=json.dumps({
                                    "one_time": False,
                                    "inline": True,
                                    "buttons": [[
                                        {
                                            "action": {
                                                "type": "text",
                                                "label": "Валид"
                                            },
                                            "color": "positive"
                                        },
                                        {
                                            "action": {
                                                "type": "text",
                                                "label": "Нет"
                                            },
                                            "color": "negative"
                                        }
                                    ]
                                    ]
                                })
                            )
                            inspektor(event.user_id)

                else:
                    agitation(event.user_id)

            else:
                users.insert(event.user_id)
                if event.from_user:
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Привет, это долгожданная вторая версия бота "Youtube перезаливы"\n'
                                'Я полностью переработал загрузку видео и исправил ошибки, теперь бот работает еще'
                                ' лучше\n'
                                'К сожалению оплата серверов это далеко не дешево, по этой причине бот был отключен'
                                ' два месяца из-за нехватки средств\n'
                                'Просить деньги за такую услугу как просмотр видео я считаю неприемлимым\n'
                                'Единственный простой и выгодный для всех сторон выход это реклама, поэтому прошу'
                                ' следовать указаниям для стабильной работы бота, все абсолютно бесплатно)\n'
                                '\n'
                                'Вам предаставляется одно тестовое видео, для ознакомления с ботом\n'
                                'Когда вы его потратите вам прийдет ссылка, по которой вы должны зарегистрироваться'
                                ' и прислать мне подтверждающий скрин регистрации, после чего вам разблокируется бот\n'
                                'К сожалению это вынужденная мера для существования бота\n'
                                'Все просто и доступно, я уверен все справятся, при возникновении проблем'
                                ' пишите админу\n'
                                'Зарание спасибо\n',
                        random_id=randint(0, 19999),
                    )

        if day != int(datetime.datetime.now().strftime("%j")):
            day = int(datetime.datetime.now().strftime("%j"))
            limit = 0
            wr()
            for root, dirs, files in os.walk("\\video_PM\\"):
                for file in files:
                    os.remove(os.path.join(root, file))
            vk.messages.send(
                user_id=253830804,
                message='Обнулился ебана рот',
                random_id=randint(0, 19999),
            )


try:
    time.sleep(2)
    main()
except requests.exceptions.ConnectionError:
    print("Поймал, ебать")
    os.system('python3 s_bot.py')
    time.sleep(1)
    quit()
except requests.exceptions.ReadTimeout:
    print("Поймал, ебать")
    os.system('python3 s_bot.py')
    time.sleep(1)
    quit()
except vk_api.exceptions.ApiError:
    print("Поймал, ебать")
    os.system('python3 s_bot.py')
    time.sleep(1)
    quit()
