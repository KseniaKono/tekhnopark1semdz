from django.shortcuts import render
from django.core.paginator import Paginator

QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'content': f'Long lorem ipsum {i}'
    } for i in range(100)
]

ANSWERS = [
    {
        'id': i,
        'title': f'Answer {i}',
        'content': f'Answer Answer Answer {i}'
    } for i in range(100)
]

TAGS = [
    {'id': 1, 'title': 'VK'},
    {'id': 2, 'title': 'Voloshin'},
    {'id': 3, 'title': 'Python'},
    {'id': 4, 'title': 'CSS'},
    {'id': 5, 'title': 'Jango'},
]


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
    page = paginate(QUESTIONS, request, 10)
    return render(request, 'index.html', {'questions': page['obj_list'], 'tags': TAGS, 'page': page})


def hot(request):
    page = paginate(QUESTIONS, request, 10)
    return render(request, 'index.html', {'questions': page['obj_list'], 'tags': TAGS, 'page': page})


def question(request, question_id):
    page = paginate(ANSWERS, request, 10)
    item = QUESTIONS[question_id]
    return render(request, 'question.html',  {'answers': page['obj_list'], 'question': item, 'tags': TAGS, 'page': page})


def tag(request, tag_title):
    page = paginate(QUESTIONS, request, 10)
    for item in TAGS:
        if item['title'] == tag_title:
            return render(request, 'tag.html', {'tag': item, 'questions': page['obj_list'], 'tags': TAGS, 'page': page})


def ask(request):
    return render(request, 'ask.html', {'tags': TAGS})


def login(request):
    return render(request, 'login.html', {'tags': TAGS})


def signup(request):
    return render(request, 'signup.html', {'tags': TAGS})


def settings(request):
    return render(request, 'settings.html', {'tags': TAGS})
