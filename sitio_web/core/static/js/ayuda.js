document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.faq-pregunta').forEach(function (el) {
    el.addEventListener('click', function () {
      el.parentElement.classList.toggle('activo');
    });
  });
});
