"""Sinh ảnh minh họa thiết bị dạng SVG (không cần ảnh ngoài, nhẹ, sắc nét mọi kích thước).

Mỗi tin đăng có `art = "kind:brand:color"` → 5 góc nhìn:
  0 = mặt trước, 1 = mặt sau / góc khác, 2 = bộ kit đi kèm, 3 = cận cảnh, 4 = bối cảnh sử dụng.
Khi chủ thuê upload ảnh thật, ảnh thật được ưu tiên hiển thị trước.
"""
from __future__ import annotations

from functools import lru_cache

KINDS = {"mirrorless", "dslr", "compact", "retro", "film", "lens", "action", "cam360", "drone", "fpv", "mini_guard", "vlog", "gimbal"}

PALETTES = [
    ("#FFE9D9", "#FFC9A6"),  # đào
    ("#E2F3EB", "#B9E1CF"),  # bạc hà
    ("#E5EEFB", "#BDD2F4"),  # trời
    ("#EEE7FA", "#D3C4F1"),  # oải hương
    ("#F7F0E1", "#E6D5AE"),  # cát
    ("#FCE6EB", "#F3C0CC"),  # hồng
    ("#E7F0F3", "#C4D9E1"),  # sương
    ("#FFF3D4", "#FFE09A"),  # bơ
]

BRANDS = {
    "sony": ("SONY", "#F08A24"),
    "canon": ("Canon", "#D7141A"),
    "fujifilm": ("FUJIFILM", "#2E9E5B"),
    "nikon": ("Nikon", "#FFD400"),
    "gopro": ("GoPro", "#1BA1E2"),
    "dji": ("DJI", "#A7B0BA"),
    "insta360": ("Insta360", "#FFD21F"),
    "olympus": ("OLYMPUS", "#3B6CC4"),
    "generic": ("", "#FF6A1A"),
}

BODY = {
    "black": ("#3A3D42", "#16171A"),
    "graphite": ("#5C6168", "#2F3236"),
    "grey": ("#8C939B", "#5B6168"),
    "silver": ("#E4E6E9", "#A8AEB6"),
    "white": ("#FAFAFA", "#D2D5D9"),
}

FONT = "Arial, Helvetica, sans-serif"


def _defs(bg: tuple[str, str], body: tuple[str, str], accent: str) -> str:
    return f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg[0]}"/><stop offset="1" stop-color="{bg[1]}"/></linearGradient>
<linearGradient id="body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{body[0]}"/><stop offset="1" stop-color="{body[1]}"/></linearGradient>
<linearGradient id="bodyh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{body[1]}"/><stop offset=".5" stop-color="{body[0]}"/><stop offset="1" stop-color="{body[1]}"/></linearGradient>
<linearGradient id="dark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E3035"/><stop offset="1" stop-color="#0E0F11"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F5F7"/><stop offset=".5" stop-color="#B9BEC5"/><stop offset="1" stop-color="#7E848C"/></linearGradient>
<radialGradient id="glass" cx=".36" cy=".34" r=".78"><stop offset="0" stop-color="#7C8FC4"/><stop offset=".25" stop-color="#3B4A7A"/><stop offset=".6" stop-color="#151A2C"/><stop offset="1" stop-color="#040508"/></radialGradient>
<radialGradient id="glass2" cx=".62" cy=".66" r=".5"><stop offset="0" stop-color="#9B6BC9" stop-opacity=".55"/><stop offset="1" stop-color="#9B6BC9" stop-opacity="0"/></radialGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8EC5FF"/><stop offset=".7" stop-color="#FFD9B8"/><stop offset="1" stop-color="#FFB98A"/></linearGradient>
<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B2F6B"/><stop offset=".6" stop-color="#A95D8C"/><stop offset="1" stop-color="#F6A365"/></linearGradient>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2BB3C0"/><stop offset="1" stop-color="#0C6E8C"/></linearGradient>
<linearGradient id="screen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7FC4FF"/><stop offset=".55" stop-color="#FFD7A8"/><stop offset=".56" stop-color="#3E8E63"/><stop offset="1" stop-color="#1F5B3D"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>
<filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<pattern id="grip" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#1A1B1E"/><circle cx="5" cy="5" r="1.6" fill="#2C2E33"/></pattern>
<pattern id="mesh" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M0 7h14M7 0v14" stroke="#000" stroke-opacity=".18" stroke-width="2"/></pattern>
<symbol id="acc" viewBox="0 0 10 10"><circle cx="5" cy="5" r="5" fill="{accent}"/></symbol>
</defs>"""


def _bg(seed: int) -> str:
    """Nền gradient + vài vòng tròn mờ trang trí."""
    a = 120 + (seed * 97) % 260
    b = 640 + (seed * 53) % 260
    return f"""<rect width="1000" height="1000" fill="url(#bg)"/>
<circle cx="{a}" cy="{180 + seed * 37 % 120}" r="210" fill="#fff" opacity=".28"/>
<circle cx="{b}" cy="{820 - seed * 29 % 120}" r="260" fill="#fff" opacity=".18"/>"""


def _shadow(cx: int = 500, cy: int = 720, rx: int = 270, ry: int = 26) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity=".16" filter="url(#blur)"/>'


def _lens(cx: float, cy: float, r: float, accent: str | None = None, barrel: str = "#141518") -> str:
    """Cụm ống kính nhìn chính diện: vành, vòng xoay, kính phản quang."""
    ring = f'<circle cx="{cx}" cy="{cy}" r="{r * .86:.1f}" fill="none" stroke="{accent}" stroke-width="{max(2, r * .03):.1f}"/>' if accent else ""
    return f"""<g>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="{barrel}"/>
