# Бот не восстанавливает данные при перезагрузке.

import vk_api, json
from vk_api.longpoll import VkLongPoll, VkEventType
from threading import Thread
from os.path import abspath as tdir
from toks import main_token
import sqlite3


vk_session = vk_api.VkApi(token = main_token)
session_api = vk_session.get_api()
LongPoll = VkLongPoll(vk_session)

def check(x):
    file = open('data.txt', 'r', encoding = 'utf-8')
    if str(x) in file.read():
        return 1
    else:
        return 0
    file.close()

def save_bd(users):
	lines = []
	for user in users:
		lines.append(f'"id" : {user.id}, "mode" : "{user.mode}", "money" : "{user.money}", "name" : "{user.name}"')
	lines = '\n'.join(lines)
	with open(f'{tdir(__file__)}/data.txt'.replace('\\', '/').replace('smartbotchat.py/', ''), 'w', encoding = 'utf-8') as file:
		file.write(lines)
		file.close()

def read_bd():
	users = []
	with open(f'{tdir(__file__)}/data.txt'.replace('\\', '/').replace('smartbotchat.py/', ''), 'r', encoding = 'utf-8') as file:
		lines = [x.replace('\n', '') for x in file.readlines()]
		file.close()
	for line in lines:
		line = eval('{' + line + '}')
		if line != '{}':
			users.append(User(id = line['id'], mode = line['mode'], money = line['money'], name = line['name']))
	return users

def adder(x):
    file = open('data.txt', 'a', encoding = 'utf-8')
    file.write(f'{x}\n')
    file.close()
    

class User:

    def __init__(self, id, mode, money = 0, name = ""):
        self.id = id
        self.mode = mode
        self.money = money
        self.name = name
        self.age = -1
        self.cars = 0
        self.axs = 0
        self.quest = 0


def get_keyboard(buts):
    nb = []
    for i in range(len(buts)):
        nb.append([])
        for k in range(len(buts[i])):
            nb[i].append(None)
    for i in range(len(buts)):
        for k in range(len(buts[i])):
            text = buts[i][k][0]
            color = {"зеленый" : "positive", "красный" : "negative", "синий" : "primary"}[buts[i][k][1]]
            nb[i][k] = {"action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"}, "color": f"{color}"}
    first_keyboard = {"one_time": False, "buttons": nb, "inline": False}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode("utf-8")
    first_keyboard = str(first_keyboard.decode("utf-8"))
    return first_keyboard

def sender(id, text, key):
    vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0, "keyboard" : key})

clear_key = get_keyboard(
    []
)

menu_key = get_keyboard([
    [("Профиль", "синий"), ("Магазин", "зеленый")],
    [("Ивент", "красный"), ("Задание", "красный")],
])

shop_key = get_keyboard([
    [("Аксессуары", "синий"), ("Автомобили", "синий")],
    [("Назад", "красный")]
])

quest_key = get_keyboard([
    [("Выполнить", "зеленый")]
])

users = []

