from . import (
    viewsets, status, Response, SearchForm, QuestionsSerializer,
    Paginator, get_object_or_404, Question, detail_route, list_route,
    AnswerSerializer
)


class QuestionViewSet(viewsets.ViewSet):
    """Search viewset API view."""

    @list_route(methods=['get'])
    def search(self, request):
        """Return searched questions."""

        params = request.query_params
        page = params.get('page', 1)
        form = SearchForm(params)
        form.submit()
        questions = form.objects
        pagination = Paginator(questions, 20).page(page)
        serializer = QuestionsSerializer(pagination, many=True)
        return Response({'questions': serializer.data},
                        status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Return a question information."""

        question = get_object_or_404(Question, pk=pk)
        serializer = QuestionsSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def answers(self, request, pk=None):
        """Return list of answers."""

        question = get_object_or_404(Question, pk=pk)
        answers = Question.objects.prefetch_related(
            'answers', 'answers__author'
        ).get(id=question.id).answers.all()
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
