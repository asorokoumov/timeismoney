from django.shortcuts import render
import telepot
import urllib3, json
from django.http import HttpResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)
logger.error('Something went wrong!')

print ('here am I')


secret = "f893df61-ee35-4a84-87fd-f0698b7438f7"
bot = telepot.Bot('408802721:AAHmVxkphGXoPWhQruHOLMDubWCkLk-vfCE')
bot.setWebhook("https://timeismoney.pythonanywhere.com/{}".format(secret), max_connections=1)

logger.debug('testd')
logger.info('testi')
logger.warning('testw')
logger.error('teste')
logger.critical('testc')

@csrf_exempt
def telegram_webhook(request):
    print("I'm done")

    update = json.loads(request.body)
    print(update)
    if "message" in update:
        print("Yes")
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
        print (chat_id, " ", text)
    else:
        print("No")


    return HttpResponse("OK")

