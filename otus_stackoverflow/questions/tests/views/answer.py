from . import APITestCase, TestCase, Question, User, Answer


class AnswerViewTest(TestCase):
    """Answers view tests."""

    def setUp(self):
        """Set up test dependencies."""

        self.user = User.objects.create(
            login='vsokoltsov', email='example@mail.com'
        )
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )

    def test_receiving_form(self):
        """Test receiving answer form with detailed question view."""

        response = self.client.get('/questions/{}'.format(self.question.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes(self.question.title, 'utf-8'), response.content)


class AnswersViewSet(APITestCase):
    """Answers view set case."""

    def setUp(self):
        """Set up test dependencies."""

        self.user = User.objects.create(
            login='vsokoltsov', email='example@mail.com'
        )
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )
        self.answer = Answer.objects.create(
            text='TEXT ANSWER', author_id=self.user.id,
            question_id=self.question.id
        )

    def test_success_answers_receiving(self):
        """Test success receiving of question's answers."""

        response = self.client.get(
            '/api/v1/questions/{}/answers/'.format(self.question.id),
            format='json'
        )
        self.assertEqual(response.status_code, 200)
