from django.contrib import admin

from django.urls import include, path

from classroom.views import classroom, students, teachers

from django.conf.urls.static import static

from django.conf import settings


urlpatterns = [
    path('', include('classroom.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]+ static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

