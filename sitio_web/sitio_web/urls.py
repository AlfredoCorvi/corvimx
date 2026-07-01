from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views

handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('servicios/', views.servicios, name='servicios'),
    path('contacto/', views.contacto, name='contacto'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('mapa-sitio/', views.mapa_sitio, name='mapa_sitio'),
    path('buzon/', views.buzon, name='buzon'),
    path('buscar/', views.buscar, name='buscar'),
    path('chat/', views.chat, name='chat'),
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('recuperar-contrasena/', auth_views.PasswordResetView.as_view(
        template_name='core/recuperar_contrasena.html',
        success_url='/login/',
    ), name='password_reset'),
]
