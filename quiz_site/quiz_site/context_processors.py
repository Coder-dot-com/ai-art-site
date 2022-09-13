 
from quiz_backend.models import Quiz


def main_quiz(request):

    try:
        quiz = Quiz.objects.filter(quiz_type="setUserPreferences")[0]
    except:
        quiz = None


    return dict(main_quiz=quiz)

