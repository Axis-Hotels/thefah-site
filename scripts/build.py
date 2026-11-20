#!/usr/bin/env python3
"""Build The FAH pages.

Outputs
  tilda/thefah-{en,ru,th}.html   code for the Tilda T123 "HTML code" block (photos from asset_base)
  tilda/НАСТРОЙКИ СТРАНИЦ.md     title, description, page address and HEAD code for Tilda
  docs/{en,ru,th}/index.html     standalone previews for GitHub Pages (photos from ../img)
  docs/logo.svg                  full logo lockup

Python standard library only: python3 scripts/build.py
"""
import json
import math
import random
import re
import sys
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
LANGS = ["en", "ru", "th"]
LANG_LABEL = {"en": "EN", "ru": "RU", "th": "TH"}
HOTEL_NAME = "the Fah by Axis.Bangkok"
TH_ADDRESS = "128/10–11 ซอยสีลม 6 ถนนสีลม แขวงสุริยวงศ์ เขตบางรัก กรุงเทพมหานคร 10500"
SVG_NS = "http://www.w3.org/2000/svg"
HOTEL_PHOTOS = ["hotel-lounge", "hotel-facade", "hotel-entrance"]
HERO_PHOTO = "king-red"
PEEK_PHOTOS = ["suite-bedroom", "king-red", "twin-main"]


def load(name):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def e(text):
    return escape(str(text), quote=True)


def plural(n, forms, lang):
    if lang == "ru" and len(forms) == 3:
        n = abs(n) % 100
        if 11 <= n <= 19:
            return forms[2]
        n %= 10
        return forms[0] if n == 1 else forms[1] if 2 <= n <= 4 else forms[2]
    return forms[0] if n == 1 else forms[1]


# ---------- logo ----------

def logo_parts():
    ET.register_namespace("", SVG_NS)
    root = ET.parse(ROOT / "source/logo/The_FAH_by_Axis_Bangkok.svg").getroot()

    def part(el_id):
        el = root.find(f".//*[@id='{el_id}']")
        s = ET.tostring(el, encoding="unicode")
        s = s.replace(f' xmlns="{SVG_NS}"', "")
        s = re.sub(r'\s+id="[^"]*"', "", s)
        s = s.replace("#102843", "currentColor").replace("#273E57", "currentColor")
        s = re.sub(r"<title[^>]*>.*?</title>", "", s, flags=re.S)
        return re.sub(r"\s+", " ", s).strip()

    return {k: part(v) for k, v in {"wing": "fah-wing", "word": "fah-wordmark", "rule": "copper-accent",
                                    "axis": "axis-bangkok-endorsement"}.items()}


def logo_symbol(full):
    """Hero copy defines the full logo once as a symbol; the footer reuses it."""
    body = full.split(">", 1)[1].rsplit("</svg>", 1)[0]
    head = full.split(">", 1)[0] + ">"
    defined = head + f'<symbol id="fah-lf" viewBox="180 196 366 340">{body}</symbol><use href="#fah-lf" x="180" y="196" width="366" height="340"/></svg>'
    reused = head + '<use href="#fah-lf" x="180" y="196" width="366" height="340"/></svg>'
    return defined, reused


def logo_svgs(p):
    label = e(HOTEL_NAME)
    # master lockup: wing above, wordmark, copper rule, "by Axis.Bangkok"
    full = (f'<svg xmlns="{SVG_NS}" viewBox="180 196 366 340" role="img" aria-label="{label}" class="fah-logo-full">'
            + p["wing"] + p["word"] + p["rule"] + p["axis"] + "</svg>")
    # horizontal header lockup: wing left, wordmark over an enlarged endorsement
    header = (f'<svg xmlns="{SVG_NS}" viewBox="0 -2 602 164" role="img" aria-label="{label}" class="fah-logo-h">'
              f'<g transform="translate(0 15) scale(1.1) translate(-289 -206)">{p["wing"]}</g>'
              f'<g transform="translate(176 2) translate(-187 -356)">{p["word"]}</g>'
              f'<g transform="translate(176 94) scale(1.6) translate(-227 -488)">{p["axis"]}</g>'
              "</svg>")
    standalone = full.replace(' role="img"', ' color="#102843" role="img"') + "\n"
    return full, header, standalone


# ---------- skyline ----------

def skyline(seed, cls):
    rnd = random.Random(seed)
    W, H = 1600, 340
    city, wins = [], {"s": [], "a": [], "b": [], "c": []}
    x = -10
    while x < W:
        w = rnd.randint(34, 96)
        h = rnd.choice([rnd.randint(50, 130), rnd.randint(90, 190), rnd.randint(150, 250)])
        if 1040 < x < 1140:  # Mahanakhon-like tower with carved "pixels"
            w, h = 64, 318
            top = H - h
            notches = "".join(f"M{x + w - 16} {top + y}h16v{s}h-16z" for y, s in ((30, 22), (78, 30), (140, 18), (196, 26)))
            city.append(f"M{x} {H}V{top}h{w}V{H}z")
            wins["s"].append(notches)
        else:
            city.append(f"M{x} {H}V{H - h}h{w}V{H}z")
            if rnd.random() < 0.25:  # spire / crown
                city.append(f"M{x + w // 2 - 2} {H - h}v-{rnd.randint(14, 40)}h4V{H - h}z")
        for wx in range(x + 8, x + w - 8, 13):
            for wy in range(H - h + 14, H - 10, 18):
                r = rnd.random()
                if r < 0.05:
                    key = rnd.choice("abc")
                elif r < 0.20:
                    key = "s"
                else:
                    continue
                wins[key].append(f"M{wx} {wy}h4v6h-4z")
        x += w + rnd.randint(0, 5)
    out = [f'<svg class="fah-city {cls}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice" aria-hidden="true">',
           f'<path class="fah-city__b" d="{"".join(city)}"/>']
    for k, ds in wins.items():
        if ds:
            out.append(f'<path class="fah-city__w fah-city__w--{k}" d="{"".join(ds)}"/>')
    out.append("</svg>")
    return "".join(out)


