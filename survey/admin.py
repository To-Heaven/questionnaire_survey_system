from django.contrib import admin

from survey import models


admin.site.register(models.Admin)
admin.site.register(models.Answer)
admin.site.register(models.Department)
admin.site.register(models.Question)
admin.site.register(models.Questionnaire)
admin.site.register(models.Choice)
admin.site.register(models.Employee)
