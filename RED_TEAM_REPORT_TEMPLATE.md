# RED_TEAM_REPORT — Equipo objetivo asignado

**Equipo atacante (nosotros):** _(nombre del equipo)_
**Integrantes:** _(nombres)_
**Fecha:** _(fecha de la práctica)_
**Equipo/aplicación objetivo:** _(nombre del equipo rival)_
**URL objetivo (ngrok, asignada por el profesor):** _(pegar aquí)_

> **Reglas de compromiso (obligatorias):**
> - Solo se prueba la URL asignada por el profesor.
> - Prohibido: DoS, fuerza bruta masiva, robo de datos real, persistencia,
>   backdoors, malware o cualquier contraataque.
> - Cada hallazgo debe documentarse con el payload exacto usado y
>   evidencia visual (capturas), de forma ética y profesional.
> - El objetivo es la mejora colectiva, no causar daño.

---

## 1. Resumen de hallazgos

| # | Vulnerabilidad | Endpoint | Severidad estimada | Estado |
|---|---|---|---|---|
| 1 | _(ej. XSS reflejado)_ | `/buscar/?q=...` | Alta/Media/Baja | Confirmado / No confirmado |
| 2 | | | | |
| 3 | | | | |

_(Agrega una fila por cada hallazgo real, encontrado únicamente contra la
URL asignada.)_

---

## 2. Herramientas utilizadas

- [ ] OWASP ZAP (escaneo pasivo/activo autorizado)
- [ ] Burp Suite (interceptación manual)
- [ ] Postman (pruebas manuales de endpoints)
- [ ] DevTools del navegador
- [ ] Nmap (solo reconocimiento básico de puertos, sin escaneo agresivo)
- [ ] Dirbuster / gobuster (enumeración de rutas, sin fuerza bruta masiva)

---

## 3. Detalle de cada hallazgo

### Hallazgo #1: _(nombre corto, ej. "XSS reflejado en buscador")_

- **Categoría:** XSS / SQLi / Broken Auth / Cabeceras faltantes / Otro
- **Endpoint / URL exacta:** `https://TU-OBJETIVO.ngrok-free.app/ruta?param=...`
- **Método HTTP:** GET / POST
- **Payload exacto utilizado:**
  ```
  (pegar aquí el payload literal, ej: <script>alert('demo')</script>)
  ```
- **Pasos para reproducir:**
  1. …
  2. …
  3. …
- **Evidencia:** _(insertar capturas de pantalla: request, response,
  consola del navegador, comportamiento observado)_
- **Impacto técnico:** _(qué podría hacer un atacante real con esto: robo
  de sesión, exfiltración de datos, escalamiento de privilegios, etc.)_
- **Impacto en el negocio/usuario:** _(en términos no técnicos: pérdida de
  confianza, exposición de datos personales, etc.)_
- **Recomendación de mitigación:** _(qué debería corregir el equipo
  defensor — validación server-side, escape de salida, CSP, etc.)_

### Hallazgo #2: _(repetir estructura anterior)_

---

## 4. Pruebas realizadas sin hallazgos (negativo también documenta valor)

_(Ej.: "Se intentó XSS almacenado en el campo mensaje del buzón; la
aplicación rechazó la entrada con un error de validación. No explotable."
Esto demuestra rigor y ayuda al equipo defensor a confirmar sus controles.)_

---

## 5. Cierre ético

Confirmo que todas las pruebas documentadas en este reporte se realizaron
exclusivamente contra la URL asignada por el profesor, sin ataques de
denegación de servicio, sin fuerza bruta masiva, sin robo real de datos ni
persistencia de acceso, y que los hallazgos se reportan con fines
educativos y de mejora colectiva.

**Firma / equipo:** _____________________
