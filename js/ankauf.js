/* =========================================================================
   ECS GmbH – Elegance Car Safi
   Ankauf-Formular (Ankaufseiten)

   Zwei Wege: „Anfrage direkt senden“ schickt die Angaben (mit Fotos)
   sofort per E-Mail an uns (js/anfrage.js, kein Mailprogramm).
   „Per WhatsApp senden“ öffnet WhatsApp mit fertiger Nachricht, Fotos
   hängt der Kunde dort an. Die Nachricht bleibt bewusst deutsch.
   ========================================================================= */
(function () {
  'use strict';

  var PHONE = '4915140315387';

  var forms = document.querySelectorAll('form[data-ankauf]');

  forms.forEach(function (form) {
    var lastChannel = 'whatsapp';

    /* Welcher der beiden Buttons wurde geklickt? (Fallback für ältere Browser) */
    form.querySelectorAll('button[type="submit"]').forEach(function (btn) {
      btn.addEventListener('click', function () { lastChannel = btn.value; });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;

      var channel = (e.submitter && e.submitter.value) || lastChannel;

      var get = function (name) {
        var el = form.elements[name];
        return el ? String(el.value).trim() : '';
      };

      if (channel === 'email') {
        /* Rückweg nötig: Telefon oder E-Mail */
        if (!get('telefon') && !get('email')) {
          var tel = form.elements.telefon;
          var hinweis = 'Bitte Telefon oder E-Mail angeben, damit wir Sie erreichen können.';
          var dict = window.ECSLang && window.ECS_I18N && window.ECS_I18N[window.ECSLang.get()];
          tel.setCustomValidity((dict && dict[hinweis]) || hinweis);
          tel.reportValidity();
          tel.addEventListener('input', function clear() { tel.setCustomValidity(''); tel.removeEventListener('input', clear); });
          return;
        }
        if (!window.ECSAnfrage) return;
        var typ = get('typ');
        window.ECSAnfrage.senden(form, 'ankauf').then(function () {
          if (window.ECSTrack) window.ECSTrack('ankauf_formular', { kanal: 'email', typ: typ });
        }, function () {});
        return;
      }

      var zeilen = [
        ['Fahrzeugtyp', get('typ')],
        ['Marke und Modell', get('modell')],
        ['Baujahr', get('baujahr')],
        ['Kilometerstand', get('km')],
        ['Standort', get('ort')],
        ['Name', get('name')],
        ['Firma', get('firma')],
        ['Telefon', get('telefon')],
        ['E-Mail', get('email')]
      ].filter(function (z) { return z[1]; })
        .map(function (z) { return z[0] + ': ' + z[1]; });

      var nachricht = get('nachricht');
      var text = ['Ankauf-Anfrage über elegancecarsafi.com', ''].concat(zeilen);
      if (nachricht) text.push('', 'Weitere Angaben:', nachricht);
      text.push('', 'Fotos schicke ich hier im Chat.');
      text = text.join('\n');

      if (window.ECSTrack) window.ECSTrack('ankauf_formular', { kanal: 'whatsapp', typ: get('typ') });

      var url = 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(text);
      /* Ohne "noopener"-Feature, sonst liefert window.open immer null */
      var win = window.open(url, '_blank');
      if (win) win.opener = null;
      else window.location.href = url;   /* Popup blockiert */
    });
  });
})();
