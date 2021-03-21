from django.urls import include, path

from .views import classroom, students, teachers

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('readys2/<int:pk>/',teachers.readys_deleguer, name='readysD'),
    path('readys/<int:pk>/',teachers.readys_responsable, name='readysR'),
    path('ready/<int:pk>/',classroom.ready, name='ready'),
    path('success', classroom.success, name='succ'),
    path('error', classroom.error, name='err'),
    path('frm', teachers.StandardForm, name='StandardForm'),
    path('services', classroom.home2, name='home2'),
    path('', classroom.get_code, name='home'),
    path('media/',classroom.doc_view,name='aff_docs'),
    path('informations/<int:pk>',classroom.index,name='inf'),
    path('debloquer/<int:pk>',classroom.index2,name='inf2'),
    path('resp/<int:pk>/',teachers.responses_vue,name='aff_rep'),
    path('cp',teachers.responses_vue2,name='cp'),
    path('resp2/<int:pk>/',teachers.responses_vue3,name='aff_rep2'),
    path('students/', include(([
        path('', students.QuizListView.as_view(), name='quiz_list'),
        path('interests/', students.StudentInterestsView.as_view(), name='student_interests'),
        path('taken/', students.TakenQuizListView.as_view(), name='taken_quiz_list'),
        path('quiz/<int:pk>/', students.take_quiz, name='take_quiz'),

    ], 'classroom'), namespace='students')),

    path('teachers/', include(([
        path('', teachers.QuizListView.as_view(), name='quiz_change_list'),
        path('quiz/add/', teachers.QuizCreateView.as_view(), name='quiz_add'),
        path('quiz/<int:pk>/', teachers.QuizUpdateView.as_view(), name='quiz_change'),
        path('quiz/<int:pk>/delete/', teachers.QuizDeleteView.as_view(), name='quiz_delete'),
        path('quiz/<int:pk>/results/', teachers.QuizResultsView.as_view(), name='quiz_results'),
        path('quiz/<int:pk>/question/add/', teachers.question_add, name='question_add'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/', teachers.question_change, name='question_change'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', teachers.QuestionDeleteView.as_view(), name='question_delete'),
    ], 'classroom'), namespace='teachers')),
]+ static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)