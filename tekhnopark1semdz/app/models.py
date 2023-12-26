from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True, default="kotik.jpg", upload_to="avatar/%Y/%m/%d")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20)
    def __str__(self):
        return self.nickname


class TagManager(models.Manager):
    def count_uses(self):
        for tag in self.all():
            tag.uses_counter = tag.question_set.count()
            tag.save()

    def popular(self):
        self.count_uses()
        return self.order_by('-uses_counter')


class Tag(models.Model):
    title = models.CharField(max_length=100)
    uses_counter = models.PositiveIntegerField(default=0)

    objects = TagManager()

    def __str__(self):
        return self.title


class Like (models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, default=None, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(default=-1)
    content_object = GenericForeignKey()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.content_object.update_rating()


class QuestionManager(models.Manager):

    def new(self):
        return self.all().order_by('date_cr').reverse()
    def best(self):
        return self.all().order_by('rating').reverse()
    def by_tag(self, tag):
        return self.all().filter(tags__title=tag)
    def by_id(self, qid):
        return self.all().filter(id=qid)



class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)
    date_cr = models.DateTimeField(default=timezone.now)
    ans_counter = models.PositiveIntegerField(default=0)
    current_rating = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0, null=False)
    likes = GenericRelation(Like)
    objects = QuestionManager()

    def update_rating(self):
        likes_count = self.likes.filter(status=True).count()
        dislikes_count = self.likes.filter(status=False).count()
        self.rating = likes_count - dislikes_count
        self.save()
    def __str__(self):
        return self.title + ' id: ' + str(self.pk)


class AnswerManager(models.Manager):
    def hot(self):
        return self.all().order_by('rating').reverse()


class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField(max_length=2000)
    date_cr = models.DateTimeField(default=timezone.now)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    likes = GenericRelation(Like, null=True)
    objects = AnswerManager()
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.question.ans_counter = self.question.answer_set.count()
        self.question.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.question.ans_counter = self.question.answer_set.count()
        self.question.save()

    def update_rating(self):
        likes_count = self.likes.filter(status=True).count()
        dislikes_count = self.likes.filter(status=False).count()
        self.rating = likes_count - dislikes_count
        self.save()

    def __str__(self):
        return self.title + ' id: ' + str(self.pk)




