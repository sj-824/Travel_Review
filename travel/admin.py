from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AnimeModel, ReviewModel,User_Profile,Access_Counter

# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(AnimeModel)
admin.site.register(ReviewModel)
admin.site.register(User_Profile)
admin.site.register(Access_Counter)
