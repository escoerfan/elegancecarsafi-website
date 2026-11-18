/* =========================================================================
   ECS GmbH – Elegance Car Safi
   Direkter Formularversand (Kontakt- und Ankauf-Formular)

   Die Angaben gehen per HTTPS an unseren Versanddienst (Cloudflare Worker
   "ecs-anfrage"), der sie als E-Mail an info@ecs-holding.com schickt.
   Kein Mailprogramm, nichts wird gespeichert. Fotos (Ankauf) werden vorher
   im Browser verkleinert.

   Nutzung:  ECSAnfrage.senden(form, 'kontakt' | 'ankauf') -> Promise
   ========================================================================= */
(function () {
  'use strict';

  var ENDPOINT = window.ECS_ANFRAGE_URL || 'https://ecs-anfrage.ecs-statistik.workers.dev/anfrage';
  var PHONE = '+49 1514 0315387';
  var MAX_FOTOS = 6;
  var MAX_KANTE = 1600;      // längste Bildseite in Pixeln
  var QUALITAET = 0.82;
  var loaded = (window.performance && performance.now) ? function () { return performance.now(); }
                                                        : (function (s) { return function () { return Date.now() - s; }; })(Date.now());

  var TEXT = {
    senden: 'Wird gesendet …',
    ok: 'Vielen Dank! Ihre Anfrage ist bei uns angekommen. Wir melden uns schnellstmöglich bei Ihnen.',
    fehler: 'Das Senden hat leider nicht geklappt. Bitte versuchen Sie es erneut oder rufen Sie uns an:',
    zuViele: 'Zu viele Anfragen in kurzer Zeit. Bitte versuchen Sie es in einer Minute erneut.',
    fotoGross: 'Die Fotos sind zu groß. Bitte wählen Sie weniger oder kleinere Fotos.',
    fotoTyp: 'Dieses Foto-Format können wir nicht verarbeiten. Bitte JPG- oder PNG-Fotos wählen.',
    fotoAnzahl: 'Bitte höchstens 6 Fotos auswählen.',
    offline: 'Keine Internetverbindung. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.'
  };

  /* Unsichtbares Lockfeld gegen Spam-Bots in jedes Formular setzen */
  function honeypot(form) {
    if (form.querySelector('input[name="website"]')) return;
    var wrap = document.createElement('div');
    wrap.setAttribute('aria-hidden', 'true');
    wrap.style.cssText = 'position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden';
    wrap.innerHTML = '<label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label>';
    form.appendChild(wrap);
  }

  function statusEl(form) {
    var el = form.querySelector('.form-status');
    if (!el) {
      el = document.createElement('p');
      el.className = 'form-status';
      el.setAttribute('role', 'status');
      el.setAttribute('aria-live', 'polite');
      var anchor = form.querySelector('.ankauf-form__actions') || form.querySelector('button[type="submit"]');
      anchor.parentNode.insertBefore(el, anchor.nextSibling);
    }
    return el;
  }

  function zeige(form, art, text, mitTelefon) {
    var el = statusEl(form);
    el.className = 'form-status form-status--' + art;
    el.textContent = '';
    el.appendChild(document.createTextNode(text));
    if (mitTelefon) {
      el.appendChild(document.createTextNode(' '));
      var a = document.createElement('a');
      a.href = 'tel:' + PHONE.replace(/\s/g, '');
      a.textContent = PHONE;
      el.appendChild(a);
    }
  }

  /* Foto verkleinern -> JPEG-Blob. Klappt das Dekodieren nicht, Original nehmen. */
  function verkleinere(file) {
    if (!window.createImageBitmap || !/^image\//.test(file.type)) return Promise.resolve(file);
    return createImageBitmap(file).then(function (bmp) {
      var f = Math.min(1, MAX_KANTE / Math.max(bmp.width, bmp.height));
      var c = document.createElement('canvas');
      c.width = Math.round(bmp.width * f);
      c.height = Math.round(bmp.height * f);
      c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
      if (bmp.close) bmp.close();
      return new Promise(function (res) {
        c.toBlob(function (blob) { res(blob || file); }, 'image/jpeg', QUALITAET);
      });
    }).catch(function () { return file; });
  }

  function fehlerText(code) {
    if (code === 'zu_viele') return [TEXT.zuViele, false];
    if (code === 'foto_zu_gross') return [TEXT.fotoGross, false];
    if (code === 'fototyp') return [TEXT.fotoTyp, false];
    if (code === 'zu_viele_fotos') return [TEXT.fotoAnzahl, false];
    return [TEXT.fehler, true];
  }

  function senden(form, formular) {
    var buttons = form.querySelectorAll('button[type="submit"]');
    var data = new FormData();

    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || el.disabled || el.type === 'file' || el.type === 'submit') return;
      if (el.type === 'checkbox') return;
      data.append(el.name, String(el.value).trim());
    });
    var consent = form.elements.consent;
    data.append('consent', consent && consent.checked ? 'ja' : '');
    data.append('formular', formular);
    data.append('seite', location.pathname);
    data.append('sprache', document.documentElement.lang || 'de');
    data.append('t', String(Math.round(loaded())));

    var input = form.querySelector('input[type="file"][name="fotos"]');
    var files = input && input.files ? Array.prototype.slice.call(input.files) : [];
    if (files.length > MAX_FOTOS) {
      zeige(form, 'fehler', TEXT.fotoAnzahl);
      return Promise.reject(new Error('fotos'));
    }

    Array.prototype.forEach.call(buttons, function (b) { b.disabled = true; });
    form.setAttribute('aria-busy', 'true');
    zeige(form, 'laeuft', TEXT.senden);

    var fertig = function () {
      Array.prototype.forEach.call(buttons, function (b) { b.disabled = false; });
      form.removeAttribute('aria-busy');
    };

    return Promise.all(files.map(verkleinere)).then(function (blobs) {
      blobs.forEach(function (b, i) {
        var name = 'foto-' + (i + 1) + (b.type === 'image/png' ? '.png' : b.type === 'image/webp' ? '.webp' : '.jpg');
        data.append('fotos', b, name);
      });
      return fetch(ENDPOINT, { method: 'POST', body: data, mode: 'cors', credentials: 'omit' });
    }).then(function (res) {
      return res.json().catch(function () { return { ok: false, fehler: 'antwort' }; });
    }).then(function (body) {
      fertig();
      if (body && body.ok) {
        form.reset();
        zeige(form, 'ok', TEXT.ok);
        return body;
      }
      var t = fehlerText(body && body.fehler);
      zeige(form, 'fehler', t[0], t[1]);
      throw new Error(body && body.fehler || 'fehler');
    }, function (err) {
      fertig();
      if (err && err.message === 'fotos') throw err;
      zeige(form, 'fehler', navigator.onLine === false ? TEXT.offline : TEXT.fehler, navigator.onLine !== false);
      throw err;
    });
  }

  document.querySelectorAll('#anfrage-form, form[data-ankauf]').forEach(honeypot);

  window.ECSAnfrage = { senden: senden };
})();
