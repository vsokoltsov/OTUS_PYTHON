from questions.models import Question


def trending_questions(reques):
    """Return list of trending questions."""

    trending_questions = Question.objects.order_by('rate')
    return {'trending_questions': trending_questions}
