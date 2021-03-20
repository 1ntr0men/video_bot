import vk_api
import requests
from db import DB, Users
from vk_api import VkUpload
from random import randint
from vk_api.longpoll import VkLongPoll, VkEventType
import json
import os
import youtube_dl
import time

# токены
user_token = "a9de7c0b0479bd9b3eba471fa7c837a383adda2fea40387cdf6c2cd560fe5b9c46a9bd3033fa74c70e248"
community_token = "519b455618498f3d0a1ed56407bc84fa7db6f3cb382ec19a734678a65861aa8afab2cc75a18e6cdefd093"

# json с куки
with open('Cookies.json', encoding='utf-8') as f:
    cookies = json.loads(f.read())

# получение данных из куки
sub_queue = cookies["sub_queue"]
limit = cookies["limit"]
ban_authors = cookies["ban_authors"]

# создание сессии вк
session = requests.Session()
vk_session = vk_api.VkApi(token=community_token)
upload = VkUpload(vk_session)

# подключение к БД
db = DB()
users = Users(db.get_connection())
users.init_table()


# cохранение данных в файл json
def wr():
    global sub_queue, limit, ban_authors
    to_json = {"limit": limit,
               "sub_queue": sub_queue,
               "ban_authors": ban_authors}
    with open('Cookies.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(to_json, ensure_ascii=False))  # сохранение словаря в файл в формате json


# декоратор повторного запуска функции в случае ошибки
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


# подключение к сессии вк
try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)

longpoll = VkLongPoll(vk_session, mode=2)
vk = vk_session.get_api()


# функция загрузки видео из ютуба
@try_repeat
def autoposter(url, userid):
    global limit

    ydl_opts = {'outtmpl': "./video_PM/%(title)s.%(ext)s", 'quiet': True,  # опции для загрузки видео через youtube_dl
                'merge_output_format': 'mp4'}

    ydl = youtube_dl.YoutubeDL(ydl_opts)
    video_info = ydl.extract_info(url, download=False)
    duration = video_info.get("duration")  # создание обьекта типа youtube_dl и парсинг данных оттуда
    views = video_info.get('view_count')
    channel = video_info.get("uploader")
    title = "{" + channel + "} " + video_info.get("title")
    video_path = ydl.prepare_filename(video_info)

    if views >= 500000 and limit < 50:  # если больше 500000 просмотров то постим на стену группы
        wallpost_flag = 1
        limit += 1
        wr()  # сохранение
    else:
        wallpost_flag = 0

    if channel in ban_authors:  # проверка, находится ли автор бане
        vk.messages.send(
            user_id=userid,
            message="Автор этого канала запретил загружать его ролики((",
            random_id=randint(0, 19999)
        )
        return 0, 0

    elif duration > 7200:  # проверка, что видео длится менее 2 часов
        vk.messages.send(
            user_id=userid,
            message="Вк не дает загружать видео больше 2 часов, пожалуйста пришли другой ролик",
            random_id=randint(0, 19999)
        )
        return 0, 0

    else:  # загрузка видео
        ydl.download([url])  # загрузка видео через youtube_dl
        video_id = upload_1(title, video_path, wallpost_flag)  # выгрузка видео в вк и получение его id обратно
        os.remove(video_path)  # удаление видео с устройства

        return video_id, title


# Выгрузка видео на сервер ВК
@try_repeat
def upload_1(title, video_path, wallpost_flag):
    params = (
        ("name", title),
        ("description", ""),
        ("wallpost", wallpost_flag),
        ('group_id', 193181102),
        ('access_token', user_token),
        ("v", "5.103")
    )

    response = requests.get('https://api.vk.com/method/video.save', params=params)
    upload_server = json.loads(response.text)['response']['upload_url']  # получение ссылки для выгрузки видео

    video_id = json.loads(response.text)['response']['video_id']  # получение id видео

    files = {'video_file': open(video_path, 'rb')}  # выгрузка файла с видео на сервер вк по полученной ссылке
    requests.post(upload_server, files=files)

    return video_id


# исправление описания видео(добавление рекламы в описание)
@try_repeat
def edit_desciption(args):
    video_id = args[0]  # распаковка аргументов
    title = args[1]

    if video_id == 0:  # если не прошли условия в autoposter
        return 0
    else:
        params = (
            ("owner_id", 193181102 * -1),
            ("video_id", id),
            ("name", title),
            ("desc", "основное сообщество - https://vk.com/youtubeupload"),
            ('access_token', user_token),
            ("v", "5.103")
        )
        requests.post('https://api.vk.com/method/video.edit', params=params)

        return video_id


# отправка видео пользователю, который запросил видео
@try_repeat
def send_video(video_id, reciever):
    if video_id:  # отправка видео пользователю
        message = "Дождитесь обработки видео ВК и наслаждайтесь просмотром"
        params = (
            ("user_id", reciever),
            ("random_id", randint(0, 19999)),
            ("message", message),
            ("attachment", "video-193181102_" + str(video_id)),
            ('access_token', community_token),
            ("v", "5.103")
        )
        requests.post('https://api.vk.com/method/messages.send', params=params)
    elif video_id == 0:  # ничего если не прошли условия в autoposter
        pass
    else:  # какие то неисправности с видео, вк или youtube
        message = "Извините, неполадки со стороны ютуба, пришлите другое видео))"
        params = (
            ("user_id", reciever),
            ("random_id", randint(0, 19999)),
            ("message", message),
            ("attachment", "video-193181102_" + str(id)),
            ('access_token', community_token),
            ("v", "5.103")
        )
        requests.post('https://api.vk.com/method/messages.send', params=params)


