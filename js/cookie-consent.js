/* =========================================================================
   ECS GmbH – Elegance Car Safi
   Cookie-Banner / Einwilligungsverwaltung

   Die Seite setzt selbst keine Tracking-Cookies. Einwilligungspflichtig sind
   nur "Externe Medien" (Standortkarte über OpenStreetMap/unpkg). Die Auswahl
   wird im localStorage des Besuchers gespeichert (technisch notwendig).

   Andere Skripte:  window.ECSConsent.has('media')
                    window.ECSConsent.onChange(function (consent) { ... })
   Banner erneut öffnen: Element mit Attribut data-cookie-settings

   Gestaltung nach den Vorgaben der Datenschutzbehörden: "Nur notwendige" und
   "Alle akzeptieren" gleich gewichtet, keine vorausgewählten Häkchen,
   Datenschutz und Impressum verlinkt, Widerruf jederzeit über den Footer.
   VERSION erhöhen, wenn sich Kategorien oder Texte ändern – dann wird neu gefragt.
   ========================================================================= */
(function () {
  'use strict';

  var STORAGE_KEY = 'ecs-cookie-consent';
  var VERSION = 2;
  var listeners = [];
  var banner = null;

  function read() {
    try {
      var data = JSON.parse(window.localStorage.getItem(STORAGE_KEY));
      return data && data.v === VERSION ? data : null;
    } catch (e) {
      return null;
    }
  }

  function save(media) {
    var data = { v: VERSION, media: !!media, date: new Date().toISOString() };
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) { /* Speicher blockiert – Auswahl gilt nur für diesen Seitenaufruf */ }
    current = data;
    listeners.forEach(function (fn) { fn(data); });
  }

  var current = read();

  window.ECSConsent = {
    has: function (category) {
      return !!(current && current[category]);
    },
    onChange: function (fn) {
      listeners.push(fn);
    },
    grant: function (category) {
      if (category === 'media') save(true);
    },
    open: open
  };

  function close() {
    if (!banner) return;
    banner.remove();
    banner = null;
  }

  function open() {
    close();

    banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-labelledby', 'cookie-banner-title');
    banner.innerHTML =
      '<p class="cookie-banner__title" id="cookie-banner-title">Cookies &amp; Datenschutz</p>' +
      '<p class="cookie-banner__text" id="cookie-banner-text">' +
        'Wir setzen keine Analyse- oder Werbe-Cookies. Technisch notwendig ist nur das Speichern ' +
        'Ihrer Auswahl. Mit Ihrer Einwilligung laden wir zusätzlich externe Medien (Standortkarte ' +
        'von OpenStreetMap), dabei wird Ihre IP-Adresse an den Anbieter übertragen. Ihre Auswahl ' +
        'können Sie jederzeit über „Cookie-Einstellungen“ im Seitenfuß ändern.' +
      '</p>' +
      '<p class="cookie-banner__links">' +
        '<a href="datenschutz">Datenschutzerklärung</a>' +
        '<a href="impressum">Impressum</a>' +
      '</p>' +
      '<div class="cookie-banner__options" hidden>' +
        '<label class="cookie-option">' +
          '<input type="checkbox" checked disabled>' +
          '<span><strong>Notwendig</strong>Speichert Ihre Cookie-Auswahl und gegebenenfalls Ihre Sprachwahl im Browser. Immer aktiv.</span>' +
        '</label>' +
        '<label class="cookie-option">' +
          '<input type="checkbox" data-consent="media"' + (window.ECSConsent.has('media') ? ' checked' : '') + '>' +
          '<span><strong>Externe Medien</strong>Standortkarte von OpenStreetMap auf der Kontaktseite, inklusive Kartenbibliothek Leaflet (unpkg).</span>' +
        '</label>' +
      '</div>' +
      '<div class="cookie-banner__actions">' +
        '<button class="btn btn--secondary" type="button" data-action="necessary">Nur notwendige</button>' +
        '<button class="btn btn--secondary" type="button" data-action="all">Alle akzeptieren</button>' +
        '<button class="btn btn--secondary btn--wide" type="button" data-action="save" hidden>Auswahl speichern</button>' +
      '</div>' +
      '<button class="cookie-banner__link" type="button" data-action="settings">Einstellungen</button>';
    banner.setAttribute('aria-describedby', 'cookie-banner-text');

    banner.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-action]');
      if (!btn) return;

      switch (btn.getAttribute('data-action')) {
        case 'all':
          save(true);
          close();
          break;
        case 'necessary':
          save(false);
          close();
          break;
        case 'save':
          save(banner.querySelector('[data-consent="media"]').checked);
          close();
          break;
        case 'settings':
          banner.querySelector('.cookie-banner__options').hidden = false;
          banner.querySelector('[data-action="save"]').hidden = false;
          btn.hidden = true;
          break;
      }
    });

    document.body.appendChild(banner);
  }

  document.addEventListener('click', function (e) {
    if (!e.target.closest('[data-cookie-settings]')) return;
    e.preventDefault();
    open();
  });

  if (!current) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', open);
    } else {
      open();
    }
  }
})();
