from . import TestCase, User, SignInForm


class SignInFormTest(TestCase):
    """Test cases for SignInForm class."""

    def setUp(self):
        """Set up testing dependencies."""

        password = 'testpassword'
        self.user = User.objects.create(
            email='example@mail.com',
            login='testlogin',
            password=password
        )
        self.user.set_password(password)
        self.user.save()
        self.params = {
            'login': self.user.login,
            'password': password
        }

    def test_success_validation(self):
        """Test success SignInForm validation."""

        form = SignInForm(data=self.params)
        self.assertTrue(form.is_valid())

    def test_failed_validation(self):
        """Test failed SignInForm validation."""

        form = SignInForm(data={})
        self.assertFalse(form.is_valid())

    def test_success_authentication(self):
        """Test success user authentication."""

        form = SignInForm(data=self.params)
        self.assertTrue(form.submit())

    def test_failed_authentication(self):
        """Test failed user authentication with empty data."""

        form = SignInForm(data={})
        self.assertFalse(form.submit())

    def test_failed_authentication_for_absent_user(self):
        """Test failed user authentication if user does not exist."""

        self.params['password'] = 'test12345'
        form = SignInForm(data=self.params)
        self.assertFalse(form.submit())
