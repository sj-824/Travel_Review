from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AnimeModel, ReviewModel

# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(AnimeModel)
admin.site.register(ReviewModel)
