/* Trang chi tiết: thẻ đặt thuê (lịch + tính giá tức thì), lịch inline, gallery, bản đồ vị trí. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const vnd = (n) => Math.round(n).toLocaleString("vi-VN").replace(/,/g, ".") + "₫";
  const roundK = (v) => Math.floor(v / 1000 + 0.5) * 1000; // khớp pricing.round_k (half-up)
  const { iso, fmt, fmtShort, diffDays } = window.calUtil;

  /* ------------------------------------------------------------ gallery */
  const photos = $("#photos");
  $$("[data-photo]").forEach((b) => b.addEventListener("click", () => {
    window.openModal("photos");
    const target = $(`#photo-${b.dataset.photo}`, photos);
    if (target) setTimeout(() => target.scrollIntoView({ block: "start" }), 50);
  }));
  const gallery = $("[data-gallery]");
  const counter = $(".gallery__count");
  if (gallery && counter) {
    gallery.addEventListener("scroll", () => {
      const i = Math.round(gallery.scrollLeft / Math.max(1, gallery.clientWidth)) + 1;
      counter.textContent = `${i} / ${$$(".gallery__item", gallery).length}`;
    }, { passive: true });
  }

  /* ---------------------------------------------------------- read more */
  const clamp = $("[data-clamp]"), clampBtn = $("[data-clamp-btn]");
  if (clamp && clampBtn) {
    if (clamp.scrollHeight <= clamp.clientHeight + 4) { clampBtn.hidden = true; clamp.classList.add("no-clamp"); }
    clampBtn.addEventListener("click", () => {
      const open = clamp.classList.toggle("is-open");
      clampBtn.firstChild.textContent = open ? "Thu gọn " : "Hiển thị thêm ";
    });
  }

  /* --------------------------------------------------------------- share */
  $("[data-share]")?.addEventListener("click", async () => {
    const data = { title: document.title, url: location.href.split("#")[0] };
    try {
      if (navigator.share) await navigator.share(data);
      else { await navigator.clipboard.writeText(data.url); window.toast("Đã sao chép liên kết"); }
    } catch (_) { /* người dùng hủy */ }
  });

  /* ------------------------------------------------------- location map */
  const mapEl = $("#listing-map");
  if (mapEl) {
    const init = () => {
      if (!window.L) { mapEl.innerHTML = '<p class="map__fallback muted">Không tải được bản đồ.</p>'; return; }
      const lat = Number(mapEl.dataset.lat), lng = Number(mapEl.dataset.lng);
      const map = L.map(mapEl, { scrollWheelZoom: false, zoomControl: true }).setView([lat, lng], 14);
      L.tileLayer(mapEl.dataset.tiles, { maxZoom: 18, attribution: mapEl.dataset.attr }).addTo(map);
      L.circle([lat, lng], { radius: 550, color: "#FF5A1F", weight: 2, fillColor: "#FF5A1F", fillOpacity: 0.15 }).addTo(map);
      L.marker([lat, lng], { icon: L.divIcon({ className: "pm-wrap", html: '<div class="price-marker" style="border-radius:50%;padding:8px">📷</div>', iconSize: [36, 36], iconAnchor: [18, 18] }) }).addTo(map);
    };
    // Khởi tạo khi cuộn tới để trang tải nhanh
    const io = new IntersectionObserver((entries) => { if (entries[0].isIntersecting) { io.disconnect(); init(); } }, { rootMargin: "300px" });
    io.observe(mapEl);
  }

  /* -------------------------------------------------------- booking card */
  const card = $("#book");
  if (!card) return;
  const cfg = JSON.parse(card.dataset.booking);
  const form = $("[data-bk-form]", card);
  const pop = $("[data-bk-pop]", card);
  const startIn = $("[data-bk-start-input]", card), endIn = $("[data-bk-end-input]", card);
  const delivery = $("[data-bk-delivery]", card);
  const submit = $("[data-bk-submit]", card);
  const instant = submit.dataset.instant === "1";
  const calTitle = $("[data-cal-title]"), calSub = $("[data-cal-sub]");
  const bar = $(".bk-bar");
  const place = (document.querySelector(".lp-intro h2")?.textContent.split("·")[1] || "").trim();
  let start = null, end = null;

  function quote() {
    const days = diffDays(start, end);
    const subtotal = cfg.priceDay * days;
    const pct = days >= 7 ? cfg.discount7d : days >= 3 ? cfg.discount3d : 0;
    const discount = roundK(subtotal * pct / 100);
    const rent = subtotal - discount;
    const service = roundK(rent * cfg.servicePct / 100);
    const deliveryFee = delivery && delivery.checked ? cfg.deliveryFee : 0;
    return { days, subtotal, pct, discount, service, deliveryFee, total: rent + service + deliveryFee };
  }

  function paint() {
    const has = start && end;
    startIn.value = start ? iso(start) : "";
    endIn.value = end ? iso(end) : "";
    const sLbl = $("[data-bk-start]", card), eLbl = $("[data-bk-end]", card);
    sLbl.textContent = start ? fmt(start) : "Thêm ngày";
    eLbl.textContent = end ? fmt(end) : "Thêm ngày";
    sLbl.classList.toggle("has-value", !!start);
    eLbl.classList.toggle("has-value", !!end);
    $("[data-bk-lines]", card).hidden = !has;
    $("[data-bk-note]", card).hidden = !has;
    submit.textContent = has ? (instant ? submit.dataset.labelInstant : submit.dataset.labelRequest) : "Kiểm tra lịch trống";

    let title = "Chọn ngày nhận máy", sub = "Thêm ngày thuê để xem tổng giá chính xác";
    if (start && !end) { title = "Chọn ngày trả máy"; sub = `Tối thiểu ${cfg.minDays} ngày · nhận máy ${fmtShort(start)}`; }
    if (has) {
      const q = quote();
      title = `${q.days} ngày thuê${place ? " tại " + place : ""}`;
      sub = `${fmtShort(start)} – ${fmtShort(end)} ${end.getFullYear()}`;
      $("[data-bk-l-days]", card).textContent = `${vnd(cfg.priceDay)} × ${q.days} ngày`;
      $("[data-bk-subtotal]", card).textContent = vnd(q.subtotal);
      $("[data-bk-row-discount]", card).hidden = !q.discount;
      $("[data-bk-l-discount]", card).textContent = `Giảm giá thuê dài (${q.pct}%)`;
      $("[data-bk-discount]", card).textContent = "−" + vnd(q.discount);
      $("[data-bk-row-delivery]", card).hidden = !q.deliveryFee;
      $("[data-bk-delivery-fee]", card).textContent = vnd(q.deliveryFee);
      $("[data-bk-service]", card).textContent = vnd(q.service);
      $("[data-bk-total]", card).textContent = vnd(q.total);
      if (bar) {
        $("[data-bar-price]", bar).textContent = vnd(q.total);
        $("[data-bar-unit]", bar).textContent = `/ ${q.days} ngày`;
        $("[data-bar-dates]", bar).textContent = `${fmtShort(start)} – ${fmtShort(end)}`;
        $("[data-bar-cta]", bar).textContent = instant ? "Đặt thuê" : "Yêu cầu";
      }
    } else if (bar) {
      $("[data-bar-price]", bar).textContent = vnd(cfg.priceDay);
      $("[data-bar-unit]", bar).textContent = "/ ngày";
      $("[data-bar-dates]", bar).textContent = "Chọn ngày để xem tổng giá";
      $("[data-bar-cta]", bar).textContent = "Chọn ngày";
    }
    if (calTitle) { calTitle.textContent = title; calSub.textContent = sub; }
    $("[data-bk-pop-title]", card).textContent = title;
    $("[data-bk-pop-sub]", card).textContent = sub;
  }

  const calOpts = { blocked: cfg.blocked, minDays: cfg.minDays, today: cfg.today };
  const cals = [];
  function onChange(source) {
    return (s, e) => {
      start = s; end = e;
      cals.forEach((c) => { if (c !== source.cal) c.set(s, e, { silent: true }); });
      paint();
      if (s && e && source.closeOnDone) setTimeout(() => (pop.hidden = true), 250);
    };
  }
  const popSrc = { closeOnDone: true }, inlineSrc = { closeOnDone: false };
  popSrc.cal = new RangeCalendar($("[data-bk-calendar]", card), { ...calOpts, months: 2, onChange: onChange(popSrc) });
  cals.push(popSrc.cal);
  const inlineEl = $("[data-inline-calendar]");
  if (inlineEl) {
    inlineSrc.cal = new RangeCalendar(inlineEl, { ...calOpts, months: 2, onChange: onChange(inlineSrc) });
    cals.push(inlineSrc.cal);
  }

  // Prefill từ URL (?start=&end=) nếu khoảng ngày còn trống
  const ps = calUtil.parse(card.dataset.preStart), pe = calUtil.parse(card.dataset.preEnd);
  if (ps && pe && popSrc.cal.isValidRange(ps, pe)) { start = ps; end = pe; cals.forEach((c) => c.set(ps, pe, { silent: true })); }
  paint();

  const openPop = () => { pop.hidden = false; };
  $("[data-bk-open]", card).addEventListener("click", (e) => { e.stopPropagation(); pop.hidden ? openPop() : (pop.hidden = true); });
  $("[data-bk-close]", card).addEventListener("click", () => (pop.hidden = true));
  $$("[data-clear-booking]").forEach((b) => b.addEventListener("click", () => cals[0].clear()));
  // composedPath() giữ đường đi lúc dispatch — phần tử ngày bị render lại (tách khỏi DOM) vẫn được tính là "bên trong"
  const openers = [$("[data-bk-open]", card), bar && $("[data-bar-cta]", bar)].filter(Boolean);
  document.addEventListener("click", (e) => {
    const path = e.composedPath();
    if (!pop.hidden && !path.includes(pop) && !openers.some((o) => path.includes(o))) pop.hidden = true;
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") pop.hidden = true; });
  delivery?.addEventListener("change", paint);
  form.addEventListener("submit", (e) => {
    if (!(start && end)) { e.preventDefault(); openPop(); }
  });
  bar && $("[data-bar-cta]", bar).addEventListener("click", (e) => {
    e.stopPropagation();
    if (start && end) form.requestSubmit(); else openPop();
  });
})();
