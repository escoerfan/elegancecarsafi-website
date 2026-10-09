/* =========================================================================
   ECS GmbH – Sprachumschaltung
   Deutsch ist die Originalsprache im HTML. Für EN/PL/RU/ES/AR liegen die
   Übersetzungen in js/lang/<code>.js (Schlüssel = deutscher Originaltext,
   Leerzeichen zusammengefasst). Die Engine ersetzt Textknoten und einige
   Attribute; per MutationObserver auch Inhalte, die Skripte nachladen
   (Fahrzeugbestand, Cookie-Banner, Karte).

   Platzhalter in Schlüsseln: {a}, {b} … – z. B. "Brutto: {a}".
   Bereiche mit data-no-i18n werden nie übersetzt.
   Auswahl wird in localStorage gemerkt; ?lang=en erzwingt eine Sprache.
   ========================================================================= */
(function () {
  var LANGS = [
    ['de', 'Deutsch'],
    ['en', 'English'],
    ['pl', 'Polski'],
    ['ru', 'Русский'],
    ['es', 'Español'],
    ['ar', 'العربية']
  ];
  var RTL = { ar: true };
  var STORE_KEY = 'ecs-lang';
  var VERSION = '20261009b';
  var ATTRS = ['alt', 'aria-label', 'placeholder', 'title'];
  var SKIP_TAGS = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, svg: 1, SVG: 1, TEXTAREA: 1 };

  var root = document.documentElement;
  var dicts = (window.ECS_I18N = window.ECS_I18N || {});

  function isKnown(code) {
    for (var i = 0; i < LANGS.length; i++) if (LANGS[i][0] === code) return true;
    return false;
  }

  function readStored() {
    try { return localStorage.getItem(STORE_KEY); } catch (e) { return null; }
  }

  function writeStored(code) {
    try { localStorage.setItem(STORE_KEY, code); } catch (e) { /* privat */ }
  }

  var param = (location.search.match(/[?&]lang=([a-z]{2})/) || [])[1];
  var lang = isKnown(param) ? param : (isKnown(readStored()) ? readStored() : 'de');
  if (param && isKnown(param)) writeStored(param);

  /* ------------------------------------------------- Laden ohne Aufblitzen
     Solange die Sprachdatei lädt, bleibt die Seite unsichtbar (max. 2,5 s). */
  var guard = document.createElement('style');
  guard.textContent = 'html.i18n-pending body{visibility:hidden}';
  document.head.appendChild(guard);

  var loaded = {};

  function loadDict(code) {
    if (code === 'de' || dicts[code]) return Promise.resolve();
    if (loaded[code]) return loaded[code];
    loaded[code] = new Promise(function (resolve) {
      var s = document.createElement('script');
      s.src = 'js/lang/' + code + '.js?v=' + VERSION;
      s.onload = resolve;
      s.onerror = resolve;
      document.head.appendChild(s);
    });
    return loaded[code];
  }

  if (lang !== 'de') {
    root.classList.add('i18n-pending');
    setTimeout(function () { root.classList.remove('i18n-pending'); }, 2500);
    loadDict(lang);
  }

  /* ------------------------------------------------------- Übersetzen */
  var compiled = {};

  function escapeRe(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  /* Schlüssel mit {a}/{b} werden einmalig zu RegExp-Mustern kompiliert */
  function patternsFor(code) {
    if (compiled[code]) return compiled[code];
    var list = [];
    var d = dicts[code] || {};
    Object.keys(d).forEach(function (key) {
      if (key.indexOf('{') === -1) return;
      var names = [];
      var re = escapeRe(key).replace(/\\\{([a-z])\\\}/g, function (m, n) {
        names.push(n);
        return '(.+?)';
      });
      if (!names.length) return;
      list.push({ re: new RegExp('^' + re + '$'), names: names, out: d[key] });
    });
    compiled[code] = list;
    return list;
  }

  function lookup(text) {
    var d = dicts[lang];
    if (!d) return null;
    if (Object.prototype.hasOwnProperty.call(d, text)) return d[text];
    var pats = patternsFor(lang);
    for (var i = 0; i < pats.length; i++) {
      var m = text.match(pats[i].re);
      if (!m) continue;
      var out = pats[i].out;
      for (var n = 0; n < pats[i].names.length; n++) {
        var inner = lookup(m[n + 1]);
        out = out.split('{' + pats[i].names[n] + '}').join(inner != null ? inner : m[n + 1]);
      }
      return out;
    }
    return null;
  }

  /* Übersetzt einen String, behält führende/folgende Leerzeichen bei */
  function translate(raw) {
    var norm = raw.replace(/\s+/g, ' ').trim();
    if (!norm) return null;
    var t = lookup(norm);
    if (t == null) return null;
    var lead = raw.match(/^\s*/)[0] ? ' ' : '';
    var trail = raw.match(/\s*$/)[0] ? ' ' : '';
    return lead + t + trail;
  }

  /* Originale merken, damit man jederzeit zurück auf Deutsch kann */
  var textState = new WeakMap();   // Textknoten → { orig, out }
  var attrState = new WeakMap();   // Element → { attr: { orig, out } }

  function skipped(el) {
    for (var n = el; n && n.nodeType === 1; n = n.parentNode) {
      if (SKIP_TAGS[n.nodeName] || n.hasAttribute('data-no-i18n')) return true;
    }
    return false;
  }

  function doText(node) {
    var st = textState.get(node);
    if (st && node.data !== st.out) st = null;          // Skript hat Text geändert
    if (!st) {
      if (!/[A-Za-zÀ-ÿ]/.test(node.data)) return;
      st = { orig: node.data, out: node.data };
      textState.set(node, st);
    }
    var next = lang === 'de' ? st.orig : (translate(st.orig) || st.orig);
    if (node.data !== next) node.data = next;
    st.out = next;
  }

  function doAttrs(el) {
    var map = attrState.get(el);
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i];
      if (!el.hasAttribute(a)) continue;
      var cur = el.getAttribute(a);
      var st = map && map[a];
      if (st && cur !== st.out) st = null;
      if (!st) {
        if (!/[A-Za-zÀ-ÿ]/.test(cur)) continue;
        if (!map) { map = {}; attrState.set(el, map); }
        st = map[a] = { orig: cur, out: cur };
      }
      var next = lang === 'de' ? st.orig : (translate(st.orig) || st.orig);
      if (cur !== next) el.setAttribute(a, next);
      st.out = next;
    }
  }

  function walk(rootNode) {
    if (rootNode.nodeType === 3) {
      if (rootNode.parentNode && !skipped(rootNode.parentNode)) doText(rootNode);
      return;
    }
    if (rootNode.nodeType !== 1 || skipped(rootNode)) return;
    doAttrs(rootNode);
    var tw = document.createTreeWalker(rootNode, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (n.nodeType === 1 && (SKIP_TAGS[n.nodeName] || n.hasAttribute('data-no-i18n'))) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = tw.nextNode())) {
      if (n.nodeType === 3) doText(n);
      else doAttrs(n);
    }
  }

  var origTitle = null;

  function applyAll() {
    root.lang = lang;
    root.dir = RTL[lang] ? 'rtl' : 'ltr';
    if (origTitle === null) origTitle = document.title;
    document.title = lang === 'de' ? origTitle : (translate(origTitle) || origTitle);
    walk(document.body);
    legalNote();
    updatePicker();
  }

  /* Hinweis auf Rechtstexten (Datenschutz nur auf Deutsch, Impressum verbindlich auf Deutsch) */
  function legalNote() {
    var main = document.querySelector('[data-i18n-note]');
    if (!main) return;
    var old = document.getElementById('i18n-legal-note');
    if (old) old.remove();
    if (lang === 'de') return;
    var d = dicts[lang] || {};
    var text = d['__note_' + main.getAttribute('data-i18n-note')];
    if (!text) return;
    var p = document.createElement('p');
    p.id = 'i18n-legal-note';
    p.className = 'legal-note';
    p.setAttribute('data-no-i18n', '');
    p.textContent = text;
    var h1 = main.querySelector('h1');
    if (h1) h1.insertAdjacentElement('afterend', p);
    else main.insertBefore(p, main.firstChild);
  }

  /* --------------------------------------------- Dynamische Inhalte */
  var observer = new MutationObserver(function (records) {
    if (lang === 'de') return;
    for (var i = 0; i < records.length; i++) {
      var r = records[i];
      if (r.type === 'childList') {
        for (var k = 0; k < r.addedNodes.length; k++) walk(r.addedNodes[k]);
      } else if (r.type === 'characterData') {
        if (r.target.parentNode && !skipped(r.target.parentNode)) doText(r.target);
      } else if (r.type === 'attributes') {
        if (!skipped(r.target)) doAttrs(r.target);
      }
    }
    if (document.title !== lastTitle) {
      origTitle = document.title;
      document.title = translate(origTitle) || origTitle;
      lastTitle = document.title;
    }
  });
  var lastTitle = '';

  /* ------------------------------------------------------- Auswahl-UI */
  var picker = null;

  var GLOBE =
    '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6">' +
    '<circle cx="12" cy="12" r="9.25"/><path d="M2.75 12h18.5"/>' +
    '<path d="M12 2.75c2.5 2.6 3.75 5.68 3.75 9.25S14.5 18.65 12 21.25C9.5 18.65 8.25 15.57 8.25 12S9.5 5.35 12 2.75z"/></svg>';

  var LABEL = {
    de: 'Sprache wählen', en: 'Choose language', pl: 'Wybierz język',
    ru: 'Выбрать язык', es: 'Elegir idioma', ar: 'اختر اللغة'
  };

  function buildPicker() {
    var host = document.querySelector('.site-header__side');
    var legalBack = document.querySelector('.legal-back');
    if (!host && !legalBack) return;

    picker = document.createElement('div');
    picker.className = 'lang-switch';
    picker.setAttribute('data-no-i18n', '');
    picker.innerHTML =
      '<button class="lang-switch__btn" type="button" aria-haspopup="true" aria-expanded="false">' +
        GLOBE + '<span class="lang-switch__code"></span>' +
      '</button>' +
      '<ul class="lang-switch__menu" role="menu" hidden>' +
        LANGS.map(function (l) {
          return '<li role="none"><button type="button" role="menuitemradio" lang="' + l[0] + '"' +
            (l[0] === 'ar' ? ' dir="rtl"' : '') + ' data-lang="' + l[0] + '">' + l[1] + '</button></li>';
        }).join('') +
      '</ul>';

    if (host) host.appendChild(picker);
    else legalBack.parentNode.insertBefore(picker, legalBack);

    var btn = picker.querySelector('.lang-switch__btn');
    var menu = picker.querySelector('.lang-switch__menu');

    function setOpen(open) {
      menu.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      picker.classList.toggle('is-open', open);
    }

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      setOpen(menu.hidden);
      if (!menu.hidden) {
        var cur = menu.querySelector('[aria-checked="true"]');
        if (cur) cur.focus();
      }
    });

    menu.addEventListener('click', function (e) {
      var b = e.target.closest('[data-lang]');
      if (!b) return;
      setOpen(false);
      setLang(b.getAttribute('data-lang'));
      btn.focus();
    });

    menu.addEventListener('keydown', function (e) {
      var items = Array.prototype.slice.call(menu.querySelectorAll('button'));
      var i = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
    });

    document.addEventListener('click', function (e) {
      if (!picker.contains(e.target)) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) { setOpen(false); btn.focus(); }
    });
  }

  function updatePicker() {
    if (!picker) return;
    picker.querySelector('.lang-switch__code').textContent = lang.toUpperCase();
    var btn = picker.querySelector('.lang-switch__btn');
    btn.setAttribute('aria-label', LABEL[lang] || LABEL.de);
    btn.setAttribute('title', LABEL[lang] || LABEL.de);
    var items = picker.querySelectorAll('[data-lang]');
    for (var i = 0; i < items.length; i++) {
      items[i].setAttribute('aria-checked', items[i].getAttribute('data-lang') === lang ? 'true' : 'false');
    }
  }

  function setLang(code) {
    if (!isKnown(code)) return;
    lang = code;
    writeStored(code);
    loadDict(code).then(function () {
      applyAll();
      lastTitle = document.title;
      root.classList.remove('i18n-pending');
    });
  }

  /* ------------------------------------------------------------ Start */
  function start() {
    buildPicker();
    loadDict(lang).then(function () {
      applyAll();
      lastTitle = document.title;
      root.classList.remove('i18n-pending');
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: true,
        attributeFilter: ATTRS
      });
      /* Titel wird u. a. von bestand.js gesetzt */
      var titleEl = document.querySelector('title');
      if (titleEl) observer.observe(titleEl, { childList: true, characterData: true, subtree: true });
    });
  }

  window.ECSLang = { set: setLang, get: function () { return lang; } };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
