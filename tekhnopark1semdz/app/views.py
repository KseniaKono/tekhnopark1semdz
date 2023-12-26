from datetime import datetime

from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_protect

from .forms import *
from .models import *


def get_top_tags():
    return Tag.objects.popular()[:5]


def paginate(objects, request, per_page=10):
    paginator = Paginator(objects, per_page)
    page_index = request.GET.get('page', 1)

    try:
        page_index = int(page_index)
    except ValueError:
        page_index = 1
    if page_index < 1:
        page_index = 1
    elif page_index > paginator.num_pages:
        page_index = paginator.num_pages
    current_page = paginator.page(page_index)
    correct_page_range = current_page.paginator.get_elided_page_range(page_index, on_each_side=3, on_ends=1)
    return {
        'page_info': current_page,
        'obj_list': current_page.object_list,
        'page_range': correct_page_range,
    }


# Create your views here.
def index(request):
    page = paginate(Question.objects.new(), request, 10)
    return render(request, 'index.html', {'questions': page['obj_list'], 'tags': get_top_tags(), 'page': page})


def hot(request):
    page = paginate(Question.objects.best(), request, 10)
    return render(request, 'index.html', {'questions': page['obj_list'], 'tags': get_top_tags(), 'page': page})


def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    page = paginate(Answer.objects.filter(question=question), request, 10)

    if request.method == "GET":
        form = AnswerForm()

    if request.method == "POST":
        form = AnswerForm(data=request.POST)
        if form.is_valid():
            answer = Answer.objects.create(question=question,
                                           author=request.user.profile,
                                           text=form.cleaned_data["text"])
            return redirect(request.path + '?page=' + str(answer.pk))
    return render(request, 'question.html',
                  {'answers': page['obj_list'], 'question': question, 'tags': get_top_tags(), 'page': page,
                   "form": form})


def tag(request, tag_title):
    questions = get_list_or_404(Question.objects.by_tag(tag_title))
    page = paginate(questions, request, 10)
    return render(request, 'tag.html',
                  {'tag_name': tag_title, 'questions': page['obj_list'], 'tags': get_top_tags(), 'page': page})


@login_required(redirect_field_name='continue', login_url='login')
def ask(request):
    if request.method == "GET":
        form = AskForm()

    if request.method == "POST":
        form = AskForm(data=request.POST)
        if form.is_valid():
            tags = form.save()
            question = Question.objects.create(author=request.user.profile,
                                               title=form.cleaned_data["title"],
                                               content=form.cleaned_data["text"],
                                               date_cr=datetime.today())
            for _tag in tags:
                question.tags.add(_tag)
                question.save()
            return redirect("question", question_id=question.id)
    return render(request, "ask.html", {'tags': get_top_tags(), "form": form})

@csrf_protect
def user_login(request):
    if request.method == 'GET':
        login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user is not None:
                login(request, user)
                next_page = request.GET.get('continue')
                if next_page is None:
                    next_page = reverse('index')
                return redirect(next_page)
            else:
                login_form.add_error(None, 'Wrong password')
                login_form.add_error('password', '')
        else:
            login_form.add_error(None, 'Something went wrong')
            login_form.add_error('password', '')
            login_form.add_error('username', '')
    return render(request, 'login.html', {'tags': get_top_tags(), "form": login_form})


@login_required(redirect_field_name='continue', login_url='login')
def user_logout(request):
    logout(request)
    return redirect(request.GET.get('continue'))


def signup(request):
    if request.method == 'GET':
        user_form = RegisterForm()
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            if user:
                 return redirect(reverse('index'))
            else:
                user_form.add_error(None, 'Error of user saving')
        else:
            user_form.add_error(None, 'Some data is not valid')

    return render(request, 'signup.html', {'tags': get_top_tags(), "form": user_form})


@login_required(redirect_field_name='continue', login_url='login')
def settings(request):
    if request.method == "GET":
        user = request.user
        settings_form = SettingsForm()
        if not user.is_authenticated:
            return HttpResponseForbidden()

    if request.method == "POST":
        settings_form = SettingsForm(data=request.POST)
        if settings_form.is_valid():
            user = request.user
            if user.is_authenticated:
                if settings_form.cleaned_data["nickname"] != user.username and settings_form.cleaned_data["nickname"] != "":
                    user.profile.nickname = settings_form.cleaned_data["nickname"]
                    user.profile.save()
                if settings_form.cleaned_data["email"] != user.email and settings_form.cleaned_data["email"] != "":
                    user.email = settings_form.cleaned_data["email"]
                    user.save()
    return render(request, "settings.html", {'tags': get_top_tags(), "form": settings_form})

