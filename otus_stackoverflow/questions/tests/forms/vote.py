from . import (TestCase, Question, User, Answer, Vote, VoteForm)
from django.contrib.contenttypes.models import ContentType
import ipdb


class VoteFormTest(TestCase):
    """Tests for VoteForm class."""

    def setUp(self):
        """Set up test dependencies."""

        self.user = User.objects.create(
            login='testlogin', email="example@mail.com"
        )
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )
        self.answer = Answer.objects.create(
            text='Answer Text', question_id=self.question.id,
            author_id=self.user.id
        )
        self.params = {
            'value': VoteForm.UP
        }

    def test_success_validation_for_question(self):
        """Succesfully validates form for question instance."""

        form = VoteForm(self.params, current_user=self.user, obj=self.question)
        self.assertTrue(form.is_valid())

    def test_success_validation_for_answer(self):
        """Successfully validates form for answer instance."""

        form = VoteForm(self.params, current_user=self.user, obj=self.answer)
        self.assertTrue(form.is_valid())

    def test_failed_validation(self):
        """Test failed validation for vote form."""

        form = VoteForm()
        self.assertFalse(form.is_valid())

    def test_success_vote_creation(self):
        """Test success creation of the vote."""

        votes_count = Vote.objects.count()
        form = VoteForm(self.params, current_user=self.user, obj=self.answer)
        form.submit()
        self.assertEqual(Vote.objects.count(), votes_count + 1)

    def test_failed_vote_creation(self):
        """Test failed vote creation."""

        votes_count = Vote.objects.count()
        form = VoteForm()
        form.submit()
        self.assertEqual(Vote.objects.count(), votes_count)

    def test_success_response_if_vote_already_exist(self):
        """Test success response if vote exist and matches the current one."""

        Vote.objects.create(content_type=ContentType.objects.get_for_model(
            Answer
        ), value=1, object_id=self.answer.id)
        votes_count = Vote.objects.count()
        form = VoteForm(self.params, current_user=self.user, obj=self.answer)
        form.submit()
        self.assertEqual(Vote.objects.count(), votes_count)

    def test_deleting_vote_if_values_are_different(self):
        """Test deletion of the vote if values are different."""

        Vote.objects.create(content_type=ContentType.objects.get_for_model(
            Answer
        ), value=-1, object_id=self.answer.id)
        votes_count = Vote.objects.count()
        form = VoteForm(self.params, current_user=self.user, obj=self.answer)
        form.submit()
        self.assertEqual(Vote.objects.count(), votes_count - 1)
