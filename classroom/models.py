from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.conf import settings
from passgen import passgen
import util.crypto as c
import util.shamir as sss
import json

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)



class Subject(models.Model):
    departement = models.CharField(max_length=30)
    annee = models.CharField(max_length=10)
    specialite = models.CharField(max_length=10)
    section = models.CharField(max_length=10)
    color = models.CharField(max_length=7, default='#007bff')



    def __str__(self):
        return '{}  {}  {}  {}'.format(self.departement, self.annee, self.specialite,self.section)

    def get_html_badge(self):
        departement = escape(self.departement)
        annee = escape(self.annee) 
        specialite = escape(self.specialite)
        section = escape(self.section)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, specialite)
        return mark_safe(html)


class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    date_fin = models.DateField(auto_now_add=False, blank=True, null=True)
    #test if the both parties are ready to view results
    results_ready=models.IntegerField(default=0)
    responsable_ready = models.CharField(max_length=20,default='', blank=True)
    deleguer_ready = models.CharField(max_length=20,default='',  blank=True)

    def __str__(self):
        return self.name
        # la méthode qui va générer les clé privé + publique, 
        # les stocker + partager la clé secrete sur les 2 parties
    def partage_cle(self):
        
        sk, pk, fk = c.generer_cles()
        # Les stocker dans un fichier qui a comme nom: nomQuiz_spécialité_section_public/private_key.pem
        name = self.name+"_"+self.subject.specialite+"_"+self.subject.section
        passwd=passgen(length=11, punctuation=False, digits=True, letters=True, case='both')
        c.store_keys(sk,pk,fk,name,passwd.encode())

        #shamir
        shamir=sss.SSS(passwd.encode())
        #recup les partages
        shares=shamir.get_Shares()

        #partage des minis secrets sur les 2 parties: p1= responsable, p2= délégué
        #inserer les mini secrets dans la table secret
        share1 = json.dumps(shares[0])
        chkey =  c.sym_crypter_msg(share1, fk)
        #insérer le mini secret du responsable
        p1= Secret.objects.create(partie=self.owner, key1=chkey, ref_quiz=self)
        p1.save()

        #insérer le mini secret du délégué
        #avoir le délégué
        quiz_specialité=self.subject
        q=Student.objects.filter(interests=quiz_specialité).filter(is_deleguer=True).values_list('user_id',flat=True)
        dlg=User.objects.filter(id=q[0])

        share2 = json.dumps(shares[1])
        chkey =  c.sym_crypter_msg(share2, fk)
        p2= Secret.objects.create(partie=dlg[0], key1=chkey, ref_quiz = self)
        p2.save()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)
    counter = models.FloatField(default=0.0)

    def __str__(self):
        return self.text


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    matricule = models.CharField('Matricule', max_length=12)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    interests = models.ManyToManyField(Subject, related_name='interested_students')
    is_deleguer = models.BooleanField(default=False)

    def get_unanswered_questions(self, quiz):

        answered_questions = self.quiz_answers \
            .filter(quiz=quiz) \
            .values_list('question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        
       
        return questions

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)   
    is_responsable = models.BooleanField(default=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='is_responsable_de')
    def __str__(self):
        return self.user.username



class TakenQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)



class StudentAnswer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='stuans')
    question = models.ForeignKey(Question, on_delete=models.CASCADE,null=True, related_name='stuanswers')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.CharField(max_length=2048)

class Documment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='doc_destination')
    title= models.CharField(max_length=500)
    filepath= models.FileField(upload_to='files/', null=True, verbose_name="")

    def __str__(self):
        return self.title + ": " + str(self.filepath)

# La table qui associe pour chaque partie son secret 
#+ le secret de l'autre partie (initialement vide, remplit apres l'échange)
class Secret(models.Model):
    partie = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partie')
    key1 = models.CharField(max_length=2048) # le secret de la partie i
    key2 = models.CharField(max_length=2048,null=True) # le secret de l'autre partie
    ref_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='ref_quiz')

class Module(models.Model):
    nom = models.CharField('Nom', max_length=255)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE, related_name='module_sp')
