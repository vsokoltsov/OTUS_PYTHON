from . import TestCase, Question, Answer, User, AnswerForm


class AnswerFormTest(TestCase):
    """Tests for AnswerForm class."""

    def setUp(self):
        """Set up testing dependencies."""

        self.user = User.objects.create(
            login='testlogin', email="example@mail.com"
        )
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )
        self.params = {
            'text': 'Test text'
        }

    def test_success_form_validation(self):
        """Test success form validation."""

        form = AnswerForm(
            self.params, current_user=self.user, question=self.question
        )
        self.assertTrue(form.is_valid())

    def test_failed_form_validation(self):
        """Test failed form validation."""

        form = AnswerForm()
        self.assertFalse(form.is_valid())

    def test_failed_form_validation_without_user(self):
        """Test failed form validation of user does not present."""

        form = AnswerForm(self.params, question=self.question)
        self.assertFalse(form.is_valid())

    def test_success_answer_creation(self):
        """Test success answer creation."""

        answers_count = Answer.objects.count()
        form = AnswerForm(
            self.params, current_user=self.user, question=self.question
        )
        form.submit()
        self.assertEqual(Answer.objects.count(), answers_count + 1)

    def test_failed_answer_creation(self):
        """Test failed answer creation."""

        answers_count = Answer.objects.count()
        form = AnswerForm()
        form.submit()
        self.assertEqual(Answer.objects.count(), answers_count)
