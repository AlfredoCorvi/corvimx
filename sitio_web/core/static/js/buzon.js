document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('formBuzon');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    const asunto = document.querySelector('[name="asunto"]').value.trim();
    const msg = document.querySelector('[name="mensaje"]').value.trim();
    if (!asunto || msg.length < 10) {
      alert('Asunto requerido y mensaje mínimo de 10 caracteres.');
      e.preventDefault();
    }
  });
});
