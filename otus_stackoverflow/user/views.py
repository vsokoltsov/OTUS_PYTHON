from django.views import View
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from .forms import SignUpForm, SignInForm, ProfileEditForm
from .models import User


class SignUpView(View):
    """Sign up view class."""

    def get(self, request):
        """Return sign up form."""
        form = SignUpForm()
        return self._render_form(request, form)

    def post(self, request):
        """Create new user."""

        form = SignUpForm(request.POST)
        if form.submit():
            login(request, form.object)
            return redirect('profile', user_id=form.object.id)
        else:
            return self._render_form(request, form)

    def _render_form(self, request, form):
        """Render sign up form with form instance."""

        return render(request, 'authorization/sign_up.html', {'form': form})


class SignInView(View):
    """Sign in view class."""

    def get(self, request):
        """Return sign in form."""

        form = SignInForm()
        return self._render_form(request, form)

    def post(self, request):
        """Authenticate presented user."""

        form = SignInForm(request.POST)
        if form.submit():
            login(request, form.object)
            return redirect('profile', user_id=form.object.id)
        else:
            return self._render_form(request, form)

    def _render_form(self, request, form):
        """Render sign in form with form instance."""

        return render(request, 'authorization/sign_in.html', {'form': form})


class SignOutView(View):
    """Sign out view class."""

    def post(self, request):
        """Sign out current user."""

        if request.user.is_authenticated:
            logout(request)

        return redirect('sign_in')


class ProfileView(View):
    """Return user's profile."""

    def get(self, request, user_id=None):
        """Return partial with user's info."""

        user = get_object_or_404(User, pk=user_id)
        return render(request, 'profile.html', {'user_data': user})


class ProfileEditView(View):
    """Update current user's information."""

    def get(self, request):
        """Return partial with user's info."""

        form = ProfileEditForm(instance=request.user)
        return self._render_form(request, form)

    def post(self, request):
        """Update user's information."""

        form = ProfileEditForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.submit():
            return redirect('profile', user_id=form.instance.id)
        else:
            return self._render_form(request, form)

    def _render_form(self, request, form):
        """Render edit form with form instance."""

        return render(request, 'edit.html', {'form': form})
