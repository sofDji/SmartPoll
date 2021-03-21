import util.crypto as c
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from ..decorators import teacher_required
from ..forms import BaseAnswerInlineFormSet, QuestionForm, TeacherSignUpForm
from ..models import Answer, Question, Quiz, User, Student, StudentAnswer, Subject, Secret, Module
from django.shortcuts import render
from django.template import Context
from django.db.models import Q
from datetime import date
from itertools import chain
from datetime import datetime 
from util.shamir import SSS
import json
from django.utils import timezone
import online_users.models
from datetime import timedelta
import os

def see_users():
  global users
  user_status = online_users.models.OnlineUserActivity.get_user_activities(timedelta(seconds=60))
  users = (user for user in  user_status)
  return users

def readys_deleguer(request,pk):
    users = see_users()
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.user.student:
        if quiz.deleguer_ready == request.user.username:
            quiz.results_ready = quiz.results_ready
        else:
            print(quiz.owner)
            if quiz.results_ready == 1:
              for u in users:
               print(quiz.owner)
               if quiz.owner == u.user:
                 print(quiz.owner)
                 quiz.deleguer_ready = request.user.username
                 quiz.results_ready = 2
               else :
                 quiz.responsable_ready = ''
            else:
              quiz.results_ready =+ 1
              quiz.deleguer_ready = request.user.username
    quiz.save()
    return redirect('cp')

def readys_responsable(request,pk):
    users = see_users()
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.user.is_teacher : 
        if quiz.responsable_ready == request.user.username:
            quiz.results_ready = quiz.results_ready
        else:
            quizs = get_object_or_404(Quiz, pk=pk, owner=request.user)
            quiz_specialité=quizs.subject
            delegue=Student.objects.filter(interests=quiz_specialité).filter(is_deleguer=True) #récuperer le délégué
            if quiz.results_ready == 1:
              for u in users:
                if delegue[0].user == u.user:
                 print(delegue[0].user)
                 quiz.responsable_ready = request.user.username
                 quiz.results_ready = 2
                else:
                 quiz.deleguer_ready = ''
            else : 
              quiz.results_ready =+ 1
              quiz.responsable_ready = request.user.username
            

    quiz.save()
    return redirect('teachers:quiz_results', quiz.pk)

class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('teachers:quiz_change_list')


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/teachers/quiz_change_list.html'

    def get_context_data(self, **kwargs):
        today = date.today()
        quizs = Quiz.objects.all()

        extra_context = {
            'today': today,
            'quizs' : quizs,
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('subject') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True)) 

        return queryset





