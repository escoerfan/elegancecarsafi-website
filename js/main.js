/* =========================================================================
   ECS GmbH – Elegance Car Safi
   Interaktionen: Mobilmenü, Scroll-Reveal, Kontaktformular, Karte
   ========================================================================= */
(function () {
  'use strict';

  /* --------------------------------------------------------- Mobilmenü */
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('site-nav');

  if (toggle && nav) {
    var setMenu = function (open) {
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
      document.body.style.overflow = open ? 'hidden' : '';
    };

    toggle.addEventListener('click', function () {
      setMenu(!nav.classList.contains('is-open'));
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });

    /* Escape schließt das Menü; beim Wechsel auf Desktop-Breite darf die
       Seite nicht gesperrt bleiben */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        setMenu(false);
        toggle.focus();
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 991 && nav.classList.contains('is-open')) setMenu(false);
    });
  }

  /* ------------------------------------------- Untermenü (Ankaufseiten)
     "Unsere Arbeit" öffnet per Klick ein Untermenü (Desktop: Dropdown,
     Handy: klappt im Menü auf). Klick daneben oder Escape schließt es. */
  var subItems = document.querySelectorAll('.nav-item--sub');

  var setSub = function (item, open) {
    item.classList.toggle('is-open', open);
    item.querySelector('.nav-sub__toggle').setAttribute('aria-expanded', String(open));
  };

  subItems.forEach(function (item) {
    item.querySelector('.nav-sub__toggle').addEventListener('click', function (e) {
      e.stopPropagation();
      setSub(item, !item.classList.contains('is-open'));
    });
  });

  document.addEventListener('click', function (e) {
    subItems.forEach(function (item) {
      if (item.classList.contains('is-open') && !item.contains(e.target)) setSub(item, false);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    subItems.forEach(function (item) {
      if (!item.classList.contains('is-open')) return;
      setSub(item, false);
      item.querySelector('.nav-sub__toggle').focus();
    });
  });

  /* ------------------------------------- Kopfzeile beim Scrollen (Glas) */
  var header = document.getElementById('site-header');

  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 40);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------------------------------ Scroll-Reveal */
  var revealables = document.querySelectorAll('.reveal');

  if ('IntersectionObserver' in window && revealables.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });

    revealables.forEach(function (el) { io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ------------------------------------------------------------ Zähler
     <span class="count" data-count="250">250</span> zählt beim ersten
     Sichtbarwerden von 0 hoch. Im HTML steht der Endwert – ohne JS oder
     bei "Bewegung reduzieren" bleibt er einfach stehen.                 */
  var counters = document.querySelectorAll('[data-count]');
  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (counters.length && 'IntersectionObserver' in window && !reduceMotion) {
    var runCounter = function (el) {
      var target = parseInt(el.getAttribute('data-count'), 10);
      var duration = 1800;
      var start = null;

      /* Breite des Endwerts messen (Schrift ist jetzt geladen) und reservieren,
         damit der Text beim Zählen nicht springt – ohne dass der Endwert aufblitzt */
      el.style.minWidth = '';
      el.textContent = String(target);
      el.style.minWidth = el.getBoundingClientRect().width + 'px';
      el.textContent = '0';

      var step = function (now) {
        if (start === null) start = now;
        var t = Math.min((now - start) / duration, 1);
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = String(Math.round(target * eased));
        if (t < 1) window.requestAnimationFrame(step);
        else el.style.minWidth = '';
      };

      window.requestAnimationFrame(step);
    };

    var countIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        countIo.unobserve(entry.target);
        runCounter(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.5 });

    counters.forEach(function (el) {
      var target = parseInt(el.getAttribute('data-count'), 10);
      if (isNaN(target)) return;
      el.style.minWidth = String(target).length + 'ch';  /* grob, bis gezählt wird */
      el.textContent = '0';
      countIo.observe(el);
    });
  }

  /* --------------------------------------------------- Kontaktformular
     Statische Seite ohne Server: die Anfrage wird als vorbereitete
     E-Mail im Mailprogramm des Besuchers geöffnet.
     Umstieg auf einen Formulardienst später: statt mailto einfach
     action/method am <form> setzen und diesen Handler entfernen.        */
  var form = document.getElementById('anfrage-form');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      if (!form.reportValidity()) return;

      var get = function (name) {
        var el = form.elements[name];
        return el ? String(el.value).trim() : '';
      };

      var vorname = get('vorname');
      var nachname = get('nachname');
      var leistung = get('dienstleistung');

      var betreff = 'Anfrage über die Website – ' + (leistung || 'Allgemein');

      var text = [
        'Name: ' + vorname + ' ' + nachname,
        'E-Mail: ' + get('email'),
        'Dienstleistungstyp: ' + leistung,
        '',
        'Nachricht:',
        get('nachricht'),
        '',
        '---',
        'Gesendet über elegancecarsafi.com'
      ].join('\n');

      window.location.href =
        'mailto:info@elegancecarsafi.com' +
        '?subject=' + encodeURIComponent(betreff) +
        '&body=' + encodeURIComponent(text);
    });
  }

  /* ---------------------------------------------------------- Karte
     Google Maps (Einbettung ohne API-Key) wird erst nach Einwilligung
     "Externe Medien" geladen (js/cookie-consent.js). Bis dahin steht ein
     Platzhalter da und es geht keine Verbindung zu Google raus.          */
  var mapEl = document.getElementById('map');
  var consent = window.ECSConsent;

  if (mapEl) {
    var map = null;
    var MAP_QUERY = 'ECS Exclusive Commerce Services GmbH, Bünteweg 13, 30989 Gehrden';

    var showMap = function () {
      if (map) return;
      var lang = (document.documentElement.lang || 'de').slice(0, 2);

      map = document.createElement('iframe');
      map.src = 'https://www.google.com/maps?q=' + encodeURIComponent(MAP_QUERY) +
        '&z=17&hl=' + lang + '&output=embed';
      map.title = 'Google-Maps-Karte mit dem Standort der ECS GmbH in Gehrden';
      map.loading = 'lazy';
      map.referrerPolicy = 'no-referrer';
      map.allowFullscreen = true;

      mapEl.innerHTML = '';
      mapEl.appendChild(map);
    };

    var showPlaceholder = function () {
      map = null;
      mapEl.innerHTML =
        '<div class="map-consent">' +
          '<p>Hier sehen Sie unseren Standort auf einer Karte von Google Maps. Beim Laden werden ' +
          'Daten wie Ihre IP-Adresse an Google übertragen. Mehr in der ' +
          '<a href="datenschutz">Datenschutzerklärung</a>.</p>' +
          '<button class="btn btn--secondary btn--sm" type="button">Karte laden</button>' +
        '</div>';

      mapEl.querySelector('button').addEventListener('click', function () {
        if (consent) consent.grant('media');
        else showMap();
      });
    };

    if (!consent || consent.has('media')) showMap();
    else showPlaceholder();

    if (consent) {
      consent.onChange(function (c) {
        if (c.media) showMap();
        else showPlaceholder();
      });
    }
  }
})();

