# SECURITY_TESTING_CHECKLIST — corvimx

Checklist paso a paso para preparar, exponer y auditar la aplicación de
forma segura y ética antes/durante la práctica de ataque y defensa.

## Fase 0 — Preparación local

- [ ] Crear y activar entorno virtual.
- [ ] `pip install -r requirements.txt`
- [ ] Copiar `.env.example` a `.env` y generar una `SECRET_KEY` real:
      `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] Confirmar en `.env`: `DJANGO_DEBUG=False`.
- [ ] `python manage.py migrate`
- [ ] `python manage.py createsuperuser` (opcional, para revisar `/admin/`)
- [ ] `python manage.py test core` → deben pasar todas las pruebas.

## Fase 1 — Hardening y auditoría previa (antes de exponer la URL)

- [ ] `python manage.py check --deploy` → revisar y resolver advertencias.
- [ ] `bandit -r . -x ./venv,./.venv` → revisar hallazgos, documentar en
      `BLUE_TEAM_REPORT.md`.
- [ ] `pip-audit` → confirmar 0 vulnerabilidades conocidas en dependencias.
- [ ] Verificar cabeceras de seguridad con `curl -I http://127.0.0.1:8000/`:
      `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`,
      `Referrer-Policy`.
- [ ] Verificar que la CSP no incluya `'unsafe-inline'` en `script-src`.
- [ ] Confirmar que `/buzon/` redirige a `/login/` sin sesión iniciada.
- [ ] Confirmar que los formularios de contacto/registro rechazan el envío
      sin marcar la verificación humana (`captcha_ok`).
- [ ] Escaneo local DAST con OWASP ZAP (baseline) contra
      `http://127.0.0.1:8000/` — documentar alertas y mitigaciones.

## Fase 2 — Exposición con ngrok

- [ ] `python manage.py runserver 0.0.0.0:8000`
- [ ] En otra terminal: `ngrok http 8000`
- [ ] Copiar la URL pública HTTPS que entrega ngrok.
- [ ] Agregar esa URL a `DJANGO_ALLOWED_HOSTS` y a
      `DJANGO_CSRF_TRUSTED_ORIGINS` en `.env` (con el dominio, sin
      `https://` en `ALLOWED_HOSTS`, con `https://` en `CSRF_TRUSTED_ORIGINS`).
- [ ] Poner `DJANGO_SECURE_SSL_REDIRECT=True` en `.env` (ngrok sirve HTTPS).
- [ ] Reiniciar `runserver` para tomar los nuevos valores de `.env`.
- [ ] Volver a correr `python manage.py check --deploy` y confirmar que ya
      no aparecen `security.W004` / `security.W008`.
- [ ] Abrir la URL de ngrok desde el navegador y navegar por el sitio para
      confirmar que todo carga correctamente (sin errores de consola por CSP).

## Fase 3 — Monitoreo durante la fase activa

- [ ] Mantener abierta una terminal con:
      `tail -f logs/security.log` (Linux/Mac) o
      `Get-Content logs\security.log -Wait` (PowerShell).
- [ ] Revisar periódicamente que aparezcan entradas `INFO` de tráfico
      normal y detectar cualquier `WARNING`/`CRITICAL`.
- [ ] Guardar capturas de pantalla de los eventos relevantes conforme
      ocurren (no solo al final).

## Fase 4 — Ofensiva ética contra el objetivo asignado

- [ ] Confirmar con el profesor cuál es la URL objetivo asignada.
- [ ] Usar únicamente: OWASP ZAP, Burp Suite, Postman, DevTools, Nmap
      (reconocimiento básico), Dirbuster/gobuster (sin fuerza bruta masiva).
- [ ] Nunca ejecutar ataques de Denegación de Servicio.
- [ ] Documentar cada hallazgo en `RED_TEAM_REPORT_TEMPLATE.md` con
      payload exacto y evidencia visual.

## Fase 5 — Cierre y entrega

- [ ] Completar `BLUE_TEAM_REPORT.md` con resultados reales (no solo la
      plantilla) y capturas de pantalla.
- [ ] Completar `RED_TEAM_REPORT_TEMPLATE.md` con los hallazgos reales
      contra el equipo objetivo.
- [ ] Revisar que `.env` y `db.sqlite3` NO se suban al repositorio
      (deben estar en `.gitignore`).
- [ ] Revisar que `requirements.txt` esté actualizado.
- [ ] Empaquetar/entregar según lo solicitado por el profesor.

## Capturas de pantalla recomendadas para el reporte

1. Salida de `python manage.py check --deploy` sin advertencias.
2. Salida de `bandit -r .`.
3. Salida de `pip-audit`.
4. Cabeceras de respuesta HTTP (`curl -I` o pestaña Network del navegador)
   mostrando `X-Frame-Options`, `Content-Security-Policy`, etc.
5. Consola del navegador SIN errores de CSP al navegar el sitio.
6. Terminal de ngrok mostrando la URL pública activa.
7. `logs/security.log` con al menos un evento `WARNING` y uno `CRITICAL`
   reales, generados durante la fase de ataque.
8. Salida de `python manage.py test core` con todas las pruebas en `OK`.
9. (Fase ofensiva) Request/response del hallazgo en la app rival, y el
   payload exacto usado, para el `RED_TEAM_REPORT_TEMPLATE.md`.
