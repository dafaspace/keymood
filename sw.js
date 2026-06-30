// Bump CACHE on every version release so clients fetch fresh files.
var CACHE = "coc-v0.0.2";
var ASSETS = ["./index.html", "./manifest.json", "./icon.png"];

self.addEventListener("install", function(e) {
  e.waitUntil(caches.open(CACHE).then(function(c) { return c.addAll(ASSETS); }));
  self.skipWaiting(); // new SW activates without waiting for old tabs to close
});

self.addEventListener("activate", function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.filter(function(k){ return k !== CACHE; })
                             .map(function(k){ return caches.delete(k); }));
    }).then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function(e) {
  var req = e.request;
  // Network-first for the app shell (the HTML document) so a new version shows
  // up the moment the device is online; fall back to cache when offline. This
  // is what makes home-screen installs self-update (no remove/re-add needed).
  var accept = req.headers.get("accept") || "";
  var isShell = req.mode === "navigate" || accept.indexOf("text/html") !== -1;
  if (isShell) {
    e.respondWith(
      fetch(req).then(function(res) {
        if (res && res.ok) {
          var copy = res.clone();
          caches.open(CACHE).then(function(c){ c.put("./index.html", copy); });
        }
        return res;
      }).catch(function() {
        return caches.match("./index.html").then(function(r){ return r || caches.match(req); });
      })
    );
    return;
  }
  // Cache-first for static assets (icon, manifest).
  e.respondWith(caches.match(req).then(function(r){ return r || fetch(req); }));
});
