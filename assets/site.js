/* tiosantos: menu do celular, filtros, compartilhamento e comentários. */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  // Links antigos (tiosantos.pages.dev/#id) continuam funcionando
  var antigos = window.TS_ANTIGOS;
  if (antigos && location.hash.length > 1) {
    var alvo = antigos[decodeURIComponent(location.hash.slice(1))];
    if (alvo) { location.replace(alvo); return; }
  }

  // Menu do celular
  var botao = document.querySelector('.menu-botao');
  var menu = document.getElementById('menu');
  if (botao && menu) {
    botao.addEventListener('click', function () {
      var aberto = menu.classList.toggle('aberto');
      botao.setAttribute('aria-expanded', aberto ? 'true' : 'false');
    });
  }

  // Filtros da lista de microtextos
  var filtros = document.querySelectorAll('.filtro');
  filtros.forEach(function (f) {
    f.addEventListener('click', function () {
      var tipo = f.getAttribute('data-tipo');
      filtros.forEach(function (o) { o.setAttribute('aria-pressed', o === f ? 'true' : 'false'); });
      document.querySelectorAll('.lista li[data-tipo]').forEach(function (li) {
        li.hidden = tipo !== '' && li.getAttribute('data-tipo') !== tipo;
      });
    });
  });

  // Compartilhar
  var aviso = document.querySelector('.partilha-aviso');
  function avisar(msg) { if (aviso) { aviso.textContent = msg; } }
  var nativo = document.querySelector('[data-partilhar]');
  if (nativo && navigator.share) {
    nativo.hidden = false;
    nativo.addEventListener('click', function () {
      navigator.share({ title: document.title, text: nativo.getAttribute('data-texto') || '', url: location.href.split('#')[0] }).catch(function () {});
    });
  }
  var copiar = document.querySelector('[data-copiar]');
  if (copiar) {
    copiar.addEventListener('click', function () {
      var url = location.href.split('#')[0];
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () { avisar('Link copiado.'); }, function () { avisar('Copie o link: ' + url); });
      } else {
        avisar('Copie o link: ' + url);
      }
    });
  }

  // Comentários (Formspree)
  var form = document.querySelector('.comentario');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var enviar = form.querySelector('button[type="submit"]');
      var estado = form.querySelector('.aviso');
      enviar.disabled = true;
      estado.textContent = 'Enviando…';
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) {
          if (!r.ok) { throw new Error('falha'); }
          form.reset();
          estado.textContent = 'Comentário enviado. Obrigado!';
          enviar.disabled = false;
        })
        .catch(function () {
          estado.textContent = 'Não foi possível enviar agora. Tente de novo em instantes.';
          enviar.disabled = false;
        });
    });
  }
})();
