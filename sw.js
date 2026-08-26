// Bump CACHE on every version release so clients fetch fresh files.
var CACHE = "coc-v2.10.0";
var ASSETS = ["./index.html", "./manifest.json", "./icon.png"];

// How long the document may wait on the network before we serve what we already have.
// This is the whole point of the rewrite - see the fetch handler.
var NET_BUDGET_MS = 3000;

self.addEventListener("install", function(e) {
  // c.addAll() is ATOMIC: one asset failing rejects the whole call and NOTHING is
  // cached. A single blip on first install therefore left the cache holding only
  // index.html (put there later by the network-first branch), with manifest.json and
  // icon.png permanently absent - so a cold offline launch had no icon and no manifest
  // metadata, and stayed that way until CACHE was bumped. Add them one at a time and
  // let any single failure pass; the healing cache-first branch below picks up the rest.
  e.waitUntil(caches.open(CACHE).then(function(c) {
    return Promise.all(ASSETS.map(function(u){ return c.add(u).catch(function(){}); }));
  }));
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
    // This branch used to fall back to cache ONLY when fetch() REJECTED, which quietly
    // assumed a failing network fails fast. It doesn't. Right after a phone reboots the
    // radio is still associating, and fetch() neither resolves nor rejects for tens of
    // seconds - respondWith stays pending and the user stares at a white screen. That is
    // the most likely explanation for home-screen shortcuts appearing "dead" after a
    // battery drain. Two further holes in the same block: a not-ok response (5xx, 404)
    // was returned to the user instead of the perfectly good cached app, and so was an
    // opaqueredirect from a captive portal.
    // So: race the network against a hard budget, and treat slow, failed, not-ok and
    // hijacked all the same way - show the app we already have.
    e.respondWith((function() {
      function offline() {
        return caches.match("./index.html").then(function(r) {
          return r || caches.match(req).then(function(r2){ return r2 || Response.error(); });
        });
      }
      // Resolves to null rather than rejecting, so the handler below can tell "too slow"
      // apart from "failed" without a second catch.
      var timed = new Promise(function(res){ setTimeout(function(){ res(null); }, NET_BUDGET_MS); });
      var net   = fetch(req).then(function(r){ return r; }).catch(function(){ return null; });
      // Whatever the race decides, a successful response still refreshes the cache - so a
      // slow-but-working network updates the app for next launch even though this launch
      // was served from cache.
      e.waitUntil(net.then(function(r) {
        if (!r || !r.ok || r.type === "opaqueredirect") return;
        var copy = r.clone();
        return caches.open(CACHE).then(function(c){ return c.put("./index.html", copy); });
      }));
      return Promise.race([net, timed]).then(function(res) {
        if (!res || !res.ok || res.type === "opaqueredirect") return offline();
        return res;
      }).catch(offline);
    })());
    return;
  }
  // Cache-first for static assets (icon, manifest) - and it now WRITES on a miss. The
  // old one never did, so anything absent from the cache stayed absent for the lifetime
  // of this CACHE name, however many times it was fetched successfully online.
  e.respondWith(caches.match(req).then(function(r) {
    if (r) return r;
    return fetch(req).then(function(res) {
      if (res && res.ok && res.type === "basic") {
        var copy = res.clone();
        caches.open(CACHE).then(function(c){ c.put(req, copy); });
      }
      return res;
    });
  }));
});
