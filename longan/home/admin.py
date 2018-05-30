from django.contrib import admin

from apps.transkribus.models import User
from django.contrib.auth.admin import GroupAdmin, UserAdmin

admin.site.register(User, UserAdmin)