<circle cx="{cx}" cy="{cy}" r="{r * .93:.1f}" fill="none" stroke="#2B2D31" stroke-width="{r * .1:.1f}" stroke-dasharray="3 5"/>
<circle cx="{cx}" cy="{cy}" r="{r * .8:.1f}" fill="#1C1D21" stroke="#34363B" stroke-width="3"/>
{ring}
<circle cx="{cx}" cy="{cy}" r="{r * .64:.1f}" fill="url(#glass)"/>
<circle cx="{cx}" cy="{cy}" r="{r * .64:.1f}" fill="url(#glass2)"/>
<circle cx="{cx}" cy="{cy}" r="{r * .42:.1f}" fill="none" stroke="#5A6A9E" stroke-opacity=".5" stroke-width="2"/>
<circle cx="{cx}" cy="{cy}" r="{r * .2:.1f}" fill="#06070B"/>
<path d="M{cx - r * .45:.1f} {cy - r * .18:.1f} A{r * .5:.1f} {r * .5:.1f} 0 0 1 {cx + r * .05:.1f} {cy - r * .5:.1f}" stroke="#fff" stroke-opacity=".6" stroke-width="{max(3, r * .07):.1f}" fill="none" stroke-linecap="round"/>
<circle cx="{cx + r * .22:.1f}" cy="{cy + r * .24:.1f}" r="{r * .06:.1f}" fill="#fff" opacity=".35"/>
</g>"""


def _label(x: float, y: float, text: str, size: int = 26, fill: str = "#ECEDEF", spacing: int = 3, weight: int = 700) -> str:
    if not text:
        return ""
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" font-weight="{weight}" '
            f'font-size="{size}" letter-spacing="{spacing}" fill="{fill}">{text}</text>')


def _screen(x: float, y: float, w: float, h: float, rx: float = 12) -> str:
    """Màn hình hiển thị phong cảnh mini."""
    return f"""<g>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#0B0D12"/>