# ---------- geometry ----------

def project(lat, lon, m):
    return ((lon - m["west"]) / (m["east"] - m["west"]) * m["width"],
            (m["north"] - lat) / (m["north"] - m["south"]) * m["height"])


def metres(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def walk_minutes(ll, m):
    return max(1, round(metres(m["hotel"], ll) * m["walk_factor"] / m["metres_per_minute"]))


def ring_radius(minutes, m):
    straight = minutes * m["metres_per_minute"] / m["walk_factor"]
    metres_per_unit = metres((m["north"], m["west"]), (m["north"], m["east"])) / m["width"]
    return straight / metres_per_unit


# ---------- pieces ----------

ICON = {
    "l": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    "r": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    "x": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
}


def img(base, slug, alt, sizes, cls="", eager=False):
    small, large = f"{base}/img/{slug}-700.jpg", f"{base}/img/{slug}-1400.jpg"
    load_attr = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{small}" srcset="{small} 700w, {large} 1400w" sizes="{sizes}" '
            f'alt="{e(alt)}" {load_attr} decoding="async" data-full="{large}">')


def fmt_size(size, lang):
    s = f"{size:g}"
    return s.replace(".", ",") if lang == "ru" else s


def contacts_list(cfg, t, lang):
    c = t["contacts"]
    rows = [(c["address"], e(c.get("address_text") or cfg["address_line"]))]
    if cfg.get("phone"):
        tel = re.sub(r"[^\d+]", "", cfg["phone"])
        rows.append((c["phone"], f'<a href="tel:{tel}">{e(cfg["phone"])}</a>'))
    if cfg.get("email"):
        rows.append((c["email"], f'<a href="mailto:{e(cfg["email"])}">{e(cfg["email"])}</a>'))
    if cfg.get("line_url"):
        rows.append((c["line"], f'<a href="{e(cfg["line_url"])}" target="_blank" rel="noopener">LINE</a>'))
    if lang != "th":
        rows.append((c["taxi"], f'<span lang="th">{TH_ADDRESS}</span>'))
    return "".join(f"<div><dt>{e(k)}</dt><dd>{v}</dd></div>" for k, v in rows)


def json_ld(cfg, t, base, lang, rooms):
    url = cfg["site_origin"] + cfg["pages"][lang]
    absolute = base.startswith("http")
    hotel_amenities = ["Free Wi-Fi in the lobby", "Luggage storage", "Security staff", "CCTV",
                       "Parking (THB 300 per day, reservation required)", "Smoke-free rooms",
                       "Designated smoking area", "Contactless check-in", "Online pre-registration"]
    room_amenities = ["Air conditioning", "Free Wi-Fi", "Satellite TV", "Kettle with tea and coffee",
                      "Hairdryer", "In-room safe", "Telephone", "Slippers", "Luggage rack"]
    feature = lambda n: {"@type": "LocationFeatureSpecification", "name": n, "value": True}
    places = []
    for r in rooms:
        rl = r[lang]
        room = {
            "@type": "HotelRoom", "name": rl["name"], "description": rl["text"],
            "floorSize": {"@type": "QuantitativeValue", "value": r["size"], "unitCode": "MTK"},
            "occupancy": {"@type": "QuantitativeValue", "maxValue": r["guests"]},
            "bed": [{"@type": "BedDetails", "numberOfBeds": n, "typeOfBed": kind} for n, kind in r["schema_beds"]],
            "amenityFeature": [feature(a) for a in room_amenities + r["schema_amenities"]],
            "url": f"{url}#fah-{r['id']}",
        }
        if absolute and r["photos"]:
            room["image"] = [f"{base}/img/{s}-1400.jpg" for s in r["photos"][:3]]
        places.append(room)
    data = {
        "@context": "https://schema.org", "@type": "Hotel", "@id": cfg["site_origin"] + cfg["pages"]["en"] + "#hotel",
        "name": HOTEL_NAME, "url": url, "description": t["meta_description"], "inLanguage": lang,
        "brand": {"@type": "Brand", "name": "Axis Hotels", "url": cfg["site_origin"]},
        "address": {"@type": "PostalAddress", "streetAddress": "128/10–11 Soi Silom 6, Silom Road, Suriya Wong",
                    "addressLocality": "Bang Rak, Bangkok", "postalCode": "10500", "addressCountry": "TH"},
        "geo": {"@type": "GeoCoordinates", "latitude": 13.7279866, "longitude": 100.5307883},
        "hasMap": "https://www.google.com/maps/search/?api=1&query=" + quote_plus(cfg["map_query"]),
        "checkinTime": "15:00", "checkoutTime": "12:00", "smokingAllowed": False,
        "amenityFeature": [feature(a) for a in hotel_amenities],
        "containsPlace": places,
    }
    if absolute:
        data["image"] = [f"{base}/img/{s}-1400.jpg" for s in (HERO_PHOTO, "hotel-facade", "suite-bedroom")]
        data["logo"] = f"{base}/logo.svg"
    if cfg.get("phone"):
        data["telephone"] = cfg["phone"]
    if cfg.get("email"):
        data["email"] = cfg["email"]
    if cfg.get("same_as"):
        data["sameAs"] = cfg["same_as"]
    if cfg.get("booking_url"):
        data["potentialAction"] = {"@type": "ReserveAction", "target": cfg["booking_url"].replace("{lang}", lang)}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


