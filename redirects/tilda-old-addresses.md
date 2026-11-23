# Старые адреса the Fah на axis-hotels.com

С 23.11.2026 сайт the Fah живёт на `/fah` (английский, основной), `/fah/ru` и `/fah/th`.
До этого (20–23.11.2026) он был опубликован на `/en/the-fah`, `/ru/the-fah` и `/th/the-fah`.

В Тильде нет серверных 301-переадресаций, поэтому на каждом старом адресе стоит служебная страница:
- в папке своего языка (EN / RU / TH), без шапки сайта, с запретом индексации;
- в HEAD: canonical на новый адрес и мгновенный переход туда с сохранением `#раздела` и параметров;
- в теле: одна строка со ссылкой на случай, если в браузере выключен JavaScript.

| Старый адрес | Куда ведёт | Страница Тильды |
|---|---|---|
| `/en/the-fah` | `/fah` | 410807109 (папка EN) |
| `/ru/the-fah` | `/fah/ru` | 410817409 (папка RU) |
| `/th/the-fah` | `/fah/th` | 410823809 (папка TH) |

## HEAD (пример для английской; для RU и TH меняется только адрес)

```html
<link rel="canonical" href="https://axis-hotels.com/fah">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url=/fah">
<script>location.replace('/fah' + location.search + location.hash);</script>
```

## Блок «HTML-код» (T123)

```html
<p style="margin:0;padding:64px 24px;text-align:center;font:16px/1.5 system-ui,sans-serif">
  the Fah by Axis.Bangkok → <a href="/fah">axis-hotels.com/fah</a>
</p>
```

Старый сайт hotel.thefah.com переадресуется на сервере — см. `hotel.thefah.com.conf`.

## Общая шапка сайта (страница Header, 5-й блок)

Блок начинается со скрипта `tilda/header-fah-menu-item.html` (пункт the Fah в меню HOTELS).
После него в том же блоке есть скрипты, добавленные не из этого репозитория:
`axis-fah-booking-option` (the Fah в выборе отеля на бронировании),
`axis-fah-home-update` (карточка the Fah и карта на главных),
`axis-booking-native-nav-visibility`. 23.11.2026 в них заменены ссылки `'/'+lang+'/the-fah'`
на новые адреса (`/fah`, `/fah/ru`, `/fah/th`); значения `the-fah` в списках выбора отеля — внутренние метки, не адреса.