@method_decorator([login_required, teacher_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name','date_fin', )
    template_name = 'classroom/teachers/quiz_add_form.html'

    def form_valid(self, form):
        today = date.today()
        quizs = Quiz.objects.filter(subject=self.request.user.teacher.subject)
        toufini = True
        for i in quizs:
            if i.date_fin > today:
                toufini = False

        if toufini == True:
            quiz = form.save(commit=False)
            quiz.owner = self.request.user
            quiz.subject = self.request.user.teacher.subject
            quiz.save()
            # la méthode qui va générer les clés + les stocker+genere les partages 
            quiz.partage_cle()
            messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
            return redirect('teachers:quiz_change', quiz.pk)
        else:
            return redirect('err')

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name','date_fin' )
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):

        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('teachers:quiz_change', kwargs={'pk': self.object.pk})


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_delete_confirm.html'
    success_url = reverse_lazy('teachers:quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        name = quiz.name+"_"+quiz.subject.specialite+"_"+quiz.subject.section
        os.remove("keys/"+name+"_private_key.pem")
        os.remove("keys/"+name+"_public_key.pem")
        os.remove("keys/"+name+"_sym_key.pem")
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_results.html'

    def get_context_data(self, **kwargs):
        today = date.today()
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('student__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score,
            'today': today
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

@login_required
def responses_vue2(request):
    interests = request.user.student.interests.all()
    quizs = Quiz.objects.filter(subject__in=interests)
    today = date.today()

    cntx = {
    'quizs' : quizs,
    'today' : today,
    }
    return render(request,'dele.html', cntx)

def responses_vue3(request,pk):
    quizs = get_object_or_404(Quiz, pk=pk)
    q = Question.objects.filter(quiz_id=quizs.id)
    secret=0
    name = quizs.name+"_"+quizs.subject.specialite+"_"+quizs.subject.section

    #recuperer KEY1 responsable vers delegue
    dlg = request.user # le delegue
    owner=quizs.owner # le responsable qui a créé le CP
    sec=Secret.objects.filter(partie=owner).filter(ref_quiz=quizs)[0] # tuple secret du responsable
    resp_secret=sec.key1 #Récuperer le secret du responsable
    
    sec_dlg =Secret.objects.filter(partie=dlg).filter(ref_quiz=quizs)[0] # tuple secret du delegue
    sec_dlg.key2=resp_secret # la mettre dans Key2 
    sec_dlg.save()

    jsonDec = json.decoder.JSONDecoder()
    shares=[]
    key1=c.sym_decrypter_msg(sec_dlg.key1, c.get_sym_key(name))
    shares.append(jsonDec.decode(key1))
    key2=c.sym_decrypter_msg(sec_dlg.key2, c.get_sym_key(name))
    shares.append(jsonDec.decode(key2))

    secret = SSS.reconstructSecret(None,shares)
    print("final key to decrypt files ="+str(secret))

    # nom du fichier
    sk = c.get_sec_key(name,secret)

	# Calculer les statistiques
    taken_quizzes2 = quizs.taken_quizzes.select_related('student__user').order_by('-date')
    total_taken_quizzes2 = taken_quizzes2.count()
	

    for i in range(0,len(q)):
        answerlist = Answer.objects.filter(question_id=q[i].id)
        l=0
        stu_answers = StudentAnswer.objects.filter(quiz_id=quizs.id).filter(question_id=q[i].id)
        for j in answerlist:
            j.counter = 0.0
            for b in stu_answers:
          # decrypter la réponse
                answer = c.decrypter_msg(b.answer, sk)
                if answer == j.text: 
                    j.counter += 1.0
            j.counter = j.counter * 100 / total_taken_quizzes2
            j.save()


    answer2 = Answer.objects.filter(question_id=q[0].id)
    for i in range(1,len(q)):
        b = Answer.objects.filter(question_id=q[i].id)
        answer2 = chain(answer2,b) 


    cn = {'cpt' : total_taken_quizzes2,'l' : l,'quiz' : quizs,'answers' : answer2}
    return render(request,'rep.html', cn)
@login_required
@teacher_required
def responses_vue(request,pk):
    quizs = get_object_or_404(Quiz, pk=pk, owner=request.user)
    q = Question.objects.filter(quiz_id=quizs.id)
    secret=0
    name = quizs.name+"_"+quizs.subject.specialite+"_"+quizs.subject.section

    #echange des KEY1 KEY2 delg vers resp
    quiz_specialité=quizs.subject
    delegue=Student.objects.filter(interests=quiz_specialité).filter(is_deleguer=True) #récuperer le délégué
    dlg=delegue[0].user
    dlg_secret=Secret.objects.filter(partie=dlg).filter(ref_quiz=quizs)[0].key1
    owner=quizs.owner
    sec=Secret.objects.filter(partie=owner).filter(ref_quiz=quizs)[0]
    sec.key2=dlg_secret
    sec.save()

    jsonDec = json.decoder.JSONDecoder()
    shares=[]
    key1=c.sym_decrypter_msg(sec.key1, c.get_sym_key(name))
    shares.append(jsonDec.decode(key1))
    key2=c.sym_decrypter_msg(sec.key2, c.get_sym_key(name))
    shares.append(jsonDec.decode(key2))
    secret = SSS.reconstructSecret(None,shares)

    # récuperer le clé privé 
    sk = c.get_sec_key(name,secret)

    
    taken_quizzes2 = quizs.taken_quizzes.select_related('student__user').order_by('-date')
    total_taken_quizzes2 = taken_quizzes2.count()
    for i in range(0,len(q)):
        answerlist = Answer.objects.filter(question_id=q[i].id)
        l=0
        stu_answers = StudentAnswer.objects.filter(quiz_id=quizs.id).filter(question_id=q[i].id)
        for j in answerlist:
            j.counter = 0.0
            for b in stu_answers:
          # decrypter la réponse
                answer = c.decrypter_msg(b.answer, sk)
                if answer == j.text: 
                    j.counter += 1.0
            j.counter = j.counter * 100 / total_taken_quizzes2
            j.save()



    answer2 = Answer.objects.filter(question_id=q[0].id)
    for i in range(1,len(q)):
        b = Answer.objects.filter(question_id=q[i].id)
        answer2 = chain(answer2,b) 



    cn = {'cpt' : total_taken_quizzes2,'l' : l,'quiz' : quizs,'answers' : answer2}

    return render(request,'rep.html', cn)

@login_required
@teacher_required
def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('teachers:question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'classroom/teachers/question_add_form.html', {'quiz': quiz, 'form': form})


@login_required
@teacher_required
def question_change(request, quiz_pk, question_pk):
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `quiz` and
    # `question` we are making sure only the owner of the quiz can
    # change its details and also only questions that belongs to this
    # specific quiz can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('teachers:quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'classroom/teachers/question_change_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'classroom/teachers/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('teachers:quiz_change', kwargs={'pk': question.quiz_id})

@login_required
@teacher_required
def StandardForm(request):
    subject = request.user.teacher.subject
    #modules
	#['CRYPTOGRAPHIE','TUNNING ET BASE DE DONNEES','SECURITE RESEAUX','SECURITE RESEAUX SANS FIL','SECURITE SYSTEMES']
    q = Module.objects.filter(subject = subject)
    t = ['Structure du plan de cours,objectifs','Methodes pédagogiques, clarté de presentation','Evaluation des apprentissages','References bibliographiques','Globalement, comment evaluez-vous cet enseignement']
    e = ['inssufisant','Tres bon','bon','tres inssufisant']
    nomCP = "CP"+subject.specialite+subject.section
    n = Quiz.objects.create(owner=request.user, name=nomCP, subject=request.user.teacher.subject, date_fin='2020-12-30')
    n.partage_cle()
    n.save()
    for j in q:
        for i in t:
            b = Question.objects.create(quiz=n, text = j.nom +":"+i)
            for c in range(0,len(e)):
                Answer.objects.create(question = b, text = e[c], is_correct=False, counter = 0)
                e[c] = e[c] + ' ';
    return redirect('teachers:quiz_change_list')
