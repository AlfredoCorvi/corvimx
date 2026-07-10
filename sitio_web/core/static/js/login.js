document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('togglePasswordBtn');
  const input = document.getElementById('inputPassword');
  const icon = document.getElementById('eyeIcon');
  const form = document.getElementById('formLogin');

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'bi bi-eye-slash';
      } else {
        input.type = 'password';
        icon.className = 'bi bi-eye';
      }
    });
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      const user = document.querySelector('[name="username"]').value.trim();
      const pass = document.querySelector('[name="password"]').value;
      if (!user || !pass) {
        alert('Completa todos los campos.');
        e.preventDefault();
      }
    });
  }
});
