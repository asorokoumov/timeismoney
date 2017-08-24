from django.shortcuts import render
import telepot
import urllib3, json
from django.http import HttpResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import logging

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))


logger = logging.getLogger(__name__)
#logger.error('Something went wrong!')

print ('Code started')


secret = "f893df61-ee35-4a84-87fd-f0698b7438f7"
bot = telepot.Bot('408802721:AAHmVxkphGXoPWhQruHOLMDubWCkLk-vfCE')
bot.setWebhook("https://timeismoney.pythonanywhere.com/webhook", max_connections=1)
print('Weebhook was set')

@csrf_exempt
def telegram_webhook(request):
    print("Got a hook!")
    print("step1!")

    update = json.loads(request.body)
    print("step2!")
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

