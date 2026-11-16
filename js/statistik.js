/* =========================================================================
   ECS GmbH – eigene Besucherstatistik (ohne Cookies)

   Zählt Seitenaufrufe und Kontakt-Klicks (Anruf, WhatsApp, E-Mail, Formular,
   PDF-Download). Es wird nichts auf dem Gerät gespeichert oder ausgelesen,
   keine IP-Adresse gespeichert und kein Profil gebildet. Details: /datenschutz

   Nicht gezählt wird: außerhalb von elegancecarsafi.com (lokale Vorschau),
   bei aktivem "Global Privacy Control", in automatisierten Browsern und wenn
   der Besucher die Statistik auf der Datenschutzseite abgeschaltet hat.

   Andere Skripte:  window.ECSTrack(name, daten)   (main.js, ankauf.js)
   Datenschutzseite: window.ECSStatistik.aus() / .an() / .istAus()
   ========================================================================= */
(function () {
  'use strict';

  var ENDPOINT = 'https://ecs-statistik.ecs-statistik.workers.dev/e';
  var OPT_OUT = 'ecs-statistik-aus';

  function optedOut() {
    try { return window.localStorage.getItem(OPT_OUT) === '1'; } catch (e) { return false; }
  }

  window.ECSStatistik = {
    istAus: optedOut,
    aus: function () { try { window.localStorage.setItem(OPT_OUT, '1'); } catch (e) {} },
    an: function () { try { window.localStorage.removeItem(OPT_OUT); } catch (e) {} }
  };

  var active = /(^|\.)elegancecarsafi\.com$/.test(window.location.hostname) &&
    !navigator.webdriver && !navigator.globalPrivacyControl;

  /* Schalter auf der Datenschutzseite (Widerspruch für diesen Browser) */
  document.querySelectorAll('[data-statistik-schalter]').forEach(function (btn) {
    var status = btn.parentNode.querySelector('[data-statistik-status]');
    function update() {
      var off = optedOut() || !!navigator.globalPrivacyControl;
      btn.hidden = !!navigator.globalPrivacyControl;
      btn.textContent = optedOut()
        ? 'Statistik für diesen Browser wieder aktivieren'
        : 'Statistik für diesen Browser deaktivieren';
      if (status) {
        status.textContent = '(derzeit: ' + (off ? 'deaktiviert' : 'aktiv') + ')';
      }
    }
    btn.addEventListener('click', function () {
      if (optedOut()) window.ECSStatistik.an(); else window.ECSStatistik.aus();
      update();
    });
    update();
  });

  /* /index.html, /kontakt.html und /kontakt/ zählen als dieselbe Seite. */
  function pagePath() {
    var p = window.location.pathname.replace(/\/index(\.html)?$/, '/').replace(/\.html$/, '');
    if (p.length > 1) p = p.replace(/\/+$/, '');
    return p || '/';
  }

  function send(type, label, extra) {
    if (!active || optedOut()) return;
    var data = { t: type, p: pagePath() };
    if (label) data.l = String(label).slice(0, 80);
    if (extra) for (var k in extra) if (extra[k]) data[k] = extra[k];
    var body = JSON.stringify(data);
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, body)) return;
    } catch (e) { /* weiter mit fetch */ }
    try {
      fetch(ENDPOINT, { method: 'POST', body: body, keepalive: true, mode: 'cors', credentials: 'omit' });
    } catch (e) { /* Statistik darf nie die Seite stören */ }
  }

  /* ------------------------------------------------------ Seitenaufruf */
  function pageview() {
    var params = new URLSearchParams(window.location.search);
    var ref = '';
    try { if (document.referrer) ref = new URL(document.referrer).hostname; } catch (e) {}
    if (ref === window.location.hostname) ref = '';
    send('view', pagePath() === '/fahrzeug' ? params.get('id') : '', {
      r: ref,
      s: params.get('utm_source') || params.get('ref') || '',
      lg: (document.documentElement.lang || '').slice(0, 2)
    });
  }

  /* Von den Speculation Rules vorgeladene Seiten erst zählen, wenn sie
     wirklich angezeigt werden. Die Sprache setzt i18n.js im <head>. */
  if (document.prerendering) {
    document.addEventListener('prerenderingchange', pageview, { once: true });
  } else {
    pageview();
  }

  /* ------------------------------------------- Ereignisse anderer Skripte */
  window.ECSTrack = function (name, data) {
    data = data || {};
    if (name === 'ankauf_formular') send('form', 'ankauf-' + (data.kanal || 'whatsapp'));
    else if (name === 'kontakt_formular') send('form', 'kontakt');
  };

  /* --------------------------------------------------- Kontakt-Klicks */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var where = a.closest('.mobile-cta') ? 'leiste'
      : a.closest('footer') ? 'footer'
      : a.closest('header, .nav, .site-header') ? 'kopf'
      : 'seite';

    if (/^tel:/i.test(href)) send('call', where);
    else if (/(^|\/\/)(wa\.me|api\.whatsapp\.com)\//i.test(href)) send('whatsapp', where);
    else if (/^mailto:/i.test(href)) send('mail', where);
    else if (/\.pdf(\?|#|$)/i.test(href)) send('download', href.split(/[?#]/)[0].split('/').pop());
  }, true);
})();
