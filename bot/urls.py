from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^f893df61-ee35-4a84-87fd-f0698b7438f7/408802721:AAHmVxkphGXoPWhQruHOLMDubWCkLk-vfCE/$',
        views.telegram_webhook, name='telegram_webhook'),

]