from django.test import TestCase
from rest_framework.test import APITestCase
from questions.models import Question, Answer, Tag
from questions.forms import SearchForm
from user.models import User

from .question import (
    QuestionsViewTest, QuestionDetailViewTest, QuestionCreateViewTests
)
from .answer import AnswerViewTest
