// Chat de demostración (simulado, sin backend real).
// Se separa a un archivo estático para cumplir la CSP estricta.
// IMPORTANTE (hardening XSS en DOM): el texto que escribe el usuario
// se inserta siempre con textContent, nunca con innerHTML, para evitar
// que un payload como <img src=x onerror=alert(1)> se ejecute en el
// navegador. Las respuestas fijas del "bot" sí usan HTML controlado
// por nosotros (no proviene del usuario).
document.addEventListener('DOMContentLoaded', function () {
  const respuestas = [
    '¡Claro! Con gusto te ayudo con eso. ¿Puedes darme más detalles?',
    'Entiendo tu consulta. Te recomiendo revisar nuestra sección de <a href="/ayuda/">Ayuda</a>.',
    'Permíteme un momento para verificar esa información...',
    'Puedes encontrar esa información en el <a href="/mapa-sitio/">Mapa del sitio</a>.',
    '¿Hay algo más en lo que pueda ayudarte?',
    'Gracias por contactarnos. Un agente humano revisará tu caso pronto.',
  ];

  let msgIdx = 0;
  const caja = document.getElementById('chatMensajes');
  const input = document.getElementById('chatTexto');
  const btnEnviar = document.getElementById('btnEnviar');

  function hora() {
    const now = new Date();
    return now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
  }

  function agregarMensaje(texto, tipo, esHtmlConfiable) {
    const div = document.createElement('div');
    div.className = `chat-msg ${tipo}`;

    const burbuja = document.createElement('div');
    burbuja.className = 'chat-burbuja';
    if (esHtmlConfiable) {
      // Solo se usa para las respuestas fijas definidas arriba, nunca
      // para texto escrito por el usuario.
      burbuja.innerHTML = texto;
    } else {
      burbuja.textContent = texto;
    }

    const horaDiv = document.createElement('div');
    horaDiv.className = 'chat-hora';
    horaDiv.textContent = hora();

    div.appendChild(burbuja);
    div.appendChild(horaDiv);
    caja.appendChild(div);
    caja.scrollTop = caja.scrollHeight;
  }

  function enviarMensaje() {
    const texto = input.value.trim();
    if (!texto) return;
    agregarMensaje(texto, 'usuario', false);
    input.value = '';

    setTimeout(() => {
      const resp = respuestas[msgIdx % respuestas.length];
      msgIdx++;
      agregarMensaje(resp, 'soporte', true);
    }, 900 + Math.random() * 600);
  }

  if (btnEnviar) btnEnviar.addEventListener('click', enviarMensaje);
  if (input) {
    input.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') enviarMensaje();
    });
  }
});
