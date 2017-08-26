from django.db import models


# Create your models here.
class Worker (models.Model):
    telegram_username = models.CharField(max_length=200)
    chat_id = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return self.telegram_username


class Project (models.Model):
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    workers = models.ManyToManyField(Worker, blank=True, default=None)

    def __str__(self):
        return self.title


class TimeSheet (models.Model):
    worker = models.ForeignKey(Worker)
    project = models.CharField(max_length=200, null=True, blank=True, default=None)
    details = models.CharField(max_length=200, null=True, blank=True, default=None)
    time_spent = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LoggingStep (models.Model):
    worker = models.ForeignKey(Worker)
    step = models.CharField(max_length=200, null=True, blank=True, default=0)
    project = models.CharField(max_length=200, null=True, blank=True, default=None)
    details = models.CharField(max_length=200, null=True, blank=True, default=None)
    time_spent = models.FloatField(null=True, blank=True, default=None)


class Reminder (models.Model):
    worker = models.ForeignKey(Worker)
    remind_at = models.DateTimeField(null=True, blank=True, default=None)
