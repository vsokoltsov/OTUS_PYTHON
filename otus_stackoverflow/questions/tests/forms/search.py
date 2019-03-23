from . import TestCase, Question, Tag, User, SearchForm
import ipdb


class SearchFormTest(TestCase):
    """Tests for the SearchForm class."""

    def setUp(self):
        """Set up testing dependencies."""

        self.user = User.objects.create(
            login='testlogin', email="example@mail.com"
        )
        self.question = Question.objects.create(
            title='Title', text='Text', author_id=self.user.id
        )
        self.tag = Tag.objects.create(title='TAG')
        self.question.tags.set([self.tag.id])
        self.params = {
            'type': SearchForm.TAGS
        }

    def test_success_form_validtion(self):
        """Test success form validation."""

        self.params['query'] = self.tag.title
        form = SearchForm(self.params)
        self.assertTrue(form.is_valid())

    def test_failed_form_validation(self):
        """Test failed form validation."""

        form = SearchForm(self.params)
        self.assertFalse(form.is_valid())

    def test_receiving_questions_by_tags(self):
        """Test success receiving questions by tags."""

        self.params['query'] = self.tag.title
        form = SearchForm(self.params)
        form.submit()
        self.assertEqual(
            [item.id for item in form.objects],
            [self.question.id]
        )

    def test_receiving_questions_by_query(self):
        """Test success receiving questions."""

        self.params['query'] = self.question.title
        self.params['type'] = SearchForm.QUESTIONS
        form = SearchForm(self.params)
        form.submit()
        self.assertEqual(
            [item.id for item in form.objects],
            [self.question.id]
        )
