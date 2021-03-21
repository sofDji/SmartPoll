import util.crypto as c
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from ..decorators import student_required
from ..forms import StudentInterestsForm, StudentSignUpForm, TakeQuizForm
from ..models import Quiz, Student, TakenQuiz, User, Answer, Question, Teacher
from datetime import date





class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:quiz_list')


@method_decorator([login_required, student_required], name='dispatch')
class StudentInterestsView(UpdateView):
    model = Student
    form_class = StudentInterestsForm
    template_name = 'classroom/students/interests_form.html'
    success_url = reverse_lazy('students:quiz_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)


@method_decorator([login_required, student_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/students/quiz_list.html'

    def get_queryset(self):
        today = date.today()
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .exclude(date_fin__lt = today ) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0) 
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'classroom/students/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset



@login_required
@student_required
def take_quiz(request, pk):
    today = date.today()
    quiz = get_object_or_404(Quiz, pk=pk)
    if (quiz.date_fin < today):
        return render(request, 'error.html',)
    else:

        q = Question.objects.filter(quiz_id=quiz.id)
        student = request.user.student

        if student.quizzes.filter(pk=pk).exists():
            return render(request, 'students/taken_quiz.html')

        total_questions = quiz.questions.count()
        unanswered_questions = student.get_unanswered_questions(quiz)
        total_unanswered_questions = unanswered_questions.count()
        progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
        question = unanswered_questions.first()

        if request.method == 'POST':
            form = TakeQuizForm(question=question, data=request.POST)
            if form.is_valid():
                with transaction.atomic():
                    
                    student_answer = form.save(commit=False)
                    student_answer.student = student
                    student_answer.quiz = quiz
                    student_answer.question = question
                    # recuperer la réponse de l'etudiant
                    answer_ch = Answer.objects.filter(id = request.POST['answer'])[0]
                    # récuperer la clé de chiffrement
                    name = quiz.name+"_"+quiz.subject.specialite+"_"+quiz.subject.section
                    public_key = c.get_pub_key(name)
                   
                    # crypter la réponse
                    answer_ch = c.crypter_msg(answer_ch.text, public_key )
                    student_answer.answer = answer_ch
                    student_answer.save()
                    if student.get_unanswered_questions(quiz).exists():
                       
                        return redirect('students:take_quiz', pk)
                    else:
                        TakenQuiz.objects.create(student=student, quiz=quiz, score=0.0)
                        return redirect('students:quiz_list')
        else:
            form = TakeQuizForm(question=question)

        return render(request, 'classroom/students/take_quiz_form.html', {
            'quiz': quiz,
            'question': question,
            'form': form,
            'progress': progress,
        })



def update_project_filter(request):
    selected_project_id = project_form.cleaned_data["Project_Name"].id
    request.session['selected_project_id'] = selected_project_id

def update_project(request):
    selected_project_id = request.session.get('selected_project_id')
