from . import ProfileEditForm, TestCase, User


class ProfileEditFormTests(TestCase):
    """Tests for ProfileEditForm tests."""

    def setUp(self):
        """Set up testing dependencies."""

        self.user = User.objects.create(
            email='testemail@mail.com',
            login='testlogin'
        )
        self.params = {'email': 'newemail@test.com'}

    def test_success_form_validation(self):
        """Test success form validation."""

        form = ProfileEditForm(data=self.params, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_failed_form_validation(self):
        """Test failed form validation."""

        form = ProfileEditForm(data={}, instance=self.user)
        self.assertFalse(form.is_valid())

    def test_update_user_information(self):
        """Test success user information update."""

        form = ProfileEditForm(data=self.params, instance=self.user)
        form.submit()
        self.user.refresh_from_db()
        self.assertEqual(self.params['email'], self.user.email)
