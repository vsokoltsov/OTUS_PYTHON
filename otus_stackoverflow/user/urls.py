from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from .views import (
    SignUpView, SignInView, ProfileView, SignOutView, ProfileEditView
)
from .api.v1 import SignInViewSet, SignUpViewSet

router = DefaultRouter()

router.register('v1/sign_in', SignInViewSet, base_name='api_v1_sign_in')
router.register('v1/sign_up', SignUpViewSet, base_name='api_v1_sign_up')

urlpatterns = [
    url(r'^sign_up', SignUpView.as_view(), name='sign_up'),
    url(r'^sign_in', SignInView.as_view(), name='sign_in'),
    url(r'^sign_out', SignOutView.as_view(), name='sign_out'),
    url(
        r'^users/(?P<user_id>[A-Za-z0-9]*)', ProfileView.as_view(),
        name='profile'
    ),
    url(
        r'^profile/settings', login_required(ProfileEditView.as_view()),
        name='edit_profile'
    ),
    url(r'api', include(router.urls)),
]
