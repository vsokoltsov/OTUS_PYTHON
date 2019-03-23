from . import APITestCase, TestCase, Question, User


class QuestionsViewTest(TestCase):
    """Tests for questions list view."""

    def setUp(self):
        """Set up test dependencies."""

        self.user = User.objects.create(
            login='vsokoltsov', email='example@mail.com'
        )
        question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )
        self.questions = [question]

    def test_success_receiving_of_list(self):
        """Test success receiving of questions list."""

        response = self.client.get('/questions')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'QUESTIONS LIST', response.content)


class QuestionDetailViewTest(TestCase):
    """Tests for question detail info."""

    def setUp(self):
        """Set up test dependencies."""

        self.user = User.objects.create(
            login='vsokoltsov', email='example@mail.com'
        )
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )

    def test_success_receiving_of_detail(self):
        """Test success receiving of question detail view."""

        response = self.client.get('/questions/{}'.format(self.question.id))
        self.assertEqual(
            response.status_code, 200
        )
        self.assertIn(bytes(self.question.title, 'utf-8'), response.content)


class QuestionCreateViewTests(TestCase):
    """Tests for question create info."""

    def setUp(self):
        """Set up test dependencies."""

        self.password = 'testpassword'
        self.user = User.objects.create(
            login='vsokoltsov', email='example@mail.com'
        )
        self.user.set_password(self.password)
        self.user.save()

    def test_form_rendering(self):
        """Test rendering of question form."""

        self.client.login(username=self.user.login, password=self.password)
        response = self.client.get('/questions/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Save question', response.content)


class QuestionViewSet(APITestCase):
    """Tests for question viewset."""

    def setUp(self):
        """Set up test dependencies."""

        self.user = User.objects.create(
            login='vsokoltsov', email='example@mail.com'
        )
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )

    def test_success_receiving_of_question(self):
        """Test success question receiving."""

        response = self.client.get(
            '/api/v1/questions/{}/'.format(
                self.question.id
            ),
            format='json'
        )
        self.assertEqual(response.status_code, 200)
