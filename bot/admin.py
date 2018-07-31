from django.contrib import admin

# Register your models here.
from .models import Worker, Project, TimeSheet, LoggingStep, Reminder

admin.site.register(Worker)
admin.site.register(Project)
admin.site.register(TimeSheet)
admin.site.register(LoggingStep)
admin.site.register(Reminder)
