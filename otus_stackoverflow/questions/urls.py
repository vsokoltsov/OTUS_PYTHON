from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from .views import (
    QuestionsView, QuestionCreateView, QuestionDetailView,
    TagsListView, AnswerCreateView, VoteAnswerView, VoteQuestionView,
    SearchView
)

from .api.v1 import QuestionViewSet

router = DefaultRouter()
router.register(
    'v1/questions', QuestionViewSet,
    base_name='api_v1_questions'
)

urlpatterns = [
    url(r'^$', QuestionsView.as_view(), name='root_path'),
    url(
        r'^questions$', QuestionsView.as_view(), name='questions_list'
    ),
    url(
        r'^questions/new$', QuestionCreateView.as_view(), name='new_question'
    ),
    url(
        r'^questions/search$', SearchView.as_view(), name="questions_search"
    ),
    url(
        r'^questions/(?P<question_id>[A-Za-z0-9]*)$',
        QuestionDetailView.as_view(), name='question_detail'
    ),
    url(
        r'^questions/(?P<question_id>[A-Za-z0-9]*)/answers$',
        AnswerCreateView.as_view(), name="new_answer"
    ),
    url(
        r'^questions/(?P<question_id>[A-Za-z0-9]*)/vote$',
        VoteQuestionView.as_view(), name="vote_question"
    ),
    url(
        r'^questions/(?P<question_id>[A-Za-z0-9]*)/answers/' +
        r'(?P<answer_id>[A-Za-z0-9]*)/vote$',
        VoteAnswerView.as_view(), name="vote_answer"
    ),
    url(
        r'^tags$', TagsListView.as_view(), name='tags_list'
    ),
    url(r'api', include(router.urls)),
]
