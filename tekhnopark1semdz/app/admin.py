from django.contrib import admin

# Register your models here.
from .models import Profile, Question, Answer, Tag, Like
from django.contrib import admin



admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Like)