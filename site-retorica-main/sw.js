const CACHE_NAME = 'retorica-v6';
const ASSETS = ['./index.html', './logs.html', './noticias.html', './manifest.json'];

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
