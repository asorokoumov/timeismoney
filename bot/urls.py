from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^webhook$',
        views.telegram_webhook, name='telegram_webhook'),

]