/* ---------------------------------------------------------- Tracking
   Vorbereitet, aber inaktiv: Ereignisse (Anruf-Klick, WhatsApp-Klick,
   Ankauf-Formular) landen nur im dataLayer, wenn eine Einwilligung
   "statistics" vorliegt. Die gibt es im Cookie-Banner derzeit nicht, und es
   wird kein Statistik-Tool geladen – deshalb passiert aktuell nichts.
   Später: Kategorie "statistics" in js/cookie-consent.js ergänzen und das
   Tool (z. B. GA4/Matomo) erst nach Einwilligung laden.               */
(function () {
  'use strict';

  window.ECSTrack = function (name, data) {
    var consent = window.ECSConsent;
    if (!consent || !consent.has('statistics')) return;
    var entry = { event: name };
    for (var k in data) if (Object.prototype.hasOwnProperty.call(data, k)) entry[k] = data[k];
    (window.dataLayer = window.dataLayer || []).push(entry);
  };

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="tel:"], a[href*="wa.me/"]');
    if (!a) return;
    var where = a.closest('.mobile-cta') ? 'leiste' : (a.closest('footer') ? 'footer' : 'seite');
    window.ECSTrack(a.href.indexOf('tel:') === 0 ? 'anruf_klick' : 'whatsapp_klick', { ort: where });
  });
})();
