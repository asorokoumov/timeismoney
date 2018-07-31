from django.shortcuts import render
import telepot
import urllib3, json
from django.http import HttpResponse
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from bot.models import Worker, LoggingStep, TimeSheet

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
    username = update["message"]["chat"]["username"]
    try:
        worker = Worker.objects.get(telegram_username=username)
        if text == "/start":
            # set current step to "Start" and start logging from the beginning
            output_start(chat_id)
            LoggingStep.objects.update_or_create(worker=worker, defaults={"step": "Start"})

        # check if we've already logged something for this worker
        elif LoggingStep.objects.filter(worker=worker).exists():
            logging_step = LoggingStep.objects.get(worker=worker)

            # "Start". Just started logging process (Расскажешь, что делал сегодня?)
            if logging_step.step == "Start":
                logic_start(chat_id=chat_id, logging_step=logging_step, text=text)

            # "Choose shoes type" (Выбери тип обуви)
            elif logging_step.step == "Choose shoes type":
                logic_choose_shoes_type(chat_id=chat_id, logging_step=logging_step, text=text)

            # Choose shoes size
            elif logging_step.step == "Choose shoes size":
                logic_choose_shoes_size(chat_id=chat_id, logging_step=logging_step, text=text)

            # Choose shoes width
            elif logging_step.step == "Choose shoes width":
                logic_choose_shoes_type(chat_id=chat_id, logging_step=logging_step, text=text)

            # Choose sole color
            elif logging_step.step == "Choose sole color":
                logic_choose_sole_color(chat_id=chat_id, logging_step=logging_step, text=text)

            # Choose top material
            elif logging_step.step == "Choose top material":
                logic_choose_top_material(chat_id=chat_id, logging_step=logging_step, text=text)

            # Enter client info
            elif logging_step.step == "Enter client info":
                logic_enter_client_info(chat_id=chat_id, logging_step=logging_step, text=text)

            # Output order NR and PDF
            elif logging_step.step == "Output order NR and PDF":
                output_order_nr_and_pdf (chat_id=chat_id, logging_step=logging_step)
        else:
            dont_understand(chat_id)
    except Worker.DoesNotExist:
        unknown_user(chat_id)


# start
def output_start(chat_id):
    bot.sendMessage(chat_id, "Привет! Что надо сделать?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Создать заказ"),
                             KeyboardButton(text="Изменить статус заказа")],
                             KeyboardButton(text="Текущие активные заказы")]
                        , resize_keyboard=True, one_time_keyboard=True))


def logic_start(text, chat_id, logging_step):
    if text == "Создать заказ":
        output_choose_shoes_type(chat_id)
        logging_step.step = "Choose shoes type"
        logging_step.save()
    elif text == "Изменить статус заказа":
        not_ready(chat_id)
    elif text == "Изменить статус заказа":
        not_ready(chat_id)

    else:
        not_ready(chat_id)


# choose shoes type
def output_choose_shoes_type(chat_id):
    bot.sendMessage(chat_id, "Какой тип обуви нужно сделать?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Кеды"), KeyboardButton(text="Туфли")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def logic_choose_shoes_type(text, chat_id, logging_step):
    if text == "Кеды":
        output_choose_shoes_size(chat_id)
        logging_step.step = "Choose shoes size"
        logging_step.save()
    elif text == "Туфли":
        output_choose_shoes_size(chat_id)
        logging_step.step = "Choose shoes size"
        logging_step.save()
    else:
        not_ready(chat_id)


