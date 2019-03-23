from rest_framework import serializers
from questions.models import Question, Answer, Tag
from user.models import User
import ipdb


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer class."""

    class Meta:
        """Metaclass for serializer."""

        model = Tag
        fields = [
            'id',
            'title'
        ]


class UserSerializer(serializers.ModelSerializer):
    """User model serializer."""

    avatar = serializers.SerializerMethodField()

    class Meta:
        """Metaclass for serializer."""

        model = User
        fields = [
            'id',
            'login',
            'email',
            'avatar',
            'created_at',
        ]

    def get_avatar(self, obj):
        """Return avatar url."""

        try:
            return obj.avatar.url
        except ValueError:
            return None


class QuestionsSerializer(serializers.ModelSerializer):
    """Questions list serializer view."""

    author = UserSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        """Metaclass for serializer."""

        model = Question
        fields = [
            'id',
            'title',
            'text',
            'rate',
            'author',
            'created_at',
            'tags'
        ]


class AnswerSerializer(serializers.ModelSerializer):
    """Answers serializer class."""

    author = UserSerializer()

    class Meta:
        """Metaclass for serializer."""

        model = Answer
        fields = [
            'id',
            'text',
            'author',
            'is_correct',
            'created_at',
        ]