<rect x="{x + w * .05:.1f}" y="{y + h * .07:.1f}" width="{w * .9:.1f}" height="{h * .86:.1f}" rx="{rx * .6:.1f}" fill="url(#screen)"/>
<circle cx="{x + w * .72:.1f}" cy="{y + h * .32:.1f}" r="{h * .1:.1f}" fill="#FFF4C2"/>
<path d="M{x + w * .05:.1f} {y + h * .62:.1f} L{x + w * .3:.1f} {y + h * .4:.1f} L{x + w * .5:.1f} {y + h * .58:.1f} L{x + w * .68:.1f} {y + h * .46:.1f} L{x + w * .95:.1f} {y + h * .64:.1f} V{y + h * .93:.1f} H{x + w * .05:.1f} Z" fill="#2F7A55" opacity=".9"/>
<rect x="{x + w * .05:.1f}" y="{y + h * .07:.1f}" width="{w * .9:.1f}" height="{h * .86:.1f}" rx="{rx * .6:.1f}" fill="none" stroke="#fff" stroke-opacity=".12" stroke-width="2"/>
</g>"""


# ----------------------------------------------------------------- cameras ---

def camera_front(kind: str, brand: str, color: str) -> str:
    label, accent = BRANDS.get(brand, BRANDS["generic"])
    retro = kind in {"retro", "film"}
    if kind == "compact":
        return compact_front(brand, color)
    big = kind == "dslr" or kind == "film"
    x0, x1 = (240, 760) if big else (265, 740)
    top, bottom = (405, 660) if big else (415, 645)
    hump_w = 95 if big else 75
    hump_h = 115 if big else 85
    cx = 515
    parts = [_shadow(500, bottom + 55, 300, 28)]
    # Thân máy
    parts.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bottom - top}" rx="34" fill="url(#body)"/>')
    if retro:
        # Da bọc đen phía dưới tấm đỉnh bạc — kiểu Fujifilm X-T / máy film
        parts.append(f'<rect x="{x0 + 6}" y="{top + 48}" width="{x1 - x0 - 12}" height="{bottom - top - 70}" rx="8" fill="url(#grip)"/>')
    # Báng cầm
    if not retro:
        parts.append(f'<rect x="{x0 - 18}" y="{top - 4}" width="122" height="{bottom - top + 8}" rx="44" fill="url(#grip)"/>')
        parts.append(f'<ellipse cx="{x0 + 42}" cy="{top - 4}" rx="34" ry="11" fill="#9EA3AA"/>')
    # Gù ngắm / lăng kính
    hx0, hx1 = cx - hump_w, cx + hump_w
    parts.append(
        f'<path d="M{hx0 - 30} {top + 2} L{hx0 + 4} {top - hump_h + 12} Q{hx0 + 10} {top - hump_h} {hx0 + 26} {top - hump_h} '
        f'L{hx1 - 26} {top - hump_h} Q{hx1 - 10} {top - hump_h} {hx1 - 4} {top - hump_h + 12} L{hx1 + 30} {top + 2} Z" fill="url(#body)"/>'
    )
    if retro:
        parts.append(f'<rect x="{hx0 + 8}" y="{top - hump_h + 30}" width="{hx1 - hx0 - 16}" height="{hump_h - 36}" rx="6" fill="#1B1C1F"/>')
        # Bánh xe tốc độ / ISO trên đỉnh
        for dx in (-205, 175):
            parts.append(f'<rect x="{cx + dx}" y="{top - 46}" width="70" height="46" rx="8" fill="url(#metal)"/>')
            parts.append(f'<path d="M{cx + dx + 8} {top - 40}v34M{cx + dx + 20} {top - 40}v34M{cx + dx + 32} {top - 40}v34M{cx + dx + 44} {top - 40}v34M{cx + dx + 56} {top - 40}v34" stroke="#6E747C" stroke-width="3"/>')
        if kind == "film":
            parts.append(f'<rect x="{cx + 130}" y="{top - 22}" width="110" height="14" rx="7" fill="url(#metal)"/>')
    else:
        parts.append(f'<rect x="{x1 - 120}" y="{top - 30}" width="80" height="30" rx="8" fill="#1E1F23"/>')
        parts.append(f'<path d="M{x1 - 112} {top - 26}v22M{x1 - 100} {top - 26}v22M{x1 - 88} {top - 26}v22M{x1 - 76} {top - 26}v22M{x1 - 64} {top - 26}v22" stroke="#3A3C42" stroke-width="3"/>')
    label_fill = "#1B1C1F" if color in {"silver", "white"} and not retro else "#ECEDEF"
    parts.append(_label(cx, top - hump_h + (58 if retro else 50), label, size=19 if len(label) > 6 else 24 if len(label) > 4 else 28,
                        fill="#ECEDEF" if retro else label_fill, spacing=2 if len(label) > 6 else 3))
    # Ngàm + ống kính
    lens_r = 158 if big else 140
    mount_ring = accent if brand in {"canon", "sony"} else None
    parts.append(f'<circle cx="{cx}" cy="{(top + bottom) // 2 + 8}" r="{lens_r + 14}" fill="url(#metal)"/>')
    parts.append(_lens(cx, (top + bottom) // 2 + 8, lens_r, mount_ring, "#121316" if not retro else "#1A1B1E"))
    if retro:
        parts.append(f'<circle cx="{cx}" cy="{(top + bottom) // 2 + 8}" r="{lens_r * .95:.0f}" fill="none" stroke="url(#metal)" stroke-width="10"/>')
    # Đèn trợ sáng AF
    parts.append(f'<circle cx="{x1 - 60}" cy="{top + 50}" r="11" fill="#2A1A12" stroke="#5B4636" stroke-width="3"/>')
    return "\n".join(parts)


def compact_front(brand: str, color: str) -> str:
    label, accent = BRANDS.get(brand, BRANDS["generic"])
    retro = color == "silver"
    x0, x1, top, bottom = 270, 730, 420, 640
    parts = [_shadow(500, 700, 270, 24)]
    parts.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bottom - top}" rx="30" fill="url(#body)"/>')
    if retro:
        parts.append(f'<rect x="{x0 + 4}" y="{top + 58}" width="{x1 - x0 - 8}" height="{bottom - top - 88}" rx="6" fill="url(#grip)"/>')
        # Cửa sổ ngắm quang học
        parts.append(f'<rect x="{x0 + 30}" y="{top + 14}" width="92" height="44" rx="6" fill="#0E1018" stroke="#2C2F36" stroke-width="4"/>')
        parts.append(f'<rect x="{x0 + 36}" y="{top + 20}" width="40" height="32" rx="3" fill="url(#glass)"/>')
        for dx in (110, 190):
            parts.append(f'<rect x="{x1 - dx}" y="{top - 34}" width="62" height="34" rx="7" fill="url(#metal)"/>')
    else:
        parts.append(f'<rect x="{x0 - 2}" y="{top + 30}" width="64" height="{bottom - top - 60}" rx="22" fill="#1E1F23"/>')
        parts.append(f'<rect x="{x0 + 90}" y="{top - 26}" width="150" height="26" rx="10" fill="url(#body)"/>')
        parts.append(f'<ellipse cx="{x1 - 140}" cy="{top - 6}" rx="40" ry="10" fill="#A1A6AD"/>')
    if retro:
        parts.append(_label(x0 + 95, bottom - 28, label, size=18, fill="#E5E6E8", spacing=2))
    else:
        parts.append(_label(x0 + 165, top + 46, label, size=22, fill="#E5E6E8"))
    cy = (top + bottom) // 2 + 14
    parts.append(f'<circle cx="565" cy="{cy}" r="{120 if retro else 112}" fill="{"url(#metal)" if retro else "#232428"}"/>')
    parts.append(_lens(565, cy, 100 if retro else 96, accent if brand == "canon" else None))
    parts.append(f'<circle cx="{x1 - 40}" cy="{top + 40}" r="9" fill="#2A1A12" stroke="#5B4636" stroke-width="3"/>')
    return "\n".join(parts)


def camera_back(kind: str, brand: str, color: str) -> str:
    label, accent = BRANDS.get(brand, BRANDS["generic"])
    compact = kind == "compact"
    x0, x1, top, bottom = (270, 730, 420, 640) if compact else (250, 750, 410, 650)
    parts = [_shadow(500, bottom + 55, 300, 28)]
    parts.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bottom - top}" rx="32" fill="url(#body)"/>')
    if not compact:
        parts.append(
            f'<path d="M420 {top + 2} L440 {top - 85} Q446 {top - 95} 458 {top - 95} L572 {top - 95} Q584 {top - 95} 590 {top - 85} L610 {top + 2} Z" fill="url(#body)"/>'
        )
        parts.append(f'<rect x="455" y="{top - 82}" width="120" height="70" rx="22" fill="#111215"/>')
        parts.append(f'<rect x="478" y="{top - 64}" width="74" height="36" rx="8" fill="#20232B"/>')
    sx, sw = (300, 300) if not compact else (300, 320)
    parts.append(_screen(sx, top + 40, sw, bottom - top - 80, 14))
    # Nút bấm & bánh xe
    bx = sx + sw + 40
    parts.append(f'<circle cx="{bx + 40}" cy="{top + 130}" r="44" fill="#1C1D21" stroke="#34363B" stroke-width="6"/>')
    parts.append(f'<circle cx="{bx + 40}" cy="{top + 130}" r="16" fill="#2B2D32"/>')
    for i, dy in enumerate((40, 210)):
        parts.append(f'<circle cx="{bx + 40}" cy="{top + dy}" r="15" fill="{accent if i == 0 else "#2B2D32"}"/>')
    parts.append(f'<rect x="{x0 + 20}" y="{top + 30}" width="12" height="{bottom - top - 60}" rx="6" fill="#000" opacity=".15"/>')
    parts.append(_label(500, bottom - 14, label, size=16, fill="#9097A0", spacing=4))
    return "\n".join(parts)


def lens_side(brand: str, color: str) -> str:
    label, accent = BRANDS.get(brand, BRANDS["generic"])
    parts = [_shadow(500, 700, 260, 24)]
    parts.append('<rect x="250" y="425" width="46" height="150" rx="8" fill="url(#metal)"/>')
    parts.append('<rect x="290" y="395" width="420" height="210" rx="22" fill="url(#body)"/>')
    # Vòng zoom (cao su) & vòng lấy nét
    parts.append('<rect x="400" y="388" width="140" height="224" rx="14" fill="url(#grip)"/>')
    parts.append('<path d="' + "".join(f"M{410 + i * 9} 392v216" for i in range(14)) + '" stroke="#0B0B0D" stroke-width="3" opacity=".7"/>')
    parts.append('<rect x="580" y="390" width="80" height="220" rx="12" fill="#18191C"/>')
    parts.append('<path d="' + "".join(f"M{586 + i * 8} 394v212" for i in range(9)) + '" stroke="#0B0B0D" stroke-width="3" opacity=".7"/>')
    parts.append(f'<rect x="552" y="398" width="12" height="204" rx="4" fill="{accent}"/>')
    parts.append('<rect x="700" y="375" width="70" height="250" rx="16" fill="#141518"/>')
    parts.append('<ellipse cx="770" cy="500" rx="26" ry="118" fill="url(#glass)"/>')
    parts.append('<path d="M760 420 Q772 470 768 520" stroke="#fff" stroke-opacity=".55" stroke-width="7" fill="none" stroke-linecap="round"/>')
    parts.append(_label(345, 512, label, size=18, fill="#C9CDD2", spacing=2))
    parts.append(f'<rect x="300" y="455" width="90" height="4" rx="2" fill="{accent}" opacity=".8"/>')
    return "\n".join(parts)


def lens_front(brand: str, color: str) -> str:
    _, accent = BRANDS.get(brand, BRANDS["generic"])
    return _shadow(500, 760, 230, 26) + _lens(500, 500, 230, accent)


# ------------------------------------------------------------- action cams ---

def action_front(brand: str, color: str) -> str:
    label, accent = BRANDS.get(brand, BRANDS["generic"])
    parts = [_shadow(500, 720, 230, 24)]
    parts.append('<rect x="485" y="640" width="30" height="46" rx="6" fill="#26282C"/><rect x="445" y="640" width="30" height="46" rx="6" fill="#26282C"/><rect x="525" y="640" width="30" height="46" rx="6" fill="#26282C"/>')
    parts.append('<rect x="320" y="360" width="360" height="290" rx="52" fill="url(#body)"/>')
    parts.append('<rect x="320" y="360" width="360" height="290" rx="52" fill="url(#mesh)" opacity=".35"/>')
    if brand == "gopro":
        parts.append('<rect x="352" y="400" width="150" height="150" rx="20" fill="#0B0D12"/>')
        parts.append('<rect x="362" y="410" width="130" height="130" rx="14" fill="url(#screen)"/>')
        parts.append(_label(427, 485, "4K·120", size=20, fill="#fff", spacing=1))
        parts.append('<rect x="522" y="392" width="132" height="132" rx="28" fill="#0F1013" stroke="#2D2F34" stroke-width="6"/>')
        parts.append(_lens(588, 458, 50))
        parts.append(_label(420, 612, label, size=30, fill="#F2F3F5", spacing=0))
        parts.append(f'<circle cx="640" cy="606" r="8" fill="#E5262B"/>')
    else:
        parts.append('<rect x="352" y="400" width="140" height="150" rx="20" fill="#0B0D12"/>')
        parts.append('<rect x="362" y="410" width="120" height="130" rx="14" fill="url(#screen)"/>')
        parts.append('<circle cx="585" cy="470" r="76" fill="#121316" stroke="#3A3D43" stroke-width="8"/>')
        parts.append(_lens(585, 470, 56))
        parts.append(_label(425, 612, label, size=30, fill="#F2F3F5", spacing=4))
        parts.append(f'<rect x="555" y="594" width="80" height="14" rx="7" fill="{accent}" opacity=".9"/>')
    parts.append('<rect x="560" y="342" width="70" height="22" rx="10" fill="#E5262B"/>')
    return "\n".join(parts)


def action_back(brand: str, color: str) -> str:
    label, _ = BRANDS.get(brand, BRANDS["generic"])
    parts = [_shadow(500, 720, 230, 24)]
    parts.append('<rect x="320" y="360" width="360" height="290" rx="52" fill="url(#body)"/>')
    parts.append(_screen(345, 385, 310, 220, 22))
    parts.append(_label(500, 636, label, size=20, fill="#AEB4BB", spacing=4))
    parts.append('<rect x="560" y="342" width="70" height="22" rx="10" fill="#E5262B"/>')
    return "\n".join(parts)


def cam360(brand: str, color: str, back: bool = False) -> str:
    label, accent = BRANDS.get(brand, BRANDS["generic"])
    parts = [_shadow(500, 900, 150, 20)]
    parts.append('<rect x="488" y="760" width="24" height="240" rx="6" fill="#3A3C40"/>')
    parts.append('<rect x="420" y="210" width="160" height="580" rx="74" fill="url(#bodyh)"/>')
    parts.append('<circle cx="500" cy="330" r="86" fill="#0B0B0E" stroke="#2F3136" stroke-width="10"/>')
    parts.append(_lens(500, 330, 68, accent))
    parts.append('<path d="M448 286 Q470 258 512 254" stroke="#fff" stroke-opacity=".5" stroke-width="10" fill="none" stroke-linecap="round"/>')
    if not back:
        parts.append(_screen(442, 448, 116, 150, 14))
        parts.append(f'<circle cx="500" cy="660" r="26" fill="#1D1E22" stroke="{accent}" stroke-width="6"/>')
    else:
        parts.append(f'<rect x="460" y="460" width="80" height="12" rx="6" fill="{accent}"/>')
    parts.append(f'<text x="500" y="730" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="18" fill="#C9CDD2">{label}</text>')
    return "\n".join(parts)


# ------------------------------------------------------------------ drones ---

def _prop(mx: float, my: float, r: float, angle: int) -> str:
    return f"""<circle cx="{mx}" cy="{my}" r="{r}" fill="#000" opacity=".06"/>
