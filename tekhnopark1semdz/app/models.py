from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=15)

    def __str__(self):
        return self.nickname
class Tag(models.Model):
    name = models.CharField(max_length=100)
    uses_counter = models.PositiveIntegerField(default=0)

    #objects = TagManager()

    def __str__(self):
        return self.name
class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)
    date_time = models.DateTimeField()
    ans_counter = models.PositiveIntegerField(default=0)
    current_rating = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)

    #objects = QuestionManager()

    def __str__(self):
        return self.title

class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    parent = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField(max_length=2000)
    date_time = models.DateTimeField()
    is_correct = models.BooleanField(default=False)
    current_rating = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.parent.ans_count = self.parent.answer_set.count()
        self.parent.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.parent.ans_count = self.parent.answer_set.count()
        self.parent.save()

    def __str__(self):
        return self.title

