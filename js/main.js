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

  /* -------------------------------------------------------- Vorteile
     Der Vorteil, der der Bildschirmmitte am nächsten ist, leuchtet auf. */
  var why = document.querySelector('.why');
  var whyItems = why ? why.querySelectorAll('.why-item') : [];

  if (whyItems.length) {
    why.classList.add('is-interactive');
    var ticking = false;

    var updateWhy = function () {
      ticking = false;
      var mid = window.innerHeight / 2;
      var best = null;
      var bestDist = Infinity;

      whyItems.forEach(function (item) {
        var r = item.getBoundingClientRect();
        var dist = Math.abs(r.top + r.height / 2 - mid);
        if (dist < bestDist) { bestDist = dist; best = item; }
      });

      whyItems.forEach(function (item) {
        item.classList.toggle('is-active', item === best);
      });
    };

    var requestWhy = function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(updateWhy); }
    };

    updateWhy();
    window.addEventListener('scroll', requestWhy, { passive: true });
    window.addEventListener('resize', requestWhy);
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
     Leaflet + OpenStreetMap werden erst nach Einwilligung "Externe Medien"
     geladen (js/cookie-consent.js). Bis dahin steht ein Platzhalter da.   */
  var mapEl = document.getElementById('map');
  var consent = window.ECSConsent;

  if (mapEl) {
    var map = null;
    var leafletLoading = null;

    var loadLeaflet = function () {
      if (window.L) return Promise.resolve();
      if (leafletLoading) return leafletLoading;

      leafletLoading = new Promise(function (resolve, reject) {
        var css = document.createElement('link');
        css.rel = 'stylesheet';
        css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(css);

        var js = document.createElement('script');
        js.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        js.onload = resolve;
        js.onerror = reject;
        document.head.appendChild(js);
      });
      return leafletLoading;
    };

    var showMap = function () {
      if (map) return;
      mapEl.innerHTML = '';

      loadLeaflet().then(function () {
        if (map || (consent && !consent.has('media'))) return;
        var lat = 52.3225528;
        var lng = 9.5968503;

        map = L.map(mapEl, { scrollWheelZoom: false }).setView([lat, lng], 17);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        L.marker([lat, lng]).addTo(map)
          .bindPopup('<strong>ECS GmbH</strong><br>Bünteweg 13<br>30989 Gehrden');
      });
    };

    var showPlaceholder = function () {
      if (map) { map.remove(); map = null; }
      mapEl.innerHTML =
        '<div class="map-consent">' +
          '<p>Hier sehen Sie unseren Standort auf einer Karte von OpenStreetMap. Beim Laden wird ' +
          'Ihre IP-Adresse an den Anbieter übertragen. Mehr in der ' +
          '<a href="datenschutz.html">Datenschutzerklärung</a>.</p>' +
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