<circle cx="{mx}" cy="{my}" r="{r}" fill="none" stroke="#000" stroke-opacity=".08" stroke-width="3"/>
<g transform="translate({mx} {my}) rotate({angle})"><rect x="{-r}" y="-10" width="{2 * r}" height="20" rx="10" fill="#33363B" opacity=".9"/></g>
<circle cx="{mx}" cy="{my}" r="30" fill="url(#dark)"/><circle cx="{mx}" cy="{my}" r="11" fill="#8E949B"/>"""


def drone_top(kind: str, brand: str, color: str) -> str:
    _, accent = BRANDS.get(brand, BRANDS["generic"])
    parts = [_shadow(500, 790, 300, 30)]
    if kind in {"fpv", "mini_guard"}:
        # Drone có lồng bảo vệ cánh (Avata / Neo / Flip)
        off = 150 if kind == "fpv" else 140
        r = 118 if kind == "fpv" else 110
        motors = [(500 - off, 500 - off), (500 + off, 500 - off), (500 - off, 500 + off), (500 + off, 500 + off)]
        for i, (mx, my) in enumerate(motors):
            parts.append(_prop(mx, my, r - 18, 25 + i * 40))
            parts.append(f'<circle cx="{mx}" cy="{my}" r="{r}" fill="none" stroke="url(#body)" stroke-width="{28 if kind == "fpv" else 18}"/>')
            if kind == "mini_guard":
                parts.append(f'<circle cx="{mx}" cy="{my}" r="{r}" fill="url(#mesh)" opacity=".5"/>')
        w, h = (190, 250) if kind == "fpv" else (150, 190)
        parts.append(f'<rect x="{500 - w / 2}" y="{500 - h / 2}" width="{w}" height="{h}" rx="{w * .38:.0f}" fill="url(#body)"/>')
        parts.append(f'<rect x="{500 - w / 2 + 22}" y="{500 - h / 2 + 30}" width="{w - 44}" height="{h - 70}" rx="{w * .3:.0f}" fill="#fff" opacity=".08"/>')
        parts.append(f'<circle cx="500" cy="{500 - h / 2 + 4}" r="34" fill="#111"/>')
        parts.append(_lens(500, 500 - h / 2 + 4, 24))
        parts.append(f'<rect x="470" y="{500 + h / 2 - 34}" width="60" height="10" rx="5" fill="{accent}" opacity=".8"/>')
        return "\n".join(parts)
    size = {"drone": 1.0}.get(kind, 1.0)
    big = brand == "dji" and color == "graphite"  # dòng Mavic: thân lớn, xám đậm
    off_x, off_y = (215, 205) if big else (200, 190)
    motors = [(500 - off_x, 500 - off_y), (500 + off_x, 500 - off_y), (500 - off_x - 20, 500 + off_y + 10), (500 + off_x + 20, 500 + off_y + 10)]
    for mx, my in motors:
        parts.append(f'<line x1="500" y1="500" x2="{mx}" y2="{my}" stroke="url(#body)" stroke-width="{38 * size:.0f}" stroke-linecap="round"/>')
    for i, (mx, my) in enumerate(motors):
        parts.append(_prop(mx, my, 135, 20 + i * 47))
    w, h = (210, 330) if big else (170, 280)
    parts.append(f'<rect x="{500 - w / 2}" y="{500 - h / 2}" width="{w}" height="{h}" rx="{w * .4:.0f}" fill="url(#body)"/>')
    parts.append(f'<rect x="{500 - w / 2 + 26}" y="{500 - h / 2 + 50}" width="{w - 52}" height="{h - 110}" rx="{w * .28:.0f}" fill="#fff" opacity=".1"/>')
    parts.append(f'<rect x="{500 - 30}" y="{500 + h / 2 - 60}" width="60" height="26" rx="8" fill="#1A1B1E" opacity=".75"/>')
    # Cụm gimbal phía trước
    gy = 500 - h / 2 - 14
    parts.append(f'<rect x="450" y="{gy - 30}" width="100" height="74" rx="30" fill="#1A1B1F"/>')
    parts.append(_lens(500, gy + 4, 28))
    parts.append(f'<circle cx="{500 - w / 2 + 20}" cy="{500 - h / 2 + 30}" r="6" fill="#36D27A"/><circle cx="{500 + w / 2 - 20}" cy="{500 - h / 2 + 30}" r="6" fill="#36D27A"/>')
    return "\n".join(parts)


def drone_front(kind: str, brand: str, color: str) -> str:
    parts = [_shadow(500, 700, 340, 26)]
    if kind in {"fpv", "mini_guard"}:
        parts.append('<ellipse cx="300" cy="500" rx="160" ry="44" fill="none" stroke="url(#body)" stroke-width="26"/>')
        parts.append('<ellipse cx="700" cy="500" rx="160" ry="44" fill="none" stroke="url(#body)" stroke-width="26"/>')
        parts.append('<ellipse cx="300" cy="490" rx="140" ry="14" fill="#2C2F34" opacity=".35"/><ellipse cx="700" cy="490" rx="140" ry="14" fill="#2C2F34" opacity=".35"/>')
        parts.append('<rect x="400" y="430" width="200" height="150" rx="56" fill="url(#body)"/>')
        parts.append('<rect x="440" y="520" width="120" height="88" rx="30" fill="#141518"/>')
        parts.append(_lens(500, 562, 34))
        return "\n".join(parts)
    parts.append('<path d="M500 470 L200 520 M500 470 L800 520" stroke="url(#body)" stroke-width="34" stroke-linecap="round"/>')
    parts.append('<path d="M330 540 L310 640 M670 540 L690 640" stroke="#2B2D31" stroke-width="14" stroke-linecap="round"/>')
    for mx in (200, 800):
        parts.append(f'<rect x="{mx - 26}" y="470" width="52" height="62" rx="16" fill="url(#dark)"/>')
        parts.append(f'<ellipse cx="{mx}" cy="462" rx="175" ry="16" fill="#2E3136" opacity=".45"/>')
        parts.append(f'<ellipse cx="{mx}" cy="462" rx="175" ry="16" fill="none" stroke="#000" stroke-opacity=".1" stroke-width="3"/>')
    parts.append('<path d="M390 430 Q500 380 610 430 L630 520 Q500 560 370 520 Z" fill="url(#body)"/>')
    parts.append('<rect x="452" y="520" width="96" height="90" rx="34" fill="#141518"/>')
    parts.append(_lens(500, 566, 36))
    parts.append('<rect x="420" y="452" width="40" height="22" rx="8" fill="#0D0E10" opacity=".8"/><rect x="540" y="452" width="40" height="22" rx="8" fill="#0D0E10" opacity=".8"/>')
    return "\n".join(parts)


# ------------------------------------------------------------ vlog / gimbal ---

def vlog_pocket(brand: str, color: str, back: bool = False) -> str:
    _, accent = BRANDS.get(brand, BRANDS["generic"])
    parts = [_shadow(500, 850, 150, 20)]
    parts.append('<rect x="440" y="440" width="120" height="400" rx="52" fill="url(#bodyh)"/>')
    if not back:
        parts.append(_screen(392, 455, 216, 128, 16))
        parts.append('<circle cx="500" cy="680" r="24" fill="#1A1B1E" stroke="#E5262B" stroke-width="6"/>')
        parts.append('<circle cx="500" cy="752" r="16" fill="#2A2C31"/>')
    else:
        parts.append(f'<rect x="470" y="600" width="60" height="10" rx="5" fill="{accent}"/>')
    parts.append('<rect x="470" y="330" width="60" height="130" rx="22" fill="url(#body)"/>')
    parts.append('<circle cx="500" cy="300" r="74" fill="url(#dark)"/>')
    parts.append(_lens(500, 300, 50))
    return "\n".join(parts)


def gimbal(brand: str, color: str) -> str:
    _, accent = BRANDS.get(brand, BRANDS["generic"])
    parts = [_shadow(500, 900, 180, 20)]
    parts.append('<rect x="465" y="560" width="70" height="320" rx="28" fill="url(#bodyh)"/>')
    parts.append('<circle cx="500" cy="650" r="20" fill="#1A1B1E" stroke="#E5262B" stroke-width="5"/>')
    parts.append(f'<rect x="478" y="720" width="44" height="64" rx="10" fill="#0E1015"/><rect x="484" y="726" width="32" height="52" rx="6" fill="{accent}" opacity=".35"/>')
    parts.append('<circle cx="500" cy="540" r="52" fill="url(#body)"/><circle cx="500" cy="540" r="22" fill="#1A1B1E"/>')
    parts.append('<rect x="540" y="250" width="44" height="300" rx="18" fill="url(#body)"/>')
    parts.append('<circle cx="562" cy="250" r="50" fill="url(#body)"/><circle cx="562" cy="250" r="20" fill="#1A1B1E"/>')
    parts.append('<rect x="300" y="228" width="270" height="40" rx="16" fill="url(#body)"/>')
    parts.append('<circle cx="300" cy="320" r="46" fill="url(#body)"/><circle cx="300" cy="320" r="18" fill="#1A1B1E"/>')
    parts.append('<rect x="290" y="250" width="22" height="80" rx="10" fill="url(#body)"/>')
    # Máy ảnh gắn trên gimbal
    parts.append('<rect x="340" y="300" width="200" height="130" rx="18" fill="#26282C"/>')
    parts.append('<rect x="400" y="276" width="80" height="30" rx="8" fill="#26282C"/>')
    parts.append(_lens(450, 372, 58))
    return "\n".join(parts)


# ---------------------------------------------------------------- dispatch ---

def product(kind: str, brand: str, color: str, view: int = 0) -> str:
    """view 0 = chính diện, 1 = mặt sau / góc khác."""
    if kind in {"mirrorless", "dslr", "retro", "film", "compact"}:
        return camera_front(kind, brand, color) if view == 0 else camera_back(kind, brand, color)
    if kind == "lens":
        return lens_side(brand, color) if view == 0 else lens_front(brand, color)
    if kind == "action":
        return action_front(brand, color) if view == 0 else action_back(brand, color)
    if kind == "cam360":
        return cam360(brand, color, back=view == 1)
    if kind in {"drone", "fpv", "mini_guard"}:
        return drone_top(kind, brand, color) if view == 0 else drone_front(kind, brand, color)
    if kind == "vlog":
        return vlog_pocket(brand, color, back=view == 1)
    if kind == "gimbal":
        return gimbal(brand, color)
    return camera_front("mirrorless", brand, color)


def kit(kind: str, brand: str, color: str) -> str:
    """Bố cục flat-lay: máy + pin + thẻ nhớ + sạc + túi/tay cầm điều khiển."""
    _, accent = BRANDS.get(brand, BRANDS["generic"])
    is_drone = kind in {"drone", "fpv", "mini_guard"}
    parts = ['<rect x="70" y="90" width="860" height="820" rx="48" fill="#fff" opacity=".55"/>']
    parts.append(f'<g transform="translate(70 40) scale(.62)">{product(kind, brand, color, 0)}</g>')
    # Pin
    for i in range(3 if is_drone else 2):
        x = 620 + i * 92
        parts.append(f'<rect x="{x}" y="160" width="74" height="{150 if is_drone else 120}" rx="14" fill="url(#dark)"/>')
        parts.append(f'<rect x="{x + 12}" y="{180}" width="50" height="10" rx="5" fill="{accent}"/>')
        parts.append(f'<rect x="{x + 22}" y="{230 if is_drone else 215}" width="30" height="30" rx="6" fill="#fff" opacity=".12"/>')
    # Thẻ nhớ
    parts.append('<path d="M640 420 h86 l22 22 v110 h-108 Z" fill="#1E2A44"/><rect x="650" y="470" width="88" height="40" rx="4" fill="#E8B531"/>')
    parts.append(_label(694, 498, "128GB", size=16, fill="#1E2A44", spacing=0))
    if is_drone:
        # Tay cầm điều khiển có màn hình (RC 2)
        parts.append('<rect x="160" y="640" width="380" height="200" rx="60" fill="url(#dark)"/>')
        parts.append(_screen(250, 668, 200, 120, 12))
        parts.append('<circle cx="200" cy="740" r="26" fill="#2A2C31"/><circle cx="500" cy="740" r="26" fill="#2A2C31"/>')
        parts.append('<g transform="translate(600 650) rotate(-18)"><rect x="0" y="0" width="230" height="22" rx="11" fill="#3A3D42"/><rect x="0" y="50" width="230" height="22" rx="11" fill="#3A3D42"/></g>')
    else:
        # Sạc + dây đeo + túi
        parts.append('<rect x="180" y="680" width="150" height="110" rx="22" fill="#F1F2F4" stroke="#C9CDD2" stroke-width="4"/>')
        parts.append('<rect x="210" y="650" width="16" height="34" rx="4" fill="#9AA0A8"/><rect x="284" y="650" width="16" height="34" rx="4" fill="#9AA0A8"/>')
        parts.append(f'<path d="M380 820 C460 700 540 860 620 740 S760 700 830 780" stroke="{accent}" stroke-width="22" fill="none" stroke-linecap="round" opacity=".85"/>')
        parts.append('<rect x="790" y="420" width="90" height="140" rx="20" fill="none" stroke="#3A3D42" stroke-width="8" stroke-dasharray="14 10"/>')
    return "\n".join(parts)


def detail(kind: str, brand: str, color: str) -> str:
    """Cận cảnh: ống kính (máy ảnh/action) hoặc cụm gimbal (flycam)."""
    _, accent = BRANDS.get(brand, BRANDS["generic"])
    if kind in {"drone", "fpv", "mini_guard"}:
        return f"""<rect x="150" y="80" width="700" height="360" rx="170" fill="url(#body)"/>