# ---------- sections ----------

def section_hero(t, base, lang, logos):
    h = t["hero"]
    b = t["booking"]
    guests = "".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{n}</option>' for n in range(1, 7))
    photo = img(base, HERO_PHOTO, t["photos"][HERO_PHOTO], "(min-width: 900px) 58vw, 100vw", eager=True)
    return f'''
<section class="fah-hero" data-phase="night">
  <div class="fah-sky" aria-hidden="true"><div class="fah-stars"></div><div class="fah-sun"></div></div>
  {skyline(7, "fah-city--hero")}
  <div class="fah-skybar">
    <div class="fah-wrap fah-dial">
      <div class="fah-dial__row"><span class="fah-dial__label">{e(h["sky"])}</span><output class="fah-dial__time">--:--</output><span class="fah-dial__phase"></span><button type="button" class="fah-dial__now">{e(h["now"])}</button></div>
      <input type="range" min="0" max="23.75" step="0.25" value="12" class="fah-dial__range" aria-label="{e(h["drag"])}">
    </div>
  </div>
  <div class="fah-wrap fah-hero__grid">
    <div class="fah-hero__text">
      <div class="fah-hero__logo">{logos[0]}</div>
      <h1>{e(h["title"])}</h1>
      <p class="fah-hero__lead">{e(h["lead"])}</p>
    </div>
    <figure class="fah-hero__photo">
      <button type="button" class="fah-zoom">{photo}</button>
    </figure>
  </div>
  <div class="fah-wrap fah-hero__bar">
    <a class="fah-hero__more" href="#fah-rooms">{e(h["rooms_btn"])} {ICON["arrow"]}</a>
    <form class="fah-booking" data-fah-booking novalidate>
      <label><span>{e(b["checkin"])}</span><input type="date" name="checkin" required></label>
      <label><span>{e(b["checkout"])}</span><input type="date" name="checkout" required></label>
      <label class="fah-booking__guests"><span>{e(b["guests"])}</span><select name="guests">{guests}</select></label>
      <button type="submit" class="fah-btn fah-btn--copper">{e(b["cta"])}<small class="fah-booking__nights" aria-live="polite"></small></button>
    </form>
  </div>
</section>'''


