from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from ..models import Documment
from django.shortcuts import render
from django.template import Context

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from smartcard.System import readers 
from smartcard.util import toHexString
from ..forms import VerifForm


global connection
global reponse
reponse = 0


def index2(request,pk):
  #AID du package et applet
  SELECT_APPLIC = [0x00,0xA4,0x04,0x00,0x05,0x11,0x11,0x11,0x11,0x11]
  SELECT_APPLET = [0x00,0xA4,0x04,0x00,0x06,0x11,0x11,0x11,0x11,0x11,0x00]
  #etape 1 : selectionner le package et l applet
  cnx = selection(SELECT_APPLIC,SELECT_APPLET)
  if cnx == 1:
    val_champ = pk
    c = debloquer(val_champ)
    if c == 1:
      msg2 = "la carte a été débloqué"
      cnt2 = {
        'msg' : msg2,
      }
      return render(request, "success.html", cnt2)
    elif c == 3:
      msg = "carte bloqué"
      cnt = {
       'msg' : msg,
      }
      return render(request, "error.html", cnt2)
    else :
      msg = "il vous reste "+ str(c)
      cnt = {
       'msg' : msg,
      }
      return render(request,'error.html',cnt)
  else:
    return HttpResponse("erreur inserez votre carte")


def index(request,pk):
  #AID du package et applet
  SELECT_APPLIC = [0x00,0xA4,0x04,0x00,0x05,0x11,0x11,0x11,0x11,0x11]
  SELECT_APPLET = [0x00,0xA4,0x04,0x00,0x06,0x11,0x11,0x11,0x11,0x11,0x00]
  #etape 1 : selectionner le package et l applet
  cnx = selection(SELECT_APPLIC,SELECT_APPLET)
  if cnx == 1:
    #on ecrit sur la carte a chaque fois car on est en simulation 
    

    # 
    # 
    #lire les donnees stockees dans la carte
    

    val_champ = pk
    rep = verify(val_champ,0)
    if rep == ['90','0'] :
      dic = Ecrire_info({0x01:"KASBADJI",0x02:"161631097303",0x03:"Sofian",0x04:"01-03-1999",0x05:"sofian"})
      # dic = Ecrire_info({0x01:"Enseignant1",0x02:"-",0x03:"prenom1",0x04:"01-05-1964",0x05:"Pr_Crypto"})
      # dic = Ecrire_info({0x01:"Enseignant2",0x02:"-",0x03:"prenom2",0x04:"01-05-1978",0x05:"Pr_secR"})
      # dic = Ecrire_info({0x01:"SEBAA",0x02:"161631097203",0x03:"Lina",0x04:"27-10-1998",0x05:"lina"})
      # dic = Ecrire_info({0x01:"ZAKARIA",0x02:"161631096205",0x03:"Lamia",0x04:"28-10-1998",0x05:"lamia"})
      # dic = Ecrire_info({0x01:"AHDIBI",0x02:"161631097297",0x03:"Aymen",0x04:"01-09-1999",0x05:"aymen"})
      # dic = Ecrire_info({0x01:"ZEMMOURI",0x02:"161631096200",0x03:"Lila",0x04:"01-05-1999",0x05:"lila"})
      liste_data = lire_info([0x10,0x21,0x31,0x40,0x0b])
      #recuperer username et password
      username = liste_data[4]
      password = val_champ
      user = authenticate(request,username=username, password=password)
      if user is not None:
        login(request,user)
        if request.user.is_authenticated:
          if request.user.is_teacher:
            return redirect('teachers:quiz_change_list')
          else:
            return redirect('students:quiz_list')
        else:
          return render(request,'error.html',)
    elif rep == ['68','1'] or rep == ['68','2']:
      rep = str(rep[-1])
      msg = "il vous reste "+ rep
      cnt = {
       'msg' : msg,
      }
      return render(request,'error.html',cnt)
      #return HttpResponse("il vous reste "+rep)
    elif rep == ['69','82']:
      msg = "carte bloqué"
      cnt = {
       'msg' : msg,
      }
      return render(request,'error.html',cnt)
      #return HttpResponse("carte bloquee")
# ---------------------------debloquer la carte ------------------------------
    # val_champ = pk
    # c = debloquer(val_champ)
    # if c == 1:
      # return HttpResponse("carte deblouquee")
    # elif c == 3:
      # return HttpResponse("carte bloquee")
    # else :
     # return HttpResponse("mot des passe incorrecte il vous reste"+str(c))
# -----------------------------------------------------------------------------
  else:
    return render(request,'error.html',)


