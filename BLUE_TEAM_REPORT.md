# BLUE_TEAM_REPORT — corvimx

**Equipo:** _(nombre del equipo)_
**Integrantes:** _(nombres)_
**Fecha:** _(fecha de la práctica)_
**Aplicación:** corvimx (Django) — app `core`
**URL expuesta durante la práctica (ngrok):** _(pegar aquí, ej. https://abcd-1234.ngrok-free.app)_

> Reporte de defensa. Documenta el hardening aplicado, los resultados de
> auditoría SAST/DAST y la detección de ataques mediante logs, según lo
> pedido en la actividad "Desafío de Ataque y Defensa" (Unidad 2).

---

## 1. Resumen ejecutivo

_(2–4 líneas: qué se hizo, qué tan expuesta estaba la app antes, qué tan
protegida quedó después.)_

Estado inicial detectado:
- `DEBUG=True` en producción.
- `SECRET_KEY` escrita directamente en el código fuente.
- `ALLOWED_HOSTS=['*']`.
- Sin `requirements.txt`, sin `.env.example`, sin `.gitignore` adecuado.
- Sin CSP.
- Sin logging de seguridad personalizado.
- Captcha visual validado solo en frontend.

Estado final: ver secciones siguientes.

---

## 2. Hardening del stack

| Medida | Implementación | Archivo |
|---|---|---|
| Variables de entorno | `django-environ` carga `.env` (no versionado) | `sitio_web/settings.py`, `.env.example` |
| `DEBUG` seguro | `DEBUG=False` por defecto vía `.env` | `sitio_web/settings.py` |
| `ALLOWED_HOSTS` controlado | Lista explícita desde `DJANGO_ALLOWED_HOSTS` | `sitio_web/settings.py` |
| `CSRF_TRUSTED_ORIGINS` para ngrok | Desde `DJANGO_CSRF_TRUSTED_ORIGINS` | `sitio_web/settings.py` |
| Cabeceras de seguridad | `X_FRAME_OPTIONS=DENY`, `SECURE_CONTENT_TYPE_NOSNIFF=True`, `SECURE_REFERRER_POLICY`, `SECURE_CROSS_ORIGIN_OPENER_POLICY` | `sitio_web/settings.py` |
| Cabecera de proxy HTTPS | `SECURE_PROXY_SSL_HEADER` para detectar HTTPS detrás de ngrok | `sitio_web/settings.py` |
| Redirección HTTPS y HSTS | `SECURE_SSL_REDIRECT` desde `.env`; HSTS activo solo si `DEBUG=False` y SSL activo | `sitio_web/settings.py` |
| Cookies seguras | `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`, `*_COOKIE_SECURE` (activo si no hay `DEBUG`) | `sitio_web/settings.py` |
| CSP estricta | `django-csp` con `script-src 'self' cdn.jsdelivr.net` (sin `unsafe-inline`), `object-src 'none'`, `frame-ancestors 'none'`, `form-action 'self'` | `sitio_web/settings.py` |
| Scripts inline eliminados | Todos los `<script>` y `onclick=` en templates se movieron a archivos `.js` en `core/static/js/` | `contacto.js`, `registro.js`, `buzon.js`, `chat.js`, `login.js`, `recuperar_contrasena.js`, `ayuda.js` |
| Validación server-side de captcha | Campo `captcha_ok` obligatorio y verificado en `RegistroForm`/`ContactoForm` | `core/forms.py` |
| Rechazo de HTML en campos de texto | Helper `_rechazar_html()` aplicado a nombre, asunto, mensaje, búsqueda | `core/forms.py` |
| Límites de longitud | `max_length` explícito en todos los `CharField` | `core/forms.py` |
| Rate limiting | `django-ratelimit` en `/login/`, `/registro/`, `/contacto/`, `/buzon/` | `core/views.py` |
| `/buzon/` protegido | Se conserva `@login_required` | `core/views.py` |
| CSRF en formularios | Se mantiene `{% csrf_token %}` en todos los `<form method="post">` | templates |
| No `mark_safe` / `|safe` / `autoescape off` | Se conserva el auto-escape de Django en toda la app | templates |

### 2.1 Corrección adicional encontrada durante el hardening (XSS en DOM)

Al mover el chat de `core/templates/core/chat.html` a `core/static/js/chat.js`
se detectó que el mensaje del usuario se insertaba con `innerHTML`, lo que
permitía ejecutar HTML/JS arbitrario en el navegador (XSS basado en DOM).
Se corrigió usando `textContent` para el texto del usuario y reservando
`innerHTML` únicamente para las respuestas fijas del "bot" (contenido
controlado por el propio desarrollo, no por el usuario).

---

## 3. Auditoría SAST/DAST (antes de exponer la URL)

### 3.1 Bandit (SAST)

Comando ejecutado:
```
bandit -r . -x ./venv,./.venv
```

Resultado obtenido en este entorno de referencia: **3 hallazgos de severidad
baja**, ninguno crítico:
- 2 falsos positivos de "hardcoded password" en `core/tests.py` (son
  contraseñas de prueba usadas solo en el entorno de pruebas).
- 1 aviso de `try/except/pass` en `core/middleware.py`, usado
  intencionalmente para no romper la petición real si falla la
  inspección de logging.

_(Pegar aquí la salida real de tu ejecución de `bandit` y una captura de
pantalla.)_

### 3.2 pip-audit (dependencias)

Comando ejecutado:
```
pip-audit
```

Resultado de referencia: **sin vulnerabilidades conocidas** una vez fijado
`Django>=5.2.8,<5.3` (la serie 5.0 usada originalmente tenía CVEs
corregidos en 5.2.8+).

_(Pegar aquí la salida real de tu ejecución y una captura de pantalla.)_

### 3.3 `python manage.py check --deploy`

Comando ejecutado:
```
python manage.py check --deploy
```

Con `DEBUG=False` y `DJANGO_SECURE_SSL_REDIRECT=True` (una vez expuesto por
HTTPS vía ngrok) no deberían quedar advertencias de `security.W004` /
`security.W008`.

_(Pegar aquí la salida real y una captura de pantalla.)_

### 3.4 OWASP ZAP (DAST)

Comando ejecutado (baseline scan local, contra tu propia URL de ngrok):
```
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://TU-URL.ngrok-free.app
```

_(Pegar aquí resumen de alertas, capturas de pantalla y las mitigaciones
aplicadas para cada alerta relevante.)_

---

## 4. Detección de intrusiones (logs)

El middleware `core/middleware.py` (`SecurityLoggingMiddleware`) registra
cada petición en `logs/security.log` con: timestamp, IP real (respetando
`X-Forwarded-For` detrás de ngrok), método, ruta, user-agent, usuario
autenticado (o "anonimo"), código de estado y duración.

Adicionalmente detecta y clasifica:
- **WARNING** `INJECTION_ATTEMPT (XSS)` — patrones de `<script`, atributos
  `on*=`, `javascript:`, `<iframe`, en query string / body (decodificados).
- **WARNING** `INJECTION_ATTEMPT (SQLi)` — comillas, comentarios SQL,
  palabras clave `UNION/SELECT/...`, patrones `OR 1=1`.
- **WARNING** `PATH_TRAVERSAL_ATTEMPT` — secuencias `../`, `/etc/passwd`, etc.
- **CRITICAL** `UNAUTHORIZED` — acceso a rutas tipo `/wp-admin`,
  `phpmyadmin` u otras rutas administrativas no válidas.
- **CRITICAL** `BLOQUEADO patrón crítico` — un conjunto muy corto de
  patrones evidentes (ej. `<script>...alert(...)`, `UNION SELECT`) se
  bloquea de entrada con `403`, para no generar falsos positivos con el
  resto de patrones (que solo se registran).

### 4.1 Evidencia de logs

_(Pegar aquí extractos reales de `logs/security.log` durante la fase 3,
capturando al menos: tráfico normal INFO, un intento de XSS, un intento de
SQLi y un intento de acceso a ruta administrativa.)_

```
[TIMESTAMP] INFO core.security: INFO: GET /buscar/ - ip=... usuario=anonimo status=200 duracion_ms=...
[TIMESTAMP] WARNING core.security: INJECTION_ATTEMPT (SQLi) | ip=... metodo=GET ruta=/buscar/ patrones=[...]
[TIMESTAMP] CRITICAL core.security: UNAUTHORIZED: intento de acceso a ruta administrativa | ip=... ruta=/wp-admin/
```

---

## 5. Pruebas automatizadas

Se agregaron pruebas en `core/tests.py` (11 pruebas) que verifican:
- `/buzon/` redirige a `/login/` sin sesión y responde `200` con sesión.
- `ContactoForm`/`RegistroForm` rechazan envíos sin `captcha_ok`.
- `ContactoForm` rechaza HTML en el mensaje.
- El buscador y el buzón no reflejan HTML/JS sin escapar (y el patrón
  más evidente de XSS es bloqueado con `403` por el middleware).
- Están presentes las cabeceras `X-Frame-Options`, `X-Content-Type-Options`
  y `Content-Security-Policy`, y esta última no incluye `'unsafe-inline'`
  en `script-src`.

Comando:
```
python manage.py test core
```

_(Pegar aquí la salida real: "Ran 11 tests ... OK", y una captura.)_

---

## 6. Conclusiones y trabajo pendiente

_(Qué quedó bien defendido, qué limitaciones existen — por ejemplo: el
CSP mantiene `'unsafe-inline'` en `style-src` porque hay estilos inline
en varios templates; se podría migrar a CSS también como mejora futura.)_