def section_rooms(t, rooms, base, lang, booking):
    rt = t["rooms"]
    fits = "".join(f'<button type="button" class="fah-chip" data-fit="{k}" aria-pressed="false">{e(v)}</button>'
                   for k, v in rt["fits"].items())
    maxa = max(r["size"] for r in rooms)
    squares = ""
    for r in sorted(rooms, key=lambda r: -r["size"]):
        side = 100 * math.sqrt(r["size"] / maxa)
        squares += f'<rect data-room-ref="{r["id"]}" x="2" y="{102 - side:.1f}" width="{side:.1f}" height="{side:.1f}"/>'
    peek = "".join(
        f'<li><button type="button" class="fah-zoom">{img(base, s, t["photos"][s], "(min-width: 900px) 18vw, 32vw")}</button></li>'
        for s in PEEK_PHOTOS)
    tabs, panels = "", ""
    for i, r in enumerate(rooms):
        rl = r[lang]
        size = f'{fmt_size(r["size"], lang)} {rt["sqm"]}'
        guests = rt["guests"].replace("{n}", str(r["guests"]))
        tabs += (f'<button type="button" class="fah-tab{" is-on" if i == 0 else ""}" data-room-tab="{r["id"]}" aria-selected="{"true" if i == 0 else "false"}" role="tab" '
                 f'data-fits="{" ".join(r["fits"])}"><span class="fah-tab__n">{i + 1:02d}</span><span class="fah-tab__name">{e(rl["name"])}</span>'
                 f'<span class="fah-tab__meta">{e(size)} · {e(guests)}</span><span class="fah-tab__match">{e(rt["match"])}</span></button>')
        n = len(r["photos"])
        if n:
            slides = "".join(
                f'<li><button type="button" class="fah-zoom" aria-label="{e(t["gallery"]["open"])} {k + 1} {e(t["gallery"]["of"])} {n}">'
                + img(base, s, t["photos"][s], "(min-width: 900px) 60vw, 100vw") + "</button></li>"
                for k, s in enumerate(r["photos"]))
            media = (f'<div class="fah-room__media"><ul class="fah-track">{slides}</ul>'
                     f'<button type="button" class="fah-nav fah-prev" aria-label="{e(t["gallery"]["prev"])}">{ICON["l"]}</button>'
                     f'<button type="button" class="fah-nav fah-next" aria-label="{e(t["gallery"]["next"])}">{ICON["r"]}</button>'
                     f'<span class="fah-count">1 / {n}</span></div>')
        else:
            beds = r.get("bedrooms", 1)
            doors = "".join("<i></i>" for _ in range(beds))
            media = (f'<div class="fah-room__media fah-noimg"><div class="fah-noimg__plan" aria-hidden="true">{doors}</div>'
                     f'<p class="fah-noimg__n">{beds} {e(plural(beds, rt["bedrooms"], lang))} · {e(size)}</p>'
                     f'<p class="fah-noimg__note">{e(rt["no_photos"])}</p></div>')
        rows = f'<div><dt>{e(rl["inroom_label"])}</dt><dd>{e(rl["inroom"])}</dd></div>'
        if rl.get("outlook"):
            rows += f'<div><dt>{e(rt["outlook"])}</dt><dd>{e(rl["outlook"])}</dd></div>'
        panels += f'''
<article class="fah-room{" is-on" if i == 0 else ""}" data-room="{r["id"]}" id="fah-{r["id"]}" role="tabpanel">
  {media}
  <div class="fah-room__info">
    <div class="fah-room__main">
      <h3>{e(rl["name"])}</h3>
      <p class="fah-room__specs">{e(rl["specs"])}</p>
      <p class="fah-room__text">{e(rl["text"])}</p>
      <a class="fah-btn fah-btn--navy" href="{e(booking + "&room-type=" + str(r["exely_room"]) if booking.startswith("http") and r.get("exely_room") else booking)}" data-fah-book>{e(rt["book_room"])} {ICON["arrow"]}</a>
    </div>
    <dl class="fah-room__dl">{rows}</dl>
  </div>
</article>'''
    amen = "".join(f"<li>{e(a)}</li>" for a in rt["amenities"])
    return f'''
<section class="fah-section fah-rooms" id="fah-rooms">
  <div class="fah-wrap">
    <div class="fah-rooms__intro">
      <div class="fah-rooms__copy">
        <p class="fah-kicker">{e(rt["kicker"])}</p>
        <h2>{e(rt["title"])}</h2>
        <p class="fah-lead">{e(t["intro"])}</p>
      </div>
      <ul class="fah-peek">{peek}</ul>
    </div>
    <div class="fah-rooms__grid">
      <aside class="fah-rooms__side">
        <div class="fah-who"><p>{e(rt["who"])}</p><div class="fah-chips">{fits}</div></div>
        <div class="fah-tabs" role="tablist">{tabs}</div>
        <figure class="fah-scale">
          <svg viewBox="0 0 104 104" aria-hidden="true">{squares}</svg>
          <figcaption><b>{e(rt["size_title"])}</b>{e(rt["size_note"])}</figcaption>
        </figure>
      </aside>
      <div class="fah-rooms__stage">{panels}
        <div class="fah-allrooms"><p class="fah-allrooms__title">{e(rt["amenities_title"])}</p><ul>{amen}</ul><p class="fah-allrooms__note">{e(rt["amenities_note"])}</p></div>
      </div>
    </div>
  </div>
</section>'''


def section_hotel(t, base):
    ht = t["hotel"]
    photos = "".join(
        f'<li><button type="button" class="fah-zoom">{img(base, s, t["photos"][s], "(min-width: 900px) 24vw, 46vw")}</button>'
        f'<span>{e(t["photos"][s])}</span></li>' for s in HOTEL_PHOTOS)
    facts = "".join(f"<li><span>{e(label)}</span><strong>{e(value)}</strong></li>" for value, label in ht["facts"])
    return f'''
<section class="fah-section fah-hotel" id="fah-hotel">
  <div class="fah-wrap fah-hotel__head">
    <div><p class="fah-kicker">{e(ht["kicker"])}</p><h2>{e(ht["title"])}</h2></div>
    <div><p class="fah-lead">{e(ht["lead"])}</p><p class="fah-hotel__online">{e(ht["online"])}</p></div>
  </div>
  <ul class="fah-wrap fah-stay">{facts}</ul>
  <ul class="fah-wrap fah-hotel__photos">{photos}</ul>
</section>'''


