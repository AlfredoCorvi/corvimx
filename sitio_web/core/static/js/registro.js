// Lógica de UI para el formulario de registro.
// Movido a archivo estático para cumplir con una CSP estricta
// (sin 'unsafe-inline' en script-src). La validación real y
// obligatoria del captcha ocurre siempre en el servidor
// (ver core/forms.py), esto es solo experiencia de usuario.
document.addEventListener('DOMContentLoaded', function () {
  let captchaOk = false;
  const captchaBox = document.getElementById('captchaBox');
  const captchaCheck = document.getElementById('captchaCheck');
  const captchaInput = document.getElementById('captchaInput');
  const captchaError = document.getElementById('captchaError');
  const form = document.getElementById('formRegistro');
  const usernameInput = document.querySelector('[name="username"]');
  const emailInput = document.querySelector('[name="email"]');

  function toggleCaptcha() {
    captchaOk = !captchaOk;
    if (captchaOk) {
      captchaCheck.innerHTML = '✓';
      captchaCheck.classList.add('marcado');
      captchaInput.value = '1';
    } else {
      captchaCheck.innerHTML = '';
      captchaCheck.classList.remove('marcado');
      captchaInput.value = '';
    }
  }

  if (captchaBox) {
    captchaBox.addEventListener('click', toggleCaptcha);
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      let ok = true;

      if (!captchaOk) {
        captchaError.style.display = 'block';
        ok = false;
      } else {
        captchaError.style.display = 'none';
      }

      const p1 = document.querySelector('[name="password1"]').value;
      const p2 = document.querySelector('[name="password2"]').value;
      if (p1 && p2 && p1 !== p2) {
        alert('Las contraseñas no coinciden.');
        ok = false;
      }

      if (!ok) e.preventDefault();
    });
  }

  if (usernameInput) {
    usernameInput.addEventListener('input', function () {
      const val = this.value;
      const regex = /^[a-zA-Z0-9_]+$/;
      if (val && !regex.test(val)) {
        this.classList.add('is-invalid');
      } else {
        this.classList.remove('is-invalid');
        if (val.length >= 3) this.classList.add('is-valid');
      }
    });
  }

  if (emailInput) {
    emailInput.addEventListener('blur', function () {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (this.value && emailRegex.test(this.value)) {
        this.classList.add('is-valid');
        this.classList.remove('is-invalid');
      } else if (this.value) {
        this.classList.add('is-invalid');
        this.classList.remove('is-valid');
      }
    });
  }
});
