/* Form đăng/sửa tin: chọn vị trí trên bản đồ, chọn nhanh khu vực, định dạng tiền, upload ảnh. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const form = $("[data-listing-form]");
  if (!form) return;

  const latIn = $("[data-lat]", form), lngIn = $("[data-lng]", form);
  const wardIn = $("[data-ward]", form), citySel = $("[data-city]", form);
  const mapEl = $("#picker-map");
  const locations = JSON.parse(mapEl.dataset.locations || "{}");
  let map = null, marker = null;

  function setPos(lat, lng, pan = true) {
    latIn.value = lat.toFixed(5);
    lngIn.value = lng.toFixed(5);
    if (marker) marker.setLatLng([lat, lng]);
    if (map && pan) map.setView([lat, lng], Math.max(map.getZoom(), 14));
  }

  if (window.L) {
    const lat = Number(latIn.value) || 21.03, lng = Number(lngIn.value) || 105.85;
    map = L.map(mapEl, { scrollWheelZoom: false }).setView([lat, lng], 14);
    L.tileLayer(mapEl.dataset.tiles, { maxZoom: 18, attribution: mapEl.dataset.attr }).addTo(map);
    marker = L.marker([lat, lng], { draggable: true }).addTo(map);
    marker.on("dragend", () => { const p = marker.getLatLng(); setPos(p.lat, p.lng, false); });
    map.on("click", (e) => setPos(e.latlng.lat, e.latlng.lng, false));
  } else {
    mapEl.innerHTML = '<p class="map__fallback muted">Không tải được bản đồ — chọn khu vực ở trên để điền toạ độ.</p>';
  }

  $("[data-loc-select]", form)?.addEventListener("change", (e) => {
    const loc = locations[e.target.value];
    if (!loc) return;
    const [city, ward, lat, lng] = loc;
    citySel.value = city;
    wardIn.value = ward;
    setPos(lat, lng);
  });

  // Định dạng số tiền 1.234.567 khi rời ô nhập
  $$("[data-money]", form).forEach((inp) => {
    const format = () => {
      const n = Number(String(inp.value).replace(/\D/g, ""));
      inp.value = n ? n.toLocaleString("vi-VN").replace(/,/g, ".") : "";
    };
    inp.addEventListener("blur", format);
    format();
  });

  // Upload ảnh: hiện số file đã chọn + hiệu ứng kéo thả
  const fileIn = $("[data-file-input]", form), count = $("[data-file-count]", form), zone = $(".dropzone", form);
  fileIn?.addEventListener("change", () => {
    const n = fileIn.files.length;
    count.textContent = n ? `Đã chọn ${n} ảnh — sẽ tải lên khi bấm lưu` : "hoặc kéo thả vào đây";
  });
  ["dragenter", "dragover"].forEach((ev) => zone?.addEventListener(ev, () => zone.classList.add("is-drag")));
  ["dragleave", "drop"].forEach((ev) => zone?.addEventListener(ev, () => zone.classList.remove("is-drag")));
})();