def section_area(t, places, routes, m, lang, base):
    at, tt = t["area"], t["transit"]
    cats = ["all"] + [c for c in ["transit", "night", "food", "sight", "shop"] if any(p["cat"] == c for p in places)]
    filters = "".join(f'<button type="button" class="fah-chip{" is-on" if c == "all" else ""}" data-cat="{c}" aria-pressed="{"true" if c == "all" else "false"}">{e(at["filters"][c])}</button>' for c in cats)
    hx, hy = project(*m["hotel"], m)
    vx, vy, W, H = m.get("view", [0, 0, m["width"], m["height"]])
    by_id = {p["id"]: p for p in places}
    items, markers, mins = "", "", []
    for i, p in enumerate(sorted(places, key=lambda p: walk_minutes(p["ll"], m))):
        mn = walk_minutes(p["ll"], m)
        mins.append(mn)
        x, y = project(*p["ll"], m)
        name, note = p[lang]
        items += (f'<li data-place="{p["id"]}" data-cat="{p["cat"]}"><button type="button">'
                  f'<span class="fah-place__dot fah-cat-{p["cat"]}" data-n="{i + 1}"></span><span class="fah-place__name">{e(name)}<small>{e(note)}</small></span>'
                  f'<span class="fah-place__min">{mn} {e(t["min"])}</span></button></li>')
        markers += (f'<g class="fah-marker fah-cat-{p["cat"]}" data-place="{p["id"]}" data-cat="{p["cat"]}" transform="translate({x:.1f} {y:.1f})">'
                    f'<line class="fah-marker__path" x1="0" y1="0" x2="{hx - x:.1f}" y2="{hy - y:.1f}"/>'
                    f'<circle r="11"/><text dy="4">{i + 1}</text>'
                    f'<g class="fah-marker__label" transform="translate(16 -14)"><rect rx="6" height="28" width="{max(80, len(name) * 8.4 + 56):.0f}"/>'
                    f'<text x="10" y="19">{e(name)} · {mn} {e(t["min"])}</text></g></g>')
    rings = "".join(f'<circle class="fah-ring" cx="{hx:.1f}" cy="{hy:.1f}" r="{ring_radius(mn, m):.1f}"/>'
                    f'<text class="fah-ring__t" x="{hx + ring_radius(mn, m) * 0.707 + 4:.1f}" y="{hy - ring_radius(mn, m) * 0.707:.1f}">{mn} {e(t["min"])}</text>'
                    for mn in (5, 10, 15))
    hotel_mark = (f'<g class="fah-hotelpin" transform="translate({hx:.1f} {hy:.1f})"><circle class="fah-hotelpin__pulse" r="18"/>'
                  f'<circle r="15"/><path d="M-6 5c2-6 6-9 12-10-3 3-4 6-9 8 3 0 5-1 7-2-3 3-6 4-10 4z" fill="#fff"/></g>')
    nums = "".join(
        f'<li><strong>{walk_minutes(by_id[pid]["ll"], m)}<small>{e(t["min"])}</small></strong><span>{e(label)}</span></li>'
        for pid, label in t["numbers"])

    lines, stations = routes["lines"], routes["stations"]
    buttons, panels = "", ""
    for i, r in enumerate(routes["routes"]):
        name, note = r[lang]
        on = " is-on" if i == 0 else ""
        buttons += (f'<button type="button" class="fah-dest{on}" data-route-btn="{r["id"]}" data-walk="{r["walk_to"]}" aria-pressed="{"true" if i == 0 else "false"}">'
                    f'<span>{e(name)}</span><small>≈ {r["minutes"]} {e(t["min"])}</small></button>')
        first = r["legs"][0]
        station_place = by_id[r["walk_to"]]
        wmin = walk_minutes(station_place["ll"], m)
        steps = [f'<li class="fah-step fah-step--start"><b>{e(tt["from"])}</b><small>Soi Silom 6</small></li>',
                 f'<li class="fah-step fah-step--walk"><span>{e(tt["walk"])} {e(station_place[lang][0])} · {wmin} {e(t["min"])}</span></li>']
        prev_to = None
        for k, leg in enumerate(r["legs"]):
            ln = lines[leg["line"]]
            if k > 0:
                frm, to = stations[prev_to][lang], stations[leg["from"]][lang]
                label = tt["boat"] if leg["line"] == "boat" else tt["change"]
                via = frm if frm == to else f"{frm} → {to}"
                steps.append(f'<li class="fah-step fah-step--change"><b>{e(label)}</b><small>{e(via)}</small></li>')
            else:
                steps.append(f'<li class="fah-step fah-step--station" style="--c:{ln["color"]}"><b>{e(stations[leg["from"]][lang])}</b><small>{e(ln[lang])}</small></li>')
            ride = (f'{leg["stops"]} {e(plural(leg["stops"], tt["stops"], lang))}' if leg["stops"] else e(ln[lang]))
            ticks = "".join("<i></i>" for _ in range(max(0, leg["stops"] - 1)))
            steps.append(f'<li class="fah-step fah-step--ride" style="--c:{ln["color"]}"><span class="fah-step__line">{ticks}</span><span>{ride}{" · " + e(ln[lang]) if leg["stops"] and k > 0 else ""}</span></li>')
            steps.append(f'<li class="fah-step fah-step--station" style="--c:{ln["color"]}"><b>{e(stations[leg["to"]][lang])}</b></li>')
            prev_to = leg["to"]
        steps.append(f'<li class="fah-step fah-step--end"><b>{e(name)}</b><small>{e(note)}</small></li>')
        total = tt["total"].replace("{n}", str(r["minutes"]))
        panels += (f'<div class="fah-route{on}" data-route="{r["id"]}"><p class="fah-route__total">≈ {r["minutes"]}<small>{e(t["min"])}</small></p>'
                   f'<p class="fah-route__sub">{e(total)}</p><ol class="fah-steps">{"".join(steps)}</ol></div>')

    lead = at["lead"].replace("{max}", str(max(mins)))
    return f'''
<section class="fah-section fah-area" id="fah-area">
  <div class="fah-wrap">
    <div class="fah-head fah-head--row">
      <div><p class="fah-kicker">{e(at["kicker"])}</p><h2>{e(at["title"])}</h2></div>
      <p class="fah-lead">{e(lead)}</p>
    </div>
    <ul class="fah-numbers">{nums}</ul>
    <div class="fah-area__grid">
      <div class="fah-map">
        <img src="{base}/img/silom-map.svg" alt="{e(at["map_alt"])}" loading="lazy" width="{W}" height="{H}">
        <svg class="fah-map__layer" viewBox="{vx} {vy} {W} {H}" aria-hidden="true">{rings}{markers}{hotel_mark}</svg>
        <p class="fah-map__legend"><span class="fah-map__ring"></span>{e(at["rings"])}<span class="fah-map__line fah-map__line--bts"></span>BTS<span class="fah-map__line fah-map__line--mrt"></span>MRT<span class="fah-map__osm">© OpenStreetMap</span></p>
      </div>
      <div class="fah-area__panel">
        <div class="fah-seg" role="tablist">
          <button type="button" class="fah-seg__btn is-on" data-mode="walk" role="tab" aria-selected="true">{e(at["mode_walk"])}</button>
          <button type="button" class="fah-seg__btn" data-mode="transit" role="tab" aria-selected="false">{e(at["mode_transit"])}</button>
        </div>
        <div class="fah-mode is-on" data-mode-panel="walk">
          <div class="fah-chips">{filters}</div>
          <ol class="fah-places">{items}</ol>
          <p class="fah-note">{e(at["approx"])}</p>
        </div>
        <div class="fah-mode" data-mode-panel="transit">
          <p class="fah-mode__lead">{e(tt["lead"])}</p>
          <div class="fah-dests">{buttons}</div>
          <div class="fah-routes">{panels}</div>
        </div>
      </div>
    </div>
  </div>
</section>'''


