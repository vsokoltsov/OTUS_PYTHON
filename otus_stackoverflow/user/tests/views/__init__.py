from django.test import TestCase, TransactionTestCase
from rest_framework.test import APITestCase
from user.models import User
from django.core.urlresolvers import reverse

from .sign_up import SignUpViewTest
from .sign_in import SignInViewTest
from .profile_edit import ProfileEditViewTest
