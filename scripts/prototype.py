#!/usr/bin/env python3
"""Pack the three language versions into one self-contained HTML file for showing to the team.

  python3 scripts/prototype.py  ->  prototype/The FAH — прототип.html

Photos (700 px, 1400 px for the hero), the map and the logo are embedded, so the file opens
offline in any browser (fonts load from Google if there is internet). Nothing is sent anywhere:
the request form shows its "not connected" message.
"""
import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
OUT = ROOT / "prototype" / "The FAH — прототип.html"
BADGE = {"en": "Prototype · not published, nothing is sent",
         "ru": "Прототип · не опубликован, заявки никуда не уходят",
         "th": "ต้นแบบ · ยังไม่เผยแพร่"}


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    cfg = build.load("config.json")
    cfg = dict(cfg, booking_url="", email="")  # prototype never sends anything
    texts, rooms = build.load("texts.json"), build.load("rooms.json")
    places, routes, m = build.load("places.json")["places"], build.load("routes.json"), build.load("map.json")
    css = build.minify_css((ROOT / "scripts/fah.css").read_text(encoding="utf-8"))
    js = (ROOT / "scripts/fah.js").read_text(encoding="utf-8").strip()
    full, header, standalone = build.logo_svgs(build.logo_parts())
    data = (texts, rooms, places, routes, m)

    templates = {}
    for lang in build.LANGS:
        html = build.render(lang, cfg, data, ("", "", (full, header)), "__B__", lambda l: f"#{l}")
        html = re.sub(r"<!--.*?-->|<link[^>]*>|<style></style>|<script></script>", "", html, flags=re.S)
        html = re.sub(r'\s(srcset|sizes)="[^"]*"', "", html)
        templates[lang] = html.strip()

    used = set(re.findall(r"__B__/img/([a-z0-9-]+)-(?:700|1400)\.jpg", "".join(templates.values())))
    hero = {build.HERO_PHOTO}
    images = {s: data_uri(ROOT / f"docs/img/{s}-{1400 if s in hero else 700}.jpg", "image/jpeg") for s in sorted(used)}
    images["__map"] = data_uri(ROOT / "docs/img/silom-map.svg", "image/svg+xml")
    favicon = data_uri(ROOT / "docs/logo.svg", "image/svg+xml")

    fonts = ("https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Manrope:wght@400;500;600"
             "&family=Kanit:wght@300;400&family=Noto+Sans+Thai:wght@400;500;600&display=swap")
    tpl_html = "".join(f'<template id="fah-{l}">{h}</template>' for l, h in templates.items())
    page = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>The FAH by Axis.Bangkok</title>
<link rel="icon" href="{favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<style>html,body{{margin:0;background:#F7F4EE}}{css}
.proto-badge{{position:fixed;left:12px;bottom:12px;z-index:70;font:600 12px/1.3 Manrope,system-ui,sans-serif;color:#fff;background:rgba(176,115,86,.95);padding:7px 12px;border-radius:100px;box-shadow:0 6px 20px rgba(0,0,0,.25);pointer-events:none}}
@media (max-width:900px){{.proto-badge{{bottom:84px}}}}</style>
</head>
<body>
<div id="app"></div>
{tpl_html}
<script>
(function () {{
  var IMG = {json.dumps(images)};
  var BADGE = {json.dumps(BADGE, ensure_ascii=False)};
  var LANGS = ['en', 'ru', 'th'], lang = location.hash.slice(1);
  if (LANGS.indexOf(lang) < 0) {{ try {{ lang = sessionStorage.getItem('fah-lang') || 'ru'; }} catch (e) {{ lang = 'ru'; }} }}
  try {{ sessionStorage.setItem('fah-lang', lang); }} catch (e) {{}}
  var JS = {json.dumps(js)};
  function render(l) {{
    lang = l;
    try {{ sessionStorage.setItem('fah-lang', l); }} catch (e) {{}}
    document.documentElement.lang = l;
    document.documentElement.style.overflow = '';
    var html = document.getElementById('fah-' + l).innerHTML
      .replace(/__B__\\/img\\/silom-map\\.svg/g, IMG.__map)
      .replace(/__B__\\/img\\/([a-z0-9-]+)-(?:700|1400)\\.jpg/g, function (m, s) {{ return IMG[s] || ''; }});
    document.getElementById('app').innerHTML = html + '<div class="proto-badge">' + BADGE[l] + '</div>';
    var s = document.createElement('script');
    s.textContent = JS;
    document.getElementById('app').appendChild(s);
  }}
  render(lang);
  window.addEventListener('hashchange', function () {{
    var l = location.hash.slice(1);
    if (LANGS.indexOf(l) > -1 && l !== lang) {{ render(l); window.scrollTo(0, 0); }}
  }});
}})();
</script>
</body>
</html>
'''
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(OUT, round(OUT.stat().st_size / 1024 / 1024, 1), "MB")
    if len(sys.argv) > 1:  # artifact page: the host adds doctype, head and body
        body = page.split("<head>", 1)[1].replace("</head>", "", 1).replace("<body>", "", 1)
        body = body.replace("</body>\n</html>", "")
        body = re.sub(r'<meta charset="utf-8">\n<meta name="viewport"[^>]*>\n', "", body)
        art = Path(sys.argv[1])
        art.write_text(body.strip() + "\n", encoding="utf-8")
        print(art, round(art.stat().st_size / 1024 / 1024, 1), "MB")


if __name__ == "__main__":
    main()
