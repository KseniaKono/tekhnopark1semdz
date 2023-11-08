from django.shortcuts import render
from django.core.paginator import Paginator

QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'content': f'Long lorem ipsum {i}'
    } for i in range(100)
]


def paginate(objects, page, per_page=15):
    paginator = Paginator(objects, per_page)

    return paginator.page(page)

# Create your views here.
def index(request):
    page = request.GET.get('page', 1)
    return render(request, '.html', {'questions': paginate(QUESTIONS, page)})


def question(request, question_id):
    item = QUESTIONS[question_id]
    return render(request, '.html', {'question': item})
