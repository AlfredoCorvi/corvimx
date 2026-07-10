// Lógica de UI para el formulario de contacto.
// Movido a archivo estático para cumplir con una CSP estricta
// (sin 'unsafe-inline' en script-src).
document.addEventListener('DOMContentLoaded', function () {
  let captchaOk = false;
  const captchaBox = document.getElementById('captchaBox');
  const captchaCheck = document.getElementById('captchaCheck');
  const captchaInput = document.getElementById('captchaInput');
  const captchaError = document.getElementById('captchaError');
  const textarea = document.querySelector('[name="mensaje"]');
  const counter = document.getElementById('charCount');
  const form = document.getElementById('formContacto');

  function toggleCaptcha() {
    captchaOk = !captchaOk;
    captchaCheck.innerHTML = captchaOk ? '✓' : '';
    captchaCheck.classList.toggle('marcado', captchaOk);
    captchaInput.value = captchaOk ? '1' : '';
  }

  if (captchaBox) {
    captchaBox.addEventListener('click', toggleCaptcha);
  }

  if (textarea && counter) {
    textarea.addEventListener('input', () => {
      counter.textContent = textarea.value.length;
      counter.style.color = textarea.value.length < 20 ? '#ef4444' : '#22c55e';
    });
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      if (!captchaOk) {
        captchaError.style.display = 'block';
        e.preventDefault();
      }
      if (textarea && textarea.value.length < 20) {
        alert('El mensaje debe tener al menos 20 caracteres.');
        e.preventDefault();
      }
    });
  }
});
