"""
Middleware de seguridad para el proyecto corvimx.

Funciones:
1. Registrar cada petición (timestamp, IP, método, ruta, user-agent,
   usuario autenticado, código de estado, duración) para auditoría y
   para el reporte BLUE_TEAM.
2. Detectar de forma defensiva patrones sospechosos comunes (XSS, SQLi,
   path traversal, acceso a rutas administrativas) en query string,
   cuerpo del request y path, y registrarlos con nivel WARNING/CRITICAL.

Este middleware NO ataca ni interactúa con terceros; solo observa el
tráfico que llega a esta aplicación. Por defecto no bloquea nada salvo
los patrones más evidentes indicados abajo, para no generar falsos
positivos durante la práctica.
"""

import logging
import re
import time
from urllib.parse import unquote_plus

from django.http import HttpResponseForbidden

logger = logging.getLogger('core.security')

# --- Patrones de detección (defensivos, no exhaustivos) --------------------

XSS_PATTERNS = [
    re.compile(r'<\s*script', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),          # onerror=, onload=, etc.
    re.compile(r'javascript\s*:', re.IGNORECASE),
    re.compile(r'<\s*iframe', re.IGNORECASE),
    re.compile(r'<\s*img[^>]+onerror', re.IGNORECASE),
]

SQLI_PATTERNS = [
    re.compile(r"(\%27)|(\')|(\-\-)|(\%23)|(#)"),        # comillas / comentarios SQL
    re.compile(r"(\b(select|union|insert|update|delete|drop|alter)\b.*\b(from|into|table|database)\b)", re.IGNORECASE),
    re.compile(r"\bor\b\s+\d+\s*=\s*\d+", re.IGNORECASE),  # OR 1=1
    re.compile(r"\band\b\s+\d+\s*=\s*\d+", re.IGNORECASE),
]

PATH_TRAVERSAL_PATTERNS = [
    re.compile(r'\.\./'),
    re.compile(r'\.\.\\'),
    re.compile(r'%2e%2e%2f', re.IGNORECASE),
    re.compile(r'/etc/passwd', re.IGNORECASE),
    re.compile(r'\bwin\.ini\b', re.IGNORECASE),
]

ADMIN_PATH_PATTERNS = [
    re.compile(r'^/admin', re.IGNORECASE),
    re.compile(r'wp-admin', re.IGNORECASE),
    re.compile(r'phpmyadmin', re.IGNORECASE),
]

# Patrones extremadamente evidentes que sí se bloquean con 403 de entrada.
# Se mantiene una lista muy corta para evitar falsos positivos.
HARD_BLOCK_PATTERNS = [
    re.compile(r'<\s*script[^>]*>.*alert\s*\(', re.IGNORECASE | re.DOTALL),
    re.compile(r'union\s+select', re.IGNORECASE),
]


def _get_client_ip(request):
    """Obtiene la IP real considerando cabeceras de proxy (ngrok, etc.)."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'desconocida')


def _collect_inspectable_text(request):
    """Reúne el texto de path, query string y body (si es legible) para
    análisis. Se decodifica el porcentaje-encoding (URL encoding) para
    que payloads como %3Cscript%3E se detecten igual que <script>."""
    raw_parts = [request.path, request.META.get('QUERY_STRING', '')]
    try:
        if request.method in ('POST', 'PUT', 'PATCH') and request.content_type == 'application/x-www-form-urlencoded':
            raw_parts.append(request.POST.urlencode())
    except Exception:
        # No se debe romper la petición real por un fallo de inspección
        pass
    combined = ' '.join(p for p in raw_parts if p)
    try:
        decoded = unquote_plus(combined)
    except Exception:
        decoded = combined
    # Se analizan ambas formas (cruda y decodificada) por si el propio
    # decodificado introdujera falsos negativos en algún caso límite.
    return combined + ' ' + decoded


def _match_any(patterns, text):
    return [p.pattern for p in patterns if p.search(text)]


class SecurityLoggingMiddleware:
    """Middleware que registra cada petición y detecta patrones sospechosos."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        ip = _get_client_ip(request)
        inspect_text = _collect_inspectable_text(request)

        xss_hits = _match_any(XSS_PATTERNS, inspect_text)
        sqli_hits = _match_any(SQLI_PATTERNS, inspect_text)
        traversal_hits = _match_any(PATH_TRAVERSAL_PATTERNS, inspect_text)
        admin_hits = _match_any(ADMIN_PATH_PATTERNS, request.path)
        hard_block_hits = _match_any(HARD_BLOCK_PATTERNS, inspect_text)

        # Bloqueo mínimo y explícito solo para los patrones más evidentes.
        if hard_block_hits:
            logger.critical(
                'BLOQUEADO patrón crítico | ip=%s metodo=%s ruta=%s patrones=%s',
                ip, request.method, request.path, hard_block_hits,
            )
            return HttpResponseForbidden('Solicitud bloqueada por política de seguridad.')

        if xss_hits:
            logger.warning(
                'INJECTION_ATTEMPT (XSS) | ip=%s metodo=%s ruta=%s patrones=%s',
                ip, request.method, request.path, xss_hits,
            )
        if sqli_hits:
            logger.warning(
                'INJECTION_ATTEMPT (SQLi) | ip=%s metodo=%s ruta=%s patrones=%s',
                ip, request.method, request.path, sqli_hits,
            )
        if traversal_hits:
            logger.warning(
                'PATH_TRAVERSAL_ATTEMPT | ip=%s metodo=%s ruta=%s patrones=%s',
                ip, request.method, request.path, traversal_hits,
            )
        if admin_hits and request.path != '/admin/':
            # Acceso a rutas tipo /admin*, wp-admin, phpmyadmin que no son el admin real de Django
            logger.critical(
                'UNAUTHORIZED: intento de acceso a ruta administrativa | ip=%s ruta=%s',
                ip, request.path,
            )

        response = self.get_response(request)
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), payment=(), usb=()'
            )


        duration_ms = (time.monotonic() - start_time) * 1000
        user = request.user.username if getattr(request, 'user', None) and request.user.is_authenticated else 'anonimo'
        user_agent = request.META.get('HTTP_USER_AGENT', 'desconocido')

        logger.info(
            'INFO: %s %s - ip=%s usuario=%s status=%s duracion_ms=%.1f ua=%s',
            request.method, request.path, ip, user, response.status_code, duration_ms, user_agent,
        )

        return response
