# Старые адреса the Fah на axis-hotels.com

С 23.11.2026 сайт the Fah живёт по схеме сайта Axis Hotels, язык первым:
`/en/fah` (английский, основной, x-default), `/ru/fah`, `/th/fah`.

Раньше он был опубликован:
- 20–23.11.2026 на `/en/the-fah`, `/ru/the-fah`, `/th/the-fah`;
- 23.11.2026, несколько часов, на `/fah`, `/fah/ru`, `/fah/th`.

В Тильде нет серверных 301-переадресаций, поэтому на каждом старом адресе стоит служебная страница:
- в папке своего языка (EN / RU / TH), без шапки сайта, с запретом индексации (её нет в sitemap);
- в HEAD: canonical на новый адрес и мгновенный переход туда с сохранением `#раздела` и параметров;
- в теле: одна строка со ссылкой на случай, если в браузере выключен JavaScript.

| Старый адрес | Куда ведёт | Страница Тильды |
|---|---|---|
| `/en/the-fah` | `/en/fah` | 410807109 (папка EN) |
| `/ru/the-fah` | `/ru/fah` | 410817409 (папка RU) |
| `/th/the-fah` | `/th/fah` | 410823809 (папка TH) |
| `/fah` | `/en/fah` | 411057509 (папка EN) |
| `/fah/ru` | `/ru/fah` | 411063109 (папка RU) |
| `/fah/th` | `/th/fah` | 411066109 (папка TH) |

Сами страницы the Fah: EN 403394509 (`en/fah`), RU 403431609 (`ru/fah`), TH 403448809 (`th/fah`).

## HEAD (пример для английской; для RU и TH меняется только адрес)

```html
<link rel="canonical" href="https://axis-hotels.com/en/fah">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url=/en/fah">
<script>location.replace('/en/fah' + location.search + location.hash);</script>
```

## Блок «HTML-код» (T123)

```html
<p style="margin:0;padding:64px 24px;text-align:center;font:16px/1.5 system-ui,sans-serif">
  the Fah by Axis.Bangkok → <a href="/en/fah">axis-hotels.com/en/fah</a>
</p>
```

Старый сайт hotel.thefah.com переадресуется на сервере ai-cz-01 из репозитория axis-infrastructure — см. `hotel.thefah.com.md`.

## Общая шапка сайта (страница Header, 5-й блок)

Блок начинается со скрипта `tilda/header-fah-menu-item.html` (пункт the Fah в меню HOTELS).
После него в том же блоке есть скрипты, добавленные не из этого репозитория:
`axis-fah-booking-option` (the Fah в выборе отеля на бронировании),
`axis-fah-home-update` (карточка the Fah и карта на главных),
`axis-booking-native-nav-visibility`. Ссылки в них на страницу отеля:
`({en:'/en/fah',ru:'/ru/fah',th:'/th/fah'}[lang]||'/en/fah')`; значения `the-fah` в списках выбора отеля —
внутренние метки, не адреса.