<rect x="300" y="380" width="400" height="300" rx="140" fill="url(#dark)"/>
<rect x="210" y="430" width="70" height="200" rx="30" fill="url(#body)"/><rect x="720" y="430" width="70" height="200" rx="30" fill="url(#body)"/>
{_lens(500, 560, 150, accent)}
"""
    if kind == "cam360":
        return _lens(500, 520, 330, accent) + '<path d="M260 380 Q330 230 520 200" stroke="#fff" stroke-opacity=".5" stroke-width="22" fill="none" stroke-linecap="round"/>'
    ring = (
        f'<path id="arc" d="M180 520 A320 320 0 0 1 820 520" fill="none"/>'
        f'<text font-family="{FONT}" font-size="34" font-weight="700" letter-spacing="6" fill="#C9CDD2">'
        f'<textPath href="#arc" startOffset="50%" text-anchor="middle">{BRANDS.get(brand, BRANDS["generic"])[0]} · LENS</textPath></text>'
    )
    return f'<circle cx="500" cy="520" r="420" fill="#131416"/>{_lens(500, 520, 390, accent)}{ring}'


def scene(kind: str, brand: str, color: str, seed: int) -> str:
    """Bối cảnh sử dụng: núi (flycam), biển (action cam), phố cổ (máy ảnh), thành phố đêm (360)."""
    if kind in {"drone", "fpv", "mini_guard"}:
        bgp = f"""<rect width="1000" height="1000" fill="url(#sky)"/>
