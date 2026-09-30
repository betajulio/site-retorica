const CACHE_NAME = 'retorica-v28';
const ASSETS = [
  './index.html',
  './regras.html',
  './galeria.html',
  './logs.html',
  './noticias.html',
  './sugestoes.html',
  './setlist.html',
  './repertorio.html',
  './style.css',
  './firebase-init.js',
  './manifest.json',
  './imagens/bands/band_pink_floyd.png',
  './imagens/bands/band_legiao_urbana.png',
  './imagens/bands/band_the_cure.png',
  './imagens/bands/band_guns_n_roses.png',
  './imagens/bands/band_nirvana.png',
  './imagens/bands/band_u2.png',
  './imagens/bands/band_raul_seixas.png',
  './imagens/bands/band_ramones.png',
  './imagens/bands/band_billy_idol.png',
  './imagens/bands/band_inxs.png',
  './imagens/bands/band_depeche_mode.png',
  './imagens/bands/band_rem.png',
  './imagens/bands/band_whitesnake.png',
  './imagens/bands/band_rpm.png',
  './imagens/bands/band_led_zeppelin.png',
  './imagens/bands/band_queen.png',
  './imagens/bands/band_acdc.png',
  './imagens/bands/band_rolling_stones.png',
  './imagens/bands/band_beatles.png',
  './imagens/bands/band_deep_purple.png',
  './imagens/bands/band_creedence.png',
  './imagens/bands/band_black_sabbath.png',
  './imagens/bands/band_aerosmith.png',
  './imagens/bands/band_the_doors.png',
  './imagens/members/member_julio.png',
  './imagens/members/member_matheus.png',
  './imagens/members/member_nei.png',
  './imagens/members/member_renato.png',
  './imagens/members/member_roni.png',
  './imagens/members/member_vini.png',
  './imagens/members/member_banda_juntos.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  
  // Não cachear requisições dinâmicas e mídias externas.
  if (e.request.url.includes('firebase') || 
      e.request.url.includes('firestore') ||
      e.request.url.includes('googleapis') ||
      e.request.url.includes('cloudfunctions.net') ||
      e.request.url.includes('.a.run.app') ||
      e.request.url.includes('themoviedb.org') ||
      e.request.url.includes('image.tmdb.org') ||
      e.request.url.includes('openlibrary.org') ||
      e.request.url.includes('covers.openlibrary.org') ||
      e.request.url.includes('img.youtube.com')) {
    e.respondWith(fetch(e.request));
    return;
  }
  
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
