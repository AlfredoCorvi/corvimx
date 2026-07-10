document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('formRecuperar');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    const email = document.querySelector('[name="email"]').value;
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!regex.test(email)) {
      alert('Ingresa un correo electrónico válido.');
      e.preventDefault();
    }
  });
});
