from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.http import JsonResponse

from .forms import QuestionForm, AnswerForm, VoteForm, SearchForm
from .models import Question, Tag, Answer
import ipdb


class QuestionsView(View):
    """Questions view class."""

    def get(self, request):
        """Return a list of questions."""

        page = request.GET.get('page')
        questions = Question.objects.prefetch_related('tags')
        pagination = Paginator(questions, 20).page(page or 1)
        return render(request, 'index.html', {'questions': pagination})


class QuestionDetailView(View):
    """Question detail view."""

    def get(self, request, question_id):
        """Return detail information about question."""

        form = AnswerForm()
        question = get_object_or_404(Question, pk=question_id)
        return render(request, 'show.html', {
            'question': question,
            'form': form
        })


class QuestionCreateView(LoginRequiredMixin, View):
    """Question create view class."""

    login_url = '/sign_in/'

    def get(self, request):
        """Return form for the new question."""

        form = QuestionForm()
        return render(request, 'form.html', {'form': form})

    def post(self, request):
        """Create new question."""

        form = QuestionForm(request.POST, current_user=request.user)
        if form.submit():
            return redirect('questions_list')
        else:
            return render(request, 'form.html', {'form': form})


class TagsListView(View):
    """Tags list view class."""

    def get(self, request):
        """Return list of tags."""

        term = request.GET.get('term', '')
        tags = Tag.objects.filter(title__contains=term)
        data = serializers.serialize('json', tags)
        return JsonResponse({'tags': data})


class AnswerCreateView(LoginRequiredMixin, View):
    """Create answer for question."""

    login_url = '/sign_in/'

    def post(self, request, question_id=None):
        """Create answer for given question."""

        question = get_object_or_404(Question, pk=question_id)
        form = AnswerForm(
            request.POST, current_user=request.user, question=question
        )
        if form.submit():
            return redirect('question_detail', question_id=question.id)
        else:
            return render(request, 'show.html', {
                'question': question,
                'form': form
            })


class VoteAnswerView(LoginRequiredMixin, View):
    """Vote for answer view."""

    def post(self, request, question_id=None, answer_id=None):
        """Vote for question."""

        question = get_object_or_404(Answer, pk=answer_id)
        form = VoteForm(request.POST, current_user=request.user, obj=question)
        if form.submit():
            data = serializers.serialize('json', {'value': form.return_value})
            return JsonResponse(data)
        else:
            errors = serializers.serialize('json', {'errors': form.errors})
            return JsonResponse(errors)


class VoteQuestionView(LoginRequiredMixin, View):
    """Vote for answer view."""

    def post(self, request, question_id=None):
        """Vote for question."""

        question = get_object_or_404(Question, pk=question_id)
        form = VoteForm(request.POST, current_user=request.user, obj=question)
        if form.submit():
            data = serializers.serialize('json', {'value': form.return_value})
            return JsonResponse(data)
        else:
            errors = serializers.serialize('json', {'errors': form.errors})
            return JsonResponse(errors)


class SearchView(View):
    """Search of questions by query."""

    def get(self, request):
        """Return searched questions with template."""

        page = request.GET.get('page', 1)
        form = SearchForm(request.GET)
        form.submit()
        questions = form.objects
        pagination = Paginator(questions, 20).page(page)
        return render(request, 'index.html', {'questions': pagination})

    def post(self, request):
        """Submit base form."""

        form = SearchForm(request.POST)
        form.submit()
        cleaned_data = form.cleaned_data
        return redirect(
            reverse('questions_search') + '?type={}&query={}'.format(
                cleaned_data.get('type'), cleaned_data.get('query')
            )
        )
