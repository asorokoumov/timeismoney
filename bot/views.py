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
    worker = Worker.objects.get(telegram_username=username)
    # check if worker exists
    if worker:
        if text == "/start":
            # set current step to "Start" and start logging from the beginning
            start(chat_id)
            LoggingStep.objects.update_or_create(worker=worker, defaults={"step": "Start"})

        # check if we've already logged something for this worker
        elif LoggingStep.objects.filter(worker=worker).exists():
            logging_step = LoggingStep.objects.get(worker=worker)

            # "Start". Just started logging process (Расскажешь, что делал сегодня?)
            if logging_step.step == "Start":
                if text == "Да":
                    define_project_type(chat_id)
                    logging_step.step = "Define project type"
                    logging_step.save()
                elif text == "Напомнить через 30 минут":
                    not_ready(chat_id)
                else:
                    not_ready(chat_id)

            # "Define Project Type" (Над каким проектом работал?)
            elif logging_step.step == "Define project type":
                if text == "Коммерческий":
                    choose_commercial_project(chat_id)
                    logging_step.step = "Choose commercial project"
                    logging_step.save()
                elif text == "Внутренний":
                    choose_internal_project(chat_id)
                    logging_step.step = "Choose internal project"
                    logging_step.save()
                else:
                    not_ready(chat_id)

            # "Choose internal project" (Список внутренних проектов)
            elif logging_step.step == "Choose internal project":
                if text == "Обучение":
                    logging_step.project = text
                    what_did_you_do(chat_id)
                    logging_step.step = "What did you do?"
                    logging_step.save()
                elif text == "Собеседование":
                    logging_step.project = text
                    who_is_the_interviewee(chat_id)
                    logging_step.step = "Who is the interviewee?"
                    logging_step.save()
                elif text == "Болезнь":
                    logging_step.project = text
                    not_ready(chat_id)
                    logging_step.step = "Was ill all day?"
                    logging_step.save()
                else:
                    not_ready(chat_id)

            # "Choose commercial project" (Список коммерческих проектов)
            elif logging_step.step == "Choose commercial project":
                logging_step.project = text
                what_did_you_do(chat_id)
                logging_step.step = "What did you do?"
                logging_step.save()

            # "What did you do?" (Что именно делал?)
            elif logging_step.step == "What did you do?":
                logging_step.details = text
                how_much_time_did_you_spend(chat_id)
                logging_step.step = "How much time did you spend?"
                logging_step.save()

            # "Who is the interviewee?" (Кого собеседовал)
            elif logging_step.step == "Who is the interviewee?":
                logging_step.details = text
                how_much_time_did_you_spend(chat_id)
                logging_step.step = "How much time did you spend?"
                logging_step.save()

            # "How much time did you spend?" (Сколько времени потратил)
            elif logging_step.step == "How much time did you spend?":
                logging_step.time_spent = float(text)
                confirm_result(chat_id=chat_id, logging_step=logging_step)
                logging_step.step = "Confirm result"
                logging_step.save()

            # "Confirm result" (Сделал это. Верно?)
            elif logging_step.step == "Confirm result":
                if text == "Да":
                    thank_you(chat_id)
                    TimeSheet.objects.create(worker=logging_step.worker, project=logging_step.project,
                                             time_spent=logging_step.time_spent, details=logging_step.details)
                    logging_step.delete()

                elif text == "Нет":
                    not_ready(chat_id)
                else:
                    not_ready(chat_id)

        else:
            dont_understand(chat_id)
    else:
        unknown_user(chat_id)


def start(chat_id):
    bot.sendMessage(chat_id, "Привет! Расскажешь, что делал сегодня?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Да"), KeyboardButton(text="Напомнить через 30 минут")]
                        ], resize_keyboard=True, one_time_keyboard=True))


def dont_understand(chat_id):
    bot.sendMessage(chat_id, "Я не знаю такой команды")


def define_project_type(chat_id):
    bot.sendMessage(chat_id, "Над каким проектом ты работал?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="Коммерческие"), KeyboardButton(text="Внутренние")]
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
