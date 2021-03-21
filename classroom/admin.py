from django.contrib import admin
from classroom.models import User,Subject,Quiz,Question,Answer,Student,TakenQuiz,StudentAnswer,Documment,Teacher,Secret, Module
 
admin.site.site_header = "Administration"

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Documment)
admin.site.register(Teacher)
admin.site.register(Module)