# choose shoes size
def output_choose_shoes_size(chat_id):
    bot.sendMessage(chat_id, "Какой тип обуви нужно сделать?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="39"),
                             KeyboardButton(text="40"),
                             KeyboardButton(text="41"),
                             KeyboardButton(text="42"),
                             KeyboardButton(text="43"),
                             KeyboardButton(text="44"),
                             KeyboardButton(text="45")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def logic_choose_shoes_size(text, chat_id, logging_step):
    sizes = ['39', '40', '41', '42', '43', '44', '45']
    if any(text in s for s in sizes):
        output_choose_shoes_width(chat_id)
        logging_step.step = "Choose shoes width"
        logging_step.save()
    else:
        not_ready(chat_id)


# choose shoes width
def output_choose_shoes_width(chat_id):
    bot.sendMessage(chat_id, "Какая полнота обуви?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Стандарт"),
                             KeyboardButton(text="+1")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def logic_choose_shoes_width(text, chat_id, logging_step):
    width = ['Стандарт', '+1']
    if any(text in s for s in width):
        output_choose_sole_color(chat_id)
        logging_step.step = "Choose sole color"
        logging_step.save()
    else:
        not_ready(chat_id)


# choose sole color
def output_choose_sole_color(chat_id):
    bot.sendMessage(chat_id, "Какой цвет подошвы?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Белый"),
                             KeyboardButton(text="Черный")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def logic_choose_sole_color(text, chat_id, logging_step):
    sole_color = ['Белый', 'Черный']
    if any(text in s for s in sole_color):
        output_choose_top_material(chat_id)
        logging_step.step = "Choose top material"
        logging_step.save()
    else:
        not_ready(chat_id)


# choose top material
def output_choose_top_material(chat_id):
    bot.sendMessage(chat_id, "Напиши материал для верха")


def logic_choose_top_material(text, chat_id, logging_step):
    output_enter_client_info(chat_id)
    logging_step.step = "Enter client info"
    logging_step.save()


#  enter client info
def output_enter_client_info(chat_id):
    bot.sendMessage(chat_id, "Напиши данные клиента")


def logic_enter_client_info(text, chat_id, logging_step):
    choose_commercial_project(chat_id)
    logging_step.step = "Output order NR and PDF"
    logging_step.save()


# orderNR, generate pdf, finish
def output_order_nr_and_pdf(chat_id, logging_step):
    bot.sendMessage(chat_id, "Номер заказа: 4242")
    bot.sendMessage(chat_id, "PDF можете скачать по ссылке: https://tinyurl.com/4poyc6x")
    bot.sendMessage(chat_id, "До новых встреч.")

    logging_step.step = "Finish"
    logging_step.save()



def dont_understand(chat_id):
    bot.sendMessage(chat_id, "Я не знаю такой команды")


def define_project_type(chat_id):
    bot.sendMessage(chat_id, "Над каким проектом ты работал?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Коммерческий"), KeyboardButton(text="Внутренний")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def choose_commercial_project(chat_id):
    bot.sendMessage(chat_id, "Над каким проектом ты работал?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Делал бота"), KeyboardButton(text="Делал работу")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def choose_internal_project(chat_id):
    bot.sendMessage(chat_id, "Над каким проектом ты работал?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Обучение"), KeyboardButton(text="Собеседование"),
                             KeyboardButton(text="Болезнь")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def what_did_you_do(chat_id):
    bot.sendMessage(chat_id, "Что именно делал?")


def who_is_the_interviewee(chat_id):
    bot.sendMessage(chat_id, "Кого собеседовал?")


def how_much_time_did_you_spend(chat_id):
    bot.sendMessage(chat_id, "Сколько времени потратил? (в часах)",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="1"), KeyboardButton(text="2"),
                             KeyboardButton(text="3"), KeyboardButton(text="4"), KeyboardButton(text="5")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def confirm_result(chat_id, logging_step):
    bot.sendMessage(chat_id, "Ты работал над проектом '" + logging_step.project +
                    "', сделал '" + logging_step.details +
                    "', за " + str(logging_step.time_spent) + " ч. Верно?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def thank_you(chat_id):
    bot.sendMessage(chat_id, "Спасибо!")


def unknown_user(chat_id):
    bot.sendMessage(chat_id, "Я вас не знаю!")


def not_ready(chat_id):
    bot.sendMessage(chat_id, "Not ready")
