from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


class Question(models.Model):
    """Question representation in the system."""

    title = models.CharField(max_length=255, null=False)
    text = models.TextField(null=False)
    rate = models.IntegerField(default=0)
    author = models.ForeignKey(
        'user.User', null=False, related_name='questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField('questions.Tag')
    votes = GenericRelation('questions.Vote')


class Tag(models.Model):
    """Tag representation in the system."""

    title = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    questions = models.ManyToManyField('questions.Question')


class Answer(models.Model):
    """Question's answer model representation."""

    text = models.TextField(null=False)
    rate = models.IntegerField(default=0)
    question = models.ForeignKey(
        'questions.Question', null=False, related_name='answers'
    )
    author = models.ForeignKey(
        'user.User', null=False, related_name='answers'
    )
    is_correct = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    votes = GenericRelation('questions.Vote')


class Vote(models.Model):
    """Vote model representation."""

    content_type = models.ForeignKey(ContentType, null=False)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    value = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
