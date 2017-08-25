from django.shortcuts import render
import telepot
import urllib3, json
from django.http import HttpResponse
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import logging


proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))


logger = logging.getLogger(__name__)
# logger.error('Something went wrong!')

print('Bot started')

secret = "f893df61-ee35-4a84-87fd-f0698b7438f7"
bot = telepot.Bot('408802721:AAHmVxkphGXoPWhQruHOLMDubWCkLk-vfCE')
bot.setWebhook("https://timeismoney.pythonanywhere.com/webhook", max_connections=1)

step = 0
worker = 0
description = ""
time = 0


@csrf_exempt
def telegram_webhook(request):
    #    print (request.body)
    body_unicode = request.body.decode('utf-8')
    update = json.loads(body_unicode)
    if "message" in update:
        logic(update)
    return HttpResponse("OK")


def logic(update):
    text = update["message"]["text"]
    chat_id = update["message"]["chat"]["id"]

    if text == "/start":
        start(chat_id)
    elif text == "Да" and step == 1:
        project_type(chat_id)
    elif text == "Коммерческие" and step == 2:
        project_list(chat_id)
    elif text == "Делал бота" and step == 3:
        job_description(chat_id)
    elif step == 4:
        get_job_description(chat_id, text)
    elif step == 5:
        get_tracked_time(chat_id, text)
    elif text == "Да" and step == 6:
        get_confirmation(chat_id)

    else:
        dont_understand(chat_id)

    print(chat_id, " ", text)


def start(chat_id):
    global step, worker
    worker = chat_id
    bot.sendMessage(chat_id, "Привет! Расскажешь, что делал сегодня?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Да"), KeyboardButton(text="Напомнить через 30 минут")]
                        ], resize_keyboard=True, one_time_keyboard=True))
    step = 1


def dont_understand(chat_id):
    bot.sendMessage(chat_id, "Я не знаю такой команды")


def project_type(chat_id):
    bot.sendMessage(chat_id, "Над каким проектом ты работал?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Коммерческие"), KeyboardButton(text="Внутренние")]
                        ], resize_keyboard=True, one_time_keyboard=True))
    global step
    step = 2


def project_list(chat_id):
    bot.sendMessage(chat_id, "Над каким проектом ты работал?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Делал бота"), KeyboardButton(text="Делал работу")]
                        ], resize_keyboard=True, one_time_keyboard=True))
    global step
    step = 3


def job_description(chat_id):
    bot.sendMessage(chat_id, "Что именно делал?")
    global step
    step = 4


def get_job_description(chat_id, text):
    global description
    description = text
    bot.sendMessage(chat_id, "Сколько времени потратил? (в часах)",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="1"), KeyboardButton(text="2"),
                             KeyboardButton(text="3"), KeyboardButton(text="4"), KeyboardButton(text="5")]
                        ], resize_keyboard=True, one_time_keyboard=True))
    global step
    step = 5


def get_tracked_time (chat_id, text):
    global time
    time = text
    bot.sendMessage(chat_id, "Ты работал над проектом 'Делал бота', сделал '"+description+"', за "+text+" часов. Верно?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
                        ], resize_keyboard=True, one_time_keyboard=True))
    global step
    step = 6


def get_confirmation(chat_id):
    bot.sendMessage(chat_id, "Спасибо!")
    global step
    step = 0