def selection(SELECT_APPLIC,SELECT_APPLET):
 global connection
 global reponse
 
 try:
  r=readers()
  print(r)
  connection = r[0].createConnection()
  connection.connect()
  reponse =1
  print(reponse)
  try:
   data, sw1, sw2 = connection.transmit(SELECT_APPLIC)
   sw1 = "%x"%sw1
   sw2 = "%x"%sw2
 
   if ((sw1=="90") and (sw2 == "0")):
    data, sw1, sw2 = connection.transmit(SELECT_APPLET)
    sw1 = "%x"%sw1
    sw2 = "%x"%sw2
    # verifier la reponse de selection de l'applet
    if ((sw1=="90") and (sw2 == "0")):
     return 1
  except:
   return 0
 except:
  return 0


def Ecrire_info(dic):
 global reponse
 global connection
 if reponse ==1:
  # SEND_ECRIR = [CLA, INS, P1, P2, LC, DATA_FIELD]
  for i in dic:
   liste = []
   donnee = str(dic[i])
   long = len(donnee)

   for x in range(long):
    liste.append(ord(donnee[x]))

   SEND_ECRIR = [176,i,0,0,len(liste)]
   for i in liste:
    SEND_ECRIR.append(i)
   dat,sw1, sw2 = connection.transmit(SEND_ECRIR)


def lire_info(liste):
 global reponse
 global connection
 donnee = ''
 if reponse ==1:
  listedonnee = []
  for i in liste: # i cest l INS 
   # SEND_LIRE = [CLA, INS, P1, P2, Le] en entier
   SEND_LIRE = [176,i,0,0] 
   data, sw1, sw2 = connection.transmit(SEND_LIRE)
   sw1 = "%x"%sw1
   sw2 = "%x"%sw2
   # print(data)
   #verifier si l action est bien passee
   if ((sw1=="90")  and (sw2 == "0")):
    # data est une liste
    donnee =''
    liste =[]
   for i in range(len(data)):
    if (data[i] != 0): #pour eviter l'affichage les case vide (/x00) 
     liste.append(chr(data[i]))
     donnee =donnee+liste[i]
   listedonnee.append(donnee)
  return listedonnee




class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

def home2(request):
  if request.user.is_authenticated:
    if request.user.is_teacher:
      return render(request,'services.html')
    else:
      return redirect('students:quiz_list')
  return render(request,'classroom/home.html',)

def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:quiz_change_list')
        else:
            return redirect('students:quiz_list')
    return render(request, 'classroom/home.html')

def home3(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:quiz_change_list')
        else:
            return redirect('students:quiz_list')
    return render(request, 'classroom/home2.html')


def doc_view(request):
    if request.user.is_authenticated:
        documents = Documment.objects.all()
        p = "http://localhost:8000/"
    else:
        documents = []
    args = {
    'documents': documents,
    'p' : p
    }
    return render(request,'doc.html', args)


def error(request):
   return render(request,'error.html',)

def success(request):
   return render(request,'success.html',)

def ready(request,pk):
  quiz = Quiz.objects.filter(id = pk)
  quiz.results_ready +=1
  quiz.save()

  return redirect(request, './',)


def get_code(request):
  global reponse
  global connection
  if request.user.is_authenticated:
    if request.user.is_teacher:
      return redirect('teachers:quiz_change_list')
    else:
      return redirect('students:quiz_list')

  elif request.method == 'POST':
    form = VerifForm(request.POST)
    if form.is_valid():
      code = form.cleaned_data['your_code']
      print(code)
      cnt = {
        'code' : code,
      }
      return render(request,'classroom/home2.html', cnt)
  else:
    form = VerifForm()

  return render(request, 'classroom/home.html',{'form': form})


def verify(val_champ,user):
 global reponse
 global connection
 # SEND_VERIFY = [176,20,user,0,4]
 donnee = str(val_champ)
 liste = []
 long = len(donnee)

 for x in range(4):
    liste.append(ord(donnee[x]))

 SEND_VERIFY = [176,0x20,user,0,4]
 for i in liste:
    SEND_VERIFY.append(i)
 dat,sw1, sw2 = connection.transmit(SEND_VERIFY)
 

 sw1 = "%x"%sw1
 sw2 = "%x"%sw2
 rep = [sw1,sw2]
 return rep

def debloquer(val_champ):
  rep = verify(val_champ,1)
  if rep == ['90','0'] :
   # success
   SEND_DEBLOK = [176,0x07,0,0,4,0x31,0x32,0x33,0x34]
   connection.transmit(SEND_DEBLOK)
   return 1
  elif rep == ['68','1'] or rep == ['68','2']:
    rep = str(rep[-1])
    return rep
  elif rep == ['69','82']:
    return 3