# просьба о регистрации
def agitation(user_id):
    vk.messages.send(
        user_id=user_id,
        message="Тестовое видео потрачено\n"
                "Для безлимитной загрузки видео зарегистрируйтесь по данной ссылке"
                " https://stvkr.com/click-HQRAA3UO-NLJQB8OF?bt=25&tl=1&sa=rjandael , после чего пришлите"
                " сюда сообщение с текстом '1' и прикрепленным скриншотом, подтверждающим регистрацию\n"
                "\n"
                "Это требуется для оплаты серверов, для вас все абсолютно бесплатно",
        random_id=randint(0, 19999),
    )


# метод добавления нового пользователя в очередь ожидающих подписку
def add_sub_queue(user_id):
    global sub_queue
    sub_queue.append(str(user_id))
    wr()  # сохранение


# основная программа
def main():
    global limit, sub_queue
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if users.exists(event.user_id)[0]: # проверка что пользователь есть в БД

                user_subscription = int(users.exists(event.user_id)[1])  # состояние подписки пользователя

                if user_subscription >= 0:
                    if event.text[:8] == "https://":  # запрос видео
                        if event.from_user:
                            vk.messages.send(
                                user_id=event.user_id,
                                message="Загрузка видео начата, ожидайте",
                                random_id=randint(0, 19999)
                            )
                            # загрузка, выгрузка в вк, изменение описания и отправка пользователю видео
                            send_video(edit_desciption(autoposter(event.text, event.user_id)), event.user_id)

                        if user_subscription == 0:  # если пользователь заказал свое первое видео
                            users.non_subscribe(event.user_id)  # установка запрета на загрузку видео
                            agitation(event.user_id)  # отправка пользователю оповещения, чтобы он зарегистрировался

                    elif event.user_id == 253830804:  # сообщение от владельца

                        if event.text.lower() == 'валид':  # скриншот валидный
                            users.subscribe(int(sub_queue[0]))  # пользователю дается доступ
                            if event.from_user:
                                vk.messages.send(  # отправка пользователю сообщения об успехе
                                    user_id=int(sub_queue[0]),
                                    message="Скриншот проверен, огромное спасибо за "
                                            "регистарцию, бот в твоем распоряжении))",
                                    random_id=randint(0, 19999),
                                )

                                vk.messages.send(  # отправление владельцу сообщения об успехе
                                    user_id=253830804,
                                    message="Аккаунт " + "https://vk.com/id" + sub_queue[0] + " - валид",
                                    random_id=randint(0, 19999),
                                )

                                sub_queue = sub_queue[1:]  # удаление пользователя из очереди на получение подписки
                                wr()  # сохранение

                        elif event.text.lower() == 'нет':  # скриншот не валидный
                            if event.from_user:
                                vk.messages.send(  # сообщение о неудаче пользователю
                                    user_id=int(sub_queue[0]),
                                    message="Скриншот проверен, пришлите пожалуйста "
                                            "настоящий скрин успешной регистрации",
                                    random_id=randint(0, 19999),
                                )

                                vk.messages.send(  # сообщение о неудаче владельцу
                                    user_id=253830804,
                                    message="Аккаунт " + "https://vk.com/id" + sub_queue[0] + " - не валид",
                                    random_id=randint(0, 19999),
                                )

                                sub_queue = sub_queue[1:]  # удаление пользователя из очереди на получение подписки
                                wr()  # сохранение

                        elif event.text.lower()[:7] == 'удалить':  # удаление пользователя из подписчиков
                            if event.from_user:
                                users.delete(int(event.text.lower()[8:]))
                                vk.messages.send(
                                    user_id=253830804,
                                    message="Аккаунт " + "https://vk.com/id" +
                                            event.text.lower()[8:] + " успешно удален",
                                    random_id=randint(0, 19999),
                                )
                        else:  # дефолтное сообщение бота, в случае отсутствия четкой команды
                            if event.from_user:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message="Я распознаю лишь ссылки на видео из YouTube",
                                    random_id=randint(0, 19999),
                                )

                    else:  # дефолтное сообщение бота, в случае отсутствия четкой команды
                        if event.from_user:
                            vk.messages.send(
                                user_id=event.user_id,
                                message="Я распознаю лишь ссылки на видео из YouTube",
                                random_id=randint(0, 19999),
                            )

                elif "attach1_type" in event.attachments:  # пользователь прислал скрин регистрации
                    if event.attachments['attach1_type'] == 'photo':
                        if event.from_user:
                            vk.messages.send(  # сообщение пользователю чтобы он ожидал проверки
                                user_id=event.user_id,
                                message='Ваш скриншот отправлен на проверку\n'
                                        'Максимальное время ожидания: 3 часа',
                                random_id=randint(0, 19999),
                            )

                            vk.messages.send(  # отправка на проверку скрина владельцу
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

                            add_sub_queue(event.user_id)  # добавление нового пользователя в очередь ожидающих подписку

                else:
                    agitation(event.user_id)  # случае отсутствия подписки присылается просьба о регистрации

            else:  # Первое сообщение новому пользователю
                users.insert(event.user_id)
                if event.from_user:
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Привет! Пришли ссылку на нужное тебе видео из ютуба, бот зальет',
                        random_id=randint(0, 19999),
                    )


# запуск основной программы и ее перезапуск в случае ошибок
try:
    time.sleep(2)
    main()
except requests.exceptions.ConnectionError:
    print("ПЕРЕЗАПУСК БОТА")
    os.system('python3 s_bot.py')
    time.sleep(1)
    quit()
except requests.exceptions.ReadTimeout:
    print("ПЕРЕЗАПУСК БОТА")
    os.system('python3 s_bot.py')
    time.sleep(1)
    quit()
except vk_api.exceptions.ApiError:
    print("ПЕРЕЗАПУСК БОТА")
    os.system('python3 s_bot.py')
    time.sleep(1)
    quit()
