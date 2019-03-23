from . import (
    viewsets, status, SignInForm, SignUpForm, jwt, Response
)


class SignInViewSet(viewsets.ViewSet):
    """Sign in viewset for API."""

    def create(self, request):
        """Sign in existing user."""

        form = SignInForm(request.data)
        if form.submit():
            token = jwt.encode_user(form.object)
            return Response({'token': token},
                            status=status.HTTP_200_OK)
        else:
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class SignUpViewSet(viewsets.ViewSet):
    """Sign up viewset for API."""

    def create(self, request):
        """Sign up an existing user."""

        form = SignUpForm(request.data)
        if form.submit():
            token = jwt.encode_user(form.object)
            return Response({'token': token},
                            status=status.HTTP_200_OK)
        else:
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)