def section_request(t, base):
    rq = t["request"]
    types = "".join(f'<label class="fah-chip"><input type="radio" name="type" value="{e(v)}"{" checked" if k == "long" else ""}><span>{e(v)}</span></label>'
                    for k, v in rq["types"].items())
    return f'''
<section class="fah-section fah-request" id="fah-request">
  <div class="fah-wrap fah-request__grid">
    <div class="fah-request__intro">
      <p class="fah-kicker">{e(rq["kicker"])}</p>
      <h2>{e(rq["title"])}</h2>
      <p class="fah-lead">{e(rq["lead"])}</p>
      <div class="fah-request__photo">{img(base, "suite-living", t["photos"]["suite-living"], "(min-width: 900px) 30vw, 90vw")}</div>
    </div>
    <form class="fah-form" data-fah-request novalidate>
      <fieldset><legend>{e(rq["type_label"])}</legend><div class="fah-chips">{types}</div></fieldset>
      <div class="fah-form__row">
        <label class="fah-field"><input name="name" autocomplete="name" placeholder=" " required><span>{e(rq["name"])}</span></label>
        <label class="fah-field"><input name="contact" autocomplete="email" placeholder=" " required><span>{e(rq["contact"])}</span></label>
      </div>
      <div class="fah-form__row fah-form__row--4">
        <label class="fah-field"><input type="date" name="checkin" placeholder=" "><span>{e(rq["checkin"])}</span></label>
        <label class="fah-field"><input type="date" name="checkout" placeholder=" "><span>{e(rq["checkout"])}</span></label>
        <label class="fah-field"><input type="number" name="guests" min="1" max="60" value="2" placeholder=" "><span>{e(rq["guests"])}</span></label>
        <label class="fah-field"><input type="number" name="rooms" min="1" max="30" value="1" placeholder=" "><span>{e(rq["rooms"])}</span></label>
      </div>
      <label class="fah-field fah-field--area"><textarea name="message" rows="4" placeholder="{e(rq["message_ph"])}"></textarea><span>{e(rq["message"])}</span></label>
      <p class="fah-form__consent">{e(rq["consent"])}</p>
      <div class="fah-form__actions">
        <button type="submit" class="fah-btn fah-btn--copper">{e(rq["submit"])} {ICON["arrow"]}</button>
        <p class="fah-form__status" role="status" aria-live="polite"></p>
      </div>
    </form>
  </div>
</section>'''


def section_faq(t):
    f = t["faq"]
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in f["items"])
    return f'''
<section class="fah-section fah-faq" id="fah-faq">
  <div class="fah-wrap fah-faq__grid">
    <div><p class="fah-kicker">{e(f["kicker"])}</p><h2>{e(f["title"])}</h2></div>
    <div class="fah-faq__list">{items}</div>
  </div>
</section>'''


def section_footer(t, cfg, logos, langs_html, map_link):
    c = t["contacts"]
    return f'''
<footer class="fah-footer" id="fah-contacts">
  <div class="fah-sky fah-sky--night" aria-hidden="true"><div class="fah-stars"></div></div>
  <div class="fah-wrap fah-footer__grid">
    <div class="fah-footer__logo">{logos[2] if len(logos) > 2 else logos[0]}</div>
    <div>
      <p class="fah-kicker">{e(c["kicker"])}</p>
      <h2>{e(c["title"])}</h2>
      <p class="fah-footer__lead">{e(c["lead"])}</p>
      <dl class="fah-contacts">{contacts_list(cfg, t, t["_lang"])}</dl>
      <div class="fah-footer__actions">
        {f'<a class="fah-btn fah-btn--copper" href="https://wa.me/{e(cfg["whatsapp"])}" target="_blank" rel="noopener">{e(c["whatsapp_btn"])} {ICON["arrow"]}</a>' if cfg.get("whatsapp") else ""}
        <a class="fah-btn fah-btn--ghost" href="{e(map_link)}" target="_blank" rel="noopener">{e(c["directions"])} {ICON["arrow"]}</a>
      </div>
    </div>
  </div>
  {skyline(23, "fah-city--footer")}
  <div class="fah-footer__bottom"><div class="fah-wrap"><span>© 2026 {HOTEL_NAME}. {e(t["footer"])}</span><span class="fah-langs">{langs_html}</span></div></div>
</footer>'''


