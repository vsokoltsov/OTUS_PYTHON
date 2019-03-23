from . import TestCase, User, reverse


class ProfileEditViewTest(TestCase):
    """Tests for ProfileEditView class."""

    def setUp(self):
        """Set up test dependencies."""

        self.password = 'testpassword'
        self.user = User.objects.create(
            login='vsokoltsov', email='example@mail.com'
        )
        self.user.set_password(self.password)
        self.user.save()

    def test_abscence_of_route_if_user_is_not_authorized(self):
        """Test failed page receiving if user is not authorized."""

        response = self.client.get('/profile/settings/')
        self.assertEqual(response.status_code, 302)

    def test_success_receiving_of_form(self):
        """Test success receiving of the profile edit form."""

        self.client.login(
            username=self.user.login, password=self.password
        )
        response = self.client.get('/profile/settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Update user', response.content)
