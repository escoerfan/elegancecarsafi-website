/* =========================================================================
   ECS GmbH – Elegance Car Safi
   Ankauf-Formular (Ankaufseiten)

   Kein Server: Aus den Angaben wird eine fertige Nachricht gebaut und
   WhatsApp bzw. das E-Mail-Programm geöffnet. Abgeschickt wird erst dort,
   Fotos hängt der Kunde dort an. Die Nachricht bleibt bewusst deutsch.
   ========================================================================= */
(function () {
  'use strict';

  var PHONE = '491713621298';
  var MAIL = 'info@elegancecarsafi.com';

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
      text.push('', channel === 'email' ? 'Fotos: siehe Anhang' : 'Fotos schicke ich hier im Chat.');
      text = text.join('\n');

      if (window.ECSTrack) window.ECSTrack('ankauf_formular', { kanal: channel, typ: get('typ') });

      if (channel === 'email') {
        var betreff = 'Ankauf-Anfrage: ' + get('typ') + ' – ' + get('modell');
        window.location.href = 'mailto:' + MAIL +
          '?subject=' + encodeURIComponent(betreff) +
          '&body=' + encodeURIComponent(text);
      } else {
        var url = 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(text);
        /* Ohne "noopener"-Feature, sonst liefert window.open immer null */
        var win = window.open(url, '_blank');
        if (win) win.opener = null;
        else window.location.href = url;   /* Popup blockiert */
      }
    });
  });
})();
