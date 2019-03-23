from . import TestCase, APITestCase, User, reverse


class SignUpViewTest(TestCase):
    """Tests for sign up view class."""

    def test_success_receiving_of_form(self):
        """Test success receiving of the sign up form."""

        response = self.client.get('/sign_up')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SIGN UP FORM', response.content)


class SignInViewSetTest(APITestCase):
    """Tests for sign in viewset class."""

    def setUp(self):
        """Set up testing dependencies."""

        self.params = {
            'email': 'example@mail.com',
            'login': 'testlogin',
            'password': 'testpassword',
            'password_confirmation': 'testpassword'
        }

    def test_success_user_authentication(self):
        """Test success user authentication."""

        response = self.client.post(
            '/api/v1/sign_up/', self.params, format='json'
        )
        self.assertEqual('token' in response.data, True)

    def test_failed_user_authentication(self):
        """Test failed user authentication."""

        response = self.client.post(
            '/api/v1/sign_in/', {}, format='json'
        )
        self.assertEqual('errors' in response.data, True)