# ---------- page ----------

def render(lang, cfg, data, assets, base, lang_href, inline=True):
    texts, rooms, places, routes, m = data
    css, js, logos = assets
    t = dict(texts[lang], _lang=lang)
    booking = (cfg.get("booking_url") or "#fah-request").replace("{lang}", lang)
    nav = t["nav"]
    nav_html = "".join(f'<li><a href="#{a}">{e(nav[k])}</a></li>' for a, k in
                       (("fah-rooms", "rooms"), ("fah-area", "area"), ("fah-hotel", "hotel"), ("fah-request", "request"), ("fah-contacts", "contacts")))
    langs_html = "".join(
        f'<a href="{e(lang_href(l))}" hreflang="{l}" lang="{l}"' + (' aria-current="true"' if l == lang else "")
        + f">{LANG_LABEL[l]}</a>" for l in LANGS)
    map_q = quote_plus(cfg["map_query"])
    map_link = f"https://www.google.com/maps/search/?api=1&query={map_q}"
    fonts = "family=Jost:wght@300;400;500&family=Manrope:wght@400;500;600"
    if lang == "th":
        fonts += "&family=Kanit:wght@300;400&family=Noto+Sans+Thai:wght@400;500;600"
    root_data = {
        "booking": cfg.get("booking_url", "").replace("{lang}", lang),
        "params": cfg.get("booking_params", {}),
        "email": cfg.get("email", ""),
        "lang": lang,
        "nights": t["booking"]["nights"],
        "rq": {k: t["request"][k] for k in ("sending", "success", "error", "required", "preview")},
        "subject": f"{HOTEL_NAME} — {t['request']['kicker']}",
    }
    style_tag = f"<style>{css}</style>" if inline else f'<link rel="stylesheet" href="{base}/fah.css">'
    script_tag = f"<script>{js}</script>" if inline else f'<script src="{base}/fah.js" defer></script>'
    ld_tag = json_ld(cfg, t, base, lang, rooms) if inline else ""
    return f'''<!-- {HOTEL_NAME} · {lang.upper()} · generated by scripts/build.py, do not edit by hand -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
{style_tag}
<div class="fah fah--{lang}" lang="{lang}" id="fah-top" data-fah='{e(json.dumps(root_data, ensure_ascii=False))}' data-phases='{e(json.dumps(dict(t["hero"]["phases"], now=t["hero"]["now"]), ensure_ascii=False))}'>
<header class="fah-header">
  <div class="fah-wrap fah-header__row">
    <a class="fah-header__logo" href="#fah-top">{logos[1]}</a>
    <nav class="fah-menu" aria-label="{e(t["menu"])}"><ul>{nav_html}</ul><div class="fah-langs fah-langs--menu">{langs_html}</div></nav>
    <div class="fah-header__end">
      <div class="fah-langs" role="group" aria-label="{e(t["language"])}">{langs_html}</div>
      <a class="fah-btn fah-btn--copper fah-header__book" href="{e(booking)}" data-fah-book>{e(t["book"])}</a>
      <button type="button" class="fah-burger" aria-expanded="false" aria-label="{e(t["menu"])}"><span></span><span></span></button>
    </div>
  </div>
</header>
<main>
{section_hero(t, base, lang, logos)}
{section_rooms(t, rooms, base, lang, booking)}
{section_area(t, places, routes, m, lang, base)}
{section_hotel(t, base)}
{section_request(t, base)}
</main>
{section_footer(t, cfg, logos, langs_html, map_link)}
<div class="fah-bookbar"><a class="fah-btn fah-btn--copper" href="{e(booking)}" data-fah-book>{e(t["book"])}</a><a class="fah-btn fah-btn--line" href="#fah-request">{e(t["nav"]["request"])}</a></div>
<div class="fah-lightbox" hidden role="dialog" aria-modal="true" aria-label="{e(t["gallery"]["open"])}">
  <img alt=""><p class="fah-lightbox__caption"></p>
  <button type="button" class="fah-lb-close" aria-label="{e(t["close"])}">{ICON["x"]}</button>
  <button type="button" class="fah-nav fah-prev" aria-label="{e(t["gallery"]["prev"])}">{ICON["l"]}</button>
  <button type="button" class="fah-nav fah-next" aria-label="{e(t["gallery"]["next"])}">{ICON["r"]}</button>
</div>
{ld_tag}
</div>
{script_tag}
'''


def preview_page(lang, t, snippet, ld=""):
    hreflang = "".join(f'<link rel="alternate" hreflang="{l}" href="../{l}/">' for l in LANGS)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t["meta_title"])}</title>
