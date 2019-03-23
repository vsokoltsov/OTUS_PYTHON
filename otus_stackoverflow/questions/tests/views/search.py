from . import APITestCase, Question, User, Answer, Tag, SearchForm


class SearchViewSetTests(APITestCase):
    """SearchViewSet tests."""

    def setUp(self):
        """Set up testing dependencies."""

        self.password = 'testpassword'
        self.user = User.objects.create(
            email='example@mail.com',
            login='testlogin',
            password=self.password
        )
        self.user.set_password(self.password)
        self.user.save()
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )
        self.tag = Tag.objects.create(title='TAG')
        self.question.tags.set([self.tag.id])
        self.params = {
            'type': SearchForm.TAGS
        }

    def test_searching_of_questions(self):
        """Tests for searching questions."""

        response = self.client.get(
            '/api/v1/questions/search/?type={}&query={}'.format(
                SearchForm.QUESTIONS, self.question.title
            ),
            format='json'
        )
        self.assertEqual('questions' in response.data, True)
