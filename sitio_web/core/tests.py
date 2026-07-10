"""
Pruebas de seguridad y funcionalidad básica para corvimx.

Cubren lo pedido para la práctica escolar:
- /buzon/ redirige si no hay sesión iniciada.
- Los formularios rechazan entradas inválidas (captcha ausente, HTML/JS
  en campos de texto).
- Las búsquedas y mensajes no ejecutan HTML/JS (se escapan o se rechazan).
- Existen las cabeceras de seguridad esperadas.
"""

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class RutasProtegidasTests(TestCase):
    def test_buzon_redirige_si_no_hay_sesion(self):
        response = self.client.get(reverse('buzon'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_buzon_accesible_con_sesion(self):
        user = User.objects.create_user(username='usuario_test', password='ClaveSegura123!')
        self.client.force_login(user)
        response = self.client.get(reverse('buzon'))
        self.assertEqual(response.status_code, 200)


class ValidacionFormulariosTests(TestCase):
    def test_contacto_rechaza_sin_captcha(self):
        response = self.client.post(reverse('contacto'), {
            'nombre': 'Ana Pérez',
            'email': 'ana@example.com',
            'asunto': 'Consulta',
            'mensaje': 'Este es un mensaje de prueba con más de veinte caracteres.',
            # captcha_ok deliberadamente omitido
        })
        self.assertEqual(response.status_code, 200)  # vuelve a mostrar el formulario con errores
        self.assertContains(response, 'corrige los errores')

    def test_contacto_rechaza_html_en_mensaje(self):
        response = self.client.post(reverse('contacto'), {
            'nombre': 'Ana Pérez',
            'email': 'ana@example.com',
            'asunto': 'Consulta',
            'mensaje': '<script>alert(1)</script> mensaje con más de veinte caracteres.',
            'captcha_ok': '1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'corrige los errores')

    def test_registro_rechaza_sin_captcha(self):
        response = self.client.post(reverse('registro'), {
            'username': 'nuevo_usuario',
            'first_name': 'Juan',
            'last_name': 'López',
            'email': 'juan@example.com',
            'password1': 'ClaveSegura123!',
            'password2': 'ClaveSegura123!',
            # captcha_ok deliberadamente omitido
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='nuevo_usuario').exists())

    def test_registro_exitoso_con_captcha(self):
        response = self.client.post(reverse('registro'), {
            'username': 'nuevo_usuario2',
            'first_name': 'Juan',
            'last_name': 'López',
            'email': 'juan2@example.com',
            'password1': 'ClaveSegura123!',
            'password2': 'ClaveSegura123!',
            'captcha_ok': '1',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='nuevo_usuario2').exists())


class BusquedaYMensajesSinXSSTests(TestCase):
    def test_busqueda_no_ejecuta_html(self):
        response = self.client.get(reverse('buscar'), {'q': '<script>alert(1)</script>'})
        # El middleware de seguridad bloquea de entrada este patrón evidente
        # de XSS con 403. En ningún caso debe reflejarse el script sin escapar.
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, '<script>alert(1)</script>', status_code=403)

    def test_busqueda_con_html_no_bloqueado_se_escapa(self):
        # Un payload de HTML que no coincide con los patrones de bloqueo
        # duro debe, aun así, ser rechazado por la validación del
        # formulario (BusquedaForm.clean_q) y nunca reflejarse sin escapar.
        response = self.client.get(reverse('buscar'), {'q': '<b>hola</b>'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<b>hola</b>')

    def test_buzon_rechaza_html_en_mensaje(self):
        user = User.objects.create_user(username='usuario_buzon', password='ClaveSegura123!')
        self.client.force_login(user)
        response = self.client.post(reverse('buzon'), {
            'asunto': 'Prueba',
            'mensaje': '<img src=x onerror=alert(1)> mensaje de prueba largo',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<img src=x onerror=alert(1)>')


class CabecerasSeguridadTests(TestCase):
    def test_cabeceras_seguridad_presentes(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.get('X-Content-Type-Options'), 'nosniff')
        self.assertIn('Content-Security-Policy', response)

    def test_csp_no_permite_unsafe_inline_en_scripts(self):
        response = self.client.get(reverse('inicio'))
        csp = response.get('Content-Security-Policy', '')
        self.assertIn("script-src", csp)
        # Verifica que la directiva script-src no incluya 'unsafe-inline'
        script_src_directive = [d for d in csp.split(';') if 'script-src' in d]
        self.assertTrue(script_src_directive)
        self.assertNotIn("'unsafe-inline'", script_src_directive[0])
