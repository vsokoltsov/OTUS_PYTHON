from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import Error as DbError

from user.models import User
from .models import Question, Tag, Answer, Vote
import ipdb


class QuestionForm(forms.Form):
    """Question form class."""

    title = forms.CharField(max_length=255, strip=True, required=True)
    text = forms.CharField(strip=True, required=True)
    author_id = forms.fields.IntegerField(required=False)
    tags = []

    def __init__(self, data=None, **kwargs):
        """Initialize question form."""

        if data:
            self.tags = data.get('tags', None)
        if self.tags:
            self.tags = [item for item in self.tags.split(',')]
        self.current_user = kwargs.pop('current_user', None)
        super(QuestionForm, self).__init__(data, **kwargs)

    def clean(self):
        """Perform custom validation."""

        cleaned_data = self.cleaned_data
        if not self.current_user:
            raise forms.ValidationError('author_id is not present')

        if not self.tags:
            raise forms.ValidationError('tags are not present')
        cleaned_data['author_id'] = self.current_user.id
        cleaned_data['tags'] = self.tags
        return cleaned_data

    def submit(self):
        """Save question to database."""

        if not self.is_valid():
            return False

        try:
            with transaction.atomic():
                params = {}
                params['title'] = self.cleaned_data['title']
                params['text'] = self.cleaned_data['text']
                params['author_id'] = self.cleaned_data['author_id']
                self.object = Question.objects.create(**params)
                self.object.tags.set(self._tags_ids())
                return True
        except DbError as e:
            return False

    def _tags_ids(self):
        """Return tags ids."""

        tags = []
        for item in self.tags:
            tag, _ = Tag.objects.get_or_create(title=item)
            tags.append(tag.id)
        return tags


class AnswerForm(forms.Form):
    """Form for answer creation."""

    text = forms.CharField(strip=True, required=True)
    author_id = forms.fields.IntegerField(required=False)
    question_id = forms.fields.IntegerField(required=False)

    def __init__(self, data=None, **kwargs):
        """Initialize question form."""

        self.current_user = kwargs.pop('current_user', None)
        self.question = kwargs.pop('question', None)
        super(AnswerForm, self).__init__(data, **kwargs)

    def clean(self):
        """Perform custom validation."""

        cleaned_data = self.cleaned_data
        if not self.current_user:
            raise forms.ValidationError('author_id is not present')
        if not self.question:
            raise forms.ValidationError('question is not present')

        cleaned_data['author_id'] = self.current_user.id
        cleaned_data['question_id'] = self.question.id
        return cleaned_data

    def submit(self):
        """Save answer to database."""

        if not self.is_valid():
            return False

        try:
            with transaction.atomic():
                params = {}
                params['text'] = self.cleaned_data['text']
                params['author_id'] = self.cleaned_data['author_id']
                params['question_id'] = self.cleaned_data['question_id']
                self.object = Answer.objects.create(**params)
                return True
        except DbError as e:
            return False


class VoteForm(forms.Form):
    """Form for creating the vote for answer or question."""

    value = forms.IntegerField(required=True)
    content_type = forms.CharField(required=False)
    object_id = forms.IntegerField(required=False)

    UP = 1
    DEFAULT = 0
    DOWN = -1

    def __init__(self, data=None, **kwargs):
        """Initialize question form."""

        self.current_user = kwargs.pop('current_user', None)
        self.obj = kwargs.pop('obj', None)
        super(VoteForm, self).__init__(data, **kwargs)

    def clean(self):
        """Perform custom validation."""

        cleaned_data = self.cleaned_data
        if not self.current_user:
            raise forms.ValidationError('author_id is not present')
        if not self.obj:
            raise forms.ValidationError('object is not present')

        cleaned_data['author_id'] = self.current_user.id
        cleaned_data['obj'] = self.obj.id
        cleaned_data['content_type'] = ContentType.objects.get_for_model(
            self.obj.__class__
        )
        return cleaned_data

    def submit(self):
        """Save answer to database."""

        if not self.is_valid():
            return False

        try:
            with transaction.atomic():
                cleaned_data = self.cleaned_data
                try:
                    vote = Vote.objects.get(
                        object_id=self.obj.id,
                        content_type=cleaned_data.get('content_type')
                    )
                except ObjectDoesNotExist:
                    vote = None

                if not vote:
                    vote = (
                        Vote.objects.create(
                            value=cleaned_data.get('value'),
                            object_id=self.obj.id,
                            content_type=cleaned_data.get('content_type'))
                    )
                    self.return_value = vote.value
                    self.obj.rate += vote.value
                else:
                    if vote.value != cleaned_data.get('value'):
                        self.obj.rate -= vote.value
                        vote.delete()
                        self.return_value = self.DEFAULT
                    else:
                        self.return_value = vote.value
                self.obj.save()
                return True
        except DbError as e:
            return False


class SearchForm(forms.Form):
    """Search form class."""

    TAGS = 1
    QUESTIONS = 2
    AVAILABLE_MODELS = [TAGS, QUESTIONS]

    type = forms.IntegerField(required=True)
    query = forms.CharField(required=True, max_length=255)

    def __init__(self, data, **kwargs):
        """Overwerite default constructor."""

        super(SearchForm, self).__init__(data, **kwargs)
        self.objects = []

    def clean(self):
        """Perform custom validation."""

        cleaned_data = self.cleaned_data
        if cleaned_data.get('type') not in self.AVAILABLE_MODELS:
            raise forms.ValidationError('these type does not present')
        return cleaned_data

    def submit(self):
        """Search the given values."""

        if not self.is_valid():
            return False

        cleaned_data = self.cleaned_data
        if cleaned_data.get('type') == self.TAGS:
            try:
                tag = Tag.objects.get(title=cleaned_data.get('query'))
                self.objects = tag.question_set.all()
            except ObjectDoesNotExist:
                self.objects = []
        elif cleaned_data.get('type') == self.QUESTIONS:
            query = self.cleaned_data.get('query')
            self.objects = Question.objects.filter(
                Q(title__contains=query) | Q(text__contains=query)
            )
        return True