<meta name="description" content="{e(t["meta_description"])}">
<meta name="robots" content="noindex">
{hreflang}
<link rel="icon" href="../logo.svg">
{ld}
<style>html,body{{margin:0;background:#F7F4EE}}</style>
</head>
<body>
{snippet}
</body>
</html>
'''


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    return css.replace(";}", "}").strip()


def write_tilda_settings(cfg, texts, asset_base, lds):
    origin = cfg["site_origin"]
    head = "\n".join(
        [f'<link rel="alternate" hreflang="{l}" href="{origin}{cfg["pages"][l]}">' for l in LANGS]
        + [f'<link rel="alternate" hreflang="x-default" href="{origin}{cfg["pages"]["en"]}">']
        # the Tilda form block under the T123 block only carries requests to e-mail: keep it off screen
        # from the first paint (fah.js does the same once it loads, for browsers without :has)
        + ['<style>.t-rec:has(.fah) ~ .t-rec:has(form.t-form){position:absolute!important;left:-10000px!important;'
           'top:auto!important;width:1px!important;height:1px!important;overflow:hidden!important}</style>'])
    names ={"en": "Английская", "ru": "Русская", "th": "Тайская"}
    out = ["# Настройки страниц в Тильде", "",
           "Файл собирается автоматически (`python3 scripts/build.py`). Копируйте значения отсюда в «Настройки страницы».", ""]
    for l in LANGS:
        t = texts[l]
        out += [f"## {names[l]} версия", "",
                f"- **Код для блока T123:** `tilda/thefah-{l}.html` (весь файл целиком)",
                f"- **Адрес страницы:** `{cfg['pages'][l].lstrip('/')}`",
                f"- **Заголовок (title):** {t['meta_title']}",
                f"- **Описание (description):** {t['meta_description']}",
                f"- **Картинка для соцсетей:** {asset_base}/img/{HERO_PHOTO}-1400.jpg",
                "- **HTML-код внутрь HEAD** (Настройки страницы → Дополнительно):", "",
                "```html", head, lds[l], "```", ""]
    (ROOT / "tilda/НАСТРОЙКИ СТРАНИЦ.md").write_text("\n".join(out), encoding="utf-8")


def main():
    cfg, texts, rooms = load("config.json"), load("texts.json"), load("rooms.json")
    places, routes, m = load("places.json")["places"], load("routes.json"), load("map.json")
    css = minify_css((ROOT / "scripts/fah.css").read_text(encoding="utf-8"))
    js = (ROOT / "scripts/fah.js").read_text(encoding="utf-8").strip()
    full, header, standalone = logo_svgs(logo_parts())
    full_def, full_use = logo_symbol(full)
    (ROOT / "docs/fah.css").write_text(css + "\n", encoding="utf-8")
    (ROOT / "docs/fah.js").write_text(js + "\n", encoding="utf-8")
    (ROOT / "docs/logo.svg").write_text(standalone, encoding="utf-8")

    slugs = set(HOTEL_PHOTOS) | {HERO_PHOTO} | set(PEEK_PHOTOS) | {"suite-living"} | {s for r in rooms for s in r["photos"]}
    problems = [f"missing docs/img/{s}-{w}.jpg" for s in sorted(slugs) for w in (700, 1400)
                if not (ROOT / f"docs/img/{s}-{w}.jpg").exists()]
    problems += [f"no {l} alt text for {s}" for s in sorted(slugs) for l in LANGS if s not in texts[l]["photos"]]
    if not (ROOT / "docs/img/silom-map.svg").exists():
        problems.append("missing docs/img/silom-map.svg (run scripts/map_base.py)")
    if problems:
        sys.exit("Build stopped:\n  " + "\n  ".join(problems))

    data = (texts, rooms, places, routes, m)
    assets = (css, js, (full_def, header, full_use))
    lds = {}
    asset_base = cfg.get("asset_base", "").rstrip("/") or "ASSET_BASE_NOT_SET"
    for lang in LANGS:
        tilda = render(lang, cfg, data, assets, asset_base, lambda l: cfg["pages"][l], inline=False)
        # Tilda refuses T123 blocks whose saved form data is over 120 000 characters (JSON-encoded)
        tilda_size = len(json.dumps([{"name": "code", "value": tilda}], ensure_ascii=False))
        if tilda_size > 115000:
            sys.exit(f"Build stopped: tilda/thefah-{lang}.html is {tilda_size} chars for Tilda, limit 120000")
        (ROOT / f"tilda/thefah-{lang}.html").write_text(tilda, encoding="utf-8")
        lds[lang] = json_ld(cfg, texts[lang], asset_base, lang, rooms)
        snippet = render(lang, cfg, data, assets, "..", lambda l: f"../{l}/", inline=False)
        out = ROOT / f"docs/{lang}/index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(preview_page(lang, texts[lang], snippet, json_ld(cfg, texts[lang], "..", lang, rooms)), encoding="utf-8")
        print(f"{lang}: tilda/thefah-{lang}.html {tilda_size} of 120000 chars allowed in Tilda")

    write_tilda_settings(cfg, texts, asset_base, lds)
    (ROOT / "docs/index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
        '<meta http-equiv="refresh" content="0; url=en/"><a href="en/">The FAH by Axis.Bangkok</a>\n', encoding="utf-8")
    (ROOT / "docs/.nojekyll").write_text("", encoding="utf-8")
    for key, what in (("booking_url", "Exely link: Book buttons lead to the request form for now"),
                      ("asset_base", "GitHub Pages address: Tilda code has no working photos yet"),
                      ("email", "request form has no destination outside Tilda"), ("phone", "phone")):
        if not cfg.get(key):
            print(f"  not set: {key} ({what})")


if __name__ == "__main__":
    main()
