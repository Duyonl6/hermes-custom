/* Hành vi chung toàn site: menu, tìm kiếm, carousel ảnh, yêu thích, modal, tab, toast. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const csrf = document.body.dataset.csrf;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (_) { /* private mode */ } },
  };

  /* ---------------------------------------------------------------- toast */
  function toast(msg, kind = "success") {
    let box = $(".toasts");
    if (!box) {
      box = document.createElement("div");
      box.className = "toasts";
      box.setAttribute("role", "status");
      document.body.appendChild(box);
    }
    const el = document.createElement("div");
    el.className = `toast toast--${kind}`;
    el.innerHTML = `<span></span><button type="button" class="toast__x" aria-label="Đóng">✕</button>`;
    el.querySelector("span").textContent = msg;
    box.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }
  window.toast = toast;
  document.addEventListener("click", (e) => {
    const x = e.target.closest(".toast__x");
    if (x) x.closest(".toast").remove();
  });
  $$(".toast").forEach((t) => setTimeout(() => t.remove(), 7000));

  /* ------------------------------------------------------------- demo bar */
  const demo = $(".demo-bar");
  if (demo) {
    if (store.get("demo-bar-hidden") === "1") demo.remove();
    else $(".demo-bar__x", demo).addEventListener("click", () => { demo.remove(); store.set("demo-bar-hidden", "1"); });
  }

  /* ------------------------------------------------------------ user menu */
  const menuBtn = $("[data-menu-btn]");
  const menuPanel = $(".usermenu__panel");
  if (menuBtn && menuPanel) {
    menuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = menuPanel.hidden;
      menuPanel.hidden = !open;
      menuBtn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", (e) => {
      if (!menuPanel.hidden && !e.target.closest(".usermenu")) {
        menuPanel.hidden = true;
        menuBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* --------------------------------------------------------------- search */
  const sb = $("[data-searchbar]");
  if (sb) {
    const body = document.body;
    const openSearch = () => body.classList.add("search-open");
    const closeSearch = () => { body.classList.remove("search-open"); closePops(); };
    $$("[data-open-search]").forEach((b) => b.addEventListener("click", openSearch));
    $$("[data-close-search]").forEach((b) => b.addEventListener("click", closeSearch));

    const pops = $$("[data-pop-panel]", sb);
    function closePops() {
      pops.forEach((p) => (p.hidden = true));
      $$(".sb-seg", sb).forEach((s) => s.classList.remove("is-open"));
    }
    function openPop(name, seg) {
      const panel = $(`[data-pop-panel="${name}"]`, sb);
      const wasOpen = !panel.hidden;
      closePops();
      if (wasOpen) return;
      panel.hidden = false;
      (seg || $(`[data-pop="${name}"]`, sb)).classList.add("is-open");
    }
    $$("[data-pop-btn]", sb).forEach((b) => b.addEventListener("click", (e) => {
      e.stopPropagation();
      openPop(b.dataset.popBtn, b.closest(".sb-seg"));
    }));
    $$(".sb-seg", sb).forEach((seg) => seg.addEventListener("click", (e) => {
      if (e.target.closest(".sb-pop") || e.target.closest("button,input")) return;
      const btn = $("[data-pop-btn]", seg);
      if (btn) btn.click(); else $("input", seg)?.focus();
    }));
    $$("[data-pop-close]", sb).forEach((b) => b.addEventListener("click", closePops));
    document.addEventListener("click", (e) => { if (!e.composedPath().includes(sb)) closePops(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") { closePops(); closeSearch(); } });

    // Chọn thành phố
    const cityInput = $("[data-city-input]", sb);
    const cityLabel = $("[data-city-label]", sb);
    const markCity = () => $$(".city-opt", sb).forEach((o) => o.classList.toggle("is-selected", o.dataset.city === cityInput.value));
    markCity();
    if (cityInput.value) cityLabel.parentElement.classList.add("has-value");
    $$(".city-opt", sb).forEach((o) => o.addEventListener("click", () => {
      cityInput.value = o.dataset.city;
      cityLabel.textContent = o.dataset.city || "Bất kỳ đâu";
      cityLabel.parentElement.classList.toggle("has-value", !!o.dataset.city);
      markCity();
      openPop("dates");
    }));

    // Lịch tìm kiếm (không có ngày bận)
    const startIn = $("[data-start-input]", sb), endIn = $("[data-end-input]", sb);
    const startLbl = $("[data-start-label]", sb), endLbl = $("[data-end-label]", sb);
    const calEl = $("[data-search-calendar]", sb);
    const paintDates = (s, e) => {
      startIn.value = s ? calUtil.iso(s) : "";
      endIn.value = e ? calUtil.iso(e) : "";
      startLbl.textContent = s ? calUtil.fmtShort(s) : "Thêm ngày";
      endLbl.textContent = e ? calUtil.fmtShort(e) : "Thêm ngày";
      startLbl.parentElement.classList.toggle("has-value", !!s);
      endLbl.parentElement.classList.toggle("has-value", !!e);
    };
    let cal = null;
    if (calEl && window.RangeCalendar) {
      cal = new RangeCalendar(calEl, {
        months: 2, start: startIn.value, end: endIn.value,
        onChange: (s, e) => { paintDates(s, e); if (s && e) setTimeout(() => { closePops(); $("#sb-q", sb)?.focus(); }, 180); },
      });
      paintDates(calUtil.parse(startIn.value), calUtil.parse(endIn.value));
    }
    $("[data-clear-dates]", sb)?.addEventListener("click", () => cal && cal.clear());
    sb.addEventListener("submit", () => {
      // Bỏ tham số rỗng cho URL gọn
      $$("input", sb).forEach((i) => { if (!i.value) i.disabled = true; });
      if (startIn.value && !endIn.value) { startIn.disabled = true; endIn.disabled = true; }
    });
  }

  /* ------------------------------------------------------ card carousels */
  document.addEventListener("click", (e) => {
    const nav = e.target.closest(".card__nav");
    if (!nav) return;
    e.preventDefault();
    e.stopPropagation();
    const track = nav.closest("[data-carousel]").querySelector(".card__track");
    track.scrollBy({ left: track.clientWidth * Number(nav.dataset.dir), behavior: "smooth" });
  });
  const syncCarousel = (track) => {
    const media = track.closest("[data-carousel]");
    const idx = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
    const dots = media.querySelectorAll(".card__dots i");
    dots.forEach((d, i) => d.classList.toggle("on", i === idx));
    const prev = media.querySelector(".card__nav--prev"), next = media.querySelector(".card__nav--next");
    if (prev) prev.disabled = idx <= 0;
    if (next) next.disabled = idx >= dots.length - 1;
  };
  $$(".card__track").forEach((t) => {
    syncCarousel(t);
    let raf = 0;
    t.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => syncCarousel(t)); }, { passive: true });
  });

  /* ------------------------------------------------------------ wishlist */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-wish]");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    if (document.body.dataset.auth !== "1") {
      location.href = `/login?next=${encodeURIComponent(location.pathname + location.search)}`;
      return;
    }
    try {
      const res = await fetch(`/api/wishlist/${btn.dataset.wish}`, { method: "POST", headers: { "X-CSRF-Token": csrf } });
      if (res.status === 401) { location.href = "/login"; return; }
      const data = await res.json();
      $$(`[data-wish="${btn.dataset.wish}"]`).forEach((b) => {
        b.classList.toggle("is-saved", data.saved);
        b.setAttribute("aria-pressed", String(data.saved));
        b.classList.remove("pop"); void b.offsetWidth; b.classList.add("pop");
      });
      toast(data.saved ? "Đã lưu vào danh sách Yêu thích" : "Đã bỏ khỏi danh sách Yêu thích");
    } catch (_) {
      toast("Không lưu được, vui lòng thử lại.", "error");
    }
  });

  /* ---------------------------------------------------------------- tabs */
  $$(".tabs").forEach((tabs) => {
    tabs.addEventListener("click", (e) => {
      const tab = e.target.closest("[data-tab]");
      if (!tab) return;
      $$("[data-tab]", tabs).forEach((t) => { t.classList.toggle("is-active", t === tab); t.setAttribute("aria-selected", String(t === tab)); });
      const scope = tabs.parentElement;
      $$("[data-tabpanel]", scope).forEach((p) => (p.hidden = p.dataset.tabpanel !== tab.dataset.tab));
    });
  });

  /* -------------------------------------------------------------- modals */
  window.openModal = (id) => {
    const dlg = document.getElementById(id);
    if (dlg && !dlg.open) { dlg.showModal(); document.documentElement.style.overflow = "hidden"; }
    return dlg;
  };
  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-open-modal]");
    if (opener) { window.openModal(opener.dataset.openModal); return; }
    const closer = e.target.closest("[data-close-modal]");
    if (closer) { closer.closest("dialog").close(); return; }
    if (e.target.tagName === "DIALOG") e.target.close(); // click nền mờ
  });
  $$("dialog").forEach((d) => d.addEventListener("close", () => (document.documentElement.style.overflow = "")));

  /* ------------------------------------------------------ confirm & misc */
  document.addEventListener("submit", (e) => {
    const f = e.target.closest("[data-confirm]");
    if (f && !confirm(f.dataset.confirm)) e.preventDefault();
  }, true);
  $$("[data-fill]").forEach((b) => b.addEventListener("click", () => {
    const form = $("form.stack");
    form.querySelector("[name=email]").value = b.dataset.fill;
    form.querySelector("[name=password]").value = "demo1234";
    form.requestSubmit();
  }));

  /* Header đổ bóng khi cuộn */
  const onScroll = () => document.body.classList.toggle("scrolled", window.scrollY > 4);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
