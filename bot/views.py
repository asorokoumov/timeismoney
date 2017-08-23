from django.shortcuts import render
import telepot
import urllib3, json

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

print("ITS ALIVE")

secret = "f893df61-ee35-4a84-87fd-f0698b7438f7"
bot = telepot.Bot('408802721:AAHmVxkphGXoPWhQruHOLMDubWCkLk-vfCE')
bot.setWebhook("https://timeismoney.pythonanywhere.com/{}".format(secret), max_connections=1)


@csrf_exempt
def telegram_webhook(request):
    print("I'm done")
    update = json.loads(request.body)
    if "message" in update:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
    return "OK"
