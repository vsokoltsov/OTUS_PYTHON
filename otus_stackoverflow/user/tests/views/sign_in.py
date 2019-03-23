from . import TestCase, APITestCase, User, reverse
import ipdb


class SignInViewTest(TestCase):
    """Tests for sign in view class."""

    def test_success_receiving_of_form(self):
        """Test success receiving of the sign in form."""

        response = self.client.get('/sign_in')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SIGN IN FORM', response.content)


class SignInViewSetTest(APITestCase):
    """Tests for sign in viewset class."""

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

    def test_success_user_authentication(self):
        """Test success user authentication."""

        response = self.client.post('/api/v1/sign_in/', {
            'login': 'testlogin',
            'password': self.password
        }, format='json')
        self.assertEqual('token' in response.data, True)

    def test_failed_user_authentication(self):
        """Test failed user authentication."""

        response = self.client.post('/api/v1/sign_in/', {
            'login': 'example@mail.com',
            'password': ''
        }, format='json')
        self.assertEqual('errors' in response.data, True)
