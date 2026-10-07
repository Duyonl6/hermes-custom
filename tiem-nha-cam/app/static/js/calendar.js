/* Lịch chọn khoảng ngày kiểu Airbnb (vanilla JS, không phụ thuộc thư viện).
 *  - Ngày bận (đã có đơn/khóa lịch) không thể làm ngày nhận máy.
 *  - Sau khi chọn ngày nhận, ngày trả không được vượt qua ngày bận đầu tiên phía sau;
 *    riêng ngày bận đó được phép làm ngày trả (đơn sau nhận máy cùng ngày) — "checkout only".
 *  - Tuân thủ số ngày thuê tối thiểu (minDays).
 */
(function () {
  "use strict";
  const WD = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];
  const pad = (n) => String(n).padStart(2, "0");
  const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const parse = (s) => {
    if (!s || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
  };
  const addDays = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
  const diffDays = (a, b) => Math.round((b - a) / 864e5);
  const fmt = (d) => (d ? `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}` : "");
  const fmtShort = (d) => (d ? `${d.getDate()} thg ${d.getMonth() + 1}` : "");

  class RangeCalendar {
    constructor(el, opts) {
      this.el = el;
      this.opts = Object.assign({ months: 2, blocked: [], minDays: 1, today: iso(new Date()), start: null, end: null, onChange() {} }, opts || {});
      this.blocked = new Set(this.opts.blocked);
      this.today = parse(this.opts.today) || new Date();
      this.start = parse(this.opts.start);
      this.end = parse(this.opts.end);
      const base = this.start || this.today;
      this.view = new Date(base.getFullYear(), base.getMonth(), 1);
      this.mq = window.matchMedia("(max-width: 743px)");
      el.addEventListener("click", (e) => this._click(e));
      el.addEventListener("mouseover", (e) => this._hover(e));
      el.addEventListener("mouseleave", () => this._paintHover(null));
      this.mq.addEventListener?.("change", () => this.render());
      this.render();
    }

    get monthCount() { return this.mq.matches ? 1 : this.opts.months; }

    /** Đặt khoảng ngày từ bên ngoài (đồng bộ giữa các lịch). */
    set(start, end, { silent = false } = {}) {
      this.start = start ? new Date(start) : null;
      this.end = end ? new Date(end) : null;
      if (this.start) {
        const first = new Date(this.view);
        const last = new Date(first.getFullYear(), first.getMonth() + this.monthCount, 0);
        if (this.start < first || this.start > last) this.view = new Date(this.start.getFullYear(), this.start.getMonth(), 1);
      }
      this.render();
      if (!silent) this.opts.onChange(this.start, this.end);
    }

    clear() { this.set(null, null); }

    /** Kiểm tra một khoảng [start, end) có hợp lệ không (dùng khi prefill từ URL). */
    isValidRange(start, end) {
      if (!start || !end || end <= start || start < this.today) return false;
      if (diffDays(start, end) < this.opts.minDays) return false;
      for (let d = new Date(start); d < end; d = addDays(d, 1)) if (this.blocked.has(iso(d))) return false;
      return true;
    }

    _limit() {
      if (!this.start) return null;
      for (let i = 1; i <= 420; i++) {
        const d = addDays(this.start, i);
        if (this.blocked.has(iso(d))) return d;
      }
      return null;
    }

    _state(d) {
      const past = d < this.today;
      const busy = this.blocked.has(iso(d));
      let disabled = past || busy;
      let checkoutOnly = false;
      if (this.start && !this.end && d > this.start) {
        const limit = this._limit();
        const tooShort = diffDays(this.start, d) < this.opts.minDays;
        if (limit && +d === +limit) {
          checkoutOnly = true;
          disabled = tooShort;
        } else {
          disabled = past || busy || (limit && d > limit) || tooShort;
        }
      }
      return { past, busy, disabled, checkoutOnly };
    }

    render() {
      const n = this.monthCount;
      this.el.style.setProperty("--months", n);
      const minView = new Date(this.today.getFullYear(), this.today.getMonth(), 1);
      let html = `<button type="button" class="rcal__nav rcal__nav--prev" data-nav="-1" aria-label="Tháng trước" ${this.view <= minView ? "disabled" : ""}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m15 5-7 7 7 7"/></svg></button>
        <button type="button" class="rcal__nav rcal__nav--next" data-nav="1" aria-label="Tháng sau">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m9 5 7 7-7 7"/></svg></button>`;
      for (let m = 0; m < n; m++) {
        const first = new Date(this.view.getFullYear(), this.view.getMonth() + m, 1);
        const days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate();
        const lead = (first.getDay() + 6) % 7; // T2 là ngày đầu tuần
        html += `<div class="rcal__month"><h4>Tháng ${first.getMonth() + 1} ${first.getFullYear()}</h4>
          <div class="rcal__wd">${WD.map((w) => `<span>${w}</span>`).join("")}</div><div class="rcal__days">`;
        html += "<span></span>".repeat(lead);
        for (let day = 1; day <= days; day++) {
          const d = new Date(first.getFullYear(), first.getMonth(), day);
          html += this._dayHtml(d);
        }
        html += "</div></div>";
      }
      this.el.innerHTML = html;
    }

    _dayHtml(d) {
      const st = this._state(d);
      const cls = ["rcal__day"];
      if (st.disabled) cls.push("is-disabled");
      if (st.busy && !st.past) cls.push("is-busy");
      if (st.checkoutOnly) cls.push("is-checkout-only");
      if (+d === +this.today) cls.push("is-today");
      if (this.start && +d === +this.start) cls.push("is-start", this.end ? "has-end" : "");
      if (this.end && +d === +this.end) cls.push("is-end");
      if (this.start && this.end && d > this.start && d < this.end) cls.push("in-range");
      const label = `${d.getDate()} tháng ${d.getMonth() + 1} ${d.getFullYear()}${st.busy ? " — đã có người thuê" : ""}${st.checkoutOnly ? " — chỉ có thể trả máy" : ""}`;
      return `<button type="button" class="${cls.join(" ")}" data-date="${iso(d)}" aria-label="${label}" ${st.disabled ? 'aria-disabled="true"' : ""}><b>${d.getDate()}</b></button>`;
    }

    _click(e) {
      const nav = e.target.closest("[data-nav]");
      if (nav) {
        if (nav.disabled) return;
        this.view = new Date(this.view.getFullYear(), this.view.getMonth() + Number(nav.dataset.nav), 1);
        this.render();
        return;
      }
      const btn = e.target.closest("[data-date]");
      if (!btn) return;
      const d = parse(btn.dataset.date);
      const st = this._state(d);
      if (!this.start || this.end) {
        if (st.past || st.busy) return;
        this.start = d;
        this.end = null;
      } else if (d <= this.start) {
        if (st.past || st.busy) return;
        this.start = d;
      } else if (st.disabled) {
        // Ngoài giới hạn → coi như chọn lại ngày nhận (giống Airbnb), trừ khi ngày đó bận/quá khứ/không đủ số ngày tối thiểu
        const tooShort = diffDays(this.start, d) < this.opts.minDays;
        if (st.past || st.busy || tooShort) return;
        this.start = d;
      } else {
        this.end = d;
      }
      this.render();
      this.opts.onChange(this.start, this.end);
    }

    _hover(e) {
      if (!this.start || this.end) return;
      const btn = e.target.closest("[data-date]");
      this._paintHover(btn ? parse(btn.dataset.date) : null);
    }

    _paintHover(target) {
      this.el.querySelectorAll(".is-hover-range").forEach((x) => x.classList.remove("is-hover-range"));
      if (!target || !this.start || this.end || target <= this.start) return;
      if (this._state(target).disabled) return;
      this.el.querySelectorAll("[data-date]").forEach((x) => {
        const d = parse(x.dataset.date);
        if (d > this.start && d <= target) x.classList.add("is-hover-range");
      });
    }
  }

  window.RangeCalendar = RangeCalendar;
  window.calUtil = { iso, parse, addDays, diffDays, fmt, fmtShort };
})();