for event in LongPoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:

            msg = event.text.lower()
            id = event.user_id
            if msg == "начать":
                flag = 0
                for user in users:
                    if user.id == id:
                        flag = 1
                        break
                if flag == 0:
                    users.append(User(id, "reg1"))
                    sender(id, "Добро пожаловать, для прохождения ивента - зарегистрируйтесь.\nВведите свой игровой ник:", clear_key)
                elif flag == 1:
                    for user in users:
                        if user.id == id:
                            if not(user.mode in ["reg1", "reg2"]):
                                sender(id, "Вы уже зарегистрировались.", clear_key)
            else:
                for user in users:
                    if user.id == id:
                        if user.mode == "reg1":
                            user.name = msg.title()
                            sender(id, "Введите свой игровой уровень:", clear_key)
                            user.mode = "reg2"

                        elif user.mode == "reg2":
                            try:
                                user.age = int(msg)
                                sender(id, "Вы успешно зарегистировались на ивент!", menu_key)
                                user.mode = "menu"
                            except:
                                sender(id, "Пожалуйста, введите корректный уровень.", clear_key)

                        elif user.mode == "menu":
                            if msg == "профиль":
                                sender(id, f"Ваш игровой ник: {user.name}\nВаш игровой уровень: {user.age}\nВаш баланс: {user.money}$", menu_key)
                else:
                    for user in users:
                        if user.id == id:

                            if user.mode == "menu":
                                if msg == "ивент":
                                    sender(id, "Привет! Мы для тебя подготовили масштабное новогоднее обновление на ONLINE RP. Новогодний Ивент, уникальный промокод, магазин сладостей и новогодняя рулетка! Ваша задача ждать ежедневные задания и выполнять, а после получать классные подарки. Ровно в 00:00 будут приходить задания, которые должен успеть сделать за 24 часа!\n Бонусы: кто имеет фамилию Wayne будет получать сразу по 2 задания! Будет доступен полный функционал магазина и официальную подпись от группы!\n Временный новогодний промокод - WaFe. Используйте его для уникального события, которая подготовила Руководство семьи. А если WaFe с уникальным юникодом, который можно узнать только в беседе, то вы на пути к мечте!\n Ивент продлится до 10.01.2023г включительно.", menu_key)
                                    user.mode = "menu"
                    else:
                        for user in users:
                            if user.id == id:

                                if user.mode == "menu":
                                    if msg == "магазин":
                                        sender(id, "Выберите интересующие вас товары:", shop_key)
                                        user.mode = "shop"
                                elif user.mode == "shop":
                                    if msg == "назад":
                                        sender(id, "Вы вернулись назад.", menu_key)
                                        user.mode = "menu"

                                    elif msg == "аксессуары":
                                        sender(id, "Пока нет товаров.", clear_key)
                                        user.mode = "get_axs_count"

                                    elif msg == "автомобили":
                                        sender(id, "Пока нет товаров.", clear_key)
                                        user.mode = "get_cars_count"

                                elif user.mode == "get_axs_count":
                                    try:
                                        col = int(msg)
                                        if user.money >= col*50:
                                            user.money -= col*50
                                            user.axs += col
                                            sender(id, f"Вы успешно приобрели товар, перешлите данное сообщение Руководству. {col} единиц", shop_key)
                                            user.mode = "shop"
                                        else:
                                            sender(id, "Не достаточно средств.", shop_key)
                                            user.mode = "shop"
                                    except Exception as e:
                                        sender(id, "Не верно введены данные.", shop_key)
                                        user.mode = "shop"

                                elif user.mode == "get_cars_count":
                                    if msg == "назад":
                                        sender(id, "Вы вернулись назад.", menu_key)
                                        user.mode = "menu"
                                    try:
                                        col = int(msg)
                                        if user.money >= col*60:
                                            user.money -= col*60
                                            user.cars += col
                                            sender(id, f"Вы успешно приобрели товар, перешлите данное сообщение Руководству. {col} единиц", shop_key)
                                            user.mode = "shop"
                                        else:
                                            sender(id, "Не достаточно средств.", shop_key)
                                            user.mode = "shop"
                                    except Exception as e:
                                        sender(id, "Не верно введены данные.", shop_key)
                                        user.mode = "shop"

                        else:
                            for user in users:
                                if user.id == id:
                                    if user.mode == "menu":
                                        if msg == "задание":
                                            sender(id, "Выполняй все инструкции, которые будут описаны поэтапно - нажимай выполнить.\n Задание: Тебе приходило сообщение, либо отправило руководство новое задание, выполняй его, подпишись на рассылку в группе, чтоб получать вовремя.", quest_key)
                                            user.mode = "quest"
                                    elif user.mode == "quest":
                                        if msg == "назад":
                                            sender(id, "Вы вернулись.", menu_key)
                                            user.mode = "menu"
                                        elif msg == "выполнить":
                                            sender(id, "Вставь в диалог док-ва для проверки и следующем сообщением нажми Выполнить.", clear_key)
                                            user.mode = "get_quest_count"
                                    elif user.mode == "get_quest_count":
                                        try:
                                            col = int(msg)
                                            if user.money <= col+0:
                                                user.money += col+10000
                                                user.quest -= col
                                                sender(id, f"Ваш отчет в обработке, но награда уже выплачена! Начислено {col}$", menu_key)
                                                user.mode = "menu"
                                            else: 
                                                sender(id, "Принято, теперь нажми выполнить, после нового сообщения напиши 10000", quest_key)
                                                user.mode = "quest"
                                        except Exception as e:
                                            sender(id, "Принято, теперь нажми выполнить, после нового сообщения напиши 10000", quest_key)
                                            user.mode = "quest"
            
                save_bd(users)
                                            
