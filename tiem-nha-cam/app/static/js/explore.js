/* Trang khám phá: bản đồ chia đôi với marker giá, bộ lọc (histogram + đếm kết quả trực tiếp), thanh danh mục. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const vnd = (n) => Number(n).toLocaleString("vi-VN").replace(/,/g, ".") + "₫";
  const shortK = (v) => (v >= 1e6 ? (v / 1e6).toFixed(1).replace(/\.0$/, "").replace(".", ",") + "tr" : Math.round(v / 1000) + "k");
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ----------------------------------------------------------- catbar */
  const scroller = $("[data-catscroll]");
  if (scroller) {
    const l = $(".catbar__arrow--l"), r = $(".catbar__arrow--r");
    const sync = () => {
      l.hidden = scroller.scrollLeft < 8;
      r.hidden = scroller.scrollLeft + scroller.clientWidth >= scroller.scrollWidth - 8;
    };
    l.addEventListener("click", () => scroller.scrollBy({ left: -scroller.clientWidth * 0.7 }));
    r.addEventListener("click", () => scroller.scrollBy({ left: scroller.clientWidth * 0.7 }));
    scroller.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    sync();
    $(".cat.is-active", scroller)?.scrollIntoView({ inline: "center", block: "nearest" });
  }

  /* -------------------------------------------------------------- map */
  const explore = $("[data-explore]");
  const toggle = $("[data-map-toggle]");
  const mapEl = $("#explore-map");
  let map = null;

  let items = [], layer = null;

  function popupHtml(it) {
    return `<a class="map-pop" href="${it.url}"><img src="${it.img}" alt=""><div><b>${escapeHtml(it.title)}</b>` +
      `<span class="muted">${escapeHtml(it.place)}</span><br><b>${vnd(it.price)}</b> / ngày${it.reviews ? ` · ★ ${it.rating.toFixed(2).replace(".", ",")}` : ""}</div></a>`;
  }

  /* Gom cụm marker chồng nhau theo khoảng cách pixel ở mức zoom hiện tại (thay cho plugin markercluster) */
  function renderMarkers() {
    layer.clearLayers();
    const groups = [];
    items.forEach((it) => {
      const pt = map.latLngToLayerPoint([it.lat, it.lng]);
      const g = groups.find((x) => Math.abs(x.pt.x - pt.x) < 64 && Math.abs(x.pt.y - pt.y) < 30);
      if (g) g.members.push(it); else groups.push({ pt, members: [it] });
    });
    groups.forEach((g) => {
      const ids = g.members.map((m) => m.id).join(" ");
      if (g.members.length === 1) {
        const it = g.members[0];
        const icon = L.divIcon({ className: "pm-wrap", html: `<div class="price-marker" data-mids="${ids}">${shortK(it.price)}</div>`, iconSize: null });
        L.marker([it.lat, it.lng], { icon, riseOnHover: true }).bindPopup(popupHtml(it), { closeButton: false, offset: [0, -6], minWidth: 260, maxWidth: 260 }).addTo(layer);
        return;
      }
      const lat = g.members.reduce((a, m) => a + m.lat, 0) / g.members.length;
      const lng = g.members.reduce((a, m) => a + m.lng, 0) / g.members.length;
      const min = Math.min(...g.members.map((m) => m.price));
      const icon = L.divIcon({ className: "pm-wrap", html: `<div class="price-marker price-marker--cluster" data-mids="${ids}">${g.members.length} máy · từ ${shortK(min)}</div>`, iconSize: null });
      const m = L.marker([lat, lng], { icon, riseOnHover: true }).addTo(layer);
      m.on("click", () => {
        const b = L.latLngBounds(g.members.map((x) => [x.lat, x.lng]));
        if (map.getZoom() < 16 && b.getNorthEast().distanceTo(b.getSouthWest()) > 30) {
          map.fitBounds(b, { padding: [80, 80], maxZoom: Math.min(18, map.getZoom() + 3) });
        } else {
          // Cùng một điểm (một chủ thuê nhiều máy) → popup danh sách
          m.bindPopup(`<div class="map-list">${g.members.map((x) => `<a href="${x.url}"><img src="${x.img}" alt=""><span><b>${escapeHtml(x.title)}</b><small>${vnd(x.price)} / ngày</small></span></a>`).join("")}</div>`,
            { closeButton: false, minWidth: 280, maxWidth: 300 }).openPopup();
        }
      });
    });
  }

  async function initMap() {
    if (map) { map.invalidateSize(); return; }
    if (!window.L) { $(".map__fallback").hidden = false; return; }
    map = L.map(mapEl, { zoomControl: true, scrollWheelZoom: true }).setView([16.2, 106.5], 6);
    L.tileLayer(mapEl.dataset.tiles, { maxZoom: 18, attribution: mapEl.dataset.attr }).addTo(map);
    layer = L.layerGroup().addTo(map);
    try {
      const res = await fetch(`/api/listings?${explore.dataset.qs}`);
      items = (await res.json()).items;
      if (items.length) map.fitBounds(items.map((it) => [it.lat, it.lng]), { padding: [40, 40], maxZoom: 14 });
      renderMarkers();
      map.on("zoomend", renderMarkers);
    } catch (_) {
      $(".map__fallback").hidden = false;
    }
  }

  function setMap(on) {
    explore.classList.toggle("map-on", on);
    toggle.setAttribute("aria-pressed", String(on));
    $('[data-when="list"]', toggle).hidden = on;
    $('[data-when="map"]', toggle).hidden = !on;
    try { sessionStorage.setItem("map-on", on ? "1" : "0"); } catch (_) { /* ignore */ }
    if (on) setTimeout(initMap, 30);
  }
  if (toggle && explore) {
    toggle.addEventListener("click", () => setMap(!explore.classList.contains("map-on")));
    let saved = null;
    try { saved = sessionStorage.getItem("map-on"); } catch (_) { /* ignore */ }
    if (saved === "1" && window.matchMedia("(min-width: 744px)").matches) setMap(true);
    // Hover card → làm nổi marker tương ứng
    $$(".card").forEach((c) => {
      c.addEventListener("mouseenter", () => document.querySelector(`.price-marker[data-mids~="${c.dataset.id}"]`)?.classList.add("is-active"));
      c.addEventListener("mouseleave", () => document.querySelector(`.price-marker[data-mids~="${c.dataset.id}"]`)?.classList.remove("is-active"));
    });
  }

  /* ---------------------------------------------------------- filters */
  const dlg = $("#filters");
  const form = $("[data-filter-form]");
  if (!dlg || !form) return;
  $$("[data-open-filters]").forEach((b) => b.addEventListener("click", () => window.openModal("filters")));
  const rMin = $("[data-range-min]", form), rMax = $("[data-range-max]", form);
  const iMin = $("[data-price-min]", form), iMax = $("[data-price-max]", form);
  const bars = $$(".histo i", form);
  const step = Number($(".histo", form).dataset.step);
  const maxVal = Number(rMax.max);
  const digits = (s) => Number(String(s).replace(/\D/g, "")) || 0;

  function paintHisto() {
    const lo = Number(rMin.value), hi = Number(rMax.value);
    bars.forEach((b) => {
      const from = Number(b.dataset.from);
      b.classList.toggle("in", from + step > lo && from <= hi);
    });
  }
  function fromRange(e) {
    let lo = Number(rMin.value), hi = Number(rMax.value);
    if (lo > hi) { if (e.target === rMin) rMin.value = lo = hi; else rMax.value = hi = lo; }
    iMin.value = lo > 0 ? lo.toLocaleString("vi-VN").replace(/,/g, ".") : "";
    iMax.value = hi < maxVal ? hi.toLocaleString("vi-VN").replace(/,/g, ".") : "";
    paintHisto();
    liveCount();
  }
  rMin.addEventListener("input", fromRange);
  rMax.addEventListener("input", fromRange);
  [iMin, iMax].forEach((inp) => inp.addEventListener("change", () => {
    if (inp.value) inp.value = digits(inp.value).toLocaleString("vi-VN").replace(/,/g, ".");
    rMin.value = iMin.value ? digits(iMin.value) : 0;
    rMax.value = iMax.value ? digits(iMax.value) : maxVal;
    paintHisto();
    liveCount();
  }));
  paintHisto();

  let timer = 0;
  function params() {
    const fd = new FormData(form);
    const p = new URLSearchParams();
    for (const [k, v] of fd.entries()) {
      if (v === "" || (k === "sort" && v === "recommended")) continue;
      p.append(k, k.endsWith("_price") ? String(digits(v)) : v);
    }
    return p;
  }
  function liveCount() {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/listings?${params()}`);
        const data = await res.json();
        $("[data-filter-submit]", form).textContent = data.total ? `Hiển thị ${data.total} thiết bị` : "Không có kết quả";
      } catch (_) { /* giữ nguyên nhãn */ }
    }, 250);
  }
  form.addEventListener("change", (e) => { if (!e.target.matches("[data-price-min],[data-price-max]")) liveCount(); });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    location.href = `/?${params()}`;
  });
})();
