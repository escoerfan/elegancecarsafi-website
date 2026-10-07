/* =========================================================================
   ECS GmbH – Elegance Car Safi
   Strukturierte Daten für den Fahrzeugbestand (Seite /fahrzeuge)

   Lädt dieselbe bestand.json wie das Fahrzeug-Widget (js/bestand.js, das
   unverändert bleibt) und hängt eine ItemList mit Vehicle + Offer als
   JSON-LD an. Reservierte Fahrzeuge werden nicht als Angebot gelistet.
   ========================================================================= */
(function () {
  'use strict';

  var URL_JSON = 'https://raw.githubusercontent.com/escoerfan/ecs-bestand/main/bestand.json';
  var BASE = 'https://elegancecarsafi.com/';

  function clean(s) {
    return String(s || '').split('*').join('').replace(/\s+/g, ' ').trim();
  }

  function vehicle(v) {
    var item = {
      '@type': 'Vehicle',
      name: clean(v.title),
      url: BASE + 'fahrzeug?id=' + encodeURIComponent(v.id),
      itemCondition: 'https://schema.org/UsedCondition'
    };
    if (v.make) item.brand = { '@type': 'Brand', name: clean(v.make) };
    if (v.model) item.model = clean(v.model);
    if (v.images && v.images.length) item.image = v.images.slice(0, 3);
    var km = parseInt(v.km, 10);
    if (!isNaN(km)) item.mileageFromOdometer = { '@type': 'QuantitativeValue', value: km, unitCode: 'KMT' };
    var reg = String(v.firstRegistration || '');
    if (/^\d{6}$/.test(reg)) item.dateVehicleFirstRegistered = reg.slice(0, 4) + '-' + reg.slice(4, 6);
    var price = parseFloat(v.price);
    if (price > 0) {
      item.offers = {
        '@type': 'Offer',
        price: price.toFixed(2),
        priceCurrency: 'EUR',
        availability: 'https://schema.org/InStock',
        itemCondition: 'https://schema.org/UsedCondition',
        seller: { '@id': BASE + '#autodealer' }
      };
    }
    return item;
  }

  fetch(URL_JSON, { cache: 'default' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      var list = data && data.vehicles;
      if (!list || !list.length) return;
      var items = list.filter(function (v) { return v && !v.reserved; })
        .map(function (v, i) { return { '@type': 'ListItem', position: i + 1, item: vehicle(v) }; });
      if (!items.length) return;
      var s = document.createElement('script');
      s.type = 'application/ld+json';
      s.textContent = JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        name: 'Gebrauchte Nutzfahrzeuge im Bestand der ECS GmbH',
        numberOfItems: items.length,
        itemListElement: items
      });
      document.head.appendChild(s);
    })
    .catch(function () { /* ohne Bestand kein Schema */ });
})();