<circle cx="760" cy="300" r="90" fill="#FFF1C9"/>
<path d="M0 640 L180 470 L330 600 L520 420 L700 590 L860 480 L1000 560 V1000 H0 Z" fill="#6E9AB8" opacity=".55"/>
<path d="M0 760 L150 640 L320 740 L470 620 L650 760 L820 650 L1000 730 V1000 H0 Z" fill="#3F7D5C"/>
<path d="M0 860 Q250 800 500 860 T1000 850 V1000 H0 Z" fill="#2D6146"/>
<path d="M60 900 Q300 860 560 905 M120 950 Q380 910 700 955" stroke="#A9D18E" stroke-width="6" fill="none" opacity=".6"/>"""
        return bgp + f'<g transform="translate(330 120) scale(.42) rotate(-10 500 500)">{drone_top(kind, brand, color)}</g>'
    if kind == "action":
        bgp = """<rect width="1000" height="1000" fill="url(#sky)"/>
<circle cx="250" cy="330" r="80" fill="#FFF1C9"/>
<rect y="560" width="1000" height="440" fill="url(#sea)"/>
<path d="M0 620 Q80 600 160 620 T320 620 T480 620 T640 620 T800 620 T960 620 T1120 620" stroke="#fff" stroke-opacity=".5" stroke-width="6" fill="none"/>
<path d="M0 700 Q80 680 160 700 T320 700 T480 700 T640 700 T800 700 T960 700 T1120 700" stroke="#fff" stroke-opacity=".35" stroke-width="6" fill="none"/>
<path d="M0 880 Q260 820 520 880 T1000 860 V1000 H0 Z" fill="#F4D9A6"/>"""
        return bgp + f'<g transform="translate(470 470) scale(.5) rotate(-8 500 500)">{action_front(brand, color)}</g>'
    if kind == "cam360":
        bld = "".join(
            f'<rect x="{x}" y="{h}" width="{w}" height="{1000 - h}" fill="#1D2147" opacity=".9"/>'
            + "".join(f'<rect x="{x + 12 + j * 22}" y="{h + 20 + k * 34}" width="10" height="16" fill="#FFD27A" opacity="{.35 + (j + k) % 3 * .2:.2f}"/>' for j in range(max(1, (w - 20) // 22)) for k in range(5))
            for x, w, h in ((0, 140, 560), (130, 110, 480), (230, 160, 600), (380, 120, 430), (490, 170, 520), (650, 120, 460), (760, 140, 580), (890, 120, 500))
        )
        return '<rect width="1000" height="1000" fill="url(#dusk)"/><circle cx="780" cy="230" r="60" fill="#FFE7B3" opacity=".9"/>' + bld + f'<g transform="translate(250 60) scale(.5)">{cam360(brand, color)}</g>'
    # Phố cổ với đèn lồng — máy ảnh, ống kính, vlog
    lantern_colors = ["#F2542D", "#FFB627", "#E23E57", "#F7A072"]
    lanterns = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{y - 40}" stroke="#5B3A29" stroke-width="3"/><ellipse cx="{x}" cy="{y}" rx="32" ry="42" fill="{lantern_colors[i % 4]}"/><rect x="{x - 14}" y="{y - 48}" width="28" height="10" fill="#5B3A29"/>'
        for i, (x, y) in enumerate(((120, 170), (290, 120), (470, 190), (640, 130), (820, 180)))
    )
    houses = """<rect x="0" y="420" width="260" height="580" fill="#F2C14E"/><path d="M-20 430 L130 330 L280 430 Z" fill="#8C3B2E"/>
