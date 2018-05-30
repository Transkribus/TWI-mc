from django.contrib import admin

from apps.transkribus.models import User

admin.register(User)(admin.ModelAdmin)
