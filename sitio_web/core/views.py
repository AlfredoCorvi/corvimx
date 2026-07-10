from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from .forms import RegistroForm, ContactoForm, BuzonForm, BusquedaForm


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class LoginRateLimitedView(LoginView):
    """Login estándar de Django con límite de intentos por IP para
    dificultar fuerza bruta (defensa, no ataque)."""
    template_name = 'core/login.html'



def inicio(request):
    return render(request, 'core/inicio.html')


def nosotros(request):
    return render(request, 'core/nosotros.html')


def servicios(request):
    servicios_lista = [
        {'icono': '🌐', 'nombre': 'Desarrollo web', 'desc': 'Sitios y aplicaciones web modernas, responsivas y optimizadas para rendimiento.'},
        {'icono': '🔐', 'nombre': 'Seguridad digital', 'desc': 'Protección de datos, autenticación segura y auditorías de vulnerabilidades.'},
        {'icono': '📊', 'nombre': 'Análisis de datos', 'desc': 'Dashboards y reportes que convierten tus datos en decisiones inteligentes.'},
        {'icono': '📱', 'nombre': 'Apps móviles', 'desc': 'Aplicaciones nativas e híbridas para iOS y Android con diseño intuitivo.'},
        {'icono': '☁️', 'nombre': 'Infraestructura cloud', 'desc': 'Migración, configuración y gestión de servicios en la nube.'},
        {'icono': '🤖', 'nombre': 'Automatización', 'desc': 'Procesos automáticos que reducen trabajo manual y errores humanos.'},
    ]
    return render(request, 'core/servicios.html', {'servicios_lista': servicios_lista})


def ayuda(request):
    return render(request, 'core/ayuda.html')


def mapa_sitio(request):
    return render(request, 'core/mapa_sitio.html')


def chat(request):
    return render(request, 'core/chat.html')


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            messages.success(request, '¡Mensaje enviado correctamente! Te contactaremos pronto.')
            return redirect('contacto')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ContactoForm()
    return render(request, 'core/contacto.html', {'form': form})


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name}! Tu cuenta fue creada.')
            return redirect('inicio')
        else:
            messages.error(request, 'Revisa los datos e intenta de nuevo.')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})


@login_required
@ratelimit(key='user_or_ip', rate='15/m', method='POST', block=True)
def buzon(request):
    if request.method == 'POST':
        form = BuzonForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Mensaje enviado al buzón correctamente.')
            return redirect('buzon')
    else:
        form = BuzonForm()
    return render(request, 'core/buzon.html', {'form': form})


def buscar(request):
    form = BusquedaForm(request.GET or None)
    resultados = []
    query = ''
    paginas = [
        {'titulo': 'Inicio', 'url': '/', 'desc': 'Página principal del sitio'},
        {'titulo': 'Nosotros', 'url': '/nosotros/', 'desc': 'Información sobre nosotros y nuestra misión'},
        {'titulo': 'Servicios', 'url': '/servicios/', 'desc': 'Nuestros servicios y soluciones'},
        {'titulo': 'Contacto', 'url': '/contacto/', 'desc': 'Formulario de contacto y ubicación'},
        {'titulo': 'Ayuda', 'url': '/ayuda/', 'desc': 'Preguntas frecuentes y soporte'},
        {'titulo': 'Mapa del sitio', 'url': '/mapa-sitio/', 'desc': 'Estructura completa del sitio'},
        {'titulo': 'Chat', 'url': '/chat/', 'desc': 'Chat de soporte en tiempo real'},
    ]
    if form.is_valid():
        query = form.cleaned_data['q'].lower()
        resultados = [p for p in paginas if query in p['titulo'].lower() or query in p['desc'].lower()]
    return render(request, 'core/buscar.html', {'form': form, 'resultados': resultados, 'query': query})


def error_404(request, exception=None):
    return render(request, 'core/404.html', status=404)


def error_500(request):
    return render(request, 'core/500.html', status=500)
