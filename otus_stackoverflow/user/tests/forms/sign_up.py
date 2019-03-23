from . import TestCase, User, SignUpForm


class SignUpFormTest(TestCase):
    """SignUpForm tests."""

    def setUp(self):
        """Set up testing environment."""
        self.params = {
            'email': 'example@mail.com',
            'login': 'testlogin',
            'password': 'testpassword',
            'password_confirmation': 'testpassword'
        }

    def test_success_validation(self):
        """Test success from validation."""

        form = SignUpForm(data=self.params)
        self.assertTrue(form.is_valid())

    def test_failed_validation(self):
        """Test failed validation."""

        form = SignUpForm(data={})
        self.assertFalse(form.is_valid())

    def test_new_user_creation(self):
        """Test success creation of the user."""

        users_count = User.objects.count()
        form = SignUpForm(data=self.params)
        form.submit()
        self.assertEqual(User.objects.count(), users_count + 1)

    def test_failed_user_creation(self):
        """Test not creating the user instance."""

        users_count = User.objects.count()
        form = SignUpForm(data={})
        form.submit()
        self.assertEqual(User.objects.count(), users_count)
