from . import TestCase, Question, User, QuestionForm
import ipdb


class QuestionFormTest(TestCase):
    """Test cases for QuestionForm class."""

    def setUp(self):
        """Set up testing dependencies."""

        self.user = User.objects.create(
            login='testlogin', email="example@mail.com"
        )
        self.params = {
            'title': 'Test title',
            'text': 'Test text',
            'tags': 'aaaa, bbbbb, cccc'
        }

    def test_success_form_validation(self):
        """Test success form validation."""

        form = QuestionForm(self.params, current_user=self.user)
        self.assertTrue(form.is_valid())

    def test_failed_form_validation(self):
        """Test failed form validation."""

        form = QuestionForm()
        self.assertFalse(form.is_valid())

    def test_failed_validation_author_is_absent(self):
        """Test failed form validation if current user does not present."""

        form = QuestionForm()
        self.assertFalse(form.is_valid())

    def test_success_question_creation(self):
        """Test success question creation."""

        questions_count = Question.objects.count()
        form = QuestionForm(self.params, current_user=self.user)
        form.submit()
        self.assertEqual(Question.objects.count(), questions_count + 1)

    def test_failed_question_creation(self):
        """Test failed question creation."""

        questions_count = Question.objects.count()
        form = QuestionForm(self.params)
        form.submit()
        self.assertEqual(Question.objects.count(), questions_count)