<rect x="250" y="380" width="280" height="620" fill="#E9A84B"/><path d="M230 390 L390 290 L550 390 Z" fill="#7A2F24"/>
<rect x="520" y="440" width="240" height="560" fill="#F4CF6B"/><path d="M500 450 L640 360 L780 450 Z" fill="#8C3B2E"/>
<rect x="750" y="400" width="260" height="600" fill="#E5A443"/><path d="M730 410 L880 310 L1030 410 Z" fill="#7A2F24"/>
<rect x="60" y="520" width="80" height="110" fill="#6B8F71"/><rect x="330" y="500" width="90" height="120" fill="#6B8F71"/><rect x="600" y="540" width="80" height="110" fill="#6B8F71"/><rect x="820" y="520" width="90" height="120" fill="#6B8F71"/>
<rect y="820" width="1000" height="180" fill="#C8B79E"/>"""
    target = product(kind, brand, color, 0)
    return f'<rect width="1000" height="1000" fill="#FFE9C7"/>{houses}{lanterns}<g transform="translate(250 330) scale(.74)">{target}</g>'


@lru_cache(maxsize=2048)
def render(art: str, palette: int = 0, view: int = 0) -> str:
    kind, brand, color = (art.split(":") + ["", "", ""])[:3]
    kind = kind if kind in KINDS else "mirrorless"
    brand = brand if brand in BRANDS else "generic"
    color = color if color in BODY else "black"
    palette = palette % len(PALETTES)
    view = view % 5
    _, accent = BRANDS[brand]
    bg = PALETTES[(palette + view) % len(PALETTES)]
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">{_defs(bg, BODY[color], accent)}'
    if view == 4:
        body = scene(kind, brand, color, palette)
    elif view == 3:
        body = _bg(palette + 3) + detail(kind, brand, color)
    elif view == 2:
        body = _bg(palette + 2) + kit(kind, brand, color)
    else:
        body = _bg(palette + view) + f'<g transform="translate(500 500) scale(1.16) translate(-500 -520)">{product(kind, brand, color, view)}</g>'
    return head + body + "</svg>"
