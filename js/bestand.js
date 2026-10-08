/* =========================================================================
   ECS GmbH – Fahrzeugbestand
   Lädt bestand.json von GitHub und rendert je nach Seite:
   - #vw-grid    Kartenliste (fahrzeuge.html, Vorschau auf index.html)
                 data-limit="3" zeigt nur die ersten n Fahrzeuge
                 #vw-filter (optional) = Kategorie-Filter
   - #vw-detail  Einzelseite eines Fahrzeugs (fahrzeug.html?id=…)
   Karten öffnen die Einzelseite in einem neuen Tab.
   ========================================================================= */
(function () {
  var JSON_URL =
    'https://raw.githubusercontent.com/escoerfan/ecs-bestand/main/bestand.json';

  /* true = Preis in bestand.json ist netto, false = brutto */
  var PREIS_IST_NETTO = false;
  var MWST = 0.19;
  var STANDORT = 'Gehrden, Deutschland';

  var BS = String.fromCharCode(92);
  var NL = String.fromCharCode(10);
  var CR = String.fromCharCode(13);
  var DOT = String.fromCharCode(8226);

  var LKW = 'Lkw ' + String.fromCharCode(252) + 'ber 7,5 t';
  var TRSP = 'Transporter bis 7,5 t';
  var SATT = 'Sattelzugmaschine';
  var AUFL = 'Auflieger';
  var BUS = 'Bus';
  var PKW = 'Pkw';
  var SONS = 'Sonstige';

  var CAT_ORDER = [LKW, SATT, AUFL, BUS, TRSP, PKW, SONS];

  var CAT = {
    SwapChassisTruck: LKW,
    BoxTruck: LKW,
    BoxBodyTruck: LKW,
    StakeBodyAndTarpaulinTruck: LKW,
    StakeBodyTruck: LKW,
    RollOffTipperTruck: LKW,
    TipperTruck: LKW,
    RefrigeratorBodyTruck: LKW,
    ChassisTruck: LKW,
    HeavyTruck: LKW,
    StandardTractorAndTrailerUnit: SATT,
    OtherSemiTrailerTruck: SATT,
    SaddleTractor: SATT,
    TipperSemiTrailer: AUFL,
    CurtainsiderSemitrailer: AUFL,
    FlatbedSemiTrailer: AUFL,
    BoxSemiTrailer: AUFL,
    RefrigeratorSemiTrailer: AUFL,
    OtherSemiTrailer: AUFL,
    Trailer: AUFL,
    BoxTypeDeliveryVan: TRSP,
    OtherVanUpTo7500: TRSP,
    Van: TRSP,
    MiniVan: TRSP,
    PanelVan: TRSP,
    LightTruck: TRSP,
    PublicServiceVehicleBus: BUS,
    CrossCountryBus: BUS,
    CityBus: BUS,
    CoachBus: BUS,
    DoubleDeckerBus: BUS,
    Limousine: PKW,
    EstateCar: PKW,
    OffRoad: PKW,
    Cabrio: PKW,
    SportsCar: PKW
  };

  var VAN_NAMEN = [
    'sprinter',
    'crafter',
    'transit',
    'ducato',
    'kangoo',
    'vito',
    'caddy',
    'jumper',
    'boxer',
    'master',
    'daily',
    'combo',
    'expert',
    'jumpy',
    'vivaro',
    'trafic',
    'talento',
    'partner',
    'berlingo'
  ];

  function has(hay, needle) {
    return String(hay).toLowerCase().indexOf(needle) !== -1;
  }

  function catLabel(v) {
    var raw = String((v && v.category) || '');
    var lbl = CAT[raw];

    if (!lbl) {
      var r = raw.toLowerCase();

      if (r.indexOf('bus') !== -1) {
        lbl = BUS;
      } else if (r.indexOf('tractor') !== -1) {
        lbl = SATT;
      } else if (r.indexOf('trailer') !== -1) {
        lbl = AUFL;
      } else if (r.indexOf('van') !== -1) {
        lbl = TRSP;
      } else if (r.indexOf('truck') !== -1) {
        lbl = LKW;
      } else if (
        r.indexOf('car') !== -1 ||
        r.indexOf('limousine') !== -1
      ) {
        lbl = PKW;
      } else {
        lbl = SONS;
      }
    }

    if (lbl === LKW) {
      var t = String((v && v.title) || '');

      for (var i = 0; i < VAN_NAMEN.length; i++) {
        if (has(t, VAN_NAMEN[i])) {
          lbl = TRSP;
          break;
        }
      }
    }

    return lbl;
  }

  function euro(n) {
    return n.toLocaleString('de-DE', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    });
  }

  function onlyDigits(val) {
    var s = String(val || '');
    var out = '';

    for (var i = 0; i < s.length; i++) {
      var c = s.charAt(i);

      if (c >= '0' && c <= '9') {
        out += c;
      }
    }

    return out;
  }

  function toNumber(val) {
    var s = String(val || '');
    var out = '';

    for (var i = 0; i < s.length; i++) {
      var c = s.charAt(i);

      if ((c >= '0' && c <= '9') || c === '.') {
        out += c;
      }
    }

    return parseFloat(out);
  }

  function fmtPrice(v) {
    var n = toNumber(v.price);

    if (!n || isNaN(n)) {
      return {
        text: 'Preis auf Anfrage',
        label: '',
        gross: '',
        onRequest: true
      };
    }

    /* Ohne ausweisbare MwSt. (vat === false, z. B. Differenzbesteuerung) nur Brutto */
    if (v.vat === false) {
      return {
        text: euro(n),
        label: 'Brutto',
        gross: '',
        onRequest: false
      };
    }

    var netApi = toNumber(v.priceNet);
    var net = netApi ? netApi : (PREIS_IST_NETTO ? n : n / (1 + MWST));
    var gross = PREIS_IST_NETTO ? n * (1 + MWST) : n;

    return {
      text: euro(net),
      label: 'Netto',
      gross: 'Brutto: ' + euro(gross),
      onRequest: false
    };
  }

  function fmtKm(val) {
    var n = parseInt(onlyDigits(val), 10);

    return n ? n.toLocaleString('de-DE') + ' km' : null;
  }

  function fmtReg(val) {
    var s = String(val || '');

    if (!s) {
      return null;
    }

    if (s.length === 6) {
      return s.slice(4, 6) + '/' + s.slice(0, 4);
    }

    if (s.indexOf('-') !== -1) {
      var p = s.split('-');
      return (p[1] || '') + '/' + p[0];
    }

    return s;
  }

  function fmtPower(v) {
    var s = String(v.description || '');
    var pos = s.toLowerCase().indexOf('kw');

    if (pos < 1) {
      return null;
    }

    var i = pos - 1;

    while (i >= 0 && s.charAt(i) === ' ') {
      i--;
    }

    var num = '';

    while (
      i >= 0 &&
      s.charAt(i) >= '0' &&
      s.charAt(i) <= '9'
    ) {
      num = s.charAt(i) + num;
      i--;
    }

    var kw = parseInt(num, 10);

    if (!kw || kw < 30 || kw > 900) {
      return null;
    }

    return kw + ' kW (' + Math.round(kw * 1.35962) + ' PS)';
  }

  function fmtFuel(v) {
    var list = [
      'Diesel',
      'Benzin',
      'Elektro',
      'Hybrid',
      'Erdgas',
      'Autogas'
    ];

    var d = String(v.description || '');

    for (var i = 0; i < list.length; i++) {
      if (has(d, list[i].toLowerCase())) {
        return list[i];
      }
    }

    return null;
  }

  function fmtSeats(v) {
    var s = String(v.description || '');
    var key = 'sitzpl';
    var pos = s.toLowerCase().indexOf(key);

    if (pos < 1) {
      return null;
    }

    var i = pos - 1;

    while (i >= 0 && s.charAt(i) === ' ') {
      i--;
    }

    var num = '';

    while (
      i >= 0 &&
      s.charAt(i) >= '0' &&
      s.charAt(i) <= '9'
    ) {
      num = s.charAt(i) + num;
      i--;
    }

    var n = parseInt(num, 10);

    return n
      ? n + ' Sitzpl' + String.fromCharCode(228) + 'tze'
      : null;
  }

  function esc(s) {
    var t = String(s);

    t = t.split('&').join('&amp;');
    t = t.split('<').join('&lt;');
    t = t.split('>').join('&gt;');
    t = t.split('"').join('&quot;');

    return t;
  }

  function normalize(raw) {
    var s = String(raw || '');

    s = s.split(BS + BS).join(NL);
    s = s.split(BS + 'n').join(NL);
    s = s.split(BS + 'r').join('');
    s = s.split(BS).join('');
    s = s.split(CR).join('');

    return s;
  }

  function cleanText(raw) {
    var s = normalize(raw);

    s = s.split('**').join('');

    var lines = s.split(NL);
    var out = [];

    for (var i = 0; i < lines.length; i++) {
      var t = lines[i];

      while (t.length && t.charAt(0) === ' ') {
        t = t.slice(1);
      }

      var bullet = false;

      while (
        t.length &&
        (t.charAt(0) === '*' || t.charAt(0) === '-')
      ) {
        t = t.slice(1);
        bullet = true;

        while (t.length && t.charAt(0) === ' ') {
          t = t.slice(1);
        }
      }

      t = t.split('*').join('');

      while (
        t.length &&
        t.charAt(t.length - 1) === ' '
      ) {
        t = t.slice(0, -1);
      }

      if (bullet && t.length) {
        t = DOT + ' ' + t;
      }

      if (
        t === '' &&
        out.length &&
        out[out.length - 1] === ''
      ) {
        continue;
      }

      out.push(t);
    }

    while (out.length && out[0] === '') {
      out.shift();
    }

    while (
      out.length &&
      out[out.length - 1] === ''
    ) {
      out.pop();
    }

    return out.join(NL);
  }

  var TITEL_STOPP = [
    'ausstattung',
    'sonder',
    'sonstiges'
  ];

  var MARKEN_ALLEIN = [
    'mercedes-benz',
    'man',
    'schmitz',
    'volvo',
    'scania',
    'daf',
    'iveco',
    'ford',
    'renault',
    'langendorf'
  ];

  function schlechterTitel(t) {
    var low = String(t).toLowerCase();

    for (var i = 0; i < TITEL_STOPP.length; i++) {
      if (low.indexOf(TITEL_STOPP[i]) === 0) {
        return true;
      }
    }

    for (var j = 0; j < MARKEN_ALLEIN.length; j++) {
      if (low === MARKEN_ALLEIN[j]) {
        return true;
      }
    }

    return false;
  }

  function buildTitle(v) {
    var t = String(v.title || '').split('*').join('');

    while (t.length && t.charAt(0) === ' ') {
      t = t.slice(1);
    }

    while (
      t.length &&
      t.charAt(t.length - 1) === ' '
    ) {
      t = t.slice(0, -1);
    }

    if (t.length >= 4 && !schlechterTitel(t)) {
      return t;
    }

    if (v.description) {
      var d = normalize(v.description);
      var a = d.indexOf('**');

      if (a !== -1) {
        var b = d.indexOf('**', a + 2);

        if (b > a + 2) {
          var cand = d
            .slice(a + 2, b)
            .split('*')
            .join('');

          while (
            cand.length &&
            cand.charAt(0) === ' '
          ) {
            cand = cand.slice(1);
          }

          while (
            cand.length &&
            cand.charAt(cand.length - 1) === ' '
          ) {
            cand = cand.slice(0, -1);
          }

          if (
            cand.length >= 4 &&
            cand.length <= 140 &&
            !schlechterTitel(cand)
          ) {
            return cand;
          }
        }
      }
    }

    var mk = String(v.make || '');

    return mk
      ? mk + ' ' + catLabel(v)
      : catLabel(v);
  }

  var ICO = {
    pin:
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8a8a8a" stroke-width="2" aria-hidden="true"><path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',

    seat:
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#262626" stroke-width="1.7" aria-hidden="true"><path d="M6 4v9a3 3 0 0 0 3 3h6"/><path d="M18 16v4"/><path d="M6 20h9"/></svg>',

    cal:
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#262626" stroke-width="1.7" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',

    km:
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#262626" stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 12l4-3"/></svg>',

    kw:
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#262626" stroke-width="1.7" stroke-linejoin="round" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/></svg>',

    fuel:
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#262626" stroke-width="1.7" aria-hidden="true"><path d="M4 20V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v15"/><path d="M3 20h12"/><path d="M14 9h3a2 2 0 0 1 2 2v6a1.5 1.5 0 0 0 3 0v-7l-2.5-3"/></svg>'
  };

  function specRow(icon, text) {
    return (
      '<div class="vw-spec">' +
      icon +
      '<span>' +
      esc(text) +
      '</span></div>'
    );
  }

  function specsHtml(v) {
    var out = '';

    var r = fmtReg(v.firstRegistration);

    if (r) {
      out += specRow(
        ICO.cal,
        'Erstzulassung: ' + r
      );
    }

    var k = fmtKm(v.km);

    if (k) {
      out += specRow(ICO.km, k);
    }

    var p = fmtPower(v);

    if (p) {
      out += specRow(ICO.kw, p);
    }

    var f = fmtFuel(v);

    if (f) {
      out += specRow(ICO.fuel, f);
    }

    var s = fmtSeats(v);

    if (s) {
      out += specRow(ICO.seat, s);
    }

    return out;
  }

  function placeholder() {
    return (
      '<div class="vw-img-placeholder">' +
      '<svg width="52" height="52" viewBox="0 0 52 52" fill="none" aria-hidden="true">' +
      '<rect x="4" y="18" width="44" height="22" rx="4" stroke="#262626" stroke-width="2"/>' +
      '<path d="M8 18l6-10h24l6 10" stroke="#262626" stroke-width="2" stroke-linejoin="round"/>' +
      '<circle cx="14" cy="40" r="5" stroke="#262626" stroke-width="2"/>' +
      '<circle cx="38" cy="40" r="5" stroke="#262626" stroke-width="2"/>' +
      '</svg>' +
      '</div>'
    );
  }

  var DETAIL_SEITE = 'fahrzeug';
  var TEL = '+491713621298';
  var WHATSAPP = '491713621298';
  var MAIL = 'info@elegancecarsafi.com';

  /* mobile.de liefert Bilder in mehreren Größen – für die Einzelseite größer */
  function bigImage(url) {
    return String(url).split('rule=mo-640').join('rule=mo-1600');
  }

  function detailUrl(v) {
    return DETAIL_SEITE + '?id=' + encodeURIComponent(v.id);
  }

  /* ------------------------------------------------------------ Kartenliste */
  var _all = [];
  var _cats = [];
  var _aktiv = 'Alle';

  var RESERVED_HTML = '<div class="vw-reserved">Reserviert</div>';

  function renderCard(v) {
    var imgs = v.images || [];
    var title = buildTitle(v);
    var p = fmtPrice(v);
    var c = catLabel(v);
    var loc = v.location || STANDORT;

    var imgHtml = imgs.length
      ? '<img src="' + esc(imgs[0]) + '" alt="' + esc(title) + '" loading="lazy">'
      : placeholder();

    var sp = specsHtml(v);

    return (
      '<a class="vw-card" href="' + esc(detailUrl(v)) + '" target="_blank" rel="noopener">' +
        '<div class="vw-img-wrap">' +
          imgHtml +
          '<div class="vw-badge">' + esc(c) + '</div>' +
          (v.reserved ? RESERVED_HTML : '') +
        '</div>' +
        '<div class="vw-body">' +
          '<div class="vw-title">' + esc(title) + '</div>' +
          '<div class="vw-loc">' + ICO.pin + '<span>' + esc(loc) + '</span></div>' +
          (sp ? '<div class="vw-specs">' + sp + '</div>' : '') +
          '<div class="vw-detail">Details und technische Daten</div>' +
          '<div class="vw-footer">' +
            '<div>' +
              (p.label ? '<div class="vw-price-label">' + p.label + '</div>' : '') +
              '<div class="vw-price' + (p.onRequest ? ' on-request' : '') + '">' + p.text + '</div>' +
              (p.gross ? '<div class="vw-price-gross">' + p.gross + '</div>' : '') +
            '</div>' +
            '<div class="vw-card-cta">Jetzt anfragen</div>' +
          '</div>' +
        '</div>' +
      '</a>'
    );
  }

  function renderFilter(filterEl) {
    var counts = {};

    for (var i = 0; i < _all.length; i++) {
      var c = catLabel(_all[i]);
      counts[c] = (counts[c] || 0) + 1;
    }

    _cats = [];

    for (var j = 0; j < CAT_ORDER.length; j++) {
      if (counts[CAT_ORDER[j]]) {
        _cats.push(CAT_ORDER[j]);
      }
    }

    var html =
      '<button class="vw-filter-btn' + (_aktiv === 'Alle' ? ' active' : '') + '" data-cat="-1">' +
      'Alle<span class="vw-filter-cnt">' + _all.length + '</span></button>';

    for (var k = 0; k < _cats.length; k++) {
      html +=
        '<button class="vw-filter-btn' + (_cats[k] === _aktiv ? ' active' : '') + '" data-cat="' + k + '">' +
        esc(_cats[k]) + '<span class="vw-filter-cnt">' + counts[_cats[k]] + '</span></button>';
    }

    filterEl.innerHTML = html;
  }

  function renderGrid(grid, limit) {
    var list = [];

    for (var i = 0; i < _all.length; i++) {
      if (_aktiv === 'Alle' || catLabel(_all[i]) === _aktiv) {
        list.push(_all[i]);
      }
    }

    if (limit) {
      list = list.slice(0, limit);
    }

    if (!list.length) {
      grid.innerHTML = '<div class="vw-status">Keine Fahrzeuge in dieser Kategorie.</div>';
      return;
    }

    var html = '';

    for (var j = 0; j < list.length; j++) {
      html += renderCard(list[j]);
    }

    grid.innerHTML = html;
  }

  /* Dasselbe Fahrzeug steht teils doppelt (zwei Inserate mit neuer id und
     leicht anderem Titel) in bestand.json – in der Liste nur einmal zeigen.
     Gleiche Marke + Preis + km + Erstzulassung = dasselbe Fahrzeug.
     Die Einzelseite findet weiterhin beide ids. */
  function uniqueVehicles(vehicles) {
    var seen = {};
    var out = [];

    for (var i = 0; i < vehicles.length; i++) {
      var v = vehicles[i];
      var key = [v.make, v.price, v.km, v.firstRegistration].join('|').toLowerCase();
      if (seen[key]) continue;
      seen[key] = true;
      out.push(v);
    }

    return out;
  }

  function initList(grid, vehicles) {
    var filterEl = document.getElementById('vw-filter');
    var limit = parseInt(grid.getAttribute('data-limit'), 10) || 0;

    _all = uniqueVehicles(vehicles);

    if (!_all.length) {
      grid.innerHTML = '<div class="vw-status">Aktuell keine Fahrzeuge im Bestand.</div>';
      return;
    }

    if (filterEl) {
      renderFilter(filterEl);

      filterEl.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-cat]');
        if (!btn) return;
        var i = parseInt(btn.getAttribute('data-cat'), 10);
        _aktiv = i === -1 ? 'Alle' : _cats[i];
        renderFilter(filterEl);
        renderGrid(grid, limit);
      });
    }

    renderGrid(grid, limit);
  }

  /* ------------------------------------------------------------ Einzelseite */
  function initDetail(box, vehicles) {
    var id = new URLSearchParams(window.location.search).get('id');
    var v = null;

    for (var i = 0; i < vehicles.length; i++) {
      if (String(vehicles[i].id) === id) {
        v = vehicles[i];
        break;
      }
    }

    var titleEl = document.getElementById('vw-d-heading');
    var catEl = document.getElementById('vw-d-eyebrow');

    if (!v) {
      if (titleEl) titleEl.textContent = 'Fahrzeug nicht gefunden';
      box.innerHTML =
        '<div class="vw-status">Dieses Fahrzeug ist nicht mehr im Bestand – vermutlich wurde es bereits verkauft. ' +
        '<a class="vw-back" href="fahrzeuge">Alle Fahrzeuge ansehen</a></div>';
      return;
    }

    var title = buildTitle(v);
    var cat = catLabel(v);
    var p = fmtPrice(v);
    var imgs = (v.images || []).map(bigImage);
    var sp = specsHtml(v);
    var desc = cleanText(v.description);
    var pageUrl = window.location.href;

    document.title = title + ' | Elegance Car Safi';
    if (titleEl) titleEl.textContent = title;
    if (catEl) catEl.textContent = cat;

    var waText = 'Hallo, ich interessiere mich für folgendes Fahrzeug: ' + title + ' – ' + pageUrl;
    var mailSubject = 'Anfrage: ' + title;
    var mailBody = 'Hallo,\n\nich interessiere mich für folgendes Fahrzeug:\n' + title + '\n' + pageUrl + '\n\n';

    var gallery = imgs.length
      ? '<div class="vw-d-stage">' +
          '<img id="vw-d-img" src="' + esc(imgs[0]) + '" alt="' + esc(title) + '">' +
          (imgs.length > 1
            ? '<div class="vw-d-nav">' +
                '<button class="vw-d-nav-btn" type="button" data-dir="-1" aria-label="Vorheriges Bild">&#8249;</button>' +
                '<span class="vw-d-counter" id="vw-d-cnt">1 / ' + imgs.length + '</span>' +
                '<button class="vw-d-nav-btn" type="button" data-dir="1" aria-label="Nächstes Bild">&#8250;</button>' +
              '</div>'
            : '') +
          (v.reserved ? RESERVED_HTML : '') +
        '</div>' +
        (imgs.length > 1
          ? '<div class="vw-d-thumbs" id="vw-d-thumbs">' +
              imgs.map(function (src, n) {
                return '<button type="button" data-idx="' + n + '"' + (n === 0 ? ' class="active"' : '') +
                  ' aria-label="Bild ' + (n + 1) + '"><img src="' + esc(src.split('rule=mo-1600').join('rule=mo-640')) +
                  '" alt="" loading="lazy"></button>';
              }).join('') +
            '</div>'
          : '')
      : '<div class="vw-d-stage">' + placeholder() + (v.reserved ? RESERVED_HTML : '') + '</div>';

    box.innerHTML =
      '<a class="vw-back" href="fahrzeuge">Alle Fahrzeuge ansehen</a>' +
      '<div class="vw-d-grid">' +
        '<div class="vw-d-gallery">' + gallery + '</div>' +
        '<aside class="vw-d-info">' +
          '<div class="vw-loc">' + ICO.pin + '<span>' + esc(v.location || STANDORT) + '</span></div>' +
          '<div class="vw-d-price-block">' +
            (p.label ? '<div class="vw-price-label">' + p.label + '</div>' : '') +
            '<div class="vw-d-price' + (p.onRequest ? ' on-request' : '') + '">' + p.text + '</div>' +
            (p.gross ? '<div class="vw-price-gross">' + p.gross + '</div>' : '') +
          '</div>' +
          (sp ? '<div class="vw-specs">' + sp + '</div>' : '') +
          '<div class="vw-d-actions">' +
            '<a class="vw-btn vw-btn-primary" href="tel:' + TEL + '">Jetzt anrufen</a>' +
            '<a class="vw-btn vw-btn-secondary" href="https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(waText) + '" target="_blank" rel="noopener">WhatsApp</a>' +
            '<a class="vw-btn vw-btn-secondary" href="mailto:' + MAIL + '?subject=' + encodeURIComponent(mailSubject) + '&body=' + encodeURIComponent(mailBody) + '">E-Mail-Anfrage</a>' +
          '</div>' +
        '</aside>' +
      '</div>' +
      (desc
        ? '<div class="vw-d-desc"><h2>Beschreibung</h2><div class="vw-d-desc-text">' + esc(desc) + '</div></div>'
        : '');

    if (imgs.length < 2) return;

    var idx = 0;
    var imgEl = document.getElementById('vw-d-img');
    var cntEl = document.getElementById('vw-d-cnt');
    var thumbs = box.querySelectorAll('#vw-d-thumbs button');

    function show(n) {
      idx = (n + imgs.length) % imgs.length;
      imgEl.src = imgs[idx];
      cntEl.textContent = (idx + 1) + ' / ' + imgs.length;

      for (var t = 0; t < thumbs.length; t++) {
        thumbs[t].classList.toggle('active', t === idx);
      }
    }

    box.addEventListener('click', function (e) {
      var nav = e.target.closest('[data-dir]');
      var th = e.target.closest('[data-idx]');
      if (nav) show(idx + parseInt(nav.getAttribute('data-dir'), 10));
      if (th) show(parseInt(th.getAttribute('data-idx'), 10));
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
  }

  /* ------------------------------------------------------------------ Start */
  var grid = document.getElementById('vw-grid');
  var detail = document.getElementById('vw-detail');

  if (!grid && !detail) return;

  function showError(msg) {
    var target = grid || detail;
    target.innerHTML = '<div class="vw-status">' + esc(msg) + '</div>';
  }

  fetch(JSON_URL + '?t=' + Date.now())
    .then(function (res) {
      if (!res.ok) {
        throw new Error('HTTP ' + res.status);
      }
      return res.json();
    })
    .then(function (data) {
      var vehicles = data.vehicles || [];

      try {
        if (grid) initList(grid, vehicles);
        if (detail) initDetail(detail, vehicles);
      } catch (err) {
        console.error('ECS Bestand Render-Fehler:', err);
        showError('Anzeigefehler: ' + err.message);
      }
    })
    .catch(function (e) {
      console.error('ECS Bestand Ladefehler:', e);
      showError('Bestand konnte nicht geladen werden (' + e.message + ').');
    });
})